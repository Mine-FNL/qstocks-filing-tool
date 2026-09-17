# Usage

Everything below assumes `qscreen-ingest` is on your `$PATH` (installed
via `pip install …` from any of the three paths in [Install](install.md)).
Replace `qscreen-ingest` with `python3 -m qscreen_ingest` if you cloned
the repo and didn't install.

---

## The one command — PDF → everything

```bash
qscreen-ingest path/to/QNB_AR_2023.pdf \
  --symbol QNBK --sector islamic_bank --year 2023 --period FY \
  --dry-run \
  --export xlsx --export html --export csv \
  --analyze --report --price 16 --shares 9200000000
```

Outputs (in the current directory):

| File | What |
|---|---|
| `<SYM>_<YEAR>_<P>_filing.json` | the **qscreen.app-uploadable** document |
| `<SYM>_<YEAR>_<P>_filing.xlsx` | the **Excel transcript** (Summary + statements + multi-year grid) |
| `<SYM>_<YEAR>_<P>_statements.html` | the printable **statements document** |
| `<SYM>_<YEAR>_<P>_filing.csv` | flat line-items table |
| `<SYM>_<YEAR>_<P>_analysis.json` / `_valuation.json` | ratios, red flags, DCF |
| `<SYM>_<YEAR>_<P>_report.html` / `.md` | the one-page **analyst report** (with charts) |

`--dry-run` extracts and writes everything **without** uploading — always
do your first run this way and inspect the JSON. Drop `--dry-run` and
ensure `INGEST_TOKEN` is set to upload to qscreen.app.

## Modes: `--basic` vs `--pro` vs `--no-llm`

The engine has three extraction strategies. Pick with `--mode`, or use
the shortcut flag.

| Flag | Strategy | When to use it |
|---|---|---|
| `--no-llm` | Deterministic only — reads line items from the PDF tables and **never** calls the model. Audit stays `unknown`, notes stay `[]`. | Auditing the regex/table pipeline; CI without a key; smoke tests |
| `--basic` / `--guided` | Deterministic-first, with a small / local model filling opinion + notes in rule-guided steps. | Tiny local runtimes (Ollama, llama.cpp, mlx-lm, LM Studio) |
| `--pro` / `--no-guided` | Single big-prompt extractor — the model does everything. | Strong cloud models (Claude, GPT-4, Moonshot, etc.) |
| *(default)* `--mode auto` | `basic` for local runtimes, `pro` for cloud providers (auto-detected). | When you're not sure |

Add `--guided-notes` to make `basic` mode also do a best-effort pass over
the accounting notes.

## Full flag table

This is the live output of `qscreen-ingest --help`:

```
usage: python3 -m qscreen_ingest [-h] [--version] [--symbol SYMBOL]
                                 [--jurisdiction JURISDICTION]
                                 [--currency CURRENCY] [--framework FRAMEWORK]
                                 [--sector {conventional_bank,islamic_bank,industrial,insurance,other}]
                                 [--no-auto-detect] [--year YEAR]
                                 [--period {FY,Q1,Q2,Q3,Q4,H1,9M}]
                                 [--provider {anthropic,apple,claude,custom,gpt,gpt4all,jan,kimi,llama-cpp,llama.cpp,llamacpp,lm-studio,lm_studio,lmstudio,local,minimax,mlx,mlx-lm,moonshot,oai,ollama,openai,openrouter}]
                                 [--base-url BASE_URL] [--model MODEL]
                                 [--list-providers] [--max-tokens MAX_TOKENS]
                                 [--timeout TIMEOUT] [--retries RETRIES]
                                 [--pages-per-chunk PAGES_PER_CHUNK]
                                 [--overlap OVERLAP] [--no-chunk]
                                 [--ocr {auto,never,always}] [--no-json-mode]
                                 [--mode {auto,basic,pro}] [--basic] [--pro]
                                 [--no-llm] [--guided] [--no-guided]
                                 [--guided-notes] [--export {csv,xlsx,html}]
                                 [--analyze] [--with-analysis] [--report]
                                 [--price PRICE] [--shares SHARES]
                                 [--manifest MANIFEST] [--resume]
                                 [--jobs JOBS] [--state-db STATE_DB]
                                 [--llm-key LLM_KEY] [--api-url API_URL]
                                 [--upload-retries UPLOAD_RETRIES]
                                 [--upload-backoff UPLOAD_BACKOFF]
                                 [--upload-timeout UPLOAD_TIMEOUT]
                                 [--token TOKEN] [--dry-run] [--self-test]
                                 [--quiet] [--debug]
                                 [pdf]
```

