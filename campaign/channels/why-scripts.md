# Why-video scripts — production notes

Three short videos (6 s each, 768p) that translate the project's
WHY into something a viewer can grasp in 10 seconds. The native
audio on the first one (H3-Max) shipped with a data-stream whoosh;
the other two are silent Token-Plan Hailuo clips and look for a
subtitle-driven experience — pair them with a banner card that
states the headline in the post body.

## When to use them

| Video | Drop it into |
|---|---|
| **why-video-1-pain-vs-fix.mp4**       | The first comment reply on HN. X thread tweet #2 (right after the hook). LinkedIn cover. Reddit r/MachineLearning top of selftext. |
| **why-video-2-gate-blocks-silent-failure.mp4** | X thread tweet #7 (architecture-explainer slot). Reddit r/quant top of selftext ("the math is the magic"). LinkedIn mid-post reply to "what does this do that other tools don't". |
| **why-video-3-fingerprint-magic.mp4** | HN reply to "how do I know the data is stable across versions". Reddit reply to "what's the upgrade story for an in-flight data pipeline". LinkedIn reply to the head-of-data-eng who always asks about idempotency. |

The three videos cover the WHY in three passes that read together:
1. **Pain**: what was broken.
2. **Magic sauce**: the math-identity gate that fixes it.
3. **Proof**: the fingerprint that makes it durable.

## Production notes

- The H3-Max first clip shipped with audio; the Hailuo clips are
  silent. If your channel supports muted autoplay (HN, Reddit
  don't; X, LinkedIn do), drop them in. Otherwise the still
  thumbnail needs to do the work and a one-line caption goes
  alongside.
- All three videos deliberately have **no humans, no faces**.
  Per the campaign brief: the audience is technical and a person
  in frame would read as marketing.
- Color palette: midnight navy (#0d1117) + cyan (#58a6ff) +
  emerald (#28a745 for the gate-success state) + crimson (the
  GATE-BLOCKED seal). Matches the hero banner + stats card so the
  brand reads consistently across the campaign's moving and
  still assets.

## Per-video narrative (for use in captions, post text, etc.)

### 1. why-video-1 — Pain vs Fix

> Today's PDF extractors are slow (5 s per filing × index-rebalance
> cadence = minutes of waiting), expensive (~$0.15/filing with
> vendor APIs adds up at index scale), and **silent about their own
> failure modes** (LLM outputs land a BS_TOTAL_ASSETS that
> contradicts L + E by 4 %; nobody notices).
>
> qscreen-filing-tool: deterministic, ~3 s per filing, $0, and the
> math-identity gate runs BEFORE the JSON ships.

### 2. why-video-2 — Gate Blocks Silent Failure

> Most extractors ship the JSON regardless of internal consistency.
> qscreen-filing-tool's gates engine checks Assets = L + Equity
> with ±2 % tolerance *and 11 cross-cutting + 25 issuer-specific
> pre-flag rules* (UDCD IP at 47 % of TA, ZHCD qualified auditor
> history, QIGD's 3 entity renames, etc.). If a record contradicts
> itself, **the record doesn't ship** and the evidence points at
> the offending line item.

### 3. why-video-3 — Fingerprint Magic

> Stability across versions: re-ingesting the same PDF on any
> engine commit produces a JSON with the **same SHA-256
> fingerprint**. The data is bit-identical across engine upgrades.
> Add Sigstore keyless signing and you can cryptographically prove
> "this PDF produced this JSON on this commit". Audit trail that
> works without trusting the operator.
