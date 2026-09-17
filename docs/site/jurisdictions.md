# Jurisdictions (profiles)

A "jurisdiction" is a per-exchange bundle of knowledge: tickers,
sector taxonomy, fiscal calendar, currency, framework timeline,
watch-KPIs, and (optionally) issuer-specific facts.

The engine itself is jurisdiction-agnostic. It loads a profile
through the same API for every exchange. The original QSE data lives
in `profiles/qatar/`; UAE / SA / KW are one directory drop away.

---

## Where profiles live

```
profiles/
├── __init__.py          ← public API (load_profile, register, etc.)
└── <jurisdiction_id>/   ← one directory per exchange
    ├── __init__.py      ← JURISDICTION_NAME + build_profile + ...
    ├── _seed.py         ← tickers, taxonomy, framework timeline
    ├── pre_flags.py     ← (optional) issuer-specific red-flag catalog
    └── data/            ← (optional) per-ticker JSON, one per file
```

A jurisdiction id is a short lowercase code (`qatar`, `uae`, `sa`,
`kw`). It maps to:

- the sub-package name (`profiles.<id>`),
- the `--jurisdiction <id>` flag,
- the `JURISDICTION_NAME` label used in the prompt and the app UI.

## The contract

Every sub-package of `profiles/` must expose:

```python
JURISDICTION_NAME: str        # human-readable, e.g. "Qatar"

def build_profile(ticker: str) -> dict | None:
    """Full static profile for one ticker, or None if unknown."""

def profile_for_year(ticker: str, year: int | None) -> dict | None:
    """Profile resolved AS OF a fiscal year (framework timeline, etc.)."""

def taxonomy() -> dict:
    """Sector → sub-sector → archetype tree."""

def symbol_subsector() -> dict:
    """{ticker: sub_sector} map."""

def subsector_to_archetype() -> dict:
    """{sub_sector: archetype} cross-walk. Archetypes are one of
    conventional_bank | islamic_bank | industrial | insurance | other."""
```

A profile dict has the shape documented in `profiles/__init__.py`
(see the top-of-file docstring):

```python
{
    ticker: str,
    company_name: str,
    jurisdiction: str,
    names: [{name, from, to}, ...],
    sub_sector: str,
    archetype: str,
    fiscal_year_end: "MM-DD",
    reporting_currency: str,           # ISO 4217
    framework_timeline: [{framework, from}, ...],
    watch_kpis: ["KPI_*", ...],
    segments_expected: {"by_geography": [...], "by_business": [...]},
    subsidiaries: [{name, country, currency, from, to}, ...],
    events: [{year, type, title, effect}, ...],
    peers: [ticker, ...],
    accounting_quirks: [str, ...],
}
```

Plus, when `profile_for_year` resolves the dict:

```python
    as_of_year: int | None,
    name_as_of: str,
    framework_as_of: str,
    active_subsidiaries: [...],
    active_currencies: [str, ...],
    active_events: [...],
```

## Drop in a new jurisdiction

The shortest path from zero to a working UAE profile:

### 1. Create the directory

```bash
mkdir -p profiles/uae/data
touch profiles/uae/__init__.py
```

### 2. Write the loader

`profiles/uae/__init__.py`:

```python
"""United Arab Emirates (ADX/DFM) per-stock knowledge base."""
from __future__ import annotations

from . import _seed

JURISDICTION_NAME = "United Arab Emirates"

def build_profile(ticker: str):
    seed = _seed.AUAJ_TAXONOMY.get(ticker.strip().upper())
    if not seed:
        return None
    return {
        "ticker": ticker.strip().upper(),
        "company_name": seed["company_name"],
        "jurisdiction": JURISDICTION_NAME,
        "names": seed.get("names", []),
        "sub_sector": seed["sub_sector"],
        "archetype": _seed.SUBSECTOR_TO_ARCHETYPE[seed["sub_sector"]],
        "fiscal_year_end": "12-31",
        "reporting_currency": "AED",
        "framework_timeline": [{"framework": "IFRS", "from": None}],
        "watch_kpis": seed.get("watch_kpis", []),
        "segments_expected": seed.get("segments_expected", {}),
        "subsidiaries": seed.get("subsidiaries", []),
        "events": seed.get("events", []),
        "peers": seed.get("peers", []),
        "accounting_quirks": seed.get("accounting_quirks", []),
    }

def profile_for_year(ticker, year):
    p = build_profile(ticker)
    if not p:
        return None
    p["as_of_year"] = year
    p["name_as_of"] = p["company_name"]
    p["framework_as_of"] = "IFRS"
    p["active_subsidiaries"] = list(p["subsidiaries"])
    p["active_currencies"] = [p["reporting_currency"]]
    p["active_events"] = [e for e in p["events"] if year is None or e["year"] <= year]
    return p

def taxonomy():
    return _seed.AUAJ_TAXONOMY

def symbol_subsector():
    return {t: s["sub_sector"] for t, s in _seed.AUAJ_TAXONOMY.items()}

def subsector_to_archetype():
    return _seed.SUBSECTOR_TO_ARCHETYPE
```

### 3. Write the seed

`profiles/uae/_seed.py` is the same shape as `profiles/qatar/_seed.py`:

- The taxonomy tree (`sector → sub_sector → archetype`).
- A per-ticker dict (`AUAJ_TAXONOMY: dict[ticker, profile_seed]`).
- A `SUBSECTOR_TO_ARCHETYPE` cross-walk.
- (Optional) `COMPANY_NAMES`, `ENRICH`, `WATCH_KPIS`.

For a first cut, even 5 tickers is enough — the engine works with
whatever is registered. Empty directories are skipped at import time
(`profiles/__init__.py:all_jurisdictions` filters for the
`JURISDICTION_NAME` symbol).

### 4. Register the package in `pyproject.toml`

The setuptools `packages = ["qatar", "profiles"]` line in
`pyproject.toml` already picks up any `profiles/<id>/` sub-package
automatically — **no edit needed**. New jurisdictions just work.

### 5. (Optional) Add a pre-flag catalog

If you have issuer-specific facts that the engine should emit as
`red_flags[]`, copy `profiles/qatar/pre_flags.py` and adapt:

```python
from profiles.qatar.pre_flags import Rule, RedFlag  # or define your own

RULES = [
    Rule(
        rule_id="auh_qualified_baseline",
        applies=lambda f, **_: f["metadata"]["ticker"] in {"AUH", "DIB"} and f["metadata"]["fiscal_year"] >= 2018,
        evaluate=lambda f: any(
            "qualified" in (f.get("audit", {}) or {}).get("opinion_text", "").lower()
            for _ in [None]
        ),
        severity="warn",
        message="AUH/DIB issuer-specific: qualified opinion observed",
        evidence_keys=["audit.opinion_text"],
    ),
]
```

The cross-cutting rules (govt-receivable, intangibles, ROE<Ke, etc.)
are issuer-agnostic and live in `qscreen_gates.py`; you don't need to
copy them.

### 6. Verify

```bash
# The new jurisdiction should appear in the list
python -c "from profiles import all_jurisdictions; print(all_jurisdictions())"

# The new ticker should resolve
python -c "from profiles import load_profile; p = load_profile('AUH', 'uae'); print(p)"
```

Then:

```bash
qscreen-ingest path/to/AUH_AR_2023.pdf --jurisdiction uae --symbol AUH --year 2023
```

### 7. Open a PR

PR title conventions:

```
1.X.0: profile <jurisdiction> — <N> tickers + <M> issuer-specific facts
```

The bench won't run against the new jurisdiction by default (the
golden set is Qatar-only), but the engine-level unit tests will
catch import errors and broken contract.

## Runtime registration

If you can't ship a sub-package (proprietary ticker list, regulatory
constraint), you can register a jurisdiction in-process:

```python
from profiles import register, Jurisdiction, JurisdictionLoader

register("internal", Jurisdiction(
    jurisdiction_id="internal",
    name="Internal",
    loader=JurisdictionLoader(
        build_profile=my_build_profile,
        profile_for_year=my_profile_for_year,
        taxonomy=lambda: MY_TAXONOMY,
        symbol_subsector=lambda: MY_SYMBOL_SUBSECTOR,
        subsector_to_archetype=lambda: MY_SUBSECTOR_TO_ARCHETYPE,
    ),
))
```

The Flask app does this for its embedded bundle on startup. The
contract is identical to the sub-package form.

## Why this design

- **One canonical API** for every exchange — the engine doesn't know
  or care which jurisdiction is loaded.
- **No engine changes** for new exchanges — drop a directory, write
  the contract, ship.
- **Back-compat preserved** — `import qatar` still works because the
  top-level `qatar/` package is a shim that re-exports
  `profiles.qatar`.
- **Issuer-specific knowledge is co-located** — pre-flag rules live
  next to the taxonomy they describe, not in a separate "global
  rules" file that nobody can navigate.

## Next

- → [Architecture](architecture.md): data flow + gates.
- → [Bench](bench.md): the regression harness.
