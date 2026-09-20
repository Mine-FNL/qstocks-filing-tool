# X thread — channel copy

Aimed at the data-engineering / quant / OSS community.

(15 tweets total. Numbers in [brackets] are character counts; Twitter
limits each tweet to 280. Trim any naturally.)

---

**Tweet 1** (the hook — the only one most people will see)

> We just shipped an open-weight engine that turns any exchange's PDF
> financial filing into lossless, fingerprintable JSON. No GPU. No LLM
> in the extract path. ~3 s per filing.
>
> 499 tests. 80.6 % bench. SLSA v1 attested on every release.
>
> https://github.com/Mine-FNL/qstocks-filing-tool
> [276]

**Tweet 2** (problem statement — for the audience that scrolls past)

> The bottleneck in financial-data extraction isn't the LLM. It's the
> math-identity check that says "your BS_TOTAL_ASSETS ≠ L + E by 4 pct".
> Most pipelines ignore it. The result: silent contradictions between
> the IS, BS, and CF in the JSON your downstream tool ingests.
> [246]

**Tweet 3** (architecture teaser)

> The pipeline runs in 5 deterministic stages with zero external calls:
>   PDF → page list → statement segment → table parse → math gates
>   → SHA-256 fingerprint
> Math gates fire the 11 cross-cutting + 25 issuer-specific pre-flag
> rules. Most firms stop at the table parse; the gates catch what
> deterministic extractors miss.
> [272]

**Tweet 4** (architecture diagram — IMAGE)

> ![architecture](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/campaign/assets/architecture-16x9.jpg)
>
> Five-stage deterministic pipeline. Every release artefact is
> cryptographically attributable to a specific commit SHA via in-toto
> SLSA v1. [170]

**Tweet 5** (the supply-chain story — what makes this not just "another pdf parser")

> What's unusual for a 1.6.x Python tool in 2026:
>
> - CycloneDX SBOM on every release tag
> - Sigstore keyless signed wheel + sdist
> - SLSA Build L3 attestation (GitHub-native; `gh attestation verify`
>   works against the release tag)
> - Container image published to ghcr.io on the same tag, multi-arch
> [240]

**Tweet 6** (verification recipe)

> Consumer-side, the receipt is end-to-end:
>
>   pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/download/v1.6.1/qscreen_filing_tool-1.6.1-py3-none-any.whl
>   gh attestation verify dist/<file> \\
>     --repo Mine-FNL/qstocks-filing-tool
>
> No PyPI UI click required. No long-lived token. [220]

**Tweet 7** (demo-flow image)

> ![demo](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/campaign/assets/demo-flow-16x9.jpg)
>
> Left: a balance-sheet PDF (with Arabic). Right: a JSON with a
> verifiable SHA-256 fingerprint + three supply-chain badges. [196]

**Tweet 8** (real numbers)

> Bench numbers (8 hand-verified golden cases, deterministic only):
>
> QNBK 2023 FY: 19 / 26 (BS + IS + CF + pre_flag checks)
> QIBK 2023 FY: 15 / 21
> IQCD 2022 FY: 14 / 16
> UDCD 2022 FY: 11 / 13
>
> Total: 100 / 124 = 80.6 % [210]

**Tweet 9** (what's not new)

> What's not new in this:
>
> - pdfplumber for tables
> - tesseract / rapidocr for scanned pages
> - BEIR-style eval harness
> - SHA-256 fingerprinting
>
> What we think is new:
> The jurisdictional pre-flag **catalog** is a first-class step. [200]

**Tweet 10** (the unique insight)

> Most extraction pipelines bolt-on the red-flag detection after the
> JSON is shipped. We run the catalog AS PART OF the extract path.
>
> Result: an extracted record either passes the gate or fails with
> evidence pointing to the specific line item. There's no "we will
> review this later" path.
> [236]

**Tweet 11** (pluggability)

> Adding a new jurisdiction (AE / SA / KW are obvious gaps) is ~25
> issuer-specific rules + a few statement templates. ~3 days of work
> for an analyst.
>
> The pipeline is profile-agnostic above that layer; one PR is a new
> jurisdiction. [220]

**Tweet 12** (call for collaboration)

> If you work an exchange-issuer desc pipeline and you want to ship
> an open-source counterpart, the take-off cost is low:
>
> 1. Pick a profile name
> 2. Write the per-issuer rules (~25)
> 3. PR profiles/<jurisdiction>/
>
> We review those PRs on priority. [202]

**Tweet 13** (bench autonomy stat)

> Re-run the regression detector anywhere:
>
>   $ pip install -e ".[dev]"
>   $ python qscreen_eval.py
>   100/124 = 80.6%
>
> 0.7 s on a laptop. We're bench-tying to a release-tag-locked
> baseline so any PR that moves the number is auto-flagged. [184]

**Tweet 14** (where the live demo lives)

> Live bench report:
>
> https://mine-fnl.github.io/qstocks-filing-tool/demo.html
>
> One page. Auto-regenerated on every push to docs/. The numbers you
> see there are the same as what CI sees at PR time.
> [178]

**Tweet 15** (CTA — last tweet)

> If this sounds like something your team would use, the install path
> is one line:
>
>   docker pull ghcr.io/Mine-FNL/qstocks-filing-tool:v1.6.1
>
> Stars help us discover new engineers who'd want to contribute. 🙏
>
> https://github.com/Mine-FNL/qstocks-filing-tool
> [210]

## Posting guidance

- **Time:** Tuesday 9 AM ET is the best slot for a tech audience.
- **Cadence:** post tweets 1-3 first as a teaser thread, then tweets
  4-10 spaced ~30 min apart over the day. Tweets 11-15 spread over
  the rest of the week.
- **Reply targets:** monitor @github mentions, the project maintainer
  handle if any, and any high-follower finance/quant accounts that
  might engage. Reply in the same technical voice; don't shill.
- **Don't:** auto-DM followers about the project. Don't reply to
  unrelated high-traffic threads with shilling. Don't post the same
  thread twice in a week.
