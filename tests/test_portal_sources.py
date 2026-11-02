import warnings
from dataclasses import replace

import duckdb
import pytest

from portal.pipeline import stages
from portal.pipeline.common import CC0, IN_COPYRIGHT, PUBLIC_DOMAIN, rights_uri, year_period
from portal.search import Query, SearchService
from portal.settings import get_source, load_sources
from portal.web.formats import rights_key

warnings.filterwarnings("ignore", category=DeprecationWarning)

SAMPLES = {
    "goskatalog": "select * from 'output/goskatalog/armenia_records.parquet' "
                  "where list_contains(armenia_matched_entities, 'place.yerevan') order by id limit 40",
    "wikidata": "select * from 'output/wikidata/records.parquet' "
                "where image is not null and map_contains(labels, 'fr') order by id limit 40",
    "bulac": "select * from 'output/bulac/records.parquet' order by id limit 40",
    "iarm": "select * from 'output/iarm/records.parquet' order by id limit 40",
}


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """A publication with real rows from every registered source."""
    root = tmp_path_factory.mktemp("sources")
    build = root / "build"
    sources = []
    for source in load_sources():
        sample = root / f"{source.id}.parquet"
        duckdb.execute(f"copy ({SAMPLES[source.id]}) to '{sample}' (format parquet)")
        source = replace(source, input=sample, review_input=None, themes=())
        stages.collect(source, build)
        stages.transform(source, build)
        sources.append(source)
    report = stages.publish(sources, build, build / "portal.sqlite", with_export=False)
    return {"build": build, "report": report, "service": SearchService(build / "portal.sqlite")}


@pytest.fixture(scope="module")
def client(built):
    from fastapi.testclient import TestClient

    from portal.web import app as web

    patch = pytest.MonkeyPatch()
    patch.setenv("PORTAL_BUILD_DIR", str(built["build"]))
    patch.setenv("PORTAL_DB", str(built["build"] / "portal.sqlite"))
    web.portal.__dict__.pop("service", None)
    yield TestClient(web.app)
    web.portal.__dict__.pop("service", None)
    patch.undo()


def test_rights_and_dates_are_normalized():
    assert rights_uri("https://creativecommons.org/licenses/by-nc/4.0/deed.fr") == "http://creativecommons.org/licenses/by-nc/4.0/"
    assert rights_uri("https://creativecommons.org/publicdomain/mark/1.0/deed.fr") == PUBLIC_DOMAIN
    assert rights_uri(name="CC BY-SA 3.0") == "http://creativecommons.org/licenses/by-sa/3.0/"
    assert rights_uri(name="Droits réservés") == IN_COPYRIGHT
    assert rights_uri(name="CC0") == CC0
    assert rights_uri() is None
    assert rights_key("https://creativecommons.org/licenses/by-sa/4.0/") == "CC-BY-SA"
    assert rights_key("http://example.org/terms") == "other"
    assert (year_period("1925-08").year_from, year_period("1925-08").year_to) == (1925, 1925)
    assert (year_period("1210s").year_from, year_period("1210s").year_to) == (1210, 1219)
    assert (year_period("13 century").year_from, year_period("13 century").year_to) == (1201, 1300)
    assert (year_period("800 BC").year_from, year_period("800 BC").year_to) == (-800, -800)
    assert year_period("unknown").year_from is None


def test_every_source_is_published(built):
    published = {source_id: data["published"] for source_id, data in built["report"]["sources"].items()}
    assert set(published) == {source.id for source in load_sources()}
    assert all(count == 40 for count in published.values())
    facets = dict(built["service"].search(Query.build())["facets"]["source"])
    assert facets == {source_id: 40 for source_id in published}


def test_records_carry_source_specific_rights(built):
    service = built["service"]
    bina = service.search(Query.build(filters={"source": ["bulac"]}), with_facets=False)["items"]
    assert {item["rights"] for item in bina} <= {PUBLIC_DOMAIN, "http://creativecommons.org/licenses/by-nc/4.0/", IN_COPYRIGHT}
    wikidata = service.record(service.search(Query.build(filters={"source": ["wikidata"]}), with_facets=False)["items"][0]["id"])
    assert wikidata["media"][0]["url"].startswith("https://commons.wikimedia.org/wiki/Special:FilePath/")
    assert wikidata["media_credit"].endswith("Wikimedia Commons")
    assert wikidata["coordinates"] and wikidata["institution"]["id"] is None
    assert wikidata["metadata_rights"]["uri"] == CC0
    iarm = service.record(service.search(Query.build(filters={"source": ["iarm"]}), with_facets=False)["items"][0]["id"])
    assert iarm["object_type"]["id"] == "manuscript" and iarm["media"] == []
    assert iarm["metadata_rights"]["attribution"].startswith("Index of Armenian Manuscripts")
    assert all("source" in service.record(item["id"])["relevance"]["criteria"] for item in bina[:5])


def test_search_spans_sources_and_languages(built):
    service = built["service"]
    sources = {item["id"].split("-")[0] for item in service.search(Query.build(q="Haratch"), with_facets=False)["items"]}
    assert "bina" in sources
    titles = {
        item["title"]["lang"]
        for item in service.search(Query.build(size=48), with_facets=False)["items"]
    } | {item["title"]["lang"] for source in ("bulac", "iarm", "wikidata")
         for item in service.search(Query.build(filters={"source": [source]}), with_facets=False)["items"]}
    assert {"ru", "hy", "en"} <= titles


def test_site_localizes_wikidata_titles_and_shows_rights(client, built):
    service = built["service"]
    record = service.record(service.search(Query.build(filters={"source": ["wikidata"]}), with_facets=False)["items"][0]["id"])
    french = client.get(f"/fr/item/{record['id']}").text
    assert record["titles"]["fr"] in french
    assert "Wikimedia Commons" in french and "CC0" in french
    iarm = service.search(Query.build(filters={"source": ["iarm"]}), with_facets=False)["items"][0]
    page = client.get(f"/en/item/{iarm['id']}")
    assert page.status_code == 200 and "Index of Armenian Manuscripts" in page.text
    assert client.get("/ru/collection/monuments").status_code == 200
    about = client.get("/en/about").text
    assert all(get_source(source_id).label("en") in about for source_id in ("wikidata", "bulac", "iarm"))
