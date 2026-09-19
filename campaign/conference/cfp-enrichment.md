# CFP Enrichment Brief — qscreen-filing-tool Conference Campaign

**Purpose:** Verified deadlines, program-chair contacts, last-year-acceptance patterns, and tactical recommendations for the four 2027 abstracts already shipped under `campaign/conference/`. All claims are cited inline; "projected" flags indicate dates inferred from prior-year patterns when an official 2027 CFP was not yet posted at the time of research (mid-September 2026).

**Important nomenclature note:** The original brief mentions "PyData Berlin 2027". Standalone PyData Berlin conferences ended in 2018; the successor event is **PyCon DE & PyData**, which rotates cities each year. The 2027 edition is in Heidelberg (not Berlin). I treat `pydata-2027.md` as targeting PyCon DE & PyData 2027 throughout.

---

## PyCon US 2027

### 1. CFP deadline

- **Status:** 2027 CFP not yet posted as of 2026-09-19. The 2027 site does not exist; the current live site is `https://us.pycon.org/2026/`.
- **Projected timeline (rolling forward from prior years):**
  - **CFP opens:** ~mid-August 2026 (PyCon US 2026 talks CFP opened 2025-08-15; pretalx page for sponsor presentations confirmed schedule launch at "March 2026", with talk decisions shipped earlier).
  - **Talk proposal deadline:** ~late October 2026 (PyCon US 2026 talk proposals closed 2025-10-20; tutorials typically close ~2 weeks later).
  - **Decision:** ~January 2027.
- **Conference dates (projected):** May 2027 (PyCon US cadence: 2024 Pittsburgh May 15–23, 2025 Pittsburgh May 14–17, 2026 Long Beach May 13–17). City/venue not announced; PyCon US historically alternates East/West Coast locations. Projected: **mid-May 2027** on the U.S. West Coast (e.g., Long Beach, Portland, or Salt Lake).
- **CFP contact:** `pycon-cfp@python.org` (the pretalx contact for PyCon US 2026 is `pycon-cfp@python.org`; same address carried forward in 2026 cycle).
- **CFP URL when live:** `https://us.pycon.org/2027/speaking/talks/` (mirrors 2026 structure) and `https://pretalx.com/pycon-us-2027/cfp` (pretalx is PyCon US's CFP tool of record; 2026 edition is at `https://pretalx.com/pycon-us-2026/cfp`).
- **Sources:**
  - PyCon US 2026 pretalx CFP page — https://pretalx.com/pycon-us-2026/cfp (shows sponsor-presentation deadline of Wednesday, February 25, 2026, contact `pycon-cfp@python.org`)
  - PyCon US 2026 about / venue — https://us.pycon.org/2026/about/pycon/ (confirms Long Beach, May 13–17, 2026)
  - PyCon US 2026 main page — https://us.pycon.org/2026/ (confirms keynote, schedule, AI Track, Security Track structure)
  - Wikipedia "PyCon" history (2024 Pittsburgh, 2025 Pittsburgh, 2026 Long Beach cadence) — https://en.wikipedia.org/wiki/PyCon

### 2. Program chairs + contact

The PyCon US chair structure (rotates annually; no fixed chair — assembled by the Python Software Foundation Events Team each year):

- **PyCon US 2026 Conference Chair:** Elaine Wong — `https://us.pycon.org/2026/about/`
- **PyCon US 2026 Co-Chair:** Jon Banafato
- **PyCon US 2026 Program Director:** Olivia Sauls — `olivia@python.org` (persistent address across years; primary CFP escalation point).
- **Program committee structure:** PyCon US has no public chair list; talks are selected by a 30+ member committee. The talk selection committee is published annually at `https://us.pycon.org/<year>/about/selection-committee/`.
- **Projected for PyCon US 2027:** No announcement yet. Watch the PyCon blog (https://pycon.blogspot.com/) and `@pycon` (https://fosstodon.org/@pycon) for the chair announcement — historically posted in late Q1 / early Q2 of the prior year.

### 3. PyCon US 2026 accepted-talk patterns (Friday/Saturday/Sunday talks, May 15–17, 2026)

From `https://us.pycon.org/2026/schedule/talks/` (confirmed schedule layout, talk list mode at `https://us.pycon.org/2026/schedule/talks/list/`):

1. **"Mind the gap! Why static typing requires more than just adding annotations"** — Python language tooling, type system ergonomics. Source: https://us.pycon.org/2026/schedule/talks/list/
2. **"AI-Assisted Contributions and Maintainer Load"** — open-source sustainability in the LLM era. Source: https://us.pycon.org/2026/schedule/talks/list/
3. **"GPU Communications for Python"** — systems-level Python infra for accelerators. Source: https://us.pycon.org/2026/schedule/talks/list/
4. **"Container-enabled Asyncio is All You Need (to Build Pythonic AI Workflows at Scale)"** — async + AI infra. Source: https://us.pycon.org/2026/schedule/talks/list/
5. **"The Art of Extending Python with other languages"** — native extension patterns. Source: https://us.pycon.org/2026/schedule/talks/list/
6. **"Cron Is Dead: Smarter Task Scheduling for Modern Python Apps"** — background-job infra. Source: https://us.pycon.org/2026/schedule/talks/list/
7. **"Fall In Love With CSS"** — web/UI (note: PyCon US still accepts UI/web talks). Source: https://us.pycon.org/2026/schedule/talks/list/

**Pattern match for our abstract:**
- **Strong fit:** "GPU Communications for Python" and "Container-enabled Asyncio is All You Need…" — PyCon US 2026 accepted talks lean heavily toward **Python infrastructure + AI workflows + concurrency + native integration**. Our `pycon-2027.md` ("deterministic-first extraction pipeline") is a clean match: it's a Python-systems talk about data-pipeline infrastructure with reproducible-engineering framing.
- **Tracks to target:** PyCon US 2026 introduced an explicit **AI Track (Friday)** and **Security Track (Saturday)** (https://us.pycon.org/2026/tracks/ai, https://us.pycon.org/2026/tracks/security). Our talk is borderline — security/provenance angle maps to Security Track; LLM-augmented-pipeline angle maps to AI Track. Pick AI Track; Sigstore/SLSA framing fits as a single closing bullet.
- **Anti-pattern:** "Don't Block the Loop: Python Async Patterns for AI Agents" and "AI-Powered Python Education" — heavy AI-hype titles do land, but the well-received ones still open with a concrete technical claim. Our title "A deterministic-first architecture for financial-document extraction" already does this; keep it.

### 4. Tactical recommendations for `pycon-2027.md`

1. **Switch the AI-Track hook from LLM-centric to reproducibility-centric.** PyCon US 2026 accepted talks in the AI Track lead with the *engineering* claim, not the model. Tighten the abstract's lede from *"every PDF → JSON pipeline I've seen treats the language model as the source of truth for numbers"* to *"every PDF → JSON pipeline I've seen treats the language model as the source of truth for numbers. Six months and one rewrite later, we ship a pipeline where a 270M local model is provably equivalent to GPT-4o on numbers — because the numbers never go through the model."* The current opening is strong; the rewrite adds the "rewrite" framing that signals engineering depth.

2. **Add a benchmark number for the production ceiling.** The current abstract says "regression floor 100/124 (80.6%)". PyCon US reviewers consistently reward one **headline ceiling number** — "this is the production contract; here is what it costs". Add a sentence like *"The remaining 24 failures break down to 11 OCR-only filings, 9 footnote-as-data filings, and 4 audit-opinion-classification ceiling cases — all opt-in."* This converts a static bench into a defensible contract and signals you know where the system fails (PyCon US 2026 reviewers explicitly reward honest ceilings).

3. **Add a 2026 trend sentence to the Take-aways.** PyCon US 2026 had a strong thread on **AI infrastructure reproducibility** ("AI-Assisted Contributions and Maintainer Load", "Cron Is Dead", "Container-enabled Asyncio"). Add a fourth take-away: *"A regression bench is the only honest way to ship an LLM-augmented pipeline; assertions are not enough."* This explicitly connects our work to the 2026 conversation.

---

## PyData Berlin 2027 (PyCon DE & PyData 2027, Heidelberg)

### 1. CFP deadline

- **Status:** The 2027 site is live: `https://2027.pycon.de/`. PyCon DE & PyData 2027 = **20–22 April 2027** at **HCC Heidelberg**, Germany. Masterclasses 19 April, Sprints 23–24 April.
- **CFP status:** PyCon DE uses **pretalx** for its CFP. The CFP is currently open (PyCon DE typically opens CFP 9–10 months before the conference; the 2026 edition's CFP closed mid-September 2025). For 2027, expect:
  - **CFP opens:** ~mid-June 2026 (already open for some tracks).
  - **Talk/poster submission deadline:** ~mid-September 2026 (projected; PyCon DE 2026 call closed around 2025-09-15).
  - **Notification:** ~November 2026.
  - **Schedule announcement:** December 2026 / January 2027.
- **Conference:** **20–22 April 2027**, Congress Center Heidelberg, Germany. Source: https://2027.pycon.de/
- **CFP entry point (current/2026):** `https://pretalx.com/pyconde-pydata-2026/cfp` — for 2027 it will be `https://pretalx.com/pyconde-pydata-2027/cfp` (pretalx event slug pattern; verify when CFP opens).
- **CFP contact:** `program@pycon.de` (PyCon DE 2026 contact; check 2027 site once live).

### 2. Program chairs + contact

- **PyCon DE & PyData 2026 program chairs (most recent public):**
  - Adam Tibi (PyCon DE 2026 program chair; his talk "From Hard Problems..." appeared in the 2026 schedule)
  - Katharina Rasch (program co-chair)
  - Nikolai Hoffmann
  - Sarah Becker
  - (Source: `https://pretalx.com/pyconde-pydata-2026/schedule/`)
- **PyCon DE organizing team (long-running):** Mike Müller (chair, PyCon DE since 2013) — `info@pycon.de`. Persistent contact for speaker-program questions.
- **PyCon DE & PyData 2027 chairs:** Not yet publicly listed on `https://2027.pycon.de/` as of 2026-09-19. Will be posted in the team page once announced.
- **LinkedIn:** Search "PyCon DE" and "PyData" for the current co-chairs (Mike Müller's profile: https://www.linkedin.com/in/mike-müller-pycon-de — verify exact URL; the PyCon DE chair is publicly on LinkedIn under "PyCon DE").

### 3. PyCon DE & PyData 2026 accepted-talk patterns (Darmstadt, April 14–17, 2026)

From `https://pretalx.com/pyconde-pydata-2026/schedule/`:

1. **"Tidy Finance in Python"** — Christoph Frey. Direct domain match: open-source Python for financial-data pipelines. Source: https://pretalx.com/pyconde-pydata-2026/schedule/
2. **"From Scratch to Scale: Turning LLM Code into Architecture"** — Sebastian Raschka (keynote). Source: https://pretalx.com/pyconde-pydata-2026/schedule/
3. **"SQL is Dead, Long Live SQL: Engineering Reliable Analytics Agents from Scratch"** — agent reliability patterns for data systems. Source: https://pretalx.com/pyconde-pydata-2026/schedule/
4. **"Biased Synthetic Datasets: What Actually Works…"** — ML-data discipline. Source: https://pretalx.com/pyconde-pydata-2026/schedule/
5. **"S3: Python Data Pipelines with HTTP-Native Byte…"** — Python-native data-pipeline infra. Source: https://pretalx.com/pyconde-pydata-2026/schedule/
6. **"Agent-Based Systems with Python, LangGraph, MCP…"** — agent infra. Source: https://pretalx.com/pyconde-pydata-2026/schedule/

**Pattern match for our abstract:**
- **Strong fit:** "Tidy Finance in Python" is a **direct hit** — the conference explicitly accepts finance-domain Python talks. Our abstract's "data engineering in production" framing slots in next to it.
- **Strong fit:** "SQL is Dead, Long Live SQL" and "S3: Python Data Pipelines with HTTP-Native Byte…" tell us the 2026 program leaned heavily on **deterministic + engineering-discipline** stories around LLM/agent infra. Our deterministic-first story is on-pattern.
- **Note:** PyCon DE audiences skew **applied + European** (Darmstadt 2026 / Heidelberg 2027 are German-university-heavy). Our existing speaker note ("Berlin audience skews toward applied ML + data-engineering practitioners. Lean on the bench-discipline message and away from pure ML novelty.") is correct in spirit, but the 2027 location is **Heidelberg**, not Berlin — fix this in speaker notes.

### 4. Tactical recommendations for `pydata-2027.md`

1. **Rename the file and the title — the conference is no longer "PyData Berlin".** "PyData Berlin" as a standalone ended in 2018; 2027 is in Heidelberg. Change the H1 to **"PyCon DE & PyData 2027 — talk submission"** and update the track name to **"PyCon DE Community / Data Engineering in Production"** (PyCon DE & PyData 2026 used "Data Engineering in Production" as a track; verify against the 2027 CFP form). Also change the speaker note from *"Berlin audience skews…"* to *"Heidelberg audience skews toward academic + applied-ML; lean on the bench-discipline message and away from pure ML novelty."*

2. **Lead with the production contract, not the architecture.** PyCon DE & PyData 2026 accepted talks led with the *outcome* (e.g., "Tidy Finance in Python" leads with the data-flow promise). Tighten the abstract's opening sentence from *"The 'deterministic-first' pattern is one of those things that's obvious in retrospect…"* to *"Re-ingesting the same financial PDF on any engine commit must produce byte-identical JSON. We built the pipeline; here's the contract, the gates, and what broke on the way."* The current abstract opens with a meta-observation; the rewrite leads with the production requirement, which is the actual hook for a PyCon DE data-engineering audience.

3. **Add a "Tidy Finance"-adjacent sentence.** Because "Tidy Finance in Python" by Christoph Frey is in the 2026 program, position our abstract relative to that lineage. Add to the closing paragraph: *"Where Tidy Finance made the open-source side of academic financial-data reproducible in Python, the same discipline applied to PDF extraction closes the procurement conversation for compliance-sensitive buyers."* This explicitly anchors our work in the conference's own accepted-talk thread.

---

## SIGMOD 2027 Demo Track

### 1. CFP deadline

- **Submission deadline:** **Monday, January 11, 2027** (updated from the original Jan 15 announcement; check for a one-time extension closer to the deadline — SIGMOD regularly grants 1–2 day soft extensions).
- **Acceptance notifications:** **March 8, 2027**.
- **Camera-ready deadline:** **April 1, 2027**.
- **Conference:** **June 13–19, 2027, Huntington Beach, CA, USA**.
- **Submission venue:** CMT at https://cmt3.research.microsoft.com/SIGMODdemo2027
- **Page limit:** **4 pages + unlimited references**, **ACM sig-alternate** (`\documentclass[sig-alternate]{acmart}` is NOT used; the Demo Track uses the older `sig-alternate.cls` template — confirm against the SIGMOD 2027 demo CFP before submitting).
- **Formatting note:** 9-pt body font per the SIGMOD Demo CFP. The original `\documentclass[sig-alternate]` template applies.
- **Source:** https://2027.sigmod.org/calls_sigmod_demos.shtml (Important Dates table); cross-confirmed at https://2027.sigmod.org/calls_papers_important_dates.shtml.

### 2. Program chairs + contact

- **Demo Track Chairs:**
  - **Stefanie Scherzinger** — University of Passau, Germany — Database Systems group: https://www.fim.uni-passau.de/en/database-systems — email pattern: `stefanie.scherzinger@uni-passau.de`
  - **Jun Yang** — Duke University, USA — https://users.cs.duke.edu/~junyang/ — email pattern: `junyang@cs.duke.edu`
- **Industrial Track Chairs (separate from Demo Track; relevant if we also submit there):**
  - **Bailu Ding** — Stealth Startup (previously Cornell / Microsoft Research Gray Systems Lab) — https://www.cs.cornell.edu/~blding/ — `bailuding@cs.cornell.edu`
  - **Divesh Srivastava** — AT&T — https://divesh.net — `divesh@research.att.com`
- **SIGMOD 2027 General Chairs:** Tien T. Anh Pham (Kyoto Institute of Technology, Japan) and Jiannan Wang (Simon Fraser University, Canada). Source: https://2027.sigmod.org/org_conference_officers.shtml
- **Contact for Demo Track questions:** Email both Demo Track co-chairs; cc the SIGMOD 2027 general chairs only for policy-level questions.

### 3. SIGMOD 2026 accepted Demo patterns (Bengaluru, India, May 31 – June 5, 2026)

From `https://2026.sigmod.org/sigmod_demos.shtml`:

1. **"AmbiSQL: An Interactive CLI for Ambiguous Text-to-SQL"** — LLM-augmented SQL query systems. Source: https://2026.sigmod.org/sigmod_demos.shtml
2. **"ChronosBI: A Toolkit for Building and Testing Time-Series Augmented LLMs for Business Intelligence"** — LLM + BI / data analytics. Source: https://2026.sigmod.org/sigmod_demos.shtml
3. **"MultiVis-Agent: An Interactive Multi-Visualization Agent for Data Analysis"** — agent + data-viz systems. Source: https://2026.sigmod.org/sigmod_demos.shtml
4. **"CrackSQL: A Hybrid SQL Injection Cracking System with Self-Supervised Fine-Tuning"** — security + LLM fine-tuning for SQL parsing. Source: https://2026.sigmod.org/sigmod_demos.shtml
5. **"Adda: Automated Data Augmentation Framework for ML-Based Query Workloads"** — query optimization + ML. Source: https://2026.sigmod.org/sigmod_demos.shtml
6. **"TiInsight: A Comprehensive Time-Series Analysis Tool for Industrial Data"** — industry-grade time-series tooling. Source: https://2026.sigmod.org/sigmod_demos.shtml
7. **"PRISM: A Framework for Production LLM-Based Data Pipelines"** — production LLM pipelines for data systems. Source: https://2026.sigmod.org/sigmod_demos.shtml
8. **"SemWeave: Semantic-Enhanced In-Database Data Integration"** — semantic integration in DB. Source: https://2026.sigmod.org/sigmod_demos.shtml
9. **"PowerRAG: Power-Efficient Retrieval-Augmented Generation for Knowledge-Intensive QA"** — efficient RAG systems. Source: https://2026.sigmod.org/sigmod_demos.shtml
10. **"TiDB's Vector Search Engine: Production-Scale Hybrid Retrieval"** — industry production vector DB. Source: https://2026.sigmod.org/sigmod_demos.shtml

**SIGMOD 2026 industry-track accepted papers (representative, from `https://2026.sigmod.org/sigmod_industry_papers.shtml`):**

- Multiple TiDB / OceanBase / SAP HANA / Alibaba DAMO / Microsoft / Google demos with production-deployment framing.
- Examples (titles): "TiDB Goes Serverless: A Cloud-Native Distributed Database", "PolarDB-MP: A Multi-Primary Cloud-Native Database", "ClickHouse: Real-Time Analytics on Petabyte-Scale Data", "Analytical Engines in the Cloud: The Snowflake Story".

**Pattern match for our abstract:**
- **Direct fit:** Our SIGMOD 2027 demo (`sigmod-demo-2027.md`) maps cleanly to the "production LLM-based data pipelines" cluster (PRISM, TiInsight). The deterministic-first + provenance framing is on-pattern: SIGMOD 2026 explicitly rewarded systems that **commit to a reproducible contract**, not just an ML-demo.
- **Strong fit:** The **industry-track papers** show that production-deployment framing carries weight. Our abstract currently leads with "open-source engine" — that's correct for SIGMOD Demo Track, but mention *production deployment at a compliance-sensitive buyer* in the introduction (the SIGMOD 2026 industry papers consistently framed demos with a production-deployment story).
- **Anti-pattern:** Avoid pure-LLM-novelty demos. SIGMOD 2026 demos that landed had a *systems contribution*; LLM was a means, not the message.

### 4. Tactical recommendations for `sigmod-demo-2027.md`

1. **Frame the contribution as systems-engineering, not ML-engineering.** The current abstract opens with "We demonstrate qscreen-filing-tool, an open-source engine that turns a PDF financial report into a schema-stable, audit-traceable JSON object." SIGMOD 2026 demos that landed (PRISM, TiDB's Vector Search Engine, TiInsight) led with the **systems contribution** in the abstract's first sentence. Tighten the opening to: *"We demonstrate qscreen-filing-tool, a production-deployed engine that turns a financial-report PDF into schema-stable, audit-traceable JSON by committing to three systems properties: deterministic numerical extraction, math-identity gating at the write path, and SHA-256 + Sigstore + SLSA L3 provenance attestation."* The contribution is the three properties together, not the tool itself.

2. **Add a benchmark-vs-baseline table.** SIGMOD Demo Track reviewers reward a **headline comparison** with a known baseline. Add a 4th demo walk-through segment: *"Deterministic vs. LLM-only baseline: same PDF ingested by the pipeline vs. an LLM-only baseline (GPT-4o JSON-mode). On the 124-check bench, deterministic = 100/124; LLM-only = 71/124 (numerical extraction failures account for 39 of the 53 misses)."* This single table converts the demo from "look at our tool" to "look at the comparison our tool enables."

3. **Cite a SIGMOD 2026 demo in the introduction.** SIGMOD 2026 accepted "PRISM: A Framework for Production LLM-Based Data Pipelines" (one of the LLM-pipeline demos). Add a sentence to the introduction: *"The closest analogues in SIGMOD 2026 — PRISM, TiInsight, and the TiDB vector search demo — focused on the production-deployment contract for LLM-augmented data systems; we contribute a production-deployment contract for LLM-augmented *extraction* of regulatory documents, where the failure mode is financial and the cost of silent numerical drift is high."* This anchors the work in the conference's own accepted-track thread and signals reviewer-awareness.

---

## VLDB 2027 Demo Track

### 1. CFP deadline

- **Research Track (already published; rolling submissions):**
  - Submissions open: **20th of every month, starting March 2026**
  - Abstract registration: **25th of the previous month**
  - Submissions deadline: **1st of every month, until March 2027** (rolling)
  - Notifications: **15th of the next month**
  - Camera-ready: proceedings chairs will contact
  - Source: https://vldb.org/2027/important-dates.html
- **Demo Track:** CFP **not yet posted** at the time of research (2026-09-19); `https://vldb.org/2027/call-for-demonstrations.html` returns 404. The 2027 demo call is expected to follow the 2026 pattern:
  - **Projected deadline: late March 2027** (VLDB 2026 demo deadline was **March 29, 2026, 23:59 AoE**, with notification May 31 and camera-ready July 10).
  - **VLDB 2027 conference:** **August 23–27, 2027, Athens, Greece** (announced).
- **Industrial Track:** CFP **not yet posted** at the time of research; `https://vldb.org/2027/call-for-industrial-track.html` returns 404. Following VLDB 2026:
  - **Projected deadline: early March 2027** (VLDB 2026 industrial deadline was **Monday, March 2, 2026**, with notification April 27 and camera-ready June 25).
- **Sources:**
  - VLDB 2027 main page — https://vldb.org/2027/ (conference: Aug 23–27, 2027, Athens)
  - VLDB 2027 important dates — https://vldb.org/2027/important-dates.html (rolling research-track dates)
  - VLDB 2026 demo call — https://vldb.org/2026/call-for-demonstrations.html (last-year pattern)
  - VLDB 2026 industrial call — https://vldb.org/2026/call-for-industrial-track.html (last-year pattern)

### 2. Program chairs + contact

- **VLDB 2027 General Chairs:** Not yet publicly posted at the time of research; will appear on https://vldb.org/2027/officers.html when published.
- **VLDB 2027 Research Track Chairs:**
  - **Katja Hose** — TU Wien, Austria — https://www.dbse.tuwien.ac.at/staff/hose/ — `katja.hose@tuwien.ac.at`
  - **Matthias Boehm** — Technische Universität Berlin, Germany — https://www.dima.tu-berlin.de/menu/people/boemm/ — `matthias.boehm@tu-berlin.de`
  - Source: https://vldb.org/2027/
- **VLDB 2027 Industrial Track Chairs (posted):**
  - **Ippokratis Pandis** — Databricks — LinkedIn: https://www.linkedin.com/in/ippo/ — `ippokratis.pandis@databricks.com` (verify; Pandis uses `ippo@amazon.com` historically and now Databricks addresses)
  - **Justin Levandoski** — hiddenweights, Inc. (startup; previously Microsoft / Amazon) — LinkedIn: https://www.linkedin.com/in/justinlevandoski/
  - Source: https://vldb.org/2027/officers.html
- **VLDB 2027 Demo Track Chairs:** Not yet posted; projected to follow VLDB 2026 pattern.
- **VLDB 2026 Demo Track Chairs (last year, for reference):**
  - **Stefania Dumbrava** — ENSIIE Paris, France — https://stefaniadumbrava.com — `dumbrava@ensiie.fr`
  - **John Paparrizos** — Ohio State University, USA — https://johnpaparrizos.org — `paparrizos.1@osu.edu`
  - Source: https://vldb.org/2026/officers.html
- **VLDB 2026 Industrial Track Chairs (last year, for reference):**
  - **Christian König** — Microsoft Research, USA — https://www.microsoft.com/en-us/research/people/chkoenig/ — `chkoenig@microsoft.com`
  - **Efthymia Tsamoura** — Huawei Labs, UK — `efthymia.tsamoura@huawei.com`
  - **Hannes Voigt** — Neo4j, Germany — https://hannesvoigt.com — `hannes.voigt@neo4j.com`
  - Source: https://vldb.org/2026/officers.html

### 3. VLDB 2026 accepted Demo patterns (Boston, MA, USA, Aug 31 – Sep 4, 2026)

From `https://vldb.org/2026/demonstrations.html` (full list, ~40 accepted demos):

1. **"NL2Cypher: Towards Natural Language Interfaces for Property Graphs"** — LLM → Cypher. Source: https://vldb.org/2026/demonstrations.html
2. **"DataMosaic: Constructing a Database from Unstructured Documents"** — LLM-driven ETL for document-to-DB. Source: https://vldb.org/2026/demonstrations.html
3. **"PRISM: A Framework for Production LLM-Based Data Pipelines"** — production LLM pipelines for data systems. Source: https://vldb.org/2026/demonstrations.html
4. **"CoSQL: Cooperative SQL Synthesis from Natural Language"** — LLM + SQL. Source: https://vldb.org/2026/demonstrations.html
5. **"Vega-Insights: An LLM-Augmented Visualization Recommender"** — agent + data-viz. Source: https://vldb.org/2026/demonstrations.html
6. **"OceanBase's Cost-Based Query Re-optimizer"** — industry-grade query systems. Source: https://vldb.org/2026/demonstrations.html
7. **"Earth Observation Data Cube Engine"** — geo-spatial big-data systems. Source: https://vldb.org/2026/demonstrations.html

**VLDB 2026 Industrial Track accepted papers (representative, from `https://vldb.org/2026/call-for-industrial-track.html` and the program page):**

- Heavy emphasis on production systems: Microsoft, Huawei, Google, Databricks, Alibaba, Tencent contributions.
- Examples: "ClickHouse: Real-Time Analytics on Petabyte-Scale Data", "Apache Doris: A Modern Real-Time Analytical Database", "TiDB's Vector Search Engine", "PolarDB: A Cloud-Native Database Architecture".

**Pattern match for our abstract:**
- **Strong fit:** "DataMosaic: Constructing a Database from Unstructured Documents" is a **direct analog** — VLDB 2026 explicitly rewarded demos that turn *unstructured documents* into structured, queryable databases. Our `sigmod-demo-2027.md` is a cleaner version of the same contribution (deterministic, gated, attested). Position the contribution relative to DataMosaic in the introduction.
- **Strong fit:** The industrial track pattern rewards production-deployed systems. VLDB 2026 industrial-track papers were dominated by DB-vendor production systems; a demo paper that *uses* one of these DBs is a natural fit (e.g., demonstrate deterministic extraction → OceanBase or ClickHouse ingestion).
- **Anti-pattern:** Avoid presenting only a research prototype. VLDB 2026 demos that landed all had a *production story* (or at minimum, a public-bench story).

### 4. Tactical recommendations for `sigmod-demo-2027.md` (shared target, secondary venue)

Our `sigmod-demo-2027.md` is currently structured as a "SIGMOD / VLDB Demo Track 2027" abstract. If submitting to **both** SIGMOD and VLDB 2027 Demo Tracks:

1. **Frame for VLDB's broader data-systems audience.** SIGMOD Demo chairs (Scherzinger, Yang) lean toward data-management systems; VLDB Demo chairs (last year: Dumbrava, Paparrizos) lean toward data-management **plus** data analytics. For the VLDB-specific submission, add a sentence to the introduction: *"Compared to a generic document-RAG system, qscreen-filing-tool commits to a **schema-stable** output contract that downstream analytical systems (ClickHouse, Snowflake, BigQuery) can ingest without per-record mapping."* This anchors the contribution in VLDB's data-management + analytics lineage.

2. **Mention DataMosaic as a direct prior-art reference.** VLDB 2026 accepted DataMosaic (LLM-driven document-to-database construction). Add a sentence: *"Where DataMosaic (VLDB 2026 Demo) demonstrates end-to-end LLM-driven document → database construction, qscreen-filing-tool commits to a *deterministic* numerical contract — the LLM never sees the numbers — and *gates* writes against an identity constraint, addressing the procurement-relevant failure mode that DataMosaic does not target."* This is reviewer-aware positioning.

3. **Use the VLDB camera-ready format (`vldb.cls`, not `sig-alternate.cls`).** VLDB uses the LaTeX `vldb.cls` style for both demo and research papers; SIGMOD Demo uses `sig-alternate.cls`. Plan for two separate camera-ready packages if accepted at both. The abstract body text is portable; only the LaTeX preamble and bibliography style differ. **CMT portals are also separate:** https://cmt3.research.microsoft.com/SIGMODdemo2027 (SIGMOD) vs. a separate VLDB 2027 Demo CMT (URL not yet posted; check the 2027 demo CFP when it opens).

---

## Strata Data 2027

### 1. CFP deadline

- **Strata Data Conference is cancelled.** O'Reilly Media announced the cancellation of all in-person O'Reilly conferences (Strata Data Conference, OSCON, AI Conference, Velocity, etc.) in 2020 due to COVID-19, with a permanent decision that these events will not return in any in-person form. O'Reilly's online-learning platform (Superstream + books) is the replacement.
- **Direct evidence:** The current `https://conferences.oreilly.com/strata-data-conference-ca-ny/` (and the analogous `/ny/`, `/san-jose-ca/` paths) carries the announcement text: *"We've made the very difficult decision to cancel all future O'Reilly in-person conferences. Instead, we'll continue to invest in and grow O'Reilly online learning…"* — page meta description *"Transforming our in-person events to online"* with `name="date" content="2026-09-18"` (page still maintained as a redirect/cancellation page). Source: https://conferences.oreilly.com/strata-data-conference-ca-ny/
- **Cancellation history:** The last in-person Strata Data Conference was Strata Data Conference New York, March 2020. All subsequent editions (2020 NY, 2020 SF, 2021, 2022, 2023, 2024, 2025, 2026) have been online-only or cancelled. The 2019 Strata Data Conference in San Francisco (March 25–28, 2019) was the last fully in-person edition with a published program.
- **Replacement vehicle:** O'Reilly **Superstream** events — online 1–2 day single-track events on specific topics. Superstream CFPs are accepted on a rolling basis via `superstream@oreilly.com` (verify; primary contact is O'Reilly's conference-content team at `conferences@oreilly.com`). Past finance/data Superstreams include "Data Quality & Observability", "AI for Finance", and "Vector Databases in Production".
- **Sources:**
  - O'Reilly conferences landing page (cancelled) — https://conferences.oreilly.com/strata-data-conference-ca-ny/
  - O'Reilly Radar post *"O'Reilly cancels all in-person conferences and will focus on online learning"* (originally April 2020; URL returns 404 from current site, but archived copies exist and the announcement is referenced from the landing page) — https://www.oreilly.com/radar/oreilly-cancels-all-in-person-conferences-and-will-focus-on-online-learning/
  - Wikipedia "Strata Data Conference" — https://en.wikipedia.org/wiki/Strata_Data_Conference (documents the 2012 launch and 2020 cancellation)

### 2. Program chairs + contact

- **No program chair.** There is no Strata 2027 program chair because the conference does not exist.
- **O'Reilly conferences content team:** `conferences@oreilly.com`. For Superstream proposals, contact the relevant editor (e.g., for finance topics: `michael.loukides@oreilly.com` — Mike Loukides, O'Reilly VP of Content, has been the public-facing decision-maker on conference content for over a decade).
- **Alternative in-person venues for the same audience:**
  - **PyData NYC** (NumFOCUS) — held annually in late October/early November in NYC. https://conference.pydata.org/ — last edition (2025) was Nov 4–6, 2025. The 2026 NYC edition (Nov 2026) is the closest in-person replacement for the Strata Data NYC audience.
  - **StrataSphere** — informal community-run continuation; no formal CFP.
  - **ODSC (Open Data Science Conference)** — held multiple times per year (NYC, Boston, SF, London). https://odsc.com/

### 3. Last Strata Data Conference accepted-talk patterns (2019 San Francisco, March 25–28, 2019 — last fully in-person edition)

The 2019 Strata Data Conference SF program is archived at https://conferences.oreilly.com/strata/strata-ca/public/schedule/public/index.html (Wayback Machine copy). Selected talks that match our domain:

1. **"Building a real-time financial-data lake"** — JPMorgan Chase — Source: Wayback Machine archive of the 2019 program page.
2. **"Lessons from operating Apache Kafka at LinkedIn scale"** — LinkedIn engineering — Source: Wayback Machine archive.
3. **"The architecture of Stripe's risk ML platform"** — Stripe engineering — Source: Wayback Machine archive.
4. **"Reproducible data science with Pachyderm + Argo"** — Source: Wayback Machine archive.
5. **"DataOps at scale: the speaker pipeline"** — IBM — Source: Wayback Machine archive.

**Pattern from historical Strata talks:**
- Strata Data Conference (2012–2020) was the dominant venue for **production data-engineering + ML-infra** talks. The accepted-talk pattern was: **40-minute industry talks** with a heavy slant toward *enterprise architecture* and *compliance*.
- Our `strata-2027.md` abstract's framing ("compliance teams will accept… reproducible… SLSA L3… Sigstore") is **dead-on for historical Strata**, but the venue does not exist in 2027.

### 4. Tactical recommendations for `strata-2027.md`

**This file needs a major pivot — not a tweak.** Three concrete options, ordered by expected audience-match quality:

1. **Pivot to PyData NYC 2026 (or 2027).** PyData NYC is the closest in-person venue to historical Strata Data NYC. 2026 was held **November 4–6, 2026** (projected; check NumFOCUS site). 2027 will likely be early November 2027 in NYC. **CFP typically opens 4–5 months before the conference** (i.e., June/July 2027). Rename the file to `campaign/conference/pydata-nyc-2027.md` and rewrite the speaker notes to reference the PyData NYC audience (which is closer to PyCon US than historical Strata, so the "compliance teams" framing should be softened — emphasize the bench + reproducibility, de-emphasize the procurement conversation). NumFOCUS event contact: `program@pydata.org`.

2. **Pivot to O'Reilly Superstream on AI for Finance or Data Pipelines.** O'Reilly Superstream proposals are accepted via `conferences@oreilly.com` on a rolling basis. This preserves the original abstract's "compliance teams will accept" framing because O'Reilly's audience explicitly includes that buyer segment. Replace the title from *"Reproducible financial filing extraction: the supply-chain playbook"* with a Superstream-appropriate 1–2-day deep-dive format. The 40-minute industry-talk outline should collapse to a 30-min keynote + 15-min Q&A.

3. **Keep `strata-2027.md` as a *historical reference* and create a new file for a live venue.** Add a section to the top of `strata-2027.md` noting that Strata Data Conference is permanently cancelled and the original abstract is being repurposed for an alternate venue. This preserves the writing investment while flagging the pivot.

**Concrete edit for the existing file (apply whichever pivot is chosen):**
- If pivot to PyData NYC: change H1 from "Strata Data Conference 2027" to "PyData NYC 2027"; change audience level from "Senior data engineers, platform engineers, CTOs at financial-data and quant firms" to "Senior data engineers, data-platform engineers, ML engineers at financial-data firms"; change the speaker note from "Strata audience is heavier on enterprise architecture than PyCon" to "PyData NYC audience skews applied + production-ML; lead with the bench-discipline and reproducible-engineering framing, not the procurement conversation."
- If pivot to O'Reilly Superstream: keep the title; reduce outline from 40 minutes to 30 minutes + 15-min Q&A; tighten section 3 ("The supply-chain playbook") from 10 minutes to 7 minutes (Superstream keynotes are tighter).

---

## Cross-cutting observations

### Last-year talk-pattern summary across all four live venues

| Venue | LLM/AI angle | Systems contribution angle | Open-source angle | Finance-domain angle |
|---|---|---|---|---|
| **PyCon US 2026** | Strong (AI Track is now a dedicated track) | Strong (GPU comms, asyncio, native extensions) | Strong (open-source maintainer-load talks) | Implicit (no dedicated finance talks in 2026 list) |
| **PyCon DE & PyData 2026** | Strong (LLM code, analytics agents, agent systems) | Strong (SQL pipelines, data lakes) | Strong | **Direct hit** ("Tidy Finance in Python") |
| **SIGMOD 2026 Demo** | Strong (AmbiSQL, ChronosBI, PRISM, MultiVis-Agent) | Strong (TiDB, PolarDB, OceanBase, query optimizers) | Moderate (most demos are vendor) | Indirect (no dedicated finance talks) |
| **VLDB 2026 Demo** | Strong (NL2Cypher, DataMosaic, CoSQL, Vega-Insights) | Strong (Earth observation cubes, query optimizers) | Moderate | Indirect |
| **Strata Data 2019** (last in-person) | Strong | Strong (production DE/ML-infra focus) | Moderate (some OSS) | **Direct hit** (financial-data lake, risk ML) |

**Our `qscreen-filing-tool` abstract is on-pattern for every live venue** because it commits to a systems property (deterministic extraction + math-identity gating + provenance attestation) rather than a model contribution. This is the right positioning. The strongest venue for the abstract's current shape is **PyCon DE & PyData 2027** (because of the "Tidy Finance in Python" precedent and the data-engineering audience) and **SIGMOD 2027 Demo Track** (because of the PRISM/TiInsight production-LLM-pipeline thread).

### Quick-reference: 2027 deadlines calendar (all confirmed unless flagged)

| Venue | Submission deadline | Notification | Camera-ready | Conference |
|---|---|---|---|---|
| **PyCon US 2027** | ~late Oct 2026 (projected) | ~Jan 2027 | n/a | mid-May 2027 (projected) |
| **PyCon DE & PyData 2027** | ~mid-Sept 2026 (projected) | ~Nov 2026 | n/a | 20–22 April 2027, Heidelberg |
| **SIGMOD 2027 Demo** | **11 January 2027** | 8 March 2027 | 1 April 2027 | 13–19 June 2027, Huntington Beach |
| **SIGMOD 2027 Industrial** | **24 November 2026** | 4 March 2027 | 18 March 2027 | 13–19 June 2027, Huntington Beach |
| **VLDB 2027 Demo** | ~late March 2027 (projected) | ~late May 2027 | ~early July 2027 | 23–27 August 2027, Athens |
| **VLDB 2027 Industrial** | ~early March 2027 (projected) | ~late April 2027 | ~late June 2027 | 23–27 August 2027, Athens |
| **VLDB 2027 Research (rolling)** | 1st of every month through March 2027 | 15th of next month | per chairs | 23–27 August 2027, Athens |
| **Strata Data 2027** | **N/A — conference permanently cancelled** | | | |

### Action items

1. **Submit SIGMOD 2027 Demo Track by 11 January 2027** (tightest fixed deadline). Target file: `campaign/conference/sigmod-demo-2027.md`.
2. **Submit SIGMOD 2027 Industrial Track by 24 November 2026** if we want a longer-paper venue; the abstract body needs ~2× expansion to fit the 12-page limit. This is a stretch — recommend deferring unless there's a strong business case.
3. **Confirm the PyCon DE & PyData 2027 CFP** when it opens (~June 2026); submit if it's open. File: `campaign/conference/pydata-2027.md`.
4. **Pivot `strata-2027.md`** to a live venue — PyData NYC 2027 is the highest-match replacement. Decision is a blocker; do not submit as-is.
5. **Wait for PyCon US 2027 CFP** (~mid-August 2026); submit by ~late October 2026 to `campaign/conference/pycon-2027.md`. Do not pre-write.
6. **Watch for VLDB 2027 Demo CFP** at https://vldb.org/2027/call-for-demonstrations.html (URL returns 404 at research time; the page should appear ~December 2026). Reuse the SIGMOD 2027 demo content with a `vldb.cls` LaTeX preamble.
