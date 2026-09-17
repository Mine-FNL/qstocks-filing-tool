# Changelog

All notable changes to **qscreen-filing-tool** are documented here.
This project follows [Semantic Versioning](https://semver.org/).

## [1.6.0] — 2026-09-16

Six minor releases over one PR cycle. Engine is jurisdiction-agnostic, idempotent, and machine-verifiable.

### Added
- **Stable text fingerprints**: `qscreen_fingerprint.py print` and `qscreen_fingerprint.py diff`. SHA-256 over whitespace-normalized text. Covers audit + statements + notes. Order-independent overall fingerprint. Auto-stamped on every saved filing. ([#29](https://github.com/Mine-FNL/qstocks-filing-tool/pull/29))
- **Per-page language detection**: pure-Unicode Arabic/English classifier (zero deps). New schema fields `metadata.languages[]` and `filing.page_languages{}`. ([#28](https://github.com/Mine-FNL/qstocks-filing-tool/pull/28))
- **Auto-detect sector / fiscal_period / reporting_framework**: reads filing cover pages; default ON; `--no-auto-detect` to disable. Never overwrites operator-provided values. ([#27](https://github.com/Mine-FNL/qstocks-filing-tool/pull/27))
- **Golden-set evaluation harness**: `python qscreen_eval.py` runs 8 hand-verified real QSE filings. Integrates non-gating in CI (matrix + smoke). ([#26](https://github.com/Mine-FNL/qstocks-filing-tool/pull/26))
- **Math-identity gates + pre-flag catalog**: skeleton detection (80%+ null), BS identity (A ≈ L + E), IS subtotal sign-aware, currency/unit sanity. Catalog: 11 cross-cutting rules + 25 issuer-specific facts. ([#25](https://github.com/Mine-FNL/qstocks-filing-tool/pull/25))
- **Idempotent batch + idempotent upload**: SQLite state at `~/.qstocks-filing-tool/state.db`, atomic `claim_row`, multiprocessing-safe `--resume`. `If-None-Match` 412 short-circuit on duplicate upload. ([#25](https://github.com/Mine-FNL/qstocks-filing-tool/pull/25))
- **Production hardening**: Flask `/healthz` + Dockerfile + CI smoke job, exponential-backoff retry on upload, URL validation, structured `qscreen.ingest` logger, exit codes 0/1/2/6/130. ([#24](https://github.com/Mine-FNL/qstocks-filing-tool/pull/24))
- **Pluggable profile system**: `profiles/<jurisdiction>/` (Qatar ships in box). Back-compat `import qatar` shim. ([#24](https://github.com/Mine-FNL/qstocks-filing-tool/pull/24))

### Quality
- 480 / 480 unit tests pass on Python 3.9, 3.10, 3.11, 3.12, 3.13.
- 12 / 12 CI jobs green (matrix + app-smoke).
- Golden-set accuracy: **100 / 124 (80.6 %)** check-level on real QSE filings.

[1.6.0]: https://github.com/Mine-FNL/qstocks-filing-tool/releases/tag/v1.6.0
