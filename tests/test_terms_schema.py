import json
import re
from pathlib import Path

from terms import CATEGORIES, FIELDNAMES, REVIEW_STATUSES, SCRIPTS, STRENGTHS, Term, validate_terms

ROOT = Path(__file__).resolve().parent.parent


def test_json_schema_matches_csv_validator(terms):
    schema = json.loads((ROOT / "schema" / "terms.schema.json").read_text(encoding="utf-8"))
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["additionalProperties"] is False
    assert schema["required"] == FIELDNAMES
    assert schema["x-csv"]["columns"] == FIELDNAMES
    assert list(schema["properties"]) == FIELDNAMES
    assert set(schema["properties"]["category"]["enum"]) == CATEGORIES
    assert set(schema["properties"]["match_strength"]["enum"]) == STRENGTHS
    assert set(schema["properties"]["review_status"]["enum"]) == REVIEW_STATUSES
    assert set(schema["properties"]["script"]["enum"]) == SCRIPTS
    entity_pattern = re.compile(schema["properties"]["entity_id"]["pattern"])
    assert all(entity_pattern.fullmatch(term.entity_id) for term in terms)
    for example in schema["examples"]:
        assert validate_terms([Term.from_row(example)]) == []
