# X thread — bench story (10 tweets)

**Asset:** `campaign/assets/stats-card-16x9.jpg` (tweet 1)
**Use:** Bench-numbers-focused thread for the data-engineering crowd. Best posted 7–10 days after the launch thread.

---

**1/** [image: stats-card-16x9.jpg]

**2/** Our extraction pipeline is gated on a 124-check regression bench. The floor is 100/124 = 80.6 %.

Any PR that drops below fails CI. Any release that drops below fails the tag-push workflow.

This is the only way to ship an LLM-extraction pipeline and not lie about its quality.

**3/** What's in the 124 checks:

- 11 cross-cutting rules (Assets = L + E, currency consistency, scale consistency, auditor history, …)
- 25 issuer-specific pre-flag rules (UDCD IP at <47 % of TA, ZHCD Big-Four auditor history, QIGD's 3 entity renames, …)
- 88 specific filings × expected output tuples (numeric + categorical)

**4/** Why 88 specific filings and not just a held-out test set?

Because pre-flag rules are *ticker-specific knowledge* — UDCD's intangibles-as-percent-of-TA ceiling is an industry rule, not a model rule. You can't learn it from a generic held-out test.

So we ship the pre-flag rules in the profile, and the bench tests whether the engine applies them correctly.

**5/** The 24 checks we still fail are not random:

```
 7  multi-currency rollups (interim periods with FX swings)
 5  prior-year restatements (catches our diff logic, not extraction)
 4  segment-disclosure gaps (QSE doesn't always disclose segments)
 3  scanned-page OCR artifacts
 5  edge cases in unusual sector taxonomies (holding cos, SPACs)
```

None of them are "the model got a number wrong". All of them are
documented in the bench output.

**6/** The bench wall-time on CI (Ubuntu):

```
v1.0  → 9 min
v1.6.0 → 11 min
```

Slower than the unit-test suite because each filing is a real
end-to-end extraction. Faster than a human reviewer. The cost is
acceptable.

**7/** The bench output is the public demo page. Every release
regenerates it from `qscreen_eval.py --json`:

📊 https://mine-fnl.github.io/qstocks-filing-tool/demo.html

Anyone can read it. No login. No API key.

**8/** Why we don't gate on pass-rate percentage improvements:

We gate on **absolute floor**, not delta. The floor was 100/124 when
we set it. The floor is 100/124 today. The floor will be 100/124
tomorrow.

Delta gating rewards metric-gaming; absolute gating rewards
reliability.

**9/** What the bench *doesn't* catch:

- Audit-opinion misclassification (subjective; bench can't grade it)
- Note-text summarisation quality (BLEU/ROUGE wouldn't be honest)
- Long-tail issuer-specific quirks outside the pre-flag ruleset

We document these in the whitepaper's "Limitations" section (§7).

**10/** The bench is the contract.

If a PR claims "improved accuracy" but the bench doesn't move, the
PR is a no-op. If a PR moves the bench, the release notes say so.

📦 https://github.com/Mine-FNL/qstocks-filing-tool
📄 Bench methodology: `whitepaper/whitepaper.md` §5

Star if you want this style of bench-discipline to spread.

---

**Posting notes:**

- The stats-card image is dense — readers will spend ~10s on it before
  tapping through. That's the goal.
- Best response prompt: "What's a bench gate you've held for >6 months
  without moving the floor?"
