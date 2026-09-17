# RUNBOOK — your first real extraction

A copy-paste guide to take one QSE filing PDF all the way to uploadable JSON and
analyst-ready outputs. Everything except the LLM extraction call runs offline; this
guide covers the one step that needs a provider key.

---

## 1. Install (once)

```bash
git clone https://github.com/0xBingBong69/qscreen-filing-tool.git
cd qscreen-filing-tool
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[xlsx,ocr]"      # xlsx = Excel transcript; ocr = scanned PDFs
```

Verify the engine without any key (should print ✅):

```bash
python3 qscreen_ingest.py --self-test
pytest -q                          # full offline suite
```

## 2. Configure a provider key (once)

```bash
cp .env.example .env               # then edit .env and paste ONE key
python3 qscreen_ingest.py --list-providers     # see options + which key is detected
set -a; . ./.env; set +a           # load it into the shell (bash/zsh)
```

You only need **one** of `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`,
`MINIMAX_API_KEY`, or `MOONSHOT_API_KEY`. The tool auto-detects whichever is set; force
one with `--provider` or `QSCREEN_PROVIDER`. `INGEST_TOKEN` is **optional** — needed only
to upload to qscreen.app; without it the tool just saves locally.

## 3. The one command — PDF → everything

```bash
python3 qscreen_ingest.py path/to/QNB_AR_2023.pdf \
  --symbol QNBK --sector islamic_bank --year 2023 --period FY \
  --dry-run \
  --export xlsx --export html --export csv \
  --analyze --report --price 16 --shares 9200000000
```

This produces, in the current directory:

| File | What |
|---|---|
| `QNBK_2023_FY_filing.json` | the **qscreen.app-uploadable** document |
| `QNBK_2023_FY_filing.xlsx` | the **Excel transcript** (Summary + statements + multi-year grid) |
| `QNBK_2023_FY_statements.html` | the printable **statements document** |
| `QNBK_2023_FY_filing.csv` | flat line-items table |
| `QNBK_2023_FY_analysis.json` / `_valuation.json` | ratios, red flags, DCF |
| `QNBK_2023_FY_report.html` / `.md` | the one-page **analyst report** (with charts) |

`--dry-run` extracts and writes everything **without** uploading — always do your first
run this way and inspect the JSON.

`--sector` is one of `conventional_bank | islamic_bank | industrial | insurance | other`.
`--period` is `FY | Q1 | Q2 | Q3 | Q4 | H1 | 9M`.

## 4. Verify the extraction

Open `QNBK_2023_FY_statements.html` in a browser (fastest sanity check) and skim the
`*_filing.json`:

- The run prints any **contract problems**; a non-conforming extract is saved but **never
  uploaded** (exit code 2). Fix prompts/inputs and re-run.
- Check `extraction_quality` and that headline figures match the PDF.
- Scanned PDF (figures missing / empty pages)? Add `--ocr always` (needs the `ocr` extra
  plus system `tesseract` + `poppler`).
- Wrong/zero numbers? Try `--no-json-mode` (some providers reject JSON mode), a larger
  `--max-tokens`, or a different `--provider`/`--model`.

## 5. Upload (when the JSON looks right)

```bash
# drop --dry-run and ensure INGEST_TOKEN is set:
python3 qscreen_ingest.py path/to/QNB_AR_2023.pdf \
  --symbol QNBK --sector islamic_bank --year 2023 --with-analysis
```

`--with-analysis` folds the computed analysis into the upload payload. Or upload an
already-saved filing from the browser app (Option A in the README).

## 6. Multiple years / quarters

```bash
# extract a few years (repeat step 3 per PDF), then combine:
python3 qscreen_workbook.py QNBK_2021_FY_filing.json QNBK_2022_FY_filing.json QNBK_2023_FY_filing.json
python3 qscreen_report.py   --symbol QNBK QNBK_2022_FY_filing.json QNBK_2023_FY_filing.json --price 16 --shares 9.2e9
python3 qscreen_periods.py  QNBK_2023_9M_filing.json QNBK_2023_FY_filing.json QNBK_2024_9M_filing.json   # TTM
```

## Batch mode

```bash
# manifest.csv:  pdf,symbol,sector,year[,period]
python3 qscreen_ingest.py --manifest manifest.csv --dry-run --export xlsx --analyze
```

---

If a real run surfaces something the offline tests don't cover (a provider quirk, an
unusual statement layout, a number that lands wrong), capture the command + the printed
problems and the relevant PDF page — that's exactly the signal needed to tune the
extraction prompt.

---

## Appendix: PyPI Trusted Publisher setup (one-time, maintainer only)

The repo ships a `publish.yml` workflow that publishes to PyPI with
**no API token** — it uses [PyPI Trusted Publishers][tp] (PEP 740 / OIDC).
The maintainer does this once on PyPI's side; from then on every
`v*` tag push is a no-secret publish.

[tp]: https://docs.pypi.org/trusted-publishers/

### Steps

1. Go to **<https://pypi.org/manage/account/publishing/>** while signed
   in as the project's owner.
2. Under **"Pending publishers"**, click **"Add a new pending publisher"**
   and fill in:
   - **PyPI Project Name**: `qscreen-filing-tool`
   - **Owner**: `Mine-FNL`
   - **Repository name**: `qstocks-filing-tool`
   - **Workflow filename**: `publish.yml`
   - **Environment name**: *(leave blank — uses default)*
3. Click **Add**. PyPI shows a confirmation; the publisher is now
   "pending" until the first successful publish.
4. From the repo, push a `v*` tag (or run **Actions → publish →
   Run workflow**) to fire the publish. The workflow uses GitHub's OIDC
   identity; PyPI matches it against the pending publisher and
   promotes it to "real" on the first successful publish.

That's it. There is no token to mint, rotate, or burn. Subsequent
releases re-use the same workflow.

### Failure modes

- *"project not found on PyPI"* — PyPI requires the project name to be
  reserved. The first publish *is* the one that reserves it. PyPI's
  pending publisher must therefore be registered before the first
  workflow run; if you see this error, register it (steps above) and
  re-run the workflow.
- *"OIDC: no matching pending publisher"* — the owner / repo /
  workflow filename tuple doesn't match. Re-check the values on
  <https://pypi.org/manage/account/publishing/> match this repo's path
  and `.github/workflows/publish.yml` exactly.
