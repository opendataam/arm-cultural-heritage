"""Goskatalog connector and mapping to the portal record model (ТЗ 6.4, appendix Б)."""

import math
from pathlib import Path
from typing import Iterator, List, Optional

import pyarrow.parquet as pq

from portal.pipeline import RULES_VERSION
from portal.pipeline.normalize import normalize_period, parse_creator, short_institution_name
from portal.settings import Source
from portal.text import clean_text

# Goskatalog typology → digital material type (appendix Б). Text types become "TEXT"
# only for multi-page scans, otherwise a single scan is shown as an image.
TEXT_TYPOLOGIES = {9, 14, 15, 16}
# Matched fields of the relevance classifier → relevance criteria (ТЗ 4.1).
FIELD_CRITERIA = {
    "authors": "creator",
    "productionPlace": "place",
    "findPlace": "place",
    "museum.name": "holding",
    "name": "subject",
    "description": "subject",
    "mainWords": "subject",
    "provenance": "subject",
    "technologies": "subject",
    "typologyDesc": "subject",
    "fund": "subject",
}
RELEVANCE_STATUS = {"include": "confirmed", "review": "candidate"}


def read_rows(path: Path, batch_size: int = 5_000) -> Iterator[dict]:
    parquet = pq.ParquetFile(path)
    for batch in parquet.iter_batches(batch_size=batch_size):
        yield from batch.to_pylist()


def _number(value) -> Optional[float]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return float(value)


def _list(value) -> List:
    return [item for item in (value or []) if item not in (None, "")]


def _text(value) -> Optional[str]:
    text = clean_text(value)
    return text or None


def relevance_criteria(fields: List[str], entity_categories: List[str]) -> List[str]:
    criteria = {FIELD_CRITERIA[field] for field in fields if field in FIELD_CRITERIA}
    if "language" in entity_categories:
        criteria.add("language")
    return sorted(criteria)


def media_type(typology_id: Optional[int], image_count: int) -> str:
    if image_count == 0:
        return "METADATA"
    if typology_id in TEXT_TYPOLOGIES and image_count > 1:
        return "TEXT"
    return "IMAGE"


def metadata_tier(record: dict) -> str:
    """Preliminary completeness tier; the method is to be approved at stage 0 (ТЗ 6.9)."""
    recommended = [
        record["description"],
        record["creators"],
        record["date"]["year_from"] is not None,
        record["production_place"] or record["find_place"],
        record["techniques"],
        record["dimensions"]["display"],
        record["identifiers"]["inventory"],
        record["provenance"],
    ]
    filled = sum(1 for value in recommended if value)
    return "A" if filled >= 6 else "B" if filled >= 3 else "C"


def transform(row: dict, source: Source, snapshot: dict, entity_categories: dict) -> dict:
    """Map one Goskatalog row to the portal record. Source values are kept as is."""
    source_id = str(row["id"])
    museum = row.get("museum") or {}
    typology = row.get("typology") or {}
    typology_id = typology.get("id")
    images = [image["url"] for image in _list(row.get("images")) if image and image.get("url")]
    creators = [creator for creator in map(parse_creator, _list(row.get("authors"))) if creator]
    period = normalize_period(row.get("periodStr"), row.get("startDate"), row.get("finishDate"))
    entities = _list(row.get("armenia_matched_entities"))
    record_url = source.record_url.format(id=source_id)
    external_url = _text(row.get("extUrl"))
    title = _text(row.get("name")) or f"{source.id} {source_id}"

    record = {
        "id": f"{source.id_prefix}-{source_id}",
        "source": {"id": source.id, "record_id": source_id, "url": record_url},
        "title": {"value": title, "lang": "ru"},
        "titles": {},
        "description": _text(row.get("description")),
        "descriptions": {},
        "metadata_lang": "ru",
        "creators": creators,
        "date": period.as_dict(),
        "production_place": _text(row.get("productionPlace")),
        "find_place": _text(row.get("findPlace")),
        "coordinates": None,
        "object_type": {
            "id": str(typology_id) if typology_id is not None else None,
            "label": typology.get("name"),
            "scheme": "goskatalog-typology",
        },
        "type_description": _text(row.get("typologyDesc")),
        "media_type": media_type(typology_id, len(images)),
        "techniques": [clean_text(value) for value in _list(row.get("technologies")) if clean_text(value)],
        "dimensions": {
            "display": _text(row.get("dimStr")),
            "height": _number(row.get("height")),
            "width": _number(row.get("width")),
            "length": _number(row.get("length")),
            "unit": (row.get("dimUnit") or {}).get("name"),
            "weight": _number(row.get("weight")),
            "weight_unit": row.get("weightUnit"),
        },
        "identifiers": {
            "inventory": _text(row.get("invNumber")),
            "goskatalog_registration": str(row["regNumber"]) if row.get("regNumber") else None,
            "kp_gik": _text(row.get("gikNumber")),
        },
        "parts_count": row.get("partsCount"),
        "fund": _text(row.get("fund")),
        "provenance": _text(row.get("provenance")),
        "keywords": _text(row.get("mainWords")),
        "institution": {
            "id": f"{source.id_prefix}-{museum.get('id')}" if museum.get("id") is not None else None,
            "name": _text(museum.get("name")),
            "short_name": short_institution_name(clean_text(museum.get("name"))),
            "code": museum.get("code"),
            "inn": museum.get("inn"),
            "country": "RU",
        },
        "provider": source.id,
        "media": [{"url": url, "type": "image"} for url in images],
        "media_credit": None,
        "iiif_manifest": None,
        "is_shown_at": external_url or record_url,
        "rights": {"uri": source.rights},
        "metadata_rights": {"uri": source.metadata_rights, "attribution": source.attribution},
        "relevance": {
            "status": RELEVANCE_STATUS.get(row.get("armenia_decision"), "candidate"),
            "criteria": relevance_criteria(
                _list(row.get("armenia_matched_fields")),
                [entity_categories.get(entity) for entity in entities],
            ),
            "confidence": row.get("armenia_confidence"),
            "strength": row.get("armenia_match_strength"),
            "matched_terms": _list(row.get("armenia_matched_terms")),
            "matched_forms": _list(row.get("armenia_matched_forms")),
            "matched_fields": _list(row.get("armenia_matched_fields")),
            "reasons": _list(row.get("armenia_match_reasons")),
            "negated_terms": _list(row.get("armenia_negated_terms")),
        },
        "entities": entities,
        "registered_at": row.get("regDate"),
        "record_provenance": {
            "source": source.id,
            "snapshot_sha256": snapshot["sha256"],
            "collected_at": snapshot["collected_at"],
            "rules_version": RULES_VERSION,
        },
    }
    record["quality"] = {
        # Image resolution is not measured yet, so records with images get tier 1 (ТЗ 6.9).
        "content_tier": 1 if images else 0,
        "metadata_tier": metadata_tier(record),
    }
    return record
