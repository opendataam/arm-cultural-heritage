#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
import mimetypes
import random
import re
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from http.client import HTTPException, IncompleteRead
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import pyarrow as pa
import pyarrow.parquet as pq

USER_AGENT = "arm-cultural-heritage-image-downloader/1.0 (+https://github.com/opendataam/arm-cultural-heritage)"
REFERER = "https://goskatalog.ru/portal/"
MANIFEST_NAME = "image_manifest.jsonl"
DOWNLOAD_REPORT_NAME = "image_download_report.json"
ESTIMATE_REPORT_NAME = "image_estimate.json"
CHUNK_SIZE = 1024 * 1024
IMAGE_SIGNATURES = (
    (b"\xff\xd8\xff", ".jpg"),
    (b"\x89PNG\r\n\x1a\n", ".png"),
    (b"GIF87a", ".gif"),
    (b"GIF89a", ".gif"),
    (b"II*\x00", ".tif"),
    (b"MM\x00*", ".tif"),
)


@dataclass(frozen=True)
class Asset:
    record_id: str
    image_index: int
    url: str


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def normalize_url(url):
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Invalid image URL: {}".format(url))
    if parsed.scheme == "http" and parsed.hostname in {"goskatalog.ru", "www.goskatalog.ru"}:
        parsed = parsed._replace(scheme="https")
    return urlunsplit(parsed)


def read_assets(input_path):
    table = pq.read_table(input_path, columns=["id", "images"])
    assets = []
    records_with_images = 0
    max_images_per_record = 0
    for row in table.to_pylist():
        images = row.get("images") or []
        if images:
            records_with_images += 1
        max_images_per_record = max(max_images_per_record, len(images))
        for image_index, image in enumerate(images, 1):
            if not isinstance(image, dict) or not image.get("url"):
                raise ValueError("Record {} has an image without a URL".format(row.get("id")))
            assets.append(Asset(str(row["id"]), image_index, normalize_url(image["url"])))
    inventory = {
        "records": table.num_rows,
        "records_with_images": records_with_images,
        "records_without_images": table.num_rows - records_with_images,
        "image_links": len(assets),
        "distinct_image_urls": len({asset.url for asset in assets}),
        "max_images_per_record": max_images_per_record,
    }
    return assets, inventory


def asset_key(asset):
    return asset.record_id, asset.image_index, asset.url


def result_key(result):
    return str(result["record_id"]), result["image_index"], result["source_url"]


def base_result(asset):
    return {
        "record_id": asset.record_id,
        "image_index": asset.image_index,
        "source_url": asset.url,
    }


def safe_component(value):
    return re.sub(r"[^A-Za-z0-9_-]", "_", value) or "unknown"


def image_extension(headers):
    content_type = headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
    disposition = headers.get("Content-Disposition", "")
    match = re.search(r"filename\s*=\s*[\"']?([^\"';]+)", disposition, re.IGNORECASE)
    if match:
        suffix = Path(unquote(match.group(1).strip())).suffix.lower()
        if re.fullmatch(r"\.[a-z0-9]{1,5}", suffix):
            return suffix
    if content_type == "image/jpeg":
        return ".jpg"
    return mimetypes.guess_extension(content_type) or ".bin"


def sniffed_extension(head):
    for signature, suffix in IMAGE_SIGNATURES:
        if head.startswith(signature):
            return suffix
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return ".webp"
    return None


def destination_stem(asset, output_dir):
    url_name = Path(urlsplit(asset.url).path).name
    image_id = safe_component(unquote(url_name))
    return output_dir / safe_component(asset.record_id) / "{:03d}_{}".format(asset.image_index, image_id)


def expected_length(headers):
    if headers.get("Content-Encoding"):
        return None
    try:
        return int(headers.get("Content-Length"))
    except (TypeError, ValueError):
        return None


def should_retry(error):
    if isinstance(error, HTTPError):
        return error.code == 429 or 500 <= error.code < 600
    return isinstance(error, (URLError, HTTPException, TimeoutError))


