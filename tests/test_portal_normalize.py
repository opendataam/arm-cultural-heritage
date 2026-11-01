import pytest

from portal.pipeline.normalize import (
    normalize_period,
    parse_creator,
    parse_period_string,
    short_institution_name,
)
from portal.text import fold, index_text, stem


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("1961 г.", (1961, 1961, "1961")),
        ("1920-1930-е гг.", (1920, 1939, "1920/1939")),
        ("1970-е гг.", (1970, 1979, "1970/1979")),
        ("1987-1990 гг.", (1987, 1990, "1987/1990")),
        ("1914-18", (1914, 1918, "1914/1918")),
        ("1958.12.04", (1958, 1958, "1958")),
        ("ок. 1650", (1650, 1650, "1650~")),
        ("Нач. ХХ в.", (1901, 1933, "1901/1933")),
        ("20 век", (1901, 2000, "1901/2000")),
        ("конец 20 века", (1968, 2000, "1968/2000")),
        ("2-я пол. XIX в.", (1851, 1900, "1851/1900")),
        ("XVIII-XIX вв.", (1701, 1900, "1701/1900")),
        ("I-III вв.", (1, 300, "0001/0300")),
        ("кон. XIX - нач. XX в.", (1868, 1933, "1868/1933")),
        ("V в. до н.э.", (-500, -401, "-0499/-0400")),
        ("1-я пол. V в. до н.э.", (-500, -451, "-0499/-0450")),
        ("2-я пол. I тыс. до н.э.", (-500, -1, "-0499/0000")),
        ("1990 в.", (1990, 1990, "1990")),
    ],
)
def test_period_strings(raw, expected):
    period = parse_period_string(raw)
    assert (period.year_from, period.year_to, period.edtf) == expected


@pytest.mark.parametrize("raw", ["поздняя бронза", "не определено", "-", "2-я пол.1000 тыс. до н.э.", ""])
def test_unparseable_period_strings(raw):
    assert parse_period_string(raw) is None


def test_structured_dates_are_validated():
    assert normalize_period(None, "1961-01-01T12:00:00.000Z", None).year_from == 1961
    # Goskatalog placeholders are rejected rather than published as dates.
    assert normalize_period(None, "2099-12-03T12:00:00.000Z", None).year_from is None
    assert normalize_period("поздняя бронза", "+198900-12-31T21:00:00.000Z", None).year_from is None
    # The human-readable string wins over a contradicting structured date.
    assert normalize_period("1990 в.", "+198900-12-31T21:00:00.000Z", None).year_from == 1990


def test_creator_roles():
    assert parse_creator("Раскин Лев Абрамович (Фотограф)") == {
        "name": "Раскин Лев Абрамович", "role": "Фотограф", "raw": "Раскин Лев Абрамович (Фотограф)",
    }
    assert parse_creator(" Дубасов Иван Иванович (Автор эскиза реверса)")["role"] == "Автор эскиза реверса"
    # A name variant in parentheses is not a role.
    assert parse_creator("Буниатов (Буниатян) Н.Г.")["name"] == "Буниатов (Буниатян) Н.Г."
    assert parse_creator("  ") is None


@pytest.mark.parametrize(
    "name, expected",
    [
        ('Федеральное государственное бюджетное учреждение культуры "Государственный Эрмитаж"', "Государственный Эрмитаж"),
        ('ГБУК города Москвы "Государственный музей-заповедник "Царицыно"', 'Государственный музей-заповедник "Царицыно"'),
        ('ФГБУК "Военно-исторический музей артиллерии" Министерства обороны', "Военно-исторический музей артиллерии"),
        ('Структурное подразделение "Музейный комплекс" учреждения "Тюменское объединение"', "Музейный комплекс"),
        ("МБУК «Краеведческий музей»", "Краеведческий музей"),
        ("Музей без кавычек", "Музей без кавычек"),
    ],
)
def test_short_institution_name(name, expected):
    assert short_institution_name(name) == expected


def test_armenian_orthography_folds_to_one_form():
    # Reformed "Երևան", classical "Երեւան" and the ligature all reach one search key (ТЗ 8.3).
    assert fold("Երևան") == fold("Երեւան") == fold("ԵՐԵՎԱՆ")
    assert fold("Եվրոպա") == fold("Եւրոպա")
    assert fold("Ёлка") == "елка"
    # Emphasis and question marks inside a word do not split it.
    assert index_text("ինչու՞") == index_text("ինչու")


def test_stemming_matches_word_forms():
    assert stem("армянская") == stem("армянский") == stem("армянских")
    assert index_text("Армянская картина") == index_text("армянские картины")
