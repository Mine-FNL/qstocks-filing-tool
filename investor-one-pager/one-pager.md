# Investor one-pager

> **qscreen-filing-tool** — lossless filing JSON, math-identity gates, attestable provenance.
>
> A jurisdiction-agnostic Python engine that turns any exchange's annual
> or interim report into a schema-stable, audit-traceable JSON object.
>
> Six months in production. 485 tests. 124-check regression bench at 80.6 %.
> Hardened supply chain (SBOM + Sigstore + SLSA L3). Multi-arch container
> on `ghcr.io`. Public 6,000-word whitepaper.

---

## The problem

Financial-document extraction is broken at the final mile. Existing tools
fall into three categories:

1. **LLM-only extractors** — hallucinate numbers at 5–10 % rate; can't
   fingerprint output across engine upgrades; expensive at scale
   ($0.04–0.12/filing).
2. **Layout-only tools** (`pdfplumber`, `camelot`, `marker`) — give you
   text or Markdown, but not a structured, schema-stable JSON contract.
3. **Vendor APIs** — opaque, expensive, vendor-locked, no cryptographic
   provenance.

Downstream pipelines re-ingest every quarter because they can't trust
hash stability. Compliance teams can't answer *"which engine version
produced this row?"* without a database comment. Quant desks re-do
reconciliation by hand because the JSON can't be trusted to be internally
consistent.

## The solution — three bets

1. **Deterministic-first extraction.** PDF tables are parsed in code
   (`pdfplumber`). The model only fills gaps (audit opinion, notes,
   segments). Numbers never pass through the model — so a 270M local
   model produces the same numerical contract as a frontier cloud model.
2. **Math-identity gate at the write path.** The JSON cannot ship if it
   contradicts itself (`Assets ≠ L + Equity` ± 2 %, with eleven
   cross-cutting + twenty-five issuer-specific pre-flag rules). Blocked
   records stay on disk with evidence pointing at the offending line
   item; they never propagate.
3. **SHA-256 cross-filing fingerprints + Sigstore keyless signing +
   SLSA Build L3 attestation.** Every release produces a wheel, an SBOM,
   a Sigstore bundle, a SLSA v1 receipt, and a multi-arch container.
   The chain is verifiable by a third party without cooperating with
   the operator.

## Traction

| | v1.0 (Mar 2026) | v1.6.0 (Sep 2026) |
|---|---|---|
| Lines of engine code | ~6,000 | ~10,500 |
| Unit tests | 120 | **485** |
| Bench checks | 30 | **124** |
| Bench pass rate | 60 % | **80.6 %** |
| Pre-flag rule coverage | 9 / 25 | **25 / 25** |
| Cross-platform CI | Ubuntu only | **Ubuntu + macOS + Windows** |
| Supply chain hardening | none | SBOM + Sigstore + SLSA L3 + CodeQL |
| Public install paths | 1 (PyPI) | **3** (Releases CDN + PEP 503 simple index + container) |
| Documentation | README | README + 9-section whitepaper + hosted docs site |
| Cross-post drafts | none | HN + Lobsters + Reddit + Product Hunt + LinkedIn + Medium + Hacker Noon + X threads |

## Market

Financial-document data infrastructure is a $XB annual market served by
Bloomberg, Refinitiv (LSEG), S&P Capital IQ, CalcBench, Sentieo, AlphaSense,
and a long tail of regional vendors. Each has the same problem: the
ingestion path is brittle, the fingerprint stability is fake, and the
provenance is opaque.

The open-source moat:
- **Jurisdiction-pluggable.** The Qatar profile ships with 55 tickers;
  AE / SA / KW are one-directory-drop extensions. New markets can be
  added without re-engineering the gate or the fingerprint.
- **Supply-chain trust.** Compliance teams cite our SBOM + Sigstore + SLSA
  receipts in their internal documentation — and we don't pay for that
  PR.
- **Profile as content.** Each jurisdiction profile is a deep artefact
  (Qatar = ~6,000 lines of seed + 25 pre-flag rules). The cost of
  building a UAE/Saudi/Kuwait profile is the asset; the engine is the
  commodity.

## Ask

| Tier | $/yr | What you get |
|---|---|---|
| **Bronze — $5k** | Logo on the README + GH Sponsors page. |
| **Silver — $15k** | Above + 1 day/month of priority feature work. |
| **Gold — $50k** | Above + private Slack channel + 6-month exclusive first-look at new releases + co-marketing on Show HN / conference abstracts. |

Equivalent grant funding via NLnet, Sovereign Tech Fund, MOSS, or
GitHub Sponsors accepted at any tier.

## What the money buys

UAE jurisdiction profile (Q4 2026) · audit-opinion classification model
trained on gate-flagged disagreements · multi-PDF batch orchestrator with
SQLite-backed resume · OpenSSF Scorecard "gold" tier hardening
(currently ~7.5/10) · conference presence (PyCon US 2027 + PyData Berlin
2027 + SIGMOD Demo Track 2027; CFP abstracts in `campaign/conference/`).

## Team

**qscreen-filing-tool maintainers** — the same small team that built the
engine, the bench, the supply chain, and the launch kit. Six months of
full-time focus; v1.0 through v1.6.0 shipped with zero failed release
gates. Maintainer: 0xBingBong69 (GitHub); background in quant data
infrastructure and MENA financial markets.

## Contact

- **Repo**: <https://github.com/Mine-FNL/qstocks-filing-tool>
- **Live bench**: <https://mine-fnl.github.io/qstocks-filing-tool/demo.html>
- **Whitepaper**: `whitepaper/whitepaper.pdf`
- **GH Sponsors**: <https://github.com/sponsors/0xBingBong69>
- **Email**: see `SECURITY.md` (mention `[investor-one-pager]` in subject)
