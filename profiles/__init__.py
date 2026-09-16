"""Jurisdiction-pluggable per-stock knowledge base.

Public API (jurisdiction-agnostic):
    all_jurisdictions()         -> sorted list of installed jurisdictions
                                   (e.g. ["qatar"], or whatever sub-packages exist)
    default_jurisdiction()       -> the jurisdiction used when none is set
                                   ("qatar" when the bundled data is present, else None)
    load_profile(ticker,         -> full static profile, or None if unknown
                  jurisdiction=None)
    profile_for_year(ticker,    -> profile resolved as of a fiscal year
                       year,
                       jurisdiction=None)
    taxonomy(jurisdiction=None)  -> sector -> sub-sector -> archetype tree
    symbol_subsector(jurisdiction=None) -> {ticker: sub_sector}
    subsector_to_archetype(jurisdiction=None) -> {sub_sector: archetype}
    register(jurisdiction,       -> register a new jurisdiction at runtime
             loader)
    export_json(jurisdiction=None, directory=None) -> write profile JSONs

A "jurisdiction" is a sub-package of ``profiles/`` (e.g. ``profiles/qatar/``)
that exposes ``build_profile``, ``profile_for_year``, ``taxonomy``,
``symbol_subsector``, ``subsector_to_archetype`` and a ``JURISDICTION_NAME``
constant. The Qatar sub-package ships in-tree; new ones (e.g. ``profiles/uae/``)
can be added by dropping a directory next to it.

Profile shape (one dict per ticker) — see profiles/qatar/_seed.py for the
full Qatar data; the contract is:

    {
      ticker: str,
      company_name: str,
      jurisdiction: str,                # NEW: "Qatar", "United Arab Emirates", ...
      names: [{name, from, to}, ...],
      sub_sector: str,
      archetype: str,                   # conventional_bank | islamic_bank |
                                        # industrial | insurance | other
      fiscal_year_end: "MM-DD",
      reporting_currency: str,          # ISO 4217 (QAR, AED, SAR, USD, ...)
      framework_timeline: [{framework, from}, ...],
      watch_kpis: ["KPI_*", ...],
      segments_expected: {"by_geography": [...], "by_business": [...]},
      subsidiaries: [{name, country, currency, from, to}, ...],
      events: [{year, type, title, effect}, ...],
      peers: [ticker, ...],
      accounting_quirks: [str, ...],
      # Resolved-at-year view (added by profile_for_year):
      as_of_year: int | None,
      name_as_of: str,
      framework_as_of: str,
      active_subsidiaries: [...],
      active_currencies: [str, ...],
      active_events: [...],
    }
"""
from __future__ import annotations

import importlib
import json
import pkgutil
from pathlib import Path
from typing import Callable, Optional

# The tool was originally authored for QSE. We default to "qatar" when its
# sub-package is present and there is no other jurisdiction registered, so
# existing commands keep working out of the box.
_PREFERRED_JURISDICTION = "qatar"


# A registry lets an embedder (Flask app, custom CLI) add a jurisdiction
# without dropping a sub-package on disk. Keyed by jurisdiction id (lowercase).
_REGISTRY: dict[str, "Jurisdiction"] = {}


class Jurisdiction:
    """A jurisdiction is a fat bundle: data + loader functions + a human name.

    A jurisdiction can either come from a ``profiles/<id>/`` sub-package, or be
    registered in-process via :func:`register`. Both feed the same API.
    """

    def __init__(self, jurisdiction_id: str, name: str, loader: "JurisdictionLoader"):
        self.id = jurisdiction_id
        self.name = name                    # human-readable: "Qatar"
        self.loader = loader                # .build_profile / .profile_for_year / taxonomy / ...


class JurisdictionLoader:
    """Five callbacks that every jurisdiction must expose.

    The defaults below just signal that the jurisdiction is broken / incomplete,
    so a missing-piece error is clear rather than a generic AttributeError.
    """

    def __init__(
        self,
        build_profile: Callable[[str], Optional[dict]],
        profile_for_year: Callable[[str, "int | None"], Optional[dict]],
        taxonomy: Callable[[], dict],
        symbol_subsector: Callable[[], dict],
        subsector_to_archetype: Callable[[], dict],
        export_json: Optional[Callable[["Path | None"], int]] = None,
    ):
        self.build_profile = build_profile
        self.profile_for_year = profile_for_year
        self._taxonomy = taxonomy
        self._symbol_subsector = symbol_subsector
        self._subsector_to_archetype = subsector_to_archetype
        self.export_json = export_json or (lambda d: 0)


def register(jurisdiction_id: str, name: str, loader: JurisdictionLoader) -> None:
    """Register a jurisdiction at runtime (alternative to dropping a sub-package)."""
    if not jurisdiction_id or not jurisdiction_id.replace("_", "").isalnum():
        raise ValueError(f"invalid jurisdiction id: {jurisdiction_id!r}")
    _REGISTRY[jurisdiction_id.lower()] = Jurisdiction(jurisdiction_id.lower(), name, loader)


def _load_subpackage(jurisdiction_id: str) -> Jurisdiction | None:
    """Try to import ``profiles.<id>`` and wrap it as a Jurisdiction."""
    try:
        mod = importlib.import_module(f"profiles.{jurisdiction_id}")
    except Exception:
        return None
    if not hasattr(mod, "JURISDICTION_NAME"):
        return None
    loader = JurisdictionLoader(
        build_profile=getattr(mod, "build_profile", lambda t: None),
        profile_for_year=getattr(mod, "profile_for_year", lambda t, y: None),
        taxonomy=getattr(mod, "taxonomy", lambda: {}),
        symbol_subsector=getattr(mod, "symbol_subsector", lambda: {}),
        subsector_to_archetype=getattr(mod, "subsector_to_archetype", lambda: {}),
        export_json=getattr(mod, "export_json", None),
    )
    return Jurisdiction(
        jurisdiction_id=jurisdiction_id,
        name=getattr(mod, "JURISDICTION_NAME"),
        loader=loader,
    )


def all_jurisdictions() -> list[str]:
    """Sorted list of installed jurisdictions (sub-packages + registered)."""
    found = set(_REGISTRY)
    pkg_path = Path(__file__).resolve().parent
    for info in pkgutil.iter_modules([str(pkg_path)]):
        if info.name in found:
            continue
        # Only count sub-packages that look like a jurisdiction (have JURISDICTION_NAME)
        try:
            if hasattr(importlib.import_module(f"profiles.{info.name}"), "JURISDICTION_NAME"):
                found.add(info.name)
        except Exception:
            continue
    return sorted(found)


def _get(jurisdiction: str | None) -> Jurisdiction | None:
    """Resolve a Jurisdiction by id, trying the registry then the sub-package."""
    if jurisdiction is None:
        jurisdiction = default_jurisdiction()
    if jurisdiction is None:
        return None
    jid = jurisdiction.strip().lower()
    if not jid:
        return None
    if jid in _REGISTRY:
        return _REGISTRY[jid]
    j = _load_subpackage(jid)
    if j is None:
        return None
    _REGISTRY[jid] = j          # cache so subsequent lookups skip the import dance
    return j


def default_jurisdiction() -> str | None:
    """The jurisdiction used when none is given. Prefers 'qatar' when its
    sub-package is bundled, else the first registered/available one."""
    for cand in (_PREFERRED_JURISDICTION, *(sorted(_REGISTRY))):
        if _load_subpackage(cand) is not None or cand in _REGISTRY:
            return cand
    return next(iter(all_jurisdictions()), None)


def load_profile(ticker: str, jurisdiction: str | None = None) -> dict | None:
    j = _get(jurisdiction)
    if j is None:
        return None
    p = j.loader.build_profile(ticker.strip().upper())
    if not p:
        return None
    # Guarantee a `jurisdiction` field even if the loader omits it.
    p.setdefault("jurisdiction", j.name)
    return p


def profile_for_year(ticker: str, year: int | None,
                     jurisdiction: str | None = None) -> dict | None:
    j = _get(jurisdiction)
    if j is None:
        return None
    p = j.loader.profile_for_year(ticker.strip().upper(), year)
    if not p:
        return None
    p.setdefault("jurisdiction", j.name)
    return p


def taxonomy(jurisdiction: str | None = None) -> dict:
    j = _get(jurisdiction)
    return j.loader._taxonomy() if j else {}


def symbol_subsector(jurisdiction: str | None = None) -> dict:
    j = _get(jurisdiction)
    return j.loader._symbol_subsector() if j else {}


def subsector_to_archetype(jurisdiction: str | None = None) -> dict:
    j = _get(jurisdiction)
    return j.loader._subsector_to_archetype() if j else {}


def export_json(jurisdiction: str | None = None,
                directory: "str | Path | None" = None) -> int:
    """Write per-ticker profile JSONs to disk (inspectable artifacts)."""
    j = _get(jurisdiction)
    if j is None or j.loader.export_json is None:
        return 0
    if directory is None:
        directory = Path(__file__).resolve().parent / (j.id) / "data"
    return j.loader.export_json(Path(directory))


__all__ = [
    "Jurisdiction", "JurisdictionLoader",
    "register", "all_jurisdictions", "default_jurisdiction",
    "load_profile", "profile_for_year",
    "taxonomy", "symbol_subsector", "subsector_to_archetype",
    "export_json",
]
