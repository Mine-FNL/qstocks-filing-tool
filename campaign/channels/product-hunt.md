# Product Hunt launch kit

**Recommended day +5 to +10 after Show HN** so the maker comment can link
the HN thread as social proof. Product Hunt rewards daily-active makers; a
lone launch from a cold account underperforms a launch from a maker who
already has a public build-in-public trail.

## Pre-launch checklist (T-7 days)

- [ ] Maker account warmed up: 1 product review per day for 5 days,
      at least 1 reply on someone else's launch per day.
- [ ] Hunter identified (the account that submits the post). Some
      makers hunt their own; the upside is a stronger first-hour
      comment chain.
- [ ] Gallery images: 5 × 1272×760 PNGs (use `architecture-`,
      `hero-`, `demo-flow-`, `stats-card-`, `why-2-explainer-captioned`
      keyframe; convert to PNG with `sips -s format png <jpg>`).
- [ ] Thumbnail (240×240 PNG; the OG card at
      `mine-fnl.github.io/qstocks-filing-tool/og.png` resized is fine).

## Tagline (≤ 60 chars)

```
Open-weight PDF → lossless filing JSON for financial reports
```

## One-line description (≤ 260 chars)

```
qscreen-filing-tool turns any exchange's annual or interim report into a
schema-stable, audit-traceable JSON object. Math-identity gate refuses to
ship self-contradictory records. SHA-256 cross-filing fingerprints +
Sigstore keyless signing. 485-test suite, containerized, install via pip,
GitHub Releases, or ghcr.io.
```

## Topics

`Open Source`, `Developer Tools`, `Finance`, `Data`, `Python`

## Maker comment (the first comment from your maker account, post immediately)

```
👋 Maker here.

Two design decisions worth flagging because they aren't obvious from the
landing page:

1. **Deterministic-first extraction.** The PDF tables are read in code
   (`pdfplumber`); the LLM only fills gaps (audit opinion, notes,
   segments). This is why a 270M local model produces the same lossless
   contract as a frontier cloud model — numbers never pass through the
   LLM. So you can run fully offline for $0.

2. **The math-identity gate.** The JSON won't ship if `Assets ≠ L + E`
   within ±2%. Eleven cross-cutting + twenty-five issuer-specific
   pre-flag rules run before `save()`. If a record contradicts itself,
   the record doesn't ship and the evidence points at the offending
   line item.

Both of these are unusual in this space and were the actual reason we
built the tool — every existing option shipped the JSON regardless of
internal consistency, which makes downstream pipelines fragile.

Try it: `pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/latest/download/qscreen_filing_tool-1.6.0-py3-none-any.whl`
then `qscreen-ingest report.pdf --symbol <TICKER> --year <YYYY>`.

Happy to answer technical questions in the comments.
```

## First-hour reply playbook

| Comment type | Reply |
|---|---|
| "How is this different from [pdfplumber / camelot / marker]?" | Link to the comparison table in the README; emphasize the math-identity gate and SHA-256 fingerprint — neither of those exist in the alternatives. |
| "What about non-English filings?" | Engine is jurisdiction-agnostic; profiles are pluggable under `profiles/`. The default `qatar` profile ships, and AE / SA / KW are documented as one-directory-drop extensions. |
| "Does this need an API key?" | Optional. `--no-llm` runs without any model (numbers come from the PDF tables). With a key, the model fills gaps (audit opinion, notes, segments). Without a key, audit defaults to `unknown` and notes are `[]` — the numbers and the gate still work. |
| "What's the install footprint?" | One `pip install` away. The container (`ghcr.io/Mine-FNL/qstocks-filing-tool:v1.6.0`) is `python:3.11-slim` + the wheel; ~150MB. |
| "Why not use GPT-4o end-to-end?" | Three reasons: (a) non-deterministic JSON — you can't fingerprint it; (b) expensive per filing at scale; (c) silent on internal contradictions. The deterministic-first model treats the LLM as a classifier, not as the source of truth. |
| "What does the bench look like?" | `mine-fnl.github.io/qstocks-filing-tool/demo.html` — 124 cross-filing checks against the current Qatar-listed universe, currently 100/124 = 80.6%. The regression gate fails the PR if it drops. |

## Gallery images (5 × 1272×760)

1. **Hero** (`assets/hero-16x9.jpg` → PNG) — the headline card.
2. **Architecture** (`assets/architecture-16x9.jpg` → PNG) — the
   PDF → JSON pipeline diagram.
3. **Demo flow** (`assets/demo-flow-16x9.jpg` → PNG) — before/after.
4. **Stats card** (`assets/stats-card-16x9.jpg` → PNG) — the 80.6%
   bench + 485 tests + supply-chain attestations.
5. **Gate in action** — screenshot of `qscreen-eval` showing a flagged
   extraction (Assets ≠ L + E with evidence pointing at line item).
   Generate with `qscreen_eval --json report.pdf | jq '.gates[]'`.

## Day-of checklist

- [ ] Submit at 12:01 AM PT (PH resets at midnight PT; the top of
      the day is the top of the leaderboard).
- [ ] Post the maker comment within 30 seconds.
- [ ] Reply to every comment within 5 minutes for the first 4 hours.
- [ ] Share the launch on X at 8 AM PT with the captioned WHY-1 video.
- [ ] Don't ask for upvotes. The PH culture punishes it.

## What's *not* here

- A paid tier (PH rewards free tools more than freemium).
- A "Download for Windows" button (the Python install is the install;
  PH users skew technical and prefer the more flexible path).
- A live demo URL behind a login (the public demo is the bench
  report at `mine-fnl.github.io/qstocks-filing-tool/demo.html`).
