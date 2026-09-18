# SIGMOD / VLDB Demo Track 2027 — paper submission

**Track:** SIGMOD 2027 Industrial Track / VLDB 2027 Demo Track

**Submission type:** 4-page demo paper + 10-min demo presentation

**Companion artifact:** qscreen-filing-tool (MIT-licensed open-source repo)

---

## Title (≤ 200 chars)

> qscreen-filing-tool: A reproducible, fingerprintable pipeline for
> financial-document extraction with built-in consistency gates

## Authors

The qscreen-filing-tool maintainers.

## Abstract (150 words, ACM style)

We demonstrate qscreen-filing-tool, an open-source engine that turns a
PDF financial report into a schema-stable, audit-traceable JSON
object with three properties: (i) deterministic numerical extraction
— the PDF's tables are read in code, so a 270M-parameter local model
produces the same numerical contract as a frontier cloud model; (ii) a
math-identity gate that refuses to ship self-contradictory records
(Assets ≠ L + Equity ± 2%, with eleven cross-cutting + twenty-five
issuer-specific pre-flag rules); and (iii) SHA-256 cross-filing
fingerprints + Sigstore keyless signing + SLSA Build L3 provenance
attestation, so any record is cryptographically traceable back to the
engine commit that produced it. We demonstrate the live pipeline on
the current Qatar-listed universe (55 tickers), show the public 124-
check regression bench (regression floor 100/124, 80.6 %), and walk
through the failure modes the architecture prevents.

## 1. Introduction

Financial-document extraction sits at the intersection of three hard
problems: (a) layout variance across issuers and reporting periods,
(b) downstream sensitivity to silently-incorrect numerical
extraction, and (c) regulatory demand for auditable provenance. We
demonstrate a production-grade open-source engine that addresses all
three.

## 2. Architecture

The pipeline ingests a PDF, parses tables with `pdfplumber`, applies
a jurisdiction-specific profile for account-code mapping + sign/scale
correction, runs a math-identity gate, and emits a JSON record
tagged with `basis: "parsed"` (numbers) or `basis: "llm"` (gaps). The
profile-pluggable architecture generalises beyond the default Qatar
profile to other markets (AE, SA, KW).

## 3. Demo walk-through

Three live demonstrations:

1. **Deterministic vs. LLM-only extraction** — same PDF run through
   the deterministic pipeline vs. an LLM-only baseline; demonstrate
   variance reduction and the line-item-level `basis` tag.
2. **Math-identity gate in action** — inject an internally-
   contradictory filing; show the gate catching it, the evidence
   payload pointing at the offending line item, and the record
   refusing to upload.
3. **Provenance verification** — re-ingest a previously-extracted
   PDF on a fresh engine commit; demonstrate bit-identical JSON;
   verify the Sigstore + SLSA chain with `gh attestation verify`
   against public Fulcio + Rekor logs.

## 4. Bench

124 cross-filing checks against the current Qatar-listed universe;
regression floor 100/124 (80.6 %); every PR that drops the floor
fails CI. Per-failure-mode breakdown documented in the whitepaper
(§5).

## 5. Limitations

Image-only PDFs (opt-in OCR); heavy footnote-as-data filings; non-
English coverage. Documented honestly in the whitepaper (§7).

## 6. Reproducibility

All artifacts (wheel, container, SBOM, signatures, SLSA receipts)
publicly hosted. Bench regenerable from `python qscreen_eval.py
--json > bench.json`. Whitepaper + appendix B document end-to-end
reproduction. Source: github.com/Mine-FNL/qstocks-filing-tool.

## Submission package

- 4-page PDF (ACM sig-alternate format)
- 10-min demo video (publicly hosted)
- Companion artifact: source repo + bench.json + SBOM
- Author agreement + conflict-of-interest disclosure

## Pitch line (for the CFP form, ≤ 200 chars)

> Open-source financial-PDF extraction with deterministic-first
> tables, math-identity gates, SHA-256 fingerprints, Sigstore +
> SLSA L3 attestation. 124-check public bench. MIT-licensed.

## What to highlight in the live demo

- A *blocked* record (gate triggered, evidence payload shown).
- The *same PDF* ingested twice producing *identical* SHA-256.
- `gh attestation verify` running live against a fresh download.
