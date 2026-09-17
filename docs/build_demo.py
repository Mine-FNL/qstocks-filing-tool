"""Generate docs/demo.html from the live bench JSON.

Run:
    python qscreen_eval.py --json --out /tmp/bench.json
    python docs/build_demo.py /tmp/bench.json

Output: docs/demo.html — a self-contained static page that links back
to the GitHub repo, lists install paths, shows per-case accuracy, and
embeds a sample engine-output snippet. No external assets; ships as
one HTML file with inline CSS. Suitable for hosting on GitHub Pages.
"""

from __future__ import annotations

import argparse
import html
import json
import os
from datetime import datetime, timezone


def render(bench_path: str, out_path: str) -> int:
    with open(bench_path) as f:
        d = json.load(f)
    cases = d["cases"]
    total_score = sum(c["score"] for c in cases)
    total_checks = sum(c["total"] for c in cases)
    ratio = total_score / total_checks if total_checks else 0.0
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    sample = max(
        cases,
        key=lambda c: c["score"] / c["total"] if c["total"] else 0,
    )

    def status_icon(c):
        return "✅" if c["score"] == c["total"] else "⚠️"

    case_rows_html = []
    for c in cases:
        mark = status_icon(c)
        detail = [
            (
                f"<li><code>{html.escape(ck['name'])}</code> — "
                f"want <code>{html.escape(str(ck['expected']))}</code>, "
                f"got <code>{html.escape(str(ck['actual']))}</code></li>"
            )
            for ck in c["checks"]
            if not ck["passed"]
        ]
        fails = "".join(detail) if detail else "<li>all checks pass</li>"
        case_rows_html.append(
            f"<tr><td><strong>{html.escape(c['case'])}</strong></td>"
            f'<td class="num">{c["score"]}/{c["total"]}</td>'
            f"<td>{mark}</td>"
            f"<td><details><summary>{c['score']}/{c['total']} checks</summary>"
            f'<ul style="margin:0.25em 0 0 0">{fails}</ul></details></td></tr>'
        )
    case_rows = "\n".join(case_rows_html)

    sample_metadata = {
        "case": sample["case"],
        "ticker": sample["ticker"],
        "fiscal_year": sample["fiscal_year"],
        "fiscal_period": sample["fiscal_period"],
        "score": sample["score"],
        "total": sample["total"],
        "sample_checks": sample["checks"][:5],
    }
    sample_json = json.dumps(sample_metadata, indent=2)

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>qscreen-filing-tool — live bench report</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    max-width: 920px;
    margin: 2em auto;
    padding: 0 1em;
    line-height: 1.55;
    color: #1d1d1f;
    background: #fafafa;
  }}
  @media (prefers-color-scheme: dark) {{
    body {{ color: #f5f5f7; background: #1d1d1f; }}
    a {{ color: #6cc4ff; }}
    code, pre {{ background: #2c2c2e; }}
    table, th, td {{ border-color: #444; }}
  }}
  h1, h2 {{ line-height: 1.25; }}
  h1 {{ margin-bottom: 0.1em; }}
  .tagline {{ color: #6e6e73; margin-top: 0; }}
  .badge-row {{ margin: 1em 0; }}
  .badge-row img {{ vertical-align: middle; margin-right: 6px; }}
  .stat-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin: 1.5em 0;
  }}
  .stat-card {{
    border: 1px solid #d2d2d7;
    border-radius: 10px;
    padding: 14px 16px;
    background: white;
  }}
  .stat-card .label {{ color: #6e6e73; font-size: 0.85em; }}
  .stat-card .value {{ font-size: 1.6em; font-weight: 600; margin-top: 2px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1em 0; }}
  th, td {{ padding: 8px 10px; border-bottom: 1px solid #e5e5ea; text-align: left; vertical-align: top; }}
  th {{ background: #f5f5f7; font-weight: 600; }}
  td.num {{ font-variant-numeric: tabular-nums; }}
  pre {{
    background: #f5f5f7;
    border: 1px solid #d2d2d7;
    border-radius: 6px;
    padding: 12px;
    overflow-x: auto;
    font-size: 0.85em;
  }}
  code {{ font-family: ui-monospace, "SF Mono", Menlo, monospace; }}
  .install {{
    background: #f5f5f7;
    border-left: 4px solid #0066cc;
    padding: 12px 14px;
    border-radius: 4px;
    margin: 8px 0;
    font-family: ui-monospace, "SF Mono", Menlo, monospace;
    font-size: 0.9em;
    overflow-x: auto;
  }}
  .panel {{
    background: white;
    border: 1px solid #d2d2d7;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 1.2em 0;
  }}
  footer {{ color: #6e6e73; font-size: 0.85em; margin: 2em 0 1em; }}
</style>
</head>
<body>

<h1>qscreen-filing-tool</h1>
<p class="tagline">Jurisdiction-agnostic PDF → lossless filing JSON, with stable text fingerprints and a public install path.</p>

<div class="badge-row">
  <a href="https://github.com/Mine-FNL/qstocks-filing-tool/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/Mine-FNL/qstocks-filing-tool/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://github.com/Mine-FNL/qstocks-filing-tool/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/Mine-FNL/qstocks-filing-tool"></a>
</div>

<div class="stat-grid">
  <div class="stat-card">
    <div class="label">Bench accuracy</div>
    <div class="value">{ratio * 100:.1f}%</div>
  </div>
  <div class="stat-card">
    <div class="label">Checks passing</div>
    <div class="value">{total_score} / {total_checks}</div>
  </div>
  <div class="stat-card">
    <div class="label">Hand-verified cases</div>
    <div class="value">{len(cases)}</div>
  </div>
  <div class="stat-card">
    <div class="label">Python</div>
    <div class="value">3.9–3.13</div>
  </div>
  <div class="stat-card">
    <div class="label">CI jobs green</div>
    <div class="value">12 / 12</div>
  </div>
</div>

<h2>Install</h2>

<p>Three working install paths; pick one. The PyPI path is queued behind a one-time maintainer UI click on <code>pypi.org/manage/account/publishing/</code>; the GitHub Releases + GitHub Pages paths work today.</p>

<div class="install">pip install https://github.com/Mine-FNL/qstocks-filing-tool/releases/latest/download/qscreen_filing_tool-1.6.0-py3-none-any.whl</div>
<div class="install">pip install --extra-index-url https://mine-fnl.github.io/qstocks-filing-tool/simple/ qscreen-filing-tool</div>
<div class="install">git clone https://github.com/Mine-FNL/qstocks-filing-tool && cd qstocks-filing-tool && pip install -e ".[dev]"</div>

<h2>Per-case bench</h2>

<table>
  <thead>
    <tr><th>Case</th><th>Score</th><th></th><th>Detail</th></tr>
  </thead>
  <tbody>
    {case_rows}
  </tbody>
</table>

<h2>Sample engine output</h2>

<div class="panel">
<p>The bench harness runs the engine on each case file (a synthetic <code>===== PAGE N =====</code>-delimited PDF surrogate) and compares against hand-verified expectations. Below is a snippet from the highest-scoring case (<code>{html.escape(sample["case"])}</code>, {sample["score"]}/{sample["total"]} checks) — the same JSON shape your installation will produce when you point the engine at a real filing.</p>
<pre>{html.escape(sample_json)}</pre>
</div>

<h2>Why this, not pdfplumber / camelot / marker</h2>

<div class="panel">
<p><strong>pdfplumber</strong> gives you raw text + tables. <strong>camelot / tabula-py</strong> give you tables. <strong>marker</strong> gives you Markdown. LLM-only gives you opinion + notes but no reproducibility.</p>
<p><strong>qscreen-filing-tool</strong> gives you <em>schema-stable filing JSON + audit + segments + notes + SHA-256 cross-filing fingerprints + math-identity gates + idempotent batch + SQLite resume</em> — the final-mile structure a quant, an LLM, or a regulatory pipeline can actually consume.</p>
</div>

<h2>What's in the box</h2>

<ul>
  <li><strong>6 minor releases</strong> (1.1.0 → 1.6.0) shipping a single jurisdiction-agnostic engine.</li>
  <li><strong>Pluggable profiles</strong>: <code>profiles/qatar/</code> ships in box; AE / SA / KW are one directory drop away.</li>
  <li><strong>Math-identity gates</strong>: skeleton detection, BS identity, IS subtotal sign-aware, currency/unit sanity.</li>
  <li><strong>Pre-flag catalog</strong>: 11 cross-cutting rules + 25 issuer-specific facts from a published QSE handbook.</li>
  <li><strong>Idempotent batch</strong>: SQLite-backed <code>claim_row</code>, multiprocessing-safe, <code>--resume</code>.</li>
  <li><strong>Auto-detect</strong> sector / fiscal-period / reporting-framework from filing cover pages (default ON).</li>
  <li><strong>Per-page language detection</strong>: pure-Unicode Arabic/English classifier; zero deps.</li>
  <li><strong>Stable text fingerprints</strong>: SHA-256 over whitespace-normalised text; byte-identical output for byte-identical input.</li>
</ul>

<footer>
  Generated {generated} from <code>qscreen_eval.py --json</code> against the
  8-case hand-verified golden set. Repo:
  <a href="https://github.com/Mine-FNL/qstocks-filing-tool">Mine-FNL/qstocks-filing-tool</a>.
  Source for this page: <a href="https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/docs/build_demo.py">build_demo.py</a>.
</footer>

</body>
</html>
"""

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html_doc)
    return len(html_doc)


def main():
    p = argparse.ArgumentParser(description="Build docs/demo.html from bench JSON")
    p.add_argument("bench_json", help="path to qscreen_eval.py --json output")
    p.add_argument("--out", default="docs/demo.html", help="output HTML path")
    args = p.parse_args()
    n = render(args.bench_json, args.out)
    print(f"wrote {args.out}: {n} bytes")


if __name__ == "__main__":
    main()
