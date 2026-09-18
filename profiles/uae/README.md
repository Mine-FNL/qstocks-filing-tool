# UAE profile (stub)

This directory is the skeleton of the **`uae`** jurisdiction profile
for the Abu Dhabi Securities Exchange (ADX) and Dubai Financial Market
(DFM).

## Status

**Stub.** The structure is in place and `build_profile()` is callable,
but the data tables are empty. The engine will work end-to-end on a
UAE filing — it falls back to autodetected defaults when
`build_profile(ticker)` returns `None` — but the issuer-specific
pre-flag rules (the rules that catch contradictions and known-bad
patterns at the issuer level) are **not yet authored** for any UAE
ticker.

## Why it's here even as a stub

The stub ships now so that:

1. **The CLI flag is wired.** ``qscreen-ingest report.pdf --jurisdiction
   uae --symbol <TICKER>`` doesn't error on import — it just runs
   with empty profile data.
2. **The audit trail is honest.** Anyone reading the source knows
   exactly what's there and what isn't.
3. **The contribution path is clear.** A contributor who wants to
   add UAE support has a known-empty `_seed.py` to fill in.

## What's needed to lift this stub to v1.7.0

| Step | Effort | Notes |
|---|---|---|
| Populate `COMPANY_NAMES` for ~30 ADX + DFM tickers | 1 day | Issuer-name → ticker map |
| Populate `SYMBOL_SUBSECTOR` for each ticker | 0.5 day | Sector taxonomy |
| Populate `WATCH_KPIS` per issuer | 1 day | From each issuer's annual report |
| Populate `ENRICH` (framework, fy_end, key events) | 1 day | Acquisitions, restatements, regulator regimes |
| Author `pre_flags.py` (~10–25 UAE-specific pre-flag rules) | 2–3 days | Mirrors `profiles/qatar/pre_flags.py`; captures UAE-specific known patterns |
| Author `tests/golden/<ticker>_<year>_<period>.json` cases | 1 day | Mirror Qatar's golden set |
| Validate against the bench regression floor (80.6%) | 0.5 day | May require profile tweaks |
| Add UAE-specific fiscal-calendar overrides (some issuers use Mar/Jun/Sep/Dec) | 0.5 day | |

**Total: ~7–10 working days** for an engineer familiar with the Qatar
profile and the engine.

## How to test what *does* work today

```bash
# The engine accepts UAE-jurisdiction flag now
qscreen-ingest reports/emirates_nbd_2024.pdf \
  --jurisdiction uae \
  --symbol EMIRATES \
  --year 2024 \
  --period FY

# It runs end-to-end (autodetected defaults). Issuer-specific
# pre-flag rules are not invoked because the ticker isn't in
# profiles/uae/_seed.py yet.
```

## Reference

- ADX listed companies: <https://www.adx.ae/>
- DFM listed companies: <https://www.dfm.ae/>
- IFRS-as-endorsed-by-UAE: <https://www.mof.gov.ae/>
- AAOIFI standards (Islamic finance): <https://aaoifi.com/>

## Roadmap

- **v1.7.0** — UAE profile populated to bench-grade (above checklist)
- **v1.8.0** — Saudi Arabia (Tadawul) profile
- **v2.0.0** — Kuwait (Boursa Kuwait) profile
