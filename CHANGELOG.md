# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Resumable Goskatalog image downloader with per-record manifests, `Content-Length` checks, signature-based file extensions, optional SHA-256 verification on resume, cancellation of queued downloads on interrupt, and sample-based volume estimates covering multiple images and unavailable links.
- Deterministic, API-refreshed image sampling with a hard file cap, full API-response caching with refetching of throttled or failed responses, and support for bounded first-iteration downloads.
- Europeana Search/Record API and NEB catalog importers with a shared normalized Parquet schema, response caching, the shared term registry, and `source_query_only` review candidates.
- Shared Europeana/NEB asset downloader with resumable manifests, an open-rights allowlist for Europeana, and a mandatory per-run `--max-files` bound for NEB.
- Armeniana taxonomy with 5 zones, 19 themes, 210 subthemes, and 13 initial person IDs.
- Deterministic field-aware thematic tagger with multi-label Parquet outputs, assignment evidence, person IDs confirmed by strong name forms, separate counts for content-based and typology- or museum-only tagging, taxonomy export, summary reports, and editorial audit samples.
- End-to-end tests for thematic assignments, unclassified records, person confirmation, false substrings, confirmed-only input, the Europeana and NEB importers, rights filtering, and truncated downloads.
- Tagging methodology, Europeana/NEB methodology, and technical specification for the Armeniana web portal.
- `.gitignore` rules that keep downloaded images, files, and HTTP caches out of Git.

## [1.0.0] - 2026-10-31

### Added

- Initial standalone repository, separated from `opendataam/armenian-keywords`.
- Streaming DuckDB/PyArrow extractor for Armenia-related Goskatalog records, including field-aware decisions, match metadata, deterministic audit samples, and resumable reclassification.
- Field-aware matcher and the 10,296-row multilingual term-registry snapshot used for the published result.
- Current full-corpus outputs with 58,291 included and 86,714 review records, plus the archived first complete result with 50,548 included and 75,968 review records.
- Evaluation tooling, 93 manually labeled records, sample-scoped evaluation reports, and end-to-end tests.
- Registry documentation, JSON Schema, dependency manifests, and MIT license.
