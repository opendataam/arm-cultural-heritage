"""Shared mapping for connectors of harvested sources (ТЗ 6.4).

Harvesters in `scripts/harvest_*.py` write Parquet files with flat source columns and
the extractor's `armenia_*` fields. Connectors build the portal record from
`base_record`, so every source fills the same keys as the Goskatalog connector.
"""

import re
from typing import Dict, List, Optional

from portal.pipeline import RULES_VERSION
from portal.pipeline.goskatalog import RELEVANCE_STATUS, metadata_tier, read_rows, relevance_criteria
from portal.pipeline.normalize import MAX_YEAR, MIN_YEAR, Period
from portal.settings import Source
from portal.text import clean_text

__all__ = ["base_record", "finish", "read_rows", "year_period", "rights_uri", "text", "texts"]

# Licence names and URLs → canonical rights URIs (RightsStatements.org and Creative Commons).
PUBLIC_DOMAIN = "http://creativecommons.org/publicdomain/mark/1.0/"
CC0 = "http://creativecommons.org/publicdomain/zero/1.0/"
IN_COPYRIGHT = "http://rightsstatements.org/vocab/InC/1.0/"
CC_URL = re.compile(r"creativecommons\.org/(licenses|publicdomain)/([a-z-]+)/(\d\.\d)", re.I)
CC_NAME = re.compile(r"^cc[ -](by(?:-sa|-nc|-nd|-nc-sa|-nc-nd)?)[ -](\d\.\d)", re.I)
YEAR = re.compile(r"^(-?\d{1,4})(?:-\d{2}(?:-\d{2})?)?$")
DECADE = re.compile(r"^(\d{3,4})s$")
CENTURY = re.compile(r"^(\d{1,2}) century$")
MILLENNIUM = re.compile(r"^(\d{1,2}) millennium$")


def text(value) -> Optional[str]:
    cleaned = clean_text(value)
    return cleaned or None


def texts(values) -> List[str]:
    return [cleaned for cleaned in (clean_text(value) for value in values or []) if cleaned]


def rights_uri(url: Optional[str] = None, name: Optional[str] = None) -> Optional[str]:
    """Canonical URI for a licence URL or short name; None when it cannot be recognised."""
    match = CC_URL.search(url or "")
    if match:
        kind, code, version = match.group(1).lower(), match.group(2).lower(), match.group(3)
        if kind == "publicdomain":
            return PUBLIC_DOMAIN if code == "mark" else CC0
        return f"http://creativecommons.org/licenses/{code}/{version}/"
    value = (name or "").strip().lower()
    if value in {"public domain", "domaine public", "pdm", "public domain mark"}:
        return PUBLIC_DOMAIN
    if value in {"cc0", "cc0 1.0", "cc-zero"}:
        return CC0
    if value in {"droits réservés", "all rights reserved", "in copyright"}:
        return IN_COPYRIGHT
    match = CC_NAME.match(value)
    if match:
        return f"http://creativecommons.org/licenses/{match.group(1)}/{match.group(2)}/"
    if url and url.startswith("http"):
        return url
    return None


def year_period(raw: Optional[str], display: Optional[str] = None) -> Period:
    """Years ('1925', '1925-08'), decades ('1210s'), centuries and millennia, optionally 'BC'."""
    value = (raw or "").strip()
    shown = display if display is not None else value
    bc = value.endswith(" BC")
    core = value[:-3] if bc else value
    bounds = None
    match = YEAR.match(core)
    if match:
        year = int(match.group(1))
        bounds = (year, year)
    elif DECADE.match(core):
        start = int(DECADE.match(core).group(1))
        bounds = (start, start + 9)
    elif CENTURY.match(core):
        number = int(CENTURY.match(core).group(1))
        bounds = ((number - 1) * 100 + 1, number * 100)
    elif MILLENNIUM.match(core):
        number = int(MILLENNIUM.match(core).group(1))
        bounds = ((number - 1) * 1000 + 1, number * 1000)
    if bounds is None:
        return Period(shown, None, None, False, "none")
    first, last = bounds
    if bc:
        first, last = -last, -first
    if not (MIN_YEAR <= first <= last <= MAX_YEAR):
        return Period(shown, None, None, False, "none")
    return Period(shown, first, last, False, "source_dates")


def base_record(source: Source, snapshot: dict, record_id: str, title: str, title_lang: str) -> dict:
    """A portal record with every key of the model; connectors fill what they have."""
    return {
        "id": f"{source.id_prefix}-{record_id}",
        "source": {"id": source.id, "record_id": record_id, "url": source.record_url.format(id=record_id)},
        "title": {"value": title, "lang": title_lang},
        "titles": {},
        "description": None,
        "descriptions": {},
        "metadata_lang": title_lang,
        "creators": [],
        "date": Period("", None, None).as_dict(),
        "production_place": None,
        "find_place": None,
        "coordinates": None,
        "object_type": {"id": None, "label": None, "scheme": "portal"},
        "type_description": None,
        "media_type": "METADATA",
        "techniques": [],
        "dimensions": {"display": None, "height": None, "width": None, "length": None, "unit": None,
                       "weight": None, "weight_unit": None},
        "identifiers": {"inventory": None},
        "parts_count": None,
        "fund": None,
        "provenance": None,
        "keywords": None,
        "institution": {"id": None, "name": None, "short_name": None, "code": None, "inn": None, "country": None},
        "provider": source.id,
        "media": [],
        "media_credit": None,
        "iiif_manifest": None,
        "is_shown_at": source.record_url.format(id=record_id),
        "rights": {"uri": source.rights},
        "metadata_rights": {"uri": source.metadata_rights, "attribution": source.attribution},
        "relevance": {},
        "entities": [],
        "registered_at": None,
        "record_provenance": {
            "source": source.id,
            "snapshot_sha256": snapshot["sha256"],
            "collected_at": snapshot["collected_at"],
            "rules_version": RULES_VERSION,
        },
    }


def finish(record: dict, row: dict, entity_categories: Dict[str, str]) -> dict:
    """Add relevance from the harvester's matcher fields and the quality tiers."""
    entities = list(row.get("armenia_matched_entities") or [])
    criteria = relevance_criteria(
        list(row.get("armenia_matched_fields") or []), [entity_categories.get(entity) for entity in entities]
    )
    record["entities"] = entities
    record["relevance"] = {
        "status": RELEVANCE_STATUS.get(row.get("armenia_decision"), "candidate"),
        # Every record of a dedicated source is relevant by the source's scope (ТЗ 4.1).
        "criteria": sorted({"source", *criteria}),
        "confidence": row.get("armenia_confidence"),
        "strength": row.get("armenia_match_strength"),
        "matched_terms": list(row.get("armenia_matched_terms") or []),
        "matched_forms": list(row.get("armenia_matched_forms") or []),
        "matched_fields": list(row.get("armenia_matched_fields") or []),
        "reasons": list(row.get("armenia_match_reasons") or []),
        "negated_terms": list(row.get("armenia_negated_terms") or []),
    }
    record["quality"] = {
        "content_tier": 1 if record["media"] else 0,
        "metadata_tier": metadata_tier(record),
    }
    return record
