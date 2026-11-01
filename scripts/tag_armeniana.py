#!/usr/bin/env python3
import argparse
import csv
import hashlib
import heapq
import json
import re
import sys
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

from matcher import flatten
from terms import normalize_text, read_terms

ROOT = Path(__file__).resolve().parent.parent
TAGGING_VERSION = "1.0.0"
THEME_FIELDS = ["zone_id", "zone_name_ru", "theme_id", "theme_name_ru", "europeana_theme"]
SUBTHEME_FIELDS = ["theme_id", "subtheme_id", "subtheme_name_ru"]
PERSON_FIELDS = ["person_id", "name_ru", "name_en", "primary_theme_id"]
RULE_FIELDS = ["rule_id", "theme_id", "subtheme_id", "fields", "pattern", "negative_pattern", "confidence"]
TEXT_FIELDS = (
    "name",
    "description",
    "authors",
    "productionPlace",
    "findPlace",
    "mainWords",
    "provenance",
    "typologyDesc",
    "technologies",
    "fund",
    "periodStr",
    "typology.name",
)
FIELD_NAMES = TEXT_FIELDS + ("museum.name", "armenia_matched_entities")
# Rules limited to these fields describe the holding collection or object class, not the subject of the record.
STRUCTURAL_FIELDS = {"typology.name", "museum.name"}
CONFIDENCE_RANK = {"low": 1, "medium": 2, "high": 3}
TAGGING_SCHEMA = pa.schema([
    pa.field("armeniana_zone_ids", pa.list_(pa.string()), nullable=False),
    pa.field("armeniana_theme_ids", pa.list_(pa.string()), nullable=False),
    pa.field("armeniana_subtheme_ids", pa.list_(pa.string()), nullable=False),
    pa.field("armeniana_person_ids", pa.list_(pa.string()), nullable=False),
    pa.field("armeniana_tagging_status", pa.string(), nullable=False),
    pa.field("armeniana_tagging_version", pa.string(), nullable=False),
])
ASSIGNMENT_SCHEMA = pa.schema([
    pa.field("record_id", pa.int64(), nullable=False),
    pa.field("zone_id", pa.string(), nullable=False),
    pa.field("theme_id", pa.string(), nullable=False),
    pa.field("subtheme_id", pa.string(), nullable=False),
    pa.field("confidence", pa.string(), nullable=False),
    pa.field("rule_ids", pa.list_(pa.string()), nullable=False),
    pa.field("matched_fields", pa.list_(pa.string()), nullable=False),
    pa.field("matched_forms", pa.list_(pa.string()), nullable=False),
    pa.field("tagging_version", pa.string(), nullable=False),
])
AUDIT_FIELDS = [
    "sample_group",
    "id",
    "name",
    "status",
    "theme_ids",
    "subtheme_ids",
    "person_ids",
    "evidence",
]


@dataclass(frozen=True)
class Theme:
    zone_id: str
    zone_name_ru: str
    theme_id: str
    theme_name_ru: str
    europeana_theme: str


@dataclass(frozen=True)
class Subtheme:
    theme_id: str
    subtheme_id: str
    subtheme_name_ru: str


@dataclass(frozen=True)
class Person:
    person_id: str
    name_ru: str
    name_en: str
    primary_theme_id: str


@dataclass(frozen=True)
class Rule:
    rule_id: str
    theme_id: str
    subtheme_id: str
    fields: tuple
    pattern: str
    negative_pattern: str
    confidence: str
    regex: re.Pattern
    negative_regex: re.Pattern


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path, fieldnames):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != fieldnames:
            raise ValueError("{} must have columns {}".format(path, ",".join(fieldnames)))
        return [{name: (row.get(name) or "").strip() for name in fieldnames} for row in reader]


def expand_fields(value):
    names = []
    for item in value.split("|"):
        if item == "text":
            names.extend(TEXT_FIELDS)
        elif item == "all":
            names.extend(FIELD_NAMES)
        elif item in FIELD_NAMES:
            names.append(item)
        else:
            raise ValueError("Unknown tagging field: {}".format(item))
    return tuple(dict.fromkeys(names))


def compile_rule_pattern(pattern):
    normalized = normalize_text(pattern)
    compiled = re.compile(r"(?<!\w)(?:{})(?!\w)".format(normalized))
    if compiled.groups:
        raise ValueError("Tagging regex must use non-capturing groups only: {}".format(pattern))
    return compiled


def load_taxonomy(themes_path, subthemes_path, persons_path, rules_path):
    themes = [Theme(**row) for row in read_rows(themes_path, THEME_FIELDS)]
    subthemes = [Subtheme(**row) for row in read_rows(subthemes_path, SUBTHEME_FIELDS)]
    persons = [Person(**row) for row in read_rows(persons_path, PERSON_FIELDS)]
    theme_map = {theme.theme_id: theme for theme in themes}
    subtheme_map = {subtheme.subtheme_id: subtheme for subtheme in subthemes}
    if len(theme_map) != len(themes) or not themes:
        raise ValueError("Theme IDs must be non-empty and unique")
    if len(subtheme_map) != len(subthemes):
        raise ValueError("Subtheme IDs must be unique")
    zone_names = {}
    for theme in themes:
        if not all((theme.zone_id, theme.zone_name_ru, theme.theme_id, theme.theme_name_ru)):
            raise ValueError("Themes must have zone and display names")
        if zone_names.setdefault(theme.zone_id, theme.zone_name_ru) != theme.zone_name_ru:
            raise ValueError("Zone names must be consistent: {}".format(theme.zone_id))
    for subtheme in subthemes:
        if subtheme.theme_id not in theme_map:
            raise ValueError("Unknown theme for subtheme: {}".format(subtheme.subtheme_id))
        if not subtheme.subtheme_id.startswith(subtheme.theme_id + "."):
            raise ValueError("Subtheme ID must start with its theme ID: {}".format(subtheme.subtheme_id))
    person_map = {person.person_id: person for person in persons}
    if len(person_map) != len(persons):
        raise ValueError("Person IDs must be unique")
    for person in persons:
        if person.primary_theme_id not in theme_map:
            raise ValueError("Unknown primary theme for person: {}".format(person.person_id))
    rules = []
    rule_ids = set()
    for row in read_rows(rules_path, RULE_FIELDS):
        if row["rule_id"] in rule_ids:
            raise ValueError("Duplicate tagging rule ID: {}".format(row["rule_id"]))
        rule_ids.add(row["rule_id"])
        if row["theme_id"] not in theme_map:
            raise ValueError("Unknown theme in rule: {}".format(row["rule_id"]))
        if row["subtheme_id"] and row["subtheme_id"] not in subtheme_map:
            raise ValueError("Unknown subtheme in rule: {}".format(row["rule_id"]))
        if row["subtheme_id"] and subtheme_map[row["subtheme_id"]].theme_id != row["theme_id"]:
            raise ValueError("Rule theme and subtheme disagree: {}".format(row["rule_id"]))
        if row["confidence"] not in CONFIDENCE_RANK:
            raise ValueError("Invalid confidence in rule: {}".format(row["rule_id"]))
        if not row["pattern"]:
            raise ValueError("Empty pattern in rule: {}".format(row["rule_id"]))
        negative = compile_rule_pattern(row["negative_pattern"]) if row["negative_pattern"] else None
        rules.append(Rule(
            rule_id=row["rule_id"],
            theme_id=row["theme_id"],
            subtheme_id=row["subtheme_id"],
            fields=expand_fields(row["fields"]),
            pattern=row["pattern"],
            negative_pattern=row["negative_pattern"],
            confidence=row["confidence"],
            regex=compile_rule_pattern(row["pattern"]),
            negative_regex=negative,
        ))
    if not rules:
        raise ValueError("Tagging rules must not be empty")
    return themes, subthemes, persons, rules


