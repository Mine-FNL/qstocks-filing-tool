# Security Policy

## Supported Versions

| Version | Supported |
|---------|:---------:|
| 1.6.x   | ✅        |
| 1.5.x   | ✅        |
| 1.4.x   | ✅        |
| 1.3.x   | ❌        |
| 1.2.x   | ❌        |
| 1.1.x   | ❌        |
| < 1.1.0 | ❌        |

The three most recent minor releases receive security fixes. Older
releases are unsupported; please upgrade.

## Reporting a Vulnerability

**Please do not file a public GitHub issue for security problems.**

Send a private disclosure to:

> **[security@mine-fnl.example](mailto:security@mine-fnl.example)**

Or use GitHub's
[private vulnerability reporting][private-report] (Repository →
Security → Advisories → "Report a vulnerability"). Private reports
are visible only to the maintainers until a fix is published.

When reporting, please include:

- A short description of the vulnerability.
- The affected module(s) and version (commit SHA if possible).
- A reproducer (a snippet of CLI invocation or the smallest PDF that
  triggers it).
- Any known workaround or mitigation.
- Whether you've already disclosed the issue publicly.

[private-report]: https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability

## What to Expect

- **Acknowledgement** within **48 hours** of the report.
- **Triage** within **5 business days** — we confirm the bug,
  classify severity (CVSS or a qualitative equivalent), and propose a
  fix timeline.
- **Fix timeline**:
    - **Critical / High**: patch release within 7 days; CVE assigned
      if applicable.
    - **Medium**: patch release within 30 days.
    - **Low**: bundled with the next minor release.
- **Disclosure**: we coordinate disclosure with the reporter. A
  GitHub Security Advisory is published alongside the fix; full
  details stay private until the patch is widely deployed.
- **Credit**: reporters are credited in the advisory (unless they
  prefer otherwise).

## Scope

In scope:

- The `qscreen_*.py` modules shipped by this repository.
- The Flask app surface (`qscreen_app.py`).
- The CLI entry points (`qscreen-ingest`, `qscreen-app`).
- The default install paths (PyPI wheel, GitHub Releases wheel,
  `pip install -e ".[dev]"`).
- The bundled `profiles/qatar/` data and the `pre_flags.py` catalog.

Out of scope:

- LLM-provider behavior (the engine defers to Anthropic / OpenAI /
  OpenRouter / Moonshot / MiniMax for the prompt-guided extraction
  pass). Report provider-side issues to the provider.
- Issues in upstream dependencies (`pdfplumber`, `flask`,
  `openpyxl`, `rapidocr-onnxruntime`, `pytesseract`, etc.). Report
  upstream.
- The user's own profile data (a custom `profiles/<cc>/` you ship
  is your code, not ours).

## Security Hardening Built Into the Engine

For background on the defenses already shipped:

- **Schema-stable output** — every value carries provenance (page,
  table-id, text-anchor). A corrupted input can't silently overwrite
  a value without leaving a trail.
- **Math-identity gates** — `qscreen_gates.py` runs BS identity, IS
  subtotal sign-aware, and skeleton detection. A prompt-injected
  output that drops a liability can't reach the upload.
- **Idempotent uploads** — `If-None-Match: <fingerprint>` + SQLite
  state means a re-run can't double-write or re-upload.
- **URL validation** — the upload URL is validated up-front so a
  typo'd `QSCREEN_API_URL` doesn't 401 against a third-party
  service.
- **Exponential-backoff retry** — transient 5xx / 429 / network
  errors are retried with backoff; a `--upload-retries 0` disables.
- **Structured logging** — `qscreen.ingest` writes to stderr; the
  friendly progress prints are separate. A container can scrape
  structured logs without seeing extracted numbers.
- **No hardcoded secrets** — keys come from env vars or `.env`. The
  PyPI Trusted Publisher flow uses OIDC, no API token is minted.

## Past Advisories

None yet. This section is the placeholder for the first advisory.

## Contact

For everything that isn't a vulnerability: open a
[GitHub issue][issues] or discussion.

For everything that is: [security@mine-fnl.example](mailto:security@mine-fnl.example).

[issues]: https://github.com/Mine-FNL/qstocks-filing-tool/issues