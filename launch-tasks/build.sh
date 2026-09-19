#!/usr/bin/env bash
# Build the launch-tasks PDF from launch-tasks.md.
#
# Pipeline: pandoc (md → html, embedded CSS) → Chrome headless (html → pdf).
# Idempotent.
#
# Usage:
#   bash launch-tasks/build.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERE="${ROOT}/launch-tasks"
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
pandoc "${HERE}/launch-tasks.md" \
  --from markdown \
  --to html5 \
  --standalone \
  --metadata author="qscreen-filing-tool maintainers" \
  --metadata date="September 2026" \
  --css="${HERE}/style.css" \
  --embed-resources --standalone \
  -o "${HERE}/launch-tasks.html"

echo "→ Chrome headless: html → pdf"
"${CHROME}" \
  --headless --disable-gpu --no-sandbox \
  --print-to-pdf="${HERE}/launch-tasks.pdf" \
  --print-to-pdf-no-header \
  "file://${HERE}/launch-tasks.html" 2>/dev/null

echo "✓ ${HERE}/launch-tasks.pdf"
ls -lh "${HERE}/launch-tasks.pdf"
