#!/usr/bin/env python3
"""qscreen-extract — shorthand wrapper for the most common extraction.

Most users only run the engine one way:
    qscreen-ingest <pdf> --symbol <TICKER> --year <YYYY> --period <PERIOD>

This wrapper is the same call with the default ``--period FY``, sane
``--quiet``, and a friendly banner. It exists so a fresh terminal
session can type ``qscreen-extract`` and get to the first JSON in one
line.

Usage:
    qscreen-extract                                  # interactive: prompts for pdf + ticker
    qscreen-extract path/to/report.pdf QIBK 2024     # explicit
    qscreen-extract --no-banner path/to/report.pdf QIBK 2024 --period H1

Exit code:
    Same as ``qscreen-ingest``. Non-zero on engine error.

This module is also importable as ``qscreen_extract``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="qscreen-extract",
        description="Shorthand wrapper for the most common qscreen-ingest invocation.",
    )
    p.add_argument(
        "pdf",
        nargs="?",
        help="Path to the PDF filing. If omitted, prompts interactively.",
    )
    p.add_argument(
        "symbol",
        nargs="?",
        help="Ticker symbol (e.g. QIBK, AKHI, MARK). If omitted, prompts interactively.",
    )
    p.add_argument(
        "year",
        nargs="?",
        type=int,
        help="Fiscal year (e.g. 2024). If omitted, prompts interactively.",
    )
    p.add_argument(
        "--period",
        default="FY",
        choices=["FY", "Q1", "Q2", "Q3", "Q4", "H1", "9M"],
        help="Fiscal period (default: FY).",
    )
    p.add_argument(
        "--sector",
        default=None,
        choices=[
            "conventional_bank",
            "islamic_bank",
            "industrial",
            "insurance",
            "real_estate",
            "holding",
            "other",
        ],
        help="Sub-sector override. Auto-detected by default.",
    )
    p.add_argument(
        "--provider",
        default=None,
        help="LLM provider (auto-detected from .env). See qscreen-ingest --list-providers.",
    )
    p.add_argument(
        "--no-banner",
        action="store_true",
        help="Skip the friendly banner.",
    )
    p.add_argument(
        "--basic",
        action="store_true",
        help="Basic mode (deterministic-first, suitable for tiny/local models).",
    )
    p.add_argument(
        "--no-llm",
        action="store_true",
        help="Run fully offline — no model at all.",
    )
    p.add_argument(
        "--upload",
        action="store_true",
        help="Upload to qscreen.app on success (requires INGEST_TOKEN).",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Produce JSON without uploading.",
    )
    args = p.parse_args(argv)

    if not args.no_banner:
        print("qscreen-extract  ·  shorthand for: qscreen-ingest <pdf> --symbol X --year Y")
        print()

    # Interactive prompts for missing args
    if not args.pdf:
        args.pdf = input("Path to PDF: ").strip()
        if not args.pdf:
            print("✗ no PDF specified", file=sys.stderr)
            return 2
    if not args.symbol:
        args.symbol = input("Ticker symbol (e.g. QIBK): ").strip().upper()
        if not args.symbol:
            print("✗ no symbol specified", file=sys.stderr)
            return 2
    if args.year is None:
        raw = input("Fiscal year (e.g. 2024): ").strip()
        try:
            args.year = int(raw)
        except ValueError:
            print(f"✗ year must be an integer, got {raw!r}", file=sys.stderr)
            return 2

    if not os.path.exists(args.pdf):
        print(f"✗ PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    # Build the qscreen-ingest command
    cmd = [
        sys.executable,
        str(REPO_ROOT / "qscreen_ingest.py"),
        args.pdf,
        "--symbol",
        args.symbol,
        "--year",
        str(args.year),
        "--period",
        args.period,
        "--quiet",
    ]
    if args.sector:
        cmd += ["--sector", args.sector]
    if args.provider:
        cmd += ["--provider", args.provider]
    if args.basic:
        cmd += ["--basic"]
    if args.no_llm:
        cmd += ["--no-llm"]
    if args.upload:
        cmd += ["--upload"]
    if args.dry_run:
        cmd += ["--dry-run"]

    import subprocess

    return subprocess.call(cmd, cwd=str(REPO_ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
