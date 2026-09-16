## What

Three "never drop" improvements from the post-1.1.0 north-star review —
gates, pre-flag catalog, and idempotent batch — shipped together as 1.2.0.
None of these are features; they're **the layer of correctness and durability
the production cron (`llm-ingest-monitor`) used to enforce by hand**.

## Why

- The cron explicitly had to invent bookkeeping to survive re-runs. The
  pre-flag catalog lived in `memory/qse-filings-extraction.md` (markdown)
  but never reached the LLM or the resulting JSON. Skeleton filings
  (80 %+ line-items null) saved against the schema and ate analyst time
  on qscreen.app.
- Every one of these gates was a Slack message and a manual file edit.
  Putting them in the tool turns "this filing was junk" into a skip in
  the manifest run.

## What's in it

### 1. Post-extraction gates (`qscreen_gates.py`)

A second pass after `validate_filing`. Three classes of check:

- **Skeleton detection** — filing where 80 %+ of `line_items[].value` is
  null is a skeleton; refuse to save, write `*_filing.error.json`.
- **Math identity** — `TotalAssets ≈ TotalLiabilities + TotalEquity`,
  `GrossProfit = Revenue − CostOfSales` (sign-aware so the rule works
  whether the model wrote `700` or `-700`). Tolerance: 1 % relative or
  10 absolute.
- **Currency / unit sanity** — `metadata.currency` is ISO-4217-shaped;
  `metadata.unit_scale ∈ {1, 1000, 1_000_000}`.

A `block_save` finding exits with code **6** (distinct from validate's 2)
and writes the structured error sidecar. A `warn` finding is appended to
`extraction_quality.warnings[]` with a dict-form record (rule + severity +
evidence) so downstream UI can render the rule.

### 2. Pre-flag catalog in code (`profiles/qatar/pre_flags.py`)

The QSE-specific knowledge from `memory/qse-filings-extraction.md`,
machine-readable and executed on every merged filing:

- 11 cross-cutting rules: KAM-intangibles, going-concern structural
  break (2+ consecutive), qualified-review insurance reserves,
  qualified-basis-surfacing, AFS-dominates-NI, AFS-share-of-equity,
  rate-swap-5 %-TL, IP-40 %-TA concentration, IFRS-9 transition flag,
  dual-IS takaful detector, non-standard first-reporting-period.
- 25 issuer-specific facts (ZHCD 8-yr qualification, DUBK goodwill
  fragility, AKHI takaful-misclassification, QIGD entity reassigned 3×,
  UDCD IP at 47 % of TA, QFLS auditor-change + reclassification, …).
- Dynamic dispatch for known issuer renames (VFQS, QETF, QATR, QIGD).

Output: `red_flags[]` array (`{rule, severity, ticker, fiscal_year, message, evidence}`)
plus string entries appended to `extraction_quality.warnings[]`. The
catalog has zero new network/parsing dependencies — it reads the merged
JSON the engine already produced.

### 3. Idempotent batch (`qscreen_state.py`)

`~/.qstocks-filing-tool/state.db` (SQLite, overridable via
`QSCREEN_STATE_DB` / `--state-db`) tracks per-row progress:

```
manifests(manifest_id PK, started_at, finished_at, row_count, completed_count, error_count)
rows(manifest_id, row_index, dedup_key UNIQUE, status, filing_id,
     last_error, attempted_at, uploaded_at)
```

- `dedup_key = SHA256(symbol + fiscal_year + fiscal_period + content_sha256)`.
  Same key is sent as `If-None-Match` on the upload so a compatible
  ingest endpoint returns `412 Precondition Failed` for duplicates and
  charges **no API spend** on re-runs.
- `claim_row()` is atomic; only one worker can transition
  `pending → in_flight`, so concurrent `--jobs N` never double-processes.
- `reset_in_flight()` on manifest start re-claims rows that crashed
  mid-flight in an earlier run.
- New CLI flags: `--resume` (skip done/uploaded), `--jobs N` (process
  pool, default 1 / `QSCREEN_JOBS`), `--state-db PATH`.
- `BatchState` is the single source of truth; `run_filing` writes to
  it after every success/upload/error so a SIGKILL leaves the db in a
  recoverable shape.

### Engine wiring

- `extract_filing` runs the pre-flag catalog on the merged result (one
  call site, two paths: pro-mode and guided-mode).
- `run_filing` runs the gates after `validate_filing`; a `block_save`
  exits with code 6, writes `*_filing.error.json`, and skips the upload.
- `upload_filing` takes an optional `dedup_key`; when set, sends
  `If-None-Match`, treats `412` as `{"status":"duplicate"}` without
  retrying, and adds `User-Agent: qscreen-filing-tool/1.2.0`.
- `run_batch` is rewritten to dispatch through `BatchState` and a
  `multiprocessing.Pool`. Each worker re-opens its own `BatchState`
  connection to the same SQLite file (atomic per-row claims keep the
  file race-free).

### Tests

- `tests/test_gates.py` — 14 tests: skeleton (3), BS identity (4),
  IS subtotals (2), metadata sanity (3), merge_warnings (1).
- `tests/test_pre_flags.py` — 15 tests: dispatch, issuer facts, going
  concern, insurer reserves, AFS dominance, dual-IS takaful, merge
  idempotency.
- `tests/test_state.py` — 14 tests: dedup_key stability, manifest
  lifecycle, row lifecycle, atomic claim, resume path, override.

**Suite: 435 passed** (392 → 435; net +43). `python qscreen_ingest.py
--self-test` still green.

### Versioning

- `__version__` 1.1.0 → 1.2.0 (auto-pulled into the wheel metadata via
  the dynamic attr).
- `[project].description` unchanged: jurisdiction-agnostic framing
  stays accurate.

## Backward compatibility

- All 392 pre-existing tests still pass.
- The legacy CLI surface (`--manifest`, `--dry-run`, `--resume`,
  `--jobs`, `--state-db`) is additive; existing callers that don't
  pass `--resume` get the old "rerun everything" behaviour.
- `qatar.export_json()` and `import qatar` paths still work; they
  don't need to know about the new modules.
- The cross-cutting pre-flag rules are **extra output** — every
  `red_flags[]` entry has a `rule` field so an old consumer can
  ignore them safely.

## Test plan

```bash
pip install -e ".[dev]"
python qscreen_ingest.py --self-test       # green
pytest -q                                  # 435 passed
# Batch state machine sanity:
python -c "from qscreen_state import BatchState, dedup_key; print(dedup_key('QNBK',2023,'FY','sha256:abc'))"
```