def display_path(path):
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def strong_person_terms(terms):
    strong = {}
    for term in terms:
        if term.category == "person":
            strong.setdefault(term.entity_id, set())
            if term.match_strength == "strong":
                strong[term.entity_id].add("{}:{}".format(term.lang, term.value))
    return strong


def record_fields(record, entities):
    values = {}
    for name in TEXT_FIELDS:
        if "." in name:
            value = record.get(name.split(".")[0])
            value = value.get(name.split(".")[1]) if isinstance(value, dict) else None
        else:
            value = record.get(name)
        values[name] = normalize_text(flatten(value))
    museum = record.get("museum")
    values["museum.name"] = normalize_text(flatten(museum.get("name") if isinstance(museum, dict) else None))
    values["armenia_matched_entities"] = normalize_text(flatten(entities))
    return values


class ThemeTagger:
    def __init__(self, themes, persons, rules, terms):
        self.themes = {theme.theme_id: theme for theme in themes}
        self.person_ids = {person.person_id for person in persons}
        self.rules = rules
        self.person_terms = strong_person_terms(terms)
        self.structural_rule_ids = {rule.rule_id for rule in rules if set(rule.fields) <= STRUCTURAL_FIELDS}

    def confirmed_entities(self, record):
        # A person entity counts only when a strong form matched; a bare surname such as
        # "хачатурян" is context-only evidence and may refer to another person.
        matched_terms = set(record.get("armenia_matched_terms") or [])
        return [
            entity for entity in record.get("armenia_matched_entities") or []
            if entity not in self.person_terms or self.person_terms[entity] & matched_terms
        ]

    def tag(self, record):
        entities = self.confirmed_entities(record)
        fields = record_fields(record, entities)
        assignments = {}
        for rule in self.rules:
            selected = " | ".join(fields[name] for name in rule.fields if fields[name])
            if not selected:
                continue
            if rule.negative_regex and rule.negative_regex.search(selected):
                continue
            forms = sorted({match.group(0) for match in rule.regex.finditer(selected)})
            if not forms:
                continue
            matched_fields = sorted(
                name for name in rule.fields
                if fields[name] and any(form in fields[name] for form in forms)
            )
            key = (rule.theme_id, rule.subtheme_id)
            current = assignments.setdefault(key, {
                "confidence": rule.confidence,
                "rule_ids": set(),
                "matched_fields": set(),
                "matched_forms": set(),
            })
            if CONFIDENCE_RANK[rule.confidence] > CONFIDENCE_RANK[current["confidence"]]:
                current["confidence"] = rule.confidence
            current["rule_ids"].add(rule.rule_id)
            current["matched_fields"].update(matched_fields)
            current["matched_forms"].update(forms)
        person_ids = sorted(self.person_ids.intersection(entities))
        theme_ids = sorted({theme_id for theme_id, _ in assignments})
        zone_ids = sorted({self.themes[theme_id].zone_id for theme_id in theme_ids})
        subtheme_ids = sorted({subtheme_id for _, subtheme_id in assignments if subtheme_id})
        metadata = {
            "armeniana_zone_ids": zone_ids,
            "armeniana_theme_ids": theme_ids,
            "armeniana_subtheme_ids": subtheme_ids,
            "armeniana_person_ids": person_ids,
            "armeniana_tagging_status": "tagged" if assignments else "unclassified",
            "armeniana_tagging_version": TAGGING_VERSION,
        }
        rows = []
        for (theme_id, subtheme_id), match in sorted(assignments.items()):
            rows.append({
                "record_id": record["id"],
                "zone_id": self.themes[theme_id].zone_id,
                "theme_id": theme_id,
                "subtheme_id": subtheme_id,
                "confidence": match["confidence"],
                "rule_ids": sorted(match["rule_ids"]),
                "matched_fields": sorted(match["matched_fields"]),
                "matched_forms": sorted(match["matched_forms"]),
                "tagging_version": TAGGING_VERSION,
            })
        return metadata, rows


