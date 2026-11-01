#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote, urlencode

import pyarrow as pa

from matcher import ArmeniaMatcher
from source_common import (
    HttpClient,
    ParquetOutputs,
    append_jsonl,
    base_record,
    classify_candidate,
    display_path,
    is_open_rights,
    text_values,
    unique_strings,
    utc_now,
    write_json,
)
from terms import read_terms

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_QUERIES = [
    "(Armenia OR Armenian OR Armenians)",
    "(Arménie OR Arménien OR Armenien OR Armenisch)",
    "(Հայաստան OR հայերեն OR հայկական)",
    "(Армения OR армянский OR армянская OR армяне)",
    "(Yerevan OR Erivan OR Ереван)",
    "(Artsakh OR Арцах)",
]
DEFAULT_API_BASE = "https://api.europeana.eu/record/v2"


def values(*sources):
    result = []
    for source in sources:
        result.extend(text_values(source))
    return unique_strings(result)


def first(items):
    return items[0] if items else None


def aggregation_parts(full_record):
    if not full_record:
        return [], []
    obj = full_record.get("object") or {}
    aggregations = obj.get("aggregations") or []
    europeana_aggregation = obj.get("europeanaAggregation") or {}
    return aggregations, [europeana_aggregation]


def extract_assets(aggregations):
    assets = {}
    for aggregation in aggregations:
        if not isinstance(aggregation, dict):
            continue
        resources = {item.get("about"): item for item in aggregation.get("webResources") or [] if isinstance(item, dict) and item.get("about")}
        roles = {}
        for field, role in (("edmIsShownBy", "shown_by"), ("edmObject", "object"), ("edmHasView", "has_view")):
            for url in text_values(aggregation.get(field)):
                roles[url] = role
        candidates = list(resources)
        candidates.extend(url for url in roles if url not in resources)
        for url in candidates:
            if not isinstance(url, str) or not url.startswith(("http://", "https://")) or url in assets:
                continue
            resource = resources.get(url, {})
            mime_type = resource.get("ebucoreHasMimeType")
            if not mime_type:
                formats = text_values(resource.get("dcFormat"))
                mime_type = formats[0] if formats else None
            if mime_type and mime_type.lower().split(";", 1)[0].strip() == "text/html":
                continue
            size = resource.get("ebucoreFileByteSize")
            try:
                size = int(size) if size is not None else None
            except (TypeError, ValueError):
                size = None
            assets[url] = {
                "url": url,
                "role": roles.get(url, "webresource"),
                "mime_type": mime_type,
                "expected_bytes": size,
            }
    return list(assets.values())


def normalize_record(item, query, retrieved_at, full_record=None):
    record_id = item["id"]
    record = base_record(record_id, "europeana", "https://www.europeana.eu/item" + record_id, query, retrieved_at)
    obj = (full_record or {}).get("object") or {}
    proxies = obj.get("proxies") or []
    aggregations, europeana_aggregations = aggregation_parts(full_record)
    titles = values(item.get("title"), item.get("dcTitleLangAware"))
    descriptions = values(item.get("dcDescription"), item.get("dcDescriptionLangAware"))
    authors = values(item.get("dcCreator"), item.get("dcCreatorLangAware"), item.get("edmAgentLabel"))
    places = values(item.get("dctermsSpatial"), item.get("edmPlaceLabel"), item.get("edmPlaceLabelLangAware"))
    subjects = values(item.get("dcSubjectLangAware"), item.get("edmConceptPrefLabelLangAware"), item.get("edmConceptLabel"))
    languages = values(item.get("language"))
    dates = values(item.get("year"))
    for proxy in proxies:
        if not isinstance(proxy, dict):
            continue
        titles = unique_strings(titles + values(proxy.get("dcTitle"), proxy.get("dctermsAlternative")))
        descriptions = unique_strings(descriptions + values(proxy.get("dcDescription")))
        authors = unique_strings(authors + values(proxy.get("dcCreator"), proxy.get("dcContributor")))
        places = unique_strings(places + values(proxy.get("dctermsSpatial"), proxy.get("dcCoverage")))
        subjects = unique_strings(subjects + values(proxy.get("dcSubject"), proxy.get("dcType")))
        languages = unique_strings(languages + values(proxy.get("dcLanguage")))
        dates = unique_strings(dates + values(proxy.get("dcDate"), proxy.get("dctermsCreated"), proxy.get("dctermsIssued")))
    rights = values(item.get("rights"))
    providers = values(item.get("dataProvider"))
    for aggregation in aggregations + europeana_aggregations:
        if isinstance(aggregation, dict):
            rights = unique_strings(rights + values(aggregation.get("edmRights"), aggregation.get("dcRights")))
            providers = unique_strings(providers + values(aggregation.get("edmDataProvider")))
    record.update({
        "title": first(titles),
        "description": "\n".join(descriptions) or None,
        "authors": authors,
        "date": first(dates),
        "places": places,
        "subjects": subjects,
        "languages": languages,
        "type": item.get("type") or obj.get("type"),
        "provider": first(providers),
        "rights": rights,
        "access": "open" if is_open_rights(rights) else ("unknown" if not rights else "restricted_or_unknown"),
        "assets": extract_assets(aggregations),
        "raw_json": {"search": item, "record": full_record} if full_record is not None else item,
    })
    return record


def record_url(api_base, record_id, api_key):
    return api_base.rstrip("/") + "/" + quote(record_id.strip("/"), safe="/") + ".json?" + urlencode({"wskey": api_key})


def extract(args):
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        raise ValueError("Set the Europeana API key in {}".format(args.api_key_env))
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    errors_path = output_dir / "errors.jsonl"
    errors_path.unlink(missing_ok=True)
    terms_path = args.terms.resolve()
    matcher = ArmeniaMatcher(read_terms(terms_path))
    client = HttpClient(args.delay, args.timeout, args.retries, args.proxy, output_dir / "cache")
    outputs = ParquetOutputs(output_dir, args.batch_size)
    started = time.monotonic()
    started_at = utc_now()
    candidates = 0
    duplicates = 0
    record_errors = 0
    seen = set()
    query_stats = []
    queries = args.query or DEFAULT_QUERIES
    try:
        for query in queries:
            cursor = "*"
            previous_cursors = set()
            query_candidates = 0
            total_results = None
            while cursor:
                if args.max_records and query_candidates >= args.max_records:
                    break
                rows = args.rows
                if args.max_records:
                    rows = min(rows, args.max_records - query_candidates)
                params = {
                    "query": query,
                    "wskey": api_key,
                    "rows": rows,
                    "profile": "rich",
                    "cursor": cursor,
                    "sort": "europeana_id asc",
                }
                if args.media:
                    params["media"] = "true"
                if args.reusability:
                    params["reusability"] = args.reusability
                search_url = args.api_base.rstrip("/") + "/search.json?" + urlencode(params)
                payload = client.get_json(search_url)
                if not payload.get("success"):
                    raise ValueError("Europeana search failed: {}".format(payload.get("error") or payload.get("message") or "unknown error"))
                total_results = payload.get("totalResults")
                items = payload.get("items") or []
                for item in items:
                    if args.max_records and query_candidates >= args.max_records:
                        break
                    candidates += 1
                    query_candidates += 1
                    record_id = item.get("id")
                    if not record_id:
                        raise ValueError("Europeana search item has no id")
                    if record_id in seen:
                        duplicates += 1
                        continue
                    seen.add(record_id)
                    retrieved_at = utc_now()
                    preview = normalize_record(item, query, retrieved_at)
                    preview_match = classify_candidate(preview, matcher, query)
                    if preview_match.decision == "exclude":
                        outputs.add(preview, preview_match)
                        continue
                    try:
                        full_record = client.get_json(record_url(args.api_base, record_id, api_key))
                        if not full_record.get("success"):
                            raise ValueError(full_record.get("error") or full_record.get("message") or "Record API returned success=false")
                    except ValueError as error:
                        record_errors += 1
                        append_jsonl(errors_path, {"id": record_id, "query": query, "error": str(error)})
                        continue
                    normalized = normalize_record(item, query, retrieved_at, full_record)
                    outputs.add(normalized, classify_candidate(normalized, matcher, query))
                next_cursor = payload.get("nextCursor")
                if not items or not next_cursor:
                    break
                if next_cursor in previous_cursors:
                    raise ValueError("Europeana returned a repeated cursor")
                previous_cursors.add(next_cursor)
                cursor = next_cursor
            query_stats.append({"query": query, "total_results": total_results, "inspected": query_candidates})
        outputs.close()
    except Exception:
        outputs.abort()
        raise
    report = {
        "source": "europeana",
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "settings": {
            "queries": queries,
            "max_records": args.max_records,
            "rows": args.rows,
            "media": args.media,
            "reusability": args.reusability,
            "delay_seconds": args.delay,
            "proxy": args.proxy,
            "api_key_env": args.api_key_env,
        },
        "terms": {"path": display_path(terms_path), "sha256": hashlib.sha256(terms_path.read_bytes()).hexdigest()},
        "counts": {
            "candidates": candidates,
            **outputs.counts,
            "duplicates": duplicates,
            "record_errors": record_errors,
        },
        "queries": query_stats,
        "http": {"network_requests": client.network_requests, "cache_hits": client.cache_hits},
        "outputs": {
            "include": display_path(outputs.paths["include"]),
            "review": display_path(outputs.paths["review"]),
            "audit_sample": display_path(output_dir / "audit_sample.csv"),
            "errors": display_path(errors_path) if errors_path.is_file() else None,
        },
    }
    write_json(output_dir / "report.json", report)
    print("Candidates: {candidates}; include: {include}; review: {review}; exclude: {exclude}; errors: {record_errors}".format(**report["counts"]))
    print("Network requests: {}; cache hits: {}".format(client.network_requests, client.cache_hits))
    print("Output:", output_dir)
    return report


def parse_args():
    parser = argparse.ArgumentParser(description="Extract Armenia-related records through the Europeana Search and Record APIs")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--terms", type=Path, default=ROOT / "data" / "terms.csv")
    parser.add_argument("--query", action="append", help="Europeana query; repeat for multiple searches")
    parser.add_argument("--max-records", type=int, default=100, help="Maximum search candidates per query; 0 means unlimited")
    parser.add_argument("--rows", type=int, default=100)
    parser.add_argument("--media", action="store_true", help="Keep only records with full media URLs")
    parser.add_argument("--reusability", choices=("open", "restricted", "permission"))
    parser.add_argument("--api-key-env", default="EUROPEANA_API_KEY")
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--proxy")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=1000)
    args = parser.parse_args()
    if args.max_records < 0 or not 1 <= args.rows <= 100 or args.batch_size < 1 or args.timeout < 1 or args.retries < 0 or args.delay < 0:
        parser.error("rows must be 1..100; max-records, delay and retries must be non-negative; timeout and batch-size must be positive")
    return args


def main():
    try:
        report = extract(parse_args())
    except (OSError, ValueError, pa.ArrowException, json.JSONDecodeError) as error:
        print("Error: {}".format(error), file=sys.stderr)
        return 1
    return 1 if report["counts"]["record_errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
