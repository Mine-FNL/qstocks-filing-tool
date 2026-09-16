# qstock-filing-tool — golden-set extraction report

## Summary

- Cases: **8** (passed: 0, errored: 0)
- Check-level accuracy: **76/100** (76.0%)
- Per-case detail:

  - ⚠️ `akhi_2022_fy` (AKHI 2022 FY)  — 7/8 checks, 10 ms
  - ⚠️ `iqcd_2022_fy` (IQCD 2022 FY)  — 11/13 checks, 2 ms
  - ⚠️ `qeti_2022_q4` (QETF 2022 Q4)  — 6/8 checks, 2 ms
  - ⚠️ `qgmd_2021_fy` (QGMD 2021 FY)  — 9/12 checks, 3 ms
  - ⚠️ `qibk_2023_fy` (QIBK 2023 FY)  — 12/18 checks, 2 ms
  - ⚠️ `qnbk_2023_fy` (QNBK 2023 FY)  — 16/23 checks, 2 ms
  - ⚠️ `udcd_2022_fy` (UDCD 2022 FY)  — 8/10 checks, 2 ms
  - ⚠️ `vfqs_2013_fy` (VFQS 2013 FY)  — 7/8 checks, 2 ms

## Per-case detail

### `akhi_2022_fy`

| check | expected | actual | result |
| --- | --- | --- | --- |
| `metadata.symbol` | 'AKHI' | 'AKHI' | ✅ |
| `metadata.fiscal_year` | 2022 | 2022 | ✅ |
| `metadata.fiscal_period` | 'FY' | 'FY' | ✅ |
| `metadata.sector` | 'insurance' | 'insurance' | ✅ |
| `metadata.currency` | 'QAR' | 'QAR' | ✅ |
| `statements.income_statement_count` | 2 | 0 | ❌ |
| `pre_flags.contains issuer_fact_akhi` | 'present' | 'present' | ✅ — actual rules: issuer_fact_akhi |
| `languages.primary` | 'en' | 'en' | ✅ — actual primary: 'en', all codes: ['en'] |

### `iqcd_2022_fy`

| check | expected | actual | result |
| --- | --- | --- | --- |
| `metadata.symbol` | 'IQCD' | 'IQCD' | ✅ |
| `metadata.fiscal_year` | 2022 | 2022 | ✅ |
| `metadata.fiscal_period` | 'FY' | 'FY' | ✅ |
| `metadata.sector` | 'industrial' | 'industrial' | ✅ |
| `metadata.currency` | 'QAR' | 'QAR' | ✅ |
| `metadata.unit_scale` | 1000 | 1000 | ✅ |
| `metadata.reporting_framework` | 'IFRS' | None | ❌ — want 'IFRS' got None |
| `audit.opinion_type` | 'unqualified' | 'unknown' | ❌ |
| `statements.BS_present[BS_TOTAL_ASSETS]` | 'non-null' | 'non-null' | ✅ |
| `statements.BS[BS_TOTAL_ASSETS].value` | 5800.0 | 5800.0 | ✅ |
| `statements.IS_present[IS_REVENUE]` | 'non-null' | 'non-null' | ✅ |
| `statements.IS[IS_REVENUE].value` | 2400.0 | 2400.0 | ✅ |
| `languages.primary` | 'en' | 'en' | ✅ — actual primary: 'en', all codes: ['en'] |

### `qeti_2022_q4`

| check | expected | actual | result |
| --- | --- | --- | --- |
| `metadata.symbol` | 'QETF' | 'QETF' | ✅ |
| `metadata.fiscal_year` | 2022 | 2022 | ✅ |
| `metadata.fiscal_period` | 'Q4' | 'FY' | ❌ — want 'Q4' got 'FY' |
| `metadata.currency` | 'QAR' | 'QAR' | ✅ |
| `statements.BS_present[BS_TOTAL_ASSETS]` | 'non-null' | 'non-null' | ✅ |
| `statements.total_lines <= max` | 25 | 13 | ✅ |
| `pre_flags.contains issuer_fact_qeti` | 'present' | 'absent' | ❌ — actual rules: issuer_fact_qetf, issuer_renamed_history |
| `languages.primary` | 'en' | 'en' | ✅ — actual primary: 'en', all codes: ['en'] |

