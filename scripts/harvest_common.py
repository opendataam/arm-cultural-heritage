#!/usr/bin/env python3
"""Shared helpers for harvesters of Armenian-focused sources.

Harvesters write one Parquet file per source with flat, source-specific columns
plus the nine `armenia_*` metadata fields produced by the extractor, so the portal
connectors treat every source the same way.
"""
import hashlib
import http.client
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from matcher import ArmeniaMatcher
from terms import read_terms

ROOT = Path(__file__).resolve().parent.parent
USER_AGENT = "opendataam-arm-cultural-heritage/1.1 (https://github.com/opendataam/arm-cultural-heritage)"
RETRY_STATUSES = {429, 500, 502, 503, 504}
METADATA_FIELDS = [
    ("armenia_decision", pa.string()),
    ("armenia_confidence", pa.string()),
    ("armenia_match_strength", pa.string()),
    ("armenia_matched_entities", pa.list_(pa.string())),
    ("armenia_matched_terms", pa.list_(pa.string())),
    ("armenia_matched_forms", pa.list_(pa.string())),
    ("armenia_matched_fields", pa.list_(pa.string())),
    ("armenia_match_reasons", pa.list_(pa.string())),
    ("armenia_negated_terms", pa.list_(pa.string())),
]


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Client:
    """Polite HTTP client: identifying User-Agent, minimum delay, retries with backoff."""

    def __init__(self, delay=0.5, timeout=120, retries=5):
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.last = 0.0
        self.requests = 0

    def get(self, url, params=None, data=None, headers=None):
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        body = urllib.parse.urlencode(data).encode() if data else None
        request_headers = {"User-Agent": USER_AGENT, **(headers or {})}
        for attempt in range(self.retries):
            wait = self.delay - (time.monotonic() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.monotonic()
            self.requests += 1
            request = urllib.request.Request(url, data=body, headers=request_headers)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    return response.read(), dict(response.headers)
            except urllib.error.HTTPError as error:
                if error.code not in RETRY_STATUSES or attempt == self.retries - 1:
                    raise
                retry_after = error.headers.get("Retry-After")
                pause = float(retry_after) if retry_after and retry_after.isdigit() else 2 ** attempt * 5
                print("HTTP {} from {}, retrying in {:.0f} s".format(error.code, url.split("?")[0], pause), file=sys.stderr, flush=True)
                time.sleep(pause)
            except (urllib.error.URLError, http.client.HTTPException, ConnectionError, TimeoutError):
                if attempt == self.retries - 1:
                    raise
                time.sleep(2 ** attempt * 5)
        raise RuntimeError("unreachable")

    def json(self, url, params=None, data=None, headers=None, maxlag_retries=30):
        """Decode JSON; MediaWiki `maxlag` refusals are retried after the advised pause."""
        for _ in range(maxlag_retries):
            content, response_headers = self.get(url, params, data, {"Accept": "application/json", **(headers or {})})
            decoded = json.loads(content)
            error = decoded.get("error") if isinstance(decoded, dict) else None
            if not error:
                return decoded, response_headers
            if error.get("code") != "maxlag":
                raise RuntimeError("{} returned an error: {}".format(url, error.get("info") or error))
            retry_after = response_headers.get("Retry-After")
            print("maxlag from {}, waiting".format(url), file=sys.stderr, flush=True)
            time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else 5)
        raise RuntimeError("{} kept refusing requests because of replication lag".format(url))


class Annotator:
    """Links records of dedicated sources to registry entities with the project matcher.

    Every record of a dedicated source is relevant by scope, so the decision is always
    `include`; the matcher contributes entities, matched terms and fields as evidence.
    Fields use the extractor's names (`name`, `description`, `productionPlace`, ...)
    so the portal maps them to relevance criteria in one place.
    """

    def __init__(self, terms_path=ROOT / "data" / "terms.csv"):
        self.matcher = ArmeniaMatcher(read_terms(terms_path))

    def annotate(self, fields):
        metadata = self.matcher.classify(fields).metadata()
        metadata["armenia_decision"] = "include"
        metadata["armenia_confidence"] = "source"
        metadata["armenia_match_reasons"] = sorted({"dedicated_source", *metadata["armenia_match_reasons"]} - {"no_active_match"})
        return metadata


def write_parquet(path, rows, columns):
    """Write rows with an explicit schema: source columns first, then armenia_* metadata."""
    schema = pa.schema([*columns, *METADATA_FIELDS])
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows, schema=schema)
    temporary = path.with_suffix(path.suffix + ".tmp")
    pq.write_table(table, temporary, compression="zstd")
    temporary.replace(path)
    return table.num_rows


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_report(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
