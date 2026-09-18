# X thread — SHA-256 fingerprint stability (8 tweets)

**Asset:** none — pure text thread (numbers land harder without imagery).
**Use:** Long-tail technical credibility thread for the Sigstore / supply-chain crowd. Post 10–14 days after the launch thread.

---

**1/** "Re-ingest the same PDF, get a different JSON" is the silent killer of financial data pipelines.

We fixed it with three properties:

1. Canonical SHA-256 over the normalised JSON content
2. Sigstore keyless signing on every release
3. SLSA Build L3 provenance attestation

Here's how the chain works. 🧵

**2/** Step 1 — canonicalisation.

```python
import json, hashlib

def fingerprint(record: dict) -> str:
    canonical = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    # exclude engine-version-specific fields
    return hashlib.sha256(canonical).hexdigest()
```

Same record → same hash, forever, on any platform.

**3/** Step 2 — bind the fingerprint to the engine commit.

```
fingerprint = sha256(canonical_json)
build       = sigstore.sign(wheel)              → signature bundle
provenance  = slsa.attest(wheel, build, source) → in-toto receipt
```

The receipt binds:
- the wheel → the source commit → the runner → the SBOM.

`gh attestation verify <wheel> --bundle <sig>` returns exit 0.

**4/** Step 3 — chain it all back to the PDF.

```
PDF sha256:abc123 → engine v1.6.0 + build sig → JSON fingerprint f7b9...cd14
                 ↘ SLSA receipt: provenance = (commit, runner, sbom, ts)
```

The chain is:

**the PDF produced this JSON on this commit, and you don't have to
trust the operator to verify it**.

**5/** Why this matters for downstream pipelines:

```python
if record["fingerprint"] == db.lookup(pdf_hash):
    skip_re_extraction()   # bit-identical; don't waste compute
else:
    re_extract_with_latest_engine()
    diff_to_old_record()
```

Most pipelines re-extract every quarter because they can't trust
hash stability. This avoids that.

**6/** What we exclude from the fingerprint (and why):

```
@extracted_at   (wall-clock; not part of the data)
@engine_version (informational; not part of the data)
@runner_id      (CI-specific)
```

Everything else — every line item, every note, every segment, every
gate result — is in the hash.

**7/** The honest ceiling:

Fingerprint stability is a **necessary** property, not a **sufficient**
one. A bad extraction that is bit-identical across upgrades is still a
bad extraction.

The fingerprint pins *what was produced*. It doesn't certify *that it
was correct*. That's what the bench gate (§5 in the whitepaper) is for.

**8/** Where this is going:

- Witness the fingerprint chain in a public Sigstore Rekor log
  (currently we sign the wheel; not yet the per-record fingerprint).
- Verifiable-claims API: anyone can POST a fingerprint and get back
  the engine version + PDF hash that produced it.

📦 https://github.com/Mine-FNL/qstocks-filing-tool
📄 §3.3 + Appendix B in the whitepaper

If you ship data pipelines, fingerprint stability should be on your
radar. RT appreciated. 🤝

---

**Posting notes:**

- This thread is targeted at the Sigstore / supply-chain crowd; it
  will underperform on impressions but over-perform on quality
  engagements.
- Pin a link to Appendix B (verifying a release) in the replies.
