"""Normalization of dates, creators and institutions (ТЗ 6.5)."""

import re
from dataclasses import asdict, dataclass
from datetime import date
from typing import Optional, Tuple

MAX_YEAR = date.today().year
MIN_YEAR = -10_000

ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}
# Russian sources often type Roman numerals with Cyrillic look-alikes: "ХХ в.", "ІІ в.".
CYRILLIC_ROMAN = str.maketrans({"х": "x", "і": "i"})

BC = re.compile(r"до\s*н\.?\s*э|до\s+нашей\s+эры")
APPROXIMATE = re.compile(r"(?:^|\W)(?:ок|около|прибл|примерно|предп)\.?(?:\W|$)|\?|~")
DECADE = re.compile(r"(\d{3,4})\s*[-–—]?\s*(?:(\d{3,4})\s*[-–—]?\s*)?(?:е|х|ые)\b")
YEAR_RANGE = re.compile(r"(?<!\d)(\d{3,4})\s*[-–—/]\s*(\d{2,4})(?!\d)")
YEAR = re.compile(r"(?<!\d)(\d{3,4})(?!\d)")
# "XIX в.", "20 век", "I-III вв.", "кон. XIX - нач. XX в.": a numeral, an optional range
# with its own qualifier, and the unit word. Four digits are allowed so that "1990 в."
# and "1000 тыс." are matched and then rejected instead of being read as other numbers.
NUMERAL = r"([ivxlc]+|\d{1,4})\s*(?:-?(?:й|го|ый|ого|е))?\s*"
ORDINAL = r"\b" + NUMERAL + r"(?:[-–—]\s*((?![ivxlc]+\b)[^\W\d]+\.?\s*)?" + NUMERAL + r")?"
CENTURY = re.compile(ORDINAL + r"(?:вв?\b\.?|век[аов]*\b)")
MILLENNIUM = re.compile(ORDINAL + r"тыс")
# Part of a century as (start, end) fractions.
CENTURY_PARTS = [
    (re.compile(r"(?:1|перв)[-\w]*\.?\s*пол"), (0.0, 0.5)),
    (re.compile(r"(?:2|втор)[-\w]*\.?\s*пол"), (0.5, 1.0)),
    (re.compile(r"(?:1|перв)[-\w]*\.?\s*четв"), (0.0, 0.25)),
    (re.compile(r"(?:2|втор)[-\w]*\.?\s*четв"), (0.25, 0.5)),
    (re.compile(r"(?:3|трет)[-\w]*\.?\s*четв"), (0.5, 0.75)),
    (re.compile(r"(?:4|четв[её]рт|послед)[-\w]*\.?\s*четв"), (0.75, 1.0)),
    (re.compile(r"нач"), (0.0, 0.33)),
    (re.compile(r"сер"), (0.33, 0.67)),
    (re.compile(r"кон"), (0.67, 1.0)),
]
SOURCE_DATE = re.compile(r"^([+-]?\d{4,6})-\d{2}-\d{2}")


@dataclass
class Period:
    display: str
    year_from: Optional[int]
    year_to: Optional[int]
    approximate: bool = False
    method: str = "none"

    @property
    def edtf(self) -> Optional[str]:
        if self.year_from is None:
            return None
        start, end = edtf_year(self.year_from), edtf_year(self.year_to)
        value = start if self.year_from == self.year_to else f"{start}/{end}"
        return value + "~" if self.approximate and "/" not in value else value

    def as_dict(self) -> dict:
        data = asdict(self)
        data["edtf"] = self.edtf
        return data


def edtf_year(year: int) -> str:
    # EDTF follows ISO 8601: year 0000 is 1 BC, so historical years BC shift by one.
    if year < 0:
        year += 1
    return f"-{abs(year):04d}" if year < 0 else f"{year:04d}"


def roman_to_int(value: str) -> Optional[int]:
    value = value.lower().translate(CYRILLIC_ROMAN)
    if value.isdigit():
        return int(value)
    if not value or any(ch not in ROMAN for ch in value):
        return None
    total = 0
    for current, following in zip(value, value[1:] + " "):
        number = ROMAN[current]
        total += -number if following in ROMAN and ROMAN[following] > number else number
    return total


def plausible(year_from: Optional[int], year_to: Optional[int]) -> bool:
    return (
        year_from is not None
        and year_to is not None
        and MIN_YEAR <= year_from <= year_to <= MAX_YEAR
    )


def century_part(text: Optional[str]) -> Tuple[float, float]:
    return next((frac for rule, frac in CENTURY_PARTS if text and rule.search(text)), (0.0, 1.0))


def _period_bounds(number: int, span: int, bc: bool, part: Tuple[float, float]) -> Tuple[int, int]:
    """Years of the n-th century (span=100) or millennium (span=1000), or of a part of it."""
    if bc:
        # Years BC count backwards: the second half of the 5th century BC is 450–401 BC.
        part = (1.0 - part[1], 1.0 - part[0])
    first, last = (number - 1) * span + 1, number * span
    start = first + round(part[0] * span)
    end = first - 1 + round(part[1] * span)
    start, end = max(start, first), min(end, last)
    if bc:
        return -end, -start
    return start, end


