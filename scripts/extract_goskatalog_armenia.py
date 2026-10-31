#!/usr/bin/env python3
import argparse
import csv
import hashlib
import heapq
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

from matcher import ArmeniaMatcher
from terms import read_terms, registry_stats

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_COLUMNS = {
    "id", "name", "description", "authors", "productionPlace", "findPlace", "mainWords",
    "provenance", "typologyDesc", "technologies", "fund", "museum", "typology",
}
METADATA_SCHEMA = pa.schema([
    pa.field("armenia_decision", pa.string(), nullable=False),
    pa.field("armenia_confidence", pa.string(), nullable=False),
    pa.field("armenia_match_strength", pa.string(), nullable=False),
    pa.field("armenia_matched_entities", pa.list_(pa.string()), nullable=False),
    pa.field("armenia_matched_terms", pa.list_(pa.string()), nullable=False),
    pa.field("armenia_matched_forms", pa.list_(pa.string()), nullable=False),
    pa.field("armenia_matched_fields", pa.list_(pa.string()), nullable=False),
    pa.field("armenia_match_reasons", pa.list_(pa.string()), nullable=False),
    pa.field("armenia_negated_terms", pa.list_(pa.string()), nullable=False),
])
METADATA_NAMES = [field.name for field in METADATA_SCHEMA]
SEARCH_EXPRESSION = """
    translate(
        replace(lower(concat_ws(' ',
            name,
            description,
            array_to_string(authors, ' '),
            productionPlace,
            findPlace,
            mainWords,
            provenance,
            typologyDesc,
            array_to_string(technologies, ' '),
            fund,
            typology.name,
            museum.name
        )), 'ё', 'е'),
        '‐‑‒–—−', '------'
    )
"""


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def add_metadata(batch, rows):
    for field in METADATA_SCHEMA:
        values = [row[field.name] for row in rows]
        batch = batch.append_column(field, pa.array(values, type=field.type))
    return batch


class AuditSamples:
    def __init__(self, size=100):
        self.size = size
        self.heaps = {"include": [], "review": [], "exclude": []}

    def add(self, decision, record, metadata):
        digest = int(hashlib.sha256("{}:{}".format(record.get("id"), decision).encode("ascii")).hexdigest()[:16], 16)
        museum = record.get("museum") or {}
        if not isinstance(museum, dict):
            museum = {}
        payload = {
            "decision": decision,
            "id": record.get("id"),
            "name": record.get("name"),
            "productionPlace": record.get("productionPlace"),
            "museum": museum.get("name"),
            "matched_terms": json.dumps(metadata["armenia_matched_terms"], ensure_ascii=False),
            "matched_fields": json.dumps(metadata["armenia_matched_fields"], ensure_ascii=False),
            "reasons": json.dumps(metadata["armenia_match_reasons"], ensure_ascii=False),
            "negated_terms": json.dumps(metadata["armenia_negated_terms"], ensure_ascii=False),
            "description": (record.get("description") or "")[:1000],
        }
        heap = self.heaps[decision]
        item = (-digest, record.get("id"), payload)
        if len(heap) < self.size:
            heapq.heappush(heap, item)
        elif digest < -heap[0][0]:
            heapq.heapreplace(heap, item)

    def write(self, path):
        fieldnames = ["decision", "id", "name", "productionPlace", "museum", "matched_terms", "matched_fields", "reasons", "negated_terms", "description"]
        rows = [item[2] for heap in self.heaps.values() for item in heap]
        rows.sort(key=lambda row: (row["decision"], row["id"]))
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)


def output_schema(input_schema):
    return pa.schema(list(input_schema) + list(METADATA_SCHEMA))


def candidate_query(source, source_params, prefilter_regex, known_paths=None, strip_metadata=False):
    known_cte = ""
    known_join = ""
    known_filter = ""
    params = [str(value) for value in source_params]
    if known_paths:
        known_cte = ", known AS (SELECT id FROM read_parquet(?) UNION SELECT id FROM read_parquet(?))"
        known_join = " LEFT JOIN known USING(id)"
        known_filter = " AND known.id IS NULL"
        params.extend(str(path) for path in known_paths)
    exclusions = ["_armenia_search_text"]
    if strip_metadata:
        exclusions.extend(METADATA_NAMES)
    query = """
        WITH normalized AS (
            SELECT *, {search} AS _armenia_search_text FROM {source}
        ){known_cte}, candidates AS (
            SELECT * FROM normalized{known_join}
            WHERE regexp_matches(_armenia_search_text, ?, 'i'){known_filter}
        )
        SELECT
            * EXCLUDE ({exclusions}),
            regexp_extract_all(_armenia_search_text, ?, 1, 'i') AS _armenia_prefilter_forms
        FROM candidates
    """.format(
        search=SEARCH_EXPRESSION,
        source=source,
        known_cte=known_cte,
        known_join=known_join,
        known_filter=known_filter,
        exclusions=", ".join(exclusions),
    )
    params.extend([prefilter_regex, prefilter_regex])
    return query, params


