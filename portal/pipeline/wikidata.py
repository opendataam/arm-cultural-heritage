"""Wikidata monuments connector (output of scripts/harvest_wikidata.py)."""

from urllib.parse import quote

from portal.pipeline.common import base_record, finish, read_rows, rights_uri, text, year_period
from portal.settings import Source

__all__ = ["read_rows", "transform"]

# Armenian first: most monuments have their fullest label in Armenian.
TITLE_ORDER = ("hy", "en", "ru", "fr", "es")
IMAGE_URL = "https://commons.wikimedia.org/wiki/Special:FilePath/{name}?width=1600"
FILE_PAGE = "https://commons.wikimedia.org/wiki/File:{name}"


def _labels(value) -> dict:
    """Parquet maps arrive as lists of (key, value) pairs."""
    if isinstance(value, dict):
        return value
    return dict(value or [])


def _pick(labels: dict, order=TITLE_ORDER):
    for code in order:
        if labels.get(code):
            return labels[code], code
    return next(iter(labels.items()), (None, None))


def transform(row: dict, source: Source, snapshot: dict, entity_categories: dict) -> dict:
    labels = {code: value for code, value in _labels(row.get("labels")).items() if text(value)}
    descriptions = {code: value for code, value in _labels(row.get("descriptions")).items() if text(value)}
    title, lang = _pick(labels)
    record = base_record(source, snapshot, row["id"], title or row["id"], lang or "en")
    record["titles"] = labels
    record["descriptions"] = descriptions
    record["description"], _ = _pick(descriptions, (lang, *TITLE_ORDER)) if descriptions else (None, None)
    types = [_labels(entry["labels"]) for entry in row.get("types") or []]
    places = [_labels(entry["labels"]) for entry in row.get("places") or []]
    designations = [_labels(entry["labels"]) for entry in row.get("designations") or []]
    record["object_type"] = {"id": "monument", "label": "Monument", "scheme": "portal"}
    record["type_description"] = "; ".join(filter(None, (_pick(names, (lang, *TITLE_ORDER))[0] for names in types))) or None
    record["production_place"] = "; ".join(filter(None, (_pick(names, (lang, *TITLE_ORDER))[0] for names in places))) or None
    record["keywords"] = "; ".join(filter(None, (_pick(names, (lang, *TITLE_ORDER))[0] for names in designations))) or None
    # An empty display lets the site render the years in the interface language.
    record["date"] = year_period(row.get("inception"), display="").as_dict()
    if row.get("latitude") is not None and row.get("longitude") is not None:
        record["coordinates"] = {"lat": round(row["latitude"], 6), "lon": round(row["longitude"], 6)}
    record["identifiers"] = {"inventory": None, "wikidata": row["id"], "wlm": text(row.get("wlm_id"))}
    if row.get("image"):
        name = row["image"].replace(" ", "_")
        record["media"] = [{"url": IMAGE_URL.format(name=quote(name)), "type": "image", "page": FILE_PAGE.format(name=quote(name))}]
        record["media_type"] = "IMAGE"
        credit = ", ".join(filter(None, [text(row.get("image_artist")), text(row.get("image_licence"))]))
        record["media_credit"] = f"{credit} · Wikimedia Commons" if credit else "Wikimedia Commons"
        record["rights"] = {"uri": rights_uri(row.get("image_licence_url"), row.get("image_licence")) or source.rights}
    record["registered_at"] = row.get("modified")
    return finish(record, row, entity_categories)
