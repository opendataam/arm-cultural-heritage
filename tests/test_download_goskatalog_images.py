import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "download_goskatalog_images.py"


def make_input(path, port):
    image_type = pa.list_(pa.struct([pa.field("url", pa.string())]))
    table = pa.table({
        "id": pa.array([101, 102, 103], pa.int64()),
        "name": pa.array(["Предмет 1", "Предмет 2", "Без изображения"], pa.string()),
        "images": pa.array([
            [{"url": "http://127.0.0.1:{}/images/first".format(port)}, {"url": "http://127.0.0.1:{}/images/second".format(port)}],
            [{"url": "http://127.0.0.1:{}/images/third".format(port)}],
            None,
        ], type=image_type),
    })
    pq.write_table(table, path)


class ImageHandler(BaseHTTPRequestHandler):
    payloads = {
        "/images/first": b"first-image",
        "/images/second": b"second-image-longer",
        "/images/third": b"third",
    }
    requests = []
    unavailable = set()
    truncated = set()
    disposition = "museum.jpg"

    def do_GET(self):
        type(self).requests.append(self.path)
        if self.headers.get("Referer") != "https://goskatalog.ru/portal/":
            self.send_error(403)
            return
        if self.path in type(self).unavailable:
            self.send_error(404)
            return
        payload = self.payloads[self.path]
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Disposition", 'attachment;filename="{}"'.format(type(self).disposition))
        if self.path in type(self).truncated:
            self.send_header("Content-Length", str(len(payload) + 100))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        pass


def run_server():
    ImageHandler.requests = []
    ImageHandler.unavailable = set()
    ImageHandler.truncated = set()
    ImageHandler.disposition = "museum.jpg"
    server = ThreadingHTTPServer(("127.0.0.1", 0), ImageHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def run_cli(source, output, *extra):
    return subprocess.run([
        sys.executable, str(SCRIPT),
        "--input", str(source),
        "--output-dir", str(output),
        "--workers", "1",
        "--retries", "0",
        *extra,
    ], cwd=ROOT, text=True, capture_output=True)


def test_downloads_every_image_and_resumes(tmp_path):
    source = tmp_path / "input.parquet"
    output = tmp_path / "images"
    server = run_server()
    make_input(source, server.server_port)
    try:
        first = run_cli(source, output)
        assert first.returncode == 0, first.stdout + first.stderr
        assert (output / "101" / "001_first.jpg").read_bytes() == b"first-image"
        assert (output / "101" / "002_second.jpg").read_bytes() == b"second-image-longer"
        assert (output / "102" / "001_third.jpg").read_bytes() == b"third"
        manifest = [json.loads(line) for line in (output / "image_manifest.jsonl").read_text(encoding="utf-8").splitlines()]
        assert len(manifest) == 3
        assert {(row["record_id"], row["image_index"]) for row in manifest} == {("101", 1), ("101", 2), ("102", 1)}
        report = json.loads((output / "image_download_report.json").read_text(encoding="utf-8"))
        assert report["input"] == {
            "path": str(source),
            "records": 3,
            "records_with_images": 2,
            "records_without_images": 1,
            "image_links": 3,
            "distinct_image_urls": 3,
            "max_images_per_record": 2,
        }
        assert report["counts"] == {"requested": 3, "downloaded": 3, "skipped": 0, "failed": 0}
        assert report["bytes"]["available_total"] == sum(len(value) for value in ImageHandler.payloads.values())
        request_count = len(ImageHandler.requests)
        second = run_cli(source, output)
        assert second.returncode == 0, second.stdout + second.stderr
        assert len(ImageHandler.requests) == request_count
        resumed = json.loads((output / "image_download_report.json").read_text(encoding="utf-8"))
        assert resumed["counts"] == {"requested": 3, "downloaded": 0, "skipped": 3, "failed": 0}
    finally:
        server.shutdown()
        server.server_close()


def test_estimate_samples_without_saving_images(tmp_path):
    source = tmp_path / "input.parquet"
    output = tmp_path / "estimate"
    server = run_server()
    make_input(source, server.server_port)
    try:
        completed = run_cli(source, output, "--estimate-only", "--sample-size", "2", "--seed", "42")
        assert completed.returncode == 0, completed.stdout + completed.stderr
        assert len(ImageHandler.requests) == 2
        report = json.loads((output / "image_estimate.json").read_text(encoding="utf-8"))
        assert report["mode"] == "estimate"
        assert report["sample"]["requested"] == 2
        assert report["sample"]["succeeded"] == 2
        assert report["sample"]["failed"] == 0
        assert report["estimated_total_bytes"] == round(report["sample"]["mean_bytes"] * 3)
        assert report["confidence_interval_95"]["lower_bytes"] <= report["estimated_total_bytes"]
        assert report["confidence_interval_95"]["upper_bytes"] >= report["estimated_total_bytes"]
        assert not (output / "image_manifest.jsonl").exists()
        assert not list(output.glob("*/*.jpg"))
    finally:
        server.shutdown()
        server.server_close()


def test_estimate_accounts_for_unavailable_images(tmp_path):
    source = tmp_path / "input.parquet"
    output = tmp_path / "estimate"
    server = run_server()
    make_input(source, server.server_port)
    ImageHandler.unavailable.add("/images/second")
    try:
        completed = run_cli(source, output, "--estimate-only", "--sample-size", "3")
        assert completed.returncode == 0, completed.stdout + completed.stderr
        report = json.loads((output / "image_estimate.json").read_text(encoding="utf-8"))
        assert report["sample"]["succeeded"] == 2
        assert report["sample"]["failed"] == 1
        assert report["estimated_available_images"] == 2
        assert report["estimated_total_bytes"] == len(b"first-image") + len(b"third")
        assert len(report["errors"]) == 1
    finally:
        server.shutdown()
        server.server_close()


def test_rejects_truncated_body_and_names_files_by_signature(tmp_path):
    source = tmp_path / "input.parquet"
    output = tmp_path / "images"
    server = run_server()
    make_input(source, server.server_port)
    ImageHandler.truncated.add("/images/second")
    ImageHandler.disposition = "museum.tif"
    original = dict(ImageHandler.payloads)
    ImageHandler.payloads["/images/first"] = b"\x89PNG\r\n\x1a\nrest-of-png"
    try:
        completed = run_cli(source, output)
        assert completed.returncode == 1
        assert (output / "101" / "001_first.png").read_bytes() == ImageHandler.payloads["/images/first"]
        assert (output / "102" / "001_third.tif").read_bytes() == b"third"
        assert not list((output / "101").glob("002_second*"))
        report = json.loads((output / "image_download_report.json").read_text(encoding="utf-8"))
        assert report["counts"]["failed"] == 1
        assert report["errors"][0]["image_index"] == 2
        ImageHandler.truncated.clear()
        resumed = run_cli(source, output, "--verify-hashes")
        assert resumed.returncode == 0, resumed.stdout + resumed.stderr
        report = json.loads((output / "image_download_report.json").read_text(encoding="utf-8"))
        assert report["counts"] == {"requested": 3, "downloaded": 1, "skipped": 2, "failed": 0}
    finally:
        ImageHandler.payloads.clear()
        ImageHandler.payloads.update(original)
        server.shutdown()
        server.server_close()
