# RepoVerity v0.1.0 Release Audit

This audit records verified release evidence. A status is **PASS** only when the corresponding check actually ran successfully.

## Evidence-producing source candidate

- Source candidate SHA: `29d44017fff79301e7159cf3e838558c08c1d408`
- Validation date: 2026-09-09
- Hosted validation OS: Ubuntu 24.04.4 / Windows GitHub-hosted runner
- Release-validation Python: 3.13.15
- Main CI run: `34298883752`
- Release validation run: `34298883741`
- Composite Action run: `34298883703`
- RepoVerity SARIF run: `34298883781`
- CodeQL run: `34298883725`

This file is itself committed after the evidence above was collected. That documentation-only recording commit must pass the same workflows before the repository is considered ready to tag; the authoritative final SHA and final-run artifact hashes are therefore the latest green `main` workflow evidence, not a self-referential SHA embedded in this file.

## Verification matrix

| Area | Result | Evidence |
| --- | --- | --- |
| pytest | PASS | 107 tests passed in hosted quality CI |
| compileall | PASS | `python -m compileall -q src tests` in Release validation |
| self-audit | PASS | 0 findings / 0 analysis issues; every severity count is zero |
| Ruff | PASS | Ruff 0.16.6: `All checks passed!` |
| Ruff format | PASS | 67 files already formatted |
| mypy | PASS | strict mode; no issues found in 30 source files |
| Python 3.11 | PASS | dedicated hosted job |
| Python 3.14 | PASS | dedicated hosted job |
| Windows | PASS | hosted Windows pytest job; prior locale/UTF-8 failure is resolved |
| build | PASS | wheel and sdist built successfully |
| Twine | PASS | wheel and sdist both PASSED |
| wheel clean install | PASS | clean venv, `--no-index --no-deps`, import verified from site-packages, known-good audit clean |
| sdist reconstruction | PASS | sdist extracted, wheel rebuilt, clean venv installed, known-good audit clean |
| composite Action | PASS | local `uses: ./` workflow succeeded |
| SARIF generation | PASS | RepoVerity SARIF workflow generation step succeeded |
| SARIF upload | PASS | GitHub code-scanning upload step succeeded |
| CodeQL | PASS | CodeQL init/analyze workflow succeeded |
| 1k benchmark | RECORDED | 1,000 analyzed LOC; 0.2182 s; 26.0 MiB max RSS |
| 10k benchmark | RECORDED | 10,000 analyzed LOC; 0.5346 s; 37.2 MiB max RSS |
| 50k benchmark | RECORDED | 50,000 analyzed LOC; 1.9453 s; 89.5 MiB max RSS |
| recovery-artifact removal | PASS | no `release-fix` paths in the recursively inspected tree |

## Benchmark environment

The fresh benchmark run used Python 3.13.15 on `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`.

`ru_maxrss` is converted from bytes on macOS and KiB on the Linux validation host. Each generated benchmark project is temporary, requested LOC equals analyzed LOC exactly, subprocess failures propagate, and the benchmark records the repository SHA returned by Git.

## Source-candidate artifacts

The source-candidate Release validation workflow produced:

- `repoverity-0.1.0-py3-none-any.whl`
  - SHA-256: `0ad63e821acdfcaaf93133591335bdfe4aeae2d0d2db497b91c31e61a87fff10`
- `repoverity-0.1.0.tar.gz`
  - SHA-256: `b5ad9c18cbb81423f2c5562662bfee9cc136cd47347838afa30bda605ee99da6`

The authoritative hashes for the eventual tag candidate must be taken from the Release validation artifact generated for the exact final `main` SHA, because archive metadata may change between builds.

## Security and adversarial behavior

Regression coverage includes target-code non-execution, symlink boundaries, malformed/binary/oversized input handling, dynamic imports, baseline fingerprint stability, changed-only rename/deletion/no-commit/detached-HEAD behavior, deterministic JSON/Markdown/SARIF output, SARIF rules/locations/fingerprints, hidden/default directory and `.venv` exclusion, workflow YAML parsing, release-workflow contract, and Action argument safety.

Production source uses no `shell=True`, `os.system`, `eval`, or `exec` path. Git subprocesses use argument arrays rather than shell interpolation.

## Packaging completeness

`python -m build` produced both wheel and sdist. Twine accepted both. The wheel was installed from outside the source checkout and `repoverity.__file__` resolved under `site-packages`. The sdist alone rebuilt a wheel that was installed into a second clean environment and successfully ran version/help and a known-good fixture audit.

## Release recommendation

The source candidate passed the full release gate. The repository is **READY TO TAG only after the documentation-recording commit also completes the same hosted validation workflows successfully**. No tag, GitHub Release, or PyPI publication is authorized by this audit.
