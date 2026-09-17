# Reddit r/MachineLearning — submission copy

## Title

> [P] qscreen-filing-tool — Open-weight, jurisdiction-agnostic PDF → lossless
> filing JSON with math-identity gates; SLSA v1 attested; 80.6 % on a 8-case
> hand-verified golden bench

## Body

(link to `assets/architecture-16x9.jpg` first, then writeup)

![architecture diagram](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/campaign/assets/architecture-16x9.jpg)

We (Mine-FNL) just shipped a deterministic, no-GPU, no-frontal-LLM in the
extraction-path engine for IFRS / AAOIFI financial filings, and wanted
to surface the architecture + the unusual supply-chain for the ML crowd.

**The headline numbers** (deterministic only, no LLM call):

- 80.6 % on the 8-case hand-verified golden bench (100 / 124 checks).
- 485 unit tests passing.
- 100/124 ≈ matches a single frontier-API call accuracy on the same
  cases, but at a tiny fraction of the cost — and **no provider
  dependency** in the binary path.
- Every release carries a CycloneDX SBOM, a Sigstore keyless signature
  against the GitHub OIDC identity, and an in-toto SLSA Build L3
  attestation — `gh attestation verify` works against the release tag.

**The pipeline (5 deterministic stages):**

1. **PDF LOADER** — pdfplumber, page list envelope.
2. **LAYOUT ANALYZER** — statement segmentation; bilingual
   (Arabic + English) language detection per page.
3. **LINE-ITEM EXTRACTOR** — table parse + auto-correction fallback.
4. **GATES ENGINE** — math-identity checks (Assets = L + E with ±2 %
   tolerance), plus 11 cross-cutting + 25 issuer-specific pre-flag
   rules (UDCD IP at 47 % of TA, ZHCD 8-of-10-year qualified auditor
   history, QIGD 3×-renamed entity, etc.).
5. **FINGERPRINTER** — SHA-256 over normalized text + schema version;
   gives stable regression detection across re-ingests.

**Why this is interesting for ML folks specifically:**

- The math-identity gate is a built-in label-noise detector. If a
  vanilla LLM extraction would have shipped BS_TOTAL_ASSETS that
  contradicts L + E by 4 %, the gate blocks the release and emits
  evidence pointing at the offending line. The bench failure mode
  is "missing numbers + contradictory numbers", not "subtle
  hallucination".
- The base extractor is a pure function (no model call). Adding a
  multilingual LLM as a fallback is a one-line swap; the existing
  gates still apply. So you can use this as a *label-noise filter*
  around an LLM extractor and keep determinism on the rest of the
  pipeline.
- The fingerprinting gives you a built-in regression test against
  the upstream PDF — re-ingest the same PDF across versions and
  the SHA-256 of the JSON is your stability check.

**Install** — three independent paths, none requires PyPI access:

    # Docker (multi-arch, GHCR)
    docker pull ghcr.io/Mine-FNL/qstocks-filing-tool:v1.6.1

    # Direct from GitHub Releases CDN
    pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/download/v1.6.1/qscreen_filing_tool-1.6.1-py3-none-any.whl

    # PEP 503 simple index on GitHub Pages
    pip install --extra-index-url https://mine-fnl.github.io/qstocks-filing-tool/simple/ qscreen-filing-tool

**Code + live bench:**

- repo: https://github.com/Mine-FNL/qstocks-filing-tool
- live bench: https://mine-fnl.github.io/qstocks-filing-tool/demo.html
- architecture deep-dive: https://mine-fnl.github.io/qstocks-filing-tool/architecture/

Curious about the bench-failure modes — we have a labelled failure
analysis per case on the demo page. Would love feedback on the
gates-engine design; the cross-cutting vs issuer-specific rule
split is the thing I'm least sure about.

Cross-post: a separate r/quant version focuses on the audit-friendly
JSON shape; this version focuses on the architecture / engineering.

---

## Posting guidance for r/MachineLearning

- **Use the [P] Project tag.** Required for project posts.
- **No editorialising claims.** Specific numbers only, with the file
  or run URL backing each number.
- **Be ready to defend numbers in comments.** First reply under any
  substantive challenge: quote the SHA-256 fingerprint of the bench
  run, not a marketing summary.
- **Don't:** allude to enterprise customers ("used at JPM"). HN/Reddit
  penalise that harshly.
- **Cross-link the r/quant thread** if/when it goes live, in a reply
  to this thread, not as a new post.
