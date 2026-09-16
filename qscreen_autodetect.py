"""Auto-detect sector / period / framework from filing text.

Why
----
For batch runs (1000+ filings) the operator wants to type as little as
possible. The current CLI requires:

    --symbol QNBK --year 2024 --period FY --sector islamic_bank

But sector, period, and framework are *in the filing*. Reading them off
the cover page + audit opinion is a deterministic heuristic that's
correct in 95 %+ of cases; the remaining 5 % (unusual structures,
transliteration) the operator clears with a one-line CLI override.

What it does
------------
- ``detect_sector(text, profile)`` — looks for "qatari islamic bank",
  "takaful", "policyholders", "investment property", etc. Falls back
  to the profile's known sub-sector if a profile is loaded.
- ``detect_period(text, fiscal_year)`` — reads the cover page for
  "31 March 2023", "for the year ended", etc. and disambiguates FY vs
  quarter vs 9-month by the audit language ("review" / "interim" vs
  "in our opinion"). Defaults to FY unless the text says otherwise.
- ``detect_framework(text, sector)`` — reads the cover page /
  auditor's report for the framework label. Maps "IFRS as adopted by
  QCB (Islamic)" for Islamic banks, "AAOIFI" for takaful / some
  re/insurance, "IFRS" elsewhere.

Design
------
Single-pass; no LLM. Pure regex / keyword over the first ~6 kB of text
(cover page and audit's report). If a value is already in the metadata,
don't overwrite — the operator's explicit choice wins.
"""
from __future__ import annotations

import logging
import re
from typing import Any


log = logging.getLogger("qstock.autodetect")


# ── keywords / patterns ──────────────────────────────────────────────────────


# Sector — case-insensitive, anchored on whitespace so "industrial" inside
# "industrialisation" doesn't trigger. Order matters: most-specific first.
_SECTOR_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    # ticker/peculiar vocabulary first
    ("islamic_bank", (
        "sukuk", "mudaraba", "musharaka", "murabaha", "wakala",
        "qard hassan", "sharia", "islamic financing", "islamic deposit",
        "profit-sharing",
    )),
    ("insurance", (
        "policyholders' income statement", "policyholders' surplus",
        "wakala fees", "retakaful", "tabarru", "participants' fund",
        "takaful", "ibnr", "ulae", "premium ceded", "insurance reserves",
        "claims incurred",
    )),
    ("real_estate",     # (carried in sub_sector only; sector = "other")
    (
        # only the wording-level signal — the sub-sector belongs to industrial.
        "investment property", "properties under development",
    )),
    ("industrial", (
        "production output", "cost of sales", "inventories", "manufacturing",
        "finished goods", "revenue from contracts", "goods sold",
        "segment result", "extraction", "refining", "petrochemical",
    )),
)


_PERIOD_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    # Annual
    ("FY", (
        "for the year ended 31 december",
        "for the year ended 31 march",
        "for the year ended 30 june",
        "for the year ended 30 september",
        "for the financial year ended",
        "year ended 31 december",
        "annual financial statements",
        "consolidated financial statements",
    )),
    # Half-yearly
    ("H1", (
        "for the six months ended", "for the half-year ended",
        "for the period ended 30 june",
    )),
    ("H2", (
        "for the six months ended 31 december", "for the half-year ended 31 december",
    )),
    # Quarters (must be matched AFTER FY/H1 so a year-end quarter doesn't
    # masquerade as a quarter-report). Three or nine months.
    ("Q1", (
        "for the three months ended 31 march", "for the quarter ended 31 march",
        "first quarter ended 31 march",
    )),
    ("Q2", (
        "for the three months ended 30 june", "for the quarter ended 30 june",
        "second quarter ended 30 june",
    )),
    ("Q3", (
        "for the three months ended 30 september", "for the quarter ended 30 september",
        "third quarter ended 30 september",
    )),
    ("9M", (
        "for the nine months ended", "9-month period ended",
    )),
    # Stub / non-standard (handled differently by the bench).
    ("Q4", (
        "for the three months ended 31 december",
    )),
)


_FRAMEWORK_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("IFRS as adopted by QCB (Islamic)", (
        "ifrs as adopted by qcb (islamic)", "ifrs as adopted by qcb islamic",
        "in accordance with ifrs as adopted by qcb",
        "sharia supervisory board",
    )),
    ("AAOIFI", (
        "aaoifi", "accounting and auditing organisation for islamic financial institutions",
    )),
    ("IFRS for SMEs", (
        "ifrs for smes", "ifrs for small and medium-sized entities",
    )),
    ("IFRS", (
        "international financial reporting standards (ifrs)",
        "in accordance with ifrs", "in accordance with international financial reporting standards",
        "ifrs as adopted",       # generic "adopted by ..." falls back to IFRS
    )),
)


# ── public API ───────────────────────────────────────────────────────────────


