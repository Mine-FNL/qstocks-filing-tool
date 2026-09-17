# Show HN — paste-ready

> This file contains the **final-form text** for the Show HN post.
> Copy the **Title** into the Title field, then copy the entire
> **Body** below it into the Body field. Leave the **URL field
> empty** (the repo URL goes in the body text — Show HN convention).

---

## Title

```
Show HN: qscreen-filing-tool – Open-weight PDF → lossless filing JSON
```

(58 characters; under HN's 80-char cap.)

---

## Body

```
We (Mine-FNL) shipped an open-weight, jurisdiction-agnostic engine that turns
any exchange's PDF annual / interim report (QSE-shipping; AE/SA/KW-ready)
into a single stable, fingerprintable JSON, ready to ingest.

The headline: 80.6% on the 8-case golden-set bench, 485 unit tests
passing, and every release carries a CycloneDX SBOM, a Sigstore keyless
signature against the GH OIDC identity, and an in-toto SLSA v1
attestation — `gh attestation verify` works end-to-end against the
release tag.

https://github.com/Mine-FNL/qstocks-filing-tool

![demo flow](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/campaign/assets/demo-flow-16x9.jpg)

What it actually does, in 5 stages (architecture diagram →

![architecture diagram](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/campaign/assets/architecture-16x9.jpg)

1. PDF LOADER — pdfplumber-based page list with `pages[]` envelope.

2. LAYOUT ANALYZER — statement segmentation; bilingual (Arabic + English)
   page-level language detection.

3. LINE-ITEM EXTRACTOR — table parse with auto-correction fallback.

4. GATES ENGINE — math-identity checks (Assets = Liabilities + Equity,
   Δ tolerance ±2pct), 11 cross-cutting pre-flags (related-party
   concentration, ROE vs Ke, etc.), and 25 issuer-specific rules (UDCD
   IP at 47% of TA, ZHCD 8-of-10-year qualified auditor history,
   QIGD 3×-renamed entity, etc.).

5. FINGERPRINTER — SHA-256 over the normalized text + schema version;
   gives stable cross-run regression detection.

Why we think this is interesting even if you don't trade QSE:

- No GPU needed: plain Python, runs on a laptop. pdfplumber + heuristics;
  no frontier LLM in the extraction path. Total runtime: ~3 s per filing.
- Verified build chain end-to-end: SBOM on every release, Sigstore
  signing, SLSA L1 attestation. Can be consumed by `gh attestation verify`
  against the release tag — no long-lived secrets anywhere.
- Three independent install paths, none of which require PyPI access:
    docker pull ghcr.io/Mine-FNL/qstocks-filing-tool:v1.6.1
    pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/download/v1.6.1/qscreen_filing_tool-1.6.1-py3-none-any.whl
    pip install --extra-index-url https://mine-fnl.github.io/qstocks-filing-tool/simple/ qscreen-filing-tool
- Lossless + audit-friendly: a re-ingest of the same PDF produces a
  bit-identical record (fingerprint=hash). Every merge into main runs
  the 8-case golden-set bench; bench failure blocks the release.

Pluggable profiles: the QSE profile ships with the repo; an AE / SA / KW
profile is one PR away once an analyst contributes the per-issuer
pre-flag rules for that jurisdiction.

Where to start:

- repo: https://github.com/Mine-FNL/qstocks-filing-tool
- live bench: https://mine-fnl.github.io/qstocks-filing-tool/demo.html
- 5-min install: https://mine-fnl.github.io/qstocks-filing-tool/install/
- supply-chain + verify recipe: https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/SECURITY.md

Happy to dig into any of the 5 stages in the comments — happy to take
PRs for additional jurisdiction profiles (AE / SA / KW are obvious gaps).

— Mine-FNL
```

---

## Posting instructions

1. Open https://news.ycombinator.com/submit in a clean browser
   session (one you've logged in from before — HN dislikes new
   accounts with high-volume posts).
2. Click "Show HN".
3. Paste title; paste body; **leave URL field empty**.
4. Solve the captcha.
5. Click Submit.

Time window: Tuesday–Thursday **08:00–10:00 US/Eastern** has the
highest technical-reader engagement window. Avoid Mondays (other
stories dominate) and Fridays (low-engagement graveyard).

---

## First-hour comment playbook

HN rewards Show HN posts that respond well in the first 60–120 minutes.
The two comment categories that move stars:

A. **Architecture pushback** ("why this stage, why not a library")
   — answer with one short paragraph + a SHA-256 of the bench run
   so the number is verifiable, not a marketing summary.

B. **Comparable tool / vendor references** ("why not Marker /
   Azure Document Intelligence / Unstructured") — answer with the
   comparison table from README.md (the table is the credible
   answer, not your prose).

C. **Install failures** — if someone can't reproduce the install, drop
   into the thread with the exact command and the SHA-256 of the wheel
   they should be downloading.

Pre-reply snippets you can paste quickly (avoids retyping):

    The 80.6% number comes from `qscreen_eval.py` against 8 hand-verified
    golden cases. You can reproduce deterministically in ~1 s:

        pip install -e ".[dev]"
        python qscreen_eval.py --json
        # exit 0 = at or above baseline; exit 1 = regression detected

    SHASUM of the bench JSON that produced that 80.6 number is in the
    commit history so you can reproduce byte-for-byte from main.

    The architecture diagram I posted earlier shows the 5 stages. The
    short answer to "why 5, not 1" is: each stage has independent
    failure modes and the gates (stage 4) catch the silent-data-loss
    bugs that the table parser (stage 3) misses. The fingerprint
    (stage 5) is the reproducibility receipt.

The standard HN trick: **if a comment is excellent and you have a
follow-on answer with a number, put the number at the top of the
reply.** HN upvotes comments with concrete facts first.

---

## What NOT to do

- Do not cross-link to a marketing page that has no code on it
- Do not assert "used by X company" without a public quote
- Do not respond to vague skeptics with longer essays — short
  answer + a file path, then move on
- Do not delete the post. Even if it flops it stays in the archive
  and benefits the next launch

---

## After first 24h

If the post crosses 50 upvotes by +12h: cross-post the show HN
URL into a tweet (let the conversation continue; don't ask for
stars in the tweet itself).

If it stalls below 20 by +12h: don't retry from a different
account — HN penalizes repeat-author re-posts. Move to the
r/MachineLearning / r/quant plans in campaign/channels/.
