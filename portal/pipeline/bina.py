"""BULAC BiNA connector (output of scripts/harvest_bina.py)."""

from portal.pipeline.common import IN_COPYRIGHT, base_record, finish, read_rows, rights_uri, text, texts, year_period
from portal.pipeline.normalize import parse_creator
from portal.settings import Source
from portal.text import script_of

__all__ = ["read_rows", "transform"]

TYPES = {"Périodique": ("periodical", "Périodique"), "Imprimé": ("book", "Imprimé")}


def transform(row: dict, source: Source, snapshot: dict, entity_categories: dict) -> dict:
    titles = texts(row.get("title"))
    descriptions = texts(row.get("description"))
    main_title = titles[0] if titles else row["id"]
    # Monthly batches of one newspaper share a title, so the issue range tells them apart.
    if row.get("type") == "Périodique" and descriptions:
        main_title = f"{main_title}, {descriptions[0]}"
    record = base_record(source, snapshot, row["id"], main_title, "hy" if script_of(main_title) == "Armn" else "fr")
    record["metadata_lang"] = "fr"
    if len(titles) > 1:
        record["titles"] = {"hy-Latn": titles[1]}
    record["description"] = "\n".join(descriptions[1:] if row.get("type") == "Périodique" else descriptions) or None
    record["creators"] = [creator for creator in map(parse_creator, texts(row.get("creator"))) if creator]
    record["date"] = year_period(row.get("date")).as_dict()
    type_id, label = TYPES.get(row.get("type"), ("book", row.get("type")))
    record["object_type"] = {"id": type_id, "label": label, "scheme": "portal"}
    record["dimensions"]["display"] = text(row.get("format"))
    record["provenance"] = "; ".join(texts(row.get("publisher"))) or None
    record["keywords"] = "; ".join(texts(row.get("subject"))) or None
    record["identifiers"] = {"inventory": text(row.get("shelfmark")), "ark": text(row.get("ark"))}
    record["institution"] = {
        "id": f"{source.id_prefix}-bulac",
        "name": text(row.get("located_at")) or "Bibliothèque universitaire des langues et civilisations",
        "short_name": "BULAC",
        "code": None,
        "inn": None,
        "country": "FR",
    }
    record["is_shown_at"] = text(row.get("item_url")) or record["source"]["url"]
    record["iiif_manifest"] = text(row.get("iiif_manifest"))
    rights = rights_uri(row.get("license"), row.get("rights")) or source.rights
    record["rights"] = {"uri": rights}
    record["media_type"] = "TEXT" if (row.get("media_count") or 0) > 1 else "IMAGE"
    # Thumbnails are shown only for openly licensed items; in-copyright items are linked.
    if row.get("thumbnail") and rights != IN_COPYRIGHT:
        record["media"] = [{"url": row["thumbnail"], "type": "image"}]
        record["media_credit"] = "BULAC – BiNA"
    else:
        record["media_type"] = "METADATA"
    record["parts_count"] = row.get("media_count")
    record["registered_at"] = row.get("modified")
    return finish(record, row, entity_categories)
