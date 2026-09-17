# Contributing to qscreen-filing-tool

Thanks for your interest in the engine. This guide covers the **day-to-day**
contribution workflow: setting up a dev environment, running the tests,
adding a bench case, and what we expect from a pull request.

For the *what* (architecture, math-identity gates, jurisdictions) see
[`docs/site/architecture.md`](docs/site/architecture.md) and
[`docs/site/jurisdictions.md`](docs/site/jurisdictions.md). For the
*why*, see [`docs/site/SHOW_HN.md`](docs/site/SHOW_HN.md).

---

## Set up a dev environment

```bash
git clone https://github.com/Mine-FNL/qstocks-filing-tool
cd qstocks-filing-tool
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"            # editable install + pytest + openpyxl
```

Optional extras:

- `.[xlsx]` — Excel transcript export.
- `.[ocr]` — scanned-PDF OCR via rapidocr-onnxruntime (no system deps).
- `.[ocr-tesseract]` — alternative OCR if you already have tesseract.

## Run the test suite

```bash
pytest -q
```

The full offline suite is **480 tests**. CI runs it on Python 3.9, 3.10,
3.11, 3.12, 3.13 — please run at least one of these locally before
opening a PR.

A few sub-suites worth knowing:

```bash
pytest -q tests/test_gates.py          # math-identity gates
pytest -q tests/test_state.py          # SQLite state machine
pytest -q tests/test_eval.py           # golden-set bench
pytest -q tests/test_fingerprint.py    # SHA-256 fingerprints
pytest -q tests/test_autodetect.py     # cover-page classifier
pytest -q tests/test_langdetect.py     # Arabic / English classifier
pytest -q tests/test_app.py            # Flask app + /healthz
```

Before anything else, the offline self-test:

```bash
python -m qscreen_ingest --self-test
```

This validates contract / normalize / merge without any LLM key or
network access. CI runs it as the first step of every matrix cell.

## Run the bench

```bash
python qscreen_eval.py --md                  # pretty-printed
python qscreen_eval.py --json --out /tmp/bench.json
python docs/build_demo.py /tmp/bench.json    # rebuild demo.html
```

The golden-set is hand-verified real QSE filings under `tests/golden/`.
The captured baseline is **100 / 124 (80.6 %)** check-level accuracy —
see [`tests/golden/BASELINE.md`](tests/golden/BASELINE.md) for the
per-case breakdown. The bench is **gating on release** (a regression
refuses to publish) and **non-gating on PR** (a regression shows a
diff in the PR comment).

## Add a new bench case

When you find a filing the engine handles incorrectly (or uniquely),
adding it to the golden set gives the whole project a permanent
regression check for that case.

1. Extract the source text from the PDF — one page per line, UTF-8, no
   headers. Save as `tests/golden/cases/<ticker>_<year>_<period>.txt`.
2. Hand-verify the expected values from the PDF page text (do **not**
   take them from a previous engine run — that's circular). Save as
   `tests/golden/<ticker>_<year>_<period>.json`.
3. Append a row to `tests/golden/BASELINE.md` with the captured
   `<passed>/<total>` count.
4. Register the case in `tests/test_eval.py` (`CASES` / `EXPECTED_DIR`).
5. Open a PR with the title `1.X.0: bench — add <TICKER> <YEAR> <PERIOD>`.

The PR-time bench workflow will run the new case and show the diff in
the PR comment.

## Add a new jurisdiction

See [`docs/site/jurisdictions.md`](docs/site/jurisdictions.md) for the
full contract. The short version:

```bash
mkdir -p profiles/<cc>/data
# write profiles/<cc>/__init__.py with the 5 loader callbacks
# write profiles/<cc>/_seed.py with the taxonomy + ticker map
```

No `pyproject.toml` change is required — setuptools picks up new
`profiles/<id>/` sub-packages automatically.

## Pull request conventions

### PR title

```
1.X.0: <module> <sub-deliverable>
```

`<module>` is one of:

- `engine` — `qscreen_ingest.py` + the inline helpers
- `gates` — `qscreen_gates.py`
- `state` — `qscreen_state.py`
- `eval` — `qscreen_eval.py`
- `autodetect` — `qscreen_autodetect.py`
- `langdetect` — `qscreen_langdetect.py`
- `fingerprint` — `qscreen_fingerprint.py`
- `profile` — `profiles/<jurisdiction>/`
- `bench` — `tests/golden/`
- `app` — `qscreen_app.py` + the Flask surface
- `ci` — `.github/workflows/`
- `docs` — `docs/`, `README.md`, `RUNBOOK.md`, `CHANGELOG.md`
- `repo` — repo-meta (`Makefile`, `.editorconfig`, etc.)

### PR body checklist (template)

The PR template is at `.github/PULL_REQUEST_TEMPLATE.md`. The four
sections are mandatory:

1. **What does this change?** — one paragraph, the why.
2. **Is it behaviorally observable?** — tests + bench score.
3. **Pre-flight** — CI green, CHANGELOG updated, py-modules updated
   if a new module was added.
4. **Risk** — `docs only` / `low` / `medium` / `high`.

## Code review checklist

The PR is reviewable when:

- [ ] `pytest -q` passes locally on at least one Python version.
- [ ] `python -m qscreen_ingest --self-test` is green.
- [ ] `python qscreen_eval.py --md` doesn't regress below the
      captured baseline (or, if it does, the regression is explained
      and a follow-up is filed).
- [ ] `CHANGELOG.md` has an entry under the next-version section.
- [ ] If a new top-level module was added, `pyproject.toml` lists it
      in `[tool.setuptools].py-modules`.
- [ ] The diff is **additive** unless the change explicitly removes a
      deprecated surface (with a note in the PR body).
- [ ] Engine code (`qscreen_*.py`) and the existing `tests/` tree are
      not modified for docs-only or DX-only PRs.

## Communication

- **Bugs and feature requests**: [GitHub Issues][issues].
- **Security disclosures**: see [`SECURITY.md`](SECURITY.md).
- **Code of conduct**: see [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
- **Questions** that don't fit a bug or feature: open a Discussion
  (or a draft PR with the `question` label).

[issues]: https://github.com/Mine-FNL/qstocks-filing-tool/issues

## License

By contributing, you agree that your contributions will be licensed
under the project's [MIT License](LICENSE).
