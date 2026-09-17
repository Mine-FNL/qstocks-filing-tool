"""Pins `profiles.qatar.pre_flags.run_pre_flags` behaviour."""

from __future__ import annotations

import pytest

from profiles.qatar import pre_flags

# ── helpers ──────────────────────────────────────────────────────────────────


def _li(code: str, value, comparatives=None):
    return {
        "account_code": code,
        "value": value,
        "comparatives": comparatives or [],
        "depth": 0,
        "is_subtotal": False,
    }


def _filing(meta=None, statements=None, audit=None, notes=None):
    return {
        "metadata": meta or {},
        "statements": statements or [],
        "audit": audit or {},
        "notes": notes or [],
    }


# ── snapshot / dispatch ─────────────────────────────────────────────────────


def test_empty_filing_emits_no_flags():
    out = pre_flags.run_pre_flags({})
    assert out == []


# ── issuer-specific facts ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "ticker,year",
    [
        ("ZHCD", 2018),  # 8 of 10+ years qualified → flag
        ("DUBK", 2021),  # intangibles M&A goodwill
        ("UDCD", 2016),  # IP at 47% of TA
        ("VFQS", 2013),  # FYE change Mar→Dec
        ("QETF", 2020),  # passive index ETF, P/B = 1.0x
    ],
)
def test_issuer_facts_surface_for_known_tickers(ticker, year):
    f = _filing(
        meta={
            "symbol": ticker,
            "fiscal_year": year,
            "sector": "conventional_bank",
            "fiscal_period": "FY",
        }
    )
    flags = pre_flags.run_pre_flags(f)
    assert flags, "expected an issuer-specific flag for %s %d" % (ticker, year)
    ids = {x.rule_id for x in flags}
    assert any(x.startswith("issuer_fact_") for x in ids)


def test_issuer_fact_does_not_fire_for_unknown_ticker():
    f = _filing(meta={"symbol": "ABCD", "fiscal_year": 2024, "fiscal_period": "FY"})
    flags = pre_flags.run_pre_flags(f)
    assert not any(x.rule_id.startswith("issuer_fact_") for x in flags)


# ── issuer renames (the special-table dispatch) ──────────────────────────────


def test_vfqs_fye_change_note_surfaces():
    f = _filing(meta={"symbol": "VFQS", "fiscal_year": 2013, "fiscal_period": "FY"})
    flags = pre_flags.run_pre_flags(f)
    notes = [x for x in flags if x.rule_id == "issuer_renamed_history"]
    assert notes and "9-month transition" in notes[0].message


# ── cross-cutting: going concern ────────────────────────────────────────────


def test_going_concern_flag_emitted_when_present():
    f = _filing(
        meta={"symbol": "QGMD", "fiscal_year": 2021, "fiscal_period": "FY"},
        audit={
            "opinion_type": "qualified",
            "material_uncertainty_going_concern": {
                "present": True,
                "text": "Material uncertainty …",
            },
        },
    )
    flags = pre_flags.run_pre_flags(f)
    rules = {x.rule_id for x in flags}
    assert "xcut_going_concern_structural_2y" in rules


def test_going_concern_rule_does_not_fire_when_absent():
    f = _filing(
        meta={"symbol": "QGMD", "fiscal_year": 2021, "fiscal_period": "FY"},
        audit={"opinion_type": "unqualified"},
    )
    flags = pre_flags.run_pre_flags(f)
    rules = {x.rule_id for x in flags}
    assert "xcut_going_concern_structural_2y" not in rules


# ── cross-cutting: insurer technical reserves ────────────────────────────────


def test_qualified_insurer_with_reserves_flag():
    f = _filing(
        meta={"symbol": "DOHI", "sector": "insurance", "fiscal_year": 2022, "fiscal_period": "FY"},
        audit={
            "opinion_type": "qualified",
            "key_audit_matters": [
                {
                    "title": "IBNR / technical reserves",
                    "text": "the completeness of IBNR is a key audit matter",
                }
            ],
        },
    )
    flags = pre_flags.run_pre_flags(f)
    rules = {x.rule_id for x in flags}
    assert "xcut_insurer_qualified_review_technical_reserves" in rules


def test_qualified_insurer_without_reserves_does_not_fire():
    f = _filing(
        meta={"symbol": "DOHI", "sector": "insurance", "fiscal_year": 2022, "fiscal_period": "FY"},
        audit={
            "opinion_type": "qualified",
            "key_audit_matters": [{"title": "Other matter", "text": ""}],
        },
    )
    flags = pre_flags.run_pre_flags(f)
    rules = {x.rule_id for x in flags}
    assert "xcut_insurer_qualified_review_technical_reserves" not in rules


# ── cross-cutting: AFS dominates NI / equity ────────────────────────────────


def test_afs_dominates_ni_when_large_ratio():
    f = _filing(
        meta={"symbol": "QATI", "sector": "insurance", "fiscal_year": 2022, "fiscal_period": "FY"},
        statements=[
            {
                "type": "balance_sheet",
                "title": "BS",
                "period_label": "FY",
                "line_items": [
                    _li("BS_AFS_RESERVE", -120_000),
                    _li("BS_TOTAL_EQUITY", 200_000),
                ],
            },
            {
                "type": "income_statement",
                "title": "IS",
                "period_label": "FY",
                "line_items": [
                    _li("IS_NET_INCOME", 200_000),
                ],
            },
        ],
    )
    flags = pre_flags.run_pre_flags(f)
    rules = {x.rule_id for x in flags}
    # 120k AFS reserve / 200k total equity = 60 % → "share of equity" rule.
    assert "xcut_aafs_share_of_equity" in rules
    # 120k AFS / 200k NI = 60 % → "dominates NI" rule also fires.
    assert "xcut_aafs_dominates_ni" in rules


def test_dual_income_statement_takaful():
    f = _filing(
        meta={
            "symbol": "QISI",
            "sector": "insurance",
            "sub_sector": "Takaful Insurance",
            "fiscal_year": 2022,
            "fiscal_period": "FY",
        },
        statements=[
            {
                "type": "income_statement",
                "title": "Policyholders IS",
                "period_label": "FY",
                "line_items": [],
            },
            {
                "type": "income_statement",
                "title": "Shareholders IS",
                "period_label": "FY",
                "line_items": [],
            },
        ],
    )
    flags = pre_flags.run_pre_flags(f)
    rules = {x.rule_id for x in flags}
    assert "xcut_dual_income_statement_takaful" in rules


# ── merge_into_filing idempotency ────────────────────────────────────────────


def test_merge_into_filing_idempotent():
    f = _filing(meta={"symbol": "ZHCD", "fiscal_year": 2020, "fiscal_period": "FY"})
    flags = pre_flags.run_pre_flags(f)
    pre_flags.merge_into_filing(f, flags)
    pre_flags.merge_into_filing(f, flags)
    rules = [x["rule"] for x in f["red_flags"]]
    assert len(rules) == len(set(rules)), "duplicate red_flags inserted"
    assert f["extraction_quality"]["pre_flag_count"] == len(flags)