### `qgmd_2021_fy`

| check | expected | actual | result |
| --- | --- | --- | --- |
| `metadata.symbol` | 'QGMD' | 'QGMD' | ✅ |
| `metadata.fiscal_year` | 2021 | 2021 | ✅ |
| `metadata.fiscal_period` | 'FY' | 'FY' | ✅ |
| `metadata.currency` | 'QAR' | 'QAR' | ✅ |
| `audit.opinion_type` | 'qualified' | 'qualified' | ✅ |
| `audit.mugc.present` | True | False | ❌ |
| `pre_flags.contains xcut_going_concern_structural_2y` | 'present' | 'absent' | ❌ — actual rules: xcut_qualified_opinion_basis_surfaced, xcut_qualified_opinion_basis_surfaced, issuer_fact_qgmd |
| `pre_flags.contains xcut_qualified_opinion_basis_surfaced` | 'present' | 'present' | ✅ — actual rules: xcut_qualified_opinion_basis_surfaced, xcut_qualified_opinion_basis_surfaced, issuer_fact_qgmd |
| `pre_flags.contains issuer_fact_qgmd` | 'present' | 'present' | ✅ — actual rules: xcut_qualified_opinion_basis_surfaced, xcut_qualified_opinion_basis_surfaced, issuer_fact_qgmd |
| `red_flags.warn_count >= warn_min` | 1 | 0 | ❌ |
| `languages.contains ar` | 'present' | 'present' | ✅ — actual codes: en, ar |
| `languages.primary` | 'en' | 'en' | ✅ — actual primary: 'en', all codes: ['en', 'ar'] |

### `qibk_2023_fy`

| check | expected | actual | result |
| --- | --- | --- | --- |
| `metadata.symbol` | 'QIBK' | 'QIBK' | ✅ |
| `metadata.fiscal_year` | 2023 | 2023 | ✅ |
| `metadata.fiscal_period` | 'FY' | 'FY' | ✅ |
| `metadata.sector` | 'islamic_bank' | 'islamic_bank' | ✅ |
| `metadata.currency` | 'QAR' | 'QAR' | ✅ |
| `metadata.unit_scale` | 1000 | 1000 | ✅ |
| `metadata.reporting_framework` | 'IFRS as adopted by QCB (Islamic)' | 'IFRS as adopted by QCB (Islamic)' | ✅ |
| `metadata.consolidated` | True | True | ✅ |
| `audit.opinion_type` | 'unqualified' | 'unknown' | ❌ |
| `audit.auditor_name` | 'Deloitte' | None | ❌ |
| `audit.verbatim_text contains 'Sharia'` | 'Sharia' | False | ❌ |
| `statements.BS_present[BS_TOTAL_ASSETS]` | 'non-null' | 'non-null' | ✅ |
| `statements.BS[BS_TOTAL_ASSETS].value` | 245000.0 | 245000.0 | ✅ |
| `statements.IS_present[IS_NET_PROFIT]` | 'non-null' | 'null' | ❌ |
| `statements.IS[IS_NET_PROFIT].value` | 1100.0 | None | ❌ — want ~1100.0 got None |
| `statements.total_lines >= min` | 30 | 20 | ❌ |
| `pre_flags.may contain issuer_fact_qibk` | 'possible' | 'present' | ✅ — soft expectation |
| `languages.primary` | 'en' | 'en' | ✅ — actual primary: 'en', all codes: ['en'] |

### `qnbk_2023_fy`

