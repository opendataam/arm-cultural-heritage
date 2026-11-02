import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from extract_collection import load_collection
from evaluate_goskatalog import load_labels
from matcher import ArmeniaMatcher
from terms import read_terms

ROOT = Path(__file__).resolve().parent.parent
HAMSHEN = ROOT / "data" / "collections" / "hamshen"
MUSEUM_TYPE = pa.struct([pa.field("name", pa.string())])


@pytest.fixture(scope="module")
def hamshen_matcher():
    return ArmeniaMatcher(read_terms(HAMSHEN / "terms.csv"))


@pytest.mark.parametrize("text", [
    "Полотенце. Армяне; армяне: армяне-колонисты: армяне амшенские",
    "Газета «Луйс Амшени», №2, 1991 г.",
    "Этнография амшенских армян",
    "Книга. «Голос амшенский»",
    "Кочконян А. «Амшен мой, прадедов земля»",
    "Снегоступ. Армяне: армяне-колонисты: хемшины (армяне амшенские)",
    "Акварель «Армянка». Армяне хопские",
    "Хамшенцы Абхазии",
    "Համշենի բարբառ",
    "Hamshen Armenians",
    "Hemşinliler",
])
def test_hamshen_terms_include(hamshen_matcher, text):
    assert hamshen_matcher.classify({"name": text}).decision == "include", text


@pytest.mark.parametrize("text", [
    "Самшенко В.Н. - секретарь ГК ВЛКСМ",
    "Плакат с биографией Памшена Сергея Дмитриевича",
    "Вид на озеро Дамшен",
    "Армянская рукопись",
])
def test_hamshen_terms_reject_false_substrings(hamshen_matcher, text):
    assert hamshen_matcher.classify({"name": text}).decision == "exclude", text


def test_published_collection_definition_is_valid():
    directory, definition = load_collection(HAMSHEN)
    assert definition["id"] == "hamshen"
    assert read_terms(directory / definition["terms"])
    rows, ids = load_labels(directory / definition["labels"])
    assert rows and len(ids) == len(set(ids))


def write_source(path, rows):
    count = len(rows)
    empty = [None] * count
    pq.write_table(pa.table({
        "id": pa.array([row["id"] for row in rows], pa.int64()),
        "name": pa.array([row["name"] for row in rows], pa.string()),
        "description": pa.array([row.get("description") for row in rows], pa.string()),
        "authors": pa.array(empty, pa.list_(pa.string())),
        "productionPlace": pa.array(empty, pa.string()),
        "findPlace": pa.array(empty, pa.string()),
        "mainWords": pa.array(empty, pa.string()),
        "provenance": pa.array(empty, pa.string()),
        "typologyDesc": pa.array(empty, pa.string()),
        "technologies": pa.array(empty, pa.list_(pa.string())),
        "fund": pa.array(empty, pa.string()),
        "museum": pa.array([{"name": row.get("museum")} for row in rows], MUSEUM_TYPE),
        "typology": pa.array(empty, MUSEUM_TYPE),
        "gikNumber": pa.array(["G{}".format(row["id"]) for row in rows], pa.string()),
    }), path)


def write_armenia(path, rows):
    pq.write_table(pa.table({
        "id": pa.array([row["id"] for row in rows], pa.int64()),
        "museum": pa.array([{"name": row.get("museum")} for row in rows], MUSEUM_TYPE),
    }), path)


def test_cli_builds_tiers_from_terms_regional_museums_and_labels(tmp_path):
    sochi = "Музей истории города-курорта Сочи"
    rows = [
        {"id": 1, "name": "Полотенце. Армяне: армяне-колонисты: армяне амшенские"},
        {"id": 2, "name": "Газета «Луйс Амшени», №2", "museum": sochi},
        {"id": 3, "name": "Фотография. Самшенко В.Н."},
        {"id": 4, "name": "Сковорода армянских переселенцев", "museum": sochi},
        {"id": 5, "name": "Армянская рукопись", "museum": "Эрмитаж"},
        {"id": 6, "name": "Лира кемендже", "description": "Инструмент понтийских греков и амшенских армян"},
        {"id": 7, "name": "Акварель «Армянин»"},
        {"id": 8, "name": "Значок «Армянская ССР»", "museum": sochi},
        {"id": 9, "name": "Как закалялась сталь на армянском языке", "museum": "Литературно-мемориальный музей Н. Островского в городе Сочи"},
        {"id": 10, "name": "Предмет"},
    ]
    source = tmp_path / "input.parquet"
    write_source(source, rows)
    armenia = tmp_path / "armenia"
    armenia.mkdir()
    by_id = {row["id"]: row for row in rows}
    write_armenia(armenia / "armenia_records.parquet", [by_id[1], by_id[4], by_id[5], by_id[8], by_id[9]])
    write_armenia(armenia / "armenia_review.parquet", [by_id[6]])
    collection = tmp_path / "collection"
    collection.mkdir()
    definition = json.loads((HAMSHEN / "collection.json").read_text(encoding="utf-8"))
    (collection / "collection.json").write_text(json.dumps(definition, ensure_ascii=False), encoding="utf-8")
    shutil.copy(HAMSHEN / "terms.csv", collection / "terms.csv")
    (collection / "labels.csv").write_text(
        "id,label,note\n"
        "6,review,Lyre of Pontic Greeks\n"
        "7,relevant,Pair to a Hopa Armenian watercolor\n"
        "8,nonrelevant,Soviet badge\n",
        encoding="utf-8",
    )
    output = tmp_path / "output"
    completed = subprocess.run([
        sys.executable,
        str(ROOT / "scripts" / "extract_collection.py"),
        "--collection", str(collection),
        "--input", str(source),
        "--armenia-dir", str(armenia),
        "--output-dir", str(output),
        "--threads", "1",
        "--memory-limit", "512MB",
        "--batch-size", "2",
    ], cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    table = pq.read_table(output / "hamshen_records.parquet")
    records = {row["id"]: row for row in table.to_pylist()}
    assert table.column("id").to_pylist() == [1, 2, 7, 4, 6]
    assert {key: row["collection_tier"] for key, row in records.items()} == {
        1: "confirmed", 2: "confirmed", 7: "confirmed", 4: "candidate", 6: "candidate",
    }
    assert records[1]["collection_reasons"] == ["strong_content"]
    assert records[1]["armenia_decision"] == "include"
    assert records[2]["collection_matched_terms"] == ["ru:Амшен"]
    assert records[2]["armenia_decision"] is None
    assert records[4]["collection_reasons"] == ["regional_museum"]
    assert records[6]["collection_reasons"] == ["manual_review", "strong_content"]
    assert records[6]["armenia_decision"] == "review"
    assert records[6]["collection_label_note"] == "Lyre of Pontic Greeks"
    assert records[7]["collection_reasons"] == ["manual_relevant"]
    assert records[7]["gikNumber"] == "G7"
    assert all(row["collection_id"] == "hamshen" for row in records.values())
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["counts"] == {
        "source_rows": 10,
        "scanned": 6,
        "confirmed": 3,
        "candidate": 2,
        "excluded": 0,
        "manual_nonrelevant": 1,
        "not_in_armenia_extraction": 2,
    }
    assert report["armenia_extraction"]["regional_candidates"] == 2
    with (output / "hamshen_records.csv").open(encoding="utf-8", newline="") as handle:
        listing = list(csv.DictReader(handle))
    assert [row["id"] for row in listing] == ["1", "2", "7", "4", "6"]
    assert listing[2]["label_note"] == "Pair to a Hopa Armenian watercolor"
    assert not list(output.glob("*.tmp"))


def test_cli_rejects_labels_missing_from_source(tmp_path):
    source = tmp_path / "input.parquet"
    write_source(source, [{"id": 1, "name": "Армяне амшенские"}])
    armenia = tmp_path / "armenia"
    armenia.mkdir()
    write_armenia(armenia / "armenia_records.parquet", [])
    write_armenia(armenia / "armenia_review.parquet", [])
    collection = tmp_path / "collection"
    collection.mkdir()
    (collection / "collection.json").write_text(json.dumps({"id": "test", "title": "Test", "terms": "terms.csv", "labels": "labels.csv"}), encoding="utf-8")
    shutil.copy(HAMSHEN / "terms.csv", collection / "terms.csv")
    (collection / "labels.csv").write_text("id,label,note\n99,relevant,Missing\n", encoding="utf-8")
    completed = subprocess.run([
        sys.executable,
        str(ROOT / "scripts" / "extract_collection.py"),
        "--collection", str(collection),
        "--input", str(source),
        "--armenia-dir", str(armenia),
        "--output-dir", str(tmp_path / "output"),
        "--threads", "1",
    ], cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode == 1
    assert "Label IDs missing in source: [99]" in completed.stderr
