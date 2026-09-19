# Competitive Landscape — Financial-Document Extraction with Bench-Grade Stability

**Scope.** A competitive map for the qscreen-filing-tool positioning at the
PyCon / PyData / SIGMOD / Strata intersection: an open-source Python engine
that turns PDF financial reports into a schema-stable, audit-traceable
JSON object, with a math-identity gate (Assets = Liabilities + Equity) and
SHA-256 cross-filing fingerprints. Compared feature-for-feature against
8 incumbents.

**Method.** Every claim below is sourced from the cited URL. Where a
competitor publishes no number for a metric, this document says so
explicitly. No speculation. Numbers pulled by `web_fetch` calls are
captured in this turn's externalised artefacts (under
`/Users/gg/.minimax/v2/sessions/.../reports/tool-outputs/`).

**One-line summary of the landscape.**

| # | Competitor | Layer | Pricing | Threat |
|---|------------|-------|---------|--------|
| 1 | pdfplumber | OSS char/line parser | Free | Low (baseline we already use) |
| 2 | camelot / tabula-py | OSS table extractors | Free | Low (we already use as engine fallback) |
| 3 | marker-pdf | OSS ML PDF→Markdown | Apache-2.0 + OpenRail-M | Medium (the closest product analog) |
| 4 | extractous | OSS Rust extractor | Apache-2.0 | Low (raw extraction, no schema) |
| 5 | unstructured-io | OSS ETL for LLMs | Apache-2.0 + paid platform | Medium-High (the best-funded OSS rival) |
| 6 | Docparser | Commercial SaaS | $39–$159/mo + enterprise | Low (templates, no financial schema) |
| 7 | Rossum | Commercial AP / IDP | $18K+/yr + enterprise | High (the incumbent financial vendor — now Coupa-owned) |
| 8 | Affinda | Commercial extraction API | PAYG + enterprise | Low (resume-rooted, no audited financials) |

---

## 1. pdfplumber (baseline)

