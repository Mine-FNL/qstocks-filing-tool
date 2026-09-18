# Whitepaper

`Lossless Filing JSON: A Deterministic-First Architecture for Financial
PDF Extraction with Built-In Consistency Gates` — the formal write-up
of the architecture, the bench, and the threat model that backs
`qscreen-filing-tool`.

## Files

| File                  | What it is                                                          |
|-----------------------|---------------------------------------------------------------------|
| `whitepaper.md`       | The source — Markdown, ~6,000 words, 9 sections + 3 appendices.    |
| `whitepaper.html`     | Pandoc-rendered HTML with TOC + embedded CSS. Self-contained.       |
| `whitepaper.pdf`      | The publishable artifact — Chrome-headless rendered, ~10 pages.     |
| `style.css`           | The typesetting stylesheet (Charter / Helvetica Neue + JetBrains).  |
| `build.sh`            | Reproducible PDF build (pandoc + Chrome headless).                  |
| `figures/cover-page.png` | A preview render of the title page.                              |

## How to rebuild the PDF

```bash
bash whitepaper/build.sh
```

Requires `pandoc` and Google Chrome on macOS. For Linux CI, swap
`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` for
`chromium` or `google-chrome-stable`.

## Sections

1. **Introduction** — three audiences (data eng, compliance, OSS maintainers).
2. **Problem** — three failure modes of existing extractors.
3. **Approach** — the three architectural bets (deterministic-first,
   math-identity gate, SHA-256 cross-filing fingerprints).
4. **Implementation** — profile pluggability, supply-chain hardening.
5. **Bench Results** — 124 cross-filing checks, 100/124 floor.
6. **Threat Model** — six threat categories, mitigations.
7. **Limitations** — honest ceilings documented.
8. **Roadmap** — Now → v1.7.0 → v2.0 → future.
9. **Conclusion** — invitation to engage.

Plus: References, Reproducing-the-bench appendix, Verifying-a-release
appendix, Citing-this-paper appendix.

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

## Distribution

- The PDF is shipped with the GitHub release.
- The HTML is hosted on the docs site at
  <https://mine-fnl.github.io/qstocks-filing-tool/whitepaper/> (TBD —
  see the `docs.yml` deploy step).
- The Markdown is the canonical source; PRs welcome.
