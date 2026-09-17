# Golden-set bench

The bench is the engine's regression gate. It runs a hand-verified set
of **real QSE filings** against the engine and reports per-case,
per-check accuracy. A check fails when the engine output doesn't
match the expected value (rounded to the issuer's reported unit).

The bench is **not** a unit test suite — it's an end-to-end accuracy
report on real PDFs, with the output of every check preserved for
diff inspection.

---

## Baseline

- **Cases**: 8 (8 issuers, 8 fiscal years)
- **Checks**: 124 (15–26 per case)
- **Pass**: 100 / 124 (80.6 %)
- **Cases** (each row = one real annual or interim report):

| Issuer | Year | Period | Pass | Total |
|---|---|---|---:|---:|
| AKHI | 2022 | FY | 10 | 11 |
| IQCD | 2022 | FY | 7 | 16 |
| QETF | 2022 | Q4 | 9 | 11 |
| QGMD | 2021 | FY | 12 | 15 |
| QIBK | 2023 | FY | 15 | 21 |
| QNBK | 2023 | FY | 19 | 26 |
| UDCD | 2022 | FY | 11 | 13 |
| VFQS | 2013 | FY | 10 | 11 |

The 80.6 % baseline is **captured** — both the bench harness and the
bench-regression CI gate refuse to publish a release whose accuracy
drops below it.

## Run the bench

```bash
# Markdown report (default; pretty-printed)
python qscreen_eval.py --md

# JSON report (machine-readable; for the demo page builder)
python qscreen_eval.py --json --out /tmp/bench.json

# HTML report (one self-contained file)
python qscreen_eval.py --html --out /tmp/bench.html
```

The bench reads the golden set from `tests/golden/` (one
`<TICKER>_<YEAR>_<PERIOD>.json` per case, hand-verified), runs the
extractor on the source PDF under `tests/golden/cases/`, and reports
the diff. There's no external state — the bench runs offline once
the model weights are cached.

### Update the demo page

The live demo at
[mine-fnl.github.io/qstocks-filing-tool/demo.html][demo]
is auto-generated from the bench JSON. Locally:

[demo]: https://mine-fnl.github.io/qstocks-filing-tool/demo.html

```bash
python qscreen_eval.py --json --out /tmp/bench.json
python docs/build_demo.py /tmp/bench.json
```

The CI pipeline runs this on every `v*` tag push (see
`.github/workflows/release.yml`).

## What the bench measures

Each case is a list of **checks**. A check has:

- `path` — a JSON pointer into the produced filing
  (e.g. `statements.income_statement.revenue`).
- `expected` — the hand-verified value from the source PDF.
- `actual` — the engine's value for the same pointer.
- `result` — ✅ / ❌.

Typical checks:

- `metadata.symbol`, `metadata.fiscal_year`, `metadata.fiscal_period`
- `metadata.sector`, `metadata.currency`
- `statements.income_statement.revenue`
- `statements.balance_sheet.total_assets`,
  `statements.balance_sheet.total_liabilities`,
  `statements.balance_sheet.total_equity`
- `statements.cash_flow.operating_cash_flow`
- `pre_flags.contains <rule_id>` — did the engine emit the
  issuer-specific red flag?

Failing checks surface a **non-blocking** warning in the bench output
— the engine is allowed to ship if it regresses within the captured
baseline, but every failure is logged for follow-up.

## Adding a new case

!!! info "When to add a case"
    When you find a filing whose shape the engine handles *incorrectly*
    or *uniquely*, add it to the golden set. A new case becomes a
    permanent regression check for every future change.

A new case is two files plus a one-line registration:

1. **`tests/golden/<ticker>_<year>_<period>.json`** — the hand-verified
   expected values. Use the same shape as the existing cases (run
   `python qscreen_eval.py --md` and look at the output format). Take
   values directly from the PDF page text — **don't** take them from a
   previous engine run (that's circular).

2. **`tests/golden/cases/<ticker>_<year>_<period>.txt`** — the source
   PDF's per-page plain text, one page per line, UTF-8, no headers.
   The bench feeds this into the engine's text path without needing
   the original PDF (PDFs are too big to commit; the bench uses the
   pre-extracted text).

3. **`tests/golden/BASELINE.md`** — the captured baseline table that
   the regression gate compares against. Append a row for the new
   case and bump the captured score.

4. **Update `tests/test_eval.py`** to register the new case (look for
   `CASES` / `EXPECTED_DIR` — they're a small list, easy to extend).

Open a PR with all four. The PR-time bench workflow
(`.github/workflows/bench.yml`) will run the new case, show the diff
in the PR comment, and refuse to merge if the bench regresses below
the captured baseline.

### Why the bench isn't a unit test

Unit tests assert invariants of the code. The bench asserts accuracy
on **real PDFs that no automated test could produce**. The bench's
job is to catch the kind of regression a unit test couldn't see:

- A new prompt that *seems* cleaner but drops a numeric field.
- A schema rename that updates the engine but breaks a downstream
  consumer's pointer.
- An issuer-specific fact that was encoded by hand and is now
  obsolete (e.g. a company that re-listed, was acquired, or changed
  reporting framework).

The 80.6 % baseline isn't a target — it's a floor. A future PR that
raises it (by improving prompts, adding a gate, fixing an
issuer-specific bug) is a free accuracy win and should be merged
without changing the engine version.

## CI gate

The bench runs in three places:

1. **On every PR** (`.github/workflows/bench.yml`, job *Bench*) —
   non-blocking comment with the current accuracy + the diff.
2. **On every push to main** — same as above, no comment.
3. **On every `v*` tag push** (`.github/workflows/release.yml`, job
   *Bench regression gate*) — **blocking**. Refuses to publish a
   release whose accuracy drops below the captured baseline.

The weekly cron run (Mondays 06:00 UTC) posts the latest accuracy to
the Actions step summary, so silent dependency regressions surface
on the dashboard.

## Live demo

The live demo at [mine-fnl.github.io/qstocks-filing-tool/demo.html][demo]
is the bench JSON rendered as a self-contained HTML page, with a
sample engine-output snippet and per-case accuracy. It is regenerated
on every release tag.

## Next

- → [CI workflows](ci.md): the four GitHub Actions that wrap the
  engine.