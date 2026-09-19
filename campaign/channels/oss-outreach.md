# Open-source outreach kit

Two audiences: **grant programs** (zero-cost funding in exchange for
milestone-bound deliverables) and **corporate sponsors** (cash for
priority features or maintenance). Both need a one-page pitch + a public
"where we are" snapshot — both of which already exist on this repo.

---

## A. Grant programs (cold-email template)

Subject line: `qscreen-filing-tool — open-weight PDF → lossless filing JSON for financial reports`

```
Hi [program officer name],

We've been building qscreen-filing-tool for the last six months — a
jurisdiction-agnostic Python engine that turns any exchange's annual or
interim report into a schema-stable, audit-traceable JSON object. Today
it ships for the QSE market (55 tickers, 124-check bench at 80.6%);
AE / SA / KW are documented as one-directory-drop extensions.

The architectural bets are the ones we'd like to harden with [program]
support:

1. **Deterministic-first extraction.** The PDF tables are read in
   code; the LLM fills gaps. Numbers never pass through the model, so
   a 270M local model produces the same contract as a frontier cloud
   model. This is unusual in the financial-extraction space and is the
   reason we can run fully offline for $0.

2. **Math-identity gate.** The JSON won't ship if `Assets ≠ L + E`
   within ±2%. Eleven cross-cutting + twenty-five issuer-specific
   pre-flag rules run before `save()`. If a record contradicts itself,
   the record doesn't ship and the evidence points at the offending
   line item.

3. **SHA-256 cross-filing fingerprints + Sigstore keyless signing.**
   Re-ingest the same PDF on any engine commit → bit-identical JSON,
   cryptographically attestable back to the engine commit that
   produced it.

The supply chain is hardened: SBOM (CycloneDX 1.5) per release, Sigstore
keyless signing on every release, SLSA Build L3 provenance attestation,
CodeQL on every PR + main + weekly schedule, `pip-audit` non-blocking
on every PR, container image on `ghcr.io/Mine-FNL/qstocks-filing-tool`.

Live bench: https://mine-fnl.github.io/qstocks-filing-tool/demo.html
Repo:        https://github.com/Mine-FNL/qstocks-filing-tool
Disclosure:  https://github.com/Mine-FNL/qstocks-filing-tool/security/policy

Where we'd like [program] help:

- A 6-month maintenance grant covering the second jurisdiction (AE) +
  a security review of the deterministic-extraction layer.
- An audit of the supply chain against the OpenSSF Scorecard "gold"
  tier (currently ~7.5/10; the gap is mostly in the security policy
  + dependency-update SLAs).

If [program]'s mandate fits, I'd love to schedule a 30-minute call to
walk through the architecture and the proposed milestones.

— [Your name]
```

### Target list (ranked by fit)

| Program | Why | URL |
|---|---|---|
| **NLnet Foundation** | Privacy/infrastructure focus; jurisdiction-agnostic engine fits the "commons infrastructure" line. | nlnet.nl |
| **Sovereign Tech Fund** (DE) | Open-source maintainer funding; the AE jurisdiction drop is a clear milestone. | sovereightyechfund.de |
| **Open Technology Fund** | Information integrity angle (financial-disclosure integrity). | opentech.fund |
| **GitHub Sponsors** (OSS-only) | Zero-friction, recurring; pairs well with a maintenance grant. | github.com/sponsors |
| **Mozilla MOSS** (open track) | Historically funds open-source security and privacy work; we'd qualify on supply-chain hardening. | www.mozilla.org/moss/ |

---

## B. Corporate sponsors (cold-email template)

Subject line: `qscreen-filing-tool — open-weight financial filing extractor (sponsorship ask)`

