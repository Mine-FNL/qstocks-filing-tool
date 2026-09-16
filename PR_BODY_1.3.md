## What

Adds the **golden-set evaluation harness** — `qscreen_eval.py` — that
exercises the engine on hand-verified extraction targets and emits a
Markdown accuracy report. Plus 8 fixture cases spanning the 5 extraction
archetypes plus 3 known-tricky shapes.

This was item #5 on the post-1.1.0 north-star list ("ship the bench
before shipping the next feature so you can see if a new feature moves
the needle"). The 435-test pytest suite proves the *invariants* of the
engine; the bench proves the *values* it produces.

## Why

Three reasons.

- A regression in extraction quality (silent: a model upgrade breaks
  every account_code mapping) is invisible to the existing pytest. The
  bench is the only place where "did we return 1_077_000 for QNBK 2023
  Total assets?" is checked.
- The pre-flag catalog from 1.2.0 was hand-written; without a bench, the
  claims on each `issuer_fact_*` are not verifiable.
- A public accuracy number is the single missing piece for
  "star-worthy in a month" (per the honest scorecard in the prior
  thread): visitors land on the repo, see a baseline, believe the tool.

## What's in it

### 1. Golden fixtures (`tests/golden/cases/`)

8 hand-verified extraction targets in the engine's expected input format
(combined audit prose + `[TABLES on page N]` recovered-table markup so
the deterministic Basic path works):

| Case | Ticker | Year | Archetype | Why included |
|---|---|---|---|---|
| `qnbk_2023_fy` | QNBK | 2023 | conventional_bank | largest QSE issuer, must extract cleanly |
| `qibk_2023_fy` | QIBK | 2023 | islamic_bank | Sharia-specific line items, framework_variant |
| `iqcd_2022_fy` | IQCD | 2022 | industrial | revenue + COGS + GP math identity |
| `akhi_2022_fy` | AKHI | 2022 | insurance | known takaful dual-IS schema misclassification trap |
| `qgmd_2021_fy` | QGMD | 2021 | healthcare | going-concern / Article 295 / losses |
| `udcd_2022_fy` | UDCD | 2022 | real_estate | IP concentration 47% of TA KAM trap |
| `qeti_2022_q4` | QETF | 2022 Q4 | other | passive index ETF, P/B = 1.0x by construction |
| `vfqs_2013_fy` | VFQS | 2013 | telecom | FYE change Mar→Dec (9-month transition) |

Each case has expected metadata, expected statement line items
(by `account_code`), expected audit fields, and expected `red_flags[]`
rule hits.

### 2. The harness (`qscreen_eval.py`)

Single-file, no extra deps. Run with:

```
python qscreen_eval.py                       # console summary
python qscreen_eval.py --md --out report.md  # full Markdown report
python qscreen_eval.py --case qnbk_2023_fy  # one case
python qscreen_eval.py --json               # CI-friendly JSON
```

The harness:
- Runs the deterministic Basic path (`--no-llm`) so no API key needed
- Applies the gates + pre-flag catalog after extraction
- Compares per-key: metadata equality, audit opinion type, going-concern
  detection, line-item values (within 1% relative / 10 abs tolerance),
  issuer_fact presence, and pre-flag rule hit counts
- Emits a pass/fail per case + aggregate accuracy %

### 3. Baseline (current state)

**Aggregate check-level accuracy: 71/91 (78.0%)** with **1 of 8 cases
fully passing** (VFQS 2013 FY). Per-case scorecard is checked into
`tests/golden/BASELINE.md` so a regression breaks it visibly.

What passes today:
- BS_TOTAL_ASSETS / IS_NET_INTEREST / IS_REVENUE / etc. values extracted exactly
- Unit scale (1 / 1000) detected
- Audit opinion type classification (unqualified / qualified)
- Issuer-specific facts that don't depend on a missing audit field
- Akhi's takaful dual-IS detection (BF_input had xcut_dual_income_statement_takaful)

What doesn't pass (the next-iteration targets):
- Going-concern detection requires the LLM path (Basic mode regex misses
  the prose cue); CI gives the same result every run
- Some metric contracts haven't been written yet (cash flow code, KAM
  surface) — see the next phase of improvements

### 4. CI integration (`.github/workflows/ci.yml`)

The bench runs as a **non-gating step** on every PR. Output is uploaded
as an artifact (`golden-eval-<py-version>`) and the first 30 lines go
into `$GITHUB_STEP_SUMMARY`. The bench does NOT break the build when it
regresses; the regression is visible in the PR for human review.

Why non-gating: the `78.0%` baseline will fluctuate as the engine
improves; pinning it to "exactly baseline" would freeze progress. The
*human* on the PR sees the diff and decides whether the regression is a
bug or a feature. We'll tighten it to a hard gate when the bench proves
stable across three consecutive PRs.

## Test plan

```bash
pip install -e ".[dev]"
python qscreen_eval.py            # 71/91 (78.0%) — baseline
python qscreen_eval.py --md
pytest -q                         # 435 passed
python qscreen_eval.py --case vfqs_2013_fy   # only one passing case
```

## Risk

The tolerance on numeric checks (1% relative / 10 abs) is generous
enough to absorb ordinary rounding; the bench is *not* sensitive to
the trivial differences between "1 077 000" and "1077000" but DOES
catch the kind of off-by-10x errors that affect the productive pipeline.

Expanding the bench is welcome — `tests/golden/cases/` is a directory;
each new file is a new case. The 8 cases here were chosen to cover the
cartesian product of (archetype × known-tricky-shape), not to be
exhaustive. ~30-50 cases (the documented "1 of each tricky shape per
fiscal year") would put the bench in a position to function as the
public benchmark.
