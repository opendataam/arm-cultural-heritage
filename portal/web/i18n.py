"""Interface localization (ТЗ 8.1, 8.2).

Messages live in `locales/<lang>.json`. Plural messages are objects keyed by CLDR
plural categories; numbers use CLDR grouping for each language.
"""

import json
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path
from typing import Optional

LOCALES = Path(__file__).parent / "locales"

# Stage 1 languages (ТЗ 8.1). Names are given in the languages themselves (ТЗ 8.2, item 7).
LANGUAGES = OrderedDict(
    [
        ("hy", {"name": "Հայերեն", "dir": "ltr", "bcp47": "hy"}),
        ("ru", {"name": "Русский", "dir": "ltr", "bcp47": "ru"}),
        ("en", {"name": "English", "dir": "ltr", "bcp47": "en"}),
        ("fr", {"name": "Français", "dir": "ltr", "bcp47": "fr"}),
        ("es", {"name": "Español", "dir": "ltr", "bcp47": "es"}),
    ]
)
DEFAULT_LANGUAGE = "hy"
FALLBACK_LANGUAGE = "en"

# CLDR grouping separators; Spanish groups only from five digits (minimumGroupingDigits = 2).
GROUP_SEPARATORS = {"hy": " ", "ru": " ", "en": ",", "fr": " ", "es": "."}
ROMAN_NUMERALS = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
                  (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def plural_category(lang: str, n: int) -> str:
    """CLDR cardinal plural rules for integers."""
    n = abs(int(n))
    if lang == "ru":
        if n % 10 == 1 and n % 100 != 11:
            return "one"
        if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
            return "few"
        return "many"
    if lang in ("hy", "fr"):
        if n in (0, 1):
            return "one"
        return "many" if lang == "fr" and n != 0 and n % 1_000_000 == 0 else "other"
    if lang == "es":
        if n == 1:
            return "one"
        return "many" if n != 0 and n % 1_000_000 == 0 else "other"
    return "one" if n == 1 else "other"


def roman(number: int) -> str:
    result = []
    for value, letters in ROMAN_NUMERALS:
        while number >= value:
            result.append(letters)
            number -= value
    return "".join(result)


class _SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


@lru_cache(maxsize=None)
def _messages(lang: str) -> dict:
    return json.loads((LOCALES / f"{lang}.json").read_text(encoding="utf-8"))


class Translator:
    def __init__(self, lang: str):
        self.lang = lang if lang in LANGUAGES else DEFAULT_LANGUAGE
        self.messages = _messages(self.lang)
        self.fallback = _messages(FALLBACK_LANGUAGE)

    def has(self, key: str) -> bool:
        return key in self.messages or key in self.fallback

    def _raw(self, key: str):
        if key in self.messages:
            return self.messages[key]
        return self.fallback.get(key, key)

    def __call__(self, key: str, default: Optional[str] = None, **values) -> str:
        message = self._raw(key) if self.has(key) or default is None else default
        if isinstance(message, dict):
            message = message.get("other", next(iter(message.values())))
        formatted = {k: self.number(v) if isinstance(v, int) and not isinstance(v, bool) else v for k, v in values.items()}
        return message.format_map(_SafeDict(formatted)) if values else message

    def plural(self, key: str, count: int, **values) -> str:
        message = self._raw(key)
        if isinstance(message, dict):
            message = message.get(plural_category(self.lang, count), message.get("other", ""))
        return message.format_map(_SafeDict(count=self.number(count), **values))

    def number(self, value: int) -> str:
        digits = str(abs(int(value)))
        if len(digits) > 3 and not (self.lang == "es" and len(digits) == 4):
            groups = []
            while digits:
                groups.insert(0, digits[-3:])
                digits = digits[:-3]
            digits = GROUP_SEPARATORS.get(self.lang, ",").join(groups)
        return ("-" if int(value) < 0 else "") + digits

    def century(self, century: int) -> str:
        key = "century.bc" if century < 0 else "century.ad"
        return self(key, roman=roman(abs(century)), number=abs(century))

    def year(self, year: int) -> str:
        return self("year.bc", year=str(abs(year))) if year < 0 else str(year)


def negotiate(accept_language: Optional[str]) -> str:
    """Pick a supported language from Accept-Language (ТЗ 8.2, item 6)."""
    if not accept_language:
        return DEFAULT_LANGUAGE
    weighted = []
    for index, part in enumerate(accept_language.split(",")):
        piece = part.strip().split(";")
        tag = piece[0].strip().lower()
        quality = 1.0
        for parameter in piece[1:]:
            if parameter.strip().startswith("q="):
                try:
                    quality = float(parameter.strip()[2:])
                except ValueError:
                    quality = 0.0
        weighted.append((-quality, index, tag))
    for _, _, tag in sorted(weighted):
        base = tag.split("-")[0]
        if base in LANGUAGES:
            return base
    return DEFAULT_LANGUAGE
