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

- **SLSA Build L3 provenance** — every released wheel, sdist, and
  SBOM is attested via `.github/workflows/provenance.yml` using the
  first-party `actions/attest-build-provenance@v1` action. The result
  is an in-toto SLSA Provenance v1 attestation stored in GitHub's
  artifact-attestations API. Consumers verify with
  `gh attestation verify <file> --owner Mine-FNL
   --repo qstocks-filing-tool` — no per-release long-lived key material
  required on either side; Sigstore + SLSA attestations are both
  keyless. Triggered automatically on `release.published`; the same
  workflow can be triggered manually with a tag input for re-attest
  of an existing release.

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

- **VEX (Vulnerability Exploitability eXchange)** — once SLSA + Sigstore
  cover the artifact side, layered VEX statements from
  `security.yml` advisories give consumers a "this advisory does not
  affect us" receipt without scanning.

- **Renovate as an alternative to Dependabot** — Dependabot's PR cadence
  and grouping is fine for ~50 dependencies; if the tree grows beyond
  that, Renovate's rules engine is more flexible.

- **slsa-framework generator instead of `actions/attest-build-provenance`** —
  the slsa-framework generator is the canonical SLSA Build L3 path for
  Python and supports more advanced provenance shapes (multi-stage
  builds, hermetic toolchains). Today we use GitHub's first-party
  attestation action because it's plug-into-existing-build; a future
  refactor could move `release.yml::publish` into the slsa generator's
  reusable workflow for richer provenance metadata.

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

# Confirm a release artifact has an SLSA Build L3 attestation
TAG=vX.Y.Z
gh release download "${TAG}" --pattern 'qscreen_filing_tool-*' --dir /tmp
gh attestation verify /tmp/qscreen_filing_tool-*-py3-none-any.whl \\
    --owner Mine-FNL --repo qstocks-filing-tool
gh attestation verify /tmp/qscreen_filing_tool-*.tar.gz \\
    --owner Mine-FNL --repo qstocks-filing-tool
gh attestation verify /tmp/sbom.cdx.json \\
    --owner Mine-FNL --repo qstocks-filing-tool

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
