"""Pipeline stages: collect → transform → publish (ТЗ 6.3).

Each stage reads the previous stage's files from the build directory and writes
its own, so any stage can be rerun alone and an orchestrator only has to call
these functions in order.
"""

import gzip
import hashlib
import json
import os
import re
import shutil
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import duckdb
import pyarrow.parquet as pq

from portal import __version__, store
from portal.pipeline import RULES_VERSION, goskatalog
from portal.pipeline.entities import Entity, load_entities
from portal.settings import TERMS_PATH, Source, load_entity_labels
from portal.text import fold, index_text

CONNECTORS = {"goskatalog_parquet": goskatalog}
LEADING_PUNCTUATION = re.compile(r"^[\W_]+")
# Publication is blocked when a source shrinks by more than this share (ТЗ 5.5, item 7).
MAX_VOLUME_DROP = 0.30


class QualityGateError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_json(path: Path) -> Optional[dict]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def entity_dictionary() -> Dict[str, Entity]:
    return load_entities(TERMS_PATH, load_entity_labels())


# --- 1. Collect -----------------------------------------------------------------


def collect(source: Source, build: Path) -> dict:
    """Store the source dump as an immutable, content-addressed snapshot."""
    checksum = sha256(source.input)
    folder = build / "snapshots" / source.id
    target = folder / f"{checksum}{source.input.suffix}"
    manifest_path = folder / f"{checksum}.json"
    manifest = read_json(manifest_path)
    if manifest is None:
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source.input, target)
        candidates = None
        if source.review_input and source.review_input.exists():
            candidates = pq.ParquetFile(source.review_input).metadata.num_rows
        manifest = {
            "source": source.id,
            "sha256": checksum,
            "path": str(target.relative_to(build)),
            "input": str(source.input),
            "rows": pq.ParquetFile(target).metadata.num_rows,
            "candidate_rows": candidates,
            "collected_at": now(),
        }
        write_json(manifest_path, manifest)
    write_json(folder / "latest.json", manifest)
    return manifest


# --- 2–6. Transform, normalize, relevance, enrichment, quality -------------------


def transform(source: Source, build: Path, entities: Optional[Dict[str, Entity]] = None) -> dict:
    snapshot = read_json(build / "snapshots" / source.id / "latest.json")
    if snapshot is None:
        raise FileNotFoundError(f"No snapshot for {source.id}; run the collect stage first")
    entities = entities if entities is not None else entity_dictionary()
    categories = {entity_id: entity.category for entity_id, entity in entities.items()}
    connector = CONNECTORS[source.connector]
    output = build / "stage" / source.id / "records.jsonl.gz"
    output.parent.mkdir(parents=True, exist_ok=True)
    stats = Counter()
    dates = Counter()
    media = Counter()
    statuses = Counter()
    started = time.monotonic()
    tmp = output.with_suffix(".tmp")
    with gzip.open(tmp, "wt", encoding="utf-8") as handle:
        for row in connector.read_rows(build / snapshot["path"]):
            stats["input"] += 1
            record = connector.transform(row, source, snapshot, categories)
            statuses[record["relevance"]["status"]] += 1
            dates[record["date"]["method"]] += 1
            media[record["media_type"]] += 1
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            stats["output"] += 1
    os.replace(tmp, output)
    result = {
        "source": source.id,
        "snapshot_sha256": snapshot["sha256"],
        "rules_version": RULES_VERSION,
        "input": stats["input"],
        "output": stats["output"],
        "candidates_not_published": snapshot.get("candidate_rows"),
        "relevance_status": dict(statuses),
        "date_methods": dict(dates),
        "media_types": dict(media),
        "seconds": round(time.monotonic() - started, 1),
        "path": str(output.relative_to(build)),
    }
    write_json(output.parent / "transform.json", result)
    return result


def read_stage(build: Path, source: Source) -> Iterable[dict]:
    with gzip.open(build / "stage" / source.id / "records.jsonl.gz", "rt", encoding="utf-8") as handle:
        for line in handle:
            yield json.loads(line)


# --- 7. Publish ---------------------------------------------------------------


