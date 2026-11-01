"""Entity dictionary seeded from the term registry (ТЗ 6.7, item 1)."""

import csv
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from portal.text import fold, title_case, tokens

# Surname, given name and patronymic entries are matching aids, not entities, and
# legacy keywords are word forms of "Armenian"; none of them is shown to users.
DISPLAY_CATEGORIES = {
    "geoname", "person", "keyword", "object", "religion", "event", "dynasty", "language", "institution",
}
KINDS = {"person": "person", "geoname": "place", "institution": "organization"}
LABEL_FALLBACKS = {
    "hy": ("hy", "ru", "en"),
    "ru": ("ru", "en"),
    "en": ("en", "ru"),
    "fr": ("fr", "en", "ru"),
    "es": ("es", "en", "ru"),
}


@dataclass
class Entity:
    id: str
    category: str
    review_status: str
    labels: Dict[str, str] = field(default_factory=dict)
    variants: List[dict] = field(default_factory=list)

    @property
    def kind(self) -> str:
        return KINDS.get(self.category, "concept")

    @property
    def displayable(self) -> bool:
        return self.category in DISPLAY_CATEGORIES and not self.id.startswith("legacy.keyword.")

    def label(self, lang: str) -> str:
        for candidate in LABEL_FALLBACKS.get(lang, (lang, "en", "ru")):
            if candidate in self.labels:
                return self.labels[candidate]
        return next(iter(self.labels.values()), self.id)

    def label_lang(self, lang: str) -> str:
        for candidate in LABEL_FALLBACKS.get(lang, (lang, "en", "ru")):
            if candidate in self.labels:
                return candidate
        return next(iter(self.labels), lang)

    def aliases(self) -> Set[str]:
        """Folded forms used for cross-language query expansion (ТЗ 8.5)."""
        result = set()
        for variant in self.variants:
            folded = fold(variant["value"])
            result.add(folded)
            parts = tokens(folded)
            # "Saryan" alone should still reach "Martiros Saryan".
            if self.category == "person" and len(parts) > 1 and len(parts[-1]) >= 4:
                result.add(parts[-1])
        for label in self.labels.values():
            result.add(fold(label))
        return {alias for alias in result if len(alias) >= 3}

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "category": self.category,
            "review_status": self.review_status,
            "labels": self.labels,
            "variants": self.variants,
        }


def load_entities(terms_path: Path, overrides: Optional[Dict[str, Dict[str, str]]] = None) -> Dict[str, Entity]:
    entities: Dict[str, Entity] = OrderedDict()
    with terms_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["review_status"] == "rejected":
                continue
            entity = entities.get(row["entity_id"])
            if entity is None:
                entity = entities[row["entity_id"]] = Entity(row["entity_id"], row["category"], row["review_status"])
            elif row["review_status"] == "approved":
                entity.review_status = "approved"
            value = row["value"].strip()
            entity.variants.append({"value": value, "lang": row["lang"], "script": row["script"]})
            # The first approved value in file order is the registry label for its language.
            if row["lang"] not in entity.labels or (
                row["review_status"] == "approved" and entity.labels.get("_status_" + row["lang"]) != "approved"
            ):
                entity.labels[row["lang"]] = title_case(value)
                entity.labels["_status_" + row["lang"]] = row["review_status"]
    for entity in entities.values():
        entity.labels = {lang: value for lang, value in entity.labels.items() if not lang.startswith("_status_")}
        entity.labels.update((overrides or {}).get(entity.id, {}))
    return entities


def alias_index(entities: Iterable[Entity]) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    for entity in entities:
        if not entity.displayable:
            continue
        for alias in entity.aliases():
            index.setdefault(alias, []).append(entity.id)
    return index
