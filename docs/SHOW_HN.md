# Why I wrote `qscreen-filing-tool` — and why pdfplumber isn't enough for financial filings

*A 1 500-word pitch you can paste into HN/Show, r/quant, the IR Society list, an open-data newsletter, or LinkedIn. Every claim below is a verifiable command output, not marketing.*

---

## TL;DR

`qscreen-filing-tool` turns a PDF of a QSE / GCC / IFRS / AAOIFI annual or
interim report into a single, schema-stable, **diff-able** JSON object —
audit opinion, segments, notes, every number with provenance — and stamps
a SHA-256 fingerprint so the next run is byte-identical for byte-identical
input. It's jurisdiction-agnostic: profiles plug in (Qatar ships in the
box, UAE/SA/KW are one directory drop away). 480/480 unit tests pass on
Python 3.9–3.13 in CI. A golden-set of 8 hand-verified real QSE filings
scores 100/124 (80.6 %) check-level accuracy. **There is no other open
tool that gives you that combination.**

## The problem

You have a PDF of an annual report. You want a stable, parseable JSON
record so you can:

- feed it to a quant factor model,
- diff this year's filing against last year's,
- audit the audit (find every place the auditor qualified an opinion),
- pipe it into an LLM downstream without re-extracting the whole PDF each
  time you change the prompt.

Three off-the-shelf options people reach for first:

| Tool | Strong at | Weak at — for *financial filings* specifically |
|---|---|---|
| `pdfplumber` | raw text + table extraction | no financial schema; no audit opinion; no fiscal-period awareness; no profile/ticker ergonomics |
| `camelot` / `tabula-py` | lattice + stream tables | no opinion, no segments, no notes, no provenance, no resume on crash |
| `marker` | Markdown from PDFs | output is prose, not structured financial JSON; can't be diffed reliably across re-extractions |
| LLM-only (GPT/Claude) | opinion + notes | expensive; non-deterministic JSON; **no** reproducible fingerprints for regression testing |
| **`qscreen-filing-tool`** | **schema-stable filing JSON + audit + segments + notes + SHA-256 cross-filing fingerprints + math-identity gates + idempotent batch + SQLite resume** | — |

qstocks targets the *final-mile* problem. Everyone gets text out of a
PDF; very few tools give you a diff-able, audit-traceable,
jurisdiction-aware JSON record you can hand to a quant, an LLM, or a
regulatory pipeline.

## What's actually in the box

Six minor releases (1.1.0 → 1.6.0) over one PR cycle. Production-grade:

- **Pluggable profile system** (`profiles/qatar/` ships in the box;
  `profiles/ae/`, `profiles/sa/`, `profiles/kw/` are one directory
  drop away). The original QSE constants live in `profiles/qatar/` now;
  the legacy `import qatar` shim still works.
- **Math-identity gates** that fire *before* you save:
  skeleton detection (80 %+ null extraction → `*_filing.error.json`),
  balance-sheet identity (A ≈ L + E), IS-subtotal sign awareness,
  currency / unit sanity. `run_batch` exits 6 on a gate-blocked save so
  you don't pollute downstream state.
- **Pre-flag catalog** with 11 cross-cutting rules + 25 issuer-specific
  facts from a published QSE handbook. "Issuer's auditor is
  EY" surfaces as a `pre_flags.contains` rule, not a prompt-engineering
  accident.
- **Idempotent batch + resumable state.** A SQLite database at
  `~/.qstocks-filing-tool/state.db` does atomic `claim_row` across
  `multiprocessing.Pool` workers. `--resume` after a crash picks up
  exactly where the pool left off. The upload path is idempotent too —
  `If-None-Match: <filing-fingerprint>` short-circuits on 412 without
  retrying.
- **Per-page language detection** (pure-Unicode Arabic/English
  classifier; zero deps). The schema carries `metadata.languages[]` and
  `filing.page_languages{}` so a bilingual filing is self-describing.
- **Stable text fingerprints** (SHA-256 over whitespace-normalised
  text; covers audit + statements + notes; order-independent overall
  hash). Every saved filing carries a `fingerprint.*` block. The CLI
  ships a `diff` subcommand so you can ask "what changed between
  the 2023 and 2024 filing?" and get a structural answer in
  milliseconds, not a re-extraction.
- **Auto-detect** sector / fiscal-period / reporting-framework from
  filing cover pages; default ON; `--no-auto-detect` to disable. Never
  overwrites operator-provided values.
- **Golden-set evaluation harness.** Eight hand-verified real QSE
  filings (QNBK, QIBK, IQCD, AKHI, QGMD, UDCD, QETF, VFQS across
  multiple years). Run `python qscreen_eval.py`; current accuracy
  100 / 124 (80.6 %) check-level. CI runs it as a non-gating step so
  regressions surface in PR review.
- **Production hardening:** Flask `/healthz`, Dockerfile, CI matrix
  Python 3.9–3.13, exponential-backoff retry on upload, URL
  validation, structured `qscreen.ingest` logger, exit codes 0 / 1 / 2
  / 6 / 130, `--debug` for tracebacks.

## Two modes

```bash
# Browser app — drag the PDF, click Extract, download JSON
qscreen-app                                # localhost:8765

# CLI — scriptable, idempotent batch
qscreen-ingest QNB_AR_2023.pdf \
  --symbol QNBK --year 2023 --period FY

# Resumable batch over a manifest
qscreen-ingest --manifest tasks.jsonl --jobs 8 --resume

# Fingerprint diff between two filings
qscreen_fingerprint.py diff before.json after.json
# → {added: [...], removed: [...], modified: [...], unchanged: [...]}
```

## How it stacks up, honestly

The bench against the 8 hand-verified filings:

| Case | Check-level accuracy |
|---|---|
| `akhi_2022_fy` (insurance) | 10 / 11 |
| `iqcd_2022_fy` (industrial) | 14 / 16 |
| `qeti_2022_q4` (ETF) | 9 / 11 |
| `qgmd_2021_fy` (real estate, bilingual) | 12 / 15 |
| `qibk_2023_fy` (Islamic bank) | 15 / 21 |
| `qnbk_2023_fy` (conventional bank) | 19 / 26 |
| `udcd_2022_fy` (industrial) | 11 / 13 |
| `vfqs_2013_fy` (real estate) | 10 / 11 |

The "what's missing" on each row is documented in `tests/golden/` —
it's the regression backlog, not a black box. If you can fill a gap,
the test harness will hold your fix accountable.

## Why I'm posting this here

The tool is at the engineering ceiling: 480 tests, a reproducible
golden-set, CI on five Python versions, an honest baseline that
deliberately stopped pre-filling values so it measures real regression
risk. The remaining gap is **reach**, not code. PyPI publishing is
one maintainer UI click away (GitHub Actions + PyPI Trusted
Publishers / OIDC; no tokens). A second jurisdiction profile (UAE)
would roughly double the addressable market.

What I cannot do alone: drop the project into a community where it
solves an active problem. If you've ever wanted a fingerprintable,
diff-able, jurisdiction-aware filing JSON record for a quant model,
an IR pipeline, or a regulatory audit — try it on one filing and
open an issue with what breaks.

- Repo: <https://github.com/Mine-FNL/qstocks-filing-tool>
- `pip install qscreen-filing-tool` (publishing through PyPI Trusted
  Publishers; OIDC, no tokens — the maintainer registers the pending
  publisher once and every subsequent release is a tag push)
- `git clone` + `pip install -e ".[dev]"` + `qscreen-app`

Thanks for the eyeballs.

— Mine-FNL maintainers