def check_volume(build: Path, sources: List[Source], force: bool) -> List[dict]:
    previous = read_json(build / "report.json") or {}
    checks = []
    for source in sources:
        current = (read_json(build / "stage" / source.id / "transform.json") or {}).get("output", 0)
        before = previous.get("sources", {}).get(source.id, {}).get("published")
        passed = not before or current >= before * (1 - MAX_VOLUME_DROP)
        checks.append({
            "name": "record_volume",
            "source": source.id,
            "passed": passed,
            "critical": True,
            "detail": f"{current} records now, {before} in the previous run",
        })
    failed = [check for check in checks if not check["passed"]]
    if failed and not force:
        raise QualityGateError("; ".join(f"{c['source']}: {c['detail']}" for c in failed))
    return checks


def facet_rows(record: dict, displayable: Dict[str, Entity]) -> Iterable[tuple]:
    yield "source", record["source"]["id"]
    yield "media", record["media_type"]
    yield "rights", record["rights"]["uri"]
    if record["object_type"]["id"]:
        yield "type", record["object_type"]["id"]
    if record["institution"]["id"]:
        yield "institution", record["institution"]["id"]
    for creator in {creator["name"] for creator in record["creators"]}:
        yield "creator", creator
    for technique in {fold(value) for value in record["techniques"]}:
        yield "technique", technique
    for criterion in record["relevance"]["criteria"]:
        yield "criteria", criterion
    for entity_id in record["entities"]:
        entity = displayable.get(entity_id)
        if entity:
            yield "entity", entity_id
            yield entity.kind if entity.kind in ("place", "person") else "concept", entity_id
    date = record["date"]
    if date["year_from"] is not None:
        first, last = date["year_from"], date["year_to"]
        centuries = {century_of(first), century_of(last)}
        # Long spans ("I-III вв.") count in every century they cover.
        if last - first <= 1000:
            centuries.update(range(century_of(first), century_of(last) + 1))
        for century in centuries - {0}:
            yield "century", str(century)


def century_of(year: int) -> int:
    """1901–2000 → 20, 1–100 → 1, 100–1 BC → -1."""
    return (year - 1) // 100 + 1 if year > 0 else -((-year - 1) // 100 + 1)


def search_columns(record: dict) -> tuple:
    body = [
        record["description"],
        record["type_description"],
        record["keywords"],
        record["provenance"],
        record["fund"],
        record["object_type"]["label"],
        " ".join(record["techniques"]),
    ]
    places = [record["production_place"], record["find_place"]]
    ids = [record["id"], record["source"]["record_id"], *record["identifiers"].values()]
    return (
        index_text(record["title"]["value"]),
        index_text(" ".join(filter(None, body))),
        index_text(" ".join(c["name"] for c in record["creators"])),
        index_text(" ".join(filter(None, places))),
        " ".join(fold(value) for value in ids if value),
    )


def export(build: Path, db: Path) -> Dict[str, dict]:
    """Bulk dumps in JSON Lines and Parquet (ТЗ 10, item 4)."""
    folder = build / "export"
    folder.mkdir(parents=True, exist_ok=True)
    jsonl = folder / "records.jsonl.gz"
    parquet = folder / "records.parquet"
    connection = store.connect(db)
    with gzip.open(jsonl, "wt", encoding="utf-8") as handle:
        for row in connection.execute("select doc from records order by rowid"):
            handle.write(row["doc"] + "\n")
    connection.close()
    duck = duckdb.connect()
    duck.execute(
        f"copy (select * from read_json('{jsonl}', format='newline_delimited', sample_size=-1)) "
        f"to '{parquet}' (format parquet, compression zstd)"
    )
    duck.close()
    return {path.name: {"sha256": sha256(path), "bytes": path.stat().st_size} for path in (jsonl, parquet)}


def publish(
    sources: List[Source],
    build: Path,
    db: Path,
    entities: Optional[Dict[str, Entity]] = None,
    force: bool = False,
    with_export: bool = True,
) -> dict:
    started = time.monotonic()
    checks = check_volume(build, sources, force)
    entities = entities if entities is not None else entity_dictionary()
    displayable = {entity_id: entity for entity_id, entity in entities.items() if entity.displayable}

    tmp_db = db.with_suffix(".tmp")
    connection = store.create(tmp_db)
    entity_counts = Counter()
    institutions: Dict[str, dict] = {}
    per_source = {}
    totals = Counter()
    rowid = 0
    seen = set()
    for source in sources:
        published = duplicates = 0
        for record in read_stage(build, source):
            # Candidates are kept in the stage files but are not published (ТЗ 6.3, item 8).
            if record["relevance"]["status"] != "confirmed":
                continue
            if record["id"] in seen:
                duplicates += 1
                continue
            seen.add(record["id"])
            rowid += 1
            published += 1
            has_media = 1 if record["media"] else 0
            totals["with_media"] += has_media
            totals["media:" + record["media_type"]] += 1
            institution = record["institution"]
            connection.execute(
                "insert into records values (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    rowid,
                    record["id"],
                    record["source"]["id"],
                    record["title"]["value"],
                    LEADING_PUNCTUATION.sub("", fold(record["title"]["value"])),
                    record["date"]["year_from"],
                    record["date"]["year_to"],
                    has_media,
                    record["media_type"],
                    record["quality"]["content_tier"],
                    record["quality"]["metadata_tier"],
                    institution["id"],
                    json.dumps(record, ensure_ascii=False),
                ),
            )
            connection.execute(
                "insert into records_fts(rowid, title, body, creators, places, ids) values (?,?,?,?,?,?)",
                (rowid, *search_columns(record)),
            )
            rows = set(facet_rows(record, displayable))
            connection.executemany("insert into facets values (?,?,?)", [(rowid, f, v) for f, v in rows])
            entity_counts.update(value for field, value in rows if field == "entity")
            if institution["id"]:
                item = institutions.setdefault(institution["id"], {**institution, "source": source.id, "count": 0, "media": 0})
                item["count"] += 1
                item["media"] += has_media
        per_source[source.id] = {
            "published": published,
            "duplicates_skipped": duplicates,
            "transform": read_json(build / "stage" / source.id / "transform.json"),
        }

    for entity_id, count in entity_counts.items():
        entity = displayable[entity_id]
        connection.execute(
            "insert into entities values (?,?,?,?,?,?)",
            (entity.id, entity.kind, entity.category, entity.review_status, count,
             json.dumps(entity.as_dict(), ensure_ascii=False)),
        )
        connection.executemany(
            "insert into entity_aliases values (?,?)", [(alias, entity.id) for alias in entity.aliases()]
        )
    connection.executemany(
        "insert into institutions values (?,?,?,?,?,?,?,?,?)",
        [
            (i["id"], i["name"], i["short_name"], i["code"], i["inn"], i["country"], i["source"], i["count"], i["media"])
            for i in institutions.values()
        ],
    )
    published_at = now()
    meta = {
        "published_at": published_at,
        "rules_version": RULES_VERSION,
        "portal_version": __version__,
        "records": str(rowid),
        "with_media": str(totals["with_media"]),
        "institutions": str(len(institutions)),
        "entities": str(len(entity_counts)),
        "sources": json.dumps({s.id: per_source[s.id]["published"] for s in sources}),
    }
    connection.executemany("insert into meta values (?,?)", meta.items())
    store.finish(connection)
    os.replace(tmp_db, db)

    report = {
        "generated_at": published_at,
        "portal_version": __version__,
        "rules_version": RULES_VERSION,
        "terms_sha256": sha256(TERMS_PATH),
        "sources": per_source,
        "published": {
            "records": rowid,
            "with_media": totals["with_media"],
            "media_types": {k.split(":", 1)[1]: v for k, v in totals.items() if k.startswith("media:")},
            "institutions": len(institutions),
            "entities": len(entity_counts),
        },
        "checks": checks,
        "database": {"path": str(db), "bytes": db.stat().st_size},
    }
    if with_export:
        report["exports"] = export(build, db)
    report["seconds"] = round(time.monotonic() - started, 1)
    write_json(build / "report.json", report)
    return report
