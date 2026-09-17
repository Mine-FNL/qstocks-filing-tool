# Reddit r/quant — submission copy

## Title

> qscreen-filing-tool — open-weight, jurisdiction-agnostic financial
> filing extraction with built-in math-identity gates and stable
> SHA-256 fingerprints (QSE-shipping; AE/SA/KW-ready)

## Body

(link to `assets/demo-flow-16x9.jpg` first)

![demo flow](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/campaign/assets/demo-flow-16x9.jpg)

Built this for our internal quant desk and decided to ship it open
under MIT. We needed a deterministic, auditable PDF filing extractor
that runs on a laptop and produces a JSON we can re-ingest six months
later and get a bit-identical record from.

**The shape we ended up with:**

- One `python -m qscreen_ingest <pdf>` command. ~3 s per filing,
  no GPU, no API key in the binary path.
- Output is a single JSON with: `statements[]` (IS + BS + CF + CI),
  `line_items[]` (mapped to canonical account codes),
  `fingerprint` (SHA-256 of the normalized text + schema version),
  `pre_flags[]` (the issuer-aware red-flag catalog).
- 11 cross-cutting pre-flags (related-party concentration,
  receivables aging, ROE vs Ke, etc.) + 25 issuer-specific rules
  that fire on the merged filing. UDCD IP at 47 % of TA, ZHCD
  qualified auditor history, QIGD's 3 entity renames — these
  are *frozen as code* not ad-hoc SQL queries.

**Audit-friendly by construction:**

- Every merge into `main` runs the 8-case golden-set bench on a
  deterministic grid; bench regression fails the release.
- The fingerprint means you can prove "this PDF produced this JSON
  on this engine commit, full stop". `gh attestation verify` works
  against the wheel + sdist + SBOM.
- The 11 cross-cutting + 25 issuer-specific red-flags are codified
  in `profiles/qatar/pre_flags.py`. PRs that change those rules
  also have to update the rule-per-case bench fixture, so the rule
  set is the source of truth and the tests are the contract.

**QSE-only right now.** Adding AE / SA / KW is one PR per jurisdiction,
and the engine is profile-agnostic above the per-issuer rule layer.
The 25 issuer-specific rules for Qatar took one analyst about 3 days
to land; same cost for AE.

**Three install paths, none of which require PyPI:**

    docker pull ghcr.io/Mine-FNL/qstocks-filing-tool:v1.6.1
    pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/download/v1.6.1/qscreen_filing_tool-1.6.1-py3-none-any.whl
    pip install --extra-index-url https://mine-fnl.github.io/qstocks-filing-tool/simple/ qscreen-filing-tool

**Live numbers I can quote without hedging:**

- 80.6 % accuracy on the 8-case golden bench (100 / 124 checks).
- 485 unit tests passing.
- Total runtime: ~3 s per filing on a single core.
- Frozen-rule coverage: 11 + 25 = 36 active pre-flag rules in the
  QSE profile as of v1.6.1.

**Where I want feedback:**

- The math-identity gate tolerance (±2 % for BS asset = L + E) is
  empirical, derived from the QSE golden cases. Adjustable per
  jurisdiction, but I want to see your firm's policy before I pin
  it for AE / SA / KW.
- Whether the per-issuer rule pre-flag pattern (verbose Python
  dictionary) holds when you scale past ~50 issuers. If anyone has
  experience shipping this kind of catalog at scale, would value a
  red-team.

Repo + live demo:

- https://github.com/Mine-FNL/qstocks-filing-tool
- https://mine-fnl.github.io/qstocks-filing-tool/demo.html

---

## Posting guidance for r/quant

- **Direct, no hedging.** Quant audience expects specific numbers
  + the file path the number lives at.
- **Don't sell.** Present as "this exists, here are the trade-offs,
  here are the things I want feedback on". That reads as authentic
  in this subreddit; puffery reads as corporate.
- **Engage finance/quant-specific feedback deeply.** If someone
  says "your ±2 % tolerance misses X", dig in. That's the audience
  whose feedback actually moves the codebase.
- **No pricing / no business model.** Free open-source, MIT, no
  paid tier. If they ask: there isn't one.
