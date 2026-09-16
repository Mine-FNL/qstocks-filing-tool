"""Post-extraction gates — the "is this thing actually usable?" filter.

Three classes of check:

1. **Skeleton detection.** A filing where 80%+ of ``line_items[].value`` are
   null is not a filing — it's an LLM that gave up. The schema accepts it
   (``validate_filing`` only checks shape), but downstream nothing useful
   can be done. Block the save; write ``*_filing.error.json`` instead.

2. **Statement math identities.** A balance sheet should satisfy
   ``TotalAssets ≈ TotalLiabilities + TotalEquity``. An income statement
   should satisfy ``GrossProfit ≈ Revenue − CostOfSales`` (when the
   subtotal is present). Skip the rule when one of the three legs is
   missing (this catches *inconsistent* filings, not under-extracted
   ones).

3. **Currency / unit sanity.** ``currency`` is an ISO-4217-shaped code;
   ``unit_scale`` is one of {1, 1_000, 1_000_000}. Anything else is
   either a transcription bug or a profile mismatch — both worth flagging
   before a research analyst gets the JSON.

Gates are advisory, not fatal. They run after ``validate_filing`` (so we
don't double-report schema problems) and emit a list of ``GateFinding``
objects the CLI writes to ``extraction_quality.warnings[]`` AND to a
``*_filing.error.json`` sidecar when the failure severity is
``"block_save"``.

These three checks are exactly what the live cron
``llm-ingest-monitor`` historically had to enforce by hand. Putting them
in the tool itself removes that ambiguity and turns "this filing was
junk" from a Slack message into a skip in the manifest.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

# Critical mass. Less than ``SKELETON_NULL_RATIO`` of line items have a
# real value → the filing is a skeleton. Tuned empirically against the
# documented silent-death cases (a real 10-statement filing has at least
# a few hundred leaf numbers; a skeleton has none).
SKELETON_NULL_RATIO = 0.80

# Numeric tolerance for math identities. The relative cap (1 %) is
# generous against QSE rounding to the nearest thousand QAR. The
# absolute cap (10) is a noise floor for tiny values where 1 % is just
# a single unit on a 100-row filing — passing inside this floor means
# "the model wrote 99.5 and the PDF said 100, fine."
MATH_TOLERANCE_REL = 0.01
MATH_TOLERANCE_ABS = 10.0

_BS_LEGS = ("BS_TOTAL_ASSETS", "BS_TOTAL_LIABILITIES", "BS_TOTAL_EQUITY")

_IS_SUBTOTAL_RULES: tuple[tuple[str, tuple[tuple[str, int], ...]], ...] = (
    # subtotal_code -> ((operand_code, sign), …)
    # Sign: +1 = operand contributes positively to the subtotal, -1 = it
    # is subtracted. This way the rule works regardless of whether the
    # model wrote COGS as a positive 700 or a negative -700.
    ("IS_GROSS_PROFIT",     (("IS_REVENUE", +1), ("IS_COST_OF_SALES", -1))),
    ("IS_OPERATING_PROFIT", (("IS_GROSS_PROFIT", +1),
                              ("IS_OPERATING_EXPENSES", -1))),
    ("IS_PROFIT_BEFORE_TAX",(("IS_OPERATING_PROFIT", +1),
                              ("IS_FINANCE_COST", -1),
                              ("IS_OTHER_INCOME", +1))),
)


@dataclass
class GateFinding:
    rule: str                 # e.g. "skeleton_high_null_rate"
    severity: str             # "warn" | "block_save"
    message: str
    evidence: dict = field(default_factory=dict)

    def to_warning(self) -> str:
        """Render as a one-line entry for ``extraction_quality.warnings``."""
        return f"[{self.rule}] {self.message}"


@dataclass
class GateResult:
    findings: list[GateFinding] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return any(f.severity == "block_save" for f in self.findings)

    @property
    def warnings(self) -> list[str]:
        return [f.to_warning() for f in self.findings]

    def to_warning_field(self) -> list[dict]:
        """Wire into extraction_quality.warnings — dict form (rule + sev)."""
        return [{"rule": f.rule, "severity": f.severity, "message": f.message,
                 **f.evidence} for f in self.findings]


# ── helpers ──────────────────────────────────────────────────────────────────

def _statement_by_code(filing: dict, code: str) -> dict | None:
    """Return the first ``line_item`` whose ``account_code`` matches, with
    the parent statement attached so the caller can label which statement
    the identity came from."""
    for st in filing.get("statements") or []:
        for li in st.get("line_items") or []:
            if li.get("account_code") == code:
                return {**li, "_statement_type": st.get("type"),
                        "_period_label":  st.get("period_label")}
    return None


def _value(item: dict | None) -> float | None:
    if not item:
        return None
    v = item.get("value")
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _imbalance(a: float, b: float) -> float:
    return abs(a - b)


def _within_tolerance(a: float, b: float) -> bool:
    """True iff |a-b| is below either the relative or the absolute cap."""
    if _imbalance(a, b) <= MATH_TOLERANCE_ABS:
        return True
    base = max(abs(a), abs(b), 1.0)
    return _imbalance(a, b) / base <= MATH_TOLERANCE_REL


# ── individual checks ─────────────────────────────────────────────────────────

def _check_skeleton(filing: dict) -> Iterable[GateFinding]:
    items = [li for st in (filing.get("statements") or [])
                  for li in (st.get("line_items") or [])]
    n = len(items)
    if n == 0:
        yield GateFinding(
            rule="skeleton_empty", severity="block_save",
            message="Filing has zero line items across all statements.")
        return
    null = sum(1 for li in items if li.get("value") in (None, ""))
    if null / n >= SKELETON_NULL_RATIO:
        yield GateFinding(
            rule="skeleton_high_null_rate", severity="block_save",
            message=(f"{null}/{n} line items have null values "
                     f"(>={SKELETON_NULL_RATIO:.0%}); refusing to save a skeleton."),
            evidence={"null": null, "total": n})
        return


def _check_balance_sheet(filing: dict) -> Iterable[GateFinding]:
    """TotalAssets ≈ TotalLiabilities + TotalEquity.

    Skip when any of the three legs is missing — under-extraction is
    already reported via the skeleton gate; we're looking for *wrong*
    numbers here, not absent ones.
    """
    a = _value(_statement_by_code(filing, "BS_TOTAL_ASSETS"))
    l = _value(_statement_by_code(filing, "BS_TOTAL_LIABILITIES"))
    e = _value(_statement_by_code(filing, "BS_TOTAL_EQUITY"))
    if a is None or l is None or e is None:
        return
    rhs = l + e
    if not _within_tolerance(a, rhs):
        yield GateFinding(
            rule="bs_identity_a_le_q", severity="warn",
            message=(f"Balance sheet doesn't balance: "
                     f"TotalAssets={a:,.0f}  TotalLiab+Equity={rhs:,.0f}  "
                     f"delta={a - rhs:+,.0f}"),
            evidence={"total_assets": a, "total_liab": l,
                      "total_equity": e, "rhs": rhs})


def _check_income_subtotals(filing: dict) -> Iterable[GateFinding]:
    """For each subtotal rule, compare stored value to the signed sum of operands.

    Same policy as the BS check: skip when any operand is missing.
    Operators carry a sign so the rule is correct regardless of the
    model's sign convention (CostOfSales=+700 vs -700, etc.).
    """
    for subtotal_code, operands in _IS_SUBTOTAL_RULES:
        sub_item = _statement_by_code(filing, subtotal_code)
        sub = _value(sub_item)
        if sub is None:
            continue
        terms = []                 # (code, signed_value)
        missing = []
        for code, sign in operands:
            v = _value(_statement_by_code(filing, code))
            if v is None:
                missing.append(code)
            else:
                terms.append((code, sign * v))
        if missing or not terms:
            continue                    # under-extracted; not our concern
        rhs = sum(signed for _, signed in terms)
        if not _within_tolerance(sub, rhs):
            rendered = " + ".join(
                f"{'-' if signed < 0 else ''}{abs(signed):,.0f}".lstrip("-")
                for _, signed in terms
            )
            yield GateFinding(
                rule=f"is_subtotal_{subtotal_code.lower()}", severity="warn",
                message=(f"{subtotal_code}={sub:,.0f} but the operands yield "
                         f"{rhs:,.0f}  delta={sub - rhs:+,.0f}"),
                evidence={"subtotal": subtotal_code, "expected": rhs,
                          "got": sub, "operands": [c for c, _ in operands]})


def _check_currency_unit(filing: dict) -> Iterable[GateFinding]:
    meta = filing.get("metadata") or {}
    cur = meta.get("currency")
    if cur is None:
        return
    if not isinstance(cur, str) or not (2 <= len(cur) <= 5) or not cur.isalpha():
        yield GateFinding(
            rule="metadata_currency_shape", severity="warn",
            message=f"metadata.currency is not ISO-4217-shaped: {cur!r}",
            evidence={"currency": cur})

    us = meta.get("unit_scale")
    if us is not None and us not in (1, 1000, 1_000_000):
        yield GateFinding(
            rule="metadata_unit_scale", severity="warn",
            message=(f"metadata.unit_scale={us!r} is not in "
                     f"{{1, 1000, 1_000_000}}; the engine rejects anything else."),
            evidence={"unit_scale": us})


# ── public entry points ─────────────────────────────────────────────────────

def gate_post_extract(filing: dict) -> GateResult:
    """Run every gate and return the aggregate result.

    A non-empty ``blocked`` result means the CLI should write
    ``*_filing.error.json`` and skip the upload.
    """
    result = GateResult()
    result.findings.extend(_check_skeleton(filing))
    result.findings.extend(_check_balance_sheet(filing))
    result.findings.extend(_check_income_subtotals(filing))
    result.findings.extend(_check_currency_unit(filing))
    return result


def merge_warnings(filing: dict, gate: GateResult) -> None:
    """Append gate messages to ``extraction_quality.warnings`` (idempotent).

    - Existing ``warnings`` list is preserved.
    - Each gate message is also added as a dict form so the new pre-flag
      rule + severity fields are surfaced alongside the old string-only
      ones downstream.
    """
    eq = filing.setdefault("extraction_quality", {})
    existing = eq.get("warnings") or []
    if not isinstance(existing, list):
        existing = [existing]
    eq["warnings"] = existing + list(gate.warnings) + gate.to_warning_field()
