#!/usr/bin/env python3
import argparse
import hashlib
import json
import mimetypes
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pyarrow as pa
import pyarrow.parquet as pq

from source_common import HttpClient, display_path, is_open_rights, utc_now, write_json

MANIFEST_NAME = "asset_manifest.jsonl"
REPORT_NAME = "asset_download_report.json"


def safe_record_id(value):
    readable = re.sub(r"[^A-Za-z0-9_-]", "_", value).strip("_")[:80] or "record"
    return readable + "-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def extension(asset):
    mime_type = (asset.get("mime_type") or "").split(";", 1)[0].lower()
    known = {"image/jpeg": ".jpg", "image/png": ".png", "application/pdf": ".pdf", "image/tiff": ".tif"}
    if mime_type in known:
        return known[mime_type]
    guessed = mimetypes.guess_extension(mime_type) if mime_type else None
    if guessed:
        return guessed
    suffix = Path(unquote(urlsplit(asset["url"]).path)).suffix.lower()
    return suffix if re.fullmatch(r"\.[a-z0-9]{1,5}", suffix) else ".bin"


def read_inventory(input_path, source, include_restricted):
    table = pq.read_table(input_path, columns=["id", "source", "record_url", "rights", "access", "assets"])
    assets = []
    rights_skipped = 0
    records = 0
    records_with_assets = 0
    for row in table.to_pylist():
        if row["source"] != source:
            continue
        records += 1
        row_assets = row.get("assets") or []
        if row_assets:
            records_with_assets += 1
        for index, asset in enumerate(row_assets, 1):
            if source == "europeana" and not include_restricted and not is_open_rights(row.get("rights")):
                rights_skipped += 1
                continue
            if source == "neb" and row.get("access") != "open":
                rights_skipped += 1
                continue
            if not asset.get("url", "").startswith(("http://", "https://")):
                rights_skipped += 1
                continue
            assets.append({
                "record_id": str(row["id"]),
                "record_url": row["record_url"],
                "asset_index": index,
                "url": asset["url"],
                "mime_type": asset.get("mime_type"),
                "role": asset.get("role"),
                "expected_bytes": asset.get("expected_bytes"),
            })
    inventory = {
        "records": records,
        "records_with_assets": records_with_assets,
        "eligible_asset_links": len(assets),
        "rights_or_access_skipped": rights_skipped,
    }
    return assets, inventory


def result_key(result):
    return result["source"], result["record_id"], result["asset_index"], result["source_url"]


def asset_key(asset, source):
    return source, asset["record_id"], asset["asset_index"], asset["url"]


def load_manifest(path, output_dir):
    previous = {}
    if not path.is_file():
        return previous
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                result = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError("Invalid manifest line {}: {}".format(line_number, error))
            if result.get("status") == "ok" and result.get("path"):
                downloaded = output_dir / result["path"]
                if downloaded.is_file() and downloaded.stat().st_size == result.get("bytes"):
                    previous[result_key(result)] = result
    return previous


def run(args):
    input_path = args.input.resolve()
    if not input_path.is_file():
        raise ValueError("Input Parquet does not exist: {}".format(input_path))
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    started_at = utc_now()
    started = time.monotonic()
    assets, inventory = read_inventory(input_path, args.source, args.include_restricted)
    if args.max_files is not None:
        assets = assets[:args.max_files]
    manifest_path = output_dir / MANIFEST_NAME
    previous = load_manifest(manifest_path, output_dir)
    pending = []
    skipped = []
    for asset in assets:
        cached = previous.get(asset_key(asset, args.source))
        if cached is None:
            pending.append(asset)
        else:
            skipped.append(cached)
    delay = args.delay if args.delay is not None else (3.0 if args.source == "neb" else 1.0)
    client = HttpClient(delay, args.timeout, args.retries, args.proxy)
    print("Eligible files: {}; already downloaded: {}; remaining: {}".format(len(assets), len(skipped), len(pending)), flush=True)
    completed = []
    with manifest_path.open("a", encoding="utf-8") as manifest:
        for number, asset in enumerate(pending, 1):
            result = {
                "source": args.source,
                "record_id": asset["record_id"],
                "record_url": asset["record_url"],
                "asset_index": asset["asset_index"],
                "source_url": asset["url"],
                "role": asset["role"],
                "expected_bytes": asset["expected_bytes"],
            }
            destination = output_dir / "files" / safe_record_id(asset["record_id"]) / ("{:03d}{}".format(asset["asset_index"], extension(asset)))
            try:
                downloaded = client.download(asset["url"], destination)
                result.update(downloaded)
                result.update({"status": "ok", "path": destination.relative_to(output_dir).as_posix()})
            except ValueError as error:
                result.update({"status": "error", "error": str(error)})
            manifest.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            manifest.flush()
            completed.append(result)
            print("[{}/{}] {} {}".format(number, len(pending), result["status"], asset["url"]), flush=True)
    downloaded = [result for result in completed if result["status"] == "ok"]
    failed = [result for result in completed if result["status"] == "error"]
    report = {
        "source": args.source,
        "mode": "download",
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "input": {"path": display_path(input_path), **inventory},
        "settings": {
            "max_files": args.max_files,
            "include_restricted": args.include_restricted,
            "delay_seconds": delay,
            "timeout_seconds": args.timeout,
            "retries": args.retries,
            "proxy": args.proxy,
        },
        "counts": {
            "requested": len(assets),
            "downloaded": len(downloaded),
            "skipped": len(skipped),
            "failed": len(failed),
        },
        "bytes": {
            "downloaded_this_run": sum(result["bytes"] for result in downloaded),
            "available_total": sum((output_dir / result["path"]).stat().st_size for result in skipped + downloaded),
        },
        "manifest": display_path(manifest_path),
        "errors": failed,
    }
    if args.source == "neb":
        report["download_notice"] = "NEB downloads must remain explicitly bounded. The NEB user agreement prohibits mass automated downloading of NEB objects without operator permission."
    write_json(output_dir / REPORT_NAME, report)
    print("Downloaded: {}; skipped: {}; failed: {}".format(len(downloaded), len(skipped), len(failed)))
    print("Report:", output_dir / REPORT_NAME)
    return report


def parse_args():
    parser = argparse.ArgumentParser(description="Download assets from normalized Europeana or NEB Parquet records")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source", choices=("europeana", "neb"), required=True)
    parser.add_argument("--max-files", type=int, help="Required for NEB; optional cap for Europeana")
    parser.add_argument("--include-restricted", action="store_true", help="Europeana only: allow assets without an open rights statement")
    parser.add_argument("--proxy")
    parser.add_argument("--delay", type=float)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()
    if args.max_files is not None and args.max_files < 1:
        parser.error("max-files must be positive")
    if args.source == "neb" and args.max_files is None:
        parser.error("--max-files is required for NEB to prevent an unbounded automated download")
    if args.source == "neb" and args.include_restricted:
        parser.error("--include-restricted is available only for Europeana")
    if args.timeout < 1 or args.retries < 0 or (args.delay is not None and args.delay < 0):
        parser.error("timeout must be positive; delay and retries must be non-negative")
    return args


def main():
    try:
        report = run(parse_args())
    except (OSError, ValueError, pa.ArrowException) as error:
        print("Error: {}".format(error), file=sys.stderr)
        return 1
    return 1 if report["counts"]["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
