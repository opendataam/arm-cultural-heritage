import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from tag_armeniana import ThemeTagger, load_taxonomy

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def taxonomy():
    return load_taxonomy(
        ROOT / "data" / "armeniana_themes.csv",
        ROOT / "data" / "armeniana_subthemes.csv",
        ROOT / "data" / "armeniana_persons.csv",
        ROOT / "data" / "armeniana_tagging_rules.csv",
    )


@pytest.fixture(scope="module")
def tagger(taxonomy):
    themes, _, persons, rules = taxonomy
    return ThemeTagger(themes, persons, rules)


def test_taxonomy_has_complete_structure(taxonomy):
    themes, subthemes, persons, rules = taxonomy
    assert len(themes) == 19
    assert len({theme.zone_id for theme in themes}) == 5
    assert sum(bool(theme.europeana_theme) for theme in themes) == 14
    assert len({rule.theme_id for rule in rules}) == 19
    assert len(persons) == 13
    assert all(rule.subtheme_id for rule in rules)


def test_tagger_assigns_multiple_themes_with_evidence(tagger):
    metadata, assignments = tagger.tag({
        "id": 1,
        "name": "Фотография хачкара у монастыря Гегард",
        "typology": {"name": "фотографии и негативы"},
        "armenia_matched_entities": [],
    })
    assert metadata["armeniana_tagging_status"] == "tagged"
    assert set(metadata["armeniana_theme_ids"]) == {"architecture", "photography", "religion"}
    assert "architecture.monasteries" in metadata["armeniana_subtheme_ids"]
    photo = next(row for row in assignments if row["theme_id"] == "photography")
    assert photo["confidence"] == "high"
    assert photo["matched_fields"] == ["name", "typology.name"]
    assert "photography.typology" in photo["rule_ids"]


def test_tagger_uses_person_ids_without_treating_them_as_text(tagger):
    metadata, assignments = tagger.tag({
        "id": 2,
        "name": "Морской пейзаж",
        "typology": {"name": "живопись"},
        "armenia_matched_entities": ["person.hovhannes_aivazovsky", "person.unknown"],
    })
    assert metadata["armeniana_person_ids"] == ["person.hovhannes_aivazovsky"]
    assert "art.marine" in metadata["armeniana_subtheme_ids"]
    person_rule = next(row for row in assignments if "art.aivazovsky" in row["rule_ids"])
    assert person_rule["matched_fields"] == ["armenia_matched_entities"]


def test_tagger_leaves_generic_records_unclassified(tagger):
    metadata, assignments = tagger.tag({
        "id": 3,
        "name": "Открытка. Армения",
        "typology": {"name": "предметы печатной продукции"},
        "armenia_matched_entities": [],
    })
    assert assignments == []
    assert metadata["armeniana_theme_ids"] == []
    assert metadata["armeniana_tagging_status"] == "unclassified"


def test_tagger_avoids_false_substrings(tagger):
    metadata, _ = tagger.tag({
        "id": 4,
        "name": "Эскиз декорации. Без вины виноватые. Маскарад",
        "typology": {"name": "графика"},
        "armenia_matched_entities": [],
    })
    assert "traditional_culture.cuisine" not in metadata["armeniana_subtheme_ids"]
    assert "maps_geography" not in metadata["armeniana_theme_ids"]
    assert "art.stage_design" in metadata["armeniana_subtheme_ids"]


def test_tagger_separates_armenian_text_from_language_history(tagger):
    metadata, _ = tagger.tag({
        "id": 5,
        "name": "Этикетка с надписью на армянском языке",
        "typology": {"name": "предметы печатной продукции"},
        "armenia_matched_entities": [],
    })
    assert "language_literature.armenian_text" in metadata["armeniana_subtheme_ids"]
    assert "language_literature.language_history" not in metadata["armeniana_subtheme_ids"]


