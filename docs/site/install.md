# Installation

There are three install paths. They install the **same wheel** — the only
difference is where the wheel comes from. Pick whichever is convenient.

---

## Path 1 — Direct from GitHub Releases (no PyPI, no token)

Use this if you want a single `pip install` against the GitHub Releases CDN
and don't want to set up an extra index.

```bash
pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/latest/download/qscreen_filing_tool-1.6.0-py3-none-any.whl
```

The wheel URL is built by `.github/workflows/release.yml` on every `v*` tag
push: bench regression gate → build → GitHub Release upload. The
`latest/download/…` redirect always points at the current release.

!!! note "Behind a corporate proxy?"
    The same wheel can be downloaded manually from the
    [Releases page](https://github.com/Mine-FNL/qstocks-filing-tool/releases/latest)
    and `pip install path/to/wheel.whl`-ed locally.

## Path 2 — PEP 503 simple index on GitHub Pages

This is the path you want for air-gapped or restricted environments that
already whitelist `--extra-index-url`.

```bash
pip install --extra-index-url https://mine-fnl.github.io/qstocks-filing-tool/simple/ qscreen-filing-tool
```

The `simple/` directory is a PEP 503 repository served off the `gh-pages`
branch (see `.github/workflows/release.yml`, job *Upload to gh-pages*).
It points at the wheel uploaded on the **same** release run, so the
index can never disagree with the wheel.

## Path 3 — From a clone (full source + dev extras)

Use this if you want to read the engine, edit it, or contribute a profile.

```bash
git clone https://github.com/Mine-FNL/qstocks-filing-tool
cd qstocks-filing-tool
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[xlsx,ocr]"      # xlsx = Excel transcript; ocr = scanned PDFs
```

!!! info "About the `.[xlsx,ocr]` extras"
    - `xlsx` pulls in `openpyxl` for `--export xlsx` (multi-sheet Excel
      transcript).
    - `ocr` pulls in `rapidocr-onnxruntime` for scanned PDFs (no system
      software needed). For `pytesseract`, use `.[ocr-tesseract]` instead.
    - `dev` pulls in `pytest` + `openpyxl` for the offline test suite.
    Multiple extras can be combined: `.[xlsx,ocr,dev]`.

## Verify the install

The engine ships an offline self-test that runs without any LLM key or
network access:

```bash
python3 -m qscreen_ingest --self-test
```

You should see a green checkmark and `OK`. Then:

```bash
pytest -q                       # the full offline suite (480 tests)
python qscreen_eval.py --md     # the golden-set bench (informational)
```

## Configure a provider key (optional — only for LLM extraction)

The engine works without a key in `--no-llm` / `--basic` mode. To unlock
opinion extraction, notes, and the prompt-guided audit you need **one**
of:

- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `OPENROUTER_API_KEY`
- `MINIMAX_API_KEY`
- `MOONSHOT_API_KEY`

Set it via `.env`:

```bash
cp .env.example .env               # edit .env and paste ONE key
python3 -m qscreen_ingest --list-providers   # see which key is detected
set -a; . ./.env; set +a           # load it into the shell
```

Or pass it inline with `--llm-key …`. `INGEST_TOKEN` is **optional** —
only needed to upload to qscreen.app; without it the tool just saves
locally.

## Next

- → [Usage](usage.md): CLI flags, batch harness, `--example` recipes.
- → [Architecture](architecture.md): data flow, gates, state, fingerprints.
