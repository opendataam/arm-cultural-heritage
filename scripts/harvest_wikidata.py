#!/usr/bin/env python3
"""Harvest heritage-designated monuments in Armenia from Wikidata.

Selects items with a heritage designation (P1435) and country Armenia (P17=Q399)
with one SPARQL query, then reads the entities through the Wikidata API in batches
of 50, which avoids query-service timeouts. Wikidata is CC0; the licence and author
of each Commons image (P18) are read from the Commons API, because every file
carries its own licence.
"""
import argparse
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

import pyarrow as pa

from harvest_common import ROOT, Annotator, Client, sha256, utc_now, write_parquet, write_report

SPARQL = "https://query.wikidata.org/sparql"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
SELECTION = "SELECT DISTINCT ?item WHERE { ?item wdt:P1435 [] ; wdt:P17 wd:Q399 . }"
LANGUAGES = ("hy", "ru", "en", "fr", "es")
BATCH = 50
TARGETS = {"types": "P31", "places": "P131", "designations": "P1435"}
TAGS = re.compile(r"<[^>]+>")
LABELS = pa.map_(pa.string(), pa.string())
NAMED = pa.list_(pa.struct([("id", pa.string()), ("labels", LABELS)]))
SCHEMA = [
    ("id", pa.string()),
    ("labels", LABELS),
    ("descriptions", LABELS),
    ("types", NAMED),
    ("places", NAMED),
    ("designations", NAMED),
    ("latitude", pa.float64()),
    ("longitude", pa.float64()),
    ("inception", pa.string()),
    ("image", pa.string()),
    ("image_licence", pa.string()),
    ("image_licence_url", pa.string()),
    ("image_artist", pa.string()),
    ("commons_category", pa.string()),
    ("wlm_id", pa.string()),
    ("modified", pa.string()),
]


def log(message):
    print("[{}] {}".format(utc_now()[11:19], message), file=sys.stderr, flush=True)


def chunks(values, size=BATCH):
    values = list(values)
    for start in range(0, len(values), size):
        yield values[start:start + size]


def item_ids(client):
    data, _ = client.json(SPARQL, data={"query": SELECTION}, headers={"Accept": "application/sparql-results+json"})
    ids = {binding["item"]["value"].rsplit("/", 1)[-1] for binding in data["results"]["bindings"]}
    return sorted(ids, key=lambda value: int(value[1:]))


def entities(client, ids, props):
    """Entities by id through wbgetentities; missing ids are skipped.

    No `maxlag`: on Wikidata it also counts query-service lag, which does not affect
    entity reads and can refuse serial read requests for hours.
    """
    result = {}
    for number, batch in enumerate(chunks(ids), 1):
        if number % 10 == 0:
            log("entities: {} of {}".format(len(result), len(ids)))
        data, _ = client.json(WIKIDATA_API, data={
            "action": "wbgetentities", "format": "json", "ids": "|".join(batch), "props": props,
            "languages": "|".join(LANGUAGES),
        })
        for entity_id, entity in data.get("entities", {}).items():
            if "missing" not in entity:
                result[entity_id] = entity
    return result


def texts(entity, key):
    return {code: value["value"] for code, value in (entity.get(key) or {}).items() if code in LANGUAGES}


def claim_values(entity, prop):
    """Main values of a property, preferred rank first, deprecated statements dropped."""
    claims = [c for c in (entity.get("claims") or {}).get(prop, []) if c.get("rank") != "deprecated"]
    claims.sort(key=lambda c: c.get("rank") != "preferred")
    return [c["mainsnak"]["datavalue"]["value"] for c in claims if c["mainsnak"].get("datavalue")]


def first(values):
    return values[0] if values else None


def year_of(value):
    """Wikidata time '+1215-00-00T00:00:00Z' → '1215'; decades and centuries keep their precision."""
    if not value:
        return None
    time = value["time"]
    bc = time.startswith("-")
    year = int(time.lstrip("+-").split("-", 1)[0])
    precision = value.get("precision", 9)
    if precision == 8:
        text = "{}s".format(year // 10 * 10)
    elif precision == 7:
        text = "{} century".format((year - 1) // 100 + 1)
    elif precision < 7:
        text = "{} millennium".format((year - 1) // 1000 + 1)
    else:
        text = str(year)
    return text + " BC" if bc else text


def plain(html):
    return " ".join(TAGS.sub(" ", html or "").split()) or None


def image_rights(client, files):
    """Licence, licence URL and author of Commons files, 50 titles per request."""
    rights = {}
    for number, batch in enumerate(chunks(sorted(files)), 1):
        if number % 10 == 0:
            log("image rights: {} of {}".format(len(rights), len(files)))
        data, _ = client.json(COMMONS_API, data={
            "action": "query", "format": "json", "formatversion": "2", "prop": "imageinfo",
            "iiprop": "extmetadata", "iiextmetadatafilter": "LicenseShortName|LicenseUrl|Artist",
            "titles": "|".join("File:" + name for name in batch), "maxlag": "5",
        })
        renamed = {entry["to"]: entry["from"] for entry in data["query"].get("normalized", [])}
        for page in data["query"]["pages"]:
            info = (page.get("imageinfo") or [{}])[0].get("extmetadata", {})
            title = renamed.get(page["title"], page["title"])
            rights[title.split(":", 1)[1]] = {
                "licence": plain(info.get("LicenseShortName", {}).get("value")),
                "url": info.get("LicenseUrl", {}).get("value") or None,
                "artist": plain(info.get("Artist", {}).get("value")),
            }
    return rights


def build_row(entity, target_labels, rights):
    coordinate = first(claim_values(entity, "P625"))
    image = first(claim_values(entity, "P18"))
    licence = rights.get(image, {}) if image else {}
    named = lambda prop: [
        {"id": value["id"], "labels": target_labels.get(value["id"], {})}
        for value in claim_values(entity, prop) if isinstance(value, dict) and "id" in value
    ]
    return {
        "id": entity["id"],
        "labels": texts(entity, "labels"),
        "descriptions": texts(entity, "descriptions"),
        "types": named("P31"),
        "places": named("P131"),
        "designations": named("P1435"),
        "latitude": coordinate["latitude"] if coordinate else None,
        "longitude": coordinate["longitude"] if coordinate else None,
        "inception": year_of(first(claim_values(entity, "P571"))),
        "image": image,
        "image_licence": licence.get("licence"),
        "image_licence_url": licence.get("url"),
        "image_artist": licence.get("artist"),
        "commons_category": first(claim_values(entity, "P373")),
        "wlm_id": first(claim_values(entity, "P2186")),
        "modified": entity.get("modified"),
    }


def matcher_fields(record):
    labels = lambda entries: " | ".join(value for entry in entries for value in entry["labels"].values())
    return {
        "name": " | ".join(record["labels"].values()),
        "description": " | ".join(record["descriptions"].values()),
        "productionPlace": labels(record["places"]),
        "typologyDesc": labels(record["types"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output" / "wikidata")
    parser.add_argument("--limit", type=int, help="Harvest only the first N items (diagnostics)")
    parser.add_argument("--skip-image-rights", action="store_true", help="Do not query Commons for image licences")
    args = parser.parse_args()

    started = utc_now()
    wikidata = Client(delay=0.5, timeout=300)
    log("selecting items")
    ids = item_ids(wikidata)[: args.limit]
    log("{} items selected".format(len(ids)))
    items = entities(wikidata, ids, "labels|descriptions|claims|info")
    targets = {
        value["id"]
        for entity in items.values() for prop in TARGETS.values()
        for value in claim_values(entity, prop) if isinstance(value, dict) and "id" in value
    }
    log("labels of {} linked items".format(len(targets)))
    target_labels = {key: texts(entity, "labels") for key, entity in entities(wikidata, sorted(targets), "labels").items()}
    commons = Client(delay=0.5)
    files = {first(claim_values(entity, "P18")) for entity in items.values()} - {None}
    log("licences of {} images".format(len(files)))
    rights = {} if args.skip_image_rights else image_rights(commons, files)
    annotator = Annotator()
    rows = []
    for entity_id in sorted(items, key=lambda value: int(value[1:])):
        record = build_row(items[entity_id], target_labels, rights)
        record.update(annotator.annotate(matcher_fields(record)))
        rows.append(record)
    output = args.output_dir / "records.parquet"
    count = write_parquet(output, rows, SCHEMA)
    write_report(args.output_dir / "report.json", {
        "source": "int.wikidata",
        "selection": SELECTION,
        "licence": "CC0-1.0",
        "started_at": started,
        "finished_at": utc_now(),
        "requests": {"wikidata": wikidata.requests, "commons": commons.requests},
        "input_sha256": hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest(),
        "selected_items": len(ids),
        "records": count,
        "with_coordinates": sum(1 for record in rows if record["latitude"] is not None),
        "with_image": sum(1 for record in rows if record["image"]),
        "image_licences": dict(Counter(r["image_licence"] or "unknown" for r in rows if r["image"]).most_common(20)),
        "labels": {code: sum(1 for record in rows if code in record["labels"]) for code in LANGUAGES},
        "linked_entities": sum(1 for record in rows if record["armenia_matched_entities"]),
        "output_sha256": sha256(output),
    })
    print("{}: {} records".format(output, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
