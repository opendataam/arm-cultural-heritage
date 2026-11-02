#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable, List, Sequence

FIELDNAMES = [
    "id",
    "name",
    "name_local",
    "url",
    "country",
    "institution_type",
    "scope",
    "integration",
    "content_types",
    "languages",
    "est_armenian_items",
    "count_note",
    "access_methods",
    "endpoint",
    "auth",
    "metadata_format",
    "metadata_license",
    "content_rights",
    "commercial_use",
    "attribution_required",
    "automated_access",
    "terms_url",
    "terms_summary",
    "priority",
    "status",
    "verified_at",
    "notes",
]
INSTITUTION_TYPES = {
    "aggregator",
    "archive",
    "authority",
    "digital_library",
    "foundation",
    "library",
    "media",
    "museum",
    "portal",
    "registry",
    "religious",
    "research_institute",
}
SCOPES = {"dedicated", "mixed", "reference"}
INTEGRATIONS = {"harvest", "filter", "link", "none"}
CONTENT_TYPES = {
    "archives",
    "articles",
    "artworks",
    "audio",
    "authority",
    "books",
    "ephemera",
    "manuscripts",
    "maps",
    "monuments",
    "objects",
    "oral_history",
    "periodicals",
    "photographs",
    "texts",
    "video",
}
ACCESS_METHODS = {"api", "bulk", "iiif", "none", "oai-pmh", "sparql", "sru", "web", "z39.50"}
AUTH_TYPES = {"none", "key", "registration", "restricted"}
METADATA_FORMATS = {
    "csv",
    "dc",
    "ead",
    "edm",
    "html",
    "iiif",
    "json",
    "lido",
    "marc",
    "mets",
    "mods",
    "other",
    "qdc",
    "rdf",
}
METADATA_LICENSES = {
    "CC0-1.0",
    "CC-BY-3.0",
    "CC-BY-4.0",
    "CC-BY-SA-3.0",
    "CC-BY-SA-4.0",
    "CC-BY-NC-4.0",
    "CC-BY-NC-SA-4.0",
    "CC-BY-NC-ND-4.0",
    "ODbL-1.0",
    "ODC-By-1.0",
    "PDDL-1.0",
    "etalab-2.0",
    "public-domain",
    "custom",
    "all-rights-reserved",
    "unknown",
}
CONTENT_RIGHTS = {"public-domain", "open", "mixed", "restricted", "all-rights-reserved", "unknown"}
TRISTATE = {"yes", "no", "conditional", "unknown"}
ATTRIBUTION = {"yes", "no", "unknown"}
AUTOMATED_ACCESS = {"allowed", "api-only", "restricted", "prohibited", "unknown"}
PRIORITIES = {"1", "2", "3", "4"}
STATUSES = {"integrated", "planned", "candidate", "blocked", "not-applicable"}
LIST_FIELDS = {
    "content_types": CONTENT_TYPES,
    "access_methods": ACCESS_METHODS,
    "metadata_format": METADATA_FORMATS,
}
ENUM_FIELDS = {
    "institution_type": INSTITUTION_TYPES,
    "scope": SCOPES,
    "integration": INTEGRATIONS,
    "auth": AUTH_TYPES,
    "metadata_license": METADATA_LICENSES,
    "content_rights": CONTENT_RIGHTS,
    "commercial_use": TRISTATE,
    "attribution_required": ATTRIBUTION,
    "automated_access": AUTOMATED_ACCESS,
    "priority": PRIORITIES,
    "status": STATUSES,
}
REQUIRED_FIELDS = (
    "id",
    "name",
    "url",
    "country",
    "institution_type",
    "scope",
    "integration",
    "content_types",
    "languages",
    "access_methods",
    "auth",
    "metadata_format",
    "metadata_license",
    "content_rights",
    "commercial_use",
    "attribution_required",
    "automated_access",
    "terms_summary",
    "priority",
    "status",
    "verified_at",
)
ID_RE = re.compile(r"[a-z]{2,3}\.[a-z0-9][a-z0-9-]*")
COUNTRY_RE = re.compile(r"[A-Z]{2}")
LANG_RE = re.compile(r"[a-z]{2,3}")
URL_RE = re.compile(r"https?://\S+")


