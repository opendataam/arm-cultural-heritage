#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

from evaluate_goskatalog import load_labels
from extract_goskatalog_armenia import REQUIRED_COLUMNS, SEARCH_EXPRESSION, utc_now
from matcher import ArmeniaMatcher
from terms import normalize_text, read_terms, registry_stats

ROOT = Path(__file__).resolve().parent.parent
COLLECTION_ID_RE = re.compile(r"[a-z0-9][a-z0-9_-]*")
COLLECTION_SCHEMA = pa.schema([
    pa.field("collection_id", pa.string(), nullable=False),
    pa.field("collection_tier", pa.string(), nullable=False),
    pa.field("collection_matched_entities", pa.list_(pa.string()), nullable=False),
    pa.field("collection_matched_terms", pa.list_(pa.string()), nullable=False),
    pa.field("collection_matched_fields", pa.list_(pa.string()), nullable=False),
    pa.field("collection_reasons", pa.list_(pa.string()), nullable=False),
    pa.field("collection_label_note", pa.string()),
    pa.field("armenia_decision", pa.string()),
])
LISTING_FIELDS = [
    "collection_tier", "id", "gikNumber", "name", "museum", "periodStr",
    "matched_terms", "reasons", "armenia_decision", "label_note",
]
ARMENIA_OUTPUTS = (("include", "armenia_records.parquet"), ("review", "armenia_review.parquet"))


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_collection(path):
    directory = path.resolve()
    definition_path = directory / "collection.json"
    definition = json.loads(definition_path.read_text(encoding="utf-8"))
    for key in ("id", "title", "terms"):
        if not definition.get(key):
            raise ValueError("{}: missing {}".format(definition_path, key))
    if not COLLECTION_ID_RE.fullmatch(definition["id"]):
        raise ValueError("{}: invalid collection id {}".format(definition_path, definition["id"]))
    candidates = definition.get("candidates") or {}
    for key in ("museum_pattern", "exclude_museum_pattern"):
        if candidates.get(key):
            try:
                re.compile(normalize_text(candidates[key]))
            except re.error as exc:
                raise ValueError("{}: invalid {}: {}".format(definition_path, key, exc))
    if candidates.get("exclude_museum_pattern") and not candidates.get("museum_pattern"):
        raise ValueError("{}: exclude_museum_pattern requires museum_pattern".format(definition_path))
    return directory, definition


def armenia_decisions(connection, armenia_dir, candidates):
    decisions = {}
    regional = set()
    museum_re = re.compile(normalize_text(candidates["museum_pattern"])) if candidates.get("museum_pattern") else None
    exclude_re = re.compile(normalize_text(candidates["exclude_museum_pattern"])) if candidates.get("exclude_museum_pattern") else None
    for decision, filename in ARMENIA_OUTPUTS:
        path = armenia_dir / filename
        if not path.is_file():
            raise ValueError("Armenia extraction output does not exist: {}".format(path))
        for record_id, museum in connection.execute("SELECT id, museum.name FROM read_parquet(?)", [str(path)]).fetchall():
            decisions[record_id] = decision
            museum = normalize_text(museum)
            if decision == "include" and museum_re and museum_re.search(museum) and not (exclude_re and exclude_re.search(museum)):
                regional.add(record_id)
    return decisions, regional


def classify(record, matcher, regional, labels):
    record_id = record.get("id")
    match = matcher.classify(record)
    tier = None
    reasons = []
    if match.decision == "include":
        tier = "confirmed"
    elif match.decision == "review":
        tier = "candidate"
    if tier:
        reasons.extend(match.reasons)
    if record_id in regional:
        tier = tier or "candidate"
        reasons.append("regional_museum")
    label = labels.get(record_id)
    if label:
        if label["label"] == "relevant":
            tier = "confirmed"
            reasons.append("manual_relevant")
        elif label["label"] == "review":
            tier = "candidate"
            reasons.append("manual_review")
        else:
            tier = None
    metadata = match.metadata()
    return tier, {
        "collection_matched_entities": metadata["armenia_matched_entities"],
        "collection_matched_terms": metadata["armenia_matched_terms"],
        "collection_matched_fields": metadata["armenia_matched_fields"],
        "collection_reasons": sorted(set(reasons)),
        "collection_label_note": label["note"] if label else None,
    }