def extract(args):
    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()
    terms_path = args.terms.resolve()
    if not input_path.is_file():
        raise ValueError("Input Parquet does not exist: {}".format(input_path))
    output_dir.mkdir(parents=True, exist_ok=True)
    include_path = output_dir / "armenia_records.parquet"
    review_path = output_dir / "armenia_review.parquet"
    if input_path in {include_path, review_path}:
        raise ValueError("Output files must not overwrite the input")
    resume_paths = None
    if args.resume_from:
        resume_dir = args.resume_from.resolve()
        resume_paths = (resume_dir / "armenia_records.parquet", resume_dir / "armenia_review.parquet")
        for path in resume_paths:
            if not path.is_file():
                raise ValueError("Resume input does not exist: {}".format(path))
    terms = read_terms(terms_path)
    matcher = ArmeniaMatcher(terms)
    connection = duckdb.connect()
    connection.execute("SET threads TO {}".format(args.threads))
    connection.execute("SET memory_limit TO '{}'".format(args.memory_limit.replace("'", "''")))
    connection.execute("SET preserve_insertion_order TO false")
    source_rows = pq.ParquetFile(str(input_path)).metadata.num_rows
    columns = {row[0] for row in connection.execute("DESCRIBE SELECT * FROM read_parquet(?)", [str(input_path)]).fetchall()}
    missing = sorted(REQUIRED_COLUMNS - columns)
    if missing:
        raise ValueError("Input is missing required columns: {}".format(", ".join(missing)))
    started = time.monotonic()
    started_at = utc_now()
    print("Source: {} ({:,} rows)".format(input_path, source_rows), flush=True)
    print("Active rules: {}; threads: {}; memory: {}".format(len(matcher.terms), args.threads, args.memory_limit), flush=True)
    if resume_paths:
        print("Resume candidates: {} and {}".format(*resume_paths), flush=True)
        previous_source = "(SELECT * FROM read_parquet(?) UNION ALL SELECT * FROM read_parquet(?))"
        query, params = candidate_query(previous_source, resume_paths, matcher.prefilter_regex, strip_metadata=True)
        result = connection.execute(query, params)
        reader = result.fetch_record_batch(args.batch_size)
    else:
        if args.limit:
            source = "(SELECT * FROM read_parquet(?) LIMIT {})".format(args.limit)
        else:
            source = "read_parquet(?)"
        query, params = candidate_query(source, [str(input_path)], matcher.prefilter_regex)
        result = connection.execute(query, params)
        reader = result.fetch_record_batch(args.batch_size)
    input_schema = pa.schema([field for field in reader.schema if field.name != "_armenia_prefilter_forms"])
    schema = output_schema(input_schema)
    include_tmp = include_path.with_suffix(".parquet.tmp")
    review_tmp = review_path.with_suffix(".parquet.tmp")
    include_writer = pq.ParquetWriter(str(include_tmp), schema, compression="zstd")
    review_writer = pq.ParquetWriter(str(review_tmp), schema, compression="zstd")
    writers = {"include": include_writer, "review": review_writer}
    paths = {"include": include_path, "review": review_path}
    counts = Counter()
    reasons = Counter()
    entities = {"include": Counter(), "review": Counter()}
    term_counts = {"include": Counter(), "review": Counter()}
    fields = {"include": Counter(), "review": Counter()}
    samples = AuditSamples()
    seen_ids = set()
    last_progress = started

    def process_reader(current_reader, stage):
        nonlocal last_progress
        current_schema = pa.schema([field for field in current_reader.schema if field.name != "_armenia_prefilter_forms"])
        if current_schema != input_schema:
            raise ValueError("Input schema changed between resume stages")
        for batch in current_reader:
            selected = {"include": [], "review": []}
            metadata = {"include": [], "review": []}
            source_batch = batch.select([index for index, name in enumerate(batch.schema.names) if name != "_armenia_prefilter_forms"])
            for index, record in enumerate(batch.to_pylist()):
                counts["candidates"] += 1
                counts[stage + "_candidates"] += 1
                record_id = record.get("id")
                if record_id in seen_ids:
                    raise ValueError("Duplicate candidate source id: {}".format(record_id))
                seen_ids.add(record_id)
                match = matcher.classify(record, record.pop("_armenia_prefilter_forms", None))
                decision = match.decision
                counts[decision] += 1
                reasons.update(match.reasons)
                details = match.metadata()
                samples.add(decision, record, details)
                if decision in selected:
                    selected[decision].append(index)
                    metadata[decision].append(details)
                    entity_counts, field_counts = matcher.count_observations(match)
                    entities[decision].update(entity_counts)
                    fields[decision].update(field_counts)
                    term_counts[decision].update("{}:{}".format(observation.term.lang, observation.term.value) for observation in match.matches)
                now = time.monotonic()
                if now - last_progress >= 30:
                    print("{} candidates: {:,}; include: {:,}; review: {:,}; exclude: {:,}; elapsed: {:.0f}s".format(
                        stage.capitalize(), counts["candidates"], counts["include"], counts["review"], counts["exclude"], now - started
                    ), flush=True)
                    last_progress = now
            for decision, indices in selected.items():
                if not indices:
                    continue
                output_batch = source_batch.take(pa.array(indices, type=pa.int32()))
                output_batch = add_metadata(output_batch, metadata[decision])
                writers[decision].write_batch(output_batch)

    try:
        if resume_paths:
            process_reader(reader, "reused")
        if args.limit:
            source = "(SELECT * FROM read_parquet(?) LIMIT {})".format(args.limit)
        else:
            source = "read_parquet(?)"
        query, params = candidate_query(source, [str(input_path)], matcher.prefilter_regex, resume_paths)
        result = connection.execute(query, params)
        reader = result.fetch_record_batch(args.batch_size)
        process_reader(reader, "new")
    except Exception:
        include_writer.close()
        review_writer.close()
        include_tmp.unlink(missing_ok=True)
        review_tmp.unlink(missing_ok=True)
        raise
    include_writer.close()
    review_writer.close()
    for decision in ("review", "include"):
        temporary = paths[decision].with_suffix(".parquet.tmp")
        if pq.ParquetFile(str(temporary)).metadata.num_rows != counts[decision]:
            raise ValueError("Output row count verification failed for {}".format(decision))
        temporary.replace(paths[decision])
    audit_path = output_dir / "audit_sample.csv"
    samples.write(audit_path)
    report = {
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "input": {
            "path": str(input_path),
            "bytes": input_path.stat().st_size,
            "rows": source_rows,
            "limit": args.limit,
        },
        "terms": {
            "path": str(terms_path),
            "sha256": hashlib.sha256(terms_path.read_bytes()).hexdigest(),
            "counts": registry_stats(terms),
            "active_rules": len(matcher.terms),
        },
        "settings": {"threads": args.threads, "memory_limit": args.memory_limit, "batch_size": args.batch_size},
        "counts": {
            "source_rows": source_rows,
            "processed_source_rows": args.limit or source_rows,
            "candidates": counts["candidates"],
            "include": counts["include"],
            "review": counts["review"],
            "exclude": counts["exclude"],
        },
        "reasons": dict(reasons.most_common()),
        "top_entities": {key: dict(value.most_common(100)) for key, value in entities.items()},
        "top_terms": {key: dict(value.most_common(100)) for key, value in term_counts.items()},
        "fields": {key: dict(value.most_common()) for key, value in fields.items()},
        "outputs": {
            "include": {"path": str(include_path), "rows": counts["include"], "bytes": include_path.stat().st_size},
            "review": {"path": str(review_path), "rows": counts["review"], "bytes": review_path.stat().st_size},
            "audit_sample": str(audit_path),
        },
    }
    if resume_paths:
        report["resume"] = {
            "from": str(args.resume_from.resolve()),
            "reused_candidates": counts["reused_candidates"],
            "new_candidates": counts["new_candidates"],
        }
    report_path = output_dir / "report.json"
    report_tmp = report_path.with_suffix(".json.tmp")
    report_tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_tmp.replace(report_path)
    print("Done in {:.1f}s: {:,} include, {:,} review, {:,} excluded candidates".format(
        report["duration_seconds"], counts["include"], counts["review"], counts["exclude"]
    ))
    if resume_paths:
        print("Reused: {:,}; new: {:,}".format(counts["reused_candidates"], counts["new_candidates"]))
    print("Include:", include_path)
    print("Review:", review_path)
    print("Report:", report_path)
    return report


def parse_args():
    parser = argparse.ArgumentParser(description="Extract Armenia-related records from a Goskatalog Parquet export")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--terms", type=Path, default=ROOT / "data" / "terms.csv")
    parser.add_argument("--threads", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument("--memory-limit", default="4GB")
    parser.add_argument("--batch-size", type=int, default=8192)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume-from", type=Path, help="Directory with complete armenia_records.parquet and armenia_review.parquet from an earlier run")
    args = parser.parse_args()
    if args.threads < 1 or args.batch_size < 1 or (args.limit is not None and args.limit < 1):
        parser.error("threads, batch-size and limit must be positive")
    if args.resume_from and args.limit:
        parser.error("--limit cannot be combined with --resume-from")
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
