# Campaign kit — qstocks-filing-tool

Ready-to-paste launch materials. All images are CC0-equivalent (generated for this project).

| File | Use it as |
|---|---|
| `assets/hero-16x9.jpg`          | Reddit / dev.to cover. HN submission body image. README header. |
| `assets/architecture-16x9.jpg` | Reddit `r/MachineLearning` / LinkedIn long-post "this is how it works" reply. docs/SHOW_HN.md illustration. |
| `assets/demo-flow-16x9.jpg`     | HN body image, X thread image #1. The before→after picture. |
| `assets/stats-card-16x9.jpg`   | The numbers card. X thread lead-tweet image. LinkedIn cover alt. |
| `assets/demo-promo-6s.mp4`      | Short promo loop (6 s, 768p, **native audio**). Embed in SHOW_HN, X, LinkedIn. |
| `assets/why-1-explainer.mp4`            | 6 s, **1920×1080 (1080p)**, **voice-over + background-music + chime** (3-layer AAC mix). **The WHY #1.** Snappy camera push-in on a vendor pricing card that shatters into pixel dust, hard cut to a typewriter terminal stamping `OK 3.0s 0 errors`, then three floating seal-stamps. Editorial motion graphics, midnight palette + cyan + emerald + crimson. |
| `assets/why-2-explainer.mp4`            | 6 s, **1920×1080 (1080p)**, **voice-over + dramatic impact boom**. **The WHY #2.** Slow-motion push-in on a financial document; lines `Assets = 1,420M / L+E = 1,389M` materialize in monospace; crimson delta pulses; a SEAL stamps diagonally with golden sparks and smoke dissipation; green checkmark seals the frame. |
| `assets/why-3-explainer.mp4`            | 6 s, **1920×1080 (1080p)**, **voice-over + triumphant arpeggio**. **The WHY #3.** Three-panel synchronized grid: glowing stable `sha256:f7b2...cd14`, Sigstore stamp animation, terminal running the same command three times. All three lock simultaneously into a green-check finale. |

## Channels (ranked by expected reach)

1. **Hacker News (Show HN)** — direct, regulated, scopes to the technical reader.
   Highest conversion-to-stars per impression.
2. **r/MachineLearning + r/quant** on Reddit — broader technical + finance reader.
3. **X / Twitter thread** with the demo-flow image — high circulation if a
   finance/quant account with a following retweets.
4. **LinkedIn long-post** (the architecture image) — the audience that actually
   buys software for a quant desk.

## Post ordering

| Day | Channel | Asset | Copy file |
|---|---|---|---|
| 0 | Show HN                              | `demo-flow-16x9.jpg` | `channels/show-hn.md` |
| 2 | r/MachineLearning (`Show` flavor)    | `architecture-16x9.jpg` | `channels/reddit-ml.md` |
| 4 | r/quant                              | `architecture-16x9.jpg` | `channels/reddit-quant.md` |
| 7 | X thread (15 tweets)                 | `hero-16x9.jpg` (card) + `architecture-16x9.jpg` (tweet 7) | `channels/x-thread.md` |
| 14 | LinkedIn long-post                   | `architecture-16x9.jpg` | `channels/linkedin.md` |

## Image specs

- **Hero (16:9):** 2752×1536 (2K). Use `assets/hero-16x9.jpg`.
  Reddit / HN / dev.to cover image. The README of the repo should also
  display this at the top.
- **Architecture (16:9):** 2752×1536 (2K). Use `assets/architecture-16x9.jpg`.
  Embed in long-form posts; GitHub comment thread on Show HN.
- **Demo-flow (16:9):** 2752×1536 (2K). Use `assets/demo-flow-16x9.jpg`.
  Direct post image for HN submission.

## In-repo hooks

- The hero image is what a stranger sees when the OG image link unfurls:
  `https://mine-fnl.github.io/qstocks-filing-tool/og.png` is the
  narrower version we ship by default; the campaign hero is the
  higher-fidelity alternative for explicit embeds.
- The architecture diagram should also live at
  `docs/site/architecture.md` as the inline illustration that
  accompanies the docs site's "Architecture" page. (TODO.)

## Not yet built

- `docs/perf.yml` workflow that posts a weekly thread summarising
  benchmark deltas to a Discord / Slack webhook. (Future sprint.)
- Animated demo GIF / MP4 (~8 s) that scrolls a real PDF through the
  extraction pipeline. Could be done by chaining several keyframes
  through the matrix video API. (Future sprint.)
- dev.to cross-post via their API (requires a DEV_TO_API_KEY secret
  on the repo). (Future sprint.)
