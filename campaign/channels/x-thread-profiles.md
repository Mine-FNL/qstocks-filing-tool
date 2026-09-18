# X thread — pluggable profiles (8 tweets)

**Asset:** `campaign/assets/architecture-16x9.jpg` (tweet 4)
**Use:** Targets the international-finance / regional-exchange crowd. Post 14–18 days after launch.

---

**1/** Adding a new jurisdiction to a financial-data pipeline usually means:

- A new PDF parser for the new layout
- A new sector taxonomy
- A new pre-flag ruleset
- New account-code mappings

We collapsed that into "drop a directory under `profiles/`". 🧵

**2/** A profile is three things:

```python
# profiles/<jurisdiction>/__init__.py

JURISDICTION_NAME = "Qatar"   # or "UAE", "Saudi Arabia", ...

def build_profile(ticker: str) -> Profile:
    return Profile(
        sector=...,
        fiscal_calendar=...,
        currency=...,
        framework=...,         # IFRS, IFRS-for-SME, AAOIFI, ...
        account_codes=...,     # ticker → {canonical_account: pdf_label}
        preflag_rules=[...],   # issuer-specific pre-flag rules
    )
```

That's it.

**3/** The engine doesn't know or care which jurisdiction is loaded. The CLI / web app / pipeline is the same code path.

```bash
qscreen-ingest report.pdf \
  --symbol AKHI \
  --jurisdiction qatar \
  --year 2022
```

Swap `--jurisdiction qatar` for `--jurisdiction uae` and the same engine
handles UAE filings.

**4/** [image: architecture-16x9.jpg]

**5/** What the profile teaches the engine:

1. **Sector** → which gate tolerances apply (banks ≠ insurance ≠ industrial).
2. **Fiscal calendar** → FY end, interim-period boundaries.
3. **Currency** → default unit, scale (thousands / millions / absolute).
4. **Framework** → IFRS / IFRS-for-SME / AAOIFI / local-GAAP.
5. **Account-code map** → ticker-specific label → canonical-account.
6. **Pre-flag rules** → issuer-specific knowledge (e.g., UDCD's IP
   ceiling).

**6/** What the engine teaches the profile:

Nothing. The engine is jurisdiction-agnostic. The profile is the only
place where jurisdiction-specific knowledge lives.

This is the architectural separation that makes new jurisdictions
cheap.

**7/** The honest accounting:

| Jurisdiction | Status               | Effort to add |
|--------------|----------------------|---------------|
| Qatar        | Shipped              | (already done) |
| UAE          | Documented, not built| 2–3 weeks      |
| Saudi Arabia | Documented, not built| 3–4 weeks      |
| Kuwait       | Documented, not built| 3–4 weeks      |
| UK           | Untouched            | 6+ weeks (FRS 102, Companies House formats) |
| US           | Untouched            | 8+ weeks (SEC EDGAR XBRL is its own beast) |

**8/** Roadmap to v1.7.0:

- UAE profile (2–3 weeks, sponsor-funded)
- A `profile-validator` test that ships with the engine so a new
  profile can be unit-tested against a held-out filing set before
  integration.

📦 https://github.com/Mine-FNL/qstocks-filing-tool
📄 §4.1 in the whitepaper.

If you maintain a regional exchange's data team, RT and we'll reach
out about a sponsored profile drop.

---

**Posting notes:**

- The "2–3 weeks to add a jurisdiction" line is the hook; expect
  questions in replies. Have the architecture-16x9.jpg ready as a
  reply-image.
- This thread is the right one to send to finance Twitter accounts
  with regional-followings (MENA-finance, GCC-finance, etc.).
