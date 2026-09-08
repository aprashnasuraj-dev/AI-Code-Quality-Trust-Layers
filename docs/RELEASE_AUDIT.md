# RepoVerity v0.1.0 Release Audit

Status labels in this document are literal: **VERIFIED**, **FAILED**, **PARTIALLY VERIFIED**, **NOT VERIFIABLE IN THIS ENVIRONMENT**, or **DEFERRED BY DESIGN**.

## Environment

- Local audit date: 2026-09-08
- Workspace: public candidate reconstructed from the preserved RepoVerity 0.1.0 sdist plus regenerated development/release scaffolding
- OS: Linux 6.18.35 x86_64
- Python: 3.13.5
- pip: 25.1.1
- Git: 2.47.3
- Candidate Git SHA: pending initial source commit

## Summary

| Gate | Status | Evidence |
| --- | --- | --- |
| Core pytest | VERIFIED | 102 collected tests pass after final local code changes |
| Compile | VERIFIED | `python -m compileall -q src tests scripts` |
| Rule fixture matrix | VERIFIED | 18 rules × bad/good/edge = 54 deterministic fixture cases materialized into temporary projects; intended rule fires only in the bad case |
| Self-audit | VERIFIED | 0 findings / 0 analysis issues after excluding intentionally-bad demo fixture |
| YAML syntax | VERIFIED | PyYAML 6.0.3 parses all `.yml`/`.yaml`; integration test guards drift |
| Target-code no-execution | VERIFIED | malicious import-time marker fixture remains unexecuted |
| Symlink boundary | VERIFIED | symlinked `.py` is skipped and reported |
| Baseline semantics | VERIFIED | new/existing/resolved plus malformed/future/duplicate baseline tests |
| Changed-only | VERIFIED | committed, staged/unstaged, untracked, detached, missing-base and non-Git cases |
| Report formats | VERIFIED | terminal, JSON, Markdown and SARIF tests, including hostile path/text escaping |
| Local Ruff | NOT VERIFIABLE IN THIS ENVIRONMENT | package-index DNS failure; hosted CI configured to run it |
| Local mypy | NOT VERIFIABLE IN THIS ENVIRONMENT | package-index DNS failure; hosted CI configured to run it |
| Local `python -m build` | NOT VERIFIABLE IN THIS ENVIRONMENT | build frontend unavailable; backend build is executed separately |
| Local Twine | NOT VERIFIABLE IN THIS ENVIRONMENT | package-index DNS failure; hosted CI configured to run it |
| GitHub-hosted CI | PENDING | evaluated after first push |
| GitHub composite Action | PENDING | hosted `uses: ./` smoke workflow prepared |
| GitHub SARIF ingestion | PENDING | push-to-main SARIF workflow prepared |
| CodeQL | PENDING | hosted workflow prepared |
| PyPI Trusted Publishing | NOT VERIFIABLE IN THIS ENVIRONMENT | requires owner-side PyPI publisher configuration and release tag |

## Local toolchain retry

An isolated development-environment install was attempted. pip failed while resolving the declared setuptools build dependency with repeated `Temporary failure in name resolution`; therefore Ruff, mypy, build frontend and Twine are not relabeled as local PASS.

## Core tests

Final pre-commit commands will be rerun after the Git index is frozen. The current reconstructed suite contains 102 tests and includes 54 parameterized rule-fixture cases materialized from one deterministic corpus.

## Security and adversarial behavior

VERIFIED locally:

- target `sitecustomize.py` and package `__init__.py` with marker-file side effects are parsed but never executed;
- symlinked sources are not followed;
- malformed syntax and binary `.py` input become analysis issues instead of crashing the audit;
- >1 MB source files hit the documented per-file limit;
- Unicode/space filenames are analyzed;
- generated-file markers are skipped;
- Git subprocess calls use argument arrays, no `shell=True`, and read-only commands;
- public-source grep review found no credential/private-path exposure. The only TODO occurrence in fixture source is an intentional comment-rule counterexample.

## Performance

See `docs/BENCHMARKS.md`: 1k = 1.3204 s / 100.8 MiB, 10k = 1.5309 s / 110.5 MiB, 50k = 2.5092 s / 169.3 MiB.

## PyPI name check

Current web/PyPI search on 2026-09-08 surfaced no exact `repoverity` project. Local `pip index versions repoverity` could not complete because DNS failed. Treat the distribution name as apparently unclaimed, not reserved; recheck immediately before any publication.

## Deferred by design

- DEP104/DEP105-style environment or installed-symbol validation that would risk misrepresenting environment absence or require user-module import.
- second language pack;
- standalone native binaries;
- automatic architecture rewrites;
- AI-authorship probability/global trust score.

## GitHub-hosted validation

Pending first push. This section will be updated with exact commit SHA, workflow run IDs and log-derived evidence after hosted execution.

## Release recommendation

**READY FOR SOURCE CANDIDATE FREEZE; NOT READY FOR v0.1.0 TAG** until hosted Ruff/mypy/build/Twine, composite Action, and critical CI gates execute successfully and the PyPI publisher setup is understood.
