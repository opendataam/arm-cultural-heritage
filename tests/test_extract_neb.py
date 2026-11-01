import json
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "extract_neb_armenia.py"


def card(port, record_id, title, description, armenian):
    pdf = ""
    if armenian:
        href = "/local/tools/exalead/getFiles.php?book_id={}&name={}&doc_type=pdf".format(record_id, record_id)
        pdf = '<a href="{}">Скачать pdf</a><a href="{}&duplicate=1">Скачать pdf</a>'.format(href, href)
    return """<!doctype html><html><head>
    <meta property="og:url" content="http://127.0.0.1:{port}/catalog/{record_id}/">
    <meta property="og:title" content="{title}">
    <meta name="description" content="{description}">
    </head><body>
    <div>Библиографическое описание</div><div>Скопировать</div><p>{description}</p>
    <div>Детальная информация</div>
    <div>Код документа в НЭБ</div><div>{record_id}</div>
    <div>Каталог</div><div>Книги</div>
    <div>Автор(ы)</div><div>А. В. Амфитеатров</div>
    <div>Заглавие</div><div>{title}</div>
    <div>Место издания</div><div>{place}</div>
    <div>Год издания</div><div>1906</div>
    <div>Язык</div><div>Русский</div>
    <div>Библиотека</div><div>Российская национальная библиотека</div>
    {pdf}
    <div>Похожие документы</div>
    </body></html>""".format(
        port=port,
        record_id=record_id,
        title=title,
        description=description,
        place="С.-Петербург" if armenian else "Москва",
        pdf=pdf,
    )


class NebHandler(BaseHTTPRequestHandler):
    requests = []

    def do_GET(self):
        type(self).requests.append(self.path)
        parsed = urlsplit(self.path)
        if parsed.path == "/search/":
            params = parse_qs(parsed.query)
            if params.get("access[]") != ["open"]:
                self.send_error(400)
                return
            body = """<html><body><div>Найдено 2 результатов</div>
            <a class="search-list__item_link ramka" href="/catalog/a/"><img src="a.jpg"></a>
            <a class="search-list__item_link" href="/catalog/a/">Армянский вопрос</a>
            <a class="search-list__item_link" href="/catalog/b/">Садоводство</a>
            </body></html>""".encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/catalog/a/":
            body = card(self.server.server_port, "a", "Армянский вопрос", "Амфитеатров. Армянский вопрос. 1906.", True).encode("utf-8")
        elif parsed.path == "/catalog/b/":
            body = card(self.server.server_port, "b", "Садоводство", "Практическое пособие по садоводству.", False).encode("utf-8")
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def run_server():
    NebHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), NebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def run_cli(output, port):
    return subprocess.run([
        sys.executable,
        str(SCRIPT),
        "--output-dir", str(output),
        "--query", "Армянский вопрос",
        "--max-records-per-query", "2",
        "--access", "open",
        "--delay", "0",
        "--batch-size", "1",
        "--base-url", "http://127.0.0.1:{}".format(port),
    ], cwd=ROOT, text=True, capture_output=True)


def test_neb_end_to_end_cards_assets_and_resume(tmp_path):
    output = tmp_path / "neb"
    server = run_server()
    try:
        completed = run_cli(output, server.server_port)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        included = pq.read_table(output / "armenia_records.parquet")
        review = pq.read_table(output / "armenia_review.parquet")
        assert included.column("id").to_pylist() == ["a"]
        assert review.column("id").to_pylist() == ["b"]
        assert review.to_pylist()[0]["armenia_match_reasons"] == ["source_query_only"]
        row = included.to_pylist()[0]
        assert row["title"] == "Армянский вопрос"
        assert row["authors"] == ["А. В. Амфитеатров"]
        assert row["access"] == "open"
        assert len(row["assets"]) == 1
        assert row["assets"][0]["mime_type"] == "application/pdf"
        assert json.loads(row["raw_json"])["fields"]["Год издания"] == "1906"
        report = json.loads((output / "report.json").read_text(encoding="utf-8"))
        assert report["counts"] == {"candidates": 2, "include": 1, "review": 1, "exclude": 0, "duplicates": 0, "card_errors": 0}
        assert not any("getFiles.php" in path for path in NebHandler.requests)
        request_count = len(NebHandler.requests)
        resumed = run_cli(output, server.server_port)
        assert resumed.returncode == 0, resumed.stdout + resumed.stderr
        assert len(NebHandler.requests) == request_count
        resumed_report = json.loads((output / "report.json").read_text(encoding="utf-8"))
        assert resumed_report["http"]["network_requests"] == 0
        assert resumed_report["http"]["cache_hits"] == 3
        assert not list(output.glob("*.tmp"))
    finally:
        server.shutdown()
        server.server_close()
