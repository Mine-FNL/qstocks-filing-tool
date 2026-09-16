"""Stable text fingerprints + cross-filing change-detection.

Why
----
When the cron `llm-ingest-monitor` re-extracts a filing, "did anything
change?" is the question that matters. The merged filing JSON has every
figure, but it doesn't tell you whether the auditor's opinion paragraph
was rephrased, whether a footnote was added, or whether a comparison
year was inserted. Operationally you'd have to byte-diff two JSONs and
eyeball where the wording moved.

This module pins stable fingerprints on every per-statement
``verbatim_text`` block + the auditor's ``verbatim_text``. Two filings
of the same PDF run through different models + different runs of the
same model will produce identical content (modulo whitespace) and
therefore identical fingerprints. Re-extractions that change the wording
of any block produce a different fingerprint for that block. No more
guessing.

Two pieces of public API:

    text_fingerprint(text)         -> str      # 16-char hex digest
    fingerprint_filing(filing)    -> dict     # {"filing_id": "...", "items": [...]}
    diff_fingerprints(prev, cur)   -> dict     # {"added": [...], "removed": [...],
                                          #  "modified": [...], "unchanged": int}

``text_fingerprint`` normalizes whitespace (collapsing arbitrary
whitespace, stripping) so the same text scanned at different PDF
resolutions still hashes the same. It does NOT trim numeric formatting —
"1,000" stays "1,000".

``fingerprint_filing`` is run automatically after each extraction so the
saved JSON carries a ``filing.fingerprint`` block. ``diff_fingerprints``
is exposed as a CLI for inline comparison.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


def text_fingerprint(text: str) -> str:
    """Stable 16-char hex digest of a text block, after whitespace normalization."""
    if not text:
        return ""
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return ""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def fingerprint_filing(filing: dict, *, short_label: str | None = None) -> dict:
    """Compute fingerprints for each per-statement verbatim_text + audit verbatim.

    Returns a dict with stable per-key fingerprints and an overall
    aggregation fingerprint across all items (16 chars; same text ⇒ same hash).
    """
    items: list[dict] = []

    def add(label: str, text: str) -> None:
        """Append an item iff the text contributes a non-empty fingerprint.
        Whitespace-only blocks are skipped (the model often emits '   '
        placeholders; they shouldn't add an item to the diff)."""
        fp = text_fingerprint(text)
        if fp:
            items.append({"key": label, "fingerprint": fp})

    audit = filing.get("audit") or {}
    if isinstance(audit, dict):
        v = audit.get("verbatim_text")
        if isinstance(v, str) and v.strip():
            add("audit.verbatim_text", v)

    for i, st in enumerate(filing.get("statements") or []):
        if not isinstance(st, dict):
            continue
        v = st.get("verbatim_text")
        if isinstance(v, str) and v.strip():
            add(f"statements[{i}].{st.get('type', '?')}.verbatim_text", v)

    for i, note in enumerate(filing.get("notes") or []):
        if not isinstance(note, dict):
            continue
        v = note.get("verbatim_text")
        if isinstance(v, str) and v.strip():
            add(f"notes[{i}].{note.get('category', '?')}.verbatim_text", v)

    # Filing-level aggregation: hash of sorted fingerprints alone (no
    # statement index in the source — the index is a window-chunk
    # artefact that varies between runs of the same PDF). Two filings
    # with the same set of verbatim blocks in any order produce the
    # same overall_fingerprint.
    overall = text_fingerprint(
        "|".join(sorted(item["fingerprint"] for item in items)))

    if short_label is not None:
        filing_id = short_label
    else:
        meta = filing.get("metadata") or {}
        if meta.get("symbol") and meta.get("fiscal_year"):
            filing_id = f"{meta['symbol']}/{meta['fiscal_year']}"
        else:
            filing_id = "<unnamed-filing>"

    return {"filing_id": filing_id,
            "overall_fingerprint": overall,
            "items": items}


def diff_fingerprints(prev: dict | None, current: dict | None) -> dict:
    """Return ``{added, removed, modified, unchanged}``.

    Each list contains statement keys (``audit.verbatim_text`` or
    ``statements[i].<type>.verbatim_text``). Two filings are "modified" on
    a key when both have it but the fingerprints differ. ``unchanged`` is
    the count of keys present in both with identical fingerprints.
    """
    prev_dict = prev if isinstance(prev, dict) else {"items": []}
    cur_dict = current if isinstance(current, dict) else {"items": []}
    prev_items = prev_dict.get("items") or []
    cur_items = cur_dict.get("items") or []
    prev_map = {x["key"]: x["fingerprint"] for x in prev_items}
    cur_map = {x["key"]: x["fingerprint"] for x in cur_items}
    added = sorted(k for k in cur_map if k not in prev_map)
    removed = sorted(k for k in prev_map if k not in cur_map)
    modified = sorted(k for k in cur_map
                       if k in prev_map and prev_map[k] != cur_map[k])
    unchanged_n = sum(1 for k in prev_map
                         if k in cur_map and prev_map[k] == cur_map[k])
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged_n,
        "prev_overall": prev_dict.get("overall_fingerprint"),
        "cur_overall": cur_dict.get("overall_fingerprint"),
        "identical": (prev_map == cur_map and not added and not removed
                       and not modified),
    }


# ── CLI ─────────────────────────────────────────────────────────────────────


def _load_filing(path: str) -> dict:
    p = Path(path)
    j = json.loads(p.read_text(encoding="utf-8"))
    if "fingerprint" in j and isinstance(j["fingerprint"], dict):
        return j["fingerprint"]
    # File without a baked-in fingerprint; build one from the raw filing.
    return fingerprint_filing(j, short_label=p.stem)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Compute / compare filing text fingerprints.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_fpr = sub.add_parser("print", help="Print the fingerprint map for one filing.")
    p_fpr.add_argument("filing", help="Filing JSON")

    p_diff = sub.add_parser("diff", help="Diff fingerprints between two filings.")
    p_diff.add_argument("prev", help="Previous filing JSON")
    p_diff.add_argument("current", help="Current filing JSON")
    p_diff.add_argument("--json", action="store_true",
                          help="Emit JSON instead of console")

    ns = ap.parse_args(argv)
    if ns.cmd == "print":
        fp = _load_filing(ns.filing)
        json.dump(fp, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0
    if ns.cmd == "diff":
        prev = _load_filing(ns.prev)
        cur = _load_filing(ns.current)
        d = diff_fingerprints(prev, cur)
        if ns.json:
            json.dump(d, sys.stdout, indent=2, ensure_ascii=False)
            sys.stdout.write("\n")
        else:
            sys.stdout.write(
                f"identical: {d['identical']}\n"
                f"added:     {len(d['added'])}\n"
                f"removed:   {len(d['removed'])}\n"
                f"modified:  {len(d['modified'])}\n"
                f"unchanged: {d['unchanged']}\n")
            for label, lst in (("+ ADDED", d["added"]),
                                ("- REMOVED", d["removed"]),
                                ("~ MODIFIED", d["modified"])):
                for k in lst:
                    sys.stdout.write(f"  {label:>10s}  {k}\n")
        return 0
    ap.error("unknown subcommand")                 # pragma: no cover
    return 2                                       # pragma: no cover


__all__ = ["text_fingerprint", "fingerprint_filing", "diff_fingerprints"]

if __name__ == "__main__":
    sys.exit(main())
