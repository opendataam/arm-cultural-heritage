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

## Portal MVP

A prototype of the heritage portal described in the [technical specification](docs/tz-heritage-portal.md) publishes the included Goskatalog records with search, facets, object pages, entity and collection pages, a REST API with EDM JSON-LD and IIIF manifests, and an interface in Armenian, Russian, English, French and Spanish. It needs Python 3.11 or later:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-portal.txt
.venv/bin/python -m portal.pipeline run
.venv/bin/uvicorn portal.web.app:app --port 8000
```

The pipeline writes to `build/portal/`, which is not tracked. Scope, deviations from the recommended stack and known limitations are described (in Russian) in [`docs/mvp.md`](docs/mvp.md).

## Validation

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/terms.py data/terms.csv
python3 -m pytest -q
```

The tests cover registry validation, matching behavior, false substrings, negative contexts, and end-to-end extraction, resume, and evaluation through the real command-line interfaces. They also build a small portal publication from real Goskatalog rows and check the pipeline stages, search, site pages, API and locales.

## Provenance and license

The source is a read-only local Parquet export of the Museum Fund of the Russian Federation. The 2,858,122,786-byte, 31,741,256-record source file is not redistributed here. Generated reports retain the original processing paths and timestamps as audit metadata.

Code and original documentation are available under the [MIT License](LICENSE). Museum metadata and derived records may be subject to third-party terms; the MIT license does not grant additional rights to Goskatalog source data.
