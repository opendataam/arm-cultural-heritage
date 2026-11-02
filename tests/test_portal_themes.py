from dataclasses import replace

import duckdb
import pytest

from portal.pipeline import stages
from portal.search import Query, SearchService
from portal.settings import get_source

THEME = "output/goskatalog/collections/hamshen/hamshen_records.parquet"
MAIN = "output/goskatalog/armenia_records.parquet"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """Goskatalog rows with some Hamshen members, published with the Hamshen theme."""
    root = tmp_path_factory.mktemp("themes")
    sample = root / "sample.parquet"
    duckdb.execute(
        f"""copy (select * from (
            (select m.* from '{MAIN}' m join '{THEME}' t using (id) where t.collection_tier = 'confirmed' order by id limit 5)
            union all
            (select m.* from '{MAIN}' m join '{THEME}' t using (id) where t.collection_tier = 'candidate' order by id limit 5)
            union all
            (select * from '{MAIN}' where id not in (select id from '{THEME}') order by id limit 20)
        )) to '{sample}' (format parquet)"""
    )
    source = replace(get_source("goskatalog"), input=sample, review_input=None)
    build = root / "build"
    stages.collect(source, build)
    transform = stages.transform(source, build)
    stages.publish([source], build, build / "portal.sqlite", with_export=False)
    confirmed = duckdb.execute(f"select count(*) from '{THEME}' where collection_tier = 'confirmed'").fetchone()[0]
    return {"transform": transform, "service": SearchService(build / "portal.sqlite"), "confirmed": confirmed}


def test_confirmed_members_missing_from_input_are_added(built):
    themes = built["transform"]["themes"]
    assert themes["files"][0]["path"].endswith("hamshen_records.parquet")
    assert themes["files"][0]["rows"] > built["confirmed"]
    assert themes["theme_only_records"] == built["confirmed"] - 5
    assert built["transform"]["output"] == 30 + themes["theme_only_records"]


def test_theme_facet_counts_only_confirmed_members(built):
    service = built["service"]
    facets = dict(service.search(Query.build())["facets"]["theme"])
    assert facets == {"hamshen": built["confirmed"]}
    collection = service.search(Query.build(filters={"theme": ["hamshen"]}), with_facets=False)
    assert collection["total"] == built["confirmed"]


def test_theme_only_record_is_published_with_theme_evidence(built):
    record = built["service"].record("gk-29955840")
    assert record is not None and "Луйс Амшени" in record["title"]["value"]
    assert record["themes"] == [{"id": "hamshen", "tier": "confirmed"}]
    assert record["relevance"]["status"] == "confirmed"
    assert "theme:hamshen" in record["relevance"]["reasons"]
    assert record["relevance"]["matched_terms"]
