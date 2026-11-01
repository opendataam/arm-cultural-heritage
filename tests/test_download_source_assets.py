import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "download_source_assets.py"


class AssetHandler(BaseHTTPRequestHandler):
    requests = []
    payloads = {
        "/image.jpg": (b"image-data", "image/jpeg"),
        "/restricted.jpg": (b"restricted", "image/jpeg"),
        "/doc.pdf": (b"%PDF-test", "application/pdf"),
    }

    def do_GET(self):
        type(self).requests.append(self.path)
        path = self.path.split("?", 1)[0]
        if path not in self.payloads:
            self.send_error(404)
            return
        payload, content_type = self.payloads[path]
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        pass


def run_server():
    AssetHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), AssetHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def make_input(path, port):
    asset_type = pa.list_(pa.struct([
        pa.field("url", pa.string()),
        pa.field("role", pa.string()),
        pa.field("mime_type", pa.string()),
        pa.field("expected_bytes", pa.int64()),
    ]))
    base = "http://127.0.0.1:{}".format(port)
    table = pa.table({
        "id": pa.array(["e1", "e2", "n1", "n2"], pa.string()),
        "source": pa.array(["europeana", "europeana", "neb", "neb"], pa.string()),
        "record_url": pa.array(["https://example.org/e1", "https://example.org/e2", "https://example.org/n1", "https://example.org/n2"], pa.string()),
        "rights": pa.array([
            ["http://creativecommons.org/publicdomain/mark/1.0/"],
            ["http://rightsstatements.org/vocab/InC/1.0/"],
            [],
            [],
        ], pa.list_(pa.string())),
        "access": pa.array(["open", "restricted_or_unknown", "open", "metadata_only_or_restricted"], pa.string()),
        "assets": pa.array([
            [{"url": base + "/image.jpg", "role": "shown_by", "mime_type": "image/jpeg", "expected_bytes": 10}],
            [{"url": base + "/restricted.jpg", "role": "shown_by", "mime_type": "image/jpeg", "expected_bytes": None}],
            [{"url": base + "/doc.pdf?name=Армянский вопрос", "role": "document", "mime_type": "application/pdf", "expected_bytes": None}],
            [{"url": base + "/restricted.jpg", "role": "document", "mime_type": "application/pdf", "expected_bytes": None}],
        ], type=asset_type),
    })
    pq.write_table(table, path)


def run_cli(source, output, source_name, *extra):
    return subprocess.run([
        sys.executable,
        str(SCRIPT),
        "--input", str(source),
        "--output-dir", str(output),
        "--source", source_name,
        "--delay", "0",
        *extra,
    ], cwd=ROOT, text=True, capture_output=True)


def test_europeana_download_open_assets_and_resume(tmp_path):
    source = tmp_path / "records.parquet"
    output = tmp_path / "europeana_files"
    server = run_server()
    make_input(source, server.server_port)
    try:
        completed = run_cli(source, output, "europeana")
        assert completed.returncode == 0, completed.stdout + completed.stderr
        assert AssetHandler.requests == ["/image.jpg"]
        report = json.loads((output / "asset_download_report.json").read_text(encoding="utf-8"))
        assert report["counts"] == {"requested": 1, "downloaded": 1, "skipped": 0, "failed": 0}
        assert report["input"]["rights_or_access_skipped"] == 1
        request_count = len(AssetHandler.requests)
        resumed = run_cli(source, output, "europeana")
        assert resumed.returncode == 0, resumed.stdout + resumed.stderr
        assert len(AssetHandler.requests) == request_count
        report = json.loads((output / "asset_download_report.json").read_text(encoding="utf-8"))
        assert report["counts"] == {"requested": 1, "downloaded": 0, "skipped": 1, "failed": 0}
    finally:
        server.shutdown()
        server.server_close()


def test_neb_requires_explicit_bound_and_downloads_only_open_document(tmp_path):
    source = tmp_path / "records.parquet"
    output = tmp_path / "neb_files"
    server = run_server()
    make_input(source, server.server_port)
    try:
        unbounded = run_cli(source, output, "neb")
        assert unbounded.returncode == 2
        assert AssetHandler.requests == []
        completed = run_cli(source, output, "neb", "--max-files", "1")
        assert completed.returncode == 0, completed.stdout + completed.stderr
        assert len(AssetHandler.requests) == 1
        assert AssetHandler.requests[0].startswith("/doc.pdf?name=")
        assert "Армянский" not in AssetHandler.requests[0]
        assert " " not in AssetHandler.requests[0]
        files = list(output.glob("files/*/*.pdf"))
        assert len(files) == 1
        assert files[0].read_bytes() == b"%PDF-test"
        report = json.loads((output / "asset_download_report.json").read_text(encoding="utf-8"))
        assert report["counts"] == {"requested": 1, "downloaded": 1, "skipped": 0, "failed": 0}
        assert report["input"]["rights_or_access_skipped"] == 1
        assert "prohibits mass automated downloading" in report["download_notice"]
    finally:
        server.shutdown()
        server.server_close()


def test_open_rights_accepts_only_unrestricted_statements():
    from source_common import is_open_rights

    for value in (
        "http://creativecommons.org/publicdomain/mark/1.0/",
        "http://creativecommons.org/publicdomain/zero/1.0/",
        "http://creativecommons.org/licenses/by/4.0/",
        "http://creativecommons.org/licenses/by-sa/3.0/de/",
    ):
        assert is_open_rights([value]), value
    for value in (
        "http://rightsstatements.org/vocab/NoC-NC/1.0/",
        "http://rightsstatements.org/vocab/NoC-OKLR/1.0/",
        "http://rightsstatements.org/vocab/NoC-CR/1.0/",
        "http://rightsstatements.org/vocab/NoC-US/1.0/",
        "http://rightsstatements.org/vocab/InC/1.0/",
        "http://creativecommons.org/licenses/by-nc/4.0/",
        "http://creativecommons.org/licenses/by-nd/4.0/",
        "http://creativecommons.org/licenses/by-nc-sa/4.0/",
    ):
        assert not is_open_rights([value]), value
    assert not is_open_rights([])
    assert not is_open_rights([
        "http://creativecommons.org/licenses/by/4.0/",
        "http://rightsstatements.org/vocab/InC/1.0/",
    ])


def test_download_aborts_files_over_size_limit(tmp_path):
    source = tmp_path / "records.parquet"
    output = tmp_path / "europeana_files"
    server = run_server()
    make_input(source, server.server_port)
    try:
        completed = run_cli(source, output, "europeana", "--max-bytes", "5")
        assert completed.returncode == 1
        report = json.loads((output / "asset_download_report.json").read_text(encoding="utf-8"))
        assert report["counts"]["failed"] == 1
        assert "exceeds 5 bytes" in report["errors"][0]["error"]
        assert not list(output.glob("files/*/*"))
    finally:
        server.shutdown()
        server.server_close()
