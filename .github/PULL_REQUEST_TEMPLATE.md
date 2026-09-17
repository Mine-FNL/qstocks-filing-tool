## What does this change?

One-paragraph summary of the change and why.

## Is it behaviorally observable?

- [ ] A new unit test covers it (`tests/test_*.py`)
- [ ] I ran `python qscreen_eval.py` and the golden-set baseline did not regress (record the score below)
- [ ] If this touches the offline/CLI surface, I ran `qscreen-ingest --self-test` locally

## Pre-flight

- [ ] CI matrix on the PR is green (Python 3.9–3.13 + the Flask `/healthz` smoke job)
- [ ] `CHANGELOG.md` updated under the next-version section
- [ ] If a new top-level module was added, it appears in `pyproject.toml [tool.setuptools].py-modules`

## Risk

Mark one:
- **docs only** — no code change
- **low** — new module, additive, behind a feature flag or `--no-…` opt-out
- **medium** — changes a default, a gate, or the JSON schema
- **high** — affects batch / state / upload semantics

## Notes for reviewer

Anything that isn't obvious from the diff: edge cases I considered, alternatives I rejected, decisions that were judgment calls.
