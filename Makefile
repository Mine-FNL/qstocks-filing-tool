# qscreen-filing-tool — repo-level developer entry point.
#
# Every target maps to a real command in this repo. Run `make help`
# (the default) to see what's available.
#
# Conventions:
#   - All targets are .PHONY (no file dependencies; always re-runs).
#   - Variables at the top are the only knobs you'd reasonably tweak.
#   - Engine code (qscreen_*.py) is never modified by `make` — these
#     targets operate on tests, docs, packaging, and CI surface.

# ---- knobs ----------------------------------------------------------------

PYTHON       ?= python3
PIP          ?= $(PYTHON) -m pip
PKG          := qscreen-filing-tool
EXTRAS_DEV   := .[dev]
EXTRAS_FULL  := .[dev,xlsx,ocr]
PORT         ?= 8765
DOCS_PORT    ?= 8000

# ---- meta -----------------------------------------------------------------

.PHONY: help
help:                       ## Show this help (default target)
	@echo "qscreen-filing-tool — make targets"
	@echo
	@awk 'BEGIN {FS = ":.*##"; printf "  \033[36m%-15s\033[0m %s\n", "target", "what it does"} \
	/^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } \
	/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' \
	$(MAKEFILE_LIST)
	@echo
	@echo "Variables: PYTHON=$(PYTHON), PIP=$(PIP), PORT=$(PORT), DOCS_PORT=$(DOCS_PORT)"

.DEFAULT_GOAL := help

# ---- install --------------------------------------------------------------

.PHONY: install
install:                    ## Install the package (runtime deps only)
	$(PIP) install $(PKG)

.PHONY: install-dev
install-dev:                ## Install editable + dev extras (pytest + openpyxl)
	$(PIP) install -e "$(EXTRAS_DEV)"

.PHONY: install-full
install-full:               ## Install editable + dev + xlsx + ocr
	$(PIP) install -e "$(EXTRAS_FULL)"

# ---- test -----------------------------------------------------------------

.PHONY: test
test:                       ## Run the full offline test suite (pytest -q)
	pytest -q

.PHONY: test-self
test-self:                  ## Offline engine self-test (no key required)
	$(PYTHON) -m qscreen_ingest --self-test

.PHONY: test-one
test-one:                   ## Run a single test (use FILE=tests/test_gates.py::test_x)
	pytest -q $(FILE)

# ---- bench ----------------------------------------------------------------

.PHONY: bench
bench:                      ## Run the golden-set bench (markdown report)
	$(PYTHON) qscreen_eval.py --md

.PHONY: bench-json
bench-json:                 ## Run the bench and emit JSON to /tmp/bench.json
	$(PYTHON) qscreen_eval.py --json --out /tmp/bench.json

.PHONY: bench-demo
bench-demo: bench-json      ## Rebuild docs/demo.html from the bench JSON
	$(PYTHON) docs/build_demo.py /tmp/bench.json

# ---- app ------------------------------------------------------------------

.PHONY: app
app:                        ## Run the Flask app on PORT (default 8765)
	QSCREEN_APP_HOST=127.0.0.1 QSCREEN_APP_PORT=$(PORT) $(PYTHON) -m qscreen_app

.PHONY: healthz
healthz:                    ## Curl /healthz on a running app on PORT
	curl -fsS http://127.0.0.1:$(PORT)/healthz | $(PYTHON) -m json.tool

# ---- lint / format --------------------------------------------------------

.PHONY: lint
lint:                       ## Static syntax check (compileall, no behaviour change)
	$(PYTHON) -m compileall -q qscreen_ingest.py qscreen_app.py profiles qatar tests || true

.PHONY: format
format:                     ## Alias for the bench demo page refresh (DX)
	@echo "No formatter configured — see CONTRIBUTING.md for the style."
	@echo "Engine modules are intentionally hand-formatted; not auto-formatted."

# ---- clean ----------------------------------------------------------------

.PHONY: clean
clean:                      ## Remove build artifacts (site/, build/, dist/, *.egg-info/)
	rm -rf site build dist
	rm -rf *.egg-info qscreen_filing_tool.egg-info
	rm -rf .mypy_cache .ruff_cache .pytest_cache
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	find . -name '*.pyc' -delete

# ---- package / publish ----------------------------------------------------

.PHONY: build
build:                      ## Build sdist + wheel into dist/
	$(PYTHON) -m pip install --upgrade build
	$(PYTHON) -m build

.PHONY: publish-test
publish-test:               ## Upload the wheel to TestPyPI (manual; needs a token)
	$(PYTHON) -m pip install --upgrade twine
	$(PYTHON) -m twine upload --repository testpypi dist/*

# ---- docs -----------------------------------------------------------------

.PHONY: docs
docs:                       ## Build the mkdocs site into ./site (--strict)
	$(PYTHON) -m pip install --upgrade mkdocs mkdocs-material
	$(PYTHON) -m mkdocs build --strict

.PHONY: docs-serve
docs-serve:                 ## Serve the mkdocs site on DOCS_PORT (live reload)
	$(PYTHON) -m pip install --upgrade mkdocs mkdocs-material
	$(PYTHON) -m mkdocs serve -a 127.0.0.1:$(DOCS_PORT)

# ---- end ------------------------------------------------------------------

# Each section uses the `## ` (target) / `##@ ` (group) markers consumed by
# the awk script in `help`. Add new targets under the section header that
# matches their purpose and they will appear in `make help` automatically.