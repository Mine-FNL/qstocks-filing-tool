"""Back-compat shim — points at the new ``profiles.qatar`` package.

Originally the tool shipped a top-level ``qatar/`` package. To make the engine
jurisdiction-agnostic that data was moved to ``profiles/qatar/``, and this
module is left in place so any script that does ``import qatar`` or
``from qatar import profile_for_year`` keeps working unchanged.

New code should import from :mod:`profiles`:

    from profiles import load_profile, profile_for_year, default_jurisdiction
    from profiles.qatar import build_profile, taxonomy

The shim transparently re-exports everything in :mod:`profiles.qatar`.

Note: historical ``qatar.export_json()`` callers used to write into
``qatar/profiles/<TICKER>.json``; the data now lives under
``profiles/qatar/data/<TICKER>.json``. The wrapped call honours that by
defaulting to the new path; callers that pass an explicit ``directory=`` get
the path they asked for.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

_qatar = importlib.import_module("profiles.qatar")
# Mirror every public name (incl. JURISDICTION_NAME, taxonomy dicts, helpers).
for _name in getattr(_qatar, "__all__", ()):
    globals()[_name] = getattr(_qatar, _name)


def _shim_export_json(directory=None):
    """Default-write location moved from ``qatar/profiles`` to
    ``profiles/qatar/data`` (where the committed JSONs live now)."""
    if directory is None:
        directory = Path(__file__).resolve().parent.parent / "profiles" / "qatar" / "data"
    return _qatar.export_json(directory)


# Replace the re-exported ``export_json`` with the path-corrected shim.
export_json = _shim_export_json
globals()["export_json"] = _shim_export_json
__all__ = sorted(n for n in globals() if not n.startswith("_"))

# Make ``import qatar._seed`` keep working for the test suite.
sys.modules.setdefault("qatar._seed", importlib.import_module("profiles.qatar._seed"))
