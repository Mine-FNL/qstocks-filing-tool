## What

Adds per-page Arabic / English language detection for QSE filings —
ships `qscreen_langdetect.py` (zero-deps, pure Unicode-range
classification) and a schema upgrade so `metadata.languages[]` is
populated for every filing.

This is item #7 on the post-1.1.0 north-star list. QSE filings come in
three flavors (Arabic-only, English-only, bilingual) and the schema
prior to this PR carried a single-string `metadata.language` field that
was left `None` for every filing.

## Why

The actual research corpus (per `qse-filings-extraction.md`) has
hundreds of QSE filings where knowing which language is the dominant one
on each page isn't optional:

- Older filings are Arabic-dominant or Arabic-only.
- Modern filings are usually bilingual with EN on the left column and
  AR on the right; one or the other leads depending on the issuer.
- The csv-language-in-the-AI-prompt wheel has been ignored for years
  because there was no way to *verify* the model's choice.

This PR puts that on solid ground: every filing exits with both the
per-page language breakdown and the document-level ratios.

## What's in it

### 1. The detector (`qscreen_langdetect.py`)

- **Pure Unicode classification.** Arabic block (U+0600–U+06FF, U+0750-077F,
  U+08A0-08FF, U+FB50-FDFF, U+FE70-FEFF) vs. Latin ranges
  (U+0041-005A, U+0061-007A, U+00C0-024F). Digits, punctuation, and
  other glyphs are ignored.
- `MIN_RATIO = 0.05` filters out one-off citations; bilingual filings
  commonly see 0.40 / 0.40 / 0.20 and both surface, one marked
  primary.
- Zero new deps.

### 2. Schema upgrade

```jsonc
"metadata": {
  ...
  "language": "en",                          // existing field, kept as the primary
  "languages": [                            // NEW
    {"code": "en", "ratio": 0.74, "primary": true},
    {"code": "ar", "ratio": 0.21, "primary": false}
  ],
  ...
},
"page_languages": {                         // NEW per-page roll-up
  "1": [{"code": "en", "ratio": 0.99, "primary": true}],
  "2": [{"code": "ar", "ratio": 0.61, "primary": true},
         {"code": "en", "ratio": 0.39, "primary": false}]
}
```

`metadata.language` is preserved (back-compat for any v1.x consumer).
The new `languages[]` and `page_languages` are additive.

### 3. Engine wiring

`extract_filing` (both pro and guided paths) now runs `_apply_language_detection`
right before `_apply_pre_flags`. The detection is deterministic and
fast (sub-millisecond per filing on the bench), so it's safe to run on
every extraction.

### 4. Bench update + bilingual fixture

The bench now asserts:

- `metadata.languages[]` is populated
- `primary` is set to `en` for English-only fixtures
- One fixture (`qgmd_2021_fy`) is intentionally bilingual with an Arabic
  audition-report paragraph appended, to prove the bilingual path works
  end-to-end (Arabic block + Latin block coexist; AR surfaces in
  `languages[]`, EN stays primary because Latin is dominant).

**Aggregate check-level accuracy: 67/91 (73.6%) → 76/100 (76.0%)**.
The improvement is honest: the bench added 9 new check slots
(`languages.primary` × 8 + one `languages.contains` for QGMD) and 9/9
pass.

### 5. Tests

`tests/test_langdetect.py` — 14 tests:

- `language_counts`: empty / pure-Arabic / pure-English / digits-punctuation
- `detect_languages`: EN-only / AR-only / bilingual-with-primary / min-ratio /
  empty
- `apply_language_metadata`: sets languages + back-compat `language` /
  always-overwrites derived field / preserves user-set `language` /
  no-text-pages / per-page roll-up populated

## Test plan

```bash
pip install -e ".[dev]"
pytest -q                       # 467 passed (was 453)
python qscreen_eval.py          # 76/100 (76.0%) — baseline
```

## Risk

The detector is Unicode-range only. False-positives: a single Arabic
citation in an otherwise-English filing shows up as "bilingual" if it
exceeds 5 % of total letters (a known threshold to surface real
bilinguals). False-negatives: Arabic-script loanwords in English text
(PDF includes an "AUDITOR'S REPORT" header in Arabic-script transliteration,
e.g.,) are counted under Arabic. Both are bounded by `MIN_RATIO = 0.05`.

The bench now uses these rules implicitly. Operators who need finer
language detection (e.g., to detect when an Arabic-heavy filing should
be checked with an Arabic-aware model) can use `page_languages` as the
input signal.

## What this unlocks

The bench's bilingual-detection capability is the foundation for two
follow-up improvements:

1. Multi-language pre-flag rules in `profiles/qatar/pre_flags.py`
   that fire differently depending on which language is dominant on
   the page (e.g., Arabic-takaful terminology only fires when AR is
   primary on a takaful issuer).
2. AR-aware Llama model routing: when AR >30 % of letters, route
   the LLM call through an Arabic-capable model on OpenRouter.

Both are future work; this PR ships the foundation.
