#!/usr/bin/env bash
#
# install.sh — fetch/update the jurisdiction-agnostic QScreen filing tool.
#
#   curl -fsSL https://raw.githubusercontent.com/0xBingBong69/qscreen-filing-tool/main/install.sh | bash
#
# Idempotent: clones on first run, fast-forwards on every run after.
#
# Environment overrides (all optional):
#   QSCREEN_REPO       git URL          (default: github HTTPS for this repo)
#   QSCREEN_TOOL_DIR   install location (default: $HOME/.qscreen-filing-tool)
#   QSCREEN_BRANCH     git branch       (default: main)
#   QSCREEN_SKIP_OCR   non-empty to skip the optional OCR deps
#
set -euo pipefail
umask 022

# Trapped handlers — any unexpected failure in an indented block below gets a
# one-line diagnostic instead of a half-installed tool directory.
trap 'echo "❌ install.sh failed at line $LINENO (exit $?)" >&2' ERR

REPO="${QSCREEN_REPO:-https://github.com/0xBingBong69/qscreen-filing-tool.git}"
DEST="${QSCREEN_TOOL_DIR:-$HOME/.qscreen-filing-tool}"
BRANCH="${QSCREEN_BRANCH:-main}"
TOOL="$DEST/qscreen_ingest.py"

echo "📦 QScreen filing tool installer"
echo "   repo:   $REPO"
echo "   dest:   $DEST"
echo "   branch: $BRANCH"

if [ -d "$DEST/.git" ]; then
  echo "↻ updating existing checkout …"
  git -C "$DEST" fetch --depth 1 origin "$BRANCH"
  git -C "$DEST" checkout -B "$BRANCH" "origin/$BRANCH" >/dev/null 2>&1
  git -C "$DEST" reset --hard "origin/$BRANCH"
else
  echo "⬇ cloning …"
  git clone --depth 1 --branch "$BRANCH" "$REPO" "$DEST"
fi

echo "🐍 ensuring python deps …"
# Use ``python3 -m pip`` so a system Python without pip-in-path still installs
# correctly. --upgrade-strategy only-if-needed keeps deterministic installs
# when the user already has newer versions present.
python3 -m pip install --quiet --upgrade --upgrade-strategy only-if-needed \
  -r "$DEST/requirements.txt"
if [ -z "${QSCREEN_SKIP_OCR:-}" ]; then
  echo "🔎 adding the offline scanned-page reader (optional) …"
  python3 -m pip install --quiet --upgrade --upgrade-strategy only-if-needed \
    -r "$DEST/requirements-ocr.txt" \
    || echo "   (Scanned-page reader unavailable for this Python — everything else still works.)"
fi

echo "🧪 self-test …"
python3 "$TOOL" --self-test

cat <<EOF

✅ Installed (with offline OCR for scanned pages, unless QSCREEN_SKIP_OCR was set). \
The tool lives at:
     $DEST

START THE APP — no API key needed:
     python3 $DEST/qscreen_app.py
   Your browser opens by itself; drag a PDF in and click Extract. The financial
   figures — income statement, cash flows, even a scanned/stamped balance sheet —
   are read offline, on your own computer.
   (Prefer no terminal at all? Download the ZIP from GitHub and double-click
   start.command on Mac / start.bat on Windows instead.)

OPTIONAL — also capture the audit opinion & note texts:
   Save an API key in the app's ⚙️ Settings panel (minimax / openrouter / kimi /
   openai / anthropic), or run a local model (Ollama / MLX / LM Studio).

CLI alternative — one command per PDF (also works with no key):
     python3 $TOOL <PDF> --symbol QIBK --sector islamic_bank --year 2024 --period FY
   --jurisdiction switches between profile bundles (default: profiles.qatar).
   --currency / --framework override what the profile reports.
   --dry-run saves the JSON without uploading.

TO UPDATE later: just re-run this installer.
EOF
