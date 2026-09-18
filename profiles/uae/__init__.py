"""UAE (ADX / DFM) per-stock knowledge base — STUB.

Status
------
This is a *stub* profile. The structure is in place so that
``build_profile(ticker)`` returns a sane ``Profile`` object for the UAE
markets, but the data tables (sub-sector taxonomy, fiscal calendar,
auditor history, pre-flag rules) are **not** populated. The engine
will work end-to-end on a UAE filing with the autodetected
defaults, but the issuer-specific pre-flag rules (which catch UDCD's
intangibles ceiling, ZHCD's auditor history, QIGD's rename history,
etc.) are not yet authored for the UAE equivalent tickers.

Roadmap
-------
v1.7.0 (target): populate ``_seed.py`` for the top 30 ADX + DFM
listed equities, mirror the pre-flag catalog from
``profiles/qatar/pre_flags.py``, and run the bench on the resulting
golden-set cases.

Public API
----------
The shape mirrors ``profiles.qatar`` so callers can swap
``--jurisdiction qatar`` for ``--jurisdiction uae`` without code
changes.
"""

from __future__ import annotations

from typing import Any

JURISDICTION_NAME: str = "UAE"

# Recognised exchanges
EXCHANGES: tuple[str, ...] = ("ADX", "DFM")

# Reporting regime: ADX + DFM require IFRS or IFRS-for-SME; UAE also
# recognises AAOIFI for Islamic-institution filings.
FRAMEWORKS: tuple[str, ...] = ("IFRS", "IFRS-for-SME", "AAOIFI")

# Default currency
CURRENCY: str = "AED"

# Sector taxonomy mirrors Qatar's QSE taxonomy for cross-jurisdiction
# comparability. Adding sector-specific overrides is part of v1.7.0.
SECTORS: tuple[str, ...] = (
    "conventional_bank",
    "islamic_bank",
    "industrial",
    "insurance",
    "real_estate",
    "holding",
    "other",
)

# Sub-sector → archetype mapping (placeholder — fill in v1.7.0)
SUBSECTOR_TO_ARCHETYPE: dict[str, str] = {
    # e.g.  "real_estate_developer": "real_estate",
}

# Issuer list (placeholder — fill in v1.7.0)
COMPANY_NAMES: dict[str, str] = {
    # e.g.  "EMIRATES": "Emirates NBD Bank PJSC",
}

# Watch KPIs (placeholder — fill in v1.7.0 from each issuer's annual
# report + IR website)
WATCH_KPIS: dict[str, list[str]] = {
    # e.g.  "EMIRATES": ["NIM", "CET1", "LCR", "Cost-to-income"],
}

# Per-issuer enrichment (placeholder — fill in v1.7.0)
ENRICH: dict[str, dict[str, Any]] = {
    # e.g.  "EMIRATES": {"framework": "IFRS", "fy_end": "12-31"},
}


def all_tickers() -> list[str]:
    """Return the sorted list of known UAE tickers."""
    return sorted(COMPANY_NAMES.keys())


def build_profile(ticker: str) -> dict[str, Any] | None:
    """Return the static profile for ``ticker`` or ``None`` if unknown.

    Note: until v1.7.0 lands, this returns ``None`` for all tickers
    except the (empty) UAE list — the engine falls back to autodetected
    defaults when ``build_profile`` returns ``None``.
    """
    if ticker not in COMPANY_NAMES:
        return None
    return {
        "ticker": ticker,
        "name": COMPANY_NAMES[ticker],
        "jurisdiction": JURISDICTION_NAME,
        "sector": ENRICH.get(ticker, {}).get("sector", "other"),
        "framework": ENRICH.get(ticker, {}).get("framework", "IFRS"),
        "currency": CURRENCY,
        "fiscal_year_end": ENRICH.get(ticker, {}).get("fy_end", "12-31"),
        "watch_kpis": WATCH_KPIS.get(ticker, []),
    }


def profile_for_year(ticker: str, fiscal_year: int) -> dict[str, Any] | None:
    """Return the profile resolved as-of ``fiscal_year``.

    Currently a thin alias for ``build_profile`` (UAE filings have not
    accumulated enough temporal variance to need a per-year resolution
    yet). Will become meaningful in v1.7.0 as the ENRICH table grows.
    """
    return build_profile(ticker)


def taxonomy() -> dict[str, str]:
    """Return the SUBSECTOR → ARCHETYPE mapping."""
    return SUBSECTOR_TO_ARCHETYPE


def symbol_subsector() -> dict[str, str]:
    """Return the SYMBOL → SUBSECTOR mapping (placeholder)."""
    return {}


def subsector_to_archetype() -> dict[str, str]:
    """Return the SUBSECTOR → ARCHETYPE mapping."""
    return SUBSECTOR_TO_ARCHETYPE


def export_json(target_dir: str) -> int:
    """Write ``profiles/uae/data/<TICKER>.json`` for every known ticker.

    Returns the count of files written. Currently zero (empty ticker
    list); will be ~30 in v1.7.0.
    """
    import json
    from pathlib import Path

    out_dir = Path(target_dir) / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for ticker in all_tickers():
        profile = build_profile(ticker)
        if profile is None:
            continue
        (out_dir / f"{ticker}.json").write_text(json.dumps(profile, indent=2, ensure_ascii=False))
        n += 1
    return n