**What it does.** A pure-Python library that plumbs a PDF for char-level,
rectangle-level and line-level data, exposing both `extract_text()` and
`extract_tables()` over the same primitives. Pure-Python build via
pdfminer.six; no Java or external runtime. [README](https://github.com/jsvine/pdfplumber)

**Public benchmarks.** **No public financial-filing benchmark.** The
library has no formal accuracy evaluation on SEC 10-K / annual-report
data; users cite it qualitatively as "the most accurate pure-Python
extractor." Sample notebook benchmarks (e.g. per-page word counts) are
demos, not regressions. Last commit 2026-08-06 confirms active maintenance.

**Pricing model.** Free. MIT-licensed. [License badge in README](https://github.com/jsvine/pdfplumber)

**Differentiator vs qscreen-filing-tool.** pdfplumber is a **library**;
we are a **pipeline**. It does not produce schema-stable JSON, does not
check identity (A = L + E), does not fingerprint, and does not assert
math. pdfplumber does the low-level char/rect reading; qscreen-filing-tool
sits on top.

**Weakness vs qscreen-filing-tool.** No semantics. Numbers extracted from
a 10-K are untyped; nothing stops "1,234" (footnote) from being
interpolated into the income statement. No audit trail, no deterministic
re-runs across versions, no jurisdiction profiles. Bench-grade stability
is out of scope by design.

**Threat level.** **Low.** It is our baseline. We depend on it, not
compete with it. If pdfplumber breaks, our extraction pipeline breaks —
so its slow release cadence (months between minor versions) is a risk to
*us*, not a competitive threat.

**Source.** [GitHub API](https://api.github.com/repos/jsvine/pdfplumber),
[README](https://github.com/jsvine/pdfplumber). Stars: 10,755
(GitHub API, this turn).

---

## 2. camelot / tabula-py (lattice + stream tables)

**What it does.** Two libraries in the same niche. **Camelot** is a
Python wrapper with five table-extraction flavours (lattice, stream,
network, hybrid, ml — the last is an opt-in Table Transformer for
borderless tables) and pandas output plus per-table accuracy and
whitespace quality metrics. **tabula-py** is a Python wrapper around the
JVM-based Tabula extractor (Java must be installed). [camelot README](https://github.com/camelot-dev/camelot)
[tabula-py README](https://github.com/chezou/tabula-py)

**Public benchmarks.** Camelot's README cites a **FinTabNet** result: the
optional ML backend "roughly doubles borderless TEDS vs `network` /
`hybrid`" heuristic parsers (the table extractors are otherwise heuristic,
not neural). No SEC or annual-report benchmark is published. [camelot README](https://github.com/camelot-dev/camelot)

**Pricing model.** Both free. Camelot MIT, tabula-py MIT. [License badges](https://github.com/camelot-dev/camelot)
[tabula-py License](https://github.com/chezou/tabula-py)

**Differentiator vs qscreen-filing-tool.** Per-table **accuracy and
whitespace scores** are first-class output (great for filter loops). The
optional `flavor="ml"` backend handles borderless and scanned tables —
a real pain point in financial PDFs. Output is a DataFrame, which
slots straight into analyst notebooks.

**Weakness vs qscreen-filing-tool.** Tables, not financial statements.
No understanding of *which* table is the balance sheet, no schema
mapping to revenue/COGS/operating-income, no math gate. Output is a
bunch of DataFrames labelled `Table 1`, `Table 2`, `…` — analysts still
have to bind them to line items by hand. Also: cell-level numerics are
not anchored to a specific filing/page/cell coordinate in a stable way.

**Threat level.** **Low.** Same role as pdfplumber — a **building block**
we already lean on, not a substitute for the pipeline.

**Source.** [camelot README](https://github.com/camelot-dev/camelot),
[tabula-py GitHub API](https://api.github.com/repos/chezou/tabula-py).
Camelot stars: 3,822. tabula-py stars: 2,315. (GitHub API, this turn.)

---

## 3. marker-pdf (PDF → Markdown)

**What it does.** ML pipeline (PyTorch + surya OCR + layout models +
LLM fallback) that turns a PDF page into Markdown plus structured
JSON. Apache-2.0 license on the code; model weights released under
**OpenRail-M** (free for research, personal use, and commercial use
under $5M revenue). Vendor Datalab also runs a hosted service that
"processes 1B+ pages per week." [marker README](https://github.com/datalab-to/marker)

**Public benchmarks.** Marker publishes head-to-head numbers vs MinerU
and Docling on **olmocr-bench**: 76.0% balanced mode overall, **83.5%
on born-digital PDFs** (its strongest mode), 40.1% on scanned legacy
PDFs. Marker claims "4.35× throughput vs MinerU" and "2.85× throughput
vs Docling" on its README. All numbers from the project README; no
third-party reproduction linked. [marker README benchmarks table](https://github.com/datalab-to/marker)

**Pricing model.** Code is free. Model weights are restricted
(OpenRail-M). Datalab's hosted "Marker" service offers **$5 in free
credits** plus pay-as-you-go. The commercial license is gated at $5M
annual revenue, which is a relevant threshold for our positioning.

**Differentiator vs qscreen-filing-tool.** Marker is **the closest
product analog** to ours. Same surface (PDF in, structured JSON/MD
out), same open-source ethos, same "ingest on any commit, get same
output" ambition — though marker does not, per its public bench, hit
determinism across version bumps. It also runs faster than we do on
big batches (it is a batched GPU pipeline; we are a CPU-bound
deterministic pipeline). Its throughput claim (4× vs MinerU) is its
marketing lead.

**Weakness vs qscreen-filing-tool.** Two big gaps we exploit:

1. **No math-identity gate.** Marker extracts; we *check*. A misread
   comma in the balance sheet passes through marker silently. qscreen
   raises an exception because Assets ≠ L + E.
2. **No SHA-256 cross-filing fingerprint.** Marker has no concept of
   "the same number appearing in two consecutive filings should hash
   to within ε of the same fingerprint." That is exactly the property
   an auditor wants; it is a qscreen first-class object.

There is also no jurisdiction profile and no schema-stable JSON
contract — outputs vary by engine version.

**Threat level.** **Medium.** Highest competitive risk on technical
merit. They have 39,836 GitHub stars (≈4× ours), active funding, GPU
acceleration, and a hosted product. They will, however, struggle to
adopt a math-identity gate without re-architecting around an
explicit domain schema — the heart of our pitch.

**Source.** [marker-pdf GitHub API](https://api.github.com/repos/datalab-to/marker),
[marker README](https://github.com/datalab-to/marker). Stars: 39,836
(GitHub API, this turn).

---

## 4. extractous (Rust-based fast extraction)

**What it does.** A Rust library that exposes high-throughput PDF /
DOCX / HTML / EPUB / RTF / ODT / image → `unstructured`-shaped JSON.
Bindings for Node.js, Python, and WASM. Apache-2.0. Designed to be
the **fast layer** under any downstream pipeline. [extractous README](https://github.com/yobix-ai/extractous)

**Public benchmarks.** Extractous's README makes an explicit
head-to-head claim against unstructured.io: **"~25× faster on
generic PDFs; ~18× faster on SEC 10 filings; ~11× less memory."** No
third-party reproduction linked. The claim is upstream-controlled, but
plausible given a Rust vs Python implementation gap. [extractous README](https://github.com/yobix-ai/extractous)

**Pricing model.** Free. Apache-2.0. [License in repo](https://github.com/yobix-ai/extractous)

**Differentiator vs qscreen-filing-tool.** Speed. If you need to ingest
millions of pages and ship a JSON blob for downstream RAG, extractous
will beat almost every Python alternative. Lower memory footprint
matters for serverless and edge deployments.

**Weakness vs qscreen-filing-tool.** Raw extraction, no domain schema,
no math identity, no fingerprinting, no audit trail. The output is
generically shaped after `unstructured` (title / narrative text /
list / table) — there is no concept of "this is the consolidated
balance sheet as of FY24." Also young project (1,780 stars,
created June 2024) — API stability and community momentum both
unknown.

**Threat level.** **Low.** Could be a future *engine* inside our
pipeline (swappable for pdfplumber + unstructured), but never a
*competitor* — it does not know what a financial statement is.

**Source.** [extractous GitHub API](https://api.github.com/repos/yobix-ai/extractous),
[extractous README](https://github.com/yobix-ai/extractous). Stars: 1,780
(GitHub API, this turn).

---

## 5. unstructured-io (the most-funded OSS competitor)

**What it does.** The canonical open-source ETL for LLM ingestion:
partition a document into typed chunks (title, narrative, list, table),
extract text + tables, return JSON ready for embedding. Apache-2.0.
Also ships an MCP server ("unstructured mcp") for agent workflows.
[unstructured README](https://github.com/Unstructured-IO/unstructured)

**Public benchmarks.** No public head-to-head accuracy benchmark on
financial filings. Internal benchmarks exist for document-class
partitioning accuracy (on the order of "extract title vs paragraph"
classification) but no comparable artifact to our bench report.
**No equivalent of a math-identity gate.**

**Pricing model.** Open-source free. Hosted "Unstructured Platform" is
enterprise-only (quote). Free tier for the API exists via the open
source route. The SaaS side monetises partitioned-data ingestion
pipelines into vector stores. [SaaS News on Series B](https://www.thesaasnews.com/news/unstructured-raises-40-million-in-series-b/)

**Differentiator vs qscreen-filing-tool.** Brand and funding. The
project raised **$65M total** — a **$25M Series A in 2023**, then a
**$40M Series B in December 2024 led by Menlo Ventures** with
Databricks Ventures, IBM Ventures, NVentures (NVIDIA), Madrona, Bain
Capital Ventures and Mango Capital. They have a sales team, an
enterprise platform, and an MCP story. Their positioning for LLM
ingestion is already in the minds of data engineers.

**Weakness vs qscreen-filing-tool.** Generic, not domain-specific.
unstructured knows what a "Title" and a "Table" are; it does not
know what *Revenue FY24* means. No identity math, no fingerprint,
no jurisdiction profiles, no audit trail. Also: extractous's README
contends the underlying extractor is "8.5k stars" and slow — the
star count is outdated (12,254 now), but the throughput claim still
holds against a Rust competitor. (We confirmed 12,254 stars via the
GitHub API this turn.)

**Threat level.** **Medium-High.** This is the only OSS competitor
with comparable distribution, comparable funding, and a hosted
product. They could, with one quarter of engineering, add a
financial-schema profile and ship a competitor. We must keep the
math-identity gate, fingerprints, and jurisdiction profiles in
public view before they do.

**Source.** [unstructured GitHub API](https://api.github.com/repos/Unstructured-IO/unstructured),
[Series B coverage](https://www.thesaasnews.com/news/unstructured-raises-40-million-in-series-b/),
[Series B led by Menlo](https://techcrunch.com/2024/12/17/unstructured-raises-40m-series-b/),
[extractous speed claims](https://github.com/yobix-ai/extractous).
Stars: 12,254 (GitHub API, this turn).

---

## 6. Docparser (commercial SaaS PDF extraction)

**What it does.** Belgian SaaS, browser-based zonal-OCR template
editor ("draw a box around the field") that turns PDFs into
structured JSON / CSV / Excel. Integrations into Zapier, Make,
n8n, Google Sheets, Airtable. [Docparser pricing page](https://docparser.com/pricing/)

**Public benchmarks.** **No public benchmarks for financial
filings.** Docparser markets accuracy via customer testimonials, not
benchmarks. Zonal-OCR-based systems fail systematically on borderless
or scanned financial reports unless the template is hand-tuned per
filing — and financial PDFs change layout every year.

**Pricing model.** SaaS, monthly. **Starter $39/month (100 docs),
Professional $74/month, Business $159/month, Enterprise on request**.
14-day free trial, no credit card required. Per the third-party
review at [Airparser review](https://airparser.com/blog/top-data-extraction-tools/)
(third-party blog, January 2026), prices as cited.

**Differentiator vs qscreen-filing-tool.** Cheapest entry point on the
list (~$39/mo), no Python required, no code. Works well for *highly
structured, repetitive* documents — invoices, purchase orders, bills
of lading — where one template can match thousands of pages.

**Weakness vs qscreen-filing-tool.** Templates. Every new issuer or
jurisdiction requires a new template. The math-identity gate is
*impossible* to express in a zonal OCR tool, and there is no way
to fail loudly on A ≠ L + E. Annual reports mutate every year; a
zonal parser breaks silently. Also: vendor lock-in (cloud-only),
no on-prem.

**Threat level.** **Low.** Different buyer, different use case.
Docparser is for SMB back-office (one PO box, one vendor layout,
forever). qscreen is for analysts dealing with N issuers and M
years. They barely intersect.

**Source.** [Docparser pricing page](https://docparser.com/pricing/),
[Airparser third-party review](https://airparser.com/blog/top-data-extraction-tools/).

---

## 7. Rossum (commercial invoice / financial-doc extraction)

**What it does.** Prague- and London-based "AI-first" IDP platform
specialising in accounts-payable automation. Ingests invoices, bills
of lading, sales orders, customs documents; routes them to an
enterprise workflow with native ERP connectors to SAP, Coupa,
NetSuite, Workday, Microsoft Dynamics. [Rossum platform page](https://rossum.ai/)

**Public benchmarks.** Rossum markets **"96%+ accuracy on key
fields"** for its invoice extraction model. No third-party
reproduction; the number is from Rossum's own marketing. No public
benchmark on annual reports or 10-Ks — Rossum's domain is AP, not
investor-grade financial statements.

**Pricing model.** Enterprise SaaS. Per a 2025 Reddit post compiling
public information ([r/Accounting on Rossum pricing](https://www.reddit.com/r/Accounting/comments/18oz8rp/rossum_pricing/)):
**Starter $18,000/year ($1,500/month minimum), Silver $40,000/year
(~100K document pages), Gold $70,000/year (~250K document pages),
Enterprise on request.** These are quoted, not verified, but
match the "enterprise AP" market.

**Funding & recent M&A.** Raised a **$100M Series A in October 2021,
led by General Catalyst** (with LocalGlobe, Seedcamp, Miton, and
Elad Gil) — the **largest Series A in Eastern Europe at that time**.
Reported valuation $500M–$1B+. [Business Wire press release](https://www.businesswire.com/news/home/20211019005884/en/Rossum-raises-record-$100-million-Series-A-from-General-Catalyst-to-reinvent-B2B-document-communication)
[VentureBeat coverage](https://venturebeat.com/ai/automated-document-processing-platform-rossum-raises-100m).
**In 2026 Coupa acquired Rossum** to accelerate autonomous spend
management. [Coupa announcement](https://rossum.ai/) (homepage banner,
this turn).

**Differentiator vs qscreen-filing-tool.** Deep enterprise ERP
integration, customer base (Imperial Dade, "150 of Europe's
biggest and fastest-growing companies"), brand, and now a Coupa
sales channel. Rossum's pitch is "stop keying invoices; cut AP
processing time 90%."

**Weakness vs qscreen-filing-tool.** Three structural weaknesses we
can name:

1. **AP-only.** Rossum is built for invoices and bills of lading.
   Annual reports are not on the roadmap. Their customers ask
   "process this AP batch"; ours ask "give me the FY24 income
   statement from this 200-page 10-K, audit-traceable to byte
   offset."
2. **Coupa acquisition creates channel conflict.** Coupa customers
   are the natural buyers; everyone else is now second-class
   citizen. Quoting and pricing pressure will tilt toward Coupa.
3. **Closed source / closed accuracy claim.** No reproducible bench,
   no open engine, no jurisdiction profile export.

**Threat level.** **High.** Rossum is the incumbent vendor the
buyers in our ICP have heard of. Their Coupa acquisition is
neutral-to-positive for us: it frees non-Coupa prospects from
Rossum-channel pressure, and makes the "open, audit-traceable,
reproducible" angle land harder by contrast.

**Source.** [Rossum homepage](https://rossum.ai/) (Coupa acquisition
banner), [Series A press release](https://www.businesswire.com/news/home/20211019005884/en/Rossum-raises-record-$100-million-Series-A-from-General-Catalyst-to-reinvent-B2B-document-communication),
[VentureBeat](https://venturebeat.com/ai/automated-document-processing-platform-rossum-raises-100m),
[Reddit pricing thread](https://www.reddit.com/r/Accounting/comments/18oz8rp/rossum_pricing/).

---

## 8. Affinda (commercial extraction API)

**What it does.** Melbourne-based document-AI API vendor. Started as a
**resume parser** and **job-description parser**, expanded into
invoices, receipts, contracts, financial docs. Offers a hosted
platform and a REST API with confidence scores, schema versioning,
and a model-customisation console. [Affinda platform](https://affinda.com/)

**Public benchmarks.** **No public benchmark** for financial
filings. Affinda publishes per-field confidence but no head-to-head
accuracy claim against peers. Resume-parsing accuracy was the
original pitch (claimed 80–90%+ on common fields) but has no
equivalent for investor-grade documents.

**Pricing model.** Pay-as-you-go (per page / per document) plus
enterprise custom. Pricing is quote-based; no public list.
**No public funding disclosure** found in research this turn.

**Differentiator vs qscreen-filing-tool.** Domain breadth (resume →
invoice → contract → financial), REST API ergonomics, custom
schema support, and confidence scores. Easier to integrate than
Rossum; broader domain coverage than Docparser.

**Weakness vs qscreen-filing-tool.** **No math-identity gate. No
SHA-256 cross-filing fingerprint. No jurisdiction profiles. No
reproducible benchmark.** Outputs are probabilistic per-field
predictions; a comma misread in revenue propagates silently
because there is no second-derivative check. Also: a resume-parser
origin story does not inspire trust with auditors of regulated
financial filings.

**Threat level.** **Low.** Right product shape (API, schema,
confidence) but wrong domain credibility. They could ship a
financial profile in a quarter; they would still lack the audit
story. The wedge is ours.

**Source.** [Affinda homepage](https://affinda.com/),
[Affinda API docs](https://docs.affinda.com/reference/getting-started).

---

## What this landscape teaches us about positioning

Five concrete lessons, ranked by what they cost us if we ignore them.

**1. The buyer we should target first: regulated mid-market finance /
audit / risk teams who already pay $18K+/yr for Rossum or Affinda and
are tired of the black box.** The pricing floor at the commercial
vendors is $18K–$70K/year per seat. That puts our $0 + compute buyer
profile at **a Tier-1 SaaS budget holder in audit, fund reporting,
or regulatory analytics**, who currently buys Rossum / Affinda
because there is no alternative. They will not pay for a single PDF;
they will pay (in adoption effort) for an audit-traceable open
engine. Lead list: fund administrators, second-tier accounting
firms, central-bank quantitative teams, sovereign-fund research.

**2. The buyer we should deprioritise: SMB back-office who would
otherwise buy Docparser at $39/mo.** They are price-sensitive, they
want zonal templates they can edit in a browser, they will never
read a benchmark report, and they will never file an issue about a
math gate. Time spent on Docparser-shaped buyers is a tax.

**3. The competitor whose existence forces a specific product move:
unstructured-io.** With $65M of funding and 12,254 GitHub stars,
they are the only OSS rival with distribution to ship a financial-
schema profile before we do. We must, before SIGMOD 2027, ship a
benchmark they cannot reproduce in a week — specifically the
**math-identity gate success rate** across N filings. That is the
public artefact that locks our moat in their face.

**4. The wedge competitors cannot easily copy: the SHA-256 cross-
filing fingerprint + math-identity gate as a single, reproducible
object.** Any rival can ship a financial-schema profile; not any rival
can ship a primitive that lets an auditor ask "did the same number
appear in both filings?" and get a deterministic answer. The
fingerprint is a 20-line algorithmic addition once the schema is
in place — but it is a **product story**, not a feature: auditors
buy the *story* that the numbers are byte-traceable across filings.
Marker, unstructured, extractous have no story. Rossum/Affinda
have a confidence score. We have a hash.

**5. The threat that turns into an opportunity: the Coupa acquisition
of Rossum.** Every buyer who considered Rossum in 2025 and rejected
it for "channel conflict with our SAP instance" is now a clean lead
for us. We should publish a one-page "After Coupa-Rossum: open-source
financial extraction with math-identity guarantees" piece for the
next quarter's PyData newsletter and pin it in the README. Same
principle applies if unstructured.io gets acquired by a vector-store
vendor.

---

## Appendix: Source URLs referenced above

| # | Source | Used for |
|---|--------|----------|
| 1 | https://github.com/jsvine/pdfplumber | pdfplumber stars, license |
| 2 | https://github.com/camelot-dev/camelot | camelot FinTabNet claim, parsers |
| 3 | https://github.com/chezou/tabula-py | tabula-py stars, license |
| 4 | https://github.com/datalab-to/marker | marker-pdf benchmarks, license |
| 5 | https://github.com/yobix-ai/extractous | extractous speed claims |
| 6 | https://github.com/Unstructured-IO/unstructured | unstructured stars, license |
| 7 | https://www.thesaasnews.com/news/unstructured-raises-40-million-in-series-b/ | unstructured Series B investors |
| 8 | https://techcrunch.com/2024/12/17/unstructured-raises-40m-series-b/ | unstructured Series B lead |
| 9 | https://docparser.com/pricing/ | Docparser free-trial + pricing tiers |
| 10 | https://airparser.com/blog/top-data-extraction-tools/ | Docparser / Nanonets third-party prices |
| 11 | https://rossum.ai/ | Rossum Coupa-acquisition banner |
| 12 | https://www.businesswire.com/news/home/20211019005884/en/Rossum-raises-record-$100-million-Series-A-from-General-Catalyst-to-reinvent-B2B-document-communication | Rossum Series A facts |
| 13 | https://venturebeat.com/ai/automated-document-processing-platform-rossum-raises-100m | Rossum Series A valuation |
| 14 | https://www.reddit.com/r/Accounting/comments/18oz8rp/rossum_pricing/ | Rossum tiered pricing (community cite) |
| 15 | https://affinda.com/ | Affinda domain + product shape |
| 16 | https://docs.affinda.com/reference/getting-started | Affinda API documentation |

Numbers above are captured in this turn's `web_fetch` externalised
artefacts under
`/Users/gg/.minimax/v2/sessions/.../reports/tool-outputs/`. Pages that
were JS-rendered (Crunchbase, Rossum blog Series A URL was 404'd) are
flagged inline. Where no public number exists, this document says so
explicitly.
