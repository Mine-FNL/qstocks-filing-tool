"""Pins `qscreen_autodetect.detect_*` and `apply_detected_metadata`."""
from __future__ import annotations

import pytest

import qscreen_autodetect as ad


# ── detect_sector ────────────────────────────────────────────────────────────


def test_sector_islamic_bank_match():
    text = """Qatar Islamic Bank (QIBK) Q.P.S.C.
    The financial position was prepared in accordance with IFRS as adopted by QCB (Islamic)
    and the Sharia Supervisory Board's directives. Net income from Islamic financing
    is the principal revenue source. We hold sukuk and Investment in Sukuk."""
    assert ad.detect_sector(text) == "islamic_bank"


def test_sector_insurance_takaful_match():
    text = """Takaful Insurance Company Q.P.S.C.
    Wakala fees, Tabarru', Retakaful ceded, IBNR technical reserves.
    Two income statements: Policyholders' Income Statement and Shareholders' Income Statement."""
    assert ad.detect_sector(text) == "insurance"


def test_sector_industrial_match():
    text = """Industries Qatar Q.P.S.C.
    Manufacturing segment revenue from contracts and goods sold.
    Cost of sales, finished goods, and inventories dominate the BS."""
    assert ad.detect_sector(text) == "industrial"


def test_sector_profile_overrides_text():
    profile = {"archetype": "islamic_bank"}
    text = "Some text about generic commerce and inventory"
    assert ad.detect_sector(text, profile=profile) == "islamic_bank"


def test_sector_none_when_no_signal():
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    assert ad.detect_sector(text) is None


def test_real_estate_signal_collapses_to_other_when_no_industrial():
    text = "Investment property carrying value QR 47 billion, real estate holding"
    # No other industrial hits; investment-property alone shouldn't claim
    # industrial.
    s = ad.detect_sector(text)
    assert s in ("other", None)


# ── detect_period ────────────────────────────────────────────────────────────


def test_period_fy():
    text = "Consolidated Income Statement for the year ended 31 December 2023"
    assert ad.detect_period(text) == "FY"


def test_period_q3():
    text = "...for the nine months ended 30 September 2023"
    assert ad.detect_period(text) == "9M"


def test_period_h1():
    text = "...for the six months ended 30 June 2023"
    assert ad.detect_period(text) == "H1"


def test_period_none_when_undetectable():
    text = "This is a press release about the upcoming shareholders meeting."
    assert ad.detect_period(text) is None


# ── detect_framework ─────────────────────────────────────────────────────────


def test_framework_ifrs_qcb_islamic():
    text = "IFRS as adopted by QCB (Islamic) and the Sharia Supervisory Board directives"
    assert ad.detect_framework(text) == "IFRS as adopted by QCB (Islamic)"


def test_framework_aaoifi():
    text = "Prepared in accordance with AAOIFI standards issued by the Accounting and " \
           "Auditing Organisation for Islamic Financial Institutions."
    assert ad.detect_framework(text) == "AAOIFI"


def test_framework_generic_ifrs():
    text = "in accordance with International Financial Reporting Standards (IFRS)"
    assert ad.detect_framework(text) == "IFRS"


def test_framework_islamic_bank_override():
    """For an Islamic bank whose cover only says 'IFRS', the regulator-mandated
    QCB-Islamic variant is the right label — KAM reporters expect this."""
    text = "Prepared in accordance with IFRS. Profit-sharing investment accounts."
    sector = "islamic_bank"
    assert ad.detect_framework(text, sector=sector) == "IFRS as adopted by QCB (Islamic)"


# ── apply_detected_metadata ──────────────────────────────────────────────────


def test_apply_does_not_overwrite_explicit_values():
    filing = {
        "metadata": {"symbol": "ABCD", "sector": "other",
                       "fiscal_period": "H1", "reporting_framework": "IFRS"}
    }
    text = """sharia wakala sukuk
    for the year ended 31 December 2023
    in accordance with IFRS as adopted by QCB (Islamic)"""
    ad.apply_detected_metadata(filing, text)
    # Operator's choices preserved verbatim.
    assert filing["metadata"]["sector"] == "other"
    assert filing["metadata"]["fiscal_period"] == "H1"
    assert filing["metadata"]["reporting_framework"] == "IFRS"


def test_apply_fills_empty_fields():
    filing = {
        "metadata": {"symbol": "ABCD"}      # sector/period/framework all None
    }
    text = """Takaful Islamic Insurance Company Wakala Tabarru'
    for the year ended 31 December 2023
    in accordance with IFRS as adopted by QCB (Islamic)"""
    ad.apply_detected_metadata(filing, text)
    meta = filing["metadata"]
    assert meta["sector"] in ("insurance",)         # takaful + tabarru → insurance
    assert meta["fiscal_period"] == "FY"
    assert meta["reporting_framework"] == "IFRS as adopted by QCB (Islamic)"
    # Operator's symbol preserved.
    assert meta["symbol"] == "ABCD"


def test_apply_skipped_when_unresolvable():
    filing = {"metadata": {"sector": None, "fiscal_period": None,
                              "reporting_framework": None}}
    # No text, no signals — fields stay None.
    ad.apply_detected_metadata(filing, "")
    assert filing["metadata"]["sector"] is None
    assert filing["metadata"]["fiscal_period"] is None
    assert filing["metadata"]["reporting_framework"] is None


def test_apply_picks_up_audit_verbatim_text():
    """When the caller passes page_text=None, we should still find the
    audit's verbatim_text and use it."""
    filing = {"metadata": {},
              "audit": {"verbatim_text": "for the year ended 31 December 2022 "
                                           "in accordance with IFRS"},
              "statements": []}
    ad.apply_detected_metadata(filing)
    meta = filing["metadata"]
    assert meta["fiscal_period"] == "FY"
    assert meta["reporting_framework"] == "IFRS"
