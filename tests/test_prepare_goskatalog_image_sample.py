import argparse
import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

import prepare_goskatalog_image_sample as preparation

ROOT = Path(__file__).resolve().parent.parent


def make_input(path):
    image_type = pa.list_(pa.struct([pa.field("url", pa.string())]))
    table = pa.table({
        "id": pa.array([101, 102, 103], pa.int64()),
        "name": pa.array(["Два изображения", "Одно изображение", "Недоступно"], pa.string()),
        "images": pa.array([
            [{"url": "http://goskatalog.ru/old/1"}, {"url": "http://goskatalog.ru/old/2"}],
            [{"url": "http://goskatalog.ru/old/3"}],
            [{"url": "http://goskatalog.ru/old/4"}],
        ], type=image_type),
    })
    pq.write_table(table, path)


def test_prepare_refreshes_images_caps_sample_and_reuses_api_cache(tmp_path, monkeypatch):
    source = tmp_path / "input.parquet"
    output = tmp_path / "sample"
    make_input(source)
    calls = []

    def fetch(record_id, timeout, retries):
        calls.append(record_id)
        if record_id == "103":
            return {"requested_id": record_id, "http_status": 403, "response": None}
        images = {
            "101": [
                {"id": 201, "fileName": "first.jpg", "deleted": False, "main": True},
                {"id": 202, "fileName": "second.jpg", "deleted": False, "main": False},
                {"id": 204, "fileName": "broken.jpg", "deleted": False, "status": 3, "lastError": "No space left on device"},
            ],
            "102": [{"id": 203, "fileName": "third.jpg", "deleted": False, "main": True}],
        }
        return {"requested_id": record_id, "http_status": 200, "response": {"id": None, "images": images[record_id]}}

    monkeypatch.setattr(preparation, "fetch_api_record", fetch)
    args = argparse.Namespace(
        input=source,
        output_dir=output,
        max_images=3,
        seed=42,
        workers=1,
        timeout=60,
        retries=0,
    )
    report = preparation.prepare(args)
    rows = pq.read_table(output / "image_sample.parquet").to_pylist()
    assert [row["id"] for row in rows] == [102, 101]
    assert [[image["url"].rsplit("/", 1)[-1] for image in row["images"]] for row in rows] == [["203"], ["201", "202"]]
    assert report["input"]["image_links"] == 4
    assert report["counts"]["selected_records"] == 2
    assert report["counts"]["selected_images"] == 3
    assert report["counts"]["api_http_status"] == {"200": 2}
    cache = [json.loads(line) for line in (output / "api_records.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(cache) == 3
    assert {row["requested_id"]: row["http_status"] for row in cache}["103"] == 403
    assert len(calls) == 3
    resumed = preparation.prepare(args)
    assert len(calls) == 3
    assert resumed["counts"]["api_records_fetched_this_run"] == 0
