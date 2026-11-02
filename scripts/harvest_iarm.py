#!/usr/bin/env python3
"""Harvest the Index of Digitized Armenian Manuscripts (IArM) from its Zenodo release.

The licensed copy is the Zenodo record (CC BY 4.0); the website and GitHub copies
carry no licence, so they are not used.
"""
import argparse
import csv
import hashlib
import io
import re
import sys
from collections import Counter
from pathlib import Path

import pyarrow as pa

from harvest_common import ROOT, Annotator, Client, sha256, utc_now, write_parquet, write_report

ZENODO_RECORD = "16355337"
INDEX_URL = "https://zenodo.org/records/{record}/files/index.tsv?download=1"
COLUMNS = {
    "ID": "siglum",
    "Cat. Number": "shelfmark",
    "Location": "location",
    "Country": "country",
    "Town": "town",
    "Permalink": "permalink",
    "Digital Library": "digital_library",
    "Support": "support",
    "Date": "date",
    "Pages": "extent",
    "Size": "size",
    "Title": "title",
    "Note": "note",
    "Genre": "genre",
    "IIIF Manifest": "iiif_manifest",
}
SCHEMA = [
    ("id", pa.string()),
    ("row_number", pa.int32()),
    *[(name, pa.string()) for name in COLUMNS.values()],
    ("zenodo_record", pa.string()),
]
SLUG = re.compile(r"[^A-Za-z0-9]+")


def record_id(siglum, shelfmark, location, seen):
    """Stable id from the siglum; rows without one fall back to holder and shelfmark."""
    base = SLUG.sub("-", siglum or "{}-{}".format(location, shelfmark)).strip("-").lower() or "row"
    seen[base] += 1
    return base if seen[base] == 1 else "{}-{}".format(base, seen[base])


def parse(text, record):
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    missing = set(COLUMNS) - set(reader.fieldnames or [])
    if missing:
        raise ValueError("IArM index lacks columns: {}".format(", ".join(sorted(missing))))
    seen = Counter()
    rows = []
    for number, raw in enumerate(reader, 1):
        row = {target: (raw.get(source) or "").strip() for source, target in COLUMNS.items()}
        row["id"] = record_id(row["siglum"], row["shelfmark"], row["location"], seen)
        row["row_number"] = number
        row["zenodo_record"] = record
        rows.append(row)
    return rows


def matcher_fields(row):
    return {
        "name": row["title"],
        "description": row["note"],
        "productionPlace": "",
        "mainWords": row["genre"],
        "typologyDesc": row["support"],
        # The holder is context, like the museum of a Goskatalog record.
        "museum": {"name": " ".join(filter(None, [row["location"], row["town"], row["country"]]))},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", default=ZENODO_RECORD, help="Zenodo record id of the IArM release")
    parser.add_argument("--input", type=Path, help="Use a local index.tsv instead of downloading it")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output" / "iarm")
    args = parser.parse_args()

    started = utc_now()
    client = Client()
    if args.input:
        content = args.input.read_bytes()
        source = str(args.input)
    else:
        source = INDEX_URL.format(record=args.record)
        content, _ = client.get(source)
    rows = parse(content.decode("utf-8-sig"), args.record)
    annotator = Annotator()
    for row in rows:
        row.update(annotator.annotate(matcher_fields(row)))
    output = args.output_dir / "records.parquet"
    count = write_parquet(output, rows, SCHEMA)
    write_report(args.output_dir / "report.json", {
        "source": "int.iarm",
        "source_url": source,
        "zenodo_record": args.record,
        "licence": "CC-BY-4.0",
        "started_at": started,
        "finished_at": utc_now(),
        "input_sha256": hashlib.sha256(content).hexdigest(),
        "records": count,
        "with_iiif_manifest": sum(1 for row in rows if row["iiif_manifest"]),
        "digital_libraries": dict(Counter(row["digital_library"] for row in rows).most_common()),
        "linked_entities": sum(1 for row in rows if row["armenia_matched_entities"]),
        "output_sha256": sha256(output),
    })
    print("{}: {} records".format(output, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
