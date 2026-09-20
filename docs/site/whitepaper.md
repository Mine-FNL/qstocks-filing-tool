# Whitepaper

> *Lossless Filing JSON: A Deterministic-First Architecture for Financial PDF
> Extraction with Built-In Consistency Gates*
>
> qscreen-filing-tool maintainers · v1.0 · September 2026 · MIT licence

## Read it

| Format | Link |
|---|---|
| **PDF (recommended)** | [whitepaper/whitepaper.pdf](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.pdf) (~10 pages, typeset) |
| **HTML** | [whitepaper/whitepaper.html](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.html) (self-contained, TOC + CSS embedded) |
| **Markdown (source)** | [whitepaper/whitepaper.md](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.md) (~6,000 words, 9 sections + 3 appendices) |

## TL;DR

A jurisdiction-agnostic engine that turns any exchange's annual or interim
report into a schema-stable, audit-traceable JSON object — in approximately
three seconds per filing, with no API cost, and with a math-identity gate
that refuses to ship self-contradictory records.

The architecture rests on three bets:

1. **Deterministic-first extraction.** PDF tables are read in code
   (`pdfplumber`); the language model only fills *gaps* (audit opinion,
   notes, segment labels). A 270-million-parameter local model produces
   the same lossless contract as a frontier cloud model.
2. **Math-identity gate.** The JSON won't ship if `Assets ≠ Liabilities +
   Equity` within a sector-aware tolerance band, with eleven cross-cutting
   and twenty-five issuer-specific pre-flag rules.
3. **SHA-256 cross-filing fingerprints + Sigstore keyless signing + SLSA
   Build L3 attestation.** Re-ingesting the same PDF on any engine commit
   produces bit-identical JSON, cryptographically attestable back to the
   engine commit.

Across a 124-check regression bench against the current Qatar-listed
universe, the engine reaches 100/124 (80.6 %). The bench fails any pull
request that drops below the floor.

## Sections

1. **Introduction** — three audiences (data eng, compliance, OSS maintainers)
2. **Problem** — three failure modes of existing extractors
3. **Approach** — the three architectural bets
4. **Implementation** — profile pluggability, supply-chain hardening
5. **Bench Results** — 124 cross-filing checks, 100/124 floor
6. **Threat Model** — six threat categories, mitigations
7. **Limitations** — honest ceilings documented
8. **Roadmap** — Now → v1.7.0 → v2.0 → future
9. **Conclusion** — invitation to engage

Plus three appendices: reproducing the bench, verifying a release,
citing this paper.

## How to cite

```bibtex
@techreport{qscreen2026whitepaper,
  title        = {Lossless Filing JSON: A Deterministic-First Architecture
                  for Financial PDF Extraction with Built-In Consistency Gates},
  author       = {{qscreen-filing-tool maintainers}},
  year         = {2026},
  month        = sep,
  number       = {v1.0},
  institution  = {Mine-FNL},
  url          = {https://github.com/Mine-FNL/qstocks-filing-tool},
  note         = {MIT licence}
}
```

## Reproducing the bench

```bash
git clone https://github.com/Mine-FNL/qstocks-filing-tool
cd qstocks-filing-tool
pip install -e ".[dev]"
python qscreen_ingest.py --self-test          # 499-test contract gate
python qscreen_eval.py --json > bench.json    # 124-check regression bench
python docs/build_demo.py bench.json          # → demo.html
```

The bench regenerates the public demo page at
[/demo/](https://mine-fnl.github.io/qstocks-filing-tool/demo.html) on every
release tag.
