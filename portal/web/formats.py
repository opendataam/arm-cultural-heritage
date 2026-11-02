"""Record serializations: EDM JSON-LD, schema.org and IIIF Presentation 3.0 (ТЗ 6.4, 10, 12.7)."""

from typing import Callable, Dict, List

from portal.settings import get_source
from portal.web.i18n import LANGUAGES, Translator

CNE = "http://rightsstatements.org/vocab/CNE/1.0/"
EDM_CONTEXT = {
    "edm": "http://www.europeana.eu/schemas/edm/",
    "ore": "http://www.openarchives.org/ore/terms/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "edm:aggregatedCHO": {"@type": "@id"},
    "edm:isShownAt": {"@type": "@id"},
    "edm:isShownBy": {"@type": "@id"},
    "edm:hasView": {"@type": "@id"},
    "edm:rights": {"@type": "@id"},
    "dcterms:spatial": {"@type": "@id"},
    "dcterms:temporal": {"@type": "@id"},
    "dc:subject": {"@type": "@id"},
}
EDM_CLASSES = {"place": "edm:Place", "person": "edm:Agent", "organization": "foaf:Organization"}
SCHEMA_TYPES = {"1": "Painting", "2": "VisualArtwork", "3": "Sculpture", "14": "Book", "17": "Photograph"}
TEXT_TYPES = {"9", "14", "15", "16"}
# Canvas size for images whose dimensions are not yet measured by the media stage (ТЗ 6.10).
NOMINAL_CANVAS = 1000


def _literal(value: str, lang: str) -> dict:
    return {"@value": value, "@language": lang}


def _edm_type(record: dict) -> str:
    if record["media_type"] == "TEXT" or record["object_type"]["id"] in TEXT_TYPES:
        return "TEXT"
    return "IMAGE"


def edm(record: dict, base: str, entities: Dict[str, dict]) -> dict:
    """The record as Europeana Data Model in JSON-LD."""
    lang = record["metadata_lang"]
    cho = f"{base}/item/{record['id']}"
    aggregation = f"{base}/aggregation/{record['id']}"
    date = record["date"]
    linked = [entities[e] for e in record["entities"] if e in entities]
    provided = {
        "@id": cho,
        "@type": "edm:ProvidedCHO",
        "dc:title": _literal(record["title"]["value"], lang),
        "edm:type": _edm_type(record),
        "dc:identifier": [v for v in [record["id"], *record["identifiers"].values()] if v],
    }
    optional = {
        "dc:description": record["description"] and _literal(record["description"], lang),
        "dc:creator": [_literal(c["name"], lang) for c in record["creators"]],
        "dc:type": record["object_type"]["label"] and _literal(record["object_type"]["label"], lang),
        "dcterms:created": date["display"] and _literal(date["display"], lang),
        "dcterms:temporal": f"{cho}#timespan" if date["edtf"] else None,
        "dcterms:medium": [_literal(t, lang) for t in record["techniques"]],
        "dcterms:extent": record["dimensions"]["display"] and _literal(record["dimensions"]["display"], lang),
        "dcterms:provenance": record["provenance"] and _literal(record["provenance"], lang),
        "dcterms:spatial": [f"{base}/entity/{e['id']}" for e in linked if e["kind"] == "place"],
        "dc:subject": [f"{base}/entity/{e['id']}" for e in linked if e["kind"] != "place"],
        "edm:currentLocation": record["institution"]["name"],
    }
    provided.update({k: v for k, v in optional.items() if v})
    media = [m["url"] for m in record["media"]]
    aggregation_node = {
        "@id": aggregation,
        "@type": "ore:Aggregation",
        "edm:aggregatedCHO": cho,
        "edm:dataProvider": record["institution"]["name"],
        "edm:provider": get_source(record["source"]["id"]).label("en"),
        "edm:isShownAt": record["is_shown_at"],
        "edm:rights": record["rights"]["uri"],
    }
    if media:
        aggregation_node["edm:isShownBy"] = media[0]
        if media[1:]:
            aggregation_node["edm:hasView"] = media[1:]
    graph: List[dict] = [provided, aggregation_node]
    graph += [{"@id": url, "@type": "edm:WebResource", "edm:rights": record["rights"]["uri"]} for url in media]
    if date["edtf"]:
        graph.append({
            "@id": f"{cho}#timespan",
            "@type": "edm:TimeSpan",
            "skos:prefLabel": _literal(date["display"] or date["edtf"], lang),
            "edm:begin": str(date["year_from"]),
            "edm:end": str(date["year_to"]),
            "skos:notation": {"@value": date["edtf"], "@type": "http://id.loc.gov/datatypes/edtf/EDTF"},
        })
    for entity in linked:
        graph.append({
            "@id": f"{base}/entity/{entity['id']}",
            "@type": EDM_CLASSES.get(entity["kind"], "skos:Concept"),
            "skos:prefLabel": [_literal(value, code) for code, value in entity["labels"].items()],
        })
    return {"@context": EDM_CONTEXT, "@graph": graph}


