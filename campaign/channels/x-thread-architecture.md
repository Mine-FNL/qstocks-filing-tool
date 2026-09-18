# X thread — architecture deep-dive (10 tweets)

**Asset:** `campaign/assets/architecture-16x9.jpg` (tweet 3)
**Use:** Post in addition to the canonical `x-thread.md` (15 tweets, the launch thread). Best slotted 5–7 days after the launch thread so the cadence doesn't collapse into one day.

---

**1/** Most "PDF → JSON" extractors treat the LLM as the source of truth for *numbers*.

That's a category error. Numbers live in tables; the LLM hallucinates 5–10 % of them.

We wrote a deterministic-first extraction engine. Here's how it works. 🧵

**2/** The pipeline:

```
PDF → pdfplumber (tables) → account-code map → JSON
              ↓
              LLM (gaps only: audit opinion, notes, segments)
```

Two parallel paths. Numbers go through `pdfplumber`, sign- and scale-corrected in code. Gaps go through the LLM.

Result: every line item is tagged `basis: "parsed"` or `basis: "llm"`.

**3/** [image: architecture-16x9.jpg]

**4/** Why this matters: **the same numbers come out regardless of which LLM you point at**. A 270M local model produces the same numerical contract as GPT-4o.

Numbers never pass through the model → numbers can never be hallucinated.

**5/** The cost math:

```
Cloud model (per filing):  $0.04–0.12 + 4–8s latency
Local 270M (per filing):   $0      + 1.2s latency
```

For a 5,000-filing/year ingest, that's $200–600 → $0, with no accuracy loss.

**6/** The LLM is still useful — for the *gaps*:

- Audit opinion classification (qualified / unqualified / disclaimer)
- Note-text summarisation (5–10 line TL;DR per disclosure note)
- Segment labels (geographic / business / product)

These are tasks where a small model is fine, and where hallucination doesn't corrupt the data, just the prose.

**7/** The `basis` field is the key. A downstream consumer who wants a fully-deterministic record can filter on `"basis": "parsed"` and ignore the model entirely:

```python
deterministic = [li for li in filing["line_items"]
                 if li["basis"] == "parsed"]
```

Same numbers on every re-extraction, forever.

**8/** Where we got it wrong the first time:

We started with "let the LLM extract everything" — the standard pattern. After three months of debugging hallucinated numbers, we swapped to deterministic-first.

The result was an 8× reduction in extraction variance and a 0.5pp pass-rate jump on the bench. Sometimes the boring answer is right.

**9/** Where the architecture breaks:

- Image-only PDFs (no text layer). Opt-in OCR with `--ocr auto` works but costs accuracy.
- Non-tabular financial reports (rare; mostly old filings).
- Heavy use of footnotes for the actual numbers (some IFRS-for-SME filings).

**10/** Repo, demo, bench:

📦 https://github.com/Mine-FNL/qstocks-filing-tool
📊 https://mine-fnl.github.io/qstocks-filing-tool/demo.html
📄 Whitepaper: `whitepaper/whitepaper.md`

If this architecture is useful, a star helps us know to write the next paper on it. RTs appreciated. 🤝

---

**Posting notes:**

- Best time: Tue–Thu, 9–11am ET.
- Quote-tweet the launch thread's tweet 2 with this thread's tweet 1 so
  the audience carries over.
- No need to re-post the demo video here; the architecture diagram is
  the right asset for this angle.
