"""Search, facets and record lookup over the published store (ТЗ 7.4, 8.5)."""

import json
import math
import re
import threading
from collections import Counter, OrderedDict
from itertools import chain
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from portal import store
from portal.text import fold, stem, tokens

FACET_FIELDS = (
    "media", "type", "century", "place", "person", "concept", "creator",
    "institution", "technique", "criteria", "rights", "source",
)
# Fields filtered by the URL but not shown as facet lists.
FILTER_ONLY_FIELDS = ("entity",)
SORTS = ("relevance", "date_asc", "date_desc", "title")
PAGE_SIZES = (24, 48, 96)
MAX_RESULTS = 10_000
QUERY_TOKEN = re.compile(r'(-?)"([^"]*)"|(\S+)')
OR_WORDS = {"OR", "ИЛИ", "OU", "O", "ԿԱՄ", "|"}
# Records with a digital object rank higher (ТЗ 6.9); bm25 scores are negative.
MEDIA_BOOST = 1.3


@dataclass(frozen=True)
class Query:
    q: str = ""
    filters: Tuple[Tuple[str, Tuple[str, ...]], ...] = ()
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    media_only: bool = False
    sort: str = "relevance"
    page: int = 1
    size: int = PAGE_SIZES[0]

    @classmethod
    def build(cls, q="", filters: Optional[Dict[str, List[str]]] = None, **kwargs) -> "Query":
        allowed = set(FACET_FIELDS) | set(FILTER_ONLY_FIELDS)
        clean = tuple(
            sorted((name, tuple(sorted(set(values)))) for name, values in (filters or {}).items()
                   if name in allowed and values)
        )
        sort = kwargs.pop("sort", "relevance")
        size = kwargs.pop("size", PAGE_SIZES[0])
        page = max(1, int(kwargs.pop("page", 1) or 1))
        size = size if size in PAGE_SIZES else PAGE_SIZES[0]
        page = min(page, MAX_RESULTS // size)
        return cls(q=(q or "").strip()[:500], filters=clean, sort=sort if sort in SORTS else "relevance",
                   page=page, size=size, **kwargs)

    def filter_dict(self) -> Dict[str, List[str]]:
        return {name: list(values) for name, values in self.filters}


@dataclass
class Clause:
    raw: str
    stems: List[str]
    negative: bool = False
    phrase: bool = False
    prefix: bool = False
    entity_ids: List[str] = field(default_factory=list)

    def fts(self) -> Optional[str]:
        if not self.stems:
            return None
        if self.phrase or len(self.stems) > 1:
            return '"' + " ".join(self.stems) + '"'
        return f'"{self.stems[0]}"' + ("*" if self.prefix else "")


def _clause(raw: str, negative: bool = False, phrase: bool = False) -> Clause:
    prefix = raw.endswith("*")
    return Clause(raw=raw.rstrip("*"), stems=[stem(t) for t in tokens(raw)], negative=negative,
                  phrase=phrase, prefix=prefix)


def parse_query(q: str) -> List[List[Clause]]:
    """Split a query into AND-ed groups of OR-ed clauses.

    Supports "phrases", -exclusion, OR (also ИЛИ, OU, O, ԿԱՄ) and trailing * for prefixes.
    """
    groups: List[List[Clause]] = []
    join_next = False
    for negative, phrase, word in QUERY_TOKEN.findall(q):
        if word and word.upper() in OR_WORDS:
            join_next = bool(groups)
            continue
        if phrase:
            clause = _clause(phrase, negative=bool(negative), phrase=True)
        else:
            clause = _clause(word[1:], negative=True) if word.startswith("-") and len(word) > 1 else _clause(word)
        if not clause.stems:
            continue
        if join_next and not clause.negative and groups and not groups[-1][0].negative:
            groups[-1].append(clause)
        else:
            groups.append([clause])
        join_next = False
    return groups


class SearchService:
    """Search over the published store.

    Full-text matching runs in SQLite FTS5. Filtering, facet counts and sorting run
    in memory over compact per-record arrays loaded at start-up: for the MVP corpus
    this keeps broad queries fast without a separate search server.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._local = threading.local()
        connection = self.connection
        self.meta = {row["key"]: row["value"] for row in connection.execute("select key, value from meta")}
        self.entities = {
            row["id"]: {**json.loads(row["doc"]), "record_count": row["record_count"]}
            for row in connection.execute("select id, doc, record_count from entities")
        }
        self.institutions = {row["id"]: dict(row) for row in connection.execute("select * from institutions")}
        self._load_arrays(connection)
        self._cache: "OrderedDict[Query, dict]" = OrderedDict()
        self._cache_lock = threading.Lock()

    @property
    def connection(self):
        connection = getattr(self._local, "connection", None)
        if connection is None:
            connection = self._local.connection = store.connect(self.db_path)
        return connection

    def _load_arrays(self, connection) -> None:
        rows = connection.execute(
            "select rowid, has_media, year_from, year_to, sort_title, metadata_tier from records order by rowid"
        ).fetchall()
        size = (rows[-1]["rowid"] + 1) if rows else 1
        self.all_rowids = frozenset(row["rowid"] for row in rows)
        self.has_media = [0] * size
        self.year_from: List[Optional[int]] = [None] * size
        self.year_to: List[Optional[int]] = [None] * size
        for row in rows:
            self.has_media[row["rowid"]] = row["has_media"]
            self.year_from[row["rowid"]] = row["year_from"]
            self.year_to[row["rowid"]] = row["year_to"]
        shuffle = lambda r: (r["rowid"] * 2654435761) % 4294967296
        # Precomputed orders; a page of any result set is read off them by membership.
        self.orders = {
            "browse": [r["rowid"] for r in sorted(rows, key=lambda r: (-r["has_media"], r["metadata_tier"], shuffle(r)))],
            "date_asc": [r["rowid"] for r in sorted(
                rows, key=lambda r: (r["year_from"] is None, r["year_from"] or 0, r["year_to"] or 0, r["rowid"]))],
            "date_desc": [r["rowid"] for r in sorted(
                rows, key=lambda r: (r["year_to"] is None, -(r["year_to"] or 0), -(r["year_from"] or 0), r["rowid"]))],
            "title": [r["rowid"] for r in sorted(rows, key=lambda r: (r["sort_title"], r["rowid"]))],
        }
        self.facet_keys: List[Tuple[str, str]] = []
        key_ids: Dict[Tuple[str, str], int] = {}
        per_record: List[List[int]] = [[] for _ in range(size)]
        placeholders = ",".join("?" * len(FACET_FIELDS))
        for rec, name, value in connection.execute(
            f"select rec, field, value from facets where field in ({placeholders})", FACET_FIELDS
        ):
            key = (name, value)
            key_id = key_ids.get(key)
            if key_id is None:
                key_id = key_ids[key] = len(self.facet_keys)
                self.facet_keys.append(key)
            per_record[rec].append(key_id)
        self.record_facets = [tuple(ids) for ids in per_record]

    # --- Query expansion ---------------------------------------------------------

    def aliases(self, text: str) -> List[str]:
        folded = fold(text)
        if len(folded) < 3:
            return []
        rows = self.connection.execute(
            "select distinct entity_id from entity_aliases where alias = ?", (folded,)
        ).fetchall()
        return [row["entity_id"] for row in rows]

    def plan(self, q: str) -> Tuple[List[List[Clause]], List[str]]:
        """Parse the query and attach entities named by its clauses (ТЗ 8.5)."""
        groups = parse_query(q)
        plain = all(len(g) == 1 and not g[0].negative and not g[0].phrase for g in groups)
        if plain and len(groups) > 1:
            # "Martiros Saryan" names one entity as a whole.
            whole = self.aliases(q)
            if whole:
                clause = Clause(raw=q, stems=[c.stems[0] for g in groups for c in g], entity_ids=whole)
                return [[clause]], whole
        expanded = []
        for group in groups:
            for clause in group:
                if not clause.negative and not clause.prefix:
                    clause.entity_ids = self.aliases(clause.raw)
                    expanded.extend(clause.entity_ids)
        return groups, list(dict.fromkeys(expanded))

    # --- Sets ---------------------------------------------------------------------

    def _fts(self, expression: str, scored: bool = False) -> Dict[int, float]:
        if scored:
            weights = ", ".join(str(w) for w in store.FTS_WEIGHTS)
            sql = f"select rowid, bm25(records_fts, {weights}) from records_fts where records_fts match ?"
            return dict(self.connection.execute(sql, (expression,)).fetchall())
        rows = self.connection.execute("select rowid from records_fts where records_fts match ?", (expression,))
        return dict.fromkeys((row[0] for row in rows), 0.0)

    def _filter_set(self, name: str, values: Tuple[str, ...]) -> set:
        rows = self.connection.execute(
            "select rec from facets where field = ? and value in (%s)" % ",".join("?" * len(values)),
            (name, *values),
        )
        return {row[0] for row in rows}

    def _match(self, groups: List[List[Clause]], scored: bool) -> Tuple[set, Dict[int, float]]:
        """Rowids matching the query and bm25 scores of its full-text part."""
        hits: Optional[set] = None
        scores: Dict[int, float] = {}
        for group in groups:
            if group[0].negative:
                continue
            expression = " OR ".join(f"({c.fts()})" for c in group if c.fts())
            matched = self._fts(expression, scored)
            for rowid, score in matched.items():
                scores[rowid] = scores.get(rowid, 0.0) + score
            group_set = set(matched)
            entity_ids = tuple(e for c in group for e in c.entity_ids)
            if entity_ids:
                group_set |= self._filter_set("entity", entity_ids)
            hits = group_set if hits is None else hits & group_set
        if hits is None:
            hits = set(self.all_rowids)
        excluded = [c.fts() for g in groups if g[0].negative for c in g if c.fts()]
        if excluded:
            hits -= set(self._fts(" OR ".join(f"({e})" for e in excluded)))
        return hits, scores

    def _restrict(self, hits: set, query: Query) -> set:
        if query.year_from is not None:
            hits = {r for r in hits if self.year_to[r] is not None and self.year_to[r] >= query.year_from}
        if query.year_to is not None:
            hits = {r for r in hits if self.year_from[r] is not None and self.year_from[r] <= query.year_to}
        if query.media_only:
            hits = {r for r in hits if self.has_media[r]}
        return hits

    # --- Public API -----------------------------------------------------------

    def search(self, query: Query, facet_limit: int = 12, with_facets: bool = True) -> dict:
        key = (query, facet_limit, with_facets)
        with self._cache_lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return self._cache[key]
        result = self._search(query, facet_limit, with_facets)
        with self._cache_lock:
            self._cache[key] = result
            if len(self._cache) > 256:
                self._cache.popitem(last=False)
        return result

    def _search(self, query: Query, facet_limit: int, with_facets: bool) -> dict:
        groups, expanded = self.plan(query.q) if query.q else ([], [])
        ranked = bool(groups) and query.sort == "relevance"
        base, scores = self._match(groups, ranked) if groups else (set(self.all_rowids), {})
        base = self._restrict(base, query)
        filter_sets = {name: self._filter_set(name, values) for name, values in query.filters}
        hits = base.intersection(*filter_sets.values()) if filter_sets else base

        offset = (query.page - 1) * query.size
        if ranked:
            boost = lambda r: scores.get(r, 0.0) * (MEDIA_BOOST if self.has_media[r] else 1.0)
            page = sorted(hits, key=lambda r: (boost(r), r))[offset : offset + query.size]
        else:
            order = self.orders["browse" if query.sort == "relevance" else query.sort]
            page = []
            seen = 0
            for rowid in order:
                if rowid in hits:
                    if seen >= offset:
                        page.append(rowid)
                        if len(page) == query.size:
                            break
                    seen += 1
        total = len(hits)
        result = {
            "total": total,
            "page": query.page,
            "size": query.size,
            "pages": max(1, min(-(-total // query.size), MAX_RESULTS // query.size)),
            "items": [summary(doc) for doc in self.docs(page)],
            "expanded_entities": expanded,
        }
        if with_facets:
            result["facets"] = self._facets(query, base, filter_sets, hits, facet_limit)
        return result

    def _count(self, rowids: Iterable[int], fields: set) -> Dict[str, List[Tuple[str, int]]]:
        counter = Counter(chain.from_iterable(self.record_facets[r] for r in rowids))
        facets: Dict[str, List[Tuple[str, int]]] = {}
        for key_id, count in counter.items():
            name, value = self.facet_keys[key_id]
            if name in fields:
                facets.setdefault(name, []).append((value, count))
        return facets

    def _facets(self, query: Query, base: set, filter_sets: Dict[str, set], hits: set, limit: int):
        facets = self._count(hits, set(FACET_FIELDS) - set(filter_sets))
        # A field's own filter is ignored for its counts, so more values can be added with OR.
        for name in set(filter_sets) & set(FACET_FIELDS):
            others = [s for other, s in filter_sets.items() if other != name]
            facets.update(self._count(base.intersection(*others) if others else base, {name}))
        selected = query.filter_dict()
        for name, values in facets.items():
            if name == "century":
                values.sort(key=lambda item: int(item[0]))
                continue
            values.sort(key=lambda item: (-item[1], item[0]))
            chosen = set(selected.get(name, []))
            facets[name] = values[:limit] + [item for item in values[limit:] if item[0] in chosen]
        return facets

    def docs(self, rowids: List[int]) -> List[dict]:
        if not rowids:
            return []
        rows = self.connection.execute(
            "select rowid, doc from records where rowid in (%s)" % ",".join("?" * len(rowids)), rowids
        ).fetchall()
        docs = {row[0]: json.loads(row[1]) for row in rows}
        return [docs[rowid] for rowid in rowids if rowid in docs]

    def record(self, record_id: str) -> Optional[dict]:
        row = self.connection.execute("select doc from records where id = ?", (record_id,)).fetchone()
        return json.loads(row["doc"]) if row else None

    def similar(self, record: dict, limit: int = 8) -> List[dict]:
        """Records sharing the most displayable entities and creators (ТЗ 7.5, item 12)."""
        keys = [("entity", e) for e in record["entities"] if e in self.entities]
        keys += [("creator", c["name"]) for c in record["creators"]]
        shared: Dict[int, float] = Counter()
        for name, value in keys:
            matched = self._filter_set(name, (value,))
            # Rare shared entities say more than "Armenia" shared with 20,000 records.
            weight = 1.0 / (1.0 + math.log(max(len(matched), 1)))
            for rowid in matched:
                shared[rowid] += weight
        own = self.connection.execute("select rowid from records where id = ?", (record["id"],)).fetchone()
        shared.pop(own[0] if own else None, None)
        browse_rank = {r: i for i, r in enumerate(self.orders["browse"])} if shared else {}
        best = sorted(shared, key=lambda r: (-shared[r], browse_rank.get(r, 0)))[:limit]
        return [summary(doc) for doc in self.docs(best)]

    def suggest(self, prefix: str, limit: int = 8) -> List[dict]:
        folded = fold(prefix)
        if len(folded) < 2:
            return []
        rows = self.connection.execute(
            """select a.entity_id, max(e.record_count) as n from entity_aliases a
               join entities e on e.id = a.entity_id
               where a.alias >= ? and a.alias < ? group by a.entity_id order by n desc limit ?""",
            (folded, folded + "\U0010ffff", limit),
        ).fetchall()
        return [{"id": row["entity_id"], "count": row["n"]} for row in rows]

    def sample(self, query: Query, count: int = 1) -> List[dict]:
        return self.search(replace(query, size=PAGE_SIZES[0], page=1), with_facets=False)["items"][:count]


def summary(record: dict) -> dict:
    """Fields for a result card (ТЗ 7.4, «Выдача»)."""
    creators = record["creators"]
    return {
        "id": record["id"],
        "title": record["title"],
        "titles": record.get("titles") or {},
        "creator": creators[0]["name"] if creators else None,
        "date": record["date"]["display"] or None,
        "institution": record["institution"]["short_name"],
        "institution_id": record["institution"]["id"],
        "media_type": record["media_type"],
        "type_id": record["object_type"]["id"],
        "thumbnail": record["media"][0]["url"] if record["media"] else None,
        "media_count": len(record["media"]),
        "rights": record["rights"]["uri"],
        "metadata_lang": record["metadata_lang"],
    }
