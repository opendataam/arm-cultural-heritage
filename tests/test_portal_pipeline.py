import json
from dataclasses import replace

import duckdb
import pytest

from portal.pipeline import stages
from portal.search import Query, SearchService, parse_query
from portal.settings import get_source

SOURCE_PARQUET = "output/goskatalog/armenia_records.parquet"


def _subset(path, where, limit):
    duckdb.execute(
        f"copy (select * from '{SOURCE_PARQUET}' where {where} order by id limit {limit}) "
        f"to '{path}' (format parquet)"
    )


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """A small publication built from real Goskatalog rows by every pipeline stage."""
    root = tmp_path_factory.mktemp("portal")
    sample = root / "sample.parquet"
    duckdb.execute(
        f"""copy (select * from (
            (select * from '{SOURCE_PARQUET}' where list_contains(armenia_matched_entities, 'place.yerevan')
             order by id limit 60)
            union all
            (select * from '{SOURCE_PARQUET}' where list_contains(armenia_matched_entities, 'person.martiros_saryan')
             order by id limit 40)
            union all
            (select * from '{SOURCE_PARQUET}' where len(images) = 0 order by id limit 20)
        ) qualify row_number() over (partition by id order by id) = 1) to '{sample}' (format parquet)"""
    )
    source = replace(get_source("goskatalog"), input=sample, review_input=None, themes=())
    build = root / "build"
    db = build / "portal.sqlite"
    snapshot = stages.collect(source, build)
    transform = stages.transform(source, build)
    report = stages.publish([source], build, db)
    return {"source": source, "build": build, "db": db, "snapshot": snapshot, "transform": transform, "report": report}


def test_snapshot_is_content_addressed(built):
    snapshot = built["snapshot"]
    assert snapshot["rows"] == built["transform"]["input"] > 0
    assert (built["build"] / snapshot["path"]).name == f"{snapshot['sha256']}.parquet"
    # Collecting the same dump again keeps the original snapshot and its date.
    assert stages.collect(built["source"], built["build"])["collected_at"] == snapshot["collected_at"]


def test_report_and_exports(built):
    report = built["report"]
    assert report["published"]["records"] == built["transform"]["output"]
    assert report["sources"]["goskatalog"]["published"] == report["published"]["records"]
    assert report["sources"]["goskatalog"]["duplicates_skipped"] == 0
    assert all(check["passed"] for check in report["checks"])
    assert {"records.jsonl.gz", "records.parquet"} <= set(report["exports"])
    saved = json.loads((built["build"] / "report.json").read_text())
    assert saved["terms_sha256"] == report["terms_sha256"]
    rows = duckdb.execute(f"select count(*) from '{built['build'] / 'export' / 'records.parquet'}'").fetchone()[0]
    assert rows == report["published"]["records"]


def test_record_model(built):
    service = SearchService(built["db"])
    item = service.search(Query.build(filters={"media": ["METADATA"]}), with_facets=False)["items"][0]
    record = service.record(item["id"])
    assert record["id"].startswith("gk-")
    assert record["title"]["lang"] == "ru"
    assert record["rights"]["uri"] == "http://rightsstatements.org/vocab/CNE/1.0/"
    assert record["relevance"]["status"] == "confirmed"
    assert record["quality"]["content_tier"] == 0
    assert record["record_provenance"]["snapshot_sha256"] == built["snapshot"]["sha256"]


def test_volume_drop_blocks_publication(built, tmp_path):
    shrunk = tmp_path / "shrunk.parquet"
    _subset(shrunk, "true", 10)
    source = replace(built["source"], input=shrunk)
    stages.collect(source, built["build"])
    stages.transform(source, built["build"])
    with pytest.raises(stages.QualityGateError):
        stages.publish([source], built["build"], tmp_path / "blocked.sqlite", with_export=False)
    assert not (tmp_path / "blocked.sqlite").exists()
    # Restore the stage files for the other tests in this module.
    stages.collect(built["source"], built["build"])
    stages.transform(built["source"], built["build"])


def test_query_parsing():
    groups = parse_query('ереван "армянская церковь" -фото ани OR гарни')
    assert [len(group) for group in groups] == [1, 1, 1, 2]
    assert groups[1][0].phrase and groups[2][0].negative
    assert parse_query("арм*")[0][0].prefix


def test_cross_language_search(built):
    service = SearchService(built["db"])
    russian = service.search(Query.build(q="Ереван"))
    for query in ("Yerevan", "Երևան", "Երեւան"):
        result = service.search(Query.build(q=query))
        assert result["total"] >= russian["total"] > 0
        assert "place.yerevan" in result["expanded_entities"]
    saryan = service.search(Query.build(q="Saryan"))
    assert saryan["total"] >= 40 and "person.martiros_saryan" in saryan["expanded_entities"]


def test_facets_and_filters(built):
    service = SearchService(built["db"])
    everything = service.search(Query.build())
    types = dict(everything["facets"]["type"])
    chosen = next(iter(types))
    filtered = service.search(Query.build(filters={"type": [chosen]}))
    assert filtered["total"] == types[chosen]
    # The selected field keeps counts for its other values, so they can be added with OR.
    assert dict(filtered["facets"]["type"]) == types
    with_media = service.search(Query.build(media_only=True))
    assert with_media["total"] == everything["total"] - dict(everything["facets"]["media"])["METADATA"]


def test_year_filter_and_sorting(built):
    service = SearchService(built["db"])
    result = service.search(Query.build(year_from=1900, year_to=1950, sort="date_asc", size=96))
    for item in result["items"]:
        record = service.record(item["id"])
        assert record["date"]["year_to"] >= 1900 and record["date"]["year_from"] <= 1950
    years = [service.record(item["id"])["date"]["year_from"] for item in result["items"]]
    assert years == sorted(years)


def test_negation_and_paging(built):
    service = SearchService(built["db"])
    total = service.search(Query.build(q="Ереван"))["total"]
    without = service.search(Query.build(q="Ереван -фотография"))["total"]
    assert without <= total
    first = service.search(Query.build(page=1), with_facets=False)["items"]
    second = service.search(Query.build(page=2), with_facets=False)["items"]
    assert not {i["id"] for i in first} & {i["id"] for i in second}


def test_suggest_and_similar(built):
    service = SearchService(built["db"])
    assert service.suggest("Yere")[0]["id"] == "place.yerevan"
    record = service.record(service.search(Query.build(q="Saryan"), with_facets=False)["items"][0]["id"])
    similar = service.similar(record)
    assert similar and record["id"] not in {item["id"] for item in similar}
