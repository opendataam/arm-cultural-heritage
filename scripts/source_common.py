#!/usr/bin/env python3
import csv
import hashlib
import heapq
import json
import re
import time
from datetime import datetime, timezone
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit
from urllib.request import ProxyHandler, Request, build_opener

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
USER_AGENT = "arm-cultural-heritage-source-importer/1.0 (+https://github.com/opendataam/arm-cultural-heritage)"
ASSET_TYPE = pa.struct([
    pa.field("url", pa.string(), nullable=False),
    pa.field("role", pa.string(), nullable=False),
    pa.field("mime_type", pa.string()),
    pa.field("expected_bytes", pa.int64()),
])
RECORD_SCHEMA = pa.schema([
    pa.field("id", pa.string(), nullable=False),
    pa.field("source", pa.string(), nullable=False),
    pa.field("record_url", pa.string(), nullable=False),
    pa.field("title", pa.string()),
    pa.field("description", pa.string()),
    pa.field("authors", pa.list_(pa.string()), nullable=False),
    pa.field("date", pa.string()),
    pa.field("places", pa.list_(pa.string()), nullable=False),
    pa.field("subjects", pa.list_(pa.string()), nullable=False),
    pa.field("languages", pa.list_(pa.string()), nullable=False),
    pa.field("type", pa.string()),
    pa.field("provider", pa.string()),
    pa.field("rights", pa.list_(pa.string()), nullable=False),
    pa.field("access", pa.string(), nullable=False),
    pa.field("assets", pa.list_(ASSET_TYPE), nullable=False),
    pa.field("source_queries", pa.list_(pa.string()), nullable=False),
    pa.field("retrieved_at", pa.string(), nullable=False),
    pa.field("raw_json", pa.string(), nullable=False),
    pa.field("armenia_decision", pa.string(), nullable=False),
    pa.field("armenia_confidence", pa.string(), nullable=False),
    pa.field("armenia_match_strength", pa.string(), nullable=False),
    pa.field("armenia_matched_entities", pa.list_(pa.string()), nullable=False),
    pa.field("armenia_matched_terms", pa.list_(pa.string()), nullable=False),
    pa.field("armenia_matched_forms", pa.list_(pa.string()), nullable=False),
    pa.field("armenia_matched_fields", pa.list_(pa.string()), nullable=False),
    pa.field("armenia_match_reasons", pa.list_(pa.string()), nullable=False),
    pa.field("armenia_negated_terms", pa.list_(pa.string()), nullable=False),
])
SENSITIVE_PARAMS = {"wskey", "apikey", "api_key", "key", "utm_campaign"}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def display_path(path):
    path = Path(path)
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def unique_strings(values):
    result = []
    seen = set()
    for value in values:
        if value is None:
            continue
        text = " ".join(str(value).split())
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def text_values(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (int, float)):
        return [str(value)]
    if isinstance(value, dict):
        values = []
        for item in value.values():
            values.extend(text_values(item))
        return values
    if isinstance(value, (list, tuple)):
        values = []
        for item in value:
            values.extend(text_values(item))
        return values
    return []


def clean_url(url):
    parsed = urlsplit(url)
    query = [(key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True) if key.lower() not in SENSITIVE_PARAMS]
    return urlunsplit(parsed._replace(query=urlencode(query, doseq=True)))


def sanitize_json(value):
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if key.lower() == "apikey":
                continue
            if key in {"link", "guid"} and isinstance(item, str):
                sanitized[key] = clean_url(item)
            else:
                sanitized[key] = sanitize_json(item)
        return sanitized
    if isinstance(value, list):
        return [sanitize_json(item) for item in value]
    return value


def should_retry(error):
    if isinstance(error, HTTPError):
        return error.code == 429 or 500 <= error.code < 600
    return isinstance(error, (URLError, HTTPException, TimeoutError, ConnectionError))


