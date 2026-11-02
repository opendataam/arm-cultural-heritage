import json
import re
from pathlib import Path

import pytest

from sources import (
    ENUM_FIELDS,
    FIELDNAMES,
    LIST_FIELDS,
    Source,
    read_sources,
    registry_stats,
    split_list,
    validate_sources,
)

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def sources():
    return read_sources(ROOT / "data" / "sources.csv")


@pytest.fixture(scope="module")
def schema():
    return json.loads((ROOT / "schema" / "sources.schema.json").read_text(encoding="utf-8"))


def test_registry_is_valid_and_sorted(sources):
    assert validate_sources(sources) == []
    assert [source.id for source in sources] == sorted(source.id for source in sources)


def test_json_schema_matches_csv_validator(sources, schema):
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["additionalProperties"] is False
    assert schema["required"] == FIELDNAMES
    assert schema["x-csv"]["columns"] == FIELDNAMES
    assert list(schema["properties"]) == FIELDNAMES
    for field, allowed in ENUM_FIELDS.items():
        assert set(schema["properties"][field]["enum"]) == allowed
    for field, allowed in LIST_FIELDS.items():
        assert set(schema["properties"][field]["x-list"]["enum"]) == allowed
    for field, prop in schema["properties"].items():
        if "pattern" not in prop:
            continue
        pattern = re.compile(prop["pattern"])
        for source in sources:
            value = getattr(source, field)
            if value or field not in ("url", "id", "country", "languages"):
                assert pattern.search(value), (source.id, field, value)
    for example in schema["examples"]:
        assert validate_sources([Source.from_row(example)]) == []


def test_every_source_documents_terms(sources):
    for source in sources:
        assert source.terms_summary
        if source.metadata_license != "unknown":
            assert source.terms_url.startswith(("http://", "https://")), source.id


def test_mvp_covers_several_sources_and_languages(sources):
    mvp = [source for source in sources if source.priority == "1" and source.harvestable]
    assert len(mvp) > 1
    languages = {language for source in mvp for language in split_list(source.languages)}
    assert {"hy", "ru", "en"} <= languages
    assert any(source.status == "integrated" for source in mvp)


def test_validator_rejects_inconsistent_rows(sources):
    base = sources[0].as_row()
    broken = [
        dict(base, id="Bad Id"),
        dict(base, access_methods="api;none"),
        dict(base, metadata_license="CC0-1.0", terms_url=""),
        dict(base, est_armenian_items="12", count_note=""),
        dict(base, integration="none", status="planned"),
        dict(base, integration="link", status="integrated"),
        dict(base, content_types="books;books"),
        dict(base, verified_at="2026-13-01"),
    ]
    for row in broken:
        assert validate_sources([Source.from_row(row)]), row
    assert any("duplicate id" in error for error in validate_sources([sources[0], sources[0]]))


def test_registry_stats_count_all_rows(sources):
    stats = registry_stats(sources)
    assert stats["total"] == len(sources)
    assert sum(value for key, value in stats.items() if key.startswith("status.")) == len(sources)