def schema_org(record: dict, page_url: str, entities: Dict[str, dict], lang: str) -> dict:
    """schema.org markup for search engines (ТЗ 12.7)."""
    linked = [entities[e] for e in record["entities"] if e in entities]
    label = lambda e: e["labels"].get(lang) or e["labels"].get("en") or next(iter(e["labels"].values()), e["id"])
    data = {
        "@context": "https://schema.org",
        "@type": SCHEMA_TYPES.get(record["object_type"]["id"], "CreativeWork"),
        "@id": page_url,
        "url": page_url,
        "name": record["title"]["value"],
        "inLanguage": record["metadata_lang"],
        "identifier": [v for v in record["identifiers"].values() if v],
        "sameAs": record["source"]["url"],
        "image": [m["url"] for m in record["media"]],
        "creator": [{"@type": "Person", "name": c["name"]} for c in record["creators"]],
        "material": record["techniques"],
        "temporalCoverage": record["date"]["edtf"],
        "contentLocation": [{"@type": "Place", "name": label(e)} for e in linked if e["kind"] == "place"],
        "about": [{"@type": "Thing", "name": label(e)} for e in linked if e["kind"] != "place"],
        "description": record["description"],
        "provider": {"@type": "Museum", "name": record["institution"]["name"]},
    }
    return {k: v for k, v in data.items() if v}


def _label_map(key: str) -> Dict[str, List[str]]:
    return {code: [Translator(code)(key)] for code in LANGUAGES}


def iiif_manifest(record: dict, base: str, page_url: Callable[[str], str]) -> dict:
    """IIIF Presentation 3.0 manifest, also for external images without one (ТЗ 6.10, item 2)."""
    lang = record["metadata_lang"]
    manifest_id = f"{base}/iiif/3/{record['id']}/manifest"
    metadata = []
    for key, value in (
        ("field.creator", "; ".join(c["name"] for c in record["creators"])),
        ("field.date", record["date"]["display"]),
        ("field.object_type", record["object_type"]["label"]),
        ("field.technique", ", ".join(record["techniques"])),
        ("field.dimensions", record["dimensions"]["display"]),
        ("field.inventory", record["identifiers"]["inventory"]),
        ("field.institution", record["institution"]["name"]),
    ):
        if value:
            metadata.append({"label": _label_map(key), "value": {lang: [value]}})
    canvases = []
    for number, media in enumerate(record["media"], start=1):
        canvas_id = f"{manifest_id}/canvas/{number}"
        canvases.append({
            "id": canvas_id,
            "type": "Canvas",
            "label": {"none": [str(number)]},
            "height": NOMINAL_CANVAS,
            "width": NOMINAL_CANVAS,
            "items": [{
                "id": f"{canvas_id}/page",
                "type": "AnnotationPage",
                "items": [{
                    "id": f"{canvas_id}/page/painting",
                    "type": "Annotation",
                    "motivation": "painting",
                    "body": {"id": media["url"], "type": "Image", "format": "image/jpeg"},
                    "target": canvas_id,
                }],
            }],
        })
    source = get_source(record["source"]["id"])
    manifest = {
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": manifest_id,
        "type": "Manifest",
        "label": {lang: [record["title"]["value"]]},
        "metadata": metadata,
        "requiredStatement": {"label": _label_map("field.institution"), "value": {lang: [record["institution"]["name"]]}},
        "rights": record["rights"]["uri"],
        "homepage": [{
            "id": page_url(record["id"]),
            "type": "Text",
            "label": {lang: [record["title"]["value"]]},
            "format": "text/html",
        }],
        "seeAlso": [{
            "id": f"{base}/api/v1/records/{record['id']}?format=edm",
            "type": "Dataset",
            "format": "application/ld+json",
            "profile": "http://www.europeana.eu/schemas/edm/",
        }],
        "provider": [{
            "id": source.homepage,
            "type": "Agent",
            "label": {code: [source.label(code)] for code in LANGUAGES},
            "homepage": [{"id": source.homepage, "type": "Text", "label": {"en": [source.label("en")]}, "format": "text/html"}],
        }],
        "items": canvases,
    }
    if record["description"]:
        manifest["summary"] = {lang: [record["description"][:1000]]}
    if record["media"]:
        manifest["thumbnail"] = [{"id": record["media"][0]["url"], "type": "Image", "format": "image/jpeg"}]
    return manifest