def split_list(value):
    return [item for item in (part.strip() for part in value.split(";")) if item]


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    name_local: str
    url: str
    country: str
    institution_type: str
    scope: str
    integration: str
    content_types: str
    languages: str
    est_armenian_items: str
    count_note: str
    access_methods: str
    endpoint: str
    auth: str
    metadata_format: str
    metadata_license: str
    content_rights: str
    commercial_use: str
    attribution_required: str
    automated_access: str
    terms_url: str
    terms_summary: str
    priority: str
    status: str
    verified_at: str
    notes: str

    @classmethod
    def from_row(cls, row):
        return cls(**{name: (row.get(name) or "").strip() for name in FIELDNAMES})

    def as_row(self):
        return {name: getattr(self, name) for name in FIELDNAMES}

    @property
    def harvestable(self):
        return self.integration in {"harvest", "filter"}


def validate_sources(sources: Sequence[Source]):
    errors = []
    ids = Counter(source.id for source in sources)
    for index, source in enumerate(sources, 2):
        location = "line {} ({})".format(index, source.id or "<empty>")
        for field in REQUIRED_FIELDS:
            if not getattr(source, field):
                errors.append("{}: missing {}".format(location, field))
        if source.id and not ID_RE.fullmatch(source.id):
            errors.append("{}: invalid id {}".format(location, source.id))
        if source.country and not COUNTRY_RE.fullmatch(source.country):
            errors.append("{}: invalid country {}".format(location, source.country))
        for field, allowed in ENUM_FIELDS.items():
            value = getattr(source, field)
            if value and value not in allowed:
                errors.append("{}: invalid {} {}".format(location, field, value))
        for field, allowed in LIST_FIELDS.items():
            values = split_list(getattr(source, field))
            for value in values:
                if value not in allowed:
                    errors.append("{}: invalid {} {}".format(location, field, value))
            if len(values) != len(set(values)):
                errors.append("{}: duplicate values in {}".format(location, field))
        for value in split_list(source.languages):
            if not LANG_RE.fullmatch(value):
                errors.append("{}: invalid language code {}".format(location, value))
        for field in ("url", "endpoint", "terms_url"):
            value = getattr(source, field)
            if value and not URL_RE.fullmatch(value):
                errors.append("{}: invalid {} {}".format(location, field, value))
        if source.est_armenian_items and not source.est_armenian_items.isdigit():
            errors.append("{}: est_armenian_items must be a non-negative integer".format(location))
        if source.est_armenian_items and not source.count_note:
            errors.append("{}: est_armenian_items requires count_note".format(location))
        if source.verified_at:
            try:
                date.fromisoformat(source.verified_at)
            except ValueError:
                errors.append("{}: invalid verified_at {}".format(location, source.verified_at))
        if source.metadata_license not in {"", "unknown"} and not source.terms_url:
            errors.append("{}: metadata_license {} requires terms_url".format(location, source.metadata_license))
        access = split_list(source.access_methods)
        if "none" in access and len(access) > 1:
            errors.append("{}: access_methods none cannot be combined".format(location))
        if source.harvestable and access == ["none"]:
            errors.append("{}: integration {} requires an access method".format(location, source.integration))
        if source.status == "integrated" and not source.harvestable:
            errors.append("{}: integrated sources must use harvest or filter".format(location))
        if source.integration == "none" and source.status not in {"not-applicable", ""}:
            errors.append("{}: integration none requires status not-applicable".format(location))
    for source_id, count in sorted(ids.items()):
        if source_id and count > 1:
            errors.append("duplicate id: {} ({} rows)".format(source_id, count))
    return errors


def read_sources(path: Path) -> List[Source]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDNAMES:
            raise ValueError("{} must have columns {}".format(path, ",".join(FIELDNAMES)))
        sources = [Source.from_row(row) for row in reader]
    errors = validate_sources(sources)
    if errors:
        raise ValueError("Invalid source registry:\n" + "\n".join(errors[:100]))
    return sources


def write_sources(path: Path, sources: Iterable[Source]):
    sources = sorted(sources, key=lambda source: source.id)
    errors = validate_sources(sources)
    if errors:
        raise ValueError("Invalid source registry:\n" + "\n".join(errors[:100]))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(source.as_row() for source in sources)
    temporary.replace(path)


def registry_stats(sources: Sequence[Source]):
    stats = {"total": len(sources)}
    for field in ("integration", "status", "priority", "metadata_license"):
        for value, count in sorted(Counter(getattr(source, field) for source in sources).items()):
            stats["{}.{}".format(field, value)] = count
    return stats


def main():
    parser = argparse.ArgumentParser(description="Validate the Armenian heritage source registry")
    parser.add_argument("path", nargs="?", type=Path, default=Path("data/sources.csv"))
    args = parser.parse_args()
    try:
        sources = read_sources(args.path)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("{}: valid".format(args.path))
    for key, value in registry_stats(sources).items():
        print("{}: {}".format(key, value))
    return 0


if __name__ == "__main__":
    sys.exit(main())
