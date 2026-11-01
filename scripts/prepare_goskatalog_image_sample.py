#!/usr/bin/env python3
import argparse
import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pyarrow as pa
import pyarrow.parquet as pq

USER_AGENT = "arm-cultural-heritage-image-downloader/1.0 (+https://github.com/opendataam/arm-cultural-heritage)"
REFERER = "https://goskatalog.ru/portal/"
API_CACHE_NAME = "api_records.jsonl"
SAMPLE_NAME = "image_sample.parquet"
REPORT_NAME = "image_sample_report.json"
API_CHUNK_SIZE = 100
# Only answers that describe the record itself are reused; 403, 429, 5xx and network errors are refetched on rerun.
FINAL_API_STATUSES = {200, 404, 410}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, payload):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_api_cache(path):
    cache = {}
    if not path.is_file():
        return cache
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                result = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError("Invalid API cache line {}: {}".format(line_number, error))
            cache[str(result["requested_id"])] = result
    return cache


def fetch_api_record(record_id, timeout, retries):
    url = "https://goskatalog.ru/muzfo-rest/rest/exhibits/{}".format(quote(record_id, safe=""))
    result = {"requested_id": record_id}
    for attempt in range(retries + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT, "Referer": REFERER})
            with urlopen(request, timeout=timeout) as response:
                result.update({"http_status": response.status, "response": json.load(response)})
                return result
        except HTTPError as error:
            result.update({"http_status": error.code, "response": None, "error": str(error)})
            if error.code != 429 and not 500 <= error.code < 600:
                return result
        except (URLError, HTTPException, OSError, ValueError) as error:
            result.update({"http_status": None, "response": None, "error": str(error)})
        if attempt < retries:
            time.sleep(0.5 * (2 ** attempt))
    return result


def current_images(api_result):
    if api_result.get("http_status") != 200 or not isinstance(api_result.get("response"), dict):
        return []
    images = []
    for image in api_result["response"].get("images") or []:
        if image.get("id") is None or image.get("deleted") is True or image.get("status") == 3:
            continue
        image_id = quote(str(image["id"]), safe="")
        images.append({"url": "https://goskatalog.ru/muzfo-imaginator/rest/images/original/{}".format(image_id)})
    return images


def prepare(args):
    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()
    if not input_path.is_file():
        raise ValueError("Input Parquet does not exist: {}".format(input_path))
    output_dir.mkdir(parents=True, exist_ok=True)
    started_at = utc_now()
    started = time.monotonic()
    table = pq.read_table(input_path)
    candidates = [row for row in table.to_pylist() if row.get("images")]
    input_image_links = sum(len(row["images"]) for row in candidates)
    random.Random(args.seed).shuffle(candidates)
    cache_path = output_dir / API_CACHE_NAME
    cache = load_api_cache(cache_path)
    selected = []
    selected_count = 0
    considered = set()
    status_counts = {}
    empty_records = 0
    over_cap_records = 0
    fetched_this_run = 0
    last_progress = started
    with cache_path.open("a", encoding="utf-8") as cache_handle, ThreadPoolExecutor(max_workers=args.workers) as executor:
        for offset in range(0, len(candidates), API_CHUNK_SIZE):
            chunk = candidates[offset:offset + API_CHUNK_SIZE]
            pending = [row for row in chunk if cache.get(str(row["id"]), {}).get("http_status") not in FINAL_API_STATUSES]
            if pending:
                results = list(executor.map(
                    lambda row: fetch_api_record(str(row["id"]), args.timeout, args.retries), pending
                ))
                for result in results:
                    result["fetched_at"] = utc_now()
                    cache_handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
                    cache_handle.flush()
                    cache[result["requested_id"]] = result
                    fetched_this_run += 1
            for row in chunk:
                record_id = str(row["id"])
                considered.add(record_id)
                api_result = cache[record_id]
                status = api_result.get("http_status")
                status_counts[str(status)] = status_counts.get(str(status), 0) + 1
                images = current_images(api_result)
                if not images:
                    if status == 200:
                        empty_records += 1
                    continue
                if selected_count + len(images) > args.max_images:
                    # Stop instead of skipping ahead: skipping biases the tail towards small records
                    # and can query the API for every remaining candidate.
                    over_cap_records += 1
                    break
                row["images"] = images
                selected.append(row)
                selected_count += len(images)
                if selected_count == args.max_images:
                    break
            now = time.monotonic()
            if now - last_progress >= 30:
                print("API records considered: {:,}; selected images: {:,}/{:,}; elapsed: {:.0f}s".format(
                    len(considered), selected_count, args.max_images, now - started
                ), flush=True)
                last_progress = now
            if selected_count == args.max_images or over_cap_records:
                break
    selected_count = sum(len(item["images"]) for item in selected)
    if not selected:
        raise ValueError("No images available for the sample")
    sample_path = output_dir / SAMPLE_NAME
    temporary = sample_path.with_suffix(".parquet.tmp")
    pq.write_table(pa.Table.from_pylist(selected, schema=table.schema), temporary, compression="zstd")
    temporary.replace(sample_path)
    report = {
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "input": {
            "path": str(input_path),
            "records": table.num_rows,
            "records_with_images": len(candidates),
            "image_links": input_image_links,
        },
        "settings": {
            "seed": args.seed,
            "max_images": args.max_images,
            "workers": args.workers,
            "timeout_seconds": args.timeout,
            "retries": args.retries,
        },
        "counts": {
            "api_records_considered": len(considered),
            "api_records_fetched_this_run": fetched_this_run,
            "api_http_status": status_counts,
            "api_records_without_images": empty_records,
            "records_over_cap": over_cap_records,
            "selected_records": len(selected),
            "selected_images": selected_count,
        },
        "outputs": {
            "sample": str(sample_path),
            "sample_bytes": sample_path.stat().st_size,
            "api_cache": str(cache_path),
        },
    }
    report_path = output_dir / REPORT_NAME
    write_json(report_path, report)
    print("Selected {:,} images from {:,} records; API unavailable: {}".format(
        selected_count, len(selected), sum(count for status, count in status_counts.items() if status != "200")
    ), flush=True)
    print("Sample:", sample_path)
    print("Report:", report_path)
    return report


def parse_args():
    parser = argparse.ArgumentParser(description="Prepare a deterministic API-refreshed Goskatalog image sample")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-images", type=int, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()
    if args.max_images < 1 or args.workers < 1 or args.timeout < 1 or args.retries < 0:
        parser.error("max-images, workers and timeout must be positive; retries must be non-negative")
    return args


def main():
    try:
        prepare(parse_args())
    except (OSError, ValueError, pa.ArrowException) as error:
        print("Error: {}".format(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
