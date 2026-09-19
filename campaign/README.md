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
| `assets/why-1-explainer-captioned.mp4` | v5 of WHY #1, **1934×1080**, **burned-in captions** (no audio needed for autoplay-on-X / LinkedIn / Reddit feed). |
| `assets/why-2-explainer-captioned.mp4` | v5 of WHY #2, **burned-in captions**. |
| `assets/why-3-explainer-captioned.mp4` | v5 of WHY #3, **burned-in captions**. |

### Which video to drop into which channel

The captioned track is **the right pick for any feed where autoplay is silent**
(X timeline, LinkedIn feed, Reddit embed, Slack unfurl, Discord embed, GitHub
social preview). The non-captioned track is for places the user already plans
to listen (HN first comment with audio enabled, demo on the docs site,
show-floor kiosk).

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
| 1 | Lobsters                             | `architecture-16x9.jpg` | `channels/lobsters.md` |
| 2 | r/MachineLearning (`Show` flavor)    | `architecture-16x9.jpg` | `channels/reddit-ml.md` |
| 4 | r/quant                              | `architecture-16x9.jpg` | `channels/reddit-quant.md` |
| 5–10 | Product Hunt                        | 5 gallery images | `channels/product-hunt.md` |
| 7 | X thread #1 (15 tweets, launch)      | `hero-16x9.jpg` (card) + `*-captioned.mp4` (tweets 2/7/9) | `channels/x-thread.md` |
| 7 | dev.to long-form                     | `architecture-16x9.jpg` | `channels/dev-to.md` |
| 12 | X thread #2 (architecture deep-dive) | `architecture-16x9.jpg` | `channels/x-thread-architecture.md` |
| 14 | X thread #3 (bench story)            | `stats-card-16x9.jpg` | `channels/x-thread-bench.md` |
| 14 | LinkedIn long-post                   | `architecture-16x9.jpg` | `channels/linkedin.md` |
| 18 | Medium (Better Programming)          | `architecture-16x9.jpg` | `channels/article-medium-specs.md` |
| 21 | X thread #4 (SHA-256 fingerprints)   | none (text-only) | `channels/x-thread-fingerprint.md` |
| 24 | Hacker Noon (supply-chain checklist) | `architecture-16x9.jpg` | `channels/article-hacker-noon.md` |
| 28 | X thread #5 (supply-chain hardening) | none (code-block heavy) | `channels/x-thread-supply-chain.md` |
| 30 | X thread #6 (pluggable profiles)     | `architecture-16x9.jpg` | `channels/x-thread-profiles.md` |
| any | InfoQ / The New Stack (cold pitch)   | n/a (email) | `channels/article-infoq-pitch.md` |
| any | OSS grant / corp sponsorship        | n/a (cold email) | `channels/oss-outreach.md` |

## Whitepaper

The canonical long-form artifact is `whitepaper/whitepaper.md` (~6,000
words, 9 sections + 3 appendices). The PDF render is
`whitepaper/whitepaper.pdf` (~10 pages, typeset in Charter / Helvetica
Neue + JetBrains Mono via pandoc + Chrome headless). Build with
`bash whitepaper/build.sh`.

Distribution: PDF + HTML ship with the GitHub release; HTML will host on
the docs site (TBD — add `mkdocs serve whitepaper/` to the docs deploy
step).

## Article archive (in `channels/`)

| File | Outlet angle | Audience |
|---|---|---|
| `show-hn.md`              | HN landing          | Tech-leadership |
| `lobsters.md`             | Post-HN cross-post  | Deep-technical |
| `reddit-ml.md`            | r/ML self-post      | ML practitioners |
| `reddit-quant.md`         | r/quant self-post   | Quants |
| `linkedin.md`             | LinkedIn long-post  | Quant-desk buyers |
| `dev-to.md`               | dev.to tutorial     | Data engineers |
| `product-hunt.md`         | Product Hunt kit    | Maker / early-adopter |
| `article-medium-specs.md` | Medium (Better Programming) | ML/data eng |
| `article-hacker-noon.md`  | Hacker Noon         | DevOps / supply-chain |
| `article-infoq-pitch.md`  | Industry press      | Editor (not direct post) |
| `oss-outreach.md`         | Grants + sponsors   | Programme officer / corporate dev-rel |
| `x-thread.md`             | X thread #1         | Launch audience |
| `x-thread-architecture.md`| X thread #2         | Architecture-curious |
| `x-thread-bench.md`       | X thread #3         | Data-eng / bench-discipline |
| `x-thread-fingerprint.md` | X thread #4         | Sigstore / supply-chain |
| `x-thread-supply-chain.md`| X thread #5         | Compliance / SRE |
| `x-thread-profiles.md`    | X thread #6         | Regional-exchange / data-team |