def parse_period_string(raw: str) -> Optional[Period]:
    """Parse the free-text Russian period: "1961 г.", "1920-1930-е гг.", "Нач. ХХ в.", "I-III вв. до н.э."."""
    if not raw:
        return None
    text = raw.strip().lower().replace("ё", "е")
    bc = bool(BC.search(text))
    approximate = bool(APPROXIMATE.search(text))

    match = DECADE.search(text)
    if match and not bc:
        first = int(match.group(1))
        last = int(match.group(2) or match.group(1))
        if first % 10 == 0 and last % 10 == 0:
            return Period(raw, first, last + 9, approximate, "decade")

    for pattern, span, limit, method in (
        (MILLENNIUM, 1000, 10, "millennium"),
        (CENTURY, 100, 21, "century"),
    ):
        # The translation is one-to-one, so match positions stay valid for `text`.
        match = pattern.search(text.translate(CYRILLIC_ROMAN))
        if not match:
            continue
        first = roman_to_int(match.group(1))
        last = roman_to_int(match.group(3)) if match.group(3) else first
        if not (first and last and 0 < first <= limit and 0 < last <= limit):
            # "1000 тыс." is not a year; "1990 в." still is one.
            if method == "millennium":
                return None
            break
        first_part = century_part(text[: match.start()])
        last_part = century_part(match.group(2)) if match.group(3) else first_part
        bounds = _period_bounds(first, span, bc, first_part) + _period_bounds(last, span, bc, last_part)
        year_from, year_to = min(bounds), max(bounds)
        if plausible(year_from, year_to):
            return Period(raw, year_from, year_to, approximate, method)
        break

    match = YEAR_RANGE.search(text)
    if match:
        first, second = match.group(1), match.group(2)
        if len(second) < len(first):
            second = first[: len(first) - len(second)] + second
        year_from, year_to = int(first), int(second)
        if bc:
            year_from, year_to = -year_from, -year_to
        year_from, year_to = min(year_from, year_to), max(year_from, year_to)
        if plausible(year_from, year_to):
            return Period(raw, year_from, year_to, approximate, "range")

    years = [int(value) for value in YEAR.findall(text)]
    if years:
        if bc:
            years = [-year for year in years]
        year_from, year_to = min(years), max(years)
        if plausible(year_from, year_to):
            return Period(raw, year_from, year_to, approximate, "year")
    return None


def source_year(value) -> Optional[int]:
    if not isinstance(value, str):
        return None
    match = SOURCE_DATE.match(value.strip())
    return int(match.group(1)) if match else None


def normalize_period(period_str, start_date, finish_date) -> Period:
    """Prefer the human-readable string; fall back to structured dates when they are plausible.

    The structured `startDate`/`finishDate` of Goskatalog contain placeholders such as
    2099-12-03 or +198900-12-31, so they are trusted only after validation.
    """
    raw = (period_str or "").strip()
    parsed = parse_period_string(raw)
    if parsed:
        return parsed
    year_from = source_year(start_date)
    year_to = source_year(finish_date) or year_from
    if plausible(year_from, year_to):
        return Period(raw or str(year_from), year_from, year_to, False, "source_dates")
    return Period(raw, None, None, False, "none")


ROLE_HINTS = (
    "автор", "фотограф", "художник", "издат", "гравер", "гравёр", "мастер", "редакт",
    "состав", "исполн", "архитект", "скульпт", "композит", "изготов", "литограф",
    "печат", "рисун", "оформ", "переплет", "типограф", "медальер", "резчик", "ювелир",
    "чеканщ", "дизайн", "иллюстр", "перевод", "модел", "мастерск", "фабрик", "завод",
    "ателье", "фирм", "владел", "отправ", "адресат", "получат", "заказ", "даритель",
)
TRAILING_PARENS = re.compile(r"^(?P<name>.*?)\s*\((?P<role>[^()]*)\)\s*$")


def parse_creator(raw: str) -> Optional[dict]:
    """Split "Раскин Лев Абрамович (Фотограф)" into a name and a role.

    A trailing parenthetical is a role only when it contains a role word, so name
    variants such as "Буниатов (Буниатян) Н.Г." stay intact.
    """
    text = re.sub(r"\s+", " ", raw or "").strip(" ,;")
    if not text:
        return None
    name, role = text, None
    match = TRAILING_PARENS.match(text)
    if match and match.group("name") and any(hint in match.group("role").lower() for hint in ROLE_HINTS):
        name, role = match.group("name").strip(" ,;"), match.group("role").strip()
    return {"name": name, "role": role, "raw": raw.strip()}


QUOTES = "\"«»“”„"


def short_institution_name(name: str) -> str:
    """Drop the legal form: 'ФГБУК "Государственный Эрмитаж"' → 'Государственный Эрмитаж'.

    The first quoted segment is the name. An odd number of quotes, or a segment that
    ends with a space, means a nested name such as 'музей-заповедник "Царицыно"'.
    """
    if not name:
        return ""
    positions = [i for i, ch in enumerate(name) if ch in QUOTES]
    if len(positions) < 2:
        return name.strip()
    first = name[positions[0] + 1 : positions[1]]
    if len(positions) % 2 == 0 and not first.endswith(" "):
        return first.strip() or name.strip()
    inner = name[positions[0] + 1 : positions[-1]].strip()
    if sum(1 for ch in inner if ch in QUOTES) % 2:
        inner += '"'
    return inner or name.strip()
