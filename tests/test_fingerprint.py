"""Pins `qscreen_fingerprint` for stable hashing + filing-level diff."""
from __future__ import annotations

import pytest

import qscreen_fingerprint as fp


# ── text_fingerprint ────────────────────────────────────────────────────────


def test_text_fingerprint_stable_across_whitespace():
    a = "Total assets\n1,077,000 980,000"
    b = " Total assets  1,077,000 980,000 \n"
    assert fp.text_fingerprint(a) == fp.text_fingerprint(b)


def test_text_fingerprint_changes_on_content():
    assert fp.text_fingerprint("Total assets 1,077,000") != \
           fp.text_fingerprint("Total assets 1,078,000")


def test_text_fingerprint_empty():
    assert fp.text_fingerprint("") == ""
    assert fp.text_fingerprint("   \n  \t  ") == ""


def test_text_fingerprint_preserves_numbers():
    # Number formatting (commas) is NOT normalized away. Two filings that
    # differ in numeric formatting should be flagged as different.
    assert fp.text_fingerprint("1,000") != fp.text_fingerprint("1000")


# ── fingerprint_filing ─────────────────────────────────────────────────────


def test_fingerprint_filing_picks_up_audit_and_statements():
    f = {"metadata": {"symbol": "QNBK", "fiscal_year": 2024},
         "audit": {"verbatim_text": "In our opinion, the financial statements ..."},
         "statements": [
             {"type": "balance_sheet", "title": "BS",
                "verbatim_text": "Total assets 1,000 Equity 300"},
             {"type": "income_statement", "title": "IS",
                "verbatim_text": "Revenue 500 Net income 100"},
         ]}
    out = fp.fingerprint_filing(f, short_label="QNBK/2024")
    assert out["filing_id"] == "QNBK/2024"
    keys = {x["key"] for x in out["items"]}
    # audit + 2 statements = 3 items
    assert len(out["items"]) == 3
    assert "audit.verbatim_text" in keys
    assert "statements[0].balance_sheet.verbatim_text" in keys
    assert "statements[1].income_statement.verbatim_text" in keys
    # overall is the stable hash of all items
    assert isinstance(out["overall_fingerprint"], str) and len(out["overall_fingerprint"]) == 16


def test_fingerprint_filing_stable_under_reordering():
    """The overall fingerprint should be order-independent — re-running
    extraction with shuffled window order produces the same hash."""
    a = {"audit": {"verbatim_text": "audit"},
          "statements": [
              {"type": "balance_sheet", "verbatim_text": "BS contents"},
              {"type": "income_statement", "verbatim_text": "IS contents"},
          ]}
    b = dict(a)
    b["statements"] = list(reversed(a["statements"]))
    assert fp.fingerprint_filing(a)["overall_fingerprint"] == \
           fp.fingerprint_filing(b)["overall_fingerprint"]


def test_fingerprint_filing_skips_blank_verbatims():
    f = {"audit": {"verbatim_text": "   "},
          "statements": [{"type": "balance_sheet", "verbatim_text": ""}]}
    out = fp.fingerprint_filing(f)
    # Whitespace-only text counts as absent so the diff stays clean.
    assert out["items"] == []


def test_fingerprint_filing_includes_notes():
    f = {"audit": {}, "statements": [],
          "notes": [{"category": "audit_basis",
                       "verbatim_text": "Basis of qualified opinion ..."}]}
    out = fp.fingerprint_filing(f)
    assert len(out["items"]) == 1
    assert out["items"][0]["key"].startswith("notes[0].audit_basis")


# ── diff_fingerprints ───────────────────────────────────────────────────────


def test_diff_identical_when_no_changes():
    f = {"audit": {"verbatim_text": "audit v1"},
          "statements": [{"type": "balance_sheet", "verbatim_text": "BS v1"}]}
    a = fp.fingerprint_filing(f)
    b = fp.fingerprint_filing(f)
    d = fp.diff_fingerprints(a, b)
    assert d["identical"] is True
    assert d["added"] == []
    assert d["removed"] == []
    assert d["modified"] == []
    assert d["unchanged"] == len(a["items"])


def test_diff_detects_modified_statement():
    a = {"audit": {"verbatim_text": "v1"},
          "statements": [{"type": "balance_sheet", "verbatim_text": "BS v1"}]}
    b = {"audit": {"verbatim_text": "v1"},
          "statements": [{"type": "balance_sheet", "verbatim_text": "BS v2"}]}
    da = fp.fingerprint_filing(a)
    db = fp.fingerprint_filing(b)
    d = fp.diff_fingerprints(da, db)
    assert d["identical"] is False
    assert d["modified"] == ["statements[0].balance_sheet.verbatim_text"]


def test_diff_detects_added_statement():
    a = {"audit": {"verbatim_text": "v1"},
          "statements": [{"type": "balance_sheet", "verbatim_text": "BS"}]}
    b = {"audit": {"verbatim_text": "v1"},
          "statements": [{"type": "balance_sheet", "verbatim_text": "BS"},
                          {"type": "income_statement", "verbatim_text": "IS"}]}
    da = fp.fingerprint_filing(a)
    db = fp.fingerprint_filing(b)
    d = fp.diff_fingerprints(da, db)
    assert d["added"] == ["statements[1].income_statement.verbatim_text"]


def test_diff_detects_removed_statement():
    a = {"audit": {"verbatim_text": "v1"},
          "statements": [{"type": "balance_sheet", "verbatim_text": "BS"},
                          {"type": "income_statement", "verbatim_text": "IS"}]}
    b = {"audit": {"verbatim_text": "v1"},
          "statements": [{"type": "balance_sheet", "verbatim_text": "BS"}]}
    da = fp.fingerprint_filing(a)
    db = fp.fingerprint_filing(b)
    d = fp.diff_fingerprints(da, db)
    assert d["removed"] == ["statements[1].income_statement.verbatim_text"]


def test_diff_treats_null_files_as_empty():
    d = fp.diff_fingerprints(None, None)
    assert d["identical"] is True
    assert d["added"] == []
    assert d["removed"] == []
    assert d["unchanged"] == 0
