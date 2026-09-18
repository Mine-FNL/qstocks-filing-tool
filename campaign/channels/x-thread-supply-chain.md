# X thread — supply chain hardening for finance (10 tweets)

**Asset:** none — code-block-heavy thread.
**Use:** Targets the security / compliance crowd. Post 12–16 days after the launch thread.

---

**1/** Most finance-flavored OSS projects treat supply chain as an afterthought.

We didn't, because the consumers are compliance teams that *will* ask for SBOM, signed releases, and SLSA provenance.

Here's the full chain we shipped. 🧵

**2/** What every release produces:

```
✅ Wheel (linux/macos/windows-compatible)
✅ SBOM — CycloneDX 1.5 (JSON + XML)
✅ Sigstore keyless signature bundle
✅ SLSA Build L3 provenance attestation
✅ Container image (linux/amd64 + linux/arm64)
✅ Demo page (regenerated from bench)
```

Six artifacts per tag. Five of them are verifiable without operator trust.

**3/** SBOM — CycloneDX 1.5:

```bash
cyclonedx-py -e -F -o sbom.json -of JSON
cyclonedx-py -e -F -o sbom.xml  -of XML
```

Lists every transitive dep, every version, every license. Audit teams
get a machine-readable inventory.

**4/** Sigstore keyless signing:

```bash
sigstore-python sign \
  --fulcio-url https://fulcio.sigstore.dev \
  --rekor-url https://rekor.sigstore.dev \
  qscreen_filing_tool-1.6.0-py3-none-any.whl
```

No GPG key to manage. OIDC from the GitHub Actions runner → Fulcio →
short-lived signing cert → Rekor transparency log.

**5/** SLSA Build L3 attestation:

```yaml
- uses: actions/attest-build-provenance@v1
  with:
    subject-path: dist/*.whl
```

Generates the SLSA v1 receipt. Verifiable with `gh attestation verify`.

The receipt binds the wheel to the source commit, the runner, and the
SBOM.

**6/** Container — multi-arch:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/Mine-FNL/qstocks-filing-tool:v1.6.0 \
  --push .
```

Pin the SHA, not the tag, in CI:

```yaml
image: ghcr.io/Mine-FNL/qstocks-filing-tool@sha256:abc123...
```

**7/** The gates that catch regressions:

| Gate          | Trigger           | What it catches                              |
|---------------|-------------------|----------------------------------------------|
| CodeQL        | PR, main, weekly  | Static-analysis findings (Python + Actions)  |
| pip-audit     | PR, main, weekly  | Known-vuln deps (non-blocking today)        |
| pre-commit    | PR, main          | Format / lint / shebang / detect-secrets     |
| ruff / mypy   | PR, main          | Style + types                                |
| bench         | PR, weekly        | 124-check regression floor (100/124)        |

**8/** What we *don't* gate on (and why):

- **OSSF Scorecard threshold.** Scorecard is informative, not normative.
  We aim for 7.5+/10 but don't gate on it.
- **Snyk / Dependabot alert counts.** Same — informational until
  actionable.
- **Container signing.** Cosign is on the roadmap (Q4 2026).

**9/** The `detect-secrets` hook catches tokens at commit time:

```yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.5.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
```

So even if someone copy-pastes an API key, the commit fails before
it lands.

**10/** What compliance teams actually want:

Not "is this SBOM-attested" (yes). Not "is the wheel signed" (yes).
Not "is the chain end-to-end auditable" (yes).

They want: **"can a third-party auditor verify this without
cooperating with us?"**. The answer is yes — the receipts are
public, the Sigstore log is public, the SLSA verification is
one command.

📦 https://github.com/Mine-FNL/qstocks-filing-tool
📄 §4.2 + §6 in the whitepaper.

RT if compliance should be the floor, not the ceiling. 🤝

---

**Posting notes:**

- This thread is dense — pin it to your profile for the week after
  posting; SRE/security folks will bookmark.
- If a finance/compliance account picks it up, expect 5–10× the
  engagement.