def fetch(asset, output_dir, timeout, retries):
    result = base_result(asset)
    part_path = None
    for attempt in range(retries + 1):
        try:
            request = Request(asset.url, headers={"User-Agent": USER_AGENT, "Referer": REFERER})
            with urlopen(request, timeout=timeout) as response:
                content_type = response.headers.get("Content-Type", "").split(";", 1)[0].lower()
                if not content_type.startswith("image/"):
                    raise ValueError("Expected an image, received {}".format(content_type or "unknown content type"))
                if output_dir is not None:
                    stem = destination_stem(asset, output_dir)
                    stem.parent.mkdir(parents=True, exist_ok=True)
                    part_path = stem.with_name(stem.name + ".part")
                    handle = part_path.open("wb")
                else:
                    stem = None
                    handle = None
                digest = hashlib.sha256()
                size = 0
                head = b""
                try:
                    while True:
                        chunk = response.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        if not head:
                            head = chunk[:16]
                        size += len(chunk)
                        digest.update(chunk)
                        if handle is not None:
                            handle.write(chunk)
                finally:
                    if handle is not None:
                        handle.close()
                if size == 0:
                    raise ValueError("Empty image response")
                # http.client returns a short body without an error when the connection closes early.
                expected = expected_length(response.headers)
                if expected is not None and size != expected:
                    raise IncompleteRead(b"", expected - size)
                destination = None
                if part_path is not None:
                    destination = stem.with_name(stem.name + (sniffed_extension(head) or image_extension(response.headers)))
                    part_path.replace(destination)
                result.update({
                    "status": "ok",
                    "bytes": size,
                    "content_type": content_type,
                    "sha256": digest.hexdigest(),
                })
                if destination is not None:
                    result["path"] = destination.relative_to(output_dir).as_posix()
                return result
        except (HTTPError, URLError, HTTPException, OSError, ValueError) as error:
            if part_path is not None:
                part_path.unlink(missing_ok=True)
                part_path = None
            result.update({"status": "error", "error": str(error)})
            if attempt < retries and should_retry(error):
                time.sleep(0.5 * (2 ** attempt))
                continue
            return result
    return result


def run_fetches(assets, output_dir, timeout, retries, workers):
    results = []
    started = time.monotonic()
    last_progress = started
    executor = ThreadPoolExecutor(max_workers=workers)
    try:
        futures = [executor.submit(fetch, asset, output_dir, timeout, retries) for asset in assets]
        for completed, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            yield result
            now = time.monotonic()
            if now - last_progress >= 30:
                failed = sum(item["status"] == "error" for item in results)
                print("Processed {:,}/{:,}; failed: {:,}; elapsed: {:.0f}s".format(
                    completed, len(assets), failed, now - started
                ), flush=True)
                last_progress = now
    finally:
        # On interruption, drop queued downloads instead of finishing them without recording them in the manifest.
        executor.shutdown(wait=True, cancel_futures=True)


def write_json(path, payload):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path, output_dir, verify_hashes=False):
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
                downloaded_path = output_dir / result["path"]
                if not downloaded_path.is_file() or downloaded_path.stat().st_size != result.get("bytes"):
                    continue
                if verify_hashes and file_sha256(downloaded_path) != result.get("sha256"):
                    continue
                previous[result_key(result)] = result
    return previous


def report_base(args, input_path, inventory, started_at, started):
    return {
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "input": {"path": str(input_path), **inventory},
        "settings": {
            "workers": args.workers,
            "timeout_seconds": args.timeout,
            "retries": args.retries,
            "verify_hashes": args.verify_hashes,
        },
    }


def download(args, input_path, assets, inventory, started_at, started):
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / MANIFEST_NAME
    previous = load_manifest(manifest_path, output_dir, args.verify_hashes)
    pending = []
    skipped = []
    for asset in assets:
        cached = previous.get(asset_key(asset))
        if cached is not None:
            skipped.append(cached)
        else:
            pending.append(asset)
    print("Images: {:,}; already downloaded: {:,}; remaining: {:,}".format(
        len(assets), len(skipped), len(pending)
    ), flush=True)
    completed = []
    with manifest_path.open("a", encoding="utf-8") as manifest:
        for result in run_fetches(pending, output_dir, args.timeout, args.retries, args.workers):
            manifest.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            manifest.flush()
            completed.append(result)
    downloaded = [result for result in completed if result["status"] == "ok"]
    failed = [result for result in completed if result["status"] == "error"]
    available = skipped + downloaded
    report = report_base(args, input_path, inventory, started_at, started)
    report.update({
        "mode": "download",
        "counts": {
            "requested": len(assets),
            "downloaded": len(downloaded),
            "skipped": len(skipped),
            "failed": len(failed),
        },
        "bytes": {
            "downloaded_this_run": sum(result["bytes"] for result in downloaded),
            "available_total": sum((output_dir / result["path"]).stat().st_size for result in available),
        },
        "manifest": str(manifest_path),
        "errors": failed,
    })
    report_path = output_dir / DOWNLOAD_REPORT_NAME
    write_json(report_path, report)
    print("Downloaded: {:,}; skipped: {:,}; failed: {:,}".format(
        len(downloaded), len(skipped), len(failed)
    ), flush=True)
    print("Report:", report_path)
    return report


