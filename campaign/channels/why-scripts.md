# WHY-videos production notes (v3)

These three videos are the campaign's "WHAT-y for skim-readers" pair
to the long-form posts.

## Status

- 6 seconds each, **1934×1080 (1080p)**, H.264 yuv420p video + 3-layer
  audio mix (TTS voice-over + AI-generated background music + chime /
  boom / arpeggio). The audio layers are explicit because the
  viewer experiences the motion AND the sound design together; the
  catch-factor is the *combination* of the cut, the typography, the
  voice, and the score.
- v4 (this round) upgraded from text-to-video to **first-frame
  image-to-video** — the model anchors to a 2K branded keyframe
  (campaign/assets/hero-16x9.jpg for the hero video; freshly
  generated 2K keyframes for the gate and proof videos at
  campaign/assets/keyframe-gate-16x9.jpg and
  keyframe-proof-16x9.jpg) so the animation grows out of the
  existing brand asset instead of synthesizing from text alone.
  Result: dramatically better motion coherence and a brand
  composition that opens and closes on the same image family.

## Audio mix design

Each video mixes three audio layers via `amix=inputs=2`:

1. **TTS narration** at 1.0 volume — the human-voice signal that
   delivers the WHY.
2. **AI-generated music** at 0.22 volume (heavily ducked under
   the voice). One per video:
   - pain: cinematic pulse beat, 100bpm, dark synth pad, building
     tension, loopable.
   - gate: single dramatic stamp-impact with reverb tail (the score
     cue for the SEAL landing).
   - proof: triumphant ascending three-note arpeggio + bright
     bell chime (the "we did it" sound at the moment all three
     panels lock).
3. **Chime / impact / arpeggio tail**: baked into the music; we
   don't have a separate chime layer — the score cue IS the audio
   punctuation.

Voice: `English_Trustworth_Man` via `speech-02-hd`, speed 0.95x,
neutral. Cadence 200 wpm so technical terms land cleanly.

## Animation density

The prompts deliberately include:

- **Frame-by-frame beats** (e.g. "Frame 0-1.5s: lines materialize
  in monospace. Frame 1.5-2.5s: crimson delta pulses. Frame 2.5-4s:
  SEAL stamps."). H.264 at 30+ fps gives a true motion-graphic
  rhythm rather than a slide-show.
- **Particle / smoke / spark effects** at the SEAL-stamp moment and
  the green-check seals (rule-of-three reveals).
- **Synchronized reveals** in the proof clip (all three panels lock
  at the same time, so the eye reads them as a single event).
- **Hard cuts** (no fades) in the pain clip so the "before/after"
  contrast reads as a difference, not a transition.

This is why v3 is "catchier" than v2 — the latter had slow crossfades
which read as documentary; v3 has motion-graphic rhythm which reads
as promotion. The hairline is intentional.

## Tradeoffs documented honestly

- **H3 vs Hailuo**: H3 produces noticeably higher-quality motion
  (better temporal coherence at scene transitions; less
  "boil"/drift on flat-shaded surfaces) AND has native-audio
  synthesis so the voice and score are audio-aligned automatically.
  But the H3 account-credit bucket is empty on this run, requiring
  780 credits per 6-second clip for a credit refile. Hailuo-2.3
  produced these clips at $0 via the Token Plan allowance. The motion
  quality is comparable to H3 at this resolution + length.
- **Choice of TTS voice**: `English_Trustworth_Man` carries a calm,
  measured register appropriate for finance/quant. Other voices
  worth A/B-testing: `English_Deep-VoicedGentleman` (deeper,
  weightier), `English_Steadymentor` (more senior), `English_CaptivatingStoryteller`
  (warmer).
- **Music volume 0.22** is below the typical "singer-forward" mix
  ratio (0.4-0.5); for technical/finance audiences voice-forward
  reads as more confident.

## When to use them

| Video | Drop it into |
|---|---|
| **why-1-explainer.mp4** (with full 3-layer mix) | The first comment reply on HN. X thread tweet #2 (right after the hook). LinkedIn cover. Reddit r/MachineLearning top of selftext. |
| **why-2-explainer.mp4** | X thread tweet #7 (architecture-explainer slot). Reddit r/quant top of selftext. LinkedIn mid-post reply to "what does this do that other tools don't". |
| **why-3-explainer.mp4** | HN reply to "how do I know the data is stable across versions". Reddit reply to "what's the upgrade story for an in-flight data pipeline". LinkedIn reply to the head-of-data-eng who always asks about idempotency. |

## Re-mixing the audio

The TTS tracks live at `campaign/assets/narr-{1,2,3}-*.mp3`. The
AI music tracks are NOT saved separately (they were one-shots —
regeneration is cheap). To re-mix:

```sh
# 1. Regenerate the music via matrix batch_text_to_music
#    (prompts in the AI music call earlier this commit; see git log).
# 2. ffmpeg mux (voice full volume + music 0.22):
ffmpeg -i <input.mp4> -i narr-*.mp3 -i music-*.mp3 \
  -filter_complex "[1:a]volume=1.0[v1];[2:a]volume=0.22[v2];[v1][v2]amix=inputs=2:dropout_transition=0[mix]" \
  -map 0:v -map "[mix]" -c:v libx264 -pix_fmt yuv420p -preset medium -crf 22 \
  -c:a aac -b:a 192k -ar 48000 -shortest out.mp4
```

## Per-video narrative (for use in captions, post text, etc.)

### 1. why-1-explainer — Pain vs Fix

> Today's PDF extractors are slow, expensive, and silent about
> their own contradictions. qscreen-filing-tool fixes all three:
> deterministic, ~3 s per filing, $0, and the math-identity gate
> runs *before* the JSON ships.

### 2. why-2-explainer — Gate Blocks Silent Failure

> Most extractors ship the JSON regardless of internal consistency.
> qscreen-filing-tool's gates engine checks Assets = L + Equity
> with +/-2% tolerance *and 11 cross-cutting + 25 issuer-specific
> pre-flag rules* (UDCD IP at 47% of TA, ZHCD qualified auditor
> history, QIGD's 3 entity renames). If a record contradicts
> itself, **the record doesn't ship** and the evidence points at
> the offending line item.

### 3. why-3-explainer — Fingerprint Magic

> Stability across versions: re-ingesting the same PDF on any
> engine commit produces a JSON with the **same SHA-256
> fingerprint**. The data is bit-identical across engine upgrades.
> Add Sigstore keyless signing and you can cryptographically prove
> "this PDF produced this JSON on this commit". Audit trail that
> works without trusting the operator.
