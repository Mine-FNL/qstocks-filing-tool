# dev.to long-form post

**Recommended day ~7 after Show HN** (after the HN signal settles). dev.to
favors longer, more didactic posts — restructure the HN body into a tutorial
shape. 1,800–2,400 words is the sweet spot.

---

## Title (≤ 100 chars, will be the H1)

```
Building a financial PDF extractor with built-in consistency gates
```

## Series / canonical URL

```
https://dev.to/mine-fnl/building-a-financial-pdf-extractor-with-built-in-consistency-gates
```

## Cover image

`campaign/assets/architecture-16x9.jpg` (2K).

## Body (Markdown — dev.to flavor)

```markdown
---
title: "Building a financial PDF extractor with built-in consistency gates"
published: true
description: "A jurisdiction-agnostic Python engine that turns a PDF financial
report into a lossless, auditable JSON object — with a math-identity gate that
refuses to ship self-contradictory records."
cover_image: https://raw.githubusercontent.com/Mine-FNL/qstocks-filing-tool/main/campaign/assets/architecture-16x9.jpg
tags: python, opensource, finance, pdf, datascience
canonical_url: https://github.com/Mine-FNL/qstocks-filing-tool
---

> Headline result: 6 lines of Python turns a PDF annual report into a
> schema-stable JSON object that downstream code can ingest without
> reconciliation. ~3 seconds per filing, $0 API cost, fully offline if
> you want.

## Why a "filing contract" instead of "table extraction"

If you've ever tried to ship a downstream pipeline that consumes financial
filings, you've hit this wall:

- The PDF's tables are laid out for humans, not machines.
- The audit opinion lives in prose paragraphs the table extractor ignores.
- The same filing, re-extracted on a different engine commit, produces a
  *different* JSON — which means you can't diff or fingerprint.
- Most extractors happily ship the JSON even when the line items
  internally contradict each other (Assets ≠ L + E by 5%, no warning).

`qscreen-filing-tool` is the tool we built to make those problems go away.

## Install

```bash
pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/latest/download/qscreen_filing_tool-1.6.0-py3-none-any.whl
```

(also on a PEP 503 simple index at
`mine-fnl.github.io/qstocks-filing-tool/simple/` and as a container at
`ghcr.io/Mine-FNL/qstocks-filing-tool:v1.6.0`)

## The 30-second demo

```bash
# 1. Pull the wheel and a sample PDF
curl -fsSL https://raw.githubusercontent.com/Mine-FNL/qstocks-filing-tool/main/install.sh | bash
qscreen-ingest report.pdf --symbol AKHI --year 2022
# → writes ./AKHI_2022_FY_filing.json in ~3 seconds
```

## The three things that matter

### 1. Deterministic-first extraction

The PDF tables are read in code. The LLM only fills *gaps* (audit opinion
classification, note-text summarization, segment labels). Numbers never
pass through the model.

This is why a 270M local model produces the same lossless filing contract
as a frontier cloud model: the numbers come from `pdfplumber`, not from
the LLM.

### 2. The math-identity gate

The JSON won't ship if `Assets ≠ L + Equity` within ±2% (with sector-aware
overrides). Eleven cross-cutting + twenty-five issuer-specific pre-flag
rules run before `save()`. If a record contradicts itself, the record
doesn't ship — and the evidence points at the offending line item.

### 3. SHA-256 cross-filing fingerprints

Re-ingest the same PDF on any engine commit → JSON with the **same
SHA-256 fingerprint**. Bit-identical across upgrades. Combine with
Sigstore keyless signing and you can cryptographically prove "this PDF
produced this JSON on this commit".

## Architecture

![architecture](https://raw.githubusercontent.com/Mine-FNL/qstocks-filing-tool/main/campaign/assets/architecture-16x9.jpg)

(continued in the README — see
[docs/SHOW_HN.md](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/docs/SHOW_HN.md)
for the full architectural deep-dive)

## The bench

Every PR runs 124 cross-filing checks against the current Qatar-listed
universe. The current regression floor is 100/124 = 80.6%. The bench
output is the demo page at
<https://mine-fnl.github.io/qstocks-filing-tool/demo.html>.

## What's not in scope

- OCR of *image-only* PDFs is opt-in (`--ocr auto`) and needs the
  `tesseract` system binary. Text-layer PDFs (the common case for
  audited annual reports) work out of the box.
- The default `qatar` profile ships 55 tickers; other markets need a
  profile drop under `profiles/`.

## Try it

```bash
git clone https://github.com/Mine-FNL/qstocks-filing-tool
cd qstocks-filing-tool && pip install -e ".[dev]"
python qscreen_ingest.py --self-test   # 485-test offline contract gate
```

Star the repo if the architecture resonates. Issues and PRs welcome.
```

## Asset checklist

- [ ] Cover image: `architecture-16x9.jpg` uploaded to dev.to media
- [ ] Canonical URL set to GitHub repo
- [ ] Series tag `python` (1st), `opensource` (2nd) for reach
- [ ] Pin to profile (`Settings → Publishing → Pin`)
- [ ] Cross-link from repo README's "Tutorials" section if it lands well
