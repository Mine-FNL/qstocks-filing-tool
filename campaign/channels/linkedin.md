# LinkedIn long-post — copy

## Audience

Quant research leads, head of data engineering at asset managers,
heads of risk at retail/trading firms, OSS-tech-aware buy-side PMs.
Style: more measured than HN; less reductive than X.

## Post

Title (the LinkedIn first-line, before "see more" cut):

> Open-weight PDF → lossless filing JSON, with built-in math-identity
> gates and a cryptographically attested release chain. We just shipped
> it under MIT.

(link to `assets/architecture-16x9.jpg`)

![architecture diagram](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/campaign/assets/architecture-16x9.jpg)

We're a small team in Doha, and we just shipped the open-source
version of the PDF filing extraction pipeline we've been using
internally for Qatar-listed issuers (QSE).

The headline numbers: 80.6 % accuracy on an 8-case hand-verified
golden bench, 499 unit tests passing, every release cryptographically
attestable via `gh attestation verify` against the wheel + sdist +
SBOM.

Why we built it:

> Our quant desk's data plumbing was the bottleneck.
> Vendor PDF-extraction services are slow (typically 4-10 s per
> filing, with API-key rotation friction), opaque (we can't inspect
> why a number was extracted wrong), and expensive (5-15¢/filing
> adds up at index-rebalance cadence). And: the silent failure
> modes are dangerous — a vanilla LLM extraction can land a
> BS_TOTAL_ASSETS that contradicts L + E by 4 % and we wouldn't
> see it in CI.

The shape we ended up with:

> A 5-stage deterministic pipeline (PDF → page list → statement
> segmentation → table parse → math gates → SHA-256 fingerprint)
> with 11 cross-cutting + 25 issuer-specific pre-flag rules
> codified as Python, not SQL. The rules grow *per-issuer*, not
> globally — so adding AE / SA / KW is one PR per jurisdiction with
> ~25 rules + a few statement templates. Cost: ~3 days per
> jurisdiction.

The supply chain matters for a buy-side firm that has to prove
provenance:

> Every release is a CycloneDX SBOM, a Sigstore-signed wheel +
> sdist (keyless, against the GitHub OIDC identity), and an
> in-toto SLSA Build L3 attestation. `gh attestation verify dist/*`
> works against the release tag. No long-lived secrets in the
> build chain anywhere.

Three install paths today (none require PyPI access — useful when
the corporate network blocks PyPI):

    # Docker, multi-arch
    docker pull ghcr.io/Mine-FNL/qstocks-filing-tool:v1.6.1

    # From GitHub Releases CDN directly
    pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/download/v1.6.1/qscreen_filing_tool-1.6.1-py3-none-any.whl

    # PEP 503 simple index on GitHub Pages
    pip install --extra-index-url https://mine-fnl.github.io/qstocks-filing-tool/simple/ qscreen-filing-tool

What's interesting:

- The stable SHA-256 fingerprint is the part I'm proudest of. It
  means re-ingest is idempotent across engine versions, so an
  audit trail on a 2023 filing still works on a 2026 engine.
- The math-identity gates catch what most extractors miss. If the
  BS doesn't reconcile, the record doesn't ship.
- The chain is verifiable from the GitHub side. Whoever consumes
  the artefact can cryptographically attribute it back to the
  commit that built it.

Where I'd value your perspective:

- Your firm's tolerance for BS / L+E reconciliation. Default in
  the QSE profile is ±2 %; we've seen buy-side desks push for
  ±0.5 % with manual override as the resolution path.
- Whether the per-issuer rule pattern (Python files) holds when
  you cover 5+ jurisdictions. The pattern scales linearly per
  issuer; rules don't cross-talk.
- AE / SA / KW profile priority. Happy to coordinate who does
  what if there's a buy-side firm already shipping per-issuer
  rules internally.

Repo: https://github.com/Mine-FNL/qstocks-filing-tool
Live bench: https://mine-fnl.github.io/qstocks-filing-tool/demo.html
Architecture deep-dive: https://mine-fnl.github.io/qstocks-filing-tool/architecture/

— Mine-FNL team

---

## Posting guidance

- **First paragraph** is the "see more" cut. ≤ 220 chars.
- **No hashtags** in the body (LinkedIn deprioritises hashtagged
  posts in the algo).
- **Tag individuals** who might benefit from a heads-up, but
  sparingly — the audience is the algo, not the tag-list.
- **Reply to every substantive comment** within 24 h, in the same
  measured technical voice. Comments are how this kind of post
  finds second-degree distribution.
