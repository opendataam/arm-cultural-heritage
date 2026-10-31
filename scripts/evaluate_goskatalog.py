#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from matcher import ArmeniaMatcher
from terms import read_terms

ROOT = Path(__file__).resolve().parent.parent
LABELS = {"relevant", "nonrelevant", "review"}


def load_labels(path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not {"id", "label", "note"}.issubset(reader.fieldnames):
            raise ValueError("Labels must have id,label,note columns")
        rows = list(reader)
    ids = [int(row["id"]) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Label IDs must be unique")
    invalid = sorted({row["label"] for row in rows} - LABELS)
    if invalid:
        raise ValueError("Invalid labels: {}".format(", ".join(invalid)))
    return rows, ids


def ratio(numerator, denominator):
    return round(numerator / denominator, 6) if denominator else None


def evaluate(args):
    labels, ids = load_labels(args.labels)
    if not ids:
        raise ValueError("No labels")
    terms = read_terms(args.terms)
    matcher = ArmeniaMatcher(terms)
    placeholders = ",".join("?" for _ in ids)
    query = "SELECT * FROM read_parquet(?) WHERE id IN ({})".format(placeholders)
    connection = duckdb.connect()
    connection.execute("SET threads TO {}".format(args.threads))
    result = connection.execute(query, [str(args.input)] + ids)
    columns = [item[0] for item in result.description]
    records = [dict(zip(columns, row)) for row in result.fetchall()]
    if len(records) != len(ids):
        found = Counter(record["id"] for record in records)
        missing = [record_id for record_id in ids if found[record_id] != 1]
        raise ValueError("Label IDs missing or duplicated in source: {}".format(missing))
    by_id = {record["id"]: record for record in records}
    confusion = Counter()
    coverage = Counter()
    details = []
    for label in labels:
        expected = label["label"]
        result = matcher.classify(by_id[int(label["id"])])
        predicted = result.decision
        confusion[(expected, predicted)] += 1
        coverage[(expected, predicted)] += 1
        metadata = result.metadata()
        details.append({
            "id": int(label["id"]),
            "label": expected,
            "predicted": predicted,
            "note": label["note"],
            "matched_terms": metadata["armenia_matched_terms"],
            "matched_fields": metadata["armenia_matched_fields"],
            "reasons": metadata["armenia_match_reasons"],
        })
    true_positive = coverage[("relevant", "include")]
    false_positive = coverage[("nonrelevant", "include")]
    false_negative = sum(coverage[("relevant", decision)] for decision in ("review", "exclude"))
    true_negative = sum(coverage[("nonrelevant", decision)] for decision in ("review", "exclude"))
    relevant_review = coverage[("relevant", "review")]
    relevant_total = true_positive + false_negative
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input": str(args.input),
        "labels": str(args.labels),
        "terms_sha256": hashlib.sha256(args.terms.read_bytes()).hexdigest(),
        "sample_size": len(ids),
        "scope": "Metrics describe only this manually labeled sample, not the full corpus",
        "automatic_filter": {
            "true_positive": true_positive,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "true_negative": true_negative,
            "precision": ratio(true_positive, true_positive + false_positive),
            "recall": ratio(true_positive, true_positive + false_negative),
        },
        "candidate_retrieval": {
            "relevant_total": relevant_total,
            "relevant_include": true_positive,
            "relevant_review": relevant_review,
            "relevant_exclude": coverage[("relevant", "exclude")],
            "candidate_recall": ratio(true_positive + relevant_review, relevant_total),
        },
        "confusion_matrix": [
            {"label": expected, "predicted": predicted, "count": count}
            for (expected, predicted), count in sorted(confusion.items())
        ],
        "records": details,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({"sample_size": len(ids), **report["automatic_filter"], **report["candidate_retrieval"]}, ensure_ascii=False, indent=2))
    print("Report:", args.output)
    return report


def main():
    parser = argparse.ArgumentParser(description="Evaluate the matcher on manually labeled Goskatalog IDs")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--labels", type=Path, default=ROOT / "evaluation" / "goskatalog_labels.csv")
    parser.add_argument("--terms", type=Path, default=ROOT / "data" / "terms.csv")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    if args.threads < 1:
        parser.error("threads must be positive")
    try:
        evaluate(args)
    except (OSError, ValueError, duckdb.Error) as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
