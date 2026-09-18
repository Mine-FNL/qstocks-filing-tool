#!/usr/bin/env bash
# GitHub Codespaces / devcontainer post-create hook.
#
# Brings the dev env up to "ready-to-extract" state in a single run:
#   1. pip install the package + dev extras
#   2. run the offline self-test (485 tests)
#   3. print a friendly banner pointing at the next steps

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

echo "┌──────────────────────────────────────────────────────────────┐"
echo "│  qscreen-filing-tool · devcontainer post-create             │"
echo "└──────────────────────────────────────────────────────────────┘"
echo

echo "→ pip install -e \".[dev]\""
pip install --quiet --disable-pip-version-check -e ".[dev]"
echo "  ✓ installed"
echo

echo "→ qscreen-ingest --self-test (offline contract gate)"
if python3 qscreen_ingest.py --self-test 2>&1 | tail -5; then
  echo "  ✓ self-test passed"
else
  echo "  ⚠ self-test reported non-zero; the workspace is still usable"
fi
echo

echo "Ready. Suggested next steps:"
echo
echo "  qscreen-demo                       # 30-second end-to-end demo"
echo "  qscreen-extract <pdf> <TICKER> <YYYY>   # shorthand for the common call"
echo "  python qscreen_eval.py --json > bench.json   # full 124-check bench"
echo "  qscreen-app                        # browser UI on http://localhost:8765"
echo
echo "  cat README.md                       # docs"
echo "  cat whitepaper/whitepaper.md        # architecture deep-dive"
echo
