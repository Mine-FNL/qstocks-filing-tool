# Lobsters cross-post

**Recommended day after Show HN**. Lobsters is invitation-friendly; if you're not yet a member, drop the post title into a friend-of-friend request.

## Title (60 chars max)

```
qscreen-filing-tool: open-weight PDF → lossless filing JSON for financial reports
```

## URL

```
https://github.com/Mine-FNL/qstocks-filing-tool
```

## Tags

`pdf`, `open-source`, `finance`, `python`

## Body

> Cross-posting from [HN](https://news.ycombinator.com/item?id=__YOUR_HN_ID__) — same project, lower-traffic venue, deeper technical audience. The QSE-flavored use case is one driver, but the engine itself is jurisdiction-agnostic: drop a profile into `profiles/` for any other market and the rest of the code doesn't change.
>
> Two engineering bets worth flagging:
>
> 1. **Deterministic-first extraction.** The PDF tables are read in code; the LLM only fills gaps (audit opinion, notes, segments). This is why a 270M local model produces the same lossless filing contract as a frontier cloud model — the numbers never pass through the LLM.
> 2. **Math-identity gate.** The JSON won't ship if `Assets ≠ L + Equity` within ±2% (with sector-aware overrides). 11 cross-cutting + 25 issuer-specific pre-flag rules run before `save`. If a record contradicts itself, the record doesn't ship, and the evidence points at the offending line item.
>
> SHA-256 cross-filing fingerprints + Sigstore keyless signing on every release means re-ingest of the same PDF produces bit-identical JSON, cryptographically attestable back to the engine commit that produced it.
>
> 485 tests, ruff clean, mkdocs --strict, container on `ghcr.io/Mine-FNL/qstocks-filing-tool`, install paths that don't require a PyPI Trusted Publisher click (GitHub Releases CDN + PEP 503 simple index on GitHub Pages + the container).
>
> Happy to dig into any of the design choices in the comments.

## Asset

- Body image: `campaign/assets/architecture-16x9.jpg`

## Posting notes

- Lobsters is low-volume; a thoughtful first-hour reply ("here's what we
  considered and rejected") gets more traction than a high-volume blast.
- Don't cross-post the captioned video — Lobsters users expect text/code
  and find heavy media spammy.
- Tag `pdf` first (highest signal-to-noise on this site).
