# Supply-chain posture

Verifiable build artifacts are the floor, not the ceiling, for shipping
internal Python tooling at a financial-services firm. This document lists
what ships today, what is wired but inactive, and what is deliberately
left as future work.

## Shipped (active in CI)

- **CycloneDX SBOM** — emitted at build time inside
  `.github/workflows/release.yml::publish`. The `dist/sbom.cdx.json`
  artifact is attached to every GitHub Release. Compatible with Grype,
  Trivy, Dependency-Track, Snyk, and any CycloneDX 1.5-aware scanner.

- **Sigstore keyless OIDC signing** — every wheel + sdist is signed by
  `sigstore/gh-action-sigstore-python@v1.2.0` against the GH OIDC
  subject (`owner/repo/.github/workflows`, pinned at release time).
  `.sig` + `.crt` are re-uploaded to the release as additional assets.

- **CodeQL semantic analysis** — `.github/workflows/security.yml` runs
  on every PR + every push to main + weekly Monday 06:00 UTC. SARIF
  uploaded to the Security tab.

- **pip-audit advisory scan** — same workflow. CycloneDX + plain JSON
  output, attached as a job artifact (30-day retention). Currently
  non-blocking (warn) because the dev tree has transient advisories
  we have not yet triaged.

- **Pre-commit hooks** — `.pre-commit-config.yaml` runs `ruff` + standard
  Python hygiene (whitespace, EOF, line-endings, large files, conflict
  markers, case conflicts, shebang executability) + `detect-secrets`
  (with `.secrets.baseline` so legitimate test fixtures don't trip
  every commit). A mirrored `.github/workflows/pre-commit.yml` runs
  the same hooks on every PR + push to main.

- **Dependabot** — pip + github-actions + docker ecosystems on a weekly
  Monday cadence, grouped minor + patch updates with `deps:` commit
  prefix.

## Wired but inactive

- **PyPI Trusted Publishers** — `.github/workflows/publish.yml` is
  configured and uses OIDC. It is dormant until the maintainer
  registers the trust on `pypi.org/manage/account/publishing/`
  (one-time UI click outside this codebase). The OIDC + `id-token: write`
  permission + the actual publishing job are all in place; only the
  external registration is pending.

## Deliberate gaps (future work)

- **SLSA Build L3 provenance attestation** — `slsa-framework/slsa-github-generator/.github/workflows/generator_python_slsa3.yml@v2.0.0`
  was the intended target, but using it from a step-level `uses:` is
  invalid syntax (the generator is a reusable workflow, not an
  action). Calling it at job-level would require refactoring our
  release flow so the build lives inside the slsa generator, not in
  `release.yml::publish`. That refactor is real work — it's deferred
  to a follow-up session, not stubbed in half-working form.

  Workaround until then: Sigstore + GH OIDC identity gives
  consumers a comparable receipt. Verify the release's provenance
  via either:
  - `gh attestation verify dist/qscreen_filing_tool-X.Y.Z-py3-none-any.whl \\
       --owner Mine-FNL --repo qstocks-filing-tool`
  - `cosign verify-blob --signature <file>.sig \\
       --certificate <file>.crt \\
       --certificate-identity 'https://github.com/Mine-FNL/qstocks-filing-tool/.github/workflows/release.yml@refs/tags/vX.Y.Z' \\
       <file>`

- **Sigstore signing + SLSA on the SBOM itself** — the SBOM is attached
  to the release but not separately signed. Add a Sigstore step over
  `dist/sbom.cdx.json` after attestation generation; coordinates with
  the SLSA work above.

- **VEX (Vulnerability Exploitability eXchange)** — once SLSA + Sigstore
  cover the artifact side, layered VEX statements from
  `security.yml` advisories give consumers a "this advisory does not
  affect us" receipt without scanning.

- **Renovate as an alternative to Dependabot** — Dependabot's PR cadence
  and grouping is fine for ~50 dependencies; if the tree grows beyond
  that, Renovate's rules engine is more flexible.

## Verification cheat-sheet

```sh
# Confirm the SBOM landed on the latest release
gh release download --pattern 'sbom.cdx.json' --dir /tmp
.venv/bin/python -c "import json; d=json.load(open('/tmp/sbom.cdx.json')); print(d['serialNumber'], d['metadata']['timestamp'], len(d['components']), 'components')"

# Confirm a release artifact is Sigstore-signed
TAG=vX.Y.Z
curl -sL "https://github.com/Mine-FNL/qstocks-filing-tool/releases/download/${TAG}/qscreen_filing_tool-${TAG#v}.tar.gz" \\
  -o /tmp/pkg.tar.gz
curl -sL "https://github.com/Mine-FNL/qstocks-filing-tool/releases/download/${TAG}/qscreen_filing_tool-${TAG#v}.tar.gz.sig" \\
  -o /tmp/pkg.tar.gz.sig
cosign verify-blob --signature /tmp/pkg.tar.gz.sig --certificate /tmp/pkg.tar.gz.crt \
    --certificate-identity "https://github.com/Mine-FNL/qstocks-filing-tool/.github/workflows/release.yml@refs/tags/${TAG}" \
    /tmp/pkg.tar.gz

# Re-run the bench locally (mirrors the CI regression gate)
.venv/bin/python qscreen_eval.py
```

## References

- SLSA Build L3: https://slsa.dev/spec/v1.1/build-providing
- CycloneDX 1.5: https://cyclonedx.org/specification/overview/
- in-toto SLSA Provenance v1: https://github.com/in-toto/attestation/tree/main/provenance
- Sigstore: https://docs.sigstore.dev/
- GitHub Artifact Attestations: https://docs.github.com/en/code-security/conveying-information-about-your-software/establishing-provenance-for-your-artifacts
- PyPI Trusted Publishers: https://docs.pypi.org/trusted-publishers/
