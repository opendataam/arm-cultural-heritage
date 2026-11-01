# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Resumable Goskatalog image downloader with per-record manifests and sample-based volume estimates covering multiple images and unavailable links.
- Deterministic, API-refreshed image sampling with a hard file cap, full API-response caching, and support for bounded first-iteration downloads.
- Armeniana taxonomy with 5 zones, 19 themes, 210 subthemes, and 13 initial person IDs.
- Deterministic field-aware thematic tagger with multi-label Parquet outputs, assignment evidence, taxonomy export, summary reports, and editorial audit samples.
- End-to-end tests for thematic assignments, unclassified records, person IDs, false substrings, and confirmed-only input.
- Tagging methodology and technical specification for the Armeniana web portal.

## [1.0.0] - 2026-10-31

### Added

- Initial standalone repository, separated from `opendataam/armenian-keywords`.
- Streaming DuckDB/PyArrow extractor for Armenia-related Goskatalog records, including field-aware decisions, match metadata, deterministic audit samples, and resumable reclassification.
- Field-aware matcher and the 10,296-row multilingual term-registry snapshot used for the published result.
- Current full-corpus outputs with 58,291 included and 86,714 review records, plus the archived first complete result with 50,548 included and 75,968 review records.
- Evaluation tooling, 93 manually labeled records, sample-scoped evaluation reports, and end-to-end tests.
- Registry documentation, JSON Schema, dependency manifests, and MIT license.
