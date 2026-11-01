"""Text normalization shared by indexing and querying (ТЗ 8.3).

Both sides must go through the same functions, otherwise stems and folded forms
stop matching.
"""

import html
import re
import unicodedata
from functools import lru_cache
from typing import List

import snowballstemmer

# Armenian emphasis, exclamation, question and abbreviation marks are written inside
# a word and must not split it (ТЗ 8.3, item 4).
ARMENIAN_INWORD_MARKS = dict.fromkeys(map(ord, "՚՛՜՞՟"))
DASHES = re.compile(r"[‐-―−]")
SPACES = re.compile(r"\s+")
TAGS = re.compile(r"<[^>]+>")
WORD = re.compile(r"\w+", re.UNICODE)

_STEMMERS = {
    "Armn": snowballstemmer.stemmer("armenian"),
    "Cyrl": snowballstemmer.stemmer("russian"),
    "Latn": snowballstemmer.stemmer("english"),
}


def clean_text(value) -> str:
    """Source text for display: NFC, no HTML or control characters, single spaces."""
    if value is None:
        return ""
    text = str(value)
    if "<" in text:
        text = TAGS.sub(" ", text)
    text = html.unescape(text)
    text = "".join(ch for ch in text if ch in "\n\t" or unicodedata.category(ch)[0] != "C")
    text = unicodedata.normalize("NFC", text)
    lines = [SPACES.sub(" ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def fold(value: str) -> str:
    """Search key: NFKC, case folding, ё→е, one Armenian orthography.

    Case folding already turns the ligature "և" (U+0587) into "եւ". Reformed
    orthography writes the same sound as "եվ" (Եվրոպա, Եւրոպա), so both are
    reduced to "եւ" (ТЗ 8.3, items 2–3).
    """
    text = unicodedata.normalize("NFKC", value or "").casefold()
    text = text.translate(ARMENIAN_INWORD_MARKS)
    text = text.replace("ё", "е").replace("եվ", "եւ")
    text = DASHES.sub("-", text)
    return SPACES.sub(" ", text).strip()


def script_of(word: str) -> str:
    for ch in word:
        if "԰" <= ch <= "֏" or "ﬓ" <= ch <= "ﬗ":
            return "Armn"
        if "Ѐ" <= ch <= "ӿ":
            return "Cyrl"
        if ch.isalpha() and ch.isascii():
            return "Latn"
    return "Other"


@lru_cache(maxsize=200_000)
def stem(word: str) -> str:
    stemmer = _STEMMERS.get(script_of(word))
    if stemmer is None or word.isdigit():
        return word
    result = stemmer.stemWord(word)
    return result or word


def tokens(value: str) -> List[str]:
    return WORD.findall(fold(value))


def index_text(value: str) -> str:
    """Folded and stemmed text for the full-text index."""
    return " ".join(stem(token) for token in tokens(value))


def title_case(value: str) -> str:
    """Capitalize lowercase registry values for display: "мартирос сарян" → "Мартирос Сарян"."""
    if not value or value != value.lower():
        return value
    return " ".join(part[:1].upper() + part[1:] for part in value.split(" "))
