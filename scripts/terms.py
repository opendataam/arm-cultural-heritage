#!/usr/bin/env python3
import argparse
import csv
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

FIELDNAMES = [
    "entity_id",
    "value",
    "lang",
    "script",
    "category",
    "pattern",
    "match_strength",
    "negative_pattern",
    "source",
    "review_status",
]
CATEGORIES = {
    "keyword",
    "geoname",
    "name",
    "surname",
    "midname",
    "person",
    "institution",
    "event",
    "language",
    "religion",
    "object",
    "dynasty",
}
STRENGTHS = {"strong", "context_only", "weak"}
REVIEW_STATUSES = {"approved", "unverified", "rejected"}
SCRIPTS = {"Cyrl", "Latn", "Armn", "Arab", "Other"}
DASHES = str.maketrans({"‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-"})


def normalize_text(value):
    value = unicodedata.normalize("NFKC", value or "").casefold()
    return " ".join(value.translate(DASHES).replace("ё", "е").split())


@dataclass(frozen=True)
class Term:
    entity_id: str
    value: str
    lang: str
    script: str
    category: str
    pattern: str
    match_strength: str
    negative_pattern: str
    source: str
    review_status: str

    @classmethod
    def from_row(cls, row):
        return cls(**{name: (row.get(name) or "").strip() for name in FIELDNAMES})

    def as_row(self):
        return {name: getattr(self, name) for name in FIELDNAMES}

    @property
    def active(self):
        return self.review_status != "rejected" and self.match_strength in {"strong", "context_only"}

    @property
    def matching_pattern(self):
        if self.pattern:
            return normalize_text(self.pattern)
        return re.escape(normalize_text(self.value)).replace(r"\ ", r"\s+")


def validate_terms(terms: Sequence[Term]):
    errors = []
    active_values = Counter()
    for index, term in enumerate(terms, 2):
        location = "line {} ({})".format(index, term.value or "<empty>")
        for field in ("entity_id", "value", "lang", "script", "category", "match_strength", "source", "review_status"):
            if not getattr(term, field):
                errors.append("{}: missing {}".format(location, field))
        if term.category not in CATEGORIES:
            errors.append("{}: invalid category {}".format(location, term.category))
        if term.match_strength not in STRENGTHS:
            errors.append("{}: invalid match_strength {}".format(location, term.match_strength))
        if term.review_status not in REVIEW_STATUSES:
            errors.append("{}: invalid review_status {}".format(location, term.review_status))
        if term.script not in SCRIPTS:
            errors.append("{}: invalid script {}".format(location, term.script))
        if not re.fullmatch(r"[a-z]{2,3}", term.lang):
            errors.append("{}: invalid language code {}".format(location, term.lang))
        if term.review_status == "rejected" and term.match_strength != "weak":
            errors.append("{}: rejected terms must have weak strength".format(location))
        for pattern in (term.pattern, term.negative_pattern):
            if not pattern:
                continue
            try:
                compiled = re.compile(normalize_text(pattern))
            except re.error as exc:
                errors.append("{}: invalid regex {}: {}".format(location, pattern, exc))
                continue
            if compiled.groups:
                errors.append("{}: regex must use non-capturing groups only: {}".format(location, pattern))
        if term.active:
            active_values[(term.lang, term.category, normalize_text(term.value))] += 1
    for (lang, category, value), count in sorted(active_values.items()):
        if count > 1:
            errors.append("duplicate active value: {}/{}/{} ({} rows)".format(lang, category, value, count))
    return errors


def read_terms(path: Path) -> List[Term]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDNAMES:
            raise ValueError("{} must have columns {}".format(path, ",".join(FIELDNAMES)))
        terms = [Term.from_row(row) for row in reader]
    errors = validate_terms(terms)
    if errors:
        raise ValueError("Invalid term registry:\n" + "\n".join(errors[:100]))
    return terms


def write_terms(path: Path, terms: Iterable[Term]):
    terms = list(terms)
    errors = validate_terms(terms)
    if errors:
        raise ValueError("Invalid term registry:\n" + "\n".join(errors[:100]))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(term.as_row() for term in terms)
    temporary.replace(path)


def registry_stats(terms: Sequence[Term]):
    return {
        "total": len(terms),
        "strong": sum(term.match_strength == "strong" and term.review_status != "rejected" for term in terms),
        "context_only": sum(term.match_strength == "context_only" and term.review_status != "rejected" for term in terms),
        "weak": sum(term.match_strength == "weak" and term.review_status != "rejected" for term in terms),
        "rejected": sum(term.review_status == "rejected" for term in terms),
        "unverified": sum(term.review_status == "unverified" for term in terms),
    }


def main():
    parser = argparse.ArgumentParser(description="Validate the Armenian keyword registry")
    parser.add_argument("path", nargs="?", type=Path, default=Path("data/terms.csv"))
    args = parser.parse_args()
    try:
        terms = read_terms(args.path)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("{}: valid".format(args.path))
    for key, value in registry_stats(terms).items():
        print("{}: {}".format(key, value))
    return 0


if __name__ == "__main__":
    sys.exit(main())