## Conference talk abstracts (in `conference/`)

CFP-ready abstracts + outlines for venues where the "industry-leading"
angle matters.

| File | Venue | Talk type | Length |
|---|---|---|---|
| `pycon-2027.md`           | PyCon US 2027                       | Technical talk      | 30 min |
| `pycon-de-pydata-2027.md` | PyCon DE & PyData 2027 (Heidelberg) | Community talk      | 25 min |
| `sigmod-demo-2027.md`     | SIGMOD / VLDB 2027                  | Industrial / demo   | 10 min + 4-page paper |
| `strata-2027.md`          | Strata Data 2027                    | Industry talk       | 40 min |

Submission deadlines are typically 4–6 months before the conference; submit
in the order above (PyCon first, Strata last). Each file includes the CFP
abstract, a section-by-section outline, a ≤ 200-char pitch line, and
speaker notes (slides pacing, audience-tuning, live-demo backup strategy).

## Research & intelligence (in `conference/`)

Sub-agent research outputs (4 parallel briefs, ~1,900 lines total) used to
calibrate the abstracts, the sponsor outreach, and the supply-chain
hardening work.

| File | What | Size |
|---|---|---|
| `cfp-enrichment.md`       | Verified CFP deadlines + program-chair contacts + last-year accepted-talk patterns for all 4 venues + 1 cross-cutting observations block | 339 lines |
| `sponsor-enrichment.md`   | 12 entity profiles (4 grants + 8 corporate sponsors) with program officers, LinkedIn handles, recent recipients, application windows. **#1 finding: XBRL US (David Tauriello, VP Operations) is the highest-leverage outreach target.** | 665 lines |
| `competitive-landscape.md`| 8-competitor matrix (pdfplumber, camelot, marker, extractous, unstructured-io, Docparser, Rossum, Affinda) + 5 positioning lessons. **#1 finding: target regulated mid-market finance/audit teams paying $18K–70K/yr for Rossum/Affinda — they're the buyers who already understand why the math-identity gate matters.** | 475 lines |
| `scorecard-hardening.md`  | OpenSSF Scorecard plan from ~7.5 → 9.0+/10 (gold tier). **Top 5 ship-ready recommendations**: SHA-pin actions + digest-pin Dockerfile + CODEOWNERS + rulesets + token-permissions hardening + persist-credentials sweep + canonical 90-day SECURITY.md. | 486 lines |

These four briefs are the research ammunition behind the integration
commits in this batch:
- `cfp-enrichment.md` → pydata-2027.md renamed to pycon-de-pydata-2027.md (factual correction: PyData Berlin ended 2018; successor is PyCon DE & PyData, 2027 edition in Heidelberg)
- `sponsor-enrichment.md` → XBRL US added as #1 partner target in `oss-outreach.md`
- `scorecard-hardening.md` → 90-day disclosure language added to `SECURITY.md`; workflow permissions tightened across `release.yml`, `docs.yml`, `docker-image.yml`, `provenance.yml`, `bench.yml`, `publish.yml`, `security.yml`
- `competitive-landscape.md` → informs the README's competitive table and the investor one-pager's positioning

## Demo GIF

`campaign/assets/demo.gif` — 5-second animated preview (800×447, 3.5 MB,
auto-loops) extracted from `why-1-explainer-captioned.mp4` via ffmpeg
palettegen + paletteuse. Embedded in the README as a fallback for
Markdown renderers that don't render `<video>` tags (GitHub issue
previews, Slack, some HN themes, some dev.to themes).

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
- 9:16 vertical cuts (LinkedIn / X / TikTok / YouTube Shorts).
  ffmpeg crop+re-encode; ~30 min once we're ready to test vertical-feed
  reach. (Future sprint.)
- Auto-generated captions via Whisper word-level timestamps (today
  the captions are hand-timed from the `.srt` files in
  `campaign/assets/narr-*.srt`; a Whisper pass would let us regenerate
  captions in any language). (Future sprint.)
