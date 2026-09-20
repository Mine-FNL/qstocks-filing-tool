/* launch-data.js — populates the pre-fill textareas on /launch.html
 *
 * Keep this in sync with campaign/channels/*.md. If the source copy
 * changes, update here too. (Documented in web/README.md.)
 */

(function () {
  'use strict';

  const COPY = {
    'hn-text': `TITLE:

qscreen-filing-tool: open-weight PDF → lossless filing JSON for financial reports

URL:

https://github.com/Mine-FNL/qstocks-filing-tool

(Or: https://qscreen-filing-tool.vercel.app)

FIRST COMMENT:

We built an open-source Python engine that turns a PDF financial report into a schema-stable, audit-traceable JSON object. ~3 s per filing, $0 API cost, math-identity gate refuses to ship self-contradictory records.

Three architectural bets:

1. **Deterministic-first extraction.** PDF tables are read in code (pdfplumber); the model only fills gaps (audit opinion, notes, segments). A 270M local model produces the same numerical contract as GPT-4o.

2. **Math-identity gate.** If Assets ≠ L + E within ±2 %, the JSON doesn't ship. 11 cross-cutting + 25 issuer-specific pre-flag rules run before save. Blocked records stay on disk with evidence pointing at the offending line item.

3. **SHA-256 cross-filing fingerprints + Sigstore keyless signing + SLSA Build L3.** Re-ingesting the same PDF on any engine commit produces bit-identical JSON, attestable back to the engine commit.

124-check public bench (Qatar-listed universe, 80.6 % pass rate, regression-gated). 499 tests. Cross-platform CI. Multi-arch container on ghcr.io.

Try it in 30 seconds (no PDF, no API key):

\`\`\`
pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/latest/download/qscreen_filing_tool-1.6.0-py3-none-any.whl
qscreen-demo
\`\`\`

Repo: https://github.com/Mine-FNL/qstocks-filing-tool
Whitepaper: https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.pdf
Live bench: https://mine-fnl.github.io/qstocks-filing-tool/demo.html

Happy to dig into any of the design choices in the comments.`,

    'lobsters-text': `TITLE:

qscreen-filing-tool: open-weight PDF → lossless filing JSON

URL:

https://github.com/Mine-FNL/qstocks-filing-tool

Cross-posting from HN — same project, lower-traffic venue, deeper technical audience. The QSE-flavored use case is one driver, but the engine itself is jurisdiction-agnostic: drop a profile into profiles/ for any other market and the rest of the code doesn't change.

Two engineering bets worth flagging:

1. Deterministic-first extraction. PDF tables are read in code; the LLM only fills gaps. Numbers never pass through the model — so a 270M local model produces the same lossless contract as a frontier cloud model.

2. Math-identity gate. The JSON won't ship if Assets ≠ L + E within ±2 %. 11 cross-cutting + 25 issuer-specific pre-flag rules run before save. If a record contradicts itself, the record doesn't ship, and the evidence points at the offending line item.

Plus SHA-256 cross-filing fingerprints + Sigstore keyless signing: re-ingest of the same PDF produces bit-identical JSON, cryptographically attestable back to the engine commit that produced it.

499 tests, ruff clean, mkdocs --strict, container on ghcr.io/Mine-FNL/qstocks-filing-tool, install paths that don't require a PyPI Trusted Publisher click.

Happy to dig into any of the design choices in the comments.`,

    'reddit-ml-text': `TITLE:

qscreen-filing-tool: open-weight PDF → lossless filing JSON (deterministic-first extraction)

BODY:

Hi r/MachineLearning — sharing a project I've been building for six months.

What it does: a Python engine that turns a PDF financial filing into a schema-stable, audit-traceable JSON object, in ~3 s per filing, $0 API cost, with a math-identity gate that refuses to ship self-contradictory records.

The non-obvious engineering bet: **the numbers never pass through the model.** PDF tables are parsed in code (pdfplumber); the model only fills gaps (audit opinion, notes, segments). This is why a 270M local model produces the same numerical contract as a frontier cloud model — the numbers come from tables, not from the LLM.

The math-identity gate runs at the write path. If Assets ≠ L + E within ±2 %, the JSON doesn't ship. 11 cross-cutting + 25 issuer-specific pre-flag rules run before save. The evidence payload points at the offending line item.

124-check public bench against the current Qatar-listed universe (80.6 % pass rate, regression-gated). 499 tests. Multi-arch container on ghcr.io.

Repo: https://github.com/Mine-FNL/qstocks-filing-tool
Live bench: https://mine-fnl.github.io/qstocks-filing-tool/demo.html
Whitepaper: https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.pdf

Happy to answer questions about the deterministic-first architecture or the math-identity gate. (Cross-posted from HN: <link>.)`,

    'reddit-quant-text': `TITLE:

qscreen-filing-tool: open-weight PDF → lossless filing JSON (with math-identity gate)

BODY:

Hi r/quant — sharing a project aimed at the failure modes we hit in production financial-data ingestion.

The pipeline:

1. PDF → pdfplumber (tables) → sign + scale correction in code → JSON
2. Math-identity gate (Assets = L + E ± 2 %, sector-aware; 11 cross-cutting + 25 issuer-specific pre-flag rules)
3. SHA-256 cross-filing fingerprint + Sigstore keyless signing

The architecture is jurisdiction-agnostic. The default profile ships 55 QSE tickers; AE / SA / KW are documented as one-directory-drop extensions. Each jurisdiction profile is a deep artefact (~6,000 lines of seed + 25 pre-flag rules in the Qatar case).

124-check public bench at 80.6 % pass rate. The bench gates every PR — drops below the floor fail CI.

Most relevant if you're working with: MENA financial markets, regulated-data workflows, compliance-grade ingestion, or financial-data infrastructure builds vs buy.

Repo: https://github.com/Mine-FNL/qstocks-filing-tool
Live bench: https://mine-fnl.github.io/qstocks-filing-tool/demo.html
Whitepaper: https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.pdf
Sponsor tiers: $5k / $15k / $50k — see investor one-pager at https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/investor-one-pager/one-pager.pdf`,

    'ph-text': `TAGLINE:

Open-weight PDF → lossless filing JSON for financial reports

ONE-LINE DESCRIPTION:

qscreen-filing-tool turns any exchange's annual or interim report into a schema-stable, audit-traceable JSON object. Math-identity gate refuses to ship self-contradictory records. SHA-256 cross-filing fingerprints + Sigstore keyless signing. 499-test suite, containerized, install via pip, GitHub Releases, or ghcr.io.

MAKER COMMENT (post immediately as yourself):

👋 Maker here.

Two design decisions worth flagging because they aren't obvious from the landing page:

1. **Deterministic-first extraction.** The PDF tables are read in code (pdfplumber); the model only fills gaps (audit opinion, notes, segments). This is why a 270M local model produces the same lossless contract as a frontier cloud model — numbers never pass through the LLM. So you can run fully offline for $0.

2. **The math-identity gate.** The JSON won't ship if Assets ≠ L + E within ±2 %. Eleven cross-cutting + twenty-five issuer-specific pre-flag rules run before save(). If a record contradicts itself, the record doesn't ship and the evidence points at the offending line item.

Both of these are unusual in this space and were the actual reason we built the tool — every existing option shipped the JSON regardless of internal consistency, which makes downstream pipelines fragile.

Try it: pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/latest/download/qscreen_filing_tool-1.6.0-py3-none-any.whl
then qscreen-ingest report.pdf --symbol <TICKER> --year <YYYY>.

Happy to answer technical questions in the comments.`,

    'linkedin-text': `TITLE:

I shipped an open-source engine for financial-document extraction with built-in consistency gates.

BODY:

Most "PDF to JSON" extractors ship the JSON regardless of internal consistency. Downstream pipelines re-ingest every quarter because they can't trust hash stability. Compliance teams can't answer "which engine version produced this row?" without a database comment.

We built qscreen-filing-tool to fix three failure modes:

1. **Deterministic-first extraction.** PDF tables are read in code; the model only fills gaps. A 270M local model produces the same numerical contract as a frontier cloud model.

2. **Math-identity gate.** If Assets ≠ Liabilities + Equity within ±2 %, the record doesn't ship. Eleven cross-cutting + twenty-five issuer-specific pre-flag rules.

3. **SHA-256 cross-filing fingerprints + Sigstore keyless signing + SLSA Build L3.** Re-ingesting the same PDF on any engine commit produces bit-identical JSON, attestable back to the engine commit.

Six months in production. 499 tests. 124-check public bench at 80.6 %. Hardened supply chain (SBOM + Sigstore + SLSA L3). Multi-arch container.

If you build or buy quant data infrastructure, the whitepaper is worth the read:

https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.pdf

Or try the 30-second demo: pip install + qscreen-demo. No PDF, no API key.

Repo: https://github.com/Mine-FNL/qstocks-filing-tool
Live bench: https://mine-fnl.github.io/qstocks-filing-tool/demo.html
Sponsor / partner inquiries: see investor one-pager at the repo.`,

    'x-text': `1/ Most "PDF → JSON" extractors ship the JSON regardless of internal consistency.

We built one that doesn't. Open-source, MIT-licensed, jurisdiction-agnostic, math-identity-gated. 🧵

2/ Three architectural bets:

1️⃣ Numbers never pass through the model. PDF tables are read in code; the model fills gaps only.

2️⃣ The JSON won't ship if Assets ≠ L + E within ±2 %. 11 cross-cutting + 25 issuer-specific pre-flag rules run before save().

3️⃣ SHA-256 cross-filing fingerprints + Sigstore keyless signing + SLSA L3 attestation. Re-ingest of the same PDF produces bit-identical JSON.

3/ 124-check public bench at 80.6 % pass rate (Qatar-listed universe). 499 tests. Multi-arch container on ghcr.io.

Repo ⤵
https://github.com/Mine-FNL/qstocks-filing-tool

4/ Deterministic-first extraction means a 270M local model produces the same numerical contract as a frontier cloud model. Numbers come from tables, not from the model. So you can run fully offline for $0.

5/ Why this matters: most extractors re-ingest every quarter because the JSON changes between runs. We don't, because the hash is part of the record's identity. Sigstore signs every release; you can verify "this PDF produced this JSON on this commit" without trusting the operator.

6/ Try it in 30 seconds (no PDF, no API key):
\`\`\`
pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/latest/download/qscreen_filing_tool-1.6.0-py3-none-any.whl
qscreen-demo
\`\`\`

7/ [image: architecture-16x9.jpg]

Architecture: deterministic extraction → gap fills → math-identity gate → SHA-256 fingerprint → optional Sigstore-signed JSON record.

8/ The gate runs *before* save(). This is the architectural choice that matters: the gate isn't a post-hoc validator, it's part of the write path. Blocked records stay on disk with evidence pointing at the offending line item; they never propagate.

9/ Compliance teams cite the SBOM + Sigstore + SLSA L3 chain in their internal docs — and we don't pay for that PR.

10/ Where we got it wrong the first three months: asking the LLM to read numbers. It hallucinates 5-10 % of them. After swapping to deterministic-first, the bench went from 60 % to 80 % and the variance dropped 8x.

11/ What's next: UAE profile (sponsor-funded), audit-opinion classification model trained on gate-flagged disagreements, multi-PDF batch orchestrator with SQLite-backed resume.

12/ If you build quant / compliance / audit pipelines, the whitepaper is worth the read (~6,000 words, 9 sections + 3 appendices):
https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.pdf

13/ Show HN landing: I posted this on HN earlier today; cross-posting here.

Repo + live bench + whitepaper + investor one-pager all linked from:
https://qscreen-filing-tool.vercel.app

14/ If you're a quant / finance-tech person who'd want to talk about a UAE or KSA jurisdiction drop, my email is on the SECURITY.md disclosure contact.

15/ Star ⭐ if the architecture resonates. RTs appreciated. End of thread.`,

    'mastodon-text': `📦 New release: qscreen-filing-tool v1.6.0 — open-weight PDF → lossless filing JSON for financial reports.

Three bets:
• Numbers never pass through the model (270M local model = same contract as frontier cloud)
• Math-identity gate blocks self-contradictory records (Assets ≠ L+E? Doesn't ship.)
• SHA-256 + Sigstore + SLSA L3 chain

124-check public bench at 80.6%. MIT.

Try it: https://qscreen-filing-tool.vercel.app
Repo: https://github.com/Mine-FNL/qstocks-filing-tool`,

    'bluesky-text': `📦 New release: qscreen-filing-tool v1.6.0

Open-weight PDF → lossless filing JSON for financial reports. 270M local model = same numerical contract as frontier cloud. Math-identity gate blocks self-contradictory records. SHA-256 + Sigstore chain. 124-check bench at 80.6%.

https://qscreen-filing-tool.vercel.app`,

    'infoq-text': `SUBJECT: How a 270M-parameter local model beat GPT-4o on a financial PDF extraction benchmark

Hi [editor name],

I'd like to pitch a story on a counterintuitive finding from six months of building an open-source financial-document extraction pipeline (qscreen-filing-tool, MIT-licensed, 499 tests, 124-check bench at 80.6 %).

The finding: a 270M-parameter local model produces the same lossless filing contract as GPT-4o or Claude Sonnet 4 — but only because we stopped asking the model to do the part it isn't good at (reading tables) and started asking it only to do the part it is good at (filling gaps).

The architectural inversion — "deterministic-first extraction" — has three properties that I think will resonate with your readers:

1. Numbers never pass through the model. Tables are parsed in code; the model fills audit opinion, note text, and segment labels.

2. The math-identity gate refuses to ship self-contradictory records. Assets = L + E is enforced ±2 % with sector-aware overrides; the record doesn't ship if it fails.

3. SHA-256 cross-filing fingerprints + Sigstore keyless signing. Re-ingesting the same PDF on any engine commit produces bit-identical JSON, cryptographically attestable back to the engine commit.

I have a 6,000-word whitepaper, a public demo page (regenerated on every release), and reproducible benchmarks. Happy to do a 30-minute walkthrough or send written materials.

Repo:        https://github.com/Mine-FNL/qstocks-filing-tool
Demo:        https://mine-fnl.github.io/qstocks-filing-tool/demo.html
Whitepaper:  https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.pdf

— [Your name]`,

    'xbrl-text': `SUBJECT: qscreen-filing-tool — upstream extractor for your AI Connector MCP server (community contribution)

Hi David,

I lead the qscreen-filing-tool project — an open-source Python engine that turns a PDF financial report into a clean iXBRL-tagged JSON object, with a math-identity gate that refuses to ship self-contradictory records (Assets ≠ L + E within ±2 %).

When I saw that XBRL US open-sourced the AI Connector / MCP server in 2026 — providing as-filed XBRL data to consumers — I thought there was a natural upstream connection: qscreen could be the deterministic ingestion layer that feeds the Connector cleaner iXBRL-tagged records. Today the Connector pulls from EDGAR; the math-identity gate is a property the upstream could enforce.

Three concrete next steps I can offer:

1. A joint demo: ingest a public 10-K through qscreen, pipe the JSON into the AI Connector, show the Connector pulling from a cleaner upstream than EDGAR-direct.

2. A joint whitepaper: "Deterministic-first ingestion for as-filed XBRL data" — 6,000-word write-up that documents the architecture and the gate-result distribution on XBRL-US-tagged filings.

3. A small grant for the UAE jurisdiction profile ($15k sponsor tier covers ~3 weeks of work); XBRL US could co-sponsor in exchange for the profile shipping with XBRL-US-flavored pre-flag rules.

The whole project is MIT-licensed, supply-chain-hardened (SBOM + Sigstore + SLSA L3), and ships a public 124-check regression bench. Happy to set up a 30-min call.

Repo:        https://github.com/Mine-FNL/qstocks-filing-tool
Live bench:  https://mine-fnl.github.io/qstocks-filing-tool/demo.html
Whitepaper:  https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.pdf
LinkedIn:    https://www.linkedin.com/in/davidtauriello (you)

— [Your name]`,

    'nlnet-text': `SUBJECT: qscreen-filing-tool — NLnet grant proposal (Nov 3, 2026 deadline)

Hi NLnet Foundation,

I'm writing to propose a 6-month project for the NLnet Privacy & Infrastructure line: building out the UAE jurisdiction profile of qscreen-filing-tool to bench-grade (top 30 ADX + DFM listed equities, ~7-10 working days of engineering, fully open-source MIT output).

Background: qscreen-filing-tool is an open-source Python engine that turns any exchange's annual or interim report into a schema-stable, audit-traceable JSON object. Six months in production. 499 tests. 124-check public bench at 80.6 %. Hardened supply chain (SBOM + Sigstore keyless signing + SLSA Build L3 attestation, all public).

The default profile ships 55 Qatar-listed tickers (QSE) with 11 cross-cutting + 25 issuer-specific pre-flag rules. The UAE jurisdiction profile is currently a stub — the engineering is bounded and the architecture is jurisdiction-agnostic, so the work is largely data-tables and pre-flag rules.

Why this fits NLnet's mandate: financial-data infrastructure is increasingly important for transparency / privacy / consumer-protection use cases. The open-source release of jurisdiction profiles makes the audit trail inspectable by anyone, not just by the operator.

Deliverables:
- profiles/uae/ populated to bench-grade (~30 tickers)
- 11 + 25 cross-cutting + issuer-specific pre-flag rules
- New golden-set cases for the bench
- Documented architecture decision records (ADRs) for the UAE-specific fiscal calendar + auditor history
- All release artifacts public, signed, and attested

Repo:        https://github.com/Mine-FNL/qstocks-filing-tool
Whitepaper:  https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.pdf

— [Your name]`,
  };

  // Populate textareas
  Object.entries(COPY).forEach(([id, text]) => {
    const el = document.getElementById(id);
    if (el) el.value = text;
  });

  // Copy-to-clipboard handlers
  document.querySelectorAll('[data-copy-target]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-copy-target');
      const el = document.getElementById(id);
      if (!el) return;
      try {
        await navigator.clipboard.writeText(el.value);
        const original = btn.textContent;
        btn.textContent = '✓ Copied';
        btn.disabled = true;
        setTimeout(() => {
          btn.textContent = original;
          btn.disabled = false;
        }, 1800);
      } catch (err) {
        // Fallback for non-clipboard-API browsers
        el.select();
        document.execCommand('copy');
      }
    });
  });

  // mailto: links for infoq and xbrl
  const infoqMailto = document.getElementById('infoq-mailto');
  if (infoqMailto) {
    infoqMailto.href = 'mailto:?subject=' + encodeURIComponent('Story pitch: open-source PDF → JSON financial extraction with a math-identity gate') + '&body=' + encodeURIComponent(COPY['infoq-text']);
  }
  const xbrlMailto = document.getElementById('xbrl-mailto');
  if (xbrlMailto) {
    xbrlMailto.href = 'mailto:?to=' + encodeURIComponent('david.tauriello@xbrl.us') + '&subject=' + encodeURIComponent('qscreen-filing-tool — upstream extractor for the AI Connector MCP server (community contribution)') + '&body=' + encodeURIComponent(COPY['xbrl-text']);
  }
})();