def write_listing(table, path):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LISTING_FIELDS, lineterminator="\n")
        writer.writeheader()
        for record in table.to_pylist():
            museum = record.get("museum") or {}
            writer.writerow({
                "collection_tier": record["collection_tier"],
                "id": record["id"],
                "gikNumber": record.get("gikNumber"),
                "name": record.get("name"),
                "museum": museum.get("name") if isinstance(museum, dict) else None,
                "periodStr": record.get("periodStr"),
                "matched_terms": json.dumps(record["collection_matched_terms"], ensure_ascii=False),
                "reasons": json.dumps(record["collection_reasons"], ensure_ascii=False),
                "armenia_decision": record["armenia_decision"],
                "label_note": record["collection_label_note"],
            })
    temporary.replace(path)


def extract(args):
    collection_dir, definition = load_collection(args.collection)
    collection_id = definition["id"]
    input_path = args.input.resolve()
    armenia_dir = args.armenia_dir.resolve()
    output_dir = (args.output_dir or ROOT / "output" / "goskatalog" / "collections" / collection_id).resolve()
    if not input_path.is_file():
        raise ValueError("Input Parquet does not exist: {}".format(input_path))
    terms_path = collection_dir / definition["terms"]
    terms = read_terms(terms_path)
    matcher = ArmeniaMatcher(terms)
    labels_path = collection_dir / definition["labels"] if definition.get("labels") else None
    labels = {}
    if labels_path:
        rows, _ = load_labels(labels_path)
        labels = {int(row["id"]): row for row in rows}
    candidates = definition.get("candidates") or {}
    connection = duckdb.connect()
    connection.execute("SET threads TO {}".format(args.threads))
    connection.execute("SET memory_limit TO '{}'".format(args.memory_limit.replace("'", "''")))
    connection.execute("SET preserve_insertion_order TO false")
    columns = {row[0] for row in connection.execute("DESCRIBE SELECT * FROM read_parquet(?)", [str(input_path)]).fetchall()}
    missing = sorted(REQUIRED_COLUMNS - columns)
    if missing:
        raise ValueError("Input is missing required columns: {}".format(", ".join(missing)))
    started = time.monotonic()
    started_at = utc_now()
    source_rows = pq.ParquetFile(str(input_path)).metadata.num_rows
    decisions, regional = armenia_decisions(connection, armenia_dir, candidates)
    print("Collection: {} ({})".format(collection_id, definition["title"]), flush=True)
    print("Source: {} ({:,} rows)".format(input_path, source_rows), flush=True)
    print("Active rules: {}; regional candidates: {:,}; labels: {:,}".format(len(matcher.terms), len(regional), len(labels)), flush=True)
    query = """
        WITH normalized AS (
            SELECT *, {search} AS _collection_search_text FROM read_parquet(?)
        )
        SELECT * EXCLUDE (_collection_search_text) FROM normalized
        WHERE regexp_matches(_collection_search_text, ?, 'i')
           OR id IN (SELECT unnest(?::BIGINT[]))
    """.format(search=SEARCH_EXPRESSION)
    extra_ids = sorted(regional | set(labels))
    reader = connection.execute(query, [str(input_path), matcher.prefilter_regex, extra_ids]).fetch_record_batch(args.batch_size)
    counts = Counter()
    reasons = Counter()
    term_counts = Counter()
    fields = Counter()
    seen_ids = set()
    batches = []
    schema = pa.schema(list(reader.schema) + list(COLLECTION_SCHEMA))
    for batch in reader:
        selected = []
        metadata = []
        for index, record in enumerate(batch.to_pylist()):
            counts["scanned"] += 1
            record_id = record.get("id")
            if record_id in seen_ids:
                raise ValueError("Duplicate source id: {}".format(record_id))
            seen_ids.add(record_id)
            tier, details = classify(record, matcher, regional, labels)
            if tier is None:
                counts["manual_nonrelevant" if record_id in labels else "excluded"] += 1
                continue
            counts[tier] += 1
            if record_id not in decisions:
                counts["not_in_armenia_extraction"] += 1
            reasons.update(details["collection_reasons"])
            term_counts.update(details["collection_matched_terms"])
            fields.update(details["collection_matched_fields"])
            selected.append(index)
            metadata.append(dict(details, collection_id=collection_id, collection_tier=tier, armenia_decision=decisions.get(record_id)))
        if not selected:
            continue
        output_batch = batch.take(pa.array(selected, type=pa.int32()))
        for field in COLLECTION_SCHEMA:
            output_batch = output_batch.append_column(field, pa.array([row[field.name] for row in metadata], type=field.type))
        batches.append(output_batch)
    missing_labels = sorted(set(labels) - seen_ids)
    if missing_labels:
        raise ValueError("Label IDs missing in source: {}".format(missing_labels))
    table = pa.Table.from_batches(batches, schema=schema).sort_by([("collection_tier", "descending"), ("id", "ascending")])
    output_dir.mkdir(parents=True, exist_ok=True)
    records_path = output_dir / "{}_records.parquet".format(collection_id)
    listing_path = output_dir / "{}_records.csv".format(collection_id)
    records_tmp = records_path.with_suffix(".parquet.tmp")
    pq.write_table(table, str(records_tmp), compression="zstd")
    records_tmp.replace(records_path)
    write_listing(table, listing_path)
    report = {
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "collection": {
            "id": collection_id,
            "title": definition["title"],
            "path": str(collection_dir),
            "definition_sha256": file_sha256(collection_dir / "collection.json"),
            "candidates": candidates,
        },
        "input": {"path": str(input_path), "bytes": input_path.stat().st_size, "rows": source_rows},
        "terms": {
            "path": str(terms_path),
            "sha256": file_sha256(terms_path),
            "counts": registry_stats(terms),
            "active_rules": len(matcher.terms),
        },
        "labels": {
            "path": str(labels_path) if labels_path else None,
            "sha256": file_sha256(labels_path) if labels_path else None,
            "counts": dict(Counter(row["label"] for row in labels.values()).most_common()),
        },
        "armenia_extraction": {
            "path": str(armenia_dir),
            "include": sum(decision == "include" for decision in decisions.values()),
            "review": sum(decision == "review" for decision in decisions.values()),
            "regional_candidates": len(regional),
        },
        "settings": {"threads": args.threads, "memory_limit": args.memory_limit, "batch_size": args.batch_size},
        "counts": {
            "source_rows": source_rows,
            "scanned": counts["scanned"],
            "confirmed": counts["confirmed"],
            "candidate": counts["candidate"],
            "excluded": counts["excluded"],
            "manual_nonrelevant": counts["manual_nonrelevant"],
            "not_in_armenia_extraction": counts["not_in_armenia_extraction"],
        },
        "reasons": dict(reasons.most_common()),
        "top_terms": dict(term_counts.most_common(100)),
        "fields": dict(fields.most_common()),
        "outputs": {
            "records": {"path": str(records_path), "rows": table.num_rows, "bytes": records_path.stat().st_size},
            "listing": str(listing_path),
        },
    }
    report_path = output_dir / "report.json"
    report_tmp = report_path.with_suffix(".json.tmp")
    report_tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_tmp.replace(report_path)
    print("Done in {:.1f}s: {:,} confirmed, {:,} candidate, {:,} excluded".format(
        report["duration_seconds"], counts["confirmed"], counts["candidate"], counts["excluded"]
    ))
    print("Records:", records_path)
    print("Listing:", listing_path)
    print("Report:", report_path)
    return report


def parse_args():
    parser = argparse.ArgumentParser(description="Extract a thematic collection from a Goskatalog Parquet export")
    parser.add_argument("--collection", type=Path, required=True, help="Directory with collection.json, terms and labels")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--armenia-dir", type=Path, default=ROOT / "output" / "goskatalog", help="Directory with armenia_records.parquet and armenia_review.parquet")
    parser.add_argument("--output-dir", type=Path, help="Defaults to output/goskatalog/collections/<id>")
    parser.add_argument("--threads", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--memory-limit", default="4GB")
    parser.add_argument("--batch-size", type=int, default=8192)
    args = parser.parse_args()
    if args.threads < 1 or args.batch_size < 1:
        parser.error("threads and batch-size must be positive")
    return args


def main():
    try:
        extract(parse_args())
    except (OSError, ValueError, duckdb.Error, pa.ArrowException) as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
