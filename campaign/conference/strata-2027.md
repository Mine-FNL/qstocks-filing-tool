# Strata Data Conference 2027 — talk submission

**Title (≤ 80 chars):**
> Reproducible financial filing extraction: the supply-chain playbook

**Talk type:** 40-minute industry talk

**Track:** Data Engineering & Architecture / Finance

**Audience level:** Senior data engineers, platform engineers, CTOs at
financial-data and quant firms.

---

## Abstract (300 words)

A "PDF to JSON" pipeline that compliance teams will accept is a different
beast from a "PDF to JSON" pipeline that demos well on a tweet. The
distinction is *reproducibility* + *provenance* + *attestation*.

This talk walks through the production playbook we built for a
financial-document extraction pipeline serving compliance-sensitive
buyers. The bench is the regression floor (124 cross-filing checks,
100/124 floor, 80.6 %); the supply chain is the procurement
conversation (SBOM, Sigstore, SLSA L3, CodeQL, container signing on
the roadmap).

Three architectural bets make the pipeline credible to a compliance
auditor:

1. **Deterministic-first extraction.** Numbers never pass through the
   LLM. A 270M local model produces the same numerical contract as
   GPT-4o. This property — "the LLM cannot be the source of
   numerical error" — is what makes the deterministic fingerprint
   meaningful.

2. **Math-identity gate at the write path.** The JSON cannot ship if
   it contradicts itself (Assets ≠ L + E, currency inconsistency,
   scale inconsistency, etc.). Eleven cross-cutting + twenty-five
   issuer-specific pre-flag rules. Blocked records stay on disk with
   evidence; they don't propagate.

3. **SHA-256 cross-filing fingerprints + Sigstore keyless signing +
   SLSA Build L3 attestation.** Every release produces a wheel, an
   SBOM, a Sigstore bundle, a SLSA v1 receipt, and a multi-arch
   container. The chain is verifiable by a third party without
   cooperating with the operator.

The talk is targeted at senior engineers and CTOs who need to make a
build-vs-buy decision on financial-document data infrastructure. The
take-away: *what* the data is, is detached from *how* it was produced
— and the supply-chain hardening is what closes that gap.

## Outline (40 min)

1. **The compliance-data problem** (5 min)
2. **Three bets** (15 min, live demos)
3. **The supply-chain playbook** (10 min — checklists + costs)
4. **The procurement conversation** (5 min)
5. **Q&A** (5 min)

## Speaker notes

- Strata audience is heavier on enterprise architecture than PyCon.
  Lean on the "compliance teams will accept" framing.
- The 40-min slot allows for a more leisurely pace + one extended Q&A.
- Bring backup slides for every live-demo segment; ship the demo
  recording with the slides in case of A/V failure.

## Pitch (≤ 200 chars)

> A reproducible financial-document pipeline with deterministic-first
> extraction, math-identity gates, and Sigstore + SLSA L3 attestation
> — the supply-chain playbook compliance teams actually accept.
