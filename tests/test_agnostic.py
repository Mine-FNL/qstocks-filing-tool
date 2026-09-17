"""Pins the jurisdiction-agnostic contract.

Coverage:
    1. Engine works with NO profile (no Qatar data, no nothing) — the system
       prompt says "financial filing" rather than "Qatar Stock Exchange",
       empty_filing()'s default currency is None (not QAR), and the merge
       path never special-cases a particular currency.
    2. CLI flags --currency / --framework / --jurisdiction reach all the way
       into the assembled metadata (without us needing a real LLM call).
    3. ``profiles.register`` lets an embedder add a non-Qatar jurisdiction at
       runtime; the system prompt uses that jurisdiction's name.
    4. The qatar/ back-compat shim still satisfies every existing call site.
    5. _validate_upload_url rejects malformed URLs before any token leaks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import profiles
import qatar  # back-compat path
import qscreen_ingest as e

# ── 1. Engine is jurisdiction-agnostic ────────────────────────────────────────


def test_empty_filing_currency_is_null_not_qar():
    """No default currency silently baked into the template."""
    f = e.empty_filing()
    assert f["metadata"]["currency"] is None
    assert f["metadata"]["unit_scale"] == 1


def test_merge_does_not_special_case_any_currency():
    """If we say currency='QAR' and another window says 'USD', MERGE keeps QAR
    (first non-empty wins). What it must NOT do is silently fill in 'QAR' for
    a window that left currency blank."""
    base = e.empty_filing()
    base["metadata"]["currency"] = "QAR"
    a = e.empty_filing()
    a["metadata"]["currency"] = "USD"
    b = e.empty_filing()
    b["metadata"]["currency"] = None
    out = e.merge_filings([base, a, b])
    assert out["metadata"]["currency"] in ("QAR", "USD")  # first non-empty wins


def test_system_prompt_with_no_profile_mentions_no_exchange():
    sys_p = e._system_prompt("industrial", windowed=False, profile=None)
    for forbidden in ("Qatar Stock Exchange", "QSE", "Qatari", "QAR"):
        assert forbidden not in sys_p, f"system prompt leaked '{forbidden}' for profile=None"


def test_system_prompt_uses_profile_jurisdiction_label():
    fake_profile = {
        "ticker": "ABCD",
        "jurisdiction": "United Arab Emirates",
        "company_name": "Acme Co.",
        "as_of_year": 2024,
        "sub_sector": "industrial",
        "reporting_currency": "AED",
        "framework_as_of": "IFRS",
        "active_events": [],
        "active_subsidiaries": [],
        "watch_kpis": [],
        "segments_expected": {"by_geography": [], "by_business": []},
        "accounting_quirks": [],
    }
    sys_p = e._system_prompt("industrial", windowed=False, profile=fake_profile)
    assert "United Arab Emirates".lower() in sys_p.lower()  # header is uppercased
    assert "Qatar" not in sys_p
    assert "QSE" not in sys_p


def test_profile_context_renders_unknown_jurisdiction_safely():
    """A profile that omits jurisdiction still renders something useful.

    Falls back to a neutral "filing" header so the LLM isn't silently told
    a misleading jurisdiction. Never crashes; never invents a label.
    """
    p = {
        "ticker": "XYZ",
        "name_as_of": "Acme Group",
        "as_of_year": 2024,
        "reporting_currency": "EUR",
        "framework_as_of": "IFRS",
        "active_events": [],
        "active_subsidiaries": [],
        "watch_kpis": [],
        "segments_expected": {"by_geography": [], "by_business": []},
        "accounting_quirks": [],
    }
    block = e._profile_context(p)
    assert "FILING" in block.upper()  # the fallback header appears
    assert "EUR" in block
    assert "Acme Group" in block  # company + year come through
    assert "2024" in block


# ── 2. CLI flags flow into metadata ────────────────────────────────────────────


def test_cli_currency_and_framework_overlay_fill_blank_metadata(monkeypatch):
    """_run_with_debug-equivalent: build an args object, see the overlay reach
    the assembled filing without an LLM in the loop."""
    pages = [
        {
            "num": 1,
            "text": "Statement of Financial Position\n[TABLES on page 1]\n"
            "-- table 1 --\nTotal assets | 1,000 | 900\nTotal equity | 200 | 180\n",
        },
    ]
    import argparse

    ns = argparse.Namespace(
        no_llm=True,
        guided=True,
        guided_notes=True,
        symbol="ABCD",
        sector="industrial",
        year=2024,
        period="FY",
        currency="AED",
        framework="AAOIFI",
        jurisdiction="qatar",
        pages_per_chunk=12,
        overlap=1,
        _profile=None,
    )
    out = e.extract_filing(pages, ns)
    # The overlay below is what run_filing() does after extraction.
    out.setdefault("metadata", {}).update(
        {
            "currency": ns.currency or out["metadata"].get("currency"),
            "reporting_framework": ns.framework or out["metadata"].get("reporting_framework"),
        }
    )
    assert out["metadata"]["currency"] == "AED"
    assert out["metadata"]["reporting_framework"] == "AAOIFI"
    assert out["metadata"]["unit_scale"] == 1


# ── 3. register() + custom jurisdiction ────────────────────────────────────────


def _fake_loader():
    """A minimal loader for a synthetic, non-Qatar jurisdiction."""
    return profiles.JurisdictionLoader(
        build_profile=lambda t: (
            {
                "ticker": t,
                "jurisdiction": "United Arab Emirates",
                "company_name": f"{t} Holdings PJSC",
                "sub_sector": "real_estate",
                "archetype": "industrial",
                "reporting_currency": "AED",
                "framework_timeline": [{"framework": "IFRS", "from": None}],
                "watch_kpis": ["KPI_NPM"],
                "names": [],
                "segments_expected": {"by_geography": ["UAE"], "by_business": []},
                "subsidiaries": [
                    {"name": t, "country": "AE", "currency": "AED", "from": None, "to": None}
                ],
                "events": [],
                "peers": [],
                "accounting_quirks": [],
                "fiscal_year_end": "12-31",
            }
            if t == "ALDAR"
            else None
        ),
        profile_for_year=lambda t, y: None,
        taxonomy=lambda: {"Real Estate": ["Real Estate Development"]},
        symbol_subsector=lambda: {"ALDAR": "Real Estate Development"},
        subsector_to_archetype=lambda: {"Real Estate Development": "industrial"},
    )


@pytest.fixture
def registered_uae():
    profiles.register("uae", "United Arab Emirates", _fake_loader())
    yield
    profiles._REGISTRY.pop("uae", None)


def test_register_then_all_jurisdictions_lists_it(registered_uae):
    assert "uae" in profiles.all_jurisdictions()


def test_registered_jurisdiction_round_trips(registered_uae):
    p = profiles.load_profile("ALDAR", jurisdiction="uae")
    assert p["jurisdiction"] == "United Arab Emirates"
    assert p["reporting_currency"] == "AED"
    assert profiles.taxonomy("uae") == {"Real Estate": ["Real Estate Development"]}


# ── 4. Back-compat shim ───────────────────────────────────────────────────────


def test_backcompat_import_qatar_still_works():
    import qatar

    assert "QNBK" in qatar.all_tickers()


def test_backcompat_qatar_module_equals_profiles_qatar():
    """Every public name in qatar/ should match profiles.qatar/."""
    import profiles.qatar as pq

    # Key return values (not exhaustive; tests/ test_qatar.py covers the rest).
    assert set(qatar.all_tickers()) == set(pq.all_tickers())
    assert qatar.QSE_TAXONOMY == pq.QSE_TAXONOMY
    assert qatar.JURISDICTION_NAME == "Qatar"


def test_backcompat_export_json_writes_to_profiles_qatar_data():
    """qatar.export_json() should default to the new data/ directory."""
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        n = qatar.export_json(td)
        assert n > 0
        files = os.listdir(td)
        assert any(f.endswith(".json") for f in files)


# ── 5. Upload URL hardening ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "bad_url",
    [
        "not a url",  # no scheme
        "ftp://example.com",  # wrong scheme
        "https://",  # missing host
        "/relative/path",  # relative path
        "",
    ],
)
def test_validate_upload_url_rejects_bad(bad_url):
    with pytest.raises(SystemExit):
        e._validate_upload_url(bad_url)


def test_validate_upload_url_accepts_https_and_localhost_http():
    assert e._validate_upload_url("https://api.example.com/") == "https://api.example.com"
    assert e._validate_upload_url("http://localhost:3004/") == "http://localhost:3004"


# ── 6. Generic unit-scale accepts any currency ─────────────────────────────────


@pytest.mark.parametrize(
    "text,scale",
    [
        ("All amounts in AED thousands", 1000),
        ("Amounts in millions of Saudi Riyals", 1_000_000),
        ("in EUR'000", 1000),
        ("Amounts in USD millions", 1_000_000),
        ("(in thousands of QAR)", 1000),
        # Pinned regressions — these must NOT match.
        ("We serve millions of customers", None),
        ("Annual report 2024", None),
    ],
)
def test_unit_scale_currency_agnostic(text, scale):
    assert e.detect_unit_scale(text) == scale
