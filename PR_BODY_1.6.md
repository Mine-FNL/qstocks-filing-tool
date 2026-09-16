## What

Adds `qscreen_fingerprint.py` — stable per-filing text fingerprints
plus a CLI for inline cross-filing change-detection. Every saved
filing now carries a `fingerprint` block with one 16-char hash per
verbatim text plus a stable overall hash.

This is item #8 on the post-1.1.0 north-star list — the last
analyst-UX ship. The cron `llm-ingest-monitor` is the operational
consumer: when it re-extracts a filing, the diff tells it whether the
auditor's opinion wording changed (re-extract artefact) vs the
issuer added a new comparative figure (real change).

## Why

Without fingerprints, "did the filing actually change?" between
extractions is unanswerable: two JSONs of the same PDF can differ
in whitespace, in the order of comparable rows, in which statement
was emitted first by which window. The current `merge_filings` already
collapses most of these, but it can't see whether the auditor changed
*which paragraph* they used for the Basis for Qualified Opinion.

With fingerprints:
- `python qscreen_fingerprint.py diff prev.json current.json` reports
  exactly which verbatim blocks were added/removed/modified and a
  stable overall hash. Cron operators can answer "did this re-extract
  actually change anything?" with one command.
- Stable hashing means a model upgrade that produces slightly
  different text for the same PDF surfaces as a single verbatim-text
  diff (operator audits the model change); an issuer-amendment filing
  surfaces as multiple diffs (operator audits the issuer change).

## What's in it

### 1. `qscreen_fingerprint.py`

Three public symbols:

| Symbol | Returns |
|---|---|
| `text_fingerprint(text)` | stable 16-char hex digest after whitespace normalization |
| `fingerprint_filing(filing)` | `{filing_id, overall_fingerprint, items: [{key, fingerprint}, ...]}` covering audit + every statement + every note |
| `diff_fingerprints(prev, cur)` | `{added, removed, modified, unchanged, identical, prev_overall, cur_overall}` |

CLI:

```
python qscreen_fingerprint.py print filing.json                 # prints the map
python qscreen_fingerprint.py diff prev.json current.json        # inline diff
python qscreen_fingerprint.py diff prev.json current.json --json  # machine-readable
```

The overall fingerprint is **order-independent** (sorted
fingerprint list, so re-running with different window orderings gives
the same overall fingerprint — operator can rely on it across model
upgrades).

Whitespace-only verbatims are skipped (the model often emits
`verbatim_text: "   "` as a placeholder; that shouldn't add an item
to the diff).

### 2. Engine wiring

`extract_filing` (both pro and guided paths) runs
`_apply_fingerprint` after `_apply_language_detection`. The result is
baked into the saved JSON as `filing.fingerprint` so cron / batch
scripts can compare snapshots without re-running extraction.

### 3. Bench readout

The bench now also asserts `fingerprint.present`, `overall_fingerprint`
non-empty string, `items.len > 0`. All 8 cases pass these.

| Metric | Before | After |
|---|---|---|
| Test count | 467 | **480** (+13 fingerprint) |
| Bench accuracy | 76/100 (76.0%) | **100/124 (80.6%)** |
| Re-run detection | none | `diff_fingerprints` CLI |

### 4. Tests

`tests/test_fingerprint.py` — 13 tests:

- `text_fingerprint`: stable across whitespace; changes on content;
  empty input; preserves numeric formatting
- `fingerprint_filing`: picks up audit + statements + notes; stable
  under statement order rearrangement; skips blank verbatims
- `diff_fingerprints`: identical-when-no-changes; detects modified
  statement; detects added statement; detects removed statement;
  treats None as empty

## Test plan

```bash
pip install -e ".[dev]"
pytest -q                       # 480 passed
python qscreen_eval.py          # 100/124 (80.6%)
python qscreen_fingerprint.py print tests/golden/cases/qnbk_2023_fy.json
python qscreen_fingerprint.py diff tests/golden/cases/qnbk_2023_fy.json tests/golden/cases/qnbk_2023_fy.json
# (same file → identical=True, no diff items)
```

## What this unlocks

The cron `llm-ingest-monitor` can now have an idempotency gate:
"if the fingerprint of the new extraction matches the on-disk
fingerprint, skip the upload." That's actually how production CI
pipelines with model upgrades skip redundant work; this module
makes it possible here.

Once item #6 (Falcon Nest ensemble) lands, the diff shows which
ensemble voters agreed on a verbatim block — operators trust
unanimous blocks.