A few flags worth highlighting:

- `--no-auto-detect` — turn off sector / period / framework inference from
  the filing's cover page. The engine will require explicit `--sector`,
  `--period`, `--framework`.
- `--no-json-mode` — some providers reject `response_format=json_object`.
  Use this if you see empty or malformed responses from one provider.
- `--ocr always` — force OCR for every page (default `auto` only OCRs
  near-empty pages). Needs the `ocr` extra.
- `--quiet` — suppress the friendly progress prints; only the structured
  `qscreen.ingest` logger output is written. Useful in containers / CI.
- `--debug` — show Python tracebacks on errors. Default is a clean
  diagnostic + non-zero exit.

## Batch mode — `--manifest --jobs --resume`

For hundreds of filings, use a CSV manifest:

```csv
pdf,symbol,sector,year,period
reports/QNBK_AR_2023.pdf,QNBK,islamic_bank,2023,FY
reports/QIBK_AR_2023.pdf,QIBK,islamic_bank,2023,FY
reports/AKHI_AR_2022.pdf,AKHI,insurance,2022,FY
```

```bash
qscreen-ingest --manifest manifest.csv --dry-run --export xlsx --analyze --jobs 4
```

`--jobs N` runs N rows in parallel (default 1, max 8 recommended — each
worker reuses `INGEST_TOKEN`, so lower it if you see HTTP 429s).

### Resume

`--resume` skips rows already marked done/uploaded by an earlier run of
the same manifest. State lives in `~/.qstocks-filing-tool/state.db`
(SQLite); override with `--state-db /path/to/state.db`.

The state machine is **atomic `claim_row`** — multiprocessing-safe. A
crashed run picks up exactly where it left off, with no double-processing
or duplicate uploads. Combined with `If-None-Match: <fingerprint>` on the
upload, the same filing never goes to qscreen.app twice.

```bash
# First run — downloads 200 reports, kills it at #87
qscreen-ingest --manifest manifest.csv --jobs 4
# ^C

# Resume — picks up at #88
qscreen-ingest --manifest manifest.csv --jobs 4 --resume
```

## Outputs and exports

- `--export csv` — flat line-items table, one row per account.
- `--export xlsx` — multi-sheet Excel transcript (Summary, IS, BS, CF,
  Notes, Multi-year grid).
- `--export html` — printable statements document.
- `--analyze` — also writes `_analysis.json` + `_valuation.json`
  (ratios, red flags, DCF inputs).
- `--report` — also writes `_report.html` + `.md` (the one-page analyst
  report with charts).

`--export` is repeatable; `--analyze` and `--report` are flags.

## Audit + segments + notes — what the engine extracts

For every PDF, the engine emits one JSON object that captures:

- **Audit opinion** — unqualified / qualified / adverse / disclaimer, plus
  the qualification language (auto-extracted by the LLM pass; in
  `--no-llm` mode the audit stays `unknown`).
- **Segments** — by geography and by business line, with the issuer's
  own vocabulary (e.g. `by_geography: ["Qatar", "UAE", "Turkey"]`).
- **Statements** — full IS, BS, CF, with line items + currency + unit +
  provenance (page number, table-id).
- **Notes** — accounting notes (in `--basic` + `--pro` mode).
- **Provenance** — every value carries a `source: {page, table_id,
  text_anchor}` reference. No values are invented; illegible cells are
  `null` with a warning.
- **Fingerprint** — `metadata.fingerprint` (SHA-256 over the
  whitespace-normalized audit + statements + notes, order-independent
  overall).

## Re-run a single filing → see what changed

```bash
# First run
qscreen-ingest QNBK_AR_2022.pdf --symbol QNBK --year 2022 --period FY

# Later run on a re-filed PDF
qscreen-ingest QNBK_AR_2022_v2.pdf --symbol QNBK --year 2022 --period FY

# Diff the two
python -m qscreen_fingerprint print QNBK_2022_FY_filing.json
python -m qscreen_fingerprint diff  QNBK_2022_FY_filing.json QNBK_2022_FY_filing_v2.json
```

The diff output shows exactly what changed: restated number vs.
footnote edit vs. audit qualification vs. fingerprint-only.

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | success (saved locally and/or uploaded) |
| `1` | generic error |
| `2` | contract problem — non-conforming extract (saved but **never** uploaded) |
| `6` | upload failed after retries |
| `130` | user interruption (`Ctrl-C`) |

## Next

- → [Architecture](architecture.md): data flow, gates, state, fingerprints.
- → [Jurisdictions](jurisdictions.md): how to drop in a new
  `profiles/<cc>/`.