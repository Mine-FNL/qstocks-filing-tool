# Medium long-form: Why we extracted numbers deterministically and let the LLM only fill gaps

**Recommended cadence:** ~14 days after Show HN (after HN signal has settled and dev.to has indexed).
**Target publication:** [Better Programming](https://medium.com/better-programming) (owned by Medium) or
[Level Up Coding](https://levelup.gitconnected.com) — both have established finance/ML readerships.

---

## Pitch (200 words)

Most LLM-based PDF extraction pipelines treat the model as the source of truth for *numbers*. That's a category error.

I spent six months building an extraction pipeline for financial filings. Here's what changed when I stopped asking the LLM to read the numbers and started asking it only to fill gaps:

- Numbers became deterministic. Same PDF, any model, same output.
- Hallucinated numbers went from ~5–10 % to ~0 %.
- A 270M local model now produces the same contract as GPT-4o.
- Per-filing cost went from $0.04–0.12 to $0.
- The bench pass rate climbed from 70 % to 80 %.

The architecture (deterministic-first extraction, math-identity gate, SHA-256 cross-filing fingerprint) is open-source and the bench is public. This is the post I'd have wanted to read before I started.

---

## Title candidates (A/B test)

```
A: Why we stopped asking the LLM to read the numbers
B: A deterministic-first architecture for financial PDF extraction
C: Numbers never pass through the model: lessons from 6 months of
   financial-document extraction
```

## Cover image

`campaign/assets/architecture-16x9.jpg` (resized to 1400×788 for Medium).

## Body (Markdown → Medium rich-text)

```markdown
# Why we stopped asking the LLM to read the numbers

## The pattern everyone starts with

Six months ago, when we started building an extraction pipeline for
financial filings, the standard architecture was obvious:

> 1. Send the PDF to the LLM.
> 2. Ask it to extract every number, note, and segment.
> 3. Parse the JSON it returns.
> 4. Ship.

It's also wrong.

## The category error

A "category error" is the mistake of treating something as belonging to
a category it doesn't actually fit in. In this case: numbers belong to
**the PDF's tables**. They live there in typed cells, with explicit
signs, scales, and parent-column references. Asking the LLM to read a
table is asking it to do something it's not good at — and ignoring
something it shouldn't be asked to do at all.

Tables are not a language-model problem. They are a parsing problem.

## What we changed

We inverted the pipeline:

> 1. Parse the PDF tables in code (`pdfplumber`).
> 2. Sign- and scale-correct the cells using the profile's account-code
>    map.
> 3. Stamp the result as `basis: "parsed"`.
> 4. *Then* send the gaps (audit opinion, notes, segments) to the LLM.
> 5. Stamp those as `basis: "llm"`.

Every numeric value in the output JSON carries its `basis`. Downstream
consumers who want a fully-deterministic record filter on
`basis: "parsed"` and ignore the model entirely.

## What changed downstream

### Cost

```
Before:  GPT-4o per filing        ≈ $0.04–0.12 + 4–8s
After:   270M local model per filing = $0       + 1.2s
```

For a 5,000-filing/year ingest: **$200–600 → $0**.

### Accuracy

Hallucinated numbers went from ~5–10 % (the LLM "reading" the table) to
~0 % (the LLM doesn't read tables). The numbers come from `pdfplumber`.
The LLM only fills gaps.

### Reproducibility

Same PDF + same engine commit = same JSON, byte-for-byte. The hash is
stable across model upgrades. The hash is stable across LLM provider
changes. The hash is stable across continent.

### The bench

The bench is 124 cross-filing checks against the current Qatar-listed
universe. With the deterministic-first architecture:

- v1.0 (LLM reads everything): 87/124 (70.2 %)
- v1.6.0 (LLM fills gaps only): 100/124 (80.6 %)

Same benchmark, same floor, same gate.

## The honest limitations

This architecture isn't free. Three things break:

1. **Image-only PDFs.** Without a text layer, there's nothing for
   `pdfplumber` to read. Opt-in OCR with `--ocr auto` works but
   sacrifices accuracy.
2. **Heavy use of footnotes for the actual numbers.** Rare in IFRS,
   more common in IFRS-for-SME filings.
3. **Non-tabular financial reports.** Old filings; niche.

For the 90 % case (audited annual / interim reports with a text layer),
this is the right architecture.

## The same architecture, different language

If you've worked on data-extraction pipelines for any structured
document — invoices, contracts, medical records, shipping manifests —
this same principle applies:

> If the answer lives in a table, parse the table. If the answer lives
> in prose, ask the model.

Treating "extract structured data from a PDF" as a single model task
ignores the actual structure of the source.

## Try it

```bash
pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/latest/download/qscreen_filing_tool-1.6.0-py3-none-any.whl
qscreen-ingest report.pdf --symbol <TICKER> --year <YYYY>
```

Repository: https://github.com/Mine-FNL/qstocks-filing-tool
Demo:        https://mine-fnl.github.io/qstocks-filing-tool/demo.html
Whitepaper:  https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.md

Star the repo if this architecture resonates. Issues and PRs welcome.
```

## Tags

`python`, `machine-learning`, `data-engineering`, `open-source`, `llm`, `pdf`, `finance`

## Submission notes

- Better Programming accepts pieces 800–2,500 words. This clocks at
  ~1,100 words — within range.
- Add 1 image (the architecture diagram) around the "We inverted the
  pipeline" section.
- Submit to Better Programming first; if rejected, fall back to
  Level Up Coding, then Towards Data Science.
- Cross-link from the repo's `README.md` "Articles" section after
  publication.
