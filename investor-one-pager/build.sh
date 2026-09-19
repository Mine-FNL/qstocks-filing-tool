#!/usr/bin/env bash
# Build the investor one-pager PDF.
#
# Pipeline: pandoc (md → html, embedded CSS) → Chrome headless (html → pdf).
# Idempotent.
#
# Usage:
#   bash investor-one-pager/build.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERE="${ROOT}/investor-one-pager"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "ERROR: pandoc not found (brew install pandoc)" >&2
  exit 1
fi
if [[ ! -x "${CHROME}" ]]; then
  echo "ERROR: Chrome not found at ${CHROME}" >&2
  exit 1
fi

echo "→ pandoc: md → html"
pandoc "${HERE}/one-pager.md" \
  --from markdown \
  --to html5 \
  --standalone \
  --metadata title="qscreen-filing-tool: investor one-pager" \
  --metadata author="qscreen-filing-tool maintainers" \
  --metadata date="September 2026" \
  --css="${HERE}/style.css" \
  --embed-resources --standalone \
  -o "${HERE}/one-pager.html"

echo "→ Chrome headless: html → pdf"
"${CHROME}" \
  --headless --disable-gpu --no-sandbox \
  --print-to-pdf="${HERE}/one-pager.pdf" \
  --print-to-pdf-no-header \
  "file://${HERE}/one-pager.html" 2>/dev/null

echo "✓ ${HERE}/one-pager.pdf"
ls -lh "${HERE}/one-pager.pdf"
