# PyCon US 2027 — talk submission

**Title (≤ 80 chars):**
> Numbers never pass through the model: deterministic-first PDF extraction

**Talk type:** 30-minute talk (regular session)

**Track:** Data Engineering / Applied Python

**Audience level:** Intermediate-to-advanced Python developers who've worked on
data pipelines or document extraction.

**Submitted by:** qscreen-filing-tool maintainers

---

## Abstract (300 words)

Every "PDF → JSON" pipeline I've seen treats the language model as the
source of truth for numbers. We treated it as the source of truth for
*gaps* — and the numbers became deterministic.

This talk is the postmortem of six months of building an extraction
pipeline for financial filings where the production requirement was:
"re-ingest the same PDF on any engine commit and get byte-identical
JSON, cryptographically attestable back to the engine commit that
produced it."

Three architectural bets made it work:

1. **Deterministic-first extraction.** PDF tables are read in code
   (`pdfplumber`); the language model only fills gaps (audit opinion,
   notes, segment labels). Numbers never pass through the model. A
   270-million-parameter local model produces the same numerical
   contract as GPT-4o.

2. **A math-identity gate that runs before `save()`.** If `Assets ≠ L +
   Equity` within a sector-aware tolerance band, the record doesn't
   ship — and the evidence points at the offending line item. Eleven
   cross-cutting + twenty-five issuer-specific pre-flag rules run
   before every write.

3. **SHA-256 cross-filing fingerprints + Sigstore keyless signing.**
   Re-ingesting the same PDF on any engine commit produces
   bit-identical JSON that you can verify against the public Fulcio +
   Rekor logs.

The bench is public: 124 cross-filing checks against the current
Qatar-listed universe, regression floor 100/124 (80.6%). Every PR
that drops the floor fails CI.

We'll show the architecture, the failure modes we hit on the way
(non-deterministic JSON, silently-shipped internal contradictions,
opaque provenance), and the three properties — deterministic
extraction, math-identity gate, fingerprintable provenance — that
solved them. We'll also cover what *doesn't* work: image-only PDFs,
heavy footnote-as-data filings, and the audit-opinion classification
ceiling.

Code: github.com/Mine-FNL/qstocks-filing-tool (MIT).
Whitepaper: included in the repo.

---

## Outline (5 sections, 30 min)

1. **The problem (5 min)** — three failure modes of existing extractors.
2. **The inversion (8 min)** — deterministic-first extraction, with live
   demo of a 270M local model producing the same contract as GPT-4o.
3. **The gates (7 min)** — math-identity gate, sector-aware tolerances,
   pre-flag rules. Live demo of a blocked record with evidence.
4. **The provenance (5 min)** — SHA-256 fingerprints + Sigstore chain.
   Live demo: `gh attestation verify` against a public release.
5. **The honest ceilings (5 min)** — what doesn't work, what's on the
   roadmap, Q&A.

## Take-aways

- If your data lives in tables, parse the tables. Don't ask a model.
- A "save point" is the right place for a consistency gate, not a
  post-hoc validator.
- Stable fingerprints are a necessary property of any data pipeline
  that survives engine upgrades.

## Pitch (≤ 200 chars for the CFP form)

> A deterministic-first extraction pipeline that lets a 270M local model
> produce the same financial filing JSON as GPT-4o. Math-identity gate
> blocks self-contradictory records. SHA-256 fingerprints + Sigstore
> signing make the audit trail attestable. 124-check public bench.

## Bio

The qscreen-filing-tool maintainers build open-source data-extraction
pipelines for the QSE-listed universe (55 tickers, IFRS / IFRS-for-SME).
The project has 485 tests, an 80.6 % bench, full SBOM + Sigstore +
SLSA L3 supply-chain hardening, and a public 124-check regression
suite. We document what doesn't work as carefully as what does.

## Speaking requirements

- HDMI projector (1080p).
- Live-demo terminal + browser (Chrome for the demo site).
- Backup slides for every live-demo segment (we have them).
- Q&A mics preferred but not required.
