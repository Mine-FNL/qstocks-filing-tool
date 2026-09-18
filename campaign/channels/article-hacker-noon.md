# Hacker Noon / DevOps angle

**Recommended cadence:** 10–14 days after Show HN.
**Target publication:** Hacker Noon (open-submission; lower bar than
Medium tier-1 pubs), DevOps.com (contributed articles).

---

## Title candidates

```
A: I shipped an OSS pipeline with Sigstore + SLSA L3 + CodeQL — here's
   what I learned
B: The supply-chain hardening checklist I wish I'd had at v0.1
C: Why my finance-flavored OSS project gates every PR on a regression
   bench (and you should too)
```

## Cover image

`campaign/assets/architecture-16x9.jpg` or a new screenshot of the
release workflow with annotations.

## Body (Markdown — Hacker Noon supports common-flavored markdown)

```markdown
# The supply-chain hardening checklist I wish I'd had at v0.1

> Six months ago I started an open-source project that processes
> financial PDFs. Today every release ships with SBOM, Sigstore keyless
> signing, SLSA Build L3 attestation, CodeQL, and a 124-check
> regression bench. This is the checklist that got me here.

## Why finance-flavored OSS needs supply-chain rigor

A "PDF to JSON" tool for the consumer market doesn't need SBOM
attestation. Nobody cares if it gets a number wrong once in a while;
the consumer can double-check.

A "PDF to JSON" tool for compliance teams is a different beast. The
data ends up in regulatory filings. The auditors will ask: *which
engine version produced this row? Can you prove it? Did the dep graph
change between v1.5 and v1.6?*

If the answer is "trust me, I ran the same code", you don't ship.

## The checklist

### 1. CycloneDX 1.5 SBOM, every release

```yaml
- name: Generate SBOM
  run: |
    pip install cyclonedx-bom
    cyclonedx-py -e -F -o sbom.json -of JSON
    cyclonedx-py -e -F -o sbom.xml  -of XML
- uses: actions/upload-artifact@v4
  with:
    name: sbom
    path: sbom.*
```

`cyclonedx-bom` is the official Python tool. Outputs both JSON and
XML. Uploaded as a release artifact.

### 2. Sigstore keyless signing, every release

```yaml
- uses: sigstore/gh-action/sign-with-sigstore@v1
  with:
    artifact: dist/*.whl
  env:
    SIGSTORE_ID_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

No GPG key. OIDC from the GitHub Actions runner → Fulcio → short-lived
cert → Rekor transparency log. The bundle is the signature.

### 3. SLSA Build L3 attestation, every release

```yaml
permissions:
  id-token: write
  attestations: write
- uses: actions/attest-build-provenance@v1
  with:
    subject-path: dist/*.whl
```

Generates the SLSA v1 in-toto receipt. One `gh attestation verify`
command checks it.

### 4. CodeQL on every PR + main + weekly

```yaml
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '17 6 * * 1'   # Mondays
```

CodeQL finds things you don't. It will save you from a CVE-class
mistake at least once.

### 5. `pip-audit` on every PR

Non-blocking today (informational), but the data is there when you
decide to gate on it.

### 6. Multi-arch container on ghcr.io

```yaml
- uses: docker/setup-buildx-action@v3
- uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/owner/repo:v${{ github.ref_name }}
```

### 7. A regression bench that fails PRs

This is the one that matters most. A supply chain that's hardened
but a project that's regressing is a polished turd.

```yaml
on:
  pull_request:
  schedule:
    - cron: '0 3 * * 1'
jobs:
  bench:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: python qscreen_eval.py --json > bench.json
      - name: Gate at floor
        run: |
          python -c "
          import json
          d = json.load(open('bench.json'))
          assert d['passed'] >= 100, d
          "
```

The bench is your **contract**. Don't gate on delta; gate on
**absolute floor**.

## What this costs

| Item                    | Build time | Per-release $ |
|-------------------------|------------|---------------|
| SBOM generation         | 8s         | $0            |
| Sigstore signing        | 6s         | $0            |
| SLSA attestation        | 4s         | $0            |
| CodeQL (PR)             | 90s        | $0            |
| pip-audit (PR)          | 12s        | $0            |
| Multi-arch container    | 4min       | $0 (GH free tier) |
| Regression bench        | 11min      | $0 (GH free tier) |

Total: ~16 minutes added to CI, $0 incremental.

## The honest ROI

The supply-chain hardening was 2 weeks of work. It's saved us from
zero CVEs so far (knock on wood). It's saved us from approximately
zero bad releases.

It *has*, however, given us three things that show up in the
procurement conversation:

1. **Audit teams stop asking "is this SBOM-attested?"** — the answer is
   on the release page.
2. **Compliance officers cite the SLSA L3 receipt** in their internal
   documentation. We get logos-in-our-favor we didn't pay for.
3. **The "show me your supply chain" question has a one-line answer.**
   That's worth the 2 weeks.

## What I'd do differently

- **Earlier.** I waited until v1.4 to add SLSA. Adding it at v0.1
  would have been 30 % less work.
- **Together, not in batches.** Adding each item one at a time meant
  each PR was a separate review cycle. Bundling them into a single
  "supply-chain hardening" PR at v0.5 would have been more efficient.
- **With a target in mind.** I built each item because the next audit
  team asked for it. Listing all of them upfront (this article is the
  list) is the better path.

## Try it on your project

The repo for the project this article is about:

📦 https://github.com/Mine-FNL/qstocks-filing-tool

The full architecture is documented in
[`whitepaper/whitepaper.md`](https://github.com/Mine-FNL/qstocks-filing-tool/blob/main/whitepaper/whitepaper.md)
and the supply-chain pipeline is in §4.2.

Star the repo if this checklist is useful.
```

## Tags

`opensource`, `devops`, `security`, `supply-chain`, `ci-cd`, `github-actions`, `python`

## Submission notes

- Hacker Noon accepts open submissions via their editorial form.
  Lead time: 2–4 weeks.
- DevOps.com accepts contributed articles; pitch via the editor first
  (similar to the InfoQ pitch).
- Cross-link from the repo's `README.md` after publication.