class AuditSamples:
    def __init__(self, per_theme=10, unclassified=50):
        self.limit = per_theme
        self.unclassified_limit = unclassified
        self.heaps = {}

    def add(self, record, metadata, assignments):
        groups = metadata["armeniana_theme_ids"] or ["unclassified"]
        payload = {
            "sample_group": "",
            "id": record["id"],
            "name": record.get("name"),
            "status": metadata["armeniana_tagging_status"],
            "theme_ids": json.dumps(metadata["armeniana_theme_ids"], ensure_ascii=False),
            "subtheme_ids": json.dumps(metadata["armeniana_subtheme_ids"], ensure_ascii=False),
            "person_ids": json.dumps(metadata["armeniana_person_ids"], ensure_ascii=False),
            "evidence": json.dumps([
                "{}:{}:{}".format(row["theme_id"], row["subtheme_id"], "|".join(row["rule_ids"]))
                for row in assignments
            ], ensure_ascii=False),
        }
        for group in groups:
            limit = self.unclassified_limit if group == "unclassified" else self.limit
            digest = int(hashlib.sha256("{}:{}".format(record["id"], group).encode("ascii")).hexdigest()[:16], 16)
            heap = self.heaps.setdefault(group, [])
            item = (-digest, record["id"], group, payload)
            if len(heap) < limit:
                heapq.heappush(heap, item)
            elif digest < -heap[0][0]:
                heapq.heapreplace(heap, item)

    def write(self, path):
        rows = []
        for group, heap in self.heaps.items():
            for _, _, _, payload in heap:
                row = dict(payload)
                row["sample_group"] = group
                rows.append(row)
        rows.sort(key=lambda row: (row["sample_group"], row["id"]))
        temporary = path.with_suffix(path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=AUDIT_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)


def taxonomy_payload(themes, subthemes, persons):
    zones = {}
    for theme in themes:
        zone = zones.setdefault(theme.zone_id, {"id": theme.zone_id, "name_ru": theme.zone_name_ru, "themes": []})
        zone["themes"].append({
            "id": theme.theme_id,
            "name_ru": theme.theme_name_ru,
            "europeana_theme": theme.europeana_theme or None,
            "subthemes": [
                {"id": subtheme.subtheme_id, "name_ru": subtheme.subtheme_name_ru}
                for subtheme in subthemes if subtheme.theme_id == theme.theme_id
            ],
        })
    return {
        "version": TAGGING_VERSION,
        "zones": list(zones.values()),
        "persons": [
            {
                "id": person.person_id,
                "name_ru": person.name_ru,
                "name_en": person.name_en,
                "primary_theme_id": person.primary_theme_id,
            }
            for person in persons
        ],
    }


def write_json(path, payload):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def tag_records(args):
    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()
    if not input_path.is_file():
        raise ValueError("Input Parquet does not exist: {}".format(input_path))
    output_dir.mkdir(parents=True, exist_ok=True)
    records_path = output_dir / "records.parquet"
    assignments_path = output_dir / "assignments.parquet"
    if input_path in {records_path, assignments_path}:
        raise ValueError("Output files must not overwrite the input")
    paths = {
        "themes": args.themes.resolve(),
        "subthemes": args.subthemes.resolve(),
        "persons": args.persons.resolve(),
        "rules": args.rules.resolve(),
        "terms": args.terms.resolve(),
    }
    themes, subthemes, persons, rules = load_taxonomy(
        paths["themes"], paths["subthemes"], paths["persons"], paths["rules"]
    )
    tagger = ThemeTagger(themes, persons, rules, read_terms(paths["terms"]))
    connection = duckdb.connect()
    columns = {row[0] for row in connection.execute("DESCRIBE SELECT * FROM read_parquet(?)", [str(input_path)]).fetchall()}
    required = {"id", "name", "armenia_decision", "armenia_matched_entities", "armenia_matched_terms"}
    missing = sorted(required - columns)
    if missing:
        raise ValueError("Input is missing required columns: {}".format(", ".join(missing)))
    source_rows = pq.ParquetFile(str(input_path)).metadata.num_rows
    reader = connection.execute("SELECT * FROM read_parquet(?)", [str(input_path)]).fetch_record_batch(args.batch_size)
    input_schema = reader.schema
    output_schema = pa.schema(list(input_schema) + list(TAGGING_SCHEMA))
    records_tmp = records_path.with_suffix(".parquet.tmp")
    assignments_tmp = assignments_path.with_suffix(".parquet.tmp")
    records_writer = pq.ParquetWriter(str(records_tmp), output_schema, compression="zstd")
    assignments_writer = pq.ParquetWriter(str(assignments_tmp), ASSIGNMENT_SCHEMA, compression="zstd")
    counts = Counter()
    theme_counts = Counter()
    zone_counts = Counter()
    subtheme_counts = Counter()
    person_counts = Counter()
    rule_counts = Counter()
    samples = AuditSamples(args.audit_per_theme, args.audit_unclassified)
    seen_ids = set()
    started = time.monotonic()
    started_at = utc_now()
    print("Source: {} ({:,} rows)".format(input_path, source_rows), flush=True)
    print("Themes: {}; subthemes: {}; rules: {}".format(len(themes), len(subthemes), len(rules)), flush=True)
    try:
        for batch in reader:
            metadata_rows = []
            assignment_rows = []
            for record in batch.to_pylist():
                record_id = record.get("id")
                if record_id in seen_ids:
                    raise ValueError("Duplicate source id: {}".format(record_id))
                seen_ids.add(record_id)
                if record.get("armenia_decision") != "include":
                    raise ValueError("Only confirmed include records may be tagged; id={}".format(record_id))
                metadata, assignments = tagger.tag(record)
                metadata_rows.append(metadata)
                assignment_rows.extend(assignments)
                counts["source_rows"] += 1
                counts["assignments"] += len(assignments)
                counts[metadata["armeniana_tagging_status"]] += 1
                if len(metadata["armeniana_theme_ids"]) > 1:
                    counts["multi_theme_records"] += 1
                if metadata["armeniana_person_ids"]:
                    counts["records_with_persons"] += 1
                if assignments:
                    if any(set(row["rule_ids"]) - tagger.structural_rule_ids for row in assignments):
                        counts["content_tagged"] += 1
                    else:
                        counts["structural_only"] += 1
                theme_counts.update(metadata["armeniana_theme_ids"])
                zone_counts.update(metadata["armeniana_zone_ids"])
                subtheme_counts.update(metadata["armeniana_subtheme_ids"])
                person_counts.update(metadata["armeniana_person_ids"])
                for row in assignments:
                    rule_counts.update(row["rule_ids"])
                samples.add(record, metadata, assignments)
            selected = batch
            for field in TAGGING_SCHEMA:
                values = [row[field.name] for row in metadata_rows]
                selected = selected.append_column(field, pa.array(values, type=field.type))
            records_writer.write_batch(selected)
            if assignment_rows:
                assignments_writer.write_table(pa.Table.from_pylist(assignment_rows, schema=ASSIGNMENT_SCHEMA))
    except Exception:
        records_writer.close()
        assignments_writer.close()
        records_tmp.unlink(missing_ok=True)
        assignments_tmp.unlink(missing_ok=True)
        raise
    records_writer.close()
    assignments_writer.close()
    if pq.ParquetFile(str(records_tmp)).metadata.num_rows != counts["source_rows"]:
        raise ValueError("Tagged output row count verification failed")
    if pq.ParquetFile(str(assignments_tmp)).metadata.num_rows != counts["assignments"]:
        raise ValueError("Assignment output row count verification failed")
    records_tmp.replace(records_path)
    assignments_tmp.replace(assignments_path)
    audit_path = output_dir / "audit_sample.csv"
    samples.write(audit_path)
    taxonomy_path = output_dir / "taxonomy.json"
    write_json(taxonomy_path, taxonomy_payload(themes, subthemes, persons))
    report = {
        "started_at": started_at,
        "finished_at": utc_now(),
        "duration_seconds": round(time.monotonic() - started, 3),
        "tagging_version": TAGGING_VERSION,
        "method": "deterministic_field_aware_rules",
        "input": {"path": display_path(input_path), "rows": source_rows, "sha256": sha256(input_path)},
        "taxonomy": {
            name: {"path": display_path(path), "sha256": sha256(path)}
            for name, path in sorted(paths.items())
        },
        "settings": {
            "batch_size": args.batch_size,
            "audit_per_theme": args.audit_per_theme,
            "audit_unclassified": args.audit_unclassified,
        },
        "counts": {
            "source_rows": counts["source_rows"],
            "tagged": counts["tagged"],
            "content_tagged": counts["content_tagged"],
            "structural_only": counts["structural_only"],
            "unclassified": counts["unclassified"],
            "multi_theme_records": counts["multi_theme_records"],
            "records_with_persons": counts["records_with_persons"],
            "assignments": counts["assignments"],
        },
        "zones": dict(zone_counts.most_common()),
        "themes": dict(theme_counts.most_common()),
        "subthemes": dict(subtheme_counts.most_common()),
        "persons": dict(person_counts.most_common()),
        "rules": dict(rule_counts.most_common()),
        "structural_rules": sorted(tagger.structural_rule_ids),
        "outputs": {
            "records": {"path": display_path(records_path), "rows": counts["source_rows"], "bytes": records_path.stat().st_size},
            "assignments": {"path": display_path(assignments_path), "rows": counts["assignments"], "bytes": assignments_path.stat().st_size},
            "taxonomy": display_path(taxonomy_path),
            "audit_sample": display_path(audit_path),
        },
    }
    report_path = output_dir / "report.json"
    write_json(report_path, report)
    print("Done in {:.1f}s: {:,} tagged ({:,} by content, {:,} by typology or museum only); {:,} unclassified; {:,} assignments".format(
        report["duration_seconds"], counts["tagged"], counts["content_tagged"], counts["structural_only"],
        counts["unclassified"], counts["assignments"]
    ))
    print("Records:", records_path)
    print("Assignments:", assignments_path)
    print("Report:", report_path)
    return report


def parse_args():
    parser = argparse.ArgumentParser(description="Apply Armeniana themes and person IDs to confirmed heritage records")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--themes", type=Path, default=ROOT / "data" / "armeniana_themes.csv")
    parser.add_argument("--subthemes", type=Path, default=ROOT / "data" / "armeniana_subthemes.csv")
    parser.add_argument("--persons", type=Path, default=ROOT / "data" / "armeniana_persons.csv")
    parser.add_argument("--rules", type=Path, default=ROOT / "data" / "armeniana_tagging_rules.csv")
    parser.add_argument("--terms", type=Path, default=ROOT / "data" / "terms.csv", help="Registry used to confirm person IDs by strong forms")
    parser.add_argument("--batch-size", type=int, default=2048)
    parser.add_argument("--audit-per-theme", type=int, default=30)
    parser.add_argument("--audit-unclassified", type=int, default=50)
    args = parser.parse_args()
    if args.batch_size < 1 or args.audit_per_theme < 1 or args.audit_unclassified < 1:
        parser.error("batch-size and audit sample sizes must be positive")
    return args


def main():
    try:
        tag_records(parse_args())
    except (OSError, ValueError, duckdb.Error, pa.ArrowException) as exc:
        print("Error: {}".format(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
