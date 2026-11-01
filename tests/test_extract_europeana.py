import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "extract_europeana_armenia.py"


class EuropeanaHandler(BaseHTTPRequestHandler):
    requests = []

    def do_GET(self):
        type(self).requests.append(self.path)
        parsed = urlsplit(self.path)
        params = parse_qs(parsed.query)
        if params.get("wskey") != ["test-key"]:
            self.send_error(401)
            return
        if parsed.path == "/record/v2/search.json":
            cursor = params.get("cursor", [""])[0]
            if cursor == "*":
                items = [
                    {
                        "id": "/1/armenia",
                        "title": ["Armenian manuscript"],
                        "type": "IMAGE",
                        "link": "https://api.europeana.eu/record/v2/1/armenia.json?wskey=test-key",
                        "guid": "https://www.europeana.eu/item/1/armenia?utm_source=api&utm_campaign=test-key",
                    },
                    {"id": "/2/other", "title": ["Unrelated object"], "type": "IMAGE"},
                ]
                payload = {"apikey": "test-key", "success": True, "totalResults": 3, "items": items, "nextCursor": "next"}
            elif cursor == "next":
                payload = {
                    "apikey": "test-key",
                    "success": True,
                    "totalResults": 3,
                    "items": [{"id": "/3/review", "title": ["Object"], "dctermsSpatial": ["Nagorno-Karabakh"], "type": "IMAGE"}],
                }
            else:
                self.send_error(400)
                return
            self.send_json(payload)
            return
        if parsed.path in {"/record/v2/1/armenia.json", "/record/v2/2/other.json", "/record/v2/3/review.json"}:
            is_armenia = parsed.path == "/record/v2/1/armenia.json"
            resources = [{
                "about": "https://example.org/armenia.jpg",
                "ebucoreHasMimeType": "image/jpeg",
                "ebucoreFileByteSize": 1234,
            }] if is_armenia else []
            payload = {
                "apikey": "test-key",
                "success": True,
                "object": {
                    "about": parsed.path[len("/record/v2/"):-len(".json")],
                    "proxies": [{"dcDescription": {"en": ["Armenian cultural heritage" if is_armenia else "Museum object"]}}],
                    "aggregations": [{
                        "edmDataProvider": {"en": ["Test Library"]},
                        "edmRights": {"def": ["http://creativecommons.org/publicdomain/mark/1.0/"]},
                        "edmIsShownBy": "https://example.org/armenia.jpg" if is_armenia else None,
                        "webResources": resources,
                    }],
                },
            }
            self.send_json(payload)
            return
        self.send_error(404)

    def send_json(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def run_server():
    EuropeanaHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), EuropeanaHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def run_cli(output, port):
    env = dict(os.environ)
    env["EUROPEANA_API_KEY"] = "test-key"
    return subprocess.run([
        sys.executable,
        str(SCRIPT),
        "--output-dir", str(output),
        "--query", "Armenia",
        "--max-records", "3",
        "--rows", "2",
        "--batch-size", "1",
        "--delay", "0",
        "--api-base", "http://127.0.0.1:{}/record/v2".format(port),
    ], cwd=ROOT, env=env, text=True, capture_output=True)


def test_europeana_end_to_end_cursor_records_and_resume(tmp_path):
    output = tmp_path / "europeana"
    server = run_server()
    try:
        completed = run_cli(output, server.server_port)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        included = pq.read_table(output / "armenia_records.parquet")
        review = pq.read_table(output / "armenia_review.parquet")
        assert included.column("id").to_pylist() == ["/1/armenia"]
        assert review.column("id").to_pylist() == ["/2/other", "/3/review"]
        query_only = review.to_pylist()[0]
        assert query_only["armenia_match_reasons"] == ["source_query_only"]
        assert query_only["armenia_matched_terms"] == []
        row = included.to_pylist()[0]
        assert row["access"] == "open"
        assert row["assets"] == [{
            "url": "https://example.org/armenia.jpg",
            "role": "shown_by",
            "mime_type": "image/jpeg",
            "expected_bytes": 1234,
        }]
        assert "test-key" not in row["raw_json"]
        assert "test-key" not in (output / "report.json").read_text(encoding="utf-8")
        for cached in (output / "cache").glob("*.json"):
            assert "test-key" not in cached.read_text(encoding="utf-8")
        report = json.loads((output / "report.json").read_text(encoding="utf-8"))
        assert report["counts"] == {"candidates": 3, "include": 1, "review": 2, "exclude": 0, "duplicates": 0, "record_errors": 0}
        assert any("/2/other" in path for path in EuropeanaHandler.requests)
        request_count = len(EuropeanaHandler.requests)
        resumed = run_cli(output, server.server_port)
        assert resumed.returncode == 0, resumed.stdout + resumed.stderr
        assert len(EuropeanaHandler.requests) == request_count
        resumed_report = json.loads((output / "report.json").read_text(encoding="utf-8"))
        assert resumed_report["http"]["network_requests"] == 0
        assert resumed_report["http"]["cache_hits"] == 5
        assert not list(output.glob("*.tmp"))
    finally:
        server.shutdown()
        server.server_close()


def test_source_query_does_not_rescue_negated_records(matcher):
    from source_common import classify_candidate

    base = {"title": "Вокзал", "description": None, "authors": [], "subjects": [], "provider": None, "type": None}
    negated = classify_candidate(dict(base, places=["Армавир, Краснодарский край"]), matcher, "Армавир")
    assert negated.decision == "exclude"
    query_only = classify_candidate(dict(base, places=["Москва"]), matcher, "Армения")
    assert query_only.decision == "review"
    assert query_only.reasons == ["source_query_only"]


def test_europeana_merges_queries_of_duplicate_records(tmp_path):
    output = tmp_path / "europeana"
    server = run_server()
    env = dict(os.environ, EUROPEANA_API_KEY="test-key")
    try:
        completed = subprocess.run([
            sys.executable, str(SCRIPT),
            "--output-dir", str(output),
            "--query", "Armenia",
            "--query", "Armenian",
            "--max-records", "3",
            "--rows", "2",
            "--batch-size", "1",
            "--delay", "0",
            "--api-base", "http://127.0.0.1:{}/record/v2".format(server.server_port),
        ], cwd=ROOT, env=env, text=True, capture_output=True)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        rows = pq.read_table(output / "armenia_records.parquet").to_pylist() + pq.read_table(output / "armenia_review.parquet").to_pylist()
        assert sorted(row["id"] for row in rows) == ["/1/armenia", "/2/other", "/3/review"]
        assert all(row["source_queries"] == ["Armenia", "Armenian"] for row in rows)
        report = json.loads((output / "report.json").read_text(encoding="utf-8"))
        assert report["counts"]["duplicates"] == 3
        assert not list(output.glob("*.tmp"))
    finally:
        server.shutdown()
        server.server_close()
