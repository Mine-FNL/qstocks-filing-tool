# Show HN — channel copy

**Title (under 80 chars):**
> Show HN: qscreen-filing-tool – Open-weight PDF → lossless filing JSON

**Body:**

We (Mine-FNL) shipped an open-weight, jurisdiction-agnostic engine that turns
any exchange's PDF annual / interim report (QSE-shipping; AE/SA/KW-ready)
into a single stable, fingerprintable JSON, ready to ingest.

The headline: **80.6 % accuracy on the 8-case golden-set bench**,
**485 unit tests passing**, and every release carries a CycloneDX SBOM, a
Sigstore keyless signature against the GH OIDC identity, and an in-toto
SLSA v1 attestation — `gh attestation verify` works end-to-end against
the release tag.

![demo flow — input PDF → pipeline → output JSON → SBOM / Sigstore / SLSA badges](https://mine-fnl.github.io/qstocks-filing-tool/demo-flow-16x9.jpg)

What it actually does, in 5 stages (architecture diagram →

![architecture diagram](https://mine-fnl.github.io/qstocks-filing-tool/architecture-16x9.jpg)

**1. PDF LOADER** — pdfplumber-based page list with `pages[]` envelope.

**2. LAYOUT ANALYZER** — statement segmentation; bilingual (Arabic +
English) page-level language detection.

**3. LINE-ITEM EXTRACTOR** — table parse with auto-correction fallback.
11 cross-cutting + 25 issuer-specific pre-flag rules fire here.

**4. GATES ENGINE** — math-identity checks (Assets = Liabilities + Equity,
Δ tolerance ±2 pct) plus 11 cross-cutting gates (related-party
concentration, ROE vs Ke, etc.) and 25 issuer-specific rules (UDCD IP
at 47 % of TA, ZHCD 8-of-10-year qualified auditor history, QIGD
3×-renamed entity, etc.).

**5. FINGERPRINTER** — SHA-256 over the normalized text + schema
version; gives stable cross-run regression detection.

Why we think this is interesting even if you don't trade QSE:

- **No GPU needed**: plain Python, runs on a laptop. PDFplumber + heuristics;
  no frontier LLM in the extraction path. Total runtime: ~3 s per filing.
- **Verified build chain end-to-end**: SBOM on every release, Sigstore
  signing, SLSA L3 attestation. Can be consumed by `gh attestation verify`
  against the release tag — no long-lived secrets anywhere.
- **Three independent install paths, none of which require PyPI access**:
  `docker pull ghcr.io/Mine-FNL/qstocks-filing-tool:v1.6.1` (multi-arch)
  OR `pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/download/v1.6.1/qscreen_filing_tool-1.6.1-py3-none-any.whl`
  OR `--extra-index-url https://mine-fnl.github.io/qstocks-filing-tool/simple/`
  (PEP 503). All three are reachable from CI now.
- **Lossless + audit-friendly**: the JSON schema is deterministic
  (fingerprint=hash), so a re-ingest of the same PDF produces a
  bit-identical record. Every merge into main runs the 8-case
  golden-set bench; bench failure blocks the release.
- **Pluggable profiles**: the QSE profile ships with the repo; an AE/SA/KW
  profile is one PR away once an analyst contributes the per-issuer
  pre-flag rules for that jurisdiction.

What's NOT new and what is:

- Not new: pdfplumber, OCR via tesseract / rapidocr, BEIR-style eval.
- New (we think): jurisdictional pre-flag **catalog** as a first-class
  construct that runs AS PART OF the extraction — not bolted on afterward.
  The catalog grows by issuer, not by global rules, so a single analyst
  can ship a new jurisdiction by contributing ~25 issuer-specific rules
  (~3 days of work) and a few statement templates.

Where to start:

- repo: https://github.com/Mine-FNL/qstocks-filing-tool
- live bench: https://mine-fnl.github.io/qstocks-filing-tool/demo.html
- 5-min install: https://mine-fnl.github.io/qstocks-filing-tool/install/

Happy to dig into any of the 5 stages in the comments — happy to take
PRs for additional jurisdiction profiles (AE / SA / KW are obvious gaps).

— Mine-FNL

---

## HN-specific notes

- The HN title format that converts: project name (in backticks if rendering
  issue), a "Show HN:" prefix, and a short concrete beneficiary verb
  ("turns X into Y" tends to beat "library for X").
- Self-promotion default tone: tell the spec/architecture facts; let the
  reader decide. No "we're excited to announce" headlines; HN penalizes
  marketing voice heavily.
- Best time to post for US-east-coast tech audience: Tuesday–Thursday
  8-10 AM ET. Avoid Mondays (other stories dominate) and Fridays
  (low-engagement graveyard).
- If asked about IP / patents / company affiliation in the comments:
  the project ships under MIT; no patent; personal fork.
- If the thread goes sideways: stay on architecture claims that map to
  concrete files in the repo (line numbers if asked). Don't speculate.
