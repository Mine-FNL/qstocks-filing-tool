"""Pins `qscreen_gates.gate_post_extract` behaviour."""

from __future__ import annotations

import copy

import pytest

import qscreen_gates as gates


def _good_bs(
    total_assets: float = 1000.0, total_liab: float = 700.0, total_equity: float = 300.0
) -> dict:
    return {
        "metadata": {"symbol": "ABCD", "fiscal_year": 2024, "currency": "USD", "unit_scale": 1000},
        "statements": [
            {
                "type": "balance_sheet",
                "title": "Statement of Financial Position",
                "period_label": "FY 2024",
                "line_items": [
                    {
                        "account_code": c,
                        "value": v,
                        "comparatives": [],
                        "depth": 0,
                        "is_subtotal": False,
                    }
                    for c, v in (
                        ("BS_TOTAL_ASSETS", total_assets),
                        ("BS_TOTAL_LIABILITIES", total_liab),
                        ("BS_TOTAL_EQUITY", total_equity),
                    )
                ],
            },
        ],
    }


def _good_is(rev: float = 1000.0, cogs: float = 700.0, gp: float | None = 300.0) -> dict:
    items = [("IS_REVENUE", rev), ("IS_COST_OF_SALES", cogs)]
    if gp is not None:
        items.append(("IS_GROSS_PROFIT", gp))
    f = _good_bs()
    f["statements"].append(
        {
            "type": "income_statement",
            "title": "Income Statement",
            "period_label": "FY 2024",
            "line_items": [
                {
                    "account_code": c,
                    "value": v,
                    "comparatives": [],
                    "depth": 0,
                    "is_subtotal": False,
                }
                for c, v in items
            ],
        }
    )
    return f


# ── skeleton ────────────────────────────────────────────────────────────────


def test_good_filing_passes_skeleton_check():
    f = _good_is()
    g = gates.gate_post_extract(f)
    rules = {x.rule for x in g.findings}
    assert "skeleton_high_null_rate" not in rules
    assert "skeleton_empty" not in rules


def test_blank_filing_blocked_for_skeleton():
    f = _good_bs()
    # Replace every line-item value with None.
    for st in f["statements"]:
        for li in st["line_items"]:
            li["value"] = None
    g = gates.gate_post_extract(f)
    assert g.blocked is True
    rules = [x.rule for x in g.findings if x.severity == "block_save"]
    assert "skeleton_high_null_rate" in rules


def test_empty_filing_blocked_for_skeleton():
    f = {"metadata": {}, "statements": []}
    g = gates.gate_post_extract(f)
    assert g.blocked is True
    rules = {x.rule for x in g.findings}
    assert "skeleton_empty" in rules


# ── balance sheet identity ──────────────────────────────────────────────────


def test_balance_sheet_balances_passes():
    g = gates.gate_post_extract(_good_bs())
    assert all(x.rule != "bs_identity_a_le_q" for x in g.findings)


def test_balance_sheet_off_by_2pct_warns():
    f = _good_bs(total_assets=1000.0, total_liab=700.0, total_equity=280.0)  # total 980
    g = gates.gate_post_extract(f)
    by_rule = {x.rule: x for x in g.findings}
    assert "bs_identity_a_le_q" in by_rule
    assert by_rule["bs_identity_a_le_q"].severity == "warn"


def test_balance_sheet_off_by_5pct_still_warns_but_within_tolerance():
    # 5 % off would NOT pass the test the off-by-2 one does — that's the
    # whole point of the 1 % / 50 abs tolerance: 5 % IS worth flagging.
    f = _good_bs(total_assets=1000.0, total_liab=900.0, total_equity=0.0)
    g = gates.gate_post_extract(f)
    # Actually under 1% relative — 1000 vs 900 → 10% off, definitely a warning.
    by_rule = {x.rule: x for x in g.findings}
    assert "bs_identity_a_le_q" in by_rule


def test_balance_sheet_rounding_within_absolute_tolerance_ignored():
    # imbalanced by 30 on a 200 000 base: within 50 abs tolerance.
    f = _good_bs(total_assets=200_000.0, total_liab=130_000.0, total_equity=70_030.0)
    g = gates.gate_post_extract(f)
    assert all(x.rule != "bs_identity_a_le_q" for x in g.findings)


def test_missing_bs_legs_no_warning():
    f = {
        "metadata": {},
        "statements": [
            {
                "type": "balance_sheet",
                "title": "BS",
                "period_label": "FY",
                "line_items": [
                    {
                        "account_code": "BS_TOTAL_ASSETS",
                        "value": 1000.0,
                        "comparatives": [],
                        "depth": 0,
                        "is_subtotal": False,
                    }
                ],
            }
        ],
    }
    g = gates.gate_post_extract(f)
    assert all(x.rule != "bs_identity_a_le_q" for x in g.findings)


# ── income statement subtotals ──────────────────────────────────────────────


def test_gross_profit_off_warns():
    f = _good_is(rev=1000.0, cogs=700.0, gp=350.0)  # expected 300
    g = gates.gate_post_extract(f)
    rules = {x.rule for x in g.findings}
    assert "is_subtotal_is_gross_profit" in rules


def test_gross_profit_within_tolerance():
    f = _good_is(rev=1000.0, cogs=700.0, gp=305.0)
    g = gates.gate_post_extract(f)
    assert all(x.rule != "is_subtotal_is_gross_profit" for x in g.findings)


# ── metadata sanity ─────────────────────────────────────────────────────────


def test_bad_currency_shape_warns():
    f = _good_bs()
    f["metadata"]["currency"] = "Qatari Riyal"  # not ISO-4217-shaped
    g = gates.gate_post_extract(f)
    assert {x.rule for x in g.findings} >= {"metadata_currency_shape"}


def test_bad_unit_scale_warns():
    f = _good_bs()
    f["metadata"]["unit_scale"] = 100
    g = gates.gate_post_extract(f)
    assert {x.rule for x in g.findings} >= {"metadata_unit_scale"}


def test_null_currency_is_fine():
    f = _good_bs()
    f["metadata"]["currency"] = None  # under-determined; not bad
    g = gates.gate_post_extract(f)
    assert all(x.rule != "metadata_currency_shape" for x in g.findings)


# ── merge_warnings ──────────────────────────────────────────────────────────


def test_merge_warnings_appends_strings_and_dicts():
    f = _good_bs()
    g = gates.gate_post_extract(_good_is(rev=1000.0, cogs=700.0, gp=9999.0))
    before = list(f.get("extraction_quality", {}).get("warnings", []))
    gates.merge_warnings(f, g)
    after = f["extraction_quality"]["warnings"]
    assert len(after) >= len(before)
    # Dict-form warnings carry {rule, severity, message}
    assert any(isinstance(x, dict) and "rule" in x for x in after)
