import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from terms import read_terms
from matcher import ArmeniaMatcher


@pytest.fixture(scope="session")
def terms():
    return read_terms(ROOT / "data" / "terms.csv")


@pytest.fixture(scope="session")
def matcher(terms):
    return ArmeniaMatcher(terms)
