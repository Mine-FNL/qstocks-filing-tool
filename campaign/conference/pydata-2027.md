# PyData Berlin 2027 — talk submission

**Title (≤ 80 chars):**
> A deterministic-first architecture for financial-document extraction

**Talk type:** 25-minute community talk

**Track:** Data Engineering in Production

**Audience level:** Data engineers, ML engineers, finance-tech practitioners.

---

## Abstract (250 words)

The "deterministic-first" pattern is one of those things that's obvious in
retrospect and hard to spot in advance. We spent six months building an
extraction pipeline for financial filings where the production requirement
was: re-ingesting the same PDF on any engine commit must produce
byte-identical JSON, cryptographically attestable back to the engine
commit that produced it.

We got there by stopping asking the LLM to do the thing it isn't good
at — reading tables — and starting to ask it only to do the thing it
is good at — filling gaps.

This talk walks through:

- **Why "let the LLM read the numbers" is a category error.** Numbers
  live in tables. Tables are a parsing problem, not a language-model
  problem.
- **The 3-bet architecture.** Deterministic-first extraction,
  math-identity gate, SHA-256 cross-filing fingerprints. Why each one
  was necessary; what broke when we tried to skip any of them.
- **The bench as contract.** 124 cross-filing checks, regression
  floor 100/124 (80.6%). The bench is the only honest way to ship an
  LLM-extraction pipeline.
- **The supply-chain story.** SBOM (CycloneDX 1.5), Sigstore keyless
  signing, SLSA Build L3 attestation, CodeQL on every PR + main +
  weekly, `pip-audit` non-blocking. Why compliance teams ask for these
  and what they cost.

We'll show live: a 270M local model producing the same filing JSON as
GPT-4o, a math-identity gate blocking a self-contradicting record with
evidence, and a `gh attestation verify` against a public release.

The architecture generalises: any pipeline that consumes structured
documents (invoices, contracts, shipping manifests) can apply the same
pattern. The trick is to identify which fields are parsing-problems
and which are language-model problems.

## Outline

1. **Where "AI extractors" break** (4 min)
2. **The 3 bets** (8 min, with live demo)
3. **The bench as contract** (5 min)
4. **The supply-chain story** (4 min)
5. **What we got wrong** (4 min — honest limitations + roadmap)

## Pitch (≤ 200 chars)

> A deterministic-first extraction pipeline where numbers never pass
> through the model. 270M local model = same contract as GPT-4o.
> Math-identity gate blocks self-contradicting records. SHA-256 +
> Sigstore + SLSA L3. Public 124-check bench.

## Speaker notes

- Berlin audience skews toward applied ML + data-engineering
  practitioners. Lean on the bench-discipline message and away from
  pure ML novelty.
- Avoid "AI" hype in the title; "deterministic-first" is the hook.
- Live-demo segment is high-risk; pre-record backup clips for each.
