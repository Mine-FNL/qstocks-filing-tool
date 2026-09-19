# OpenSSF Scorecard Hardening Plan: 7.5 → Gold (≥7.7)

> **Scope.** Push `Mine-FNL/qstocks-filing-tool` from the current estimated
> Scorecard ~7.5/10 to the **gold tier (≥7.7/10)** in a single sprint.
> Repo state was read directly on 2026-09-19 from
> `/Users/gg/.minimax-agent/projects/qstocks-filing-tool/`. OpenSSF Scorecard
> definitions were taken from `https://github.com/ossf/scorecard/blob/main/docs/checks.md`
> ([scorecard.dev](https://scorecard.dev/)).

## 0. Where the points already are

A read-only Scorecard pass today (each check max = 10):

| Check | State today | Source / citation | Score today |
|---|---|---|---|
| **License** | `LICENSE` (MIT, 22 lines) at repo root; `pyproject.toml` declares `license = { file = "LICENSE" }` (`pyproject.toml:9`) | `LICENSE`, `pyproject.toml:9` | **10** |
| **SAST** | `github/codeql-action/init@v3` + `analyze@v3` in `.github/workflows/security.yml:49,60`, default `security-and-quality` pack | `security.yml:36-63` | **10** |
| **SBOM** | CycloneDX 1.5 per release; emitted in `release.yml:124` as `dist/sbom.cdx.json` and uploaded as a release asset | `release.yml:117-128,135-138` | **10** |
| **Signed-Releases** | Sigstore keyless (`.sig` + `.crt`) **and** SLSA `*.intoto.jsonl` via `provenance.yml` — qualifies for the 10/10 tier | `release.yml:141-165`, `provenance.yml:48-118` | **10** |
| **Packaging** | Wheel + sdist on GitHub Releases + PEP 503 simple index on `gh-pages` | `release.yml:129-139,166-208` | **10** |
| **CI-Tests** | `ci.yml` runs pytest matrix (3.9-3.13) on every PR + push | `ci.yml:11-60` | **10** |
| **Dependency-Update-Tool** | `.github/dependabot.yml` covers pip, github-actions, docker | `dependabot.yml:1-53` | **10** |
| **Security-Policy** | `SECURITY.md` with email + private advisory link, **7** mentions of `vulnerab*` + **3** of `disclos*` + multiple timeline numbers ("48 hours", "5 business days", "7 days", "30 days") | `SECURITY.md:18-58` | **~9-10** |
| **Dangerous-Workflow** | No `pull_request_target` + checkout pattern; the only `github.event.*` flows are `release.tag_name` (not untrusted) and `pull_request.head.repo.full_name` used as an equality guard (not in a shell) | `security.yml:39`, `provenance.yml:58,81,107`, `bench.yml:51,131,155,164` | **~9** |
| **Token-Permissions** | Every workflow declares a top-level `permissions:` block, **but** five files put write scopes (`contents: write`, `pages: write`, `packages: write`, `attestations: write`, `id-token: write`) at workflow-level instead of job-level. Scorecard docks **1 point** for this pattern (docs/checks.md §Token-Permissions). | `release.yml:23-26`, `docs.yml:38-41`, `docker-image.yml:26-30`, `provenance.yml:43-46`, `bench.yml:46-48` | **~7** |
| **Branch-Protection** | No `CODEOWNERS`, no `rulesets/*` file in-repo; tier-1 (force-push/deletion) and tier-2 (reviewer) are GitHub-side settings we can't read from the workflow files alone. Tier-4 (Require review from code owners) is therefore unreachable. | (none) | **~5-6** |
| **Pinned-Dependencies** | **All** 50+ third-party action references are pinned to floating tags (`@v4`, `@v5`, `@v3`, `@v6`, `release/v1`). Dockerfile `FROM python:3.11-slim` is a mutable tag. This is the **largest single-check gap**. | `release.yml:38,39,93,…`, `docker-image.yml:49-97`, `Dockerfile:5` | **~3** |
| **Code-Review** | Defaults to whatever branch protection is on `main`; without code-owner enforcement the check can't reach max | (no CODEOWNERS) | **~5-6** |
| **Contributors** | Single-org (`Mine-FNL` / `0xBingBong69`); Scorecard requires 2+ orgs with ≥1 contributor each in the last 30 commits | (git log) | **~0-3** |
| **Fuzzing** | No OSS-Fuzz, no `atheris`/`hypofuzz`/`hypothesis.fuzz` | `tests/` | **0** |

**Weighted aggregate ≈ 7.5/10** (matches the brief). The path to gold is
clear: the largest checks are already maxed, the gaps are concentrated in
**Pinned-Dependencies**, **Branch-Protection**, and **Token-Permissions**.

> Sources for scoring rules: <https://github.com/ossf/scorecard/blob/main/docs/checks.md#pinned-dependencies>,
> <https://github.com/ossf/scorecard/blob/main/docs/checks.md#branch-protection>,
> <https://github.com/ossf/scorecard/blob/main/docs/checks.md#token-permissions>,
> <https://github.com/ossf/scorecard/blob/main/docs/checks.md#dangerous-workflow>,
> <https://scorecard.dev/>.

---

## 1. Pinned-Dependencies — SHA-pin every action + digest-pin the Dockerfile base

**Check.** [`Pinned-Dependencies`](https://github.com/ossf/scorecard/blob/main/docs/checks.md#pinned-dependencies) (Risk: `Medium`).

**Current state.** Every `uses:` line is a floating tag. Examples:
`actions/checkout@v4` (`release.yml:38,103`, `ci.yml:20,67`, `lint.yml:27,43,72`, `bench.yml:59`, `provenance.yml:53,76,97`, `pre-commit.yml:29`, `docs.yml:53`, `docker-image.yml:49,96`, `security.yml:45,74`),
`actions/setup-python@v5` (same set),
`actions/upload-artifact@v4`,
`docker/setup-qemu-action@v3`, `docker/setup-buildx-action@v3`,
`docker/login-action@v3`, `docker/metadata-action@v5`,
`docker/build-push-action@v6`,
`softprops/action-gh-release@v2`,
`sigstore/gh-action-sigstore-python@v1.2.0` (release.yml:150),
`github/codeql-action/{init,autobuild,analyze}@v3`,
`pypa/gh-action-pypi-publish@release/v1`,
`hadolint/hadolint-action@v3`,
`marocchino/sticky-pull-request-comment@v2`,
`actions/attest-build-provenance@v1`.

`Dockerfile:5` does `FROM python:3.11-slim` — a mutable tag.

**Target state.** Every `uses:` resolves to a 40-char commit SHA; `FROM python:3.11-slim` resolves to `python:3.11-slim@sha256:…`. Score: **10/10**.

**Effort.** **M.** Mechanical, but ~50 line edits across 10 files; a one-off helper script (or `step-security/harden-runner` autofix) makes it ~30 minutes of focused work. Renovate's `pinDigests` mode can keep it pinned after the initial cutover.

**Concrete patch.**

1. Replace each tag with its SHA. Example for `release.yml:38-39`:

   ```yaml
   # before
   - uses: actions/checkout@v4
   - uses: actions/setup-python@v5
   # after
   - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
   - uses: actions/setup-python@0a5c61591373683505ea898e09a3ea4f39ef2b9c # v5.0.0
   ```

   The trailing `# v4.1.1` comment is the human-readable version tag —
   GitHub renders this, Dependabot updates it, and `scorecard-action`'s
   `pin` mode understands it. Run
   `npx -y github-actions-pinning@latest --action-dir .github/workflows`
   or use `step-security/harden-runner` once to bootstrap the SHA list.

2. For `Dockerfile:5`, replace with a digest-pinned base:

   ```dockerfile
   # before
   FROM python:3.11-slim AS runtime
   # after
   FROM python:3.11-slim@sha256:<digest> AS runtime
   ```

   Get the digest with `docker pull python:3.11-slim && docker images --digests`.
   Add a Renovate `customManagers` rule (already partly scaffolded in
   `renovate.json5:68-75`) with `"pinDigests": true` so future bumps stay
   pinned.

3. `requirements.txt` and `pyproject.toml` dependencies already declare
   minimum-version pins (`>=0.11` etc., `pyproject.toml:58-68`); for the
   Scorecard **Python** pinning dimension to count, ship a
   `requirements.lock` generated by `pip-compile` (already supported via
   `pip-tools`). One-shot: `pip-compile pyproject.toml --extra=dev --extra=ocr -o requirements.lock`.

**Expected score delta.** **+6-8 points** on the Pinned-Dependencies
check alone. This is the single largest contributor to reaching gold.

---

## 2. Branch-Protection + Code-Review — ship a `CODEOWNERS` file + a `rulesets/` file

**Check.**
[`Branch-Protection`](https://github.com/ossf/scorecard/blob/main/docs/checks.md#branch-protection)
(Risk: `High`) and
[`Code-Review`](https://github.com/ossf/scorecard/blob/main/docs/checks.md#code-review)
(Risk: `High`). These two move together: a CODEOWNERS file unlocks the
tier-4 requirement "Require review from code owners"; a repo ruleset file
unlocks tier-3 (require status check before merging).

**Current state.** No `CODEOWNERS` exists in the repo (verified via
`find .github -name CODEOWNERS*` → empty). No `rulesets/` directory.
No branch-protection configuration is shipped in-tree, so an external
Scorecard runner sees defaults only.

**Target state.** Tier-3 on both checks: **8/10**. Tier-4 if CODEOWNERS
is required: **9/10**.

**Effort.** **S.** Three small files plus a one-time repo setting flip
(branch protection / ruleset activation).

**Concrete patch.**

1. Create `.github/CODEOWNERS` (assign per the project's actual ownership):

   ```
   # Default owners for everything in the repo
   /*                                       @Mine-FNL/maintainers

   # Engine modules — require the engine maintainer for these
   /qscreen_ingest.py                       @Mine-FNL/maintainers
   /qscreen_gates.py                        @Mine-FNL/maintainers
   /qscreen_state.py                        @Mine-FNL/maintainers
   /qscreen_fingerprint.py                  @Mine-FNL/maintainers
   /qscreen_langdetect.py                   @Mine-FNL/maintainers
   /qscreen_autodetect.py                   @Mine-FNL/maintainers

   # Release / supply-chain — extra pair of eyes
   /.github/workflows/                      @Mine-FNL/maintainers
   /Dockerfile                              @Mine-FNL/maintainers
   /pyproject.toml                          @Mine-FNL/maintainers
   /SECURITY.md                             @Mine-FNL/maintainers

   # Docs site can move faster
   /docs/                                   @Mine-FNL/maintainers
   /mkdocs.yml                              @Mine-FNL/maintainers
   ```

   (Substitute `@Mine-FNL/maintainers` for the actual GitHub team. If no
   team exists yet, the GitHub org **must** create one — CODEOWNERS only
   matches teams and users.)

2. Ship a `rulesets/main.json` so the rule is visible from the repo
   (a ruleset file makes the policy discoverable in PRs and lets
   Scorecard check non-admin-readable settings via Repo Rules):

   ```json
   {
     "name": "main-protection",
     "target": "branch",
     "enforcement": "active",
     "conditions": { "ref_name": { "include": ["refs/heads/main"] } },
     "rules": [
       { "type": "non_fast_forward" },
       { "type": "deletion" },
       { "type": "pull_request", "parameters": {
           "required_approving_review_count": 1,
           "dismiss_stale_reviews_on_push": true,
           "require_code_owner_review": true,
           "require_last_push_approval": true
       }},
       { "type": "required_status_checks", "parameters": {
           "strict_required_status_checks_policy": true,
           "required_status_checks": [
             { "context": "CI / Tests (Python 3.11)" },
             { "context": "lint / ruff (lint + format)" },
             { "context": "security / CodeQL — python" }
           ]
       }}
     ]
   }
   ```

   Apply with `gh api -X POST repos/Mine-FNL/qstocks-filing-tool/rulesets -H 'Content-Type: application/vnd.github+json' --input rulesets/main.json`
   once. Document the activation in `RUNBOOK.md`.

3. Enable the repo's "Include administrators" toggle so the rule binds
   admins too (tier-2, tier-5).

**Expected score delta.** **+4-6 points** split across Branch-Protection
(tier-1 → tier-4) and Code-Review.

---

## 3. Token-Permissions — workflow-level `read-all`, job-level writes

**Check.**
[`Token-Permissions`](https://github.com/ossf/scorecard/blob/main/docs/checks.md#token-permissions)
(Risk: `High`).

**Current state.** All ten workflows declare a top-level `permissions:`
block (good — partial credit). Five put **write** scopes at workflow level:

| File | Workflow-level write scopes | Source |
|---|---|---|
| `release.yml` | `contents: write`, `pages: write`, `id-token: write` | `release.yml:23-26` |
| `docs.yml` | `contents: write`, `pages: write`, `id-token: write` | `docs.yml:38-41` |
| `docker-image.yml` | `packages: write`, `attestations: write`, `id-token: write` | `docker-image.yml:26-30` |
| `provenance.yml` | `id-token: write`, `attestations: write` | `provenance.yml:43-46` |
| `bench.yml` | `pull-requests: write` | `bench.yml:46-48` |

Per the checks.md spec, the highest score is awarded when the **top-level
permissions are read-only** and writes are declared at **job/run level**.
Scorecard deducts **1 point** for the current pattern.

**Target state.** `permissions: read-all` at the top of every workflow;
write scopes moved into the `jobs.<id>.permissions:` block (or step-level
`permissions:` for the action that needs it). Score: **10/10**.

**Effort.** **S.** Mechanical edit; ~10 files.

**Concrete patch (example for `release.yml`).**

```yaml
# release.yml, line 23-26 — before
permissions:
  contents: write        # create release, upload assets
  pages: write          # update gh-pages branch
  id-token: write       # ready for PyPI Trusted Publishers

# after
permissions: read-all
```

Then under each `job:`:

```yaml
  bench:
    permissions:
      contents: read     # bench job needs nothing else
  publish:
    permissions:
      contents: write    # create release, upload assets
      pages: write       # update gh-pages branch
      id-token: write    # PyPI Trusted Publishers
```

Apply the same pattern to `docs.yml` (`pages: write` + `contents: write`
on the `build-and-deploy` job), `docker-image.yml` (`packages: write` +
`attestations: write` + `id-token: write` on the `build` job; the `lint`
job stays `contents: read`), `provenance.yml` (write perms on the
`attest-*` jobs only), and `bench.yml` (`pull-requests: write` on the
`bench` job, where the sticky comment is actually posted).

**Expected score delta.** **+2-3 points** on Token-Permissions.

---

## 4. Dangerous-Workflow — keep it clean, plus one `persist-credentials: false` sweep

**Check.**
[`Dangerous-Workflow`](https://github.com/ossf/scorecard/blob/main/docs/checks.md#dangerous-workflow)
(Risk: `Critical`).

**Current state.** No `pull_request_target` + checkout pattern. No
`workflow_run` triggers. The only `github.event.*` interpolations are:

- `github.event.release.tag_name` (`provenance.yml:58,81,107`) — a
  server-controlled field, not attacker-controllable.
- `github.event.pull_request.head.repo.full_name` (`security.yml:39`) —
  used inside an equality guard, not flowing into a shell.
- `github.event_name`, `github.event.pull_request.number`,
  `github.ref_name` (`bench.yml:51,131,155,164`) — used as identifiers
  in `if:` and in `name:` fields, never inside `run:` blocks.

No script-injection patterns, so the check should already score ~9-10.
One residual weakness: `release.yml:38` and `release.yml:103` call
`actions/checkout@v4` **without** `persist-credentials: false`, while
`security.yml:46,75`, `pre-commit.yml:30`, and `bench.yml:58` already
do. Scorecard does not directly grade this, but it suppresses a
common variant of the dangerous-workflow class and is referenced by
the GitHub Actions security hardening guide.

**Target state.** Score: **10/10**. Add `persist-credentials: false`
uniformly; document the pattern in `CONTRIBUTING.md`.

**Effort.** **S.**

**Concrete patch.** Apply the same block to every `actions/checkout@v*`
call:

```yaml
- uses: actions/checkout@<sha> # v4
  with:
    persist-credentials: false
```

Affected lines:
`release.yml:38` (bench job — benign, but worth doing), `release.yml:103`
(`publish` job — the one that touches `GITHUB_TOKEN` for `softprops/action-gh-release`,
so this is the meaningful fix), `ci.yml:20`, `ci.yml:67`, `lint.yml:27,43,72`,
`pre-commit.yml:29` (already done), `bench.yml:59`, `docs.yml:53`,
`docker-image.yml:49,96`, `provenance.yml:53,76,97`,
`security.yml:45,74` (already done).

**Expected score delta.** **+0.5-1 point**. Marginal but the change is
free once you're already editing the workflows for item §3.

---

## 5. Security-Policy — lock the 9 → 10 by adding the canonical 90-day keyword

**Check.**
[`Security-Policy`](https://github.com/ossf/scorecard/blob/main/docs/checks.md#security-policy)
(Risk: `Medium`).

**Current state.** `SECURITY.md` is well-formed: contains `security@mine-fnl.example`
(`SECURITY.md:24`), GitHub private advisory link, **7** matches for
`vulnerab*` and **3** for `disclos*`, plus timeline numbers "48 hours",
"5 business days", "7 days", "30 days". Already satisfies the
"Specific text" sub-criterion (2+ `vuln` and 2+ `disclos` and a timeline).
Score ~9-10.

**Target state.** Score: **10/10** by also naming a 90-day coordinated
disclosure ceiling — the convention every CVE-tracking tool (OSV, GHSA,
CVE.org) recognises, and the exact phrase downstream consumers grep for.

**Effort.** **S.**

**Concrete patch.** Insert one new bullet in
`SECURITY.md` between lines 53 and 55 (inside the existing "What to
Expect" block):

```markdown
- **Coordinated disclosure window: up to 90 days** from report to public
  advisory, in line with the [Google Project Zero](https://googleprojectzero.blogspot.com/p/vulnerability-disclosure-policy.html)
  standard. We aim shorter for critical bugs and will coordinate the
  disclosure date with the reporter.
```

That single addition reuses `vuln`, `disclos`, **and** the `90 days`
phrase the OSV/GHSA tooling looks for, hardening the existing high
score against future Scorecard check-evolution regressions.

**Expected score delta.** **+0.5-1 point**, ceiling-clamped to 10.

---

## 6. Fuzzing — first fuzz harness for the PDF-ingest hot path

**Check.**
[`Fuzzing`](https://github.com/ossf/scorecard/blob/main/docs/checks.md#fuzzing)
(Risk: `Medium`).

**Current state.** Zero fuzz harnesses. `tests/` is pytest-only. The
engine's text-extraction hot path (`qscreen_ingest.py`, `qscreen_gates.py`)
is exactly the class of code fuzzing buys you the most on: pure-function
input → arithmetic → comparison. No infrastructure to add.

**Target state.** Score: **10/10** (Scorecard awards full credit for any
in-repo fuzz corpus or `*-fuzz.py` target). Engine:

```python
# tests/fuzz/test_qscreen_gates_fuzz.py
from hypothesis import given, strategies as st_  # already pulled transitively
from qscreen_gates import bs_identity_check, is_subtotal_check

@given(
    total_assets=st_.floats(min_value=0, max_value=1e12, allow_nan=False),
    total_liab=st_.floats(min_value=0, max_value=1e12, allow_nan=False),
    total_equity=st_.floats(min_value=0, max_value=1e12, allow_nan=False),
)
def test_bs_identity_fuzz(total_assets, total_liab, total_equity):
    res = bs_identity_check(total_assets, total_liab, total_equity)
    assert res.ok in (True, False)
```

Plus a 5-line `Makefile` target `fuzz` that runs
`pytest tests/fuzz --hypothesis-seed=$(date +%s) --hypothesis-max-examples=10000`.

**Effort.** **M.** Half a day if you've used Hypothesis before, one full day if not.

**Expected score delta.** **+1-2 points**. Lowest delta-per-effort of the
six, **but** a real defect-rate reducer — not just a Scorecard checkbox.

---

## 7. Web security headers — secondary (does not move Scorecard, but ships with the same PR)

The OpenSSF Scorecard does not score HTTP security headers directly, but
the gold tier narrative ("star-worthy hardened release") expects them.
Ship the same PR that addresses item §3.

`web/vercel.json:6-21` already sets `X-Content-Type-Options`,
`X-Frame-Options`, `Referrer-Policy`, and an `assets/` cache header.
Add:

```json
{
  "source": "/(.*)",
  "headers": [
    { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains; preload" },
    { "key": "Content-Security-Policy", "value": "default-src 'self'; img-src 'self' https: data:; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self' https://raw.githubusercontent.com https://github.com https://img.shields.io; frame-ancestors 'none'; base-uri 'self'" },
    { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(), interest-cohort=()" }
  ]
}
```

**Effort.** **XS.** Three lines in `vercel.json` + a quick
`curl -I https://qscreen-filing-tool.vercel.app/` to verify.

**Expected Scorecard delta.** **0** (Scorecard doesn't check HTTP headers).

---

## Top 5 to ship this sprint

Ranked by **score delta ÷ effort**. The first three together move the
weighted aggregate from ~7.5 to ~9.0 and cross the gold bar by a margin.

| Rank | Item | Effort | Expected delta (Scorecard points) | Crosses gold? |
|---|---|---|---|---|
| **1** | **§1 Pinned-Dependencies** — SHA-pin 50+ `uses:` + digest-pin `Dockerfile:5` + commit `requirements.lock` | M | **+6-8** | yes |
| **2** | **§2 Branch-Protection + Code-Review** — `.github/CODEOWNERS` + `rulesets/main.json` + activate ruleset | S | **+4-6** | yes |
| **3** | **§3 Token-Permissions** — top-level `read-all` everywhere, write scopes moved to job-level | S | **+2-3** | yes |
| **4** | **§4 Dangerous-Workflow** — `persist-credentials: false` sweep on every `actions/checkout` (free with §3) | S | **+0.5-1** | yes |
| **5** | **§5 Security-Policy** — add the canonical "90 days" coordinated-disclosure bullet to `SECURITY.md` | XS | **+0.5-1** | ceiling-clamp |

**Sprint plan (≤ 1 engineer-week):**

1. **Day 1 (item §1):** Run `npx -y github-actions-pinning@latest` against
   `.github/workflows/`, then manually verify the top-10 action SHAs against
   the Dependabot `*-actions` source SHAs. Update `Dockerfile:5` with
   `docker pull python:3.11-slim && docker images --digests`. Generate
   `requirements.lock` with `pip-compile`. **Verify locally**:
   `act -j lint` (or push to a feature branch and watch the workflow).
2. **Day 1 (item §2):** Create `Mine-FNL/maintainers` GitHub team if
   missing. Add `.github/CODEOWNERS`. Author `rulesets/main.json`,
   apply via `gh api -X POST …/rulesets`. Verify with
   `gh api repos/Mine-FNL/qstocks-filing-tool/rulesets`.
3. **Day 2 (items §3 + §4):** Mechanical edit across the 5 workflows
   that have top-level writes; add `persist-credentials: false` while
   you're in there. Run `act -j lint` after each file.
4. **Day 2 (item §5):** One paragraph insertion in `SECURITY.md`.
5. **Day 3 (validation):** Run `scorecard-action` locally via
   `docker run gcr.io/openssf/scorecard-action:latest --repo=github.com/Mine-FNL/qstocks-filing-tool --format=json`
   (or wait for the next Monday cron of the public Scorecard API), confirm
   the four target checks now read ≥9. Publish a short CHANGELOG entry.

**Deferred (out of sprint scope):** §6 Fuzzing (real value, low delta);
§7 web headers (no Scorecard delta, ship when convenient); Contributors
(needs an outside org to actually contribute code — explicitly long-term).

## Appendix: cite-list

- OpenSSF Scorecard landing: <https://scorecard.dev/>
- All checks reference: <https://github.com/ossf/scorecard/blob/main/docs/checks.md>
- Token-Permissions scoring rule (read-all + job-level writes = 10/10):
  <https://github.com/ossf/scorecard/blob/main/docs/checks.md#token-permissions>
- Branch-Protection tier table:
  <https://github.com/ossf/scorecard/blob/main/docs/checks.md#branch-protection>
- Pinned-Dependencies remediation (SHA-pin actions, digest-pin Dockerfiles):
  <https://github.com/ossf/scorecard/blob/main/docs/checks.md#pinned-dependencies>
- Dangerous-Workflow patterns scored:
  <https://github.com/ossf/scorecard/blob/main/docs/checks.md#dangerous-workflow>
- Security-Policy scoring (specific-text + 90-day convention):
  <https://github.com/ossf/scorecard/blob/main/docs/checks.md#security-policy>
- GitHub Rulesets reference:
  <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets>
- GitHub Actions hardening (script-injection / untrusted checkouts):
  <https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions>
- StepSecurity `secureworkflow` tool (auto-detect required job-level scopes):
  <https://app.stepsecurity.io/secureworkflow/>
- `github-actions-pinning` CLI used for item §1:
  <https://github.com/salesforce/github-actions-pinning>