#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlencode, urljoin, urlsplit

import pyarrow as pa

from matcher import ArmeniaMatcher
from source_common import (
    HttpClient,
    ParquetOutputs,
    append_jsonl,
    base_record,
    classify_candidate,
    display_path,
    unique_strings,
    utc_now,
    write_json,
)
from terms import read_terms

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_URL = "https://rusneb.ru"
DEFAULT_QUERIES = ["Армения", "армянский", "армянская", "армяне", "Ереван", "Арцах", "Armenia", "Armenian", "Yerevan", "Artsakh", "Հայաստան", "հայերեն"]
DETAIL_LABELS = {
    "Код документа в НЭБ",
    "Каталог",
    "Автор(ы)",
    "Заглавие",
    "Место издания",
    "Издательство",
    "Год издания",
    "Объем",
    "Ответственность",
    "ISBN",
    "ISSN",
    "Язык",
    "Тематика",
    "Рубрика",
    "Ключевые слова",
    "ББК",
    "УДК",
    "Библиотека",
    "Место хранения оригинала",
    "Место хранения оригинала документа на карте",
}
# Expand/collapse controls and the empty library-map widget template rendered inside card fields.
UI_NOISE = {"Еще", "Свернуть", "Еще Свернуть", "Скопировать", "Адрес:", "График работы:", "Участник", "перейти в библиотеку"}


class SearchParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attributes = dict(attrs)
        href = attributes.get("href", "")
        classes = attributes.get("class", "").split()
        if "/catalog/" in href and "search-list__item_link" in classes:
            self.urls.append(href)


class CardParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.links = []
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "meta":
            key = attributes.get("property") or attributes.get("name")
            if key and attributes.get("content") is not None:
                self.meta[key] = attributes["content"]
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag in {"script", "style"}:
            self.skip += 1
        if tag in {"br", "p", "div", "li", "h1", "h2", "h3", "tr", "dt", "dd", "section"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip = max(0, self.skip - 1)
        if tag in {"p", "div", "li", "h1", "h2", "h3", "tr", "dt", "dd", "section"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

    def lines(self):
        return [" ".join(line.split()) for line in "".join(self.parts).splitlines() if line.strip()]


def parse_search(html, base_url):
    parser = SearchParser()
    parser.feed(html)
    urls = []
    seen = set()
    for href in parser.urls:
        url = urljoin(base_url, href).split("#", 1)[0]
        if url not in seen:
            seen.add(url)
            urls.append(url)
    match = re.search(r"Найдено\s+([\d\s]+)\s+результат", html)
    total = int(match.group(1).replace(" ", "")) if match else None
    return urls, total


def detail_fields(lines):
    try:
        start = lines.index("Детальная информация") + 1
    except ValueError:
        return {}
    collected = {}
    current = None
    for line in lines[start:]:
        if line == "Похожие документы" or line.startswith("Национальная электронная библиотека (НЭБ) предлагает"):
            break
        if line in DETAIL_LABELS:
            current = line
            collected.setdefault(current, [])
            continue
        if current and line not in UI_NOISE:
            collected[current].append(line)
    return {key: " ".join(value).strip() for key, value in collected.items() if value}


def bibliographic_description(lines):
    if "Библиографическое описание" not in lines or "Детальная информация" not in lines:
        return None
    start = lines.index("Библиографическое описание") + 1
    end = lines.index("Детальная информация", start)
    parts = [line for line in lines[start:end] if line not in UI_NOISE]
    return " ".join(parts).strip() or None


def normalize_card(html, url, query, retrieved_at):
    parser = CardParser()
    parser.feed(html)
    lines = parser.lines()
    fields = detail_fields(lines)
    canonical_url = parser.meta.get("og:url") or url
    path_id = unquote(urlsplit(canonical_url).path.rstrip("/").rsplit("/", 1)[-1])
    record_id = fields.get("Код документа в НЭБ") or path_id
    title = fields.get("Заглавие") or parser.meta.get("og:title") or parser.meta.get("description")
    authors = [fields["Автор(ы)"]] if fields.get("Автор(ы)") else []
    subjects = [fields[name] for name in ("Тематика", "Рубрика", "Ключевые слова", "ББК") if fields.get(name)]
    places = [fields["Место издания"]] if fields.get("Место издания") else []
    languages = [fields["Язык"]] if fields.get("Язык") else []
    assets = []
    seen_types = set()
    for href in parser.links:
        if "/local/tools/exalead/getFiles.php" not in href:
            continue
        asset_url = urljoin(canonical_url, href)
        doc_type = (parse_qs(urlsplit(asset_url).query).get("doc_type") or ["bin"])[0].lower()
        if doc_type in seen_types:
            continue
        seen_types.add(doc_type)
        assets.append({
            "url": asset_url,
            "role": "document",
            "mime_type": "application/pdf" if doc_type == "pdf" else "application/octet-stream",
            "expected_bytes": None,
        })
    record = base_record(record_id, "neb", canonical_url, query, retrieved_at)
    record.update({
        "title": title,
        "description": bibliographic_description(lines) or parser.meta.get("description"),
        "authors": authors,
        "date": fields.get("Год издания"),
        "places": unique_strings(places),
        "subjects": unique_strings(subjects),
        "languages": unique_strings(languages),
        "type": fields.get("Каталог") or parser.meta.get("og:type"),
        "provider": fields.get("Библиотека"),
        "access": "open" if assets else "metadata_only_or_restricted",
        "assets": assets,
        "raw_json": {"fields": fields, "meta": {key: parser.meta.get(key) for key in ("description", "og:title", "og:description", "og:type") if parser.meta.get(key)}},
    })
    return record


def extract(args):
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
    card_errors = 0
    seen = set()
    query_stats = []
    queries = args.query or DEFAULT_QUERIES
    try:
        for query in queries:
            page = 1
            query_candidates = 0
            total_results = None
            while True:
                if args.max_records_per_query and query_candidates >= args.max_records_per_query:
                    break
                params = [("q", query)]
                if args.access == "open":
                    params.append(("access[]", "open"))
                if page > 1:
                    params.append(("PAGEN_1", str(page)))
                search_url = args.base_url.rstrip("/") + "/search/?" + urlencode(params)
                urls, total_results = parse_search(client.get_text(search_url), args.base_url)
                if not urls:
                    break
                for url in urls:
                    if args.max_records_per_query and query_candidates >= args.max_records_per_query:
                        break
                    record_id = unquote(urlsplit(url).path.rstrip("/").rsplit("/", 1)[-1])
                    if record_id in seen:
                        duplicates += 1
                        continue
                    seen.add(record_id)
                    candidates += 1
                    query_candidates += 1
                    try:
                        html = client.get_text(url)
                        record = normalize_card(html, url, query, utc_now())
                    except ValueError as error:
                        card_errors += 1
                        append_jsonl(errors_path, {"id": record_id, "url": url, "query": query, "error": str(error)})
                        continue
                    outputs.add(record, classify_candidate(record, matcher, query))
                page += 1
                if total_results is not None and (page - 1) * 15 >= total_results:
                    break
                if len(urls) < 15:
                    break
            query_stats.append({"query": query, "total_results": total_results, "inspected": query_candidates})
        outputs.close()
    except Exception:
        outputs.abort()
        raise
    report = {
        "source": "neb",
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "settings": {
            "queries": queries,
            "max_records_per_query": args.max_records_per_query,
            "access": args.access,
            "delay_seconds": args.delay,
            "proxy": args.proxy,
        },
        "terms": {"path": display_path(terms_path), "sha256": hashlib.sha256(terms_path.read_bytes()).hexdigest()},
        "counts": {"candidates": candidates, **outputs.counts, "duplicates": duplicates, "card_errors": card_errors},
        "queries": query_stats,
        "http": {"network_requests": client.network_requests, "cache_hits": client.cache_hits},
        "outputs": {
            "include": display_path(outputs.paths["include"]),
            "review": display_path(outputs.paths["review"]),
            "audit_sample": display_path(output_dir / "audit_sample.csv"),
            "errors": display_path(errors_path) if errors_path.is_file() else None,
        },
        "download_notice": "The NEB user agreement prohibits mass automated downloading of NEB objects. Use only explicit bounded downloads of open documents unless the operator grants permission.",
    }
    write_json(output_dir / "report.json", report)
    print("Candidates: {candidates}; include: {include}; review: {review}; exclude: {exclude}; errors: {card_errors}".format(**report["counts"]))
    print("Network requests: {}; cache hits: {}".format(client.network_requests, client.cache_hits))
    print("Output:", output_dir)
    return report


def parse_args():
    parser = argparse.ArgumentParser(description="Extract Armenia-related metadata from the public NEB catalog")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--terms", type=Path, default=ROOT / "data" / "terms.csv")
    parser.add_argument("--query", action="append", help="Search query; repeat for multiple searches")
    parser.add_argument("--max-records-per-query", type=int, default=15, help="0 means all search results")
    parser.add_argument("--access", choices=("all", "open"), default="all")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--proxy", help="Optional HTTP(S) proxy with a Russian IP address")
    parser.add_argument("--delay", type=float, default=3.0)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=1000)
    args = parser.parse_args()
    if args.max_records_per_query < 0 or args.batch_size < 1 or args.timeout < 1 or args.retries < 0 or args.delay < 0:
        parser.error("max-records-per-query, delay and retries must be non-negative; timeout and batch-size must be positive")
    return args


def main():
    try:
        report = extract(parse_args())
    except (OSError, ValueError, pa.ArrowException, json.JSONDecodeError) as error:
        print("Error: {}".format(error), file=sys.stderr)
        return 1
    return 1 if report["counts"]["card_errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
