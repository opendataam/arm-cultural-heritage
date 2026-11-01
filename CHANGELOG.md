# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Draft technical specification (in Russian) for a multilingual Armenian cultural heritage portal modelled on Europeana: [`docs/tz-heritage-portal.md`](docs/tz-heritage-portal.md). Version 0.2 adopts a component-based architecture around a custom core and adds pipeline orchestration requirements.
- Portal MVP built on the included Goskatalog records: an aggregation pipeline with immutable snapshots, date normalization to EDTF, entity links from the term registry and a volume check that blocks publication; SQLite full-text search with Armenian, Russian and English stemming, facets and cross-language entity expansion; a server-rendered site in Armenian, Russian, English, French and Spanish; a REST API with EDM and schema.org JSON-LD, IIIF Presentation 3.0 manifests and bulk dumps; and Dagster definitions over the pipeline. See [`docs/mvp.md`](docs/mvp.md).

## [1.0.0] - 2026-10-31

### Added

- Initial standalone repository, separated from `opendataam/armenian-keywords`.
- Streaming DuckDB/PyArrow extractor for Armenia-related Goskatalog records, including field-aware decisions, match metadata, deterministic audit samples, and resumable reclassification.
- Field-aware matcher and the 10,296-row multilingual term-registry snapshot used for the published result.
- Current full-corpus outputs with 58,291 included and 86,714 review records, plus the archived first complete result with 50,548 included and 75,968 review records.
- Evaluation tooling, 93 manually labeled records, sample-scoped evaluation reports, and end-to-end tests.
- Registry documentation, JSON Schema, dependency manifests, and MIT license.