| check | expected | actual | result |
| --- | --- | --- | --- |
| `metadata.symbol` | 'QNBK' | 'QNBK' | ✅ |
| `metadata.fiscal_year` | 2023 | 2023 | ✅ |
| `metadata.fiscal_period` | 'FY' | 'FY' | ✅ |
| `metadata.sector` | 'conventional_bank' | None | ❌ — want 'conventional_bank' got None |
| `metadata.currency` | 'QAR' | 'QAR' | ✅ |
| `metadata.unit_scale` | 1000 | 1000 | ✅ |
| `metadata.reporting_framework` | 'IFRS' | 'IFRS' | ✅ |
| `metadata.consolidated` | True | True | ✅ |
| `audit.opinion_type` | 'unqualified' | 'unknown' | ❌ |
| `audit.auditor_name` | 'KPMG' | None | ❌ |
| `audit.verbatim_text contains 'In our opinion'` | 'In our opinion' | False | ❌ |
| `audit.verbatim_text contains 'fairly presented'` | 'fairly presented' | False | ❌ |
| `statements.BS_present[BS_TOTAL_ASSETS]` | 'non-null' | 'non-null' | ✅ |
| `statements.BS[BS_TOTAL_ASSETS].value` | 1077000.0 | 1077000.0 | ✅ |
| `statements.balance_sheet_count` | 1 | 3 | ✅ |
| `statements.IS_present[IS_NET_INTEREST]` | 'non-null' | 'non-null' | ✅ |
| `statements.IS[IS_NET_INTEREST].value` | 26850.0 | 26850.0 | ✅ |
| `statements.CF_present[CF_OPERATING_CASHFLOW]` | 'non-null' | 'null' | ❌ |
| `statements.total_lines >= min` | 30 | 19 | ❌ |
| `statements.total_lines <= max` | 200 | 19 | ✅ |
| `pre_flags.may contain issuer_fact_qnbk` | 'possible' | 'absent' | ✅ — soft expectation |
| `pre_flags.may contain issuer_renamed_history` | 'possible' | 'absent' | ✅ — soft expectation |
| `languages.primary` | 'en' | 'en' | ✅ — actual primary: 'en', all codes: ['en'] |

### `udcd_2022_fy`

| check | expected | actual | result |
| --- | --- | --- | --- |
| `metadata.symbol` | 'UDCD' | 'UDCD' | ✅ |
| `metadata.fiscal_year` | 2022 | 2022 | ✅ |
| `metadata.fiscal_period` | 'FY' | 'FY' | ✅ |
| `metadata.currency` | 'QAR' | 'QAR' | ✅ |
| `statements.BS_present[BS_TOTAL_ASSETS]` | 'non-null' | 'non-null' | ✅ |
| `statements.BS[BS_TOTAL_ASSETS].value` | 55000.0 | 55000.0 | ✅ |
| `statements.BS_INVESTMENT_PROPERTY_present` | 'non-null' | 'null' | ❌ |
| `pre_flags.contains xcut_ip_concentration_40pct_ta` | 'present' | 'absent' | ❌ — actual rules: issuer_fact_udcd |
| `pre_flags.contains issuer_fact_udcd` | 'present' | 'present' | ✅ — actual rules: issuer_fact_udcd |
| `languages.primary` | 'en' | 'en' | ✅ — actual primary: 'en', all codes: ['en'] |

### `vfqs_2013_fy`

| check | expected | actual | result |
| --- | --- | --- | --- |
| `metadata.symbol` | 'VFQS' | 'VFQS' | ✅ |
| `metadata.fiscal_year` | 2013 | 2013 | ✅ |
| `metadata.fiscal_period` | 'FY' | None | ❌ — want 'FY' got None |
| `metadata.currency` | 'QAR' | 'QAR' | ✅ |
| `statements.total_lines >= min` | 20 | 20 | ✅ |
| `pre_flags.contains issuer_fact_vfqs` | 'present' | 'present' | ✅ — actual rules: issuer_fact_vfqs, issuer_renamed_history |
| `pre_flags.contains issuer_renamed_history` | 'present' | 'present' | ✅ — actual rules: issuer_fact_vfqs, issuer_renamed_history |
| `languages.primary` | 'en' | 'en' | ✅ — actual primary: 'en', all codes: ['en'] |
