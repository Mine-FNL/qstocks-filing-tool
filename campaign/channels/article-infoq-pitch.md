# InfoQ / The New Stack / industry-press pitch

**Recommended cadence:** Send the pitch 7–10 days after Show HN (let the HN signal give the journalist cover).
**Targets:** InfoQ, The New Stack, ACM Queue, IEEE Software.

---

## Pitch email (≤ 300 words)

```
Subject: How a 270M-parameter local model beat GPT-4o on a financial
         PDF extraction benchmark — and what that says about LLM
         pipelines generally

Hi [editor],

I'd like to pitch a story on a counterintuitive finding from six months
of building an open-source financial-document extraction pipeline
(qscreen-filing-tool, MIT-licensed, 485 tests, 124-check bench at
80.6 %).

The finding: a 270M-parameter local model produces the same lossless
filing contract as GPT-4o or Claude Sonnet 4 — but only because we
stopped asking the model to do the part it isn't good at (reading
tables) and started asking it only to do the part it is good at (filling
gaps).

The architectural inversion — "deterministic-first extraction" — has
three properties that I think will resonate with your readers:

1. **Numbers never pass through the model.** Tables are parsed in code;
   the model fills audit opinion, note text, and segment labels.
2. **The math-identity gate refuses to ship self-contradictory records.**
   Assets = L + E is enforced ±2 % with sector-aware overrides; the
   record doesn't ship if it fails.
3. **SHA-256 cross-filing fingerprints + Sigstore keyless signing.**
   Re-ingesting the same PDF on any engine commit produces bit-identical
   JSON, cryptographically attestable back to the engine commit.

I have a 6,000-word whitepaper, a public demo page (regenerated on
every release), and reproducible benchmarks. Happy to do a 30-minute
walkthrough or send written materials.

Repo:        https://github.com/Mine-FNL/qstocks-filing-tool
Demo:        https://mine-fnl.github.io/qstocks-filing-tool/demo.html
Whitepaper:  https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.md

— [Your name]
```

## Target editors (ranked by fit)

| Outlet       | Editor (or last known)              | Why they'll care                                                                 |
|--------------|-------------------------------------|----------------------------------------------------------------------------------|
| InfoQ        | Editor-in-chief: Thomas Betts; ML / data eng: Charles Humble    | ML + data-eng readership; the architectural-inversion angle is a good fit.       |
| The New Stack | Alex Williams (founder); Lynne Rowald (production)              | Open-source + production-grade supply-chain story.                                |
| ACM Queue    | Articles editor: Dean Hendrix                                   | Practitioner-oriented, less hype-driven; supply-chain hardening is in their wheelhouse. |
| IEEE Software| Special-issues editor                                            | Architectural / engineering-rigor angle; less "ML demo" and more "engineering practice". |
| The Pragmatic Engineer (newsletter) | Gergely Orosz                | 250k+ subscribers; loves deep-dives on engineering practice + open-source projects. |
| Last Week in AWS (newsletter)       | Corey Quinn                  | Supply-chain / open-source-distribution angle fits his beat. |

## Follow-up cadence (1/3/7 day rule)

- **Day 1**: If no reply, send a one-line bump with a relevant recent
  tweet / HN thread URL as additional context.
- **Day 3**: Final bump with an alternative angle ("happy to frame this
  as a supply-chain story instead, or a data-engineering story — let me
  know what fits your calendar").
- **Day 7**: Stop. Move to the next outlet.

## What we will *not* do

- Pitch a "GPT-4o killer" angle. The story is more nuanced than that;
  the architecture is the point, not the model.
- Offer an exclusive. We want the story in front of the broadest
  audience possible.
- Promise an interview with "the founder". The project is open-source
  and the maintainer is the canonical source.
