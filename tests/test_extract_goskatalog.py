import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent


def make_input(path):
    names = ["Армянская рукопись", "Предмет из Карса", "Бармен", "Часть рации", "Предмет"]
    places = [None, None, None, None, "Армавир, Краснодарский край"]
    museums = [None, None, None, "Музей Армении", None]
    count = len(names)
    table = pa.table({
        "id": pa.array(range(1, count + 1), pa.int64()),
        "name": pa.array(names, pa.string()),
        "description": pa.array([None] * count, pa.string()),
        "authors": pa.array([None] * count, pa.list_(pa.string())),
        "productionPlace": pa.array(places, pa.string()),
        "findPlace": pa.array([None] * count, pa.string()),
        "mainWords": pa.array([None] * count, pa.string()),
        "provenance": pa.array([None] * count, pa.string()),
        "typologyDesc": pa.array([None] * count, pa.string()),
        "technologies": pa.array([None] * count, pa.list_(pa.string())),
        "fund": pa.array([None] * count, pa.string()),
        "museum": pa.array([{"name": value} if value else None for value in museums], pa.struct([pa.field("name", pa.string())])),
        "typology": pa.array([None] * count, pa.struct([pa.field("name", pa.string())])),
        "invNumber": pa.array(["A1", "A2", "A3", "A4", "A5"], pa.string()),
    })
    pq.write_table(table, path)


def test_cli_end_to_end_preserves_records_and_metadata(tmp_path):
    source = tmp_path / "input.parquet"
    output = tmp_path / "output"
    make_input(source)
    completed = subprocess.run([
        sys.executable,
        str(ROOT / "scripts" / "extract_goskatalog_armenia.py"),
        "--input", str(source),
        "--output-dir", str(output),
        "--threads", "1",
        "--memory-limit", "512MB",
        "--batch-size", "2",
    ], cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    included = pq.read_table(output / "armenia_records.parquet")
    review = pq.read_table(output / "armenia_review.parquet")
    assert included.num_rows == 1
    assert review.num_rows == 2
    assert included.column("id").to_pylist() == [1]
    assert included.column("invNumber").to_pylist() == ["A1"]
    assert included.column("armenia_decision").to_pylist() == ["include"]
    assert "armenia_matched_terms" in included.column_names
    assert "_armenia_prefilter_forms" not in included.column_names
    assert "_armenia_search_text" not in included.column_names
    assert set(review.column("id").to_pylist()) == {2, 4}
    report = json.loads((output / "report.json").read_text(encoding="utf-8"))
    assert report["counts"] == {"source_rows": 5, "processed_source_rows": 5, "candidates": 4, "include": 1, "review": 2, "exclude": 1}
    assert (output / "audit_sample.csv").is_file()
    assert not list(output.glob("*.tmp"))


def test_resume_reprocesses_previous_candidates_without_duplicate_outputs(tmp_path):
    source = tmp_path / "input.parquet"
    initial = tmp_path / "initial"
    resumed = tmp_path / "resumed"
    make_input(source)
    base_command = [
        sys.executable,
        str(ROOT / "scripts" / "extract_goskatalog_armenia.py"),
        "--input", str(source),
        "--threads", "1",
        "--memory-limit", "512MB",
        "--batch-size", "2",
    ]
    first = subprocess.run(base_command + ["--output-dir", str(initial)], cwd=ROOT, text=True, capture_output=True)
    assert first.returncode == 0, first.stdout + first.stderr
    second = subprocess.run(base_command + ["--output-dir", str(resumed), "--resume-from", str(initial)], cwd=ROOT, text=True, capture_output=True)
    assert second.returncode == 0, second.stdout + second.stderr
    report = json.loads((resumed / "report.json").read_text(encoding="utf-8"))
    assert report["counts"]["include"] == 1
    assert report["counts"]["review"] == 2
    assert report["resume"]["reused_candidates"] == 3
    assert report["resume"]["new_candidates"] == 1
    included = pq.read_table(resumed / "armenia_records.parquet")
    review = pq.read_table(resumed / "armenia_review.parquet")
    assert included.column("id").to_pylist() == [1]
    assert set(review.column("id").to_pylist()) == {2, 4}
    assert len(included.column_names) == 23
    assert not list(resumed.glob("*.tmp"))
