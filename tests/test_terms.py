import unicodedata

from terms import registry_stats, validate_terms


def test_registry_is_valid(terms):
    assert validate_terms(terms) == []


def test_registry_separates_evidence_levels(terms):
    stats = registry_stats(terms)
    assert stats["strong"] > 400
    assert stats["context_only"] > 80
    assert stats["weak"] > 9000
    assert stats["rejected"] >= 50
    assert all(term.active for term in terms if term.match_strength == "strong")
    assert all(not term.active for term in terms if term.match_strength == "weak" or term.review_status == "rejected")


def test_core_terms_and_armenian_script_exist(terms):
    values = {(term.lang, term.value, term.match_strength) for term in terms if term.review_status != "rejected"}
    assert ("ru", "армянский", "strong") in values
    assert ("ru", "армянская", "strong") in values
    assert ("ru", "армяне", "strong") in values
    assert ("hy", "Հայաստան", "strong") in values
    assert ("hy", "հայկական", "strong") in values
    assert ("ru", "армавир", "context_only") in values


def test_no_active_mixed_scripts_or_rejected_ocr(terms):
    for term in terms:
        if not term.active:
            continue
        scripts = {
            "latin" if "LATIN" in unicodedata.name(char, "") else
            "cyrillic" if "CYRILLIC" in unicodedata.name(char, "") else
            "armenian" if "ARMENIAN" in unicodedata.name(char, "") else
            "other"
            for char in term.value if char.isalpha()
        }
        assert len(scripts) == 1 or term.script == "Other"
        assert term.value not in {"армянскомуписателю", "армениия", "ереванеметодом"}
