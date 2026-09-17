# CI workflows

Four GitHub Actions workflows wrap the engine. They're designed so
that **a regression in extraction logic can never silently ship** to
PyPI / GitHub Releases / a stranger's `pip install`.

---

## The four workflows

### `ci.yml` — the test matrix

- **Triggers**: every push, every PR.
- **Matrix**: Python 3.9, 3.10, 3.11, 3.12, 3.13.
- **Steps**: `pip install -e ".[dev]"` →
  `python -m qscreen_ingest --self-test` →
  `pytest -q --maxfail=1 --durations=10`.
- **Plus**: a Flask app smoke job (`app-smoke`) that boots the app on
  port 18765 and curls `/healthz` — proves the production surface is
  reachable.
- **Plus**: an informational golden-set bench on every matrix cell (the
  bench JSON is uploaded as an artifact for inspection).

This is the test-only workflow. It never publishes anything.

### `bench.yml` — PR-time + nightly bench gate

- **Triggers**: every PR touching engine files, every push to `main`,
  manual `workflow_dispatch`, **and** a Monday 06:00 UTC cron.
- **Behavior**: runs `qscreen_eval.py` against the golden set and
  posts a summary as a PR comment. Refuses to merge if the bench
  regresses below the captured baseline (80.6 %, 100 / 124).
- **Cron purpose**: silent dependency regressions (a new pdfplumber
  version that subtly changes table extraction, etc.) surface on the
  Actions dashboard within a week.

The bench path filter is narrow by design — only engine modules, the
golden set, and `pyproject.toml`. Docs-only or workflow-only PRs don't
re-trigger it.

### `release.yml` — full automated release pipeline

- **Triggers**: push of a `v*` tag (e.g. `v1.6.0`), or manual
  `workflow_dispatch` (with a `skip_bench` toggle for non-engine
  changes).
- **Pipeline**:
    1. **Bench regression gate** — runs `qscreen_eval.py` and refuses
       to continue if accuracy regresses below the baseline.
    2. **Build** — `python -m build` produces `sdist` + `wheel`.
    3. **Upload to GitHub Releases** — the wheel + sdist become
       release artifacts. The `latest/download/…` URL in the README
       always points here.
    4. **Update gh-pages** — refreshes the PEP 503 `simple/` index
       served at `mine-fnl.github.io/qstocks-filing-tool/simple/`.

- **Permissions**: `contents: write` (release + assets), `pages: write`
  (gh-pages), `id-token: write` (ready for PyPI Trusted Publishers).
- **Concurrency**: `group: release, cancel-in-progress: false`. A
  release in flight is never cancelled — re-running is a manual
  decision.

The same wheel is uploaded to GitHub Releases **and** indexed on
gh-pages, so a stranger's `pip install` either path is consistent.

### `publish.yml` — PyPI publish (Trusted Publishers)

- **Triggers**: push of a `v*` tag, or manual `workflow_dispatch`.
- **Behavior**: builds the wheel and publishes to PyPI via OIDC
  Trusted Publishers (PEP 740). No API token is ever minted, pasted,
  or rotated — the trust relationship is configured one-time on
  PyPI's side (see `RUNBOOK.md` §"PyPI Trusted Publisher setup").
- **Permissions**: `contents: read`, `id-token: write` (the OIDC
  identity token).
- **Status**: pending publisher registration on `pypi.org`. The
  workflow is wired and ready; the first publish promotes it from
  pending to real.

Until the pending publisher is registered, the public install
surface is GitHub Releases + the GitHub Pages `simple/` index — both
of which are already wired and live.

### `docs.yml` — mkdocs site deploy (new in 1.6.0)

- **Triggers**: push to `main` when `docs/site/**`, `mkdocs.yml`,
  `docs/SHOW_HN.md`, or `docs/build_demo.py` changes, plus manual
  `workflow_dispatch`.
- **Behavior**: `pip install mkdocs mkdocs-material` →
  `mkdocs build --strict` → deploy `site/` to `gh-pages` via
  `peaceiris/actions-gh-pages@v3` (`force_orphan: true`).
- **Permissions**: `contents: write`, `pages: write`, `id-token: write`.

The mkdocs site, the `simple/` index, and `docs/demo.html` all live
on the `gh-pages` branch at different paths:

```
mine-fnl.github.io/qstocks-filing-tool/                 ← mkdocs site root
mine-fnl.github.io/qstocks-filing-tool/simple/         ← PEP 503 index (release.yml)
mine-fnl.github.io/qstocks-filing-tool/demo.html        ← live bench report (release.yml)
```

!!! warning "Inter-workflow ordering on `gh-pages`"
    `docs.yml` deploys with `force_orphan: true`, which **replaces** the
    gh-pages branch contents with `site/`. This will remove the
    `simple/` index and `demo.html` last published by `release.yml`.
    They are re-published on the next `v*` tag push (release.yml writes
    `simple/`, `index.html`, and `demo.html` to the same branch). If
    you ever need both to be present **without** an intervening release
    tag, switch `docs.yml` to `force_orphan: false` — the mkdocs build
    and the release.yml artifacts live at disjoint paths and won't
    collide.

## Why the bench gate is the hard one

The bench is the only signal that distinguishes a *passing* engine
from a *working* engine. The test suite proves the contract holds;
the bench proves the contract produces the right answer on a real
PDF. A regression can pass the test suite (e.g. a schema rename that
updates every test) while dropping 20 % on the bench — and only the
bench will catch it.

So the bench is **gating** on release (a regression refuses to publish)
and **non-gating** on PR (a regression shows a diff in the PR comment
but doesn't block merge). The asymmetry is intentional: a regression
on a PR is a learning signal, a regression on a tag is a trust
break.

## Reproducing CI locally

```bash
# CI matrix (one cell)
pip install -e ".[dev]"
python -m qscreen_ingest --self-test
pytest -q

# Bench (one cell)
python qscreen_eval.py --md
python qscreen_eval.py --json --out /tmp/bench.json
python docs/build_demo.py /tmp/bench.json

# App smoke (one cell)
python -m qscreen_app &
APP_PID=$!
for i in $(seq 1 30); do curl -fsS http://127.0.0.1:8765/healthz && break; sleep 1; done
python scripts/ci_healthz_assert.py http://127.0.0.1:8765/healthz
kill $APP_PID

# Docs (one cell)
pip install mkdocs mkdocs-material
python -m mkdocs build --strict
```

The Makefile (at the repo root) wraps these as `make test`,
`make bench`, `make docs`, `make docs-serve`.

## Next

- → [Bench](bench.md): the 80.6 % baseline, what the checks measure.
- → [Architecture](architecture.md): the data flow the workflows gate.
