import pytest


@pytest.mark.parametrize("text", [
    "Армянская рукопись",
    "армянский ковёр",
    "армяне",
    "армян",
    "армянине",
    "армянской",
    "армянскаго",
    "армянскiй",
    "армянскiими",
    "АрмССР",
    "Арм. ССР",
    "Ереванский театр",
    "Хранился в Ереване",
    "Хачкары Арцаха",
    "Матенадаран",
    "Հայկական ձեռագիր",
    "Հայաստան",
    "Հայաստանում",
    "հայերի",
    "Ermenistan",
    "Arménie",
    "Armenien",
    "ارمنستان",
    "أرمينيا",
    "Месроп Маштоц",
    "Иван Айвазовский",
    "Картина И.К. Айвазовского",
    "Айвазовский И.К.",
    "Портрет Сергея Параджанова",
    "Режиссер Параджанов С.И.",
    "А.И. Хачатурян",
    "Сарьян М.С.",
    "Квартет имени Комитаса",
    "Саят-Нова",
    "Храм в Артике в Армении",
    "Перевод с древнеармянского",
    "Новоармянская церковь",
    "На армянск. яз.",
    "Гандзасарский монастырь",
    "Эчмиадзинь",
    "Ериван",
    "Armeniae",
    "Нарекаци Григор",
    "de Armeniaco",
    "Armeni",
    "дельи Армени",
])
def test_strong_matches_include(matcher, text):
    result = matcher.classify({"name": text})
    assert result.decision == "include", text
    assert result.strength == "strong"


@pytest.mark.parametrize("text", [
    "Бармен",
    "Ванна",
    "Дядя Ваня",
    "Ткацкое бердо",
    "Килики",
    "Армянск",
    "армянскомуписателю",
    "армениия",
    "Арменинова",
    "Армяниновой",
    "germanian",
    "organization",
])
def test_false_substrings_and_ocr_do_not_match(matcher, text):
    assert matcher.classify({"name": text}).decision == "exclude"


@pytest.mark.parametrize("text", [
    "Григорианский календарь",
    "Предмет из Карса",
    "Тифлис",
    "Нахичеван",
    "dolma",
    "David",
    "Petrosyan",
    "Cher seigneur d'Aguilles",
    "артик. 4461",
    "Айвазовский",
    "Хачатурян",
    "Параджанов",
    "Арменин",
    "armeniaco",
    "Нахичевань-на-Дону",
    "Портрет Екатерины II тип А. Рослина",
])
def test_context_and_weak_matches_require_review(matcher, text):
    result = matcher.classify({"name": text})
    assert result.decision == "review", text
    assert result.strength in {"context_only", "weak"}


def test_armavir_negative_context_is_local_to_rule(matcher):
    negative = matcher.classify({"name": "Предмет", "productionPlace": "Армавир, Краснодарский край"})
    assert negative.decision == "exclude"
    assert negative.negated
    positive = matcher.classify({"name": "Предмет", "productionPlace": "Армавир, Армянская ССР"})
    assert positive.decision == "include"
    independent = matcher.classify({"name": "Книга об Армении", "productionPlace": "Армавир, Краснодарский край"})
    assert independent.decision == "include"


def test_museum_is_not_standalone_evidence(matcher):
    result = matcher.classify({"name": "Часть рации", "museum": {"name": "Музей Армении"}})
    assert result.decision == "review"
    assert result.strength == "museum_only"
    assert result.metadata()["armenia_matched_fields"] == ["museum.name"]
    armyansk = matcher.classify({"name": "Часть рации", "museum": {"name": "Музей города Армянска Республики Крым"}})
    assert armyansk.decision == "exclude"


def test_context_plus_strong_is_included(matcher):
    result = matcher.classify({"name": "Dolma", "description": "Armenian cuisine"})
    assert result.decision == "include"
    assert "context_only" not in result.strength


def test_nested_fields_and_original_field_names(matcher):
    result = matcher.classify({"name": "Предмет", "typology": {"name": "Армянская рукопись"}})
    assert result.decision == "include"
    assert "typology.name" in result.metadata()["armenia_matched_fields"]


def test_unicode_yo_and_dash_normalization(matcher):
    result = matcher.classify({"name": "Армяно—григорианская церковь"})
    assert result.decision == "include"


def test_prefilter_hints_do_not_change_exact_matches(matcher):
    record = {"name": "Армения и Карс", "description": "Армянская рукопись и Dolma"}
    full = matcher.classify(record).metadata()
    hinted = matcher.classify(record, ["армения", "карс", "армянская", "dolma"]).metadata()
    assert hinted == full