def estimate(args, input_path, assets, inventory, started_at, started):
    if not assets:
        raise ValueError("Input contains no images")
    sample_size = min(args.sample_size, len(assets))
    sample = random.Random(args.seed).sample(assets, sample_size)
    print("Estimating {:,} images from a sample of {:,}".format(len(assets), sample_size), flush=True)
    results = list(run_fetches(sample, None, args.timeout, args.retries, args.workers))
    succeeded = [result for result in results if result["status"] == "ok"]
    failed = [result for result in results if result["status"] == "error"]
    if not succeeded:
        raise ValueError("Could not measure any sampled images")
    successful_sizes = [result["bytes"] for result in succeeded]
    observed_sizes = successful_sizes + [0] * len(failed)
    sampled_bytes = sum(successful_sizes)
    mean_successful = sampled_bytes / len(succeeded)
    mean_per_link = sampled_bytes / len(observed_sizes)
    estimated_total = mean_per_link * len(assets)
    interval = None
    if len(observed_sizes) > 1:
        margin = 1.96 * statistics.stdev(observed_sizes) / math.sqrt(len(observed_sizes)) * len(assets)
        interval = {
            "lower_bytes": max(0, round(estimated_total - margin)),
            "upper_bytes": round(estimated_total + margin),
        }
    report = report_base(args, input_path, inventory, started_at, started)
    report.update({
        "mode": "estimate",
        "method": "Deterministic simple random sample of image links; full GET responses measured in memory; failed requests count as zero downloadable bytes",
        "sample": {
            "seed": args.seed,
            "requested": sample_size,
            "succeeded": len(succeeded),
            "failed": len(failed),
            "bytes": sampled_bytes,
            "mean_bytes": mean_successful,
            "mean_bytes_per_link": mean_per_link,
        },
        "estimated_available_images": round(len(assets) * len(succeeded) / sample_size),
        "estimated_total_bytes": round(estimated_total),
        "confidence_interval_95": interval,
        "errors": failed,
    })
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / ESTIMATE_REPORT_NAME
    write_json(report_path, report)
    print("Sampled: {:,}; failed: {:,}; mean: {:.1f} MiB".format(
        len(succeeded), len(failed), mean_successful / (1024 ** 2)
    ), flush=True)
    print("Estimated total: {:.2f} GiB".format(estimated_total / (1024 ** 3)))
    if interval:
        print("Approximate 95% interval: {:.2f}–{:.2f} GiB".format(
            interval["lower_bytes"] / (1024 ** 3), interval["upper_bytes"] / (1024 ** 3)
        ))
    print("Report:", report_path)
    return report


def run(args):
    input_path = args.input.resolve()
    if not input_path.is_file():
        raise ValueError("Input Parquet does not exist: {}".format(input_path))
    started_at = utc_now()
    started = time.monotonic()
    assets, inventory = read_assets(input_path)
    print("Records: {:,}; with images: {:,}; image links: {:,}; maximum per record: {:,}".format(
        inventory["records"], inventory["records_with_images"], inventory["image_links"],
        inventory["max_images_per_record"]
    ), flush=True)
    if args.estimate_only:
        return estimate(args, input_path, assets, inventory, started_at, started)
    return download(args, input_path, assets, inventory, started_at, started)


def parse_args():
    parser = argparse.ArgumentParser(description="Download every image linked from Goskatalog Parquet records")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--estimate-only", action="store_true", help="Measure a random sample without saving images")
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--verify-hashes", action="store_true", help="Recompute SHA-256 of completed files before skipping them")
    args = parser.parse_args()
    if args.sample_size < 1 or args.workers < 1 or args.timeout < 1 or args.retries < 0:
        parser.error("sample-size, workers and timeout must be positive; retries must be non-negative")
    return args


def main():
    try:
        report = run(parse_args())
    except (OSError, ValueError, pa.ArrowException) as error:
        print("Error: {}".format(error), file=sys.stderr)
        return 1
    if report["mode"] == "download" and report["counts"]["failed"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