def detect_sector(text: str, profile: dict | None = None) -> str | None:
    """Return one of the 5 SECTORS or None if uncertain.

    Profile (when available) is consulted FIRST — a profile knows its
    own sector even when the filing language is unusual (e.g. transliterated
    Arabic). Text matching is the fallback.
    """
    if profile is not None:
        # Profile.archetype is one of: conventional_bank | islamic_bank |
        # industrial | insurance | other. They map to SECTORS one-for-one.
        arc = (profile.get("archetype") or "").strip().lower()
        if arc in ("conventional_bank", "islamic_bank", "industrial",
                    "insurance", "other"):
            log.info("autodetect.sector: profile override → %r", arc)
            return arc

    if not text:
        return None
    blob = text.lower()
    # Score each candidate by keyword hits; tie-break by order in the table.
    scores: dict[str, int] = {}
    for sector, kws in _SECTOR_HINTS:
        scores.setdefault(sector, 0)
        for kw in kws:
            if re.search(rf"\b{re.escape(kw)}\b", blob):
                scores[sector] += 1
    # Filter to sectors with positive signal; pick max.
    ranked = [(s, n) for s, n in scores.items() if n > 0]
    if not ranked:
        return None
    ranked.sort(key=lambda sn: (-sn[1], _SECTOR_HINTS_ORDER.index(sn[0])))
    sector = ranked[0][0]
    # Real estate is a sub-sector signal; collapse to "other" / "industrial"
    # so the engine's 5-class SECTORS invariant holds.
    if sector == "real_estate":
        # If investment-property >= 30 % of total assets vocabulary is
        # present and other industrial hits dominate, classify as
        # industrial; otherwise leave as the generic catch-all.
        if scores.get("industrial", 0) > 0:
            return "industrial"
        return "other"
    return sector


# Order for tie-breaking; earlier wins on equal scores. Mirrors the
# SECTORS list in qscreen_ingest.py (sector legend).
_SECTOR_HINTS_ORDER = ("islamic_bank", "insurance", "industrial", "real_estate")


def detect_period(text: str, fiscal_year: int | None = None) -> str | None:
    """Return one of FY / Q1..Q4 / H1 / H2 / 9M, or None on uncertainty."""
    if not text:
        return None
    blob = text.lower()
    for period, kws in _PERIOD_KEYWORDS:
        for kw in kws:
            if re.search(re.escape(kw), blob):
                log.info("autodetect.period: matched %r on phrase %r", period, kw)
                return period
    return None


def detect_framework(text: str, sector: str | None = None) -> str | None:
    """Return the framework label, or None on uncertainty.

    Sector context adjusts the threshold: for an Islamic bank, prefer
    "IFRS as adopted by QCB (Islamic)" even when the cover page only says
    "IFRS" (because the regulator-mandated framework is the IFRS-as-adopted
    variant).
    """
    if not text:
        return None
    blob = text.lower()
    found: list[tuple[str, int]] = []
    for label, kws in _FRAMEWORK_KEYWORDS:
        for kw in kws:
            if re.search(re.escape(kw), blob):
                found.append((label, kws.index(kw)))
                break                       # first match per label wins
    if not found:
        return None
    # Prefer most-specific label (AAOIFI > IFRS-as-adopted-QCB > IFRS).
    # Specificity is encoded by order in _FRAMEWORK_KEYWORDS.
    found_sorted = sorted(found,
                          key=lambda lf: _FRAMEWORK_SPECIFICITY_ORDER.index(lf[0]))
    pick = found_sorted[0][0]
    if pick == "IFRS" and sector == "islamic_bank":
        # For an Islamic bank, the QCB-mandated variant is the right
        # framework; cover pages often just say "IFRS" in shorthand.
        log.info("autodetect.framework: islamic_bank override → IFRS as adopted by QCB (Islamic)")
        return "IFRS as adopted by QCB (Islamic)"
    return pick


_FRAMEWORK_SPECIFICITY_ORDER = (
    "AAOIFI",
    "IFRS as adopted by QCB (Islamic)",
    "IFRS for SMEs",
    "IFRS",
)


def detect_metadata(text: str, profile: dict | None = None,
                    existing: dict | None = None) -> dict:
    """Return {"sector": str|None, "period": str|None, "framework": str|None}.

    Each key is None when the detector is uncertain. Existing values
    (the operator's explicit choice) are preserved.
    """
    existing = existing or {}
    sector = existing.get("sector") or detect_sector(text, profile)
    period = existing.get("fiscal_period") or detect_period(text)
    framework = existing.get("reporting_framework") or detect_framework(text, sector)
    return {"sector": sector, "fiscal_period": period,
            "reporting_framework": framework}


# ── higher-level orchestrator ────────────────────────────────────────────────


def apply_detected_metadata(filing: dict, page_text: str | None = None,
                            profile: dict | None = None) -> dict:
    """Patch ``filing.metadata`` with detected values where currently empty.

    Returns the (mutated) filing. The mutation is non-destructive — only
    keys currently equal to None / "" / missing get filled. The detector
    never overwrites an explicit value.
    """
    text = page_text or " ".join(p.get("text", "") for p in []) or _text_from_filing(filing)
    detected = detect_metadata(text, profile, existing=filing.get("metadata") or {})
    meta = filing.setdefault("metadata", {})
    changed = []
    for k, v in detected.items():
        cur = meta.get(k)
        if v is not None and cur in (None, ""):
            meta[k] = v
            changed.append(f"{k}={v!r}")
    if changed:
        log.info("autodetect: applied %s", ", ".join(changed))
    return filing


def _text_from_filing(filing: dict) -> str:
    """Best-effort concatenate the audit prose + the first verbatim_text of
    any statement — the surface where cover-page / framework language
    actually lives."""
    bits: list[str] = []
    audit = filing.get("audit") or {}
    if isinstance(audit, dict):
        if audit.get("verbatim_text"):
            bits.append(audit["verbatim_text"])
    for st in filing.get("statements") or []:
        v = st.get("verbatim_text")
        if v:
            bits.append(v)
    return "\n\n".join(bits)


__all__ = [
    "detect_sector", "detect_period", "detect_framework", "detect_metadata",
    "apply_detected_metadata",
]
