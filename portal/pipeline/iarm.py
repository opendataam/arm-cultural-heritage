"""Index of Armenian Manuscripts connector (output of scripts/harvest_iarm.py)."""

import re

from portal.pipeline.common import base_record, finish, read_rows, text
from portal.pipeline.normalize import normalize_period
from portal.settings import Source

__all__ = ["read_rows", "transform"]

SLUG = re.compile(r"[^a-z0-9]+")


def transform(row: dict, source: Source, snapshot: dict, entity_categories: dict) -> dict:
    holder = text(row.get("location"))
    title = text(row.get("title")) or " ".join(filter(None, [holder, row.get("shelfmark")])) or row["id"]
    record = base_record(source, snapshot, row["id"], title, "en")
    record["source"]["url"] = text(row.get("permalink")) or source.homepage
    record["is_shown_at"] = record["source"]["url"]
    record["object_type"] = {"id": "manuscript", "label": "Manuscript", "scheme": "portal"}
    record["type_description"] = text(row.get("note"))
    record["techniques"] = [value.strip() for value in re.split(r"[,/]| and ", row.get("support") or "") if value.strip()]
    record["dimensions"]["display"] = "; ".join(filter(None, [text(row.get("size")), text(row.get("extent"))])) or None
    record["date"] = normalize_period(row.get("date"), None, None).as_dict()
    record["keywords"] = text(row.get("genre")) if row.get("genre") not in (None, "", "Undefined") else None
    record["fund"] = text(row.get("digital_library"))
    record["identifiers"] = {
        "inventory": text(row.get("shelfmark")),
        "siglum": text(row.get("siglum")),
    }
    if holder:
        place = ", ".join(filter(None, [text(row.get("town")), text(row.get("country"))]))
        record["institution"] = {
            "id": f"{source.id_prefix}-{SLUG.sub('-', holder.lower()).strip('-')}",
            "name": f"{holder} ({place})" if place else holder,
            "short_name": holder,
            "code": None,
            "inn": None,
            "country": text(row.get("country")),
        }
    record["iiif_manifest"] = text(row.get("iiif_manifest"))
    # Images stay with the holding libraries under their own terms; the portal links to them.
    return finish(record, row, entity_categories)
