#!/usr/bin/env python3
"""Harvest the Armenian domain of BULAC's digital library BiNA through the Omeka S API.

Notices are reusable under the Licence Ouverte (Etalab 2.0) with source citation;
each item's own `dcterms:license` or `dcterms:rights` governs its images.
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pyarrow as pa

from harvest_common import ROOT, Annotator, Client, sha256, utc_now, write_parquet, write_report

API = "https://bina.bulac.fr/api/items"
ITEM_SET = 359095
ITEM_PAGE = "https://bina.bulac.fr/s/bina/item/{id}"
MANIFEST = "https://bina.bulac.fr/iiif/3/{id}/manifest"
PAGE_SIZE = 100
LIST = pa.list_(pa.string())
SCHEMA = [
    ("id", pa.string()),
    ("title", LIST),
    ("creator", LIST),
    ("contributor", LIST),
    ("date", pa.string()),
    ("description", LIST),
    ("subject", LIST),
    ("publisher", LIST),
    ("type", pa.string()),
    ("format", pa.string()),
    ("language", LIST),
    ("rights", pa.string()),
    ("license", pa.string()),
    ("shelfmark", pa.string()),
    ("ark", pa.string()),
    ("located_at", pa.string()),
    ("catalogue_urls", LIST),
    ("versions", LIST),
    ("item_sets", LIST),
    ("media_count", pa.int32()),
    ("thumbnail", pa.string()),
    ("item_url", pa.string()),
    ("iiif_manifest", pa.string()),
    ("modified", pa.string()),
]


def values(item, term):
    """Literal values and labelled links of a property; bare authority URIs are skipped."""
    result = []
    for value in item.get(term) or []:
        text = value.get("@value") or value.get("o:label")
        if text:
            text = " ".join(str(text).split())
            if text not in result:
                result.append(text)
    return result


def links(item, term):
    return [value["@id"] for value in item.get(term) or [] if value.get("@id")]


def first(sequence):
    return sequence[0] if sequence else None


def language_codes(item):
    return [uri.rsplit("/", 1)[-1] for uri in links(item, "dcterms:language")] or values(item, "dcterms:language")


def flatten(item):
    item_id = item["o:id"]
    thumbnails = item.get("thumbnail_display_urls") or {}
    return {
        "id": str(item_id),
        "title": values(item, "dcterms:title") or [item.get("o:title") or str(item_id)],
        "creator": values(item, "dcterms:creator"),
        "contributor": values(item, "dcterms:contributor"),
        "date": first(values(item, "dcterms:date")),
        "description": values(item, "dcterms:description"),
        "subject": values(item, "dcterms:subject"),
        "publisher": values(item, "dcterms:publisher"),
        "type": first(values(item, "dcterms:type")),
        "format": first(values(item, "dcterms:format")),
        "language": language_codes(item),
        "rights": first(values(item, "dcterms:rights")),
        "license": first(links(item, "dcterms:license")),
        "shelfmark": first(values(item, "dcterms:source")),
        "ark": first(values(item, "dcterms:identifier")),
        "located_at": first(values(item, "cld:isLocatedAt")),
        "catalogue_urls": links(item, "bibo:uri"),
        "versions": links(item, "dcterms:hasVersion"),
        "item_sets": [str(entry["o:id"]) for entry in item.get("o:item_set") or []],
        "media_count": len(item.get("o:media") or []),
        "thumbnail": thumbnails.get("large"),
        "item_url": ITEM_PAGE.format(id=item_id),
        "iiif_manifest": MANIFEST.format(id=item_id) if item.get("o:media") else None,
        "modified": (item.get("o:modified") or {}).get("@value"),
    }


def matcher_fields(row):
    return {
        "name": " | ".join(row["title"]),
        "description": " | ".join(row["description"]),
        "authors": row["creator"] + row["contributor"],
        "mainWords": " | ".join(row["subject"]),
        "provenance": " | ".join(row["publisher"]),
        "typologyDesc": row["type"],
    }


def harvest(client, item_set):
    items = []
    page = 1
    total = None
    while total is None or len(items) < total:
        batch, headers = client.json(API, {
            "item_set_id": item_set, "per_page": PAGE_SIZE, "page": page, "sort_by": "id", "sort_order": "asc",
        })
        total = int(headers.get("Omeka-S-Total-Results") or headers.get("omeka-s-total-results") or 0)
        if not batch:
            break
        items.extend(batch)
        page += 1
    if len(items) != total:
        raise RuntimeError("BiNA returned {} items, expected {}".format(len(items), total))
    return items


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--item-set", type=int, default=ITEM_SET, help="Omeka S item set id ('Domaine arménien')")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output" / "bulac")
    args = parser.parse_args()

    started = utc_now()
    client = Client(delay=1.0)
    items = harvest(client, args.item_set)
    raw = json.dumps(items, ensure_ascii=False, sort_keys=True).encode("utf-8")
    annotator = Annotator()
    rows = []
    for item in items:
        row = flatten(item)
        row.update(annotator.annotate(matcher_fields(row)))
        rows.append(row)
    output = args.output_dir / "records.parquet"
    count = write_parquet(output, rows, SCHEMA)
    write_report(args.output_dir / "report.json", {
        "source": "fr.bulac",
        "source_url": "{}?item_set_id={}".format(API, args.item_set),
        "licence": "etalab-2.0",
        "started_at": started,
        "finished_at": utc_now(),
        "requests": client.requests,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "records": count,
        "rights": dict(Counter(row["license"] or row["rights"] or "none" for row in rows).most_common()),
        "types": dict(Counter(row["type"] or "none" for row in rows).most_common()),
        "linked_entities": sum(1 for row in rows if row["armenia_matched_entities"]),
        "output_sha256": sha256(output),
    })
    print("{}: {} records".format(output, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