def test_tagger_recognizes_general_sport_subject(tagger):
    metadata, _ = tagger.tag({
        "id": 6,
        "name": "Фотография участников спартакиады школьников СССР в Ереване",
        "typology": {"name": "фотографии и негативы"},
        "armenia_matched_entities": [],
    })
    assert "sport" in metadata["armeniana_theme_ids"]
    assert "sport.olympics" in metadata["armeniana_subtheme_ids"]


def make_input(path, decisions=None):
    names = [
        "Фотография монастыря Гегард",
        "Кредитный билет Армянской республики 100 рублей",
        "Эскиз декорации. Армянский театр",
        "Открытка. Армения",
        "Морской пейзаж",
        "Без вины виноватые",
    ]
    typologies = [
        "фотографии и негативы",
        "предметы нумизматики",
        "графика",
        "предметы печатной продукции",
        "живопись",
        None,
    ]
    entities = [
        [],
        [],
        [],
        [],
        ["person.hovhannes_aivazovsky"],
        [],
    ]
    decisions = decisions or ["include"] * len(names)
    table = pa.table({
        "id": pa.array(range(1, len(names) + 1), pa.int64()),
        "name": pa.array(names, pa.string()),
        "invNumber": pa.array(["A{}".format(index) for index in range(1, len(names) + 1)], pa.string()),
        "typology": pa.array([{"name": value} if value else None for value in typologies], pa.struct([pa.field("name", pa.string())])),
        "museum": pa.array([None] * len(names), pa.struct([pa.field("name", pa.string())])),
        "armenia_decision": pa.array(decisions, pa.string()),
        "armenia_matched_entities": pa.array(entities, pa.list_(pa.string())),
    })
    pq.write_table(table, path)


def test_cli_end_to_end_writes_tagged_records_and_audit(tmp_path):
    source = tmp_path / "input.parquet"
    output = tmp_path / "output"
    make_input(source)
    completed = subprocess.run([
        sys.executable,
        str(ROOT / "scripts" / "tag_armeniana.py"),
        "--input", str(source),
        "--output-dir", str(output),
        "--batch-size", "2",
    ], cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    records = pq.read_table(output / "records.parquet")
    assignments = pq.read_table(output / "assignments.parquet")
    assert records.num_rows == 6
    assert records.column("invNumber").to_pylist() == ["A1", "A2", "A3", "A4", "A5", "A6"]
    assert records.column("armeniana_tagging_status").to_pylist().count("unclassified") == 2
    by_id = {record["id"]: record for record in records.to_pylist()}
    assert set(by_id[1]["armeniana_theme_ids"]) == {"architecture", "photography", "religion"}
    assert set(by_id[2]["armeniana_theme_ids"]) == {"history", "numismatics_philately"}
    assert by_id[5]["armeniana_person_ids"] == ["person.hovhannes_aivazovsky"]
    assert "art.marine" in by_id[5]["armeniana_subtheme_ids"]
    assert all(row["rule_ids"] and row["matched_fields"] for row in assignments.to_pylist())
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["counts"]["source_rows"] == 6
    assert report["counts"]["tagged"] == 4
    assert report["counts"]["unclassified"] == 2
    assert report["counts"]["assignments"] == assignments.num_rows
    taxonomy = json.loads((output / "taxonomy.json").read_text(encoding="utf-8"))
    assert len(taxonomy["zones"]) == 5
    assert (output / "audit_sample.csv").is_file()
    assert not list(output.glob("*.tmp"))


def test_cli_rejects_unconfirmed_records(tmp_path):
    source = tmp_path / "input.parquet"
    output = tmp_path / "output"
    make_input(source, decisions=["review"] + ["include"] * 5)
    completed = subprocess.run([
        sys.executable,
        str(ROOT / "scripts" / "tag_armeniana.py"),
        "--input", str(source),
        "--output-dir", str(output),
    ], cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode == 1
    assert "Only confirmed include records" in completed.stderr
    assert not (output / "records.parquet").exists()
    assert not list(output.glob("*.tmp"))
