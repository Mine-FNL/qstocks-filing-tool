#!/usr/bin/env python3
"""qscreen-demo — the 30-second "try the engine" experience.

Runs the engine end-to-end on a real golden-set case from
``tests/golden/`` and prints the deterministic JSON contract. No PDF
required, no API key required, no setup required.

This is the lowest-friction way to *see* the engine produce a lossless
filing JSON. The gate result and the bench accuracy are both printed
so the user knows what "success" looks like.

Usage:
    qscreen-demo                    # default case: qnbk_2023_fy (19/26 = 73.1%)
    qscreen-demo --case akhi_2022_fy
    qscreen-demo --case qnbk_2023_fy --json

Exit code:
    0 — engine ran end-to-end and produced a non-empty JSON record.
    1 — engine errored or produced an empty record.
    2 — invalid arguments.

This module is also importable as ``qscreen_demo`` so the same code path
can be embedded in docs / tests.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_CASE = "qnbk_2023_fy"

BANNER = r"""
   _____                                  __     _ _           _   _
  / ____|                                / _|   | (_)         | | (_)
 | |  __  ___ _ __   ___ _ __ __ _  ___ | |_ ___| |_ _ __   __| |  _ _______
 | | |_ |/ _ \ '_ \ / _ \ '__/ _` |/ _ \|  _/ _ \ | | '_ \ / _` | | |_  / _ \
 | |__| |  __/ | | |  __/ | | (_| | (_) | ||  __/ | | | | | (_| | |   / /  __/
  \_____|\___|_| |_|\___|_|  \__, |\___/|_| \___|_|_|_| |_|\__,_|_|  /___\___|
                               __/ |
                              |___/
                lossless filing JSON · math-identity gate · 80.6% bench
"""


def _strip_log_lines(text: str) -> str:
    """Strip leading INFO / WARNING log lines so the remainder is JSON."""
    out_lines = []
    for line in text.splitlines():
        if re.match(
            r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\s+(INFO|WARNING|ERROR|DEBUG|CRITICAL)\s+", line
        ):
            continue
        out_lines.append(line)
    return "\n".join(out_lines)


def _run_eval(case: str) -> tuple[int, dict | None, str]:
    """Run ``qscreen_eval.py --case <case> --json`` and return parsed output."""
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "qscreen_eval.py"), "--case", case, "--json"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    raw = _strip_log_lines(proc.stdout)
    try:
        return proc.returncode, json.loads(raw), ""
    except json.JSONDecodeError as ex:
        return proc.returncode or 2, None, f"could not parse eval JSON: {ex}\n{raw[:500]}"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="qscreen-demo",
        description="30-second end-to-end demo of the qscreen filing engine.",
    )
    p.add_argument(
        "--case",
        default=DEFAULT_CASE,
        help=(
            "Golden-set case id from tests/golden/. "
            f"Default: {DEFAULT_CASE} (highest bench pass-rate at 19/26)."
        ),
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Print only the JSON record (no banner, no prose).",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress the per-check detail.",
    )
    args = p.parse_args(argv)

    if not args.json:
        print(BANNER)
        print(f"→ Running engine on golden case: {args.case!r}")
        print("  (no PDF, no API key, no setup — same code path as a real filing)")
        print()

    _rc, payload, err = _run_eval(args.case)
    if payload is None:
        if args.json:
            print(json.dumps({"ok": False, "error": err}), file=sys.stderr)
        else:
            print(f"✗ engine errored on case {args.case!r}", file=sys.stderr)
            print(f"  {err.strip()[:500]}", file=sys.stderr)
        return 1

    cases = payload.get("cases") or []
    case_row = next((c for c in cases if c.get("case") == args.case), None)
    if case_row is None:
        print(f"✗ case {args.case!r} not in eval output", file=sys.stderr)
        return 1

    if case_row.get("error"):
        if args.json:
            print(json.dumps({"ok": False, "error": case_row["error"]}), file=sys.stderr)
        else:
            print(f"✗ engine error: {case_row['error']}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(case_row, indent=2, ensure_ascii=False))
        return 0

    # Friendly console summary
    score = case_row.get("score", 0)
    total = case_row.get("total", 0)
    duration_ms = case_row.get("duration_ms") or 0
    ticker = case_row.get("ticker", "?")
    fiscal_year = case_row.get("fiscal_year", "?")
    fiscal_period = case_row.get("fiscal_period", "?")
    pass_pct = (100.0 * score / total) if total else 0.0

    print(f"✓ engine completed in {duration_ms:.0f}ms")
    print(
        f"✓ {ticker} {fiscal_year} {fiscal_period}  ·  {score}/{total} checks passed ({pass_pct:.1f}%)"
    )
    print()

    if not args.quiet:
        checks = case_row.get("checks") or []
        # Group checks into passed / failed
        passed = [c for c in checks if c.get("passed")]
        failed = [c for c in checks if not c.get("passed")]
        if passed:
            print(f"  passed checks ({len(passed)}):")
            for c in passed[:5]:
                print(f"    ✓ {c.get('name')}")
            if len(passed) > 5:
                print(f"    … and {len(passed) - 5} more")
        if failed:
            print(f"  failed checks ({len(failed)}):")
            for c in failed[:5]:
                print(f"    ✗ {c.get('name')}  ({c.get('detail', '')})")
            if len(failed) > 5:
                print(f"    … and {len(failed) - 5} more")

    print()
    print("Now try it with your own PDF:")
    print()
    print("    qscreen-ingest report.pdf --symbol QIBK --year 2024 --period FY")
    print()
    print("Or run the full bench:")
    print()
    print("    python qscreen_eval.py --json > bench.json")
    print()
    print("Repo:  https://github.com/Mine-FNL/qstocks-filing-tool")
    print("Demo:  https://mine-fnl.github.io/qstocks-filing-tool/demo.html")
    print("Docs:  https://mine-fnl.github.io/qstocks-filing-tool/")
    print()
    print("Star ⭐ if the architecture resonates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
