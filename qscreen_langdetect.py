"""Per-page language detection for QSE filings.

QSE financials come in three flavors:
  * English only       — most modern filings
  * Arabic only        — older filings, government-owned entities
  * Bilingual          — Arabic + English in the same PDF, often two side-by-side cols

The schema today has ``metadata.language`` (a single string) and is left as
``None`` in every filing because nothing populates it. Bilingual filings need
``metadata.languages = [{code, ratio, primary}]``.

This module makes the language-tag accurate WITHOUT adding any deps. It
classifies by Unicode-range character counts:

  * Latin        : any glyph in U+0041-U+007A (letters), U+00C0-U+024F (extended Latin)
  * Arabic       : U+0600-U+06FF (Arabic), U+0750-U+077F (Arabic Supplement)
  * Digit        : 0-9 (counted as "Latin" since Arabic-digit filings often
                     exist side-by-side with Latin-digit content — see below)

Diacritics / punctuation / numbers don't influence the per-language count.
The detector returns a tiny ``Language``-shaped dict (code + ratio + primary)
per language it found above ``MIN_RATIO``; everything below is dropped.

Why Unicode-range not "lingua-py" or similar library?
  - Zero-dep is mandatory (the tool runs in tight CI matrices).
  - The Arabic block is unambiguous and has no Latin-only fallback.
  - For QSE filings the only practical languages are Arabic + English
    (French filings exist but are vanishingly rare) — supporting
    them is out of scope here.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable

log = logging.getLogger("qstock.langdetect")


# Tuning knobs — exposed as constants so tests can pin them.
ARABIC_RANGES = (
    (0x0600, 0x06FF),  # Arabic block
    (0x0750, 0x077F),  # Arabic Supplement
    (0x08A0, 0x08FF),  # Arabic Extended-A
    (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
    (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
)
LATIN_RANGES = (
    (0x0041, 0x005A),  # A-Z
    (0x0061, 0x007A),  # a-z
    (0x00C0, 0x024F),  # Latin Extended-A + B
)

# Minimum ratio for a language to be reported. Real bilingual filings see
# ~0.40 / 0.40 / 0.20 (en / ar / other); one-off citations shouldn't claim.
MIN_RATIO = 0.05


def _classify_char(c: str) -> str | None:
    """Return 'ar' / 'latin' / None for a single char."""
    if not c or not c.isalpha():
        return None
    cp = ord(c)
    for lo, hi in ARABIC_RANGES:
        if lo <= cp <= hi:
            return "ar"
    for lo, hi in LATIN_RANGES:
        if lo <= cp <= hi:
            return "latin"
    return None


def language_counts(text: str) -> dict[str, int]:
    """Return {"ar": int, "latin": int} counts in this text."""
    ar = latin = 0
    for c in text:
        cat = _classify_char(c)
        if cat == "ar":
            ar += 1
        elif cat == "latin":
            latin += 1
    return {"ar": ar, "latin": latin}


def detect_languages(text: str) -> list[dict]:
    """Return a sorted list of languages present in ``text``.

    Each entry: ``{"code": "ar"|"en", "ratio": float, "primary": bool}``.

    - "en" is the conventional ISO code for Latin letters; "ar" for Arabic.
    - ``primary`` is True for the language with the highest ratio. Exactly
      one entry is marked primary when two or more pass MIN_RATIO.
    - Languages below MIN_RATIO are dropped.
    - Empty / non-text input returns ``[]``.
    """
    counts = language_counts(text or "")
    total = counts["ar"] + counts["latin"]
    if total == 0:
        return []

    rows: list[dict] = []
    for code, count_key in (("en", "latin"), ("ar", "ar")):
        n = counts[count_key]
        if n == 0:
            continue
        ratio = n / total
        if ratio < MIN_RATIO:
            continue
        rows.append({"code": code, "ratio": round(ratio, 4)})

    if not rows:
        return []

    rows.sort(key=lambda r: -r["ratio"])
    rows[0]["primary"] = True
    for r in rows[1:]:
        r["primary"] = False
    return rows


def detect_languages_per_page(pages: Iterable[dict]) -> dict:
    """Aggregate per-page language detection across a filing.

    Returns ``{"languages": [...], "per_page": [{"page": int, "languages": [...]}, ...]}``.
    Each per-page list carries the same shape as ``detect_languages``.
    """
    per_page: list[dict] = []
    totals = {"ar": 0, "latin": 0}
    for p in pages or []:
        text = (p or {}).get("text", "")
        per = detect_languages(text)
        per_page.append({"page": p.get("num"), "languages": per})
        cnt = language_counts(text)
        totals["ar"] += cnt["ar"]
        totals["latin"] += cnt["latin"]

    return {
        "per_page": per_page,
        "languages": detect_languages(
            "\n\n".join((p or {}).get("text", "") for p in (pages or []))
        ),
    }


def apply_language_metadata(
    filing: dict, pages: list[dict] | None = None, text: str | None = None
) -> dict:
    """Set ``metadata.languages[]`` on a filing from its pages (or raw text).

    The metadata is non-destructive — only mutates ``metadata.languages`` and
    leaves every other key alone. Returns the (mutated) filing.

    ``pages`` is preferred when available; ``text`` is the fallback when the
    caller has only joined page text already on hand.
    """
    if pages is None and text is not None:
        # Coerce to a single fake page so the aggregator has something to walk.
        pages = [{"num": 1, "text": text}]
    elif pages is None:
        pages = []

    result = detect_languages_per_page(pages)
    lang_list = result["languages"]

    meta = filing.setdefault("metadata", {})
    # Always overwrite ``languages`` — it's a derived field; the operator's
    # explicit --language choice would only apply during a v2 schema.
    if lang_list:
        meta["languages"] = lang_list
        # Backwards-compat with the single-string field: pin the primary.
        primary = next((l["code"] for l in lang_list if l.get("primary")), None)
        if primary and not meta.get("language"):
            meta["language"] = primary
    else:
        meta["languages"] = []

    # Always present a non-empty per-page roll-up so analysts can see it.
    if result["per_page"]:
        filing["page_languages"] = {
            p["page"]: p["languages"]
            for p in result["per_page"]
            if p["languages"]  # only include pages with detected text
        }
    log.info(
        "langdetect: %d language(s) detected across %d page(s)", len(lang_list), len(pages or [])
    )
    return filing


__all__ = [
    "MIN_RATIO",
    "apply_language_metadata",
    "detect_languages",
    "detect_languages_per_page",
    "language_counts",
]
