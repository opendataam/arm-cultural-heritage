import json
import subprocess
import sys
from pathlib import Path

from test_extract_goskatalog import make_input

ROOT = Path(__file__).resolve().parent.parent


def test_evaluation_cli_uses_labels_and_reports_sample_metrics(tmp_path):
    source = tmp_path / "input.parquet"
    labels = tmp_path / "labels.csv"
    output = tmp_path / "evaluation.json"
    make_input(source)
    labels.write_text(
        "id,label,note\n"
        "1,relevant,Explicit Armenian manuscript\n"
        "2,review,Context-only place\n"
        "3,nonrelevant,False substring\n"
        "4,review,Museum-only evidence\n"
        "5,nonrelevant,Russian Armavir\n",
        encoding="utf-8",
    )
    completed = subprocess.run([
        sys.executable,
        str(ROOT / "scripts" / "evaluate_goskatalog.py"),
        "--input", str(source),
        "--labels", str(labels),
        "--output", str(output),
        "--threads", "1",
    ], cwd=ROOT, text=True, capture_output=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["sample_size"] == 5
    assert report["automatic_filter"] == {
        "true_positive": 1,
        "false_positive": 0,
        "false_negative": 0,
        "true_negative": 2,
        "precision": 1.0,
        "recall": 1.0,
    }
    assert report["candidate_retrieval"] == {
        "relevant_total": 1,
        "relevant_include": 1,
        "relevant_review": 0,
        "relevant_exclude": 0,
        "candidate_recall": 1.0,
    }
    assert len(report["records"]) == 5
