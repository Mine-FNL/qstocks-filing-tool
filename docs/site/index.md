# qscreen-filing-tool

**Turn a PDF financial report into a lossless, auditable filing JSON — ready
for ingest.**

A jurisdiction-agnostic engine that takes any exchange's annual / interim
report (IFRS, AAOIFI, or anything in between) and emits a single stable,
fingerprintable JSON object: every number, the audit opinion, segments, note
text, and provenance. Pluggable profiles (Qatar ships out of the box;
AE / SA / KW are one directory drop away).

Two modes: **local browser app** (drag-and-drop, ~3 min to first JSON) or
**one-command CLI** (scriptable, idempotent batches with SQLite-backed
resume).

---

## Install — one of three paths

```bash
# (1) Direct from the public GitHub Releases CDN (no PyPI needed, no token)
pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/latest/download/qscreen_filing_tool-1.6.0-py3-none-any.whl

# (2) PEP 503 simple index hosted on GitHub Pages (PyPI-equivalent for one package)
pip install --extra-index-url https://mine-fnl.github.io/qstocks-filing-tool/simple/ qscreen-filing-tool

# (3) From a clone (full source + dev extras)
git clone https://github.com/Mine-FNL/qstocks-filing-tool
cd qstocks-filing-tool && pip install -e ".[dev]"
```

Then either:

```bash
qscreen-app          # → localhost:8765  (drag PDF, click Extract)
qscreen-ingest report.pdf --symbol AKHI --year 2022
```

!!! tip "First run?"
    Follow the [RUNBOOK](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/RUNBOOK.md) — install → key → one command → every
    output. The RUNBOOK is the same content used by the bench harness to
    verify the engine after every release.

## Quick demo (no install required)

- **Live bench report** (auto-generated from `qscreen_eval.py`):
  [mine-fnl.github.io/qstocks-filing-tool/demo.html][demo]
- **Long-form pitch** (HN/Show, r/quant, IR Society):
  [docs/SHOW_HN.md][hn]

[demo]: https://mine-fnl.github.io/qstocks-filing-tool/demo.html
[hn]: https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/docs/SHOW_HN.md

## What's in the box

- **Engine core** — `qscreen_ingest.py` turns a PDF into a schema-stable
  filing JSON (audit, segments, notes, provenance). Pluggable profiles,
  not hardcoded to one exchange.
- **Browser app** — `qscreen_app.py` is a Flask app on port 8765. Drag a
  PDF, click Extract, save or upload. Ships `/healthz` for orchestrators.
- **CLI batch** — `--manifest`, `--jobs`, `--resume` for hundreds of
  filings. SQLite state at `~/.qstocks-filing-tool/state.db` makes a
  crashed run pick up where it left off.
- **Math-identity gates** — `qscreen_gates.py` runs BS identity
  (A ≈ L + E), IS subtotal sign-aware checks, skeleton detection
  (>80 % null), currency/unit sanity. Failures never upload.
- **Stable text fingerprints** — `qscreen_fingerprint.py print` and
  `... diff`. SHA-256 over whitespace-normalized text. Order-independent
  overall fingerprint. Stamped on every saved filing. Means a re-run on
  the same input is byte-identical for byte-identical input, and a
  cross-filing diff tells you exactly what changed (restated number vs.
  footnote edit vs. audit qualification).
- **Auto-detect** — sector, fiscal period, reporting framework inferred
  from the filing's cover page. Default ON; `--no-auto-detect` to disable.
  Never overwrites operator-provided values.
- **Bilingual** — pure-Unicode Arabic/English classifier; `metadata.languages[]`
  + `filing.page_languages{}` on every output.
- **Pre-flag catalog** — 11 cross-cutting rules + 25 issuer-specific
  facts (Qatar). ZHCD 8-of-10 qualified opinions, AKHI misclassification
  guard, QIGD renames, UDCD intangibles, etc. Emits `red_flags[]`
  automatically.
- **Golden-set bench** — `python qscreen_eval.py` runs 8 hand-verified
  real QSE filings. Baseline: **100 / 124 (80.6 %)** check-level
  accuracy. Integrated in CI as a regression gate.

## Why this, not `pdfplumber` / `camelot` / `marker`?

| Tool | Strong at | Weak at — for *financial filings* specifically |
|---|---|---|
| `pdfplumber` | raw text + table extraction | no financial schema; no audit opinion; no fiscal-period awareness; no profile/ticker ergonomics |
| `camelot` / `tabula-py` | lattice + stream tables | no opinion, no segments, no notes, no provenance, no resume on crash |
| `marker` | Markdown from PDFs | output is prose, not structured financial JSON; can't be diffed reliably across re-extractions |
| LLM-only (GPT/Claude) | opinion + notes | expensive; non-deterministic JSON; **no** reproducible fingerprints for regression testing |
| **qscreen-filing-tool** | schema-stable filing JSON + audit + segments + notes + **SHA-256 cross-filing fingerprints** + math-identity gates + idempotent batch + SQLite resume | — |

The engine targets the *final-mile* problem: everyone gets text out of a
PDF; very few tools give you a diff-able, audit-traceable,
jurisdiction-aware JSON record you can hand to a quant, an LLM, or a
regulatory pipeline.

## What's next

- [Install qscreen-filing-tool](install.md)
- [Use the CLI or batch harness](usage.md)
- [Read the architecture](architecture.md)
- [Drop in a new jurisdiction](jurisdictions.md)
- [Run the bench / read the CI story](bench.md)