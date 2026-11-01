"""SQLite store: published records, full-text index, facets and entities.

The MVP keeps the record store and the search index in one SQLite file. The
interfaces in `portal.search` hide this, so PostgreSQL and OpenSearch (ТЗ 5.3)
can replace it without changing the API or the site.
"""

import sqlite3
from pathlib import Path

SCHEMA = """
create table meta (key text primary key, value text not null);

create table records (
    rowid integer primary key,
    id text not null unique,
    source text not null,
    title text not null,
    sort_title text not null,
    year_from integer,
    year_to integer,
    has_media integer not null,
    media_type text not null,
    content_tier integer not null,
    metadata_tier text not null,
    institution_id text,
    doc text not null
);

-- Contentless index over folded and stemmed text (portal.text.index_text).
create virtual table records_fts using fts5(
    title, body, creators, places, ids,
    content='', tokenize='unicode61 remove_diacritics 2'
);

create table facets (rec integer not null, field text not null, value text not null);

create table entities (
    id text primary key,
    kind text not null,
    category text not null,
    review_status text not null,
    record_count integer not null,
    doc text not null
);

create table entity_aliases (alias text not null, entity_id text not null);

create table institutions (
    id text primary key,
    name text,
    short_name text,
    code text,
    inn text,
    country text,
    source text not null,
    record_count integer not null,
    with_media integer not null
);
"""

INDEXES = """
create index facets_field_value on facets(field, value, rec);
create index facets_rec on facets(rec, field);
create index entity_aliases_alias on entity_aliases(alias);
create index records_year on records(year_from, year_to);
create index records_sort_title on records(sort_title);
create index records_institution on records(institution_id);
"""

# Columns of records_fts and their bm25 weights.
FTS_WEIGHTS = (8.0, 1.0, 4.0, 3.0, 2.0)


def create(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    connection.execute("pragma journal_mode=off")
    connection.execute("pragma synchronous=off")
    connection.executescript(SCHEMA)
    return connection


def finish(connection: sqlite3.Connection) -> None:
    connection.executescript(INDEXES)
    connection.execute("insert into records_fts(records_fts) values ('optimize')")
    connection.commit()
    connection.execute("analyze")
    connection.execute("vacuum")
    connection.close()


def connect(path: Path) -> sqlite3.Connection:
    """Read-only connection for the API; safe to share between threads."""
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection
