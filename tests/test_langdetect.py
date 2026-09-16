"""Pins `qscreen_langdetect.detect_languages` / `apply_language_metadata`."""
from __future__ import annotations

import pytest

import qscreen_langdetect as ld


# ── language_counts ─────────────────────────────────────────────────────────


def test_empty_text_returns_zero_counts():
    assert ld.language_counts("") == {"ar": 0, "latin": 0}


def test_pure_arabic_text_counted_arabic():
    text = "ميزان المراجعة"      # Arabic-script word "balance sheet"
    counts = ld.language_counts(text)
    assert counts["ar"] >= 5
    assert counts["latin"] == 0


def test_pure_english_text_counted_latin():
    text = "Total assets for the year ended 31 December 2023"
    counts = ld.language_counts(text)
    assert counts["latin"] >= 8
    assert counts["ar"] == 0


def test_digits_punctuation_dont_count():
    # Digits, punctuation, and ASCII non-letters are dropped.
    counts = ld.language_counts("0123456789.,;:()[]{}/!?'\"")
    assert counts == {"ar": 0, "latin": 0}


# ── detect_languages ─────────────────────────────────────────────────────────


def test_english_only_filing_is_en_primary():
    text = ("Total assets for the year ended 31 December 2023 "
            "Total liabilities were higher than the prior period.")
    langs = ld.detect_languages(text)
    assert len(langs) == 1
    assert langs[0]["code"] == "en"
    assert langs[0]["primary"] is True
    assert langs[0]["ratio"] == pytest.approx(1.0, abs=0.01)


def test_arabic_only_filing_is_ar_primary():
    text = "ميزان المراجعة القوائم المالية الموحدة الإيرادات المصروفات"
    langs = ld.detect_languages(text)
    assert len(langs) == 1
    assert langs[0]["code"] == "ar"
    assert langs[0]["primary"] is True


def test_bilingual_filing_both_languages_with_one_primary():
    # Mix Arabic + Latin in roughly equal weights. Both must surface, one
    # gets primary, the other not.
    text = "ميزان المراجعة بآلاف الريالات القطرية " * 6 + \
           "Total assets for the year ended 31 December 2023 " * 4
    langs = ld.detect_languages(text)
    codes = {l["code"] for l in langs}
    assert {"ar", "en"} <= codes
    primaries = [l for l in langs if l["primary"]]
    assert len(primaries) == 1


def test_min_ratio_filters_one_off_citations():
    # Heavy English text with a single Arabic word — Arabic shouldn't surface.
    text = ("Total assets for the year ended 31 December 2023. "
            "Total liabilities were higher. ") * 20 + "ميزان"
    langs = ld.detect_languages(text)
    # Very few Arabic letters vs many Latin letters — Arabic ratio well under 5%.
    arabic_langs = [l for l in langs if l["code"] == "ar"]
    assert arabic_langs == []


def test_empty_input_returns_empty_list():
    assert ld.detect_languages("") == []
    assert ld.detect_languages("12345 -- ???!") == []


# ── apply_language_metadata ──────────────────────────────────────────────────


def test_apply_sets_languages_and_backcompat_language_field():
    pages = [
        {"num": 1, "text": "Total assets ميزان المراجعة for the year ended"},
        {"num": 2, "text": "ميزان القوائم المالية Consolidated balance"},
    ]
    filing = {"metadata": {}}
    out = ld.apply_language_metadata(filing, pages=pages)
    assert "languages" in out["metadata"]
    assert out["metadata"]["languages"][0]["primary"] is True
    # Backwards-compat: metadata.language is the primary language code.
    assert out["metadata"]["language"] == out["metadata"]["languages"][0]["code"]
    assert out["metadata"]["languages"][0]["code"] in {"ar", "en"}


def test_apply_overwrites_existing_languages_field():
    """derived field; always recomputed."""
    filing = {"metadata": {"languages": [{"code": "fr", "ratio": 1.0, "primary": True}]}}
    pages = [{"num": 1, "text": "Total assets for the year ended 31 December"}]
    out = ld.apply_language_metadata(filing, pages=pages)
    assert all(l["code"] != "fr" for l in out["metadata"]["languages"])


def test_apply_preserves_user_set_language():
    """Backwards-compat: don't overwrite an explicit metadata.language."""
    filing = {"metadata": {"language": "en"}}
    pages = [{"num": 1, "text": "ميزان المراجعة القوائم"}]
    out = ld.apply_language_metadata(filing, pages=pages)
    # The detected primary is "ar" but the operator pinned "en".
    assert out["metadata"]["language"] == "en"


def test_apply_handles_no_text_pages():
    pages = [{"num": 1, "text": " "}, {"num": 2, "text": ""}]
    filing = {"metadata": {}}
    out = ld.apply_language_metadata(filing, pages=pages)
    assert out["metadata"]["languages"] == []


def test_per_page_rollup_present_in_filing():
    pages = [
        {"num": 1, "text": "Total assets"},
        {"num": 2, "text": "ميزان المراجعة"},
        {"num": 3, "text": "ميزان\nميزان\nميزان"},      # ar-dominant
    ]
    filing = {}
    out = ld.apply_language_metadata(filing, pages=pages)
    assert "page_languages" in out
    # Every page with detectable text should appear.
    assert 1 in out["page_languages"]
    assert 2 in out["page_languages"]
    assert 3 in out["page_languages"]
    assert out["page_languages"][1][0]["code"] == "en"
    assert out["page_languages"][2][0]["code"] == "ar"
