# Armenian Cultural Heritage

Tools and derived datasets for finding records related to Armenia and the Armenian people in the Museum Fund of the Russian Federation export from [Goskatalog](https://goskatalog.ru/).

The extractor scans Parquet metadata with DuckDB, classifies candidates with a field-aware matcher, and writes auditable Parquet outputs. It preserves all source columns and does not modify the input.

## Published data

The current result in [`output/goskatalog/`](output/goskatalog/) was produced on 2026-10-31 from 31,741,256 source records:

| Result | Records | Meaning |
| --- | ---: | --- |
| `armenia_records.parquet` | 58,291 | Strong content evidence for automatic inclusion |
| `armenia_review.parquet` | 86,714 | Ambiguous candidates requiring contextual or manual review |
| `audit_sample.csv` | 300 | Deterministic sample of included, review, and excluded candidates |
| `report.json` | — | Source and registry hashes, settings, counts, timing, and match statistics |
| `evaluation.json` | 93 labeled records | Metrics for the manually labeled sample only |

The previous complete result is preserved in [`output/goskatalog_v1/`](output/goskatalog_v1/): 50,548 included and 75,968 review records. It can be used with `--resume-from` to compare or reproduce the transition to the current registry.

These are candidate-extraction results, not a definitive catalog of Armenian heritage. In particular, `armenia_review.parquet` must not be treated as confirmed relevant material. Evaluation metrics describe only the labeled sample, not the full corpus.

Both Parquet outputs retain every source field and add nine metadata fields:

- `armenia_decision`, `armenia_confidence`, and `armenia_match_strength`;
- `armenia_matched_entities`, `armenia_matched_terms`, and `armenia_matched_forms`;
- `armenia_matched_fields`, `armenia_match_reasons`, and `armenia_negated_terms`.

Example inspection with DuckDB:

```bash
duckdb -c "SELECT id, name, armenia_matched_terms, armenia_matched_fields FROM 'output/goskatalog/armenia_records.parquet' LIMIT 20"
```

## Thematic tagging for Armeniana

The current result in [`output/armeniana/`](output/armeniana/) applies 19 themes, 210 subthemes, and 13 person IDs to the 58,291 confirmed records. The multi-label tagging is deterministic and auditable, but it is not expert attribution of every object. Records without a reliable thematic rule remain `unclassified` rather than being forced into an arbitrary category.

| Output | Meaning |
| --- | --- |
| `records.parquet` | All source fields plus zone, theme, subtheme, person, status, and versioning metadata |
| `assignments.parquet` | One row per record/subtheme assignment with confidence, rules, fields, and matched forms |
| `taxonomy.json` | Five zones, theme hierarchy, and person registry for website import |
| `report.json` | Input hashes, counts, theme and person distributions, and rule statistics |
| `audit_sample.csv` | Deterministic per-theme and unclassified samples for editorial review |

Run the tagger:

```bash
python3 scripts/tag_armeniana.py \
  --input output/goskatalog/armenia_records.parquet \
  --output-dir output/armeniana
```

See the [tagging methodology and data dictionary](docs/armeniana_tagging.md) and the [technical specification for the Armeniana web portal](docs/armeniana_website_spec.md). The 86,714 ambiguous Goskatalog candidates are not included in the website's initial confirmed dataset.

## Run the extractor

Python 3.9 or later is required.

```bash
python3 -m pip install -r requirements.txt
python3 scripts/extract_goskatalog_armenia.py \
  --input /path/to/goskatalog/data.parquet \
  --output-dir output/goskatalog_new \
  --threads 4 \
  --memory-limit 4GB
```

The source export is not included. The extractor expects the Goskatalog Parquet schema with fields including `id`, `name`, `description`, `authors`, `productionPlace`, `findPlace`, `mainWords`, `provenance`, `typologyDesc`, `technologies`, `fund`, `museum`, and `typology`.

For a diagnostic run, append `--limit 100000`. The limit is applied before candidate filtering and must not be used for a final export.

To reclassify a previous complete result and scan the source only for new candidates:

```bash
python3 scripts/extract_goskatalog_armenia.py \
  --input /path/to/goskatalog/data.parquet \
  --resume-from output/goskatalog_v1 \
  --output-dir output/goskatalog_new \
  --threads 4 \
  --memory-limit 4GB
```

The resume directory must contain complete `armenia_records.parquet` and `armenia_review.parquet` files. `--limit` cannot be combined with `--resume-from`.

## Download Goskatalog images

Download every URL in the `images` column, including all images belonging to the same record:

```bash
python3 scripts/download_goskatalog_images.py \
  --input output/goskatalog/armenia_records.parquet \
  --output-dir output/goskatalog_images
```

Files are grouped by record ID. `image_manifest.jsonl` records each record/image association, source URL, local path, size, and SHA-256; `image_download_report.json` summarizes inventory, downloaded bytes, and failures. Completed files are verified and skipped on subsequent runs. The command exits nonzero if any files remain unavailable.

For a bounded first iteration with current image IDs from the exhibits API, prepare a sample and then download it:

```bash
python3 scripts/prepare_goskatalog_image_sample.py \
  --input output/goskatalog/armenia_records.parquet \
  --output-dir output/goskatalog_images_iteration1 \
  --max-images 6634

python3 scripts/download_goskatalog_images.py \
  --input output/goskatalog_images_iteration1/image_sample.parquet \
  --output-dir output/goskatalog_images_iteration1
```

The preparer shuffles records deterministically, keeps every available current image of each selected record, and never exceeds `--max-images`. Images marked deleted or assigned the API's error status 3 are excluded. It writes full API responses to `api_records.jsonl`, the selected Parquet to `image_sample.parquet`, and selection counts to `image_sample_report.json`. Cached API responses and completed downloads are reused on rerun. Records for which the API returns an error are reported rather than treated as confirmed deletions.

Goskatalog does not provide usable file sizes through `HEAD` and does not honor byte-range requests for these resources. To estimate the total from a deterministic random sample without saving images:

```bash
python3 scripts/download_goskatalog_images.py \
  --input output/goskatalog/armenia_records.parquet \
  --output-dir output/goskatalog \
  --estimate-only \
  --sample-size 200
```

The estimator measures complete responses in memory, counts unavailable links as zero downloadable bytes, and writes `image_estimate.json` with an approximate 95% confidence interval. The exact total is known only after a complete download. Check the source and museum terms before redistributing downloaded images; the repository's MIT license does not grant rights to them.

## Europeana and NEB

Two additional importers collect Armenia-related records from [Europeana](https://www.europeana.eu/) and the [National Electronic Library (NEB)](https://rusneb.ru/). They share a normalized Parquet schema, preserve source metadata, apply the same term registry, cache responses for resumable runs, and separate confirmed records from query-only or contextual review candidates.

```bash
export EUROPEANA_API_KEY='your-key'
python3 scripts/extract_europeana_armenia.py \
  --output-dir output/europeana \
  --max-records 100

python3 scripts/extract_neb_armenia.py \
  --output-dir output/neb \
  --max-records-per-query 15 \
  --access open
```

Use `--proxy http://127.0.0.1:7070` for Europeana when the direct route is unavailable. NEB requires a direct Russian route or an explicitly configured Russian proxy.

The shared asset downloader writes resumable manifests and SHA-256 hashes. Europeana downloads are limited to open rights statements by default. NEB requires an explicit `--max-files` bound for every download run: its user agreement prohibits mass automated downloading of NEB objects.

```bash
python3 scripts/download_source_assets.py \
  --input output/europeana/armenia_records.parquet \
  --output-dir output/europeana_files \
  --source europeana \
  --max-files 100
```

See the [Europeana and NEB methodology, commands, schema, rights, and pilot results](docs/europeana_neb.md). The pilots contain three full records from each source, one downloaded Europeana JPEG, and one downloaded open NEB PDF; an unavailable Europeana provider URL is retained in the error report.

## Matching and term registry

The local `data/terms.csv` is the exact registry snapshot used for the current published extraction; its SHA-256 is recorded in `output/goskatalog/report.json`. The registry format is documented in [`docs/terms.md`](docs/terms.md), with a machine-readable schema in [`schema/terms.schema.json`](schema/terms.schema.json).

The multilingual registry originates in [opendataam/armenian-keywords](https://github.com/opendataam/armenian-keywords). This repository includes the matcher and registry snapshot so that extraction and testing work independently.

Matching uses Unicode normalization, word boundaries, curated morphology, field-specific evidence, and negative contexts:

- strong evidence in content fields produces `include`;
- context-only evidence produces `review` unless stronger evidence exists;
- a match only in `museum.name` never produces automatic inclusion;
- standalone given names, patronymics, and surnames are weak supporting evidence;
- ambiguous terms can be suppressed by their own negative-context rules.

## Evaluation

```bash
python3 scripts/evaluate_goskatalog.py \
  --input /path/to/goskatalog/data.parquet \
  --labels evaluation/goskatalog_labels.csv \
  --output output/goskatalog_new/evaluation.json
```

Labels use `id,label,note`, where `label` is `relevant`, `nonrelevant`, or `review`. The included evaluation report covers 93 manually reviewed records and must not be generalized to the entire source dataset.

## Validation

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/terms.py data/terms.csv
python3 -m pytest -q
```

The tests cover registry validation, matching behavior, false substrings, negative contexts, and end-to-end extraction, resume, and evaluation through the real command-line interfaces.

## Provenance and license

The source is a read-only local Parquet export of the Museum Fund of the Russian Federation. The 2,858,122,786-byte, 31,741,256-record source file is not redistributed here. Generated reports retain the original processing paths and timestamps as audit metadata.

Code and original documentation are available under the [MIT License](LICENSE). Museum metadata and derived records may be subject to third-party terms; the MIT license does not grant additional rights to Goskatalog source data.