```
Hi [name],

I lead qscreen-filing-tool, an open-source engine that turns a PDF
financial report into a lossless, audit-traceable JSON object. We have
[485 tests, 80.6% bench, SBOM + Sigstore + SLSA L3 provenance per
release, containerized] and are looking for a corporate sponsor to fund
[two priority features OR 12 months of maintenance].

Why this matters for [company]:

- [Company] is in the financial-data / quant / analytics space. The
  typical filing-ingest path in your segment is: a vendor API ($$$),
  or a brittle `pdfplumber` script that breaks every quarterly layout
  change, or an LLM-only pipeline that can't be fingerprinted.

- The math-identity gate and the SHA-256 cross-filing fingerprints
  solve two pain points that compliance / quant desks typically hit:
  (1) silently-shipped internal contradictions and (2) data
  re-extraction drift across model upgrades.

- It's open-weight + open-source + containerized + has a public bench
  regression gate, so the procurement path is short.

Sponsorship tiers:

- **$5k/yr — Bronze**: Logo on the README + GH Sponsors page.
- **$15k/yr — Silver**: Above + 1 day/month of priority feature
  work (e.g., extra jurisdiction profiles, custom profiles, sector
  taxonomy).
- **$50k/yr — Gold**: Above + private Slack channel + 6-month
  exclusive first-look at new releases + co-marketing on the next
  Show HN.

If [company] would prefer a paid feature contract instead of an OSS
sponsorship, I'm open to that too — happy to walk through the
priority-feature roadmap.

Live bench: https://mine-fnl.github.io/qstocks-filing-tool/demo.html
Repo:        https://github.com/Mine-FNL/qstocks-filing-tool

— [Your name]
```

### Target list (ranked by fit)

| Rank | Segment | Specific orgs | Why |
|---|---|---|---|
| **1 (NEW)** | **Standards-body partner** | **XBRL US** ([David Tauriello, VP Operations](https://linkedin.com/in/davidtauriello)) | XBRL US built and open-sourced an **AI Connector / MCP server** for as-filed XBRL data in 2026 and is actively recruiting community contributions. qscreen is the upstream extractor that feeds it cleaner iXBRL-tagged data. Not a cash-grants fit (small consortium), but a credibility / co-publication / joint-research fit. See `campaign/conference/sponsor-enrichment.md` §12 for the full profile and a draft intro email. **Highest-leverage outreach on this list.** |
| 2 | **Financial-data vendors** | CalcBench, Sentieo, Audit Analytics, Edgar Online | Direct adjacency; small sponsorship buys a high-signal logo. |
| 3 | **Quant / hedge fund tooling** | Two Sigma (Dagon), Man AHL (Research Forge), Hudson River Trading (OSS), Jane Street (OSS) | Recurring sponsorship budget; PR upside; few large OSS sponsorships from this segment so visibility is high. |
| 4 | **Cloud / infra** | AWS OSS, GCP OSS, Cloudflare OSS | Don't usually fund, but a featured "Cloudflare OSS Project" badge is itself PR. |
| 5 | **Quant LLM-platform vendors** | RavenPack, AlphaSense, YipitData | Direct adjacency; sponsorship is also a recruiting signal. |
| 6 | **Regional exchanges** | QSE, ADX, Tadawul, Boursa Kuwait | Direct end-user; sponsorship is also a long-term partnership path. |

> **Action:** `sponsor-enrichment.md` (in `campaign/conference/`) has the
> full profiles — program officer names, LinkedIn handles, recent
> recipients, application windows — for **12 entities** (4 grants + 8
> corporate sponsors). The original `oss-outreach.md` is a cold-email
> template; `sponsor-enrichment.md` is the targeting ammunition.

---

## What I'm *not* doing in this kit

- **Cold-DM on Twitter / LinkedIn.** Corporate sponsorship works better
  via intro. If you (the user) have a warm intro to anyone on the
  target list above, that's the highest-leverage move.
- **A press release.** The project is too small to get meaningful
  press pickup; the leverage is on direct sponsor outreach, not PR.
- **A "Support us on Patreon" button.** Tier-1 OSS sponsorships are
  the right scale; micro-sponsorship underperforms at this stage.
