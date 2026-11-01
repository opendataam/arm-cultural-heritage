import os
import tomllib
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
TERMS_PATH = ROOT / "data" / "terms.csv"


def build_dir() -> Path:
    return Path(os.environ.get("PORTAL_BUILD_DIR", ROOT / "build" / "portal"))


def db_path() -> Path:
    return Path(os.environ.get("PORTAL_DB", build_dir() / "portal.sqlite"))


@dataclass(frozen=True)
class Source:
    id: str
    name: Dict[str, str]
    connector: str
    input: Path
    homepage: str
    record_url: str
    id_prefix: str
    rights: str
    schedule: str = ""
    review_input: Path = None
    options: Dict[str, object] = field(default_factory=dict)

    def label(self, lang: str) -> str:
        return self.name.get(lang) or self.name.get("en") or self.id


def _resolve(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


@lru_cache(maxsize=None)
def load_sources(path: Path = CONFIG_DIR / "sources.toml") -> List[Source]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    sources = []
    for item in data["source"]:
        sources.append(
            Source(
                id=item["id"],
                name=item["name"],
                connector=item["connector"],
                input=_resolve(item["input"]),
                review_input=_resolve(item["review_input"]) if item.get("review_input") else None,
                homepage=item["homepage"],
                record_url=item["record_url"],
                id_prefix=item["id_prefix"],
                rights=item["rights"],
                schedule=item.get("schedule", ""),
                options=item.get("options", {}),
            )
        )
    return sources


def get_source(source_id: str) -> Source:
    for source in load_sources():
        if source.id == source_id:
            return source
    raise KeyError(f"Unknown source: {source_id}")


@lru_cache(maxsize=None)
def load_collections(path: Path = CONFIG_DIR / "collections.toml") -> List[dict]:
    return tomllib.loads(path.read_text(encoding="utf-8"))["collection"]


@lru_cache(maxsize=None)
def load_entity_labels(path: Path = CONFIG_DIR / "entity_labels.toml") -> Dict[str, Dict[str, str]]:
    return tomllib.loads(path.read_text(encoding="utf-8"))
