"""Public site and API (ТЗ 7, 10). Run: `uvicorn portal.web.app:app`."""

import json
from datetime import date
from functools import cached_property
from pathlib import Path
from typing import Dict, List, Literal, Optional
from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException, Query as Param, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from portal import __version__
from portal.pipeline.entities import LABEL_FALLBACKS
from portal.search import FACET_FIELDS, FILTER_ONLY_FIELDS, PAGE_SIZES, SORTS, Query, SearchService
from portal.settings import build_dir, db_path, get_source, load_collections, load_sources
from portal.text import title_case
from portal.web import formats
from portal.web.i18n import DEFAULT_LANGUAGE, LANGUAGES, Translator, negotiate

HERE = Path(__file__).parent
REPOSITORY = "https://github.com/opendataam/arm-cultural-heritage"
EXAMPLE_QUERIES = ["Сарьян", "Komitas", "Երևան", "хачкар", "Ani", "\"армянская церковь\""]
COOKIE = "lang"
SOURCE_LANG_FIELDS = {"creator", "technique", "institution"}

app = FastAPI(
    title="Armenian Cultural Heritage API",
    version=__version__,
    description="MVP API of the Armenian cultural heritage portal: search with facets, records in EDM and "
    "schema.org JSON-LD, entities, institutions and IIIF Presentation 3.0 manifests.",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"])
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
app.mount("/dumps", StaticFiles(directory=build_dir() / "export", check_dir=False), name="dumps")
templates = Jinja2Templates(directory=HERE / "templates")
templates.env.filters["title_case"] = title_case


class Portal:
    """Lazily opened search service, so the app starts before the index is built."""

    @cached_property
    def service(self) -> Optional[SearchService]:
        path = db_path()
        return SearchService(path) if path.exists() else None


portal = Portal()


def service() -> SearchService:
    if portal.service is None:
        raise HTTPException(status_code=503, detail="index-missing")
    return portal.service


# --- Request state ---------------------------------------------------------------


def _int(value: Optional[str]) -> Optional[int]:
    try:
        return int(value) if value not in (None, "") else None
    except ValueError:
        return None


def query_from_request(request: Request, fixed: Optional[Dict[str, List[str]]] = None) -> Query:
    params = request.query_params
    filters: Dict[str, List[str]] = {}
    for name in (*FACET_FIELDS, *FILTER_ONLY_FIELDS):
        values = params.getlist(f"f.{name}")
        if values:
            filters[name] = values
    for name, values in (fixed or {}).items():
        filters[name] = list(dict.fromkeys([*filters.get(name, []), *values]))
    return Query.build(
        q=params.get("q", ""),
        filters=filters,
        year_from=_int(params.get("yf")),
        year_to=_int(params.get("yt")),
        media_only=params.get("media") == "1",
        sort=params.get("sort", "relevance"),
        page=_int(params.get("page")) or 1,
        size=_int(params.get("size")) or PAGE_SIZES[0],
    )


def state_params(query: Query, fixed: Optional[Dict[str, List[str]]] = None, **changes) -> List[tuple]:
    """URL parameters of a search state (ТЗ 7.1, item 7). Fixed filters live in the path."""
    state = {
        "q": query.q,
        "filters": query.filter_dict(),
        "yf": query.year_from,
        "yt": query.year_to,
        "media": query.media_only,
        "sort": query.sort,
        "page": query.page,
        "size": query.size,
    }
    if any(key != "page" for key in changes):
        state["page"] = 1
    state.update(changes)
    params = []
    if state["q"]:
        params.append(("q", state["q"]))
    for name, values in sorted(state["filters"].items()):
        for value in values:
            if value not in (fixed or {}).get(name, []):
                params.append((f"f.{name}", value))
    for key in ("yf", "yt"):
        if state[key] is not None:
            params.append((key, state[key]))
    if state["media"]:
        params.append(("media", "1"))
    if state["sort"] != "relevance":
        params.append(("sort", state["sort"]))
    if state["size"] != PAGE_SIZES[0]:
        params.append(("size", state["size"]))
    if state["page"] > 1:
        params.append(("page", state["page"]))
    return params


class View:
    """Template helpers bound to the request language."""

    def __init__(self, request: Request, lang: str):
        self.request = request
        self.lang = lang
        self.t = Translator(lang)
        self.service = portal.service

    def url(self, path: str = "/", lang: Optional[str] = None) -> str:
        return f"/{lang or self.lang}{path}"

    def switch_url(self, lang: str) -> str:
        path = self.request.url.path
        parts = path.split("/", 2)
        rest = "/" + parts[2] if len(parts) > 2 else "/"
        query = self.request.url.query
        return f"/{lang}{rest}" + (f"?{query}" if query else "")

    def _entity_name(self, entity_id: str):
        entity = self.service.entities.get(entity_id) if self.service else None
        if not entity:
            return entity_id, self.lang
        for code in LABEL_FALLBACKS.get(self.lang, (self.lang, "en", "ru")):
            if code in entity["labels"]:
                return entity["labels"][code], code
        return next(iter(entity["labels"].items()), (entity_id, self.lang))

    def title(self, record: dict) -> dict:
        """Title in the interface language when the source provides one (ТЗ 8.2)."""
        titles = record.get("titles") or {}
        if titles.get(self.lang):
            return {"value": titles[self.lang], "lang": self.lang}
        return record["title"]

    def description(self, record: dict) -> dict:
        descriptions = record.get("descriptions") or {}
        if descriptions.get(self.lang):
            return {"value": descriptions[self.lang], "lang": self.lang}
        return {"value": record.get("description"), "lang": record["metadata_lang"]}

    def rights(self, uri: str) -> str:
        return formats.rights_key(uri)

    def entity_label(self, entity_id: str) -> str:
        return self._entity_name(entity_id)[0]

    def entity_lang(self, entity_id: str) -> str:
        return self._entity_name(entity_id)[1]

    def facet_label(self, name: str, value: str) -> str:
        t = self.t
        if name == "media":
            return t(f"media.{value}")
        if name == "type":
            return t(f"typology.{value}", default=value)
        if name == "theme":
            return t(f"theme.{value}", default=value)
        if name == "century":
            return t.century(int(value))
        if name in ("place", "person", "concept", "entity"):
            return self.entity_label(value)
        if name == "institution":
            institution = self.service.institutions.get(value) if self.service else None
            return institution["short_name"] or institution["name"] if institution else value
        if name == "criteria":
            return t(f"criteria.{value}")
        if name == "rights":
            return t(f"rights.{formats.rights_key(value)}")
        if name == "source":
            return get_source(value).label(self.lang)
        return value

    def facet_lang(self, name: str, value: str) -> Optional[str]:
        """`lang` attribute for values that are not in the interface language (ТЗ 8.2, item 5)."""
        if name in SOURCE_LANG_FIELDS:
            return "ru"
        if name in ("place", "person", "concept", "entity"):
            return self.entity_lang(value)
        return None

    def date(self, record_date: dict) -> str:
        if record_date["display"]:
            return record_date["display"]
        if record_date["year_from"] is None:
            return ""
        first, last = self.t.year(record_date["year_from"]), self.t.year(record_date["year_to"])
        return first if first == last else f"{first}–{last}"

    def number(self, value) -> str:
        return self.t.number(int(value))


def render(request: Request, lang: str, template: str, status_code: int = 200, **context):
    view = View(request, lang)
    meta = view.service.meta if view.service else {}
    response = templates.TemplateResponse(
        request,
        template,
        {
            "v": view,
            "t": view.t,
            "lang": lang,
            "languages": LANGUAGES,
            "meta": meta,
            "repository": REPOSITORY,
            **context,
        },
        status_code=status_code,
    )
    response.set_cookie(COOKIE, lang, max_age=365 * 24 * 3600, samesite="lax")
    return response


def check_lang(lang: str) -> str:
    if lang not in LANGUAGES:
        raise HTTPException(status_code=404)
    return lang


# --- Pages ---------------------------------------------------------------------


@app.get("/", include_in_schema=False)
def root(request: Request):
    lang = request.cookies.get(COOKIE)
    if lang not in LANGUAGES:
        lang = negotiate(request.headers.get("accept-language"))
    return RedirectResponse(f"/{lang}/", status_code=302)


@app.get("/{lang}/", include_in_schema=False)
def home(request: Request, lang: str):
    check_lang(lang)
    search = service()
    overview = search.search(Query.build(), facet_limit=10)
    collections = []
    for collection in load_collections():
        query = Query.build(filters=collection["filters"], media_only=True)
        total = search.search(Query.build(filters=collection["filters"]), with_facets=False)["total"]
        cover = search.sample(query)
        collections.append({**collection, "total": total, "cover": cover[0] if cover else None})
    with_media = search.orders["browse"][: int(search.meta["with_media"])]
    featured = None
    if with_media:
        rowid = with_media[date.today().toordinal() % len(with_media)]
        featured = search.docs([rowid])[0]
    return render(
        request, lang, "home.html",
        overview=overview, collections=collections, featured=featured, examples=EXAMPLE_QUERIES,
    )


def render_search(request: Request, lang: str, fixed: Optional[Dict[str, List[str]]] = None, **context):
    search = service()
    query = query_from_request(request, fixed)
    result = search.search(query)
    path = request.url.path

    def link(**changes) -> str:
        params = state_params(query, fixed, **changes)
        return path + ("?" + urlencode(params) if params else "")

    def toggle(name: str, value: str) -> str:
        filters = query.filter_dict()
        values = filters.get(name, [])
        filters[name] = [v for v in values if v != value] if value in values else [*values, value]
        return link(filters={k: v for k, v in filters.items() if v})

    selected = [
        (name, value) for name, values in query.filters for value in values
        if value not in (fixed or {}).get(name, [])
    ]
    return render(
        request, lang, context.pop("template", "search.html"),
        query=query, result=result, link=link, toggle=toggle, selected=selected,
        fixed=fixed or {}, sorts=SORTS, sizes=PAGE_SIZES, facet_fields=FACET_FIELDS, **context,
    )


@app.get("/{lang}/search", include_in_schema=False)
def search_page(request: Request, lang: str):
    check_lang(lang)
    return render_search(request, lang)


@app.get("/{lang}/collection/{slug}", include_in_schema=False)
def collection_page(request: Request, lang: str, slug: str):
    check_lang(lang)
    collection = next((c for c in load_collections() if c["slug"] == slug), None)
    if collection is None:
        raise HTTPException(status_code=404)
    return render_search(request, lang, fixed=collection["filters"], collection=collection)


@app.get("/{lang}/entity/{entity_id}", include_in_schema=False)
def entity_page(request: Request, lang: str, entity_id: str):
    check_lang(lang)
    entity = service().entities.get(entity_id)
    if entity is None:
        raise HTTPException(status_code=404)
    return render_search(request, lang, fixed={"entity": [entity_id]}, entity=entity)


@app.get("/{lang}/institution/{institution_id}", include_in_schema=False)
def institution_page(request: Request, lang: str, institution_id: str):
    check_lang(lang)
    institution = service().institutions.get(institution_id)
    if institution is None:
        raise HTTPException(status_code=404)
    return render_search(
        request, lang, fixed={"institution": [institution_id]}, institution=institution,
        source=get_source(institution["source"]),
    )


@app.get("/{lang}/item/{record_id}", include_in_schema=False)
def item_page(request: Request, lang: str, record_id: str):
    check_lang(lang)
    search = service()
    record = search.record(record_id)
    if record is None:
        raise HTTPException(status_code=404)
    base = str(request.base_url).rstrip("/")
    page_url = f"{base}/{lang}/item/{record_id}"
    return render(
        request, lang, "item.html",
        record=record,
        similar=search.similar(record),
        entities=[search.entities[e] for e in record["entities"] if e in search.entities],
        source=get_source(record["source"]["id"]),
        page_url=page_url,
        manifest_url=f"{base}/iiif/3/{record_id}/manifest",
        schema=formats.schema_org(record, page_url, search.entities, lang),
    )


@app.get("/{lang}/about", include_in_schema=False)
def about_page(request: Request, lang: str):
    check_lang(lang)
    search = service()
    candidates = sum(
        (s.get("transform") or {}).get("candidates_not_published") or 0
        for s in (_report() or {}).get("sources", {}).values()
    )
    return render(request, lang, "about.html", candidates=candidates, sources=load_sources(), stats=search.meta)


# --- API -----------------------------------------------------------------------


def _report() -> Optional[dict]:
    path = build_dir() / "report.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _api_lang(lang: Optional[str]) -> str:
    return lang if lang in LANGUAGES else "en"


@app.get("/api/v1/search", tags=["search"])
def api_search(
    request: Request,
    q: str = Param("", description="Query: words, \"phrases\", -exclusions, OR, prefix*"),
    sort: str = Param("relevance", description="relevance, date_asc, date_desc or title"),
    page: int = Param(1, ge=1),
    size: int = Param(PAGE_SIZES[0], description=f"One of {PAGE_SIZES}"),
    yf: Optional[int] = Param(None, description="Created in or after this year (negative for BC)"),
    yt: Optional[int] = Param(None, description="Created in or before this year"),
    media: Optional[str] = Param(None, description="1 to return only records with a digital object"),
    lang: str = Param("en", description="Language of facet and entity labels"),
):
    """Search with facets. Filter with repeatable `f.<field>=<value>` parameters, e.g. `f.type=17`.

    Fields: media, type, century, place, person, concept, creator, institution, technique,
    criteria, rights, source and entity.
    """
    search = service()
    query = query_from_request(request)
    result = search.search(query)
    view = View(request, _api_lang(lang))
    return {
        "total": result["total"],
        "page": result["page"],
        "pages": result["pages"],
        "size": result["size"],
        "items": result["items"],
        "facets": {
            name: [{"value": v, "count": n, "label": view.facet_label(name, v)} for v, n in values]
            for name, values in result["facets"].items()
        },
        "expanded_entities": [{"id": e, "label": view.entity_label(e)} for e in result["expanded_entities"]],
    }


@app.get("/api/v1/records/{record_id}", tags=["records"])
def api_record(
    request: Request,
    record_id: str,
    format: Literal["json", "edm", "schema"] = Param("json", description="Portal JSON, EDM JSON-LD or schema.org"),
):
    """A published record in the portal model, EDM JSON-LD or schema.org JSON-LD."""
    search = service()
    record = search.record(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    base = str(request.base_url).rstrip("/")
    if format == "edm":
        return JSONResponse(formats.edm(record, base, search.entities), media_type="application/ld+json")
    if format == "schema":
        page_url = f"{base}/{DEFAULT_LANGUAGE}/item/{record_id}"
        return JSONResponse(formats.schema_org(record, page_url, search.entities, "en"), media_type="application/ld+json")
    return record


@app.get("/api/v1/entities/{entity_id}", tags=["entities"])
def api_entity(entity_id: str):
    """An entity with labels, name variants and the number of linked records."""
    entity = service().entities.get(entity_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@app.get("/api/v1/suggest", tags=["entities"])
def api_suggest(request: Request, q: str = Param(..., min_length=1), lang: str = "en", limit: int = Param(8, le=20)):
    """Autocomplete over entity names in all languages (ТЗ 7.4)."""
    view = View(request, _api_lang(lang))
    return [
        {**item, "label": view.entity_label(item["id"]), "kind": service().entities[item["id"]]["kind"]}
        for item in service().suggest(q, limit)
    ]


@app.get("/api/v1/institutions", tags=["institutions"])
def api_institutions(limit: int = Param(100, le=2000), offset: int = Param(0, ge=0)):
    """Holding institutions ordered by the number of published records."""
    items = sorted(service().institutions.values(), key=lambda i: (-i["record_count"], i["id"]))
    return {"total": len(items), "items": items[offset : offset + limit]}


@app.get("/api/v1/institutions/{institution_id}", tags=["institutions"])
def api_institution(institution_id: str):
    institution = service().institutions.get(institution_id)
    if institution is None:
        raise HTTPException(status_code=404, detail="Institution not found")
    return institution


@app.get("/api/v1/stats", tags=["service"])
def api_stats():
    """Corpus statistics of the current publication."""
    meta = dict(service().meta)
    meta["sources"] = json.loads(meta.get("sources", "{}"))
    return meta


@app.get("/api/v1/report", tags=["service"])
def api_report():
    """Metadata of the latest pipeline run: volumes, checksums, rule versions, checks (ТЗ 5.5, item 6)."""
    report = _report()
    if report is None:
        raise HTTPException(status_code=404, detail="No pipeline run yet")
    return report


@app.get("/iiif/3/{record_id}/manifest", tags=["iiif"])
def iiif_manifest(request: Request, record_id: str):
    """IIIF Presentation API 3.0 manifest of a record."""
    record = service().record(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    base = str(request.base_url).rstrip("/")
    manifest = formats.iiif_manifest(record, base, lambda rid: f"{base}/{DEFAULT_LANGUAGE}/item/{rid}")
    return JSONResponse(
        manifest,
        media_type='application/ld+json;profile="http://iiif.io/api/presentation/3/context.json"',
    )


@app.get("/robots.txt", include_in_schema=False)
def robots():
    return Response("User-agent: *\nDisallow: /api/\n", media_type="text/plain")


# --- Errors --------------------------------------------------------------------


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    path = request.url.path
    if path.startswith(("/api/", "/iiif/", "/dumps/", "/static/")):
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
    segment = path.split("/")[1] if path.count("/") >= 1 else ""
    lang = segment if segment in LANGUAGES else negotiate(request.headers.get("accept-language"))
    if exc.detail == "index-missing":
        return render(request, lang, "error.html", status_code=503, message_key="error.no_index")
    return render(request, lang, "error.html", status_code=exc.status_code, message_key="error.not_found_text")