class HttpClient:
    def __init__(self, delay=1.0, timeout=30, retries=3, proxy=None, cache_dir=None):
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.cache_dir = Path(cache_dir) if cache_dir is not None else None
        if self.cache_dir is not None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        proxies = {"http": proxy, "https": proxy} if proxy else {}
        self.opener = build_opener(ProxyHandler(proxies))
        self.last_request = None
        self.network_requests = 0
        self.cache_hits = 0

    def _wait(self):
        if self.last_request is not None and self.delay > 0:
            remaining = self.delay - (time.monotonic() - self.last_request)
            if remaining > 0:
                time.sleep(remaining)

    def _cache_path(self, url, suffix):
        digest = hashlib.sha256(clean_url(url).encode("utf-8")).hexdigest()
        return self.cache_dir / (digest + suffix)

    def _error(self, url, error):
        if isinstance(error, HTTPError):
            detail = "HTTP {}".format(error.code)
        else:
            detail = str(error)
        return ValueError("Request failed: {} ({})".format(clean_url(url), detail))

    def _get_network(self, url):
        last_error = None
        for attempt in range(self.retries + 1):
            try:
                self._wait()
                request = Request(quote(url, safe=":/?#[]@!$&'()*+,;=%"), headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
                with self.opener.open(request, timeout=self.timeout) as response:
                    body = response.read()
                self.last_request = time.monotonic()
                self.network_requests += 1
                return body
            except (HTTPError, URLError, HTTPException, TimeoutError, ConnectionError, OSError) as error:
                self.last_request = time.monotonic()
                last_error = error
                if attempt >= self.retries or not should_retry(error):
                    break
                retry_after = error.headers.get("Retry-After") if isinstance(error, HTTPError) else None
                try:
                    pause = float(retry_after) if retry_after else 0.5 * (2 ** attempt)
                except ValueError:
                    pause = 0.5 * (2 ** attempt)
                time.sleep(min(pause, 60.0))
        raise self._error(url, last_error)

    def get_json(self, url):
        path = self._cache_path(url, ".json")
        cached = path.is_file()
        if cached:
            self.cache_hits += 1
            payload = json.loads(path.read_text(encoding="utf-8"))
        else:
            payload = json.loads(self._get_network(url).decode("utf-8"))
        sanitized = sanitize_json(payload)
        if not cached or sanitized != payload:
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_text(json.dumps(sanitized, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
            temporary.replace(path)
        return sanitized

    def get_text(self, url):
        path = self._cache_path(url, ".html")
        if path.is_file():
            self.cache_hits += 1
            return path.read_text(encoding="utf-8")
        body = self._get_network(url)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(body)
        temporary.replace(path)
        return body.decode("utf-8", "replace")

    def download(self, url, destination, max_bytes=None):
        part_path = destination.with_name(destination.name + ".part")
        last_error = None
        for attempt in range(self.retries + 1):
            try:
                self._wait()
                request = Request(quote(url, safe=":/?#[]@!$&'()*+,;=%"), headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"})
                with self.opener.open(request, timeout=self.timeout) as response:
                    content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
                    if content_type in {"text/html", "application/xhtml+xml"}:
                        raise ValueError("Expected a file, received {}: {}".format(content_type, clean_url(url)))
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    digest = hashlib.sha256()
                    size = 0
                    with part_path.open("wb") as handle:
                        while True:
                            chunk = response.read(1024 * 1024)
                            if not chunk:
                                break
                            handle.write(chunk)
                            digest.update(chunk)
                            size += len(chunk)
                            if max_bytes is not None and size > max_bytes:
                                raise ValueError("File exceeds {} bytes: {}".format(max_bytes, clean_url(url)))
                if size == 0:
                    raise ValueError("Empty file: {}".format(clean_url(url)))
                part_path.replace(destination)
                self.last_request = time.monotonic()
                self.network_requests += 1
                return {"bytes": size, "sha256": digest.hexdigest(), "content_type": content_type}
            except (HTTPError, URLError, HTTPException, TimeoutError, ConnectionError, OSError, ValueError) as error:
                part_path.unlink(missing_ok=True)
                self.last_request = time.monotonic()
                last_error = error
                if attempt >= self.retries or not should_retry(error):
                    break
                time.sleep(min(0.5 * (2 ** attempt), 60.0))
        if isinstance(last_error, ValueError):
            raise last_error
        raise self._error(url, last_error)


def matcher_record(record):
    return {
        "name": record.get("title"),
        "description": record.get("description"),
        "authors": record.get("authors"),
        "productionPlace": " ".join(record.get("places") or []),
        "findPlace": None,
        "mainWords": record.get("subjects"),
        "provenance": record.get("provider"),
        "typologyDesc": record.get("type"),
        "technologies": [],
        "fund": record.get("provider"),
        "museum": None,
        "typology": {"name": record.get("type")},
    }


def classify_candidate(record, matcher, query):
    match = matcher.classify(matcher_record(record))
    # A term suppressed by its negative context is evidence against relevance, so the query must not rescue it.
    if match.decision == "exclude" and not match.negated and matcher.classify({"name": query}).decision != "exclude":
        match.decision = "review"
        match.confidence = "review"
        match.strength = "source_query_only"
        match.reasons = ["source_query_only"]
    return match


OPEN_RIGHTS = re.compile(r"creativecommons\.org/(?:publicdomain/(?:mark|zero)|licenses/(?:by|by-sa))/")
# NoC-NC, NoC-OKLR and NoC-CR are "no copyright" statements that still restrict reuse; NoC-US applies only in the US.
RESTRICTED_RIGHTS = re.compile(
    r"rightsstatements\.org/vocab/(?:inc|noc-nc|noc-oklr|noc-cr|noc-us|cne|und|nkc)"
    r"|creativecommons\.org/licenses/[a-z-]*(?:nc|nd)"
)


def is_open_rights(rights):
    values = [value.lower() for value in rights or []]
    if any(RESTRICTED_RIGHTS.search(value) for value in values):
        return False
    return any(OPEN_RIGHTS.search(value) for value in values)


def base_record(record_id, source, record_url, query, retrieved_at):
    return {
        "id": str(record_id),
        "source": source,
        "record_url": record_url,
        "title": None,
        "description": None,
        "authors": [],
        "date": None,
        "places": [],
        "subjects": [],
        "languages": [],
        "type": None,
        "provider": None,
        "rights": [],
        "access": "unknown",
        "assets": [],
        "source_queries": [query],
        "retrieved_at": retrieved_at,
        "raw_json": "{}",
    }


class AuditSamples:
    def __init__(self, size=100):
        self.size = size
        self.heaps = {"include": [], "review": [], "exclude": []}

    def add(self, decision, record, metadata):
        digest = int(hashlib.sha256("{}:{}:{}".format(record["source"], record["id"], decision).encode("utf-8")).hexdigest()[:16], 16)
        payload = {
            "decision": decision,
            "id": record["id"],
            "title": record.get("title"),
            "record_url": record.get("record_url"),
            "matched_terms": json.dumps(metadata["armenia_matched_terms"], ensure_ascii=False),
            "matched_fields": json.dumps(metadata["armenia_matched_fields"], ensure_ascii=False),
            "reasons": json.dumps(metadata["armenia_match_reasons"], ensure_ascii=False),
            "negated_terms": json.dumps(metadata["armenia_negated_terms"], ensure_ascii=False),
            "description": (record.get("description") or "")[:1000],
        }
        heap = self.heaps[decision]
        item = (-digest, record["id"], payload)
        if len(heap) < self.size:
            heapq.heappush(heap, item)
        elif digest < -heap[0][0]:
            heapq.heapreplace(heap, item)

    def write(self, path):
        fieldnames = ["decision", "id", "title", "record_url", "matched_terms", "matched_fields", "reasons", "negated_terms", "description"]
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for decision in ("include", "review", "exclude"):
                for item in sorted(self.heaps[decision], key=lambda value: value[1]):
                    writer.writerow(item[2])
        temporary.replace(path)


class ParquetOutputs:
    def __init__(self, output_dir, batch_size=1000):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.batch_size = batch_size
        self.paths = {decision: self.output_dir / name for decision, name in (("include", "armenia_records.parquet"), ("review", "armenia_review.parquet"))}
        self.temporary = {decision: path.with_suffix(".parquet.tmp") for decision, path in self.paths.items()}
        self.writers = {decision: pq.ParquetWriter(str(path), RECORD_SCHEMA, compression="zstd") for decision, path in self.temporary.items()}
        self.buffers = {"include": [], "review": []}
        self.counts = {"include": 0, "review": 0, "exclude": 0}
        self.samples = AuditSamples()
        self.extra_queries = {}

    def add_query(self, record_id, query):
        # A record found again by a later query keeps one row; the query is merged into it on close.
        self.extra_queries.setdefault(str(record_id), []).append(query)

    def add(self, record, match):
        metadata = match.metadata()
        decision = match.decision
        self.counts[decision] += 1
        self.samples.add(decision, record, metadata)
        if decision == "exclude":
            return
        row = dict(record)
        row["raw_json"] = json.dumps(row["raw_json"], ensure_ascii=False, sort_keys=True) if not isinstance(row["raw_json"], str) else row["raw_json"]
        row.update(metadata)
        self.buffers[decision].append(row)
        if len(self.buffers[decision]) >= self.batch_size:
            self._flush(decision)

    def _flush(self, decision):
        if not self.buffers[decision]:
            return
        table = pa.Table.from_pylist(self.buffers[decision], schema=RECORD_SCHEMA)
        self.writers[decision].write_table(table)
        self.buffers[decision] = []

    def _merge_queries(self, decision):
        path = self.temporary[decision]
        merged = path.with_suffix(".merged.tmp")
        writer = pq.ParquetWriter(str(merged), RECORD_SCHEMA, compression="zstd")
        try:
            for batch in pq.ParquetFile(str(path)).iter_batches(batch_size=self.batch_size):
                rows = batch.to_pylist()
                for row in rows:
                    row["source_queries"] = unique_strings(row["source_queries"] + self.extra_queries.get(row["id"], []))
                writer.write_table(pa.Table.from_pylist(rows, schema=RECORD_SCHEMA))
        except Exception:
            writer.close()
            merged.unlink(missing_ok=True)
            raise
        writer.close()
        merged.replace(path)

    def close(self):
        for decision in ("include", "review"):
            self._flush(decision)
            self.writers[decision].close()
            if self.extra_queries:
                self._merge_queries(decision)
            if pq.ParquetFile(str(self.temporary[decision])).metadata.num_rows != self.counts[decision]:
                raise ValueError("Output row count verification failed for {}".format(decision))
            self.temporary[decision].replace(self.paths[decision])
        self.samples.write(self.output_dir / "audit_sample.csv")

    def abort(self):
        for writer in self.writers.values():
            writer.close()
        for path in self.temporary.values():
            path.unlink(missing_ok=True)


def write_json(path, payload):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def append_jsonl(path, payload):
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
