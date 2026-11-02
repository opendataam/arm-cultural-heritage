import json
import warnings
from dataclasses import replace

import duckdb
import pytest

from portal.pipeline import stages
from portal.settings import get_source
from portal.web.i18n import LANGUAGES, LOCALES, Translator, negotiate, plural_category

warnings.filterwarnings("ignore", category=DeprecationWarning)


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    from fastapi.testclient import TestClient

    from portal.web import app as web

    root = tmp_path_factory.mktemp("web")
    sample = root / "sample.parquet"
    duckdb.execute(
        "copy (select * from 'output/goskatalog/armenia_records.parquet' "
        "where list_contains(armenia_matched_entities, 'place.yerevan') order by id limit 80) "
        f"to '{sample}' (format parquet)"
    )
    source = replace(get_source("goskatalog"), input=sample, review_input=None, themes=())
    build = root / "build"
    stages.collect(source, build)
    stages.transform(source, build)
    stages.publish([source], build, build / "portal.sqlite", with_export=False)
    patch = pytest.MonkeyPatch()
    patch.setenv("PORTAL_BUILD_DIR", str(build))
    patch.setenv("PORTAL_DB", str(build / "portal.sqlite"))
    web.portal.__dict__.pop("service", None)
    yield TestClient(web.app)
    web.portal.__dict__.pop("service", None)
    patch.undo()


def test_root_redirects_by_accept_language(client):
    response = client.get("/", headers={"accept-language": "fr-CA,fr;q=0.9,en;q=0.5"}, follow_redirects=False)
    assert response.status_code == 302 and response.headers["location"] == "/fr/"
    # A language chosen earlier wins over the browser header (ТЗ 8.2, item 6).
    client.cookies.set("lang", "hy")
    response = client.get("/", headers={"accept-language": "fr"}, follow_redirects=False)
    assert response.headers["location"] == "/hy/"
    client.cookies.clear()


@pytest.mark.parametrize("lang", list(LANGUAGES))
def test_pages_in_every_language(client, lang):
    record_id = client.get("/api/v1/search").json()["items"][0]["id"]
    for path in ("/", "/search?q=Ереван", f"/item/{record_id}", "/entity/place.yerevan", "/collection/yerevan", "/about"):
        response = client.get(f"/{lang}{path}")
        assert response.status_code == 200, path
        assert f'<html lang="{lang}"' in response.text
        # The language switcher keeps the current page (ТЗ 8.2, item 8).
        assert f'href="/ru{path.split("?")[0]}' in response.text


def test_unknown_pages(client):
    assert client.get("/de/").status_code == 404
    assert client.get("/ru/item/gk-0").status_code == 404
    assert client.get("/api/v1/records/gk-0").json() == {"detail": "Record not found"}


def test_search_state_is_in_the_url(client):
    page = client.get("/ru/search?q=Ереван&f.media=IMAGE&sort=date_desc").text
    assert 'name="sort" data-autosubmit' in page
    assert "f.media=IMAGE" in page and "sort=date_desc" in page


def test_api_search_and_records(client):
    data = client.get("/api/v1/search", params={"q": "Yerevan", "lang": "hy"}).json()
    assert data["total"] > 0
    assert data["expanded_entities"][0] == {"id": "place.yerevan", "label": "Երևան"}
    assert {"value", "count", "label"} <= set(data["facets"]["type"][0])
    record_id = data["items"][0]["id"]

    edm = client.get(f"/api/v1/records/{record_id}", params={"format": "edm"})
    assert edm.headers["content-type"].startswith("application/ld+json")
    types = {node["@type"] for node in edm.json()["@graph"]}
    assert {"edm:ProvidedCHO", "ore:Aggregation"} <= types

    schema = client.get(f"/api/v1/records/{record_id}", params={"format": "schema"}).json()
    assert schema["@context"] == "https://schema.org" and schema["name"]


def test_iiif_manifest(client):
    data = client.get("/api/v1/search", params={"media": "1"}).json()
    record = client.get(f"/api/v1/records/{data['items'][0]['id']}").json()
    manifest = client.get(f"/iiif/3/{record['id']}/manifest").json()
    assert manifest["type"] == "Manifest"
    assert manifest["@context"] == "http://iiif.io/api/presentation/3/context.json"
    assert len(manifest["items"]) == len(record["media"])
    body = manifest["items"][0]["items"][0]["items"][0]["body"]
    assert body["id"] == record["media"][0]["url"]
    assert set(manifest["requiredStatement"]["label"]) == set(LANGUAGES)


def test_service_endpoints(client):
    assert client.get("/api/v1/suggest", params={"q": "Երև"}).json()[0]["id"] == "place.yerevan"
    assert client.get("/api/v1/stats").json()["records"] == "80"
    assert client.get("/api/v1/report").json()["published"]["records"] == 80
    assert client.get("/api/v1/institutions", params={"limit": 1}).json()["total"] >= 1


def test_locales_have_the_same_keys():
    keys = set(json.loads((LOCALES / "en.json").read_text(encoding="utf-8")))
    for lang in LANGUAGES:
        assert set(json.loads((LOCALES / f"{lang}.json").read_text(encoding="utf-8"))) == keys, lang


@pytest.mark.parametrize(
    "lang, number, category",
    [
        ("ru", 1, "one"), ("ru", 21, "one"), ("ru", 11, "many"), ("ru", 2, "few"), ("ru", 24, "few"),
        ("ru", 12, "many"), ("ru", 5, "many"), ("ru", 58291, "one"),
        ("hy", 0, "one"), ("hy", 1, "one"), ("hy", 2, "other"),
        ("fr", 0, "one"), ("fr", 2, "other"), ("fr", 1_000_000, "many"),
        ("es", 1, "one"), ("es", 0, "other"), ("en", 1, "one"), ("en", 0, "other"),
    ],
)
def test_plural_rules(lang, number, category):
    assert plural_category(lang, number) == category


def test_number_formatting_and_negotiation():
    assert Translator("en").number(58291) == "58,291"
    assert Translator("ru").number(58291) == "58 291"
    assert Translator("es").number(1428) == "1428" and Translator("es").number(58291) == "58.291"
    assert Translator("ru").plural("search.results", 3) == "3 результата"
    assert Translator("ru").century(-5) == "V век до н. э."
    assert negotiate("de-DE,de;q=0.9,es;q=0.8") == "es"
    assert negotiate(None) == "hy"
