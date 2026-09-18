#!/usr/bin/env bash
# Build the whitepaper PDF from whitepaper.md.
#
# Pipeline: pandoc (md → html, with TOC + embedded CSS) → Chrome headless
# (html → pdf). Reproducible: requires pandoc + Google Chrome (both
# pre-installed on macOS dev machines; for CI use `chromium` instead).
#
# Usage:
#   bash whitepaper/build.sh
#   bash whitepaper/build.sh && open whitepaper/whitepaper.pdf

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WHITEPAPER="${ROOT}/whitepaper"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "ERROR: pandoc not found. Install with: brew install pandoc" >&2
  exit 1
fi

if [[ ! -x "${CHROME}" ]]; then
  echo "ERROR: Google Chrome not found at ${CHROME}" >&2
  exit 1
fi

echo "→ pandoc: md → html"
pandoc "${WHITEPAPER}/whitepaper.md" \
  --from markdown \
  --to html5 \
  --standalone \
  --toc \
  --toc-depth=2 \
  --metadata title="Lossless Filing JSON" \
  --metadata author="qscreen-filing-tool maintainers" \
  --metadata date="September 2026" \
  --css="${WHITEPAPER}/style.css" \
  --embed-resources --standalone \
  -o "${WHITEPAPER}/whitepaper.html"

echo "→ Chrome headless: html → pdf"
"${CHROME}" \
  --headless --disable-gpu --no-sandbox \
  --print-to-pdf="${WHITEPAPER}/whitepaper.pdf" \
  --print-to-pdf-no-header \
  "file://${WHITEPAPER}/whitepaper.html" 2>/dev/null

echo "✓ ${WHITEPAPER}/whitepaper.pdf"
ls -lh "${WHITEPAPER}/whitepaper.pdf"
