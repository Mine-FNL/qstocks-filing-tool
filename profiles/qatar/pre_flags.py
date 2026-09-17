"""Qatar-specific pre-flag catalog, machine-readable.

The QSE pre-flag knowledge has lived in ``memory/qse-filings-extraction.md``
for years. This module ports the catalog into Python so the engine can emit
``red_flags[]`` and ``extraction_quality.warnings`` automatically — instead
of expecting a downstream analyst to apply them by hand.

Schema
------
A rule is a small dataclass with:
    rule_id        — stable string for tests + log search
    applies        — predicate on the (ticker, sector, fiscal_year, fiscal_period)
    evaluate       — predicate on the merged filing
    severity       — "info" | "warn" | "block" (block is reserved for rules
                     that should veto the save, e.g. a 2x consecutive going-concern)
    message        — short, human-rendered note
    evidence_keys  — which filing fields are referenced in the message

A ``RedFlag`` is the result of evaluating one rule on one filing:
    rule_id, ticker, year, severity, message, evidence

The cross-cutting rules (govt-receivable, intangibles, ROE<Ke, etc.) are
issuer-agnostic and evaluate against any filing. The issuer-specific rules
encode deep knowledge that a vanilla LLM has never seen (ZHCD 8 of 10+ years
qualified, AKHI corpus misclassifies as islamic_bank, QIGD entity changed
3x via renames, UDCD IP at 47 % of TA, etc.).

Adding a rule
-------------
1. Pick a stable ``rule_id`` ("zhcd_qualified_baseline" — never reused).
2. Choose the ``applies`` predicate correctly; most issuer-specific rules
   are only meaningful after a known year (e.g. ``DUBK 2021+``).
3. Implement ``evaluate`` as a small pure function on the merged filing.
4. Add the test fixture in tests/test_pre_flags.py with a synthetic filing
   that triggers the rule, plus a synthetic filing that doesn't.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

# ── result + rule shape ──────────────────────────────────────────────────────


@dataclass
class RedFlag:
    rule_id: str
    ticker: str | None
    fiscal_year: int | None
    severity: str  # info | warn | block
    message: str
    evidence: dict = field(default_factory=dict)

    def to_warning(self) -> dict:
        return {
            "rule": self.rule_id,
            "severity": self.severity,
            "ticker": self.ticker,
            "fiscal_year": self.fiscal_year,
            "message": self.message,
            **self.evidence,
        }


@dataclass
class Rule:
    rule_id: str
    severity: str
    message: str
    applies: Callable[[FilingSnapshot], bool]
    evaluate: Callable[[FilingSnapshot], dict | None]
    issuer_specific: bool = False
    note: str = ""  # short citation back to the catalog


@dataclass
class FilingSnapshot:
    """Everything the rules need to look at, in one place.

    Built once per filing from the merged JSON. Pure data; no schema
    violations expected because gates run before this.
    """

    ticker: str | None
    sector: str | None
    fiscal_year: int | None
    fiscal_period: str | None
    reporting_currency: str | None
    reporting_framework: str | None
    sub_sector: str | None
    audit_opinion_type: str | None
    audit_material_uncertainty_going_concern: dict | None
    audit_key_audit_matters: list[dict]
    audit_emphasis_of_matter: list[str]
    line_items: list[dict]  # flat: every statement's items
    prior_line_items: list[dict] = field(default_factory=list)
    notes: list[dict] = field(default_factory=list)
    company_name: str | None = None
    raw: dict = field(default_factory=dict)  # the merged filing (for ad-hoc rules)


def build_snapshot(filing: dict) -> FilingSnapshot:
    meta = filing.get("metadata") or {}
    audit = filing.get("audit") or {}
    items = [li for st in (filing.get("statements") or []) for li in (st.get("line_items") or [])]
    notes = filing.get("notes") or []
    return FilingSnapshot(
        ticker=(meta.get("symbol") or "").upper() or None,
        sector=meta.get("sector"),
        fiscal_year=meta.get("fiscal_year"),
        fiscal_period=meta.get("fiscal_period"),
        reporting_currency=meta.get("currency"),
        reporting_framework=meta.get("reporting_framework"),
        sub_sector=meta.get("sub_sector"),
        audit_opinion_type=(audit.get("opinion_type") or None),
        audit_material_uncertainty_going_concern=audit.get("material_uncertainty_going_concern"),
        audit_key_audit_matters=audit.get("key_audit_matters") or [],
        audit_emphasis_of_matter=audit.get("emphasis_of_matter") or [],
        line_items=items,
        notes=notes,
        company_name=meta.get("company_name"),
        raw=filing,
    )


# ── small evaluator helpers ────────────────────────────────────────────────


def _li_value(snap: FilingSnapshot, code: str) -> float | None:
    """Latest-year value of an account code; the second of comparatives is
    reserved for prior-year access (not implemented here — kept simple)."""
    for li in snap.line_items:
        if li.get("account_code") == code:
            v = li.get("value")
            if v is None or v == "":
                return None
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
    return None


def _pct(numerator, denominator) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return 100.0 * numerator / denominator


def _li_yoy(snap: FilingSnapshot, code: str) -> tuple[float | None, float | None]:
    """Return (current, prior) for an account code from comparatives[0]."""
    for li in snap.line_items:
        if li.get("account_code") == code:
            v = li.get("value")
            try:
                cur = float(v) if v not in (None, "") else None
            except (TypeError, ValueError):
                cur = None
            comps = li.get("comparatives") or []
            pri = None
            if comps:
                try:
                    pri = float(comps[0].get("value"))
                except (TypeError, ValueError, IndexError):
                    pri = None
            return cur, pri
    return None, None


def _has_kam_with_phrase(snap: FilingSnapshot, phrase_re: str) -> bool:
    rx = re.compile(phrase_re, re.IGNORECASE)
    for kam in snap.audit_key_audit_matters:
        title = kam.get("title") or ""
        text = kam.get("text") or ""
        if rx.search(title) or rx.search(text):
            return True
    return False


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       Cross-cutting rules                                ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


def _rule_govt_qatar_receivable() -> Rule:
    """Government of Qatar receivable > 5 % of total assets → flag.

    Catalog: 'Government of Qatar receivable > 5% of total assets → flag'.
    """
    return Rule(
        rule_id="xcut_govt_qatar_receivable_5pct",
        severity="warn",
        message="Government of Qatar receivable >5% of total assets — counterparty risk.",
        applies=lambda s: bool(s.ticker and s.fiscal_year),
        evaluate=lambda s: (lambda: None)(),
    )


# The above is too coarse — we don't know the counterparty from the line
# items alone. The catalog rule is *intent* not *mechanizable* from the
# JSON. Keep it as a no-op stub for now; wire it through the audit-text
# scan if the notes mention "Government of Qatar".


def _rule_kam_intangibles_concentration() -> Rule:
    """KAM text mentions "intangibles"/"goodwill" + large absolute value.

    Catalog: 'IP at > 40% of TA → KAM-level for real estate; trading at
    < 0.6x book NAV + > 5% div yield = market pricing IP write-down'.
    """
    return Rule(
        rule_id="xcut_kam_intangibles_or_ip_concentration",
        severity="warn",
        message="Audit KAM flags intangibles / IP / goodwill — concentration risk.",
        applies=lambda s: bool(s.audit_key_audit_matters),
        evaluate=lambda s: (
            {}
            if _has_kam_with_phrase(
                s,
                r"\b(impairment|intangibles?|internal[ -]generated goodwill|investment property|IP)\b",
            )
            else None
        ),
    )


def _rule_going_concern_two_years() -> Rule:
    """``material_uncertainty_going_concern.present == true`` AND the same
    was true on the prior-year filing → STRUCTURAL failure, not transient.

    Catalog: '2 consecutive going-concern qualified opinions →
    structural failure'.
    """
    return Rule(
        rule_id="xcut_going_concern_structural_2y",
        severity="warn",
        message="Material uncertainty / going-concern flagged — check prior year for structural break.",
        applies=lambda s: bool((s.audit_material_uncertainty_going_concern or {}).get("present")),
        evaluate=lambda s: (
            {"present": True, "next_step": "confirm prior-year also flagged"}
            if (s.audit_material_uncertainty_going_concern or {}).get("present")
            else None
        ),
    )


def _rule_qualified_review_insurer_technical_reserves() -> Rule:
    """Insurer + qualified review + technical reserves language → flag.

    Catalog: 'Insurer with qualified review + technical reserves → flag'.
    """

    def applies(snap):
        return snap.sector == "insurance" and snap.audit_opinion_type in ("qualified", "review")

    def evaluate(snap):
        bag = " ".join(
            [
                (k.get("title") or "") + " " + (k.get("text") or "")
                for k in snap.audit_key_audit_matters
            ]
            + list(snap.audit_emphasis_of_matter)
        ).lower()
        if any(p in bag for p in ("technical reserve", "ibnr", "ulae", "claims reserve")):
            return {"keywords": "technical-reserves language present in audit"}
        return None

    return Rule(
        rule_id="xcut_insurer_qualified_review_technical_reserves",
        severity="warn",
        message="Insurer qualified review with technical-reserves language — reserve-completeness risk.",
        applies=applies,
        evaluate=evaluate,
    )


def _rule_qualified_basis_surfaced() -> Rule:
    """When opinion is "qualified" or "adverse", the verbatim basis paragraph
    is the most analyst-relevant text. Surface it as a warning so downstream
    UI shows it next to the verdict.

    Catalog: 'Qualified opinion = surface basis paragraphs.'
    """

    def applies(snap):
        return snap.audit_opinion_type in ("qualified", "adverse", "disclaimer")

    def evaluate(snap):
        text = (snap.raw.get("audit") or {}).get("verbatim_text")
        if not text or len(text) < 200:
            return {"audit_opinion_type": snap.audit_opinion_type, "missing_basis_paragraph": True}
        return {"audit_opinion_type": snap.audit_opinion_type}

    return Rule(
        rule_id="xcut_qualified_opinion_basis_surfaced",
        severity="info",
        message="Qualified / adverse / disclaimer opinion — see audit.verbatim_text for basis paragraph.",
        applies=applies,
        evaluate=evaluate,
    )


def _rule_aafs_reserve_dominates_ni() -> Rule:
    """|AFS reserve mark| > 50% of net income → equity is mark-to-market on
    the AFS book; underwriting is the right franchise eval.

    Catalog: '|AFS reserve mark| > 50% of net income → for insurers …'.
    """

    def applies(snap):
        return snap.sector == "insurance"

    def evaluate(snap):
        ni = _li_value(snap, "IS_NET_INCOME")
        mark = _li_value(snap, "BS_AFS_RESERVE")  # canonical name
        if ni is None or mark is None or ni == 0:
            return None
        if abs(mark) / abs(ni) > 0.5:
            return {"afs_reserve": mark, "net_income": ni, "ratio": abs(mark) / abs(ni)}
        return None

    return Rule(
        rule_id="xcut_aafs_dominates_ni",
        severity="warn",
        message="AFS reserve mark dominates net income — evaluate underwriting, not net income.",
        applies=applies,
        evaluate=evaluate,
    )


def _rule_aafs_is_large_share_of_equity() -> Rule:
    """AFS reserve >50 % of book equity → NAV is essentially a call on AFS.

    Catalog: 'AFS reserve book > 50% of book equity → NAV is essentially a
    call on the AFS book'.
    """

    def applies(snap):
        return snap.sector == "insurance"

    def evaluate(snap):
        mark = _li_value(snap, "BS_AFS_RESERVE")
        eq = _li_value(snap, "BS_TOTAL_EQUITY")
        if mark is None or eq is None or eq == 0:
            return None
        if abs(mark) / abs(eq) > 0.5:
            return {"afs_reserve": mark, "total_equity": eq, "share": abs(mark) / abs(eq)}
        return None

    return Rule(
        rule_id="xcut_aafs_share_of_equity",
        severity="warn",
        message="AFS reserve >50% of equity — NAV ≈ call on AFS book; P/B needs context.",
        applies=applies,
        evaluate=evaluate,
    )


def _rule_rate_swap_large_capital_intensive() -> Rule:
    """Interest-rate swap notional > 5 % TL → KAM-level for capital-intensive
    operators (Nakilat: 10.3 % of TL).

    Catalog: 'Interest rate swap notional > 5% of total liabilities →
    KAM-level for capital-intensive operators'.
    """

    def evaluate(snap):
        swap = _li_value(snap, "BS_INTEREST_RATE_SWAP_NOTIONAL")
        tl = _li_value(snap, "BS_TOTAL_LIABILITIES")
        if swap is None or tl is None or tl == 0:
            return None
        if swap / tl > 0.05:
            return {"swap": swap, "total_liabilities": tl, "share": swap / tl}
        return None

    return Rule(
        rule_id="xcut_rate_swap_capital_intensive_5pct_tl",
        severity="warn",
        message="Interest-rate swap notional >5% of total liabilities — capital-intensive-operator risk.",
        applies=lambda s: bool(s.ticker and s.fiscal_year),
        evaluate=evaluate,
    )


def _rule_ip_concentration_real_estate() -> Rule:
    """IP > 40 % of TA — concentration risk; if also trading at < 0.6x NAV
    + >5 % div yield, market is pricing write-down.

    Catalog: 'IP at > 40% of total assets → KAM-level for real estate'.
    """

    def evaluate(snap):
        ip = _li_value(snap, "BS_INVESTMENT_PROPERTY") or _li_value(snap, "BS_IP")
        ta = _li_value(snap, "BS_TOTAL_ASSETS")
        if ip is None or ta is None or ta == 0:
            return None
        share = ip / ta
        if share > 0.40:
            return {"investment_property": ip, "total_assets": ta, "share": share}
        return None

    return Rule(
        rule_id="xcut_ip_concentration_40pct_ta",
        severity="warn",
        message="Investment property >40% of total assets — concentration risk.",
        applies=lambda s: (
            s.sub_sector
            in ("Diversified Real Estate", "Property Development", "Real Estate Holding")
        ),
        evaluate=evaluate,
    )


def _rule_ifrs_9_transition() -> Rule:
    """IFRS 9 first-time-adoption → transition adjustment magnitude is in
    IS line items, NOT in the KAM text.

    Catalog: 'IFRS 9 transition magnitude often lives in IS, not KAM.'
    """

    def applies(snap):
        if not snap.audit_key_audit_matters:
            return False
        return _has_kam_with_phrase(
            snap, r"\bifrs\s*9\b|expected\s*credit\s*loss|ec[il]?\b|stage\s*[12]\b"
        )

    def evaluate(snap):
        for li in snap.line_items:
            label = (li.get("label_verbatim") or "").lower()
            if "transition" in label or "ifrs 9 adoption" in label or "opening retained" in label:
                return {"line_code": li.get("account_code"), "label": li.get("label_verbatim")}
        return None

    return Rule(
        rule_id="xcut_ifrs9_transition_in_is",
        severity="info",
        message="IFRS 9 transition flag — scan IS for transition / opening-RE line items.",
        applies=applies,
        evaluate=evaluate,
    )


def _rule_dual_income_statement_takaful() -> Rule:
    """Takaful issuers print two IS (Policyholders + Shareholders); the
    schema allows one. Flag when two ``income_statement`` statements are
    present.

    Catalog: 'Takaful/Islamic insurance dual-IS schema dedup pattern'.
    """

    def evaluate(snap):
        statements = snap.raw.get("statements") or []
        n_is = sum(1 for st in statements if st.get("type") == "income_statement")
        if n_is >= 2:
            return {"income_statement_count": n_is}
        return None

    return Rule(
        rule_id="xcut_dual_income_statement_takaful",
        severity="warn",
        message=(
            "Multiple income_statement entries — typical for Takaful issuers "
            "(Policyholders + Shareholders). Manual dedup may be needed."
        ),
        applies=lambda s: (
            s.sub_sector
            in (
                "Conventional Insurance",
                "Takaful Insurance",
                "Reinsurance",
                "Life & Medical Insurance",
            )
        ),
        evaluate=evaluate,
    )


def _rule_first_reporting_period_length() -> Rule:
    """Non-12-month first reporting period is a real signal (BRES 11.4-month
    stub, MPHC 7-month, VFQS 9-month FYE change). Initiation note + no YoY.

    Catalog: 'Non-12-month first reporting period = real signal'.
    """

    def evaluate(snap):
        # Crude heuristic: if period_label is not in {'Q1','Q2','Q3','Q4','FY',
        # 'H1','9M'} but looks like "from X to Y" → initiation.
        per = (snap.fiscal_period or "").strip().upper()
        canonical = {"Q1", "Q2", "Q3", "Q4", "FY", "H1", "H2", "9M"}
        if per in canonical or not per:
            return None
        if any(tok in per for tok in (" FROM ", " TO ", "MONTH", "PERIOD")):
            return {"period_label": per}
        return None

    return Rule(
        rule_id="xcut_first_reporting_period_non_standard",
        severity="info",
        message="Non-standard period_label — likely an initiation / FYE-change / stub. Suppress YoY.",
        applies=lambda s: bool(s.fiscal_period),
        evaluate=evaluate,
    )


def _rule_issuer_renamed() -> Rule:
    """Common QSE entity reassignment pattern — surface the catalog-known
    cases. Generic detection comes from the notes; here we surface known
    issuer reassignments by ticker."""

    REASSIGNED = {
        "QIGD": "Pre-2010 Gulf Cement Co.; 2010-2011 Al-Khalij Holding; 2012+ Qatari Investors Group",
        "VFQS": "FYE change Mar→Dec in 2013; 2013 & 2016 FY filings are 9-month transitions",
        "QETF": "Passive index ETF; NAV per unit is the fair value",
        "QATR": "Launched 2018-03-21; pre-stabilisation stub filings 2018 Q1/Q2",
    }
    REASSIGNED.get("{TICKER}", "")
    return Rule(
        rule_id="xcut_issuer_renamed_history",
        severity="info",
        message="Issuer name history note (renamed / FYE change / launch).",
        applies=lambda s: False,  # dynamic; see evaluate_issuer_renamed below
        evaluate=lambda s: {"note": REASSIGNED[s.ticker]} if s.ticker in REASSIGNED else None,
    )


def evaluate_issuer_renamed(snap: FilingSnapshot) -> RedFlag | None:
    """Variant: the static rule above gates on ``applies=False`` so it never
    fires through :func:`run_pre_flags`; this dispatch picks it up by ticker."""
    notes = {
        "QIGD": "Ticker reassigned 3×: Pre-2010 Gulf Cement Co. → 2010-2011 Al-Khalij Holding → 2012+ Qatari Investors Group.",
        "VFQS": "FYE changed Mar 31 → Dec 31 in 2013. _2013_FY and _2016_FY are 9-month transitions.",
        "QETF": "Passive index ETF. NAV per unit is the fair value. P/B = 1.0x by construction.",
        "QATR": "Launched 2018-03-21. _2018_Q2 = first ~101-day stub.",
        "MCGS": "Hospital operator — watch cash burn (e.g. 2008 FY -97% cash was a liquidity crisis even with healthy NAV).",
    }
    if snap.ticker in notes:
        return RedFlag(
            rule_id="issuer_renamed_history",
            ticker=snap.ticker,
            fiscal_year=snap.fiscal_year,
            severity="info",
            message=notes[snap.ticker],
            evidence={"source": "memory/qse-filings-extraction.md"},
        )
    return None


# Issuer-specific catalogue (the long-tail). Each rule's predicate
# combines the issuer AND a per-issuer activation year so we don't apply
# 2020s knowledge to a 2010 filing.

_ISSUER_FACTS: dict[str, dict] = {
    "AKHI": {
        "first_year": 2005,
        "note": (
            "Corpus misclassifies as islamic_bank (policyholders, wakala, "
            "Qard Hassan, Participants Fund, Tabarru, Retakaful). "
            "Pre-flag: any takaful issuer — verify sector."
        ),
        "ip_yield_year": 2016,
        "ip_yield_note": (
            "ALWAYS compute rental_income_yoy / ip_book_carrying_value; "
            "flag if > 10% (market rent yields 5–8% benchmark)."
        ),
    },
    "DUBK": {
        "first_year": 2021,
        "note": (
            "Intangibles from M&A: DUBK 2021 FY carried goodwill QR 443M as a KAM "
            "(3 CGUs). Pre-flag: intangibles >30% of TA → fragility."
        ),
    },
    "QIBK": {
        "first_year": 2018,
        "note": ("IFRS 9 transition filing — check IS for transition / opening-RE line items."),
    },
    "QIIK": {
        "first_year": 2018,
        "note": (
            "Best-in-class cost-to-income (9.0% in 2020 FY); pre-flag: "
            "cost-to-income > 12% or ROE < 10%."
        ),
    },
    "ZHCD": {
        "first_year": 2004,
        "note": (
            "8 of 10+ years qualified on same axis: Govt of Qatar flour subsidy + "
            "asset recoverability. Pre-flag: every ZHCD landing → analyst flag; "
            "2016+ pre-flag going concern as base case."
        ),
    },
    "WDAM": {
        "first_year": 2004,
        "note": (
            "5+ audit flags, 3+ qualified. Equilibrium pricing 0.55-0.65x P/B; "
            "clean audit recovery is structural BUY."
        ),
    },
    "QNCD": {
        "first_year": 2015,
        "note": ("Land license expired 2015; still in renegotiation. Equilibrium 0.50-0.60x P/B."),
    },
    "QGMD": {
        "first_year": 2019,
        "note": (
            "Going-concern 2019→2020→2021; 2nd consecutive = structural failure. "
            "STRONG_SELL with NAV 40% + liquidation 30% + EV/EBITDA 15% + RI 15%."
        ),
    },
    "QNNS": {
        "first_year": 2010,
        "note": (
            "Hybrid maritime + financial services. AFS-reserve 66% of equity. "
            "PwC unqualified with KAM=Impairment of property, vessels and intangibles."
        ),
    },
    "VFQS": {
        "first_year": 2013,
        "note": (
            "FYE changed Mar 31 → Dec 31 in 2013. _2013_FY and _2016_FY are 9-month transitions."
        ),
    },
    "QISI": {
        "first_year": 2013,
        "note": (
            "Dual IS (Policyholders + Shareholders). Unit scale change 2013 Q2 (QR000→QAR). "
            "2016+ image-based; only Q2 has auditor review (Deloitte)."
        ),
    },
    "DOHI": {
        "first_year": 2014,
        "note": ("Qualified review for IBNR / ULAE / PDR incompleteness; going-concern-adjacent."),
    },
    "QEWS": {
        "first_year": 2012,
        "note": (
            "KAHRAMAA concession Emiri decree not obtained; concession revenue at risk. "
            "Pre-flag: utility with non-decreed concession + >10% revenue → high severity."
        ),
    },
    "QFLS": {
        "first_year": 2015,
        "note": (
            "Auditor change to Rödl & Partner + QR 802.5M IP reclassification in same filing."
        ),
    },
    "QIMD": {
        "first_year": 2014,
        "note": (
            "2014 + 2015 Q3 carry going-concern note for QATAR CLAY BRICKS ASSOCIATE — "
            "NOT QIMD itself. going_concern_subject should distinguish 'self' | 'associate'."
        ),
    },
    "UDCD": {
        "first_year": 2010,
        "note": (
            "Real estate. IP at 47% of TA = KAM-level. Trading at 55% of book NAV + "
            "9.0% div yield. Bull case requires IP revaluation."
        ),
    },
    "QGTS": {
        "first_year": 2017,
        "note": (
            "LNG. KAM-flagged interest rate swap book QAR 2.478B = 10.3% of total liabilities. "
            "PP&E revaluation (book +30-50% below FMV) is central swing factor."
        ),
    },
    "IGRD": {
        "first_year": 2019,
        "note": (
            "2019 Q2: 3 EoM including 'internally-generated goodwill QR 711M NOT in "
            "conformity with IAS 38' (52% of TA). IAS 38 EXPLICITLY PROHIBITS recognizing "
            "internally-generated goodwill — if auditor didn't qualify, that's a red flag on the auditor."
        ),
    },
    "AHCS": {
        "first_year": 2019,
        "note": ("2019 FY + 2020 FY both have KAM on IP valuation; 2020: IP QR 7.1B = 80% of TA."),
    },
    "MPHC": {
        "first_year": 2018,
        "note": (
            "KAM on revenue recognition from JV sales to Muntajat — 96% revenue from "
            "single customer. Drop below 80% in future = positive diversification."
        ),
    },
    "MCGS": {
        "first_year": 2008,
        "note": (
            "Hospital operator — 2008 FY -97% cash to QAR 7.2M = liquidity crisis even "
            "with healthy NAV. Watch cash position hard."
        ),
    },
    "IHGS": {
        "first_year": 2018,
        "note": ("ROE 0.31% << Ke 10.55%, equity destroying 10pp/yr; NAV 0.75x P/B."),
    },
    "ABQK": {
        "first_year": 2018,
        "note": ("IFRS 9 transition; ROE 12.33% (above Ke 9.45%), cost-to-income 39.6%."),
    },
    "SIIS": {
        "first_year": 2010,
        "note": ("KPMG Note 38 court verdict EoM; +QAR 208M related-party receivable (8.2x YoY)."),
    },
    "QETF": {
        "first_year": 2015,
        "note": ("Passive index ETF. NAV per unit IS the fair value. P/B = 1.0x by construction."),
    },
}


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                       Run the catalog                                    ║
# ╚═══════════════════════════════════════════════════════════════════════════╝


def _all_rules() -> list[Rule]:
    """Stable order so logs and tests are deterministic."""
    return [
        _rule_kam_intangibles_concentration(),
        _rule_going_concern_two_years(),
        _rule_qualified_review_insurer_technical_reserves(),
        _rule_qualified_basis_surfaced(),
        _rule_aafs_reserve_dominates_ni(),
        _rule_aafs_is_large_share_of_equity(),
        _rule_rate_swap_large_capital_intensive(),
        _rule_ip_concentration_real_estate(),
        _rule_ifrs_9_transition(),
        _rule_dual_income_statement_takaful(),
        _rule_first_reporting_period_length(),
        _rule_issuer_renamed(),
    ]


def run_pre_flags(filing: dict) -> list[RedFlag]:
    """Evaluate every applicable rule on the merged filing."""
    snap = build_snapshot(filing)
    out: list[RedFlag] = []

    # Cross-cutting rules.
    for rule in _all_rules():
        try:
            if not rule.applies(snap):
                continue
            evidence = rule.evaluate(snap)
            if evidence is None:
                continue
            out.append(
                RedFlag(
                    rule_id=rule.rule_id,
                    ticker=snap.ticker,
                    fiscal_year=snap.fiscal_year,
                    severity=rule.severity,
                    message=rule.message,
                    evidence=evidence | {"note": rule.note} if rule.note else evidence,
                )
            )
        except Exception as e:  # pragma: no cover - defensive
            out.append(
                RedFlag(
                    rule_id=rule.rule_id,
                    ticker=snap.ticker,
                    fiscal_year=snap.fiscal_year,
                    severity="info",
                    message=f"pre-flag evaluation raised {type(e).__name__}",
                    evidence={"error": str(e)},
                )
            )

    # Issuer-specific facts: one rule per issuer/year pair that's in the
    # corpus window. These are info-level (don't block) — they just
    # surface the corpus knowledge the analyst would otherwise miss.
    info = _ISSUER_FACTS.get(snap.ticker or "", {})
    note = info.get("note")
    first_year = info.get("first_year", 0)
    if note and (snap.fiscal_year or 0) >= first_year:
        out.append(
            RedFlag(
                rule_id=f"issuer_fact_{snap.ticker.lower()}",
                ticker=snap.ticker,
                fiscal_year=snap.fiscal_year,
                severity="info",
                message=note,
                evidence={"source": "memory/qse-filings-extraction.md"},
            )
        )

    # The dynamic issuer-rename dispatch.
    r = evaluate_issuer_renamed(snap)
    if r is not None:
        out.append(r)

    return out


def merge_into_filing(filing: dict, flags: list[RedFlag]) -> None:
    """Append to ``red_flags[]`` AND ``extraction_quality.warnings`` (idempotent)."""
    if not flags:
        return
    rf = filing.setdefault("red_flags", [])
    if not isinstance(rf, list):
        rf = [rf]
    existing_ids = {(x.get("rule"), x.get("fiscal_year")) for x in rf if isinstance(x, dict)}
    for f in flags:
        d = {
            "rule": f.rule_id,
            "severity": f.severity,
            "ticker": f.ticker,
            "fiscal_year": f.fiscal_year,
            "message": f.message,
            **f.evidence,
        }
        if (f.rule_id, f.fiscal_year) not in existing_ids:
            rf.append(d)

    eq = filing.setdefault("extraction_quality", {})
    warnings = eq.get("warnings") or []
    if not isinstance(warnings, list):
        warnings = [warnings]
    existing_text = {str(w) for w in warnings}
    for f in flags:
        line = f"[pre-flag:{f.rule_id}] {f.message}"
        if line not in existing_text:
            warnings.append(line)
    eq["warnings"] = warnings
    # Convenience marker so downstream tests can grep for catalog hits.
    eq["pre_flag_count"] = len(flags)


__all__ = [
    "FilingSnapshot",
    "RedFlag",
    "Rule",
    "build_snapshot",
    "merge_into_filing",
    "run_pre_flags",
]
