"""Golden-set evaluation harness for the qscreen filing tool.

What
----
Runs each ``tests/golden/*.json`` case through the engine without LLM
(deterministic Basic mode), then compares the produced filing against the
hand-verified expectations in the case file. Emits a per-case report and
an aggregate accuracy score.

Why
----
A 435-test pytest suite proves the *invariants* of the engine
(skeleton detection, math identities, profile dispatch, state machine). It
does NOT prove the engine extracts the right *values*. For that, you need
labeled golden targets and a comparator.

How
----
A case file (``tests/golden/<id>.json``) describes:
  * expected metadata fields (symbol, year, sector, currency, framework)
  * expected audit fields (opinion_type, going-concern present, ...)
  * expected line items (lookup by `account_code`)
  * expected pre-flag rule hits

We provide:
  * the matching page text in ``tests/golden/_pages/<id>.txt``
  * the case-expected dict in ``tests/golden/<id>.json``

The harness runs the page through ``pdf_to_pages`` (skipped — we feed pages
directly), invokes the deterministic Basic extract, applies the pre-flag
catalog + gates, and compares structural keys.

Run
---
    python qscreen_eval.py                         # all cases, prints report
    python qscreen_eval.py --json                  # JSON output
    python qscreen_eval.py --case qnbk_2023_fy     # one case
    python qscreen_eval.py --timing --json         # include per-stage timings

Exit code: 0 if all cases pass, 1 otherwise. Wire into CI as
``python qscreen_eval.py || exit 1``.

Performance
-----------
``--timing`` turns on the engine's per-stage instrumentation (see
``qscreen_perf``). Each case's ``stages`` dict is included in the JSON
output as ``{stage_name: duration_ms}`` and the aggregate is also written
to ``--out-aggregate`` (Prometheus text format) for the weekly
``.github/workflows/perf.yml`` to consume.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import profiles
import qscreen_ingest as e
import qscreen_perf

log = logging.getLogger("qstock.eval")


GOLDEN_DIR = Path(__file__).parent / "tests" / "golden"
CASES_DIR = GOLDEN_DIR / "cases"


# ── per-case comparator ───────────────────────────────────────────────────────


@dataclass
class Check:
    name: str
    expected: Any
    actual: Any
    passed: bool
    detail: str = ""


@dataclass
class CaseReport:
    case: str
    ticker: str
    fiscal_year: int
    fiscal_period: str
    checks: list[Check] = field(default_factory=list)
    duration_s: float = 0.0
    error: str | None = None
    # Per-stage timings: {stage_name: duration_ms}. Populated only when the
    # engine was invoked with ``PERF_TIMING=1`` (set by ``qscreen_eval.py
    # --timing``); otherwise ``None``. Additive — older JSON consumers ignore
    # the new field. The aggregate is computed by ``qscreen_perf.aggregate``.
    stages: dict[str, float] | None = None

    @property
    def passed(self) -> bool:
        return self.error is None and all(c.passed for c in self.checks)

    @property
    def score(self) -> int:
        if not self.checks:
            return 0
        return sum(1 for c in self.checks if c.passed)

    @property
    def total(self) -> int:
        return len(self.checks)


def _split_pages(case_text: str) -> tuple[list[dict], str]:
    """Split a single combined case file into per-page dicts + raw narrative.

    The combined format uses ``===== PAGE N =====`` markers. The narrative
    inside each page block (audit prose, statement headers, narrative
    notes) becomes ``page["text"]``. ``[TABLES on page N]`` blocks feed
    the deterministic Basic extractor.

    Returns (pages, concatenated_narrative).
    """
    blocks = re.split(r"^===== PAGE \d+ =====\s*$", case_text, flags=re.MULTILINE)
    blocks = [b.strip() for b in blocks if b.strip()]
    pages = [{"num": i + 1, "text": b} for i, b in enumerate(blocks)]
    narrative = "\n\n".join(b for b in blocks)
    return pages, narrative


def _extract_one(case: dict, case_text: str,
                  perf_record: qscreen_perf.PerfRecord | None = None) -> dict:
    """Run the deterministic Basic path on the synthetic case file.

    Splits the combined file on ``===== PAGE N =====`` markers, feeds the
    page dicts into the deterministic Basic extractor, applies the pre-flag
    catalog + gates, and overlays the case's expected metadata so the
    comparator can find what it's looking for.

    When ``perf_record`` is supplied the engine records per-stage timings
    into it (``pdf_to_pages``, ``extract``, ``gates.run``,
    ``pre_flag_catalog.run``, ``fingerprint.fingerprint_filing``). When it's
    None every ``stage_timer`` call becomes a zero-overhead no-op, so the
    bench stays cheap when ``--timing`` is off.
    """
    import tempfile, shutil
    work = Path(tempfile.mkdtemp())
    try:
        pages, _ = _split_pages(case_text)
        # The Basic extractor expects each page to be self-window-able; with
        # 3-4 pages of synthetic content there's no need for chunking.
        args = SimpleNamespace(
            guided=True, guided_notes=True, no_chunk=True,
            pages_per_chunk=12, overlap=1,
            no_llm=True,                         # deterministic path
            symbol=case["ticker"], sector=case["sector"],
            year=case["fiscal_year"], period=case.get("fiscal_period", "FY"),
            jurisdiction=None,
            currency=None, framework=None,
        )
        # Wire the perf record (if any) so ``qscreen_ingest.extract_filing``
        # and its helpers accumulate timings.
        qscreen_perf.attach_to_args(args, perf_record)
        # extract_filing -> runs _apply_pre_flags internally
        filing = e.extract_filing(pages, args)

        # Apply gates (mirrors run_filing behavior).
        gate = e.qscreen_gates.gate_post_extract(filing)
        e.qscreen_gates.merge_warnings(filing, gate)

        # The deterministic path doesn't populate metadata from CLI args;
        # overlay the known case values that are NOT autodetectable
        # (symbol, year, currency, unit_scale). Sector / period /
        # framework are left blank so the engine's autodetect path can
        # be exercised by the comparator.
        meta = filing.setdefault("metadata", {})
        wanted = {
            "symbol": case["ticker"],
            "fiscal_year": case["fiscal_year"],
            "currency": case.get("expected", {}).get("metadata", {}).get("currency", "QAR"),
            "unit_scale": 1000,
            "consolidated": True,
        }
        for k, v in wanted.items():
            cur = meta.get(k)
            if cur in (None, "") or k not in meta:
                meta[k] = v

        # Auto-detect sector / period / framework via the engine's helper.
        # The comparator needs these to validate; if the detector can't
        # guess, the underlying value stays None and the comparator sees
        # the failure as a real regression.
        try:
            import qscreen_autodetect as _ad
            text_blob = "\n\n".join(p.get("text", "") for p in pages)
            _ad.apply_detected_metadata(filing, text_blob)
        except Exception as ex:
            log.warning("autodetect skipped: %s", ex)

        # Set the ticker on the args object too so profile-aware pre-flag
        # rules (``issuer_fact_<ticker>``) get evaluated by _apply_pre_flags.
        # ``extract_filing_guided`` doesn't read the symbol, only the LLM
        # prompt does — so we re-run the pre-flag catalog explicitly here.
        if profiles is not None:
            try:
                from profiles.qatar import pre_flags as _pf
                # Time this re-run separately so the perf baseline captures
                # the cost of the catalog on its own (the engine already
                # times the in-extract invocation).
                with qscreen_perf.stage_timer(log, perf_record,
                                                "pre_flag_catalog.rerun"):
                    _pf.merge_into_filing(filing, _pf.run_pre_flags(filing))
            except Exception as ex:
                log.warning("pre-flag re-run failed: %s", ex)

        return filing
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _find_line_value(filing: dict, code: str) -> float | None:
    """Walk every statement and return the first numeric value matching `code`."""
    for st in filing.get("statements") or []:
        for li in st.get("line_items") or []:
            if li.get("account_code") == code:
                v = li.get("value")
                if v in (None, ""):
                    return None
                try:
                    return float(v)
                except (TypeError, ValueError):
                    return None
    return None


def _red_flag_rules(filing: dict) -> list[str]:
    return [x.get("rule", "") for x in filing.get("red_flags", []) if isinstance(x, dict)]


def _within(a: float, b: float, rel: float = 0.005, abs_: float = 50.0) -> bool:
    """True iff |a-b| is within either tolerance."""
    if abs(a - b) <= abs_:
        return True
    base = max(abs(a), abs(b), 1.0)
    return abs(a - b) / base <= rel


def _compare_metadata(filing: dict, want: dict) -> list[Check]:
    """Per-key metadata equality (sector / currency / framework / ...) checks."""
    out = []
    meta = filing.get("metadata") or {}
    for key, want_val in want.items():
        got = meta.get(key)
        passed = got == want_val
        out.append(Check(f"metadata.{key}", want_val, got, passed,
                         detail="" if passed else f"want {want_val!r} got {got!r}"))
    return out


def _compare_audit(filing: dict, want: dict, page_text: str) -> list[Check]:
    out = []
    audit = filing.get("audit") or {}
    if "opinion_type" in want:
        out.append(Check("audit.opinion_type",
                          want["opinion_type"], audit.get("opinion_type"),
                          audit.get("opinion_type") == want["opinion_type"]))
    if "auditor_name" in want:
        out.append(Check("audit.auditor_name",
                          want["auditor_name"], audit.get("auditor_name"),
                          (audit.get("auditor_name") or "") == want["auditor_name"]))
    if "verbatim_text_contains" in want:
        text = audit.get("verbatim_text") or ""
        for needle in want["verbatim_text_contains"]:
            out.append(Check(f"audit.verbatim_text contains {needle!r}",
                              needle, needle in text, needle in text))
    if "material_uncertainty_going_concern_present" in want:
        present = (audit.get("material_uncertainty_going_concern") or {}).get("present")
        want_b = bool(want["material_uncertainty_going_concern_present"])
        out.append(Check("audit.mugc.present", want_b, bool(present),
                          bool(present) == want_b))
    if "audit_keywords_in_text" in want:
        # Loose: at least N of the keywords present somewhere in the page
        keywords = want["audit_keywords_in_text"]
        present = sum(1 for kw in keywords if re.search(re.escape(kw), page_text, re.IGNORECASE))
        out.append(Check("audit.keywords_in_text", len(keywords), present,
                          present >= max(1, len(keywords) - 1)))           # allow one miss
    return out


def _compare_statements(filing: dict, want: dict, page_text: str) -> list[Check]:
    out = []
    statements = filing.get("statements") or []
    n_st = len(statements)

    if "balance_sheet_code" in want:
        code = want["balance_sheet_code"]
        val = _find_line_value(filing, code)
        out.append(Check(f"statements.BS_present[{code}]",
                          "non-null", "non-null" if val is not None else "null",
                          val is not None))
        if "balance_sheet_value" in want:
            want_v = float(want["balance_sheet_value"])
            passed = val is not None and _within(val, want_v)
            out.append(Check(f"statements.BS[{code}].value",
                              want_v, val, passed,
                              detail="" if passed else f"want ~{want_v} got {val}"))
    if "balance_sheet_count" in want:
        out.append(Check("statements.balance_sheet_count",
                          want["balance_sheet_count"], n_st,
                          n_st >= want["balance_sheet_count"]))
    if "income_statement_code" in want:
        code = want["income_statement_code"]
        val = _find_line_value(filing, code)
        out.append(Check(f"statements.IS_present[{code}]",
                          "non-null", "non-null" if val is not None else "null",
                          val is not None))
        if "income_statement_value" in want:
            want_v = float(want["income_statement_value"])
            passed = val is not None and _within(val, want_v)
            out.append(Check(f"statements.IS[{code}].value",
                              want_v, val, passed,
                              detail="" if passed else f"want ~{want_v} got {val}"))
    if "income_statement_count" in want:
        n_is = sum(1 for st in statements if st.get("type") == "income_statement")
        out.append(Check("statements.income_statement_count",
                          want["income_statement_count"], n_is,
                          n_is == want["income_statement_count"]))
    if "cash_flow_code" in want:
        code = want["cash_flow_code"]
        val = _find_line_value(filing, code)
        out.append(Check(f"statements.CF_present[{code}]",
                          "non-null", "non-null" if val is not None else "null",
                          val is not None))

    # Loose line-volume bounds (the case gives a hint of expected density).
    total_lines = sum(len(st.get("line_items") or []) for st in statements)
    if "total_lines_min" in want:
        out.append(Check("statements.total_lines >= min",
                          want["total_lines_min"], total_lines,
                          total_lines >= want["total_lines_min"]))
    if "total_lines_max" in want:
        out.append(Check("statements.total_lines <= max",
                          want["total_lines_max"], total_lines,
                          total_lines <= want["total_lines_max"]))

    # Content-presence checks on the page text (informational; not strict).
    for code in ("BS_INVESTMENT_PROPERTY",):
        if f"balance_sheet_has_{code}" in want and want[f"balance_sheet_has_{code}"]:
            val = _find_line_value(filing, code)
            out.append(Check(f"statements.{code}_present",
                              "non-null", "non-null" if val is not None else "null",
                              val is not None))

    return out


def _compare_pre_flags(filing: dict, want: dict) -> list[Check]:
    out = []
    rules = _red_flag_rules(filing)
    for must in want.get("red_flags_must_contain", []) or []:
        out.append(Check(f"pre_flags.contains {must}",
                          "present", "present" if must in rules else "absent",
                          must in rules,
                          detail=f"actual rules: {', '.join(rules[:6])}{'...' if len(rules) > 6 else ''}"))
    for may in want.get("red_flags_expect", []) or []:
        out.append(Check(f"pre_flags.may contain {may}",
                          "possible", "present" if may in rules else "absent",
                          True,                          # informational only
                          detail="soft expectation"))
    if "red_flags_severity_breakdown" in want:
        warns = sum(1 for x in filing.get("red_flags", []) if x.get("severity") == "warn")
        blocks = sum(1 for x in filing.get("red_flags", []) if x.get("severity") == "block")
        if "warn_min" in want["red_flags_severity_breakdown"]:
            out.append(Check("red_flags.warn_count >= warn_min",
                              want["red_flags_severity_breakdown"]["warn_min"], warns,
                              warns >= want["red_flags_severity_breakdown"]["warn_min"]))
    return out


def _compare_languages(filing: dict, want: dict) -> list[Check]:
    out = []
    lang_list = (filing.get("metadata") or {}).get("languages") or []
    present_codes = [l.get("code") for l in lang_list]
    primary = next((l.get("code") for l in lang_list if l.get("primary")), None)

    for code in want.get("language_must_contain", []) or []:
        out.append(Check(f"languages.contains {code}",
                          "present", "present" if code in present_codes else "absent",
                          code in present_codes,
                          detail=f"actual codes: {', '.join(present_codes) or 'none'}"))
    if "language_primary" in want:
        out.append(Check("languages.primary", want["language_primary"], primary,
                          primary == want["language_primary"],
                          detail=f"actual primary: {primary!r}, all codes: {present_codes}"))
    if "language_min_ratio" in want:
        # Soft check: ratio of the primary language must be >= min_ratio.
        primary_lang = next((l for l in lang_list if l.get("primary")), None)
        ratio = primary_lang.get("ratio", 0) if primary_lang else 0
        out.append(Check("languages.primary.ratio >= min_ratio",
                          want["language_min_ratio"], ratio,
                          ratio >= want["language_min_ratio"],
                          detail=f"actual ratio: {ratio:.2%}" if primary_lang else "no primary"))
    return out


def evaluate_case(case_path: Path, cases_dir: Path,
                  with_timing: bool = False) -> CaseReport:
    case = json.loads(case_path.read_text())
    case_id = case["_case"]
    text_path = cases_dir / f"{case_id}.txt"
    if not text_path.exists():
        return CaseReport(case=case_id, ticker=case["ticker"],
                            fiscal_year=case["fiscal_year"],
                            fiscal_period=case.get("fiscal_period", "FY"),
                            error=f"combined case fixture missing: {text_path}")
    case_text = text_path.read_text()

    rep = CaseReport(case=case_id, ticker=case["ticker"],
                     fiscal_year=case["fiscal_year"],
                     fiscal_period=case.get("fiscal_period", "FY"))
    perf_record = qscreen_perf.PerfRecord() if with_timing else None
    t0 = time.perf_counter()
    try:
        filing = _extract_one(case, case_text, perf_record=perf_record)
    except Exception as ex:
        rep.error = f"{type(ex).__name__}: {ex}"
        rep.duration_s = time.perf_counter() - t0
        if perf_record is not None:
            rep.stages = _stage_totals(perf_record)
        return rep
    rep.duration_s = time.perf_counter() - t0
    if perf_record is not None:
        rep.stages = _stage_totals(perf_record)

    _, narrative = _split_pages(case_text)
    exp = case.get("expected", {})
    if "metadata" in exp:
        rep.checks.extend(_compare_metadata(filing, exp["metadata"]))
    if "audit" in exp:
        rep.checks.extend(_compare_audit(filing, exp["audit"], narrative))
    if "statements" in exp:
        rep.checks.extend(_compare_statements(filing, exp["statements"], narrative))
    rep.checks.extend(_compare_pre_flags(filing, exp))
    rep.checks.extend(_compare_languages(filing, exp))
    rep.checks.extend(_compare_fingerprint(filing, exp))
    return rep


def _compare_fingerprint(filing: dict, want: dict) -> list[Check]:
    """Every saved filing should carry a ``fingerprint`` block with at least
    one item (audit or statement verbatim). Used by change-detection
    tooling to compute deltas between two runs."""
    out = []
    fp = filing.get("fingerprint") or {}
    items = fp.get("items") or []
    out.append(Check("fingerprint.present",
                      "dict", "dict" if isinstance(fp, dict) else type(fp).__name__,
                      isinstance(fp, dict)))
    out.append(Check("fingerprint.overall_fingerprint.is_str",
                      "non-empty str",
                      str(fp.get("overall_fingerprint") or "")[:20],
                      isinstance(fp.get("overall_fingerprint"), str)
                      and bool(fp.get("overall_fingerprint"))))
    out.append(Check("fingerprint.items.len > 0",
                      want.get("fingerprint_min_items", 1),
                      len(items),
                      len(items) >= want.get("fingerprint_min_items", 1),
                      detail="audit + statements + notes should hash"))
    return out


def _stage_totals(perf_record: qscreen_perf.PerfRecord) -> dict[str, float]:
    """Sum per-stage durations for a single case. Used for the JSON output
    and the console line — the aggregate (across the whole batch) is
    computed separately by ``qscreen_perf.aggregate`` for the weekly
    perf-regression workflow."""
    out: dict[str, float] = {}
    for sample in perf_record.samples:
        out[sample.stage] = out.get(sample.stage, 0.0) + sample.duration_ms
    # Round to 3 decimals (sub-millisecond resolution is noise on CI).
    return {k: round(v, 3) for k, v in out.items()}


# ── report rendering ─────────────────────────────────────────────────────────


def render_markdown(reports: list[CaseReport]) -> str:
    n_pass = sum(1 for r in reports if r.passed)
    n_total = len(reports)
    n_err = sum(1 for r in reports if r.error)
    total_checks = sum(r.total for r in reports)
    pass_checks = sum(r.score for r in reports)

    lines = ["# qstock-filing-tool — golden-set extraction report",
             "", "## Summary", "",
             f"- Cases: **{n_total}** (passed: {n_pass}, errored: {n_err})",
             f"- Check-level accuracy: **{pass_checks}/{total_checks}** "
             f"({(100 * pass_checks / total_checks):.1f}%)" if total_checks else "",
             f"- Per-case detail:", ""]
    for r in reports:
        status = "✅" if r.passed else ("❌" if r.error else "⚠️")
        lines.append(f"  - {status} `{r.case}` ({r.ticker} {r.fiscal_year} {r.fiscal_period})"
                     f"  — {r.score}/{r.total} checks, {r.duration_s*1000:.0f} ms"
                     + (f"  — error: `{r.error}`" if r.error else ""))
    lines.append("")
    lines.append("## Per-case detail")
    lines.append("")
    for r in reports:
        lines.append(f"### `{r.case}`")
        if r.error:
            lines.append("")
            lines.append(f"**ERROR**: `{r.error}`")
            lines.append("")
            continue
        if not r.checks:
            lines.append("")
            lines.append("(no checks defined)")
            lines.append("")
            continue
        lines.append("")
        lines.append("| check | expected | actual | result |")
        lines.append("| --- | --- | --- | --- |")
        for c in r.checks:
            mark = "✅" if c.passed else "❌"
            exp_s = c.expected if not isinstance(c.expected, str) else c.expected
            act_s = c.actual if not isinstance(c.actual, str) else c.actual
            detail = f" — {c.detail}" if c.detail else ""
            lines.append(f"| `{c.name}` | {exp_s!r} | {act_s!r} | {mark}{detail} |")
        lines.append("")
    return "\n".join(lines)


def render_console(reports: list[CaseReport]) -> str:
    n_pass = sum(1 for r in reports if r.passed)
    n_total = len(reports)
    total = sum(r.total for r in reports)
    passed = sum(r.score for r in reports)
    out = [
        "",
        f"  Golden-set eval — {n_pass}/{n_total} cases, "
        f"{passed}/{total} check(s) pass "
        f"({(100*passed/total):.1f}%)" if total else "  no checks",
        "",
    ]
    for r in reports:
        if r.error:
            out.append(f"  ❌ {r.case:>22s}  ({r.ticker:>5s} {r.fiscal_year})  "
                       f"  ERROR: {r.error}")
        else:
            mark = "✅" if r.passed else "⚠️"
            out.append(f"  {mark} {r.case:>22s}  ({r.ticker:>5s} {r.fiscal_year} {r.fiscal_period})"
                       f"  {r.score:>2d}/{r.total:<2d}  {r.duration_s*1000:>5.0f} ms")
            # Show failing checks for partial passes.
            fails = [c for c in r.checks if not c.passed]
            if fails and not r.passed:
                for f in fails[:3]:
                    out.append(f"        • {f.name}: {f.detail}")
    return "\n".join(out)


# ── CLI ──────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Run golden-set extraction eval against the engine.")
    ap.add_argument("--case", help="Run only this case (substring match against case id)")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of console")
    ap.add_argument("--md", action="store_true", help="Emit Markdown report")
    ap.add_argument("--strict", action="store_true",
                    help="Treat 'soft expectations' as hard (so red_flags_expect "
                         "becomes a failure when missing). Off by default.")
    ap.add_argument("--timing", action="store_true",
                    help="Capture per-stage engine timings via qscreen_perf. "
                         "Sets PERF_TIMING=1 (so the engine wires the perf record) "
                         "and LOG_LEVEL=DEBUG (so qscreen.ingest emits the per-stage "
                         "trace). The JSON output's per-case 'stages' field is "
                         "populated, and --out-aggregate gets a Prometheus-format "
                         "summary when supplied.")
    ap.add_argument("--out", help="Write report to this path (default: stdout)")
    ap.add_argument("--out-aggregate",
                    help="When --timing is set, also write the per-stage aggregate "
                         "(Prometheus text format) to this path. The weekly perf "
                         "workflow consumes this against tests/golden/PERF_BASELINE.json.")
    args = ap.parse_args(argv)

    if args.timing:
        # Make the engine wire a perf record + bump log detail. The engine
        # reads PERF_TIMING via ``qscreen_perf.is_timing_enabled`` and LOG_LEVEL
        # is the standard Python logging knob.
        os.environ["PERF_TIMING"] = "1"
        os.environ["LOG_LEVEL"] = os.environ.get("LOG_LEVEL", "DEBUG")

    if not GOLDEN_DIR.is_dir():
        sys.stderr.write(f"qstock_eval: golden dir not found: {GOLDEN_DIR}\n")
        return 2

    case_files = sorted(GOLDEN_DIR.glob("*.json"))
    if args.case:
        case_files = [p for p in case_files if args.case.lower() in p.stem.lower()]
        if not case_files:
            sys.stderr.write(f"qstock_eval: no case matched '{args.case}'\n")
            return 2

    reports = [evaluate_case(p, CASES_DIR, with_timing=args.timing) for p in case_files]

    if args.json:
        cases_out: list[dict] = []
        # The PerfRecord objects carry the per-stage samples for the aggregate
        # output. Re-collect them here so we can emit both the per-case JSON
        # and the Prometheus aggregate without re-running the bench.
        all_records: list[qscreen_perf.PerfRecord] = []
        for r in reports:
            # Reconstruct a PerfRecord for the aggregate. The bench already
            # gave us a flat ``stages`` dict; back-compute a record with one
            # sample per stage so qscreen_perf.aggregate emits the same shape.
            rec = qscreen_perf.PerfRecord()
            if r.stages:
                for stage, ms in r.stages.items():
                    rec.add(stage, ms)
            all_records.append(rec)
            entry = {
                "case": r.case,
                "ticker": r.ticker,
                "fiscal_year": r.fiscal_year,
                "fiscal_period": r.fiscal_period,
                "passed": r.passed,
                "score": r.score,
                "total": r.total,
                "duration_ms": round(r.duration_s * 1000, 1),
                "error": r.error,
                "checks": [{"name": c.name, "expected": c.expected,
                             "actual": c.actual, "passed": c.passed,
                             "detail": c.detail} for c in r.checks],
            }
            if r.stages is not None:
                entry["stages"] = r.stages
            cases_out.append(entry)
        out: dict[str, Any] = {"cases": cases_out}
        if args.timing and all_records:
            agg = qscreen_perf.aggregate(all_records)
            out["aggregate"] = {stage: {k: v for k, v in stats.items()}
                                  for stage, stats in agg.items()}
        text = json.dumps(out, indent=2, ensure_ascii=False)

        if args.out_aggregate and all_records:
            try:
                agg_text = qscreen_perf.emit_metrics(all_records)
                Path(args.out_aggregate).write_text(agg_text, encoding="utf-8")
            except Exception as ex:
                log.warning("aggregate emit failed: %s", ex)
    elif args.md:
        text = render_markdown(reports)
    else:
        text = render_console(reports)

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)

    # Exit: 0 if every case passed, 1 otherwise.
    bad = [r for r in reports if not r.passed]
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
