# RepoVerity v0.1.0 Release Audit

This audit records verified release evidence. A status is **PASS** only when the corresponding check actually ran successfully. The release process deliberately separates evidence about the software from the later act of publishing it.

## Evidence-producing source candidate

- Source candidate SHA: `68e21d14ed78fdc9a5b480d86a1ff9823e317f2e`
- Validation date: 2026-09-10
- Hosted validation OS: Ubuntu 24.04 / Windows GitHub-hosted runner
- Release-validation Python: 3.13.15
- Main CI run: `34428177273`
- Release validation run: `34428177319`
- Composite Action run: `34428177296`
- RepoVerity SARIF run: `34428177257`
- CodeQL run: `34428177278`

This file is itself committed after the evidence above was collected. The documentation-only recording commit must pass the same permanent workflows before it becomes the tag target. That prevents the release audit from claiming evidence for a SHA that was never itself validated.

## Verification matrix

| Area | Result | Evidence |
| --- | --- | --- |
| pytest | PASS | 108 tests passed in hosted quality CI |
| compileall | PASS | `python -m compileall -q src tests` in Release validation |
| self-audit | PASS | 0 findings / 0 analysis issues; every severity count is zero |
| Ruff | PASS | Ruff 0.16.6: all checks passed |
| Ruff format | PASS | hosted format check passed |
| mypy | PASS | strict mode; no issues found in 30 source files |
| Python 3.11 | PASS | dedicated hosted pytest job |
| Python 3.14 | PASS | dedicated hosted pytest job |
| Windows | PASS | dedicated hosted Windows pytest job |
| build | PASS | wheel and sdist built successfully |
| Twine | PASS | wheel and sdist metadata accepted |
| global `--version` | PASS | source regression test plus clean wheel and reconstructed-sdist smoke checks |
| wheel clean install | PASS | clean venv, `--no-index --no-deps`, `repoverity --version`, help, site-packages import, known-good audit |
| sdist reconstruction | PASS | sdist extracted, wheel rebuilt, clean venv installed, `repoverity --version`, help, known-good audit |
| composite Action | PASS | local `uses: ./` workflow succeeded without a RepoVerity API key |
| SARIF generation | PASS | final-candidate SARIF generation step succeeded |
| SARIF upload | PASS | GitHub code-scanning upload step succeeded |
| CodeQL | PASS | CodeQL init/analyze workflow succeeded |
| 1k benchmark | RECORDED | 1,000 analyzed LOC; 0.2328 s; 26.0 MiB max RSS |
| 10k benchmark | RECORDED | 10,000 analyzed LOC; 0.5360 s; 37.4 MiB max RSS |
| 50k benchmark | RECORDED | 50,000 analyzed LOC; 2.0462 s; 89.7 MiB max RSS |
| release/recovery artifact cleanup | PASS | temporary recovery files are absent from `main`; build/caches/venv are not tracked |

## Benchmark environment

The fresh benchmark run used Python 3.13.15 on `Linux-6.17.0-1022-azure-x86_64-with-glibc2.39`.

`ru_maxrss` is converted from bytes on macOS and KiB on the Linux validation host. Each generated benchmark project is temporary, requested LOC equals analyzed LOC exactly, subprocess failures propagate, and the benchmark records the repository SHA returned by Git.

The measured 50k-LOC workload completed in about 2.05 seconds with under 90 MiB maximum RSS on the hosted runner. These numbers are measurements for this runner, not universal performance guarantees.

## Candidate distribution artifacts

The Release validation workflow for `68e21d14ed78fdc9a5b480d86a1ff9823e317f2e` produced:

- `repoverity-0.1.0-py3-none-any.whl`
  - SHA-256: `cf4d0853be1682540a5cf25c7218cbe5afb0d0992b198abd0f694ecaaaac75d4`
- `repoverity-0.1.0.tar.gz`
  - SHA-256: `6529e202e8318c0c93075f532b2fa793349ba600d8cd991f49909763d8cb7080`

The actual tag/release build will generate its own SHA-256 file. Those release assets must be treated as authoritative for the published artifacts rather than assuming archive bytes are identical across separate builds.

## CLI and package contract

The release exposes both:

```text
repoverity --version
repoverity version
```

The global flag prints the package version. The `version` subcommand additionally reports the Python and platform environment. The global flag is tested from source, from a clean installed wheel, and from a wheel reconstructed solely from the sdist.

The package declares Python `>=3.11,<3.15`, matching the 3.11 and 3.14 hosted compatibility-edge jobs. Runtime dependencies are empty.

## Security and adversarial behavior

Regression coverage includes target-code non-execution, symlink boundaries, malformed/binary/oversized input handling, dynamic imports, baseline fingerprint stability, changed-only rename/deletion/no-commit/detached-HEAD behavior, deterministic JSON/Markdown/SARIF output, SARIF rules/locations/fingerprints, hidden/default directory and `.venv` exclusion, workflow YAML parsing, release-workflow contract, and Action argument safety.

Production source uses no `shell=True`, `os.system`, `eval`, or `exec` path. Git subprocesses use argument arrays rather than shell interpolation.

RepoVerity's security claim is intentionally bounded: static analysis and adversarial tests reduce specific classes of risk but do not prove the analyzer—or the code it audits—is defect-free.

## Public documentation and discoverability

The publication candidate includes:

- a detailed README with install, local audit, baselines, changed-only analysis, output formats, GitHub Action integration, security model, limitations, and concrete examples;
- `docs/GETTING_STARTED.md` for staged adoption;
- `docs/RULES.md` for all 18 rules, including counterexamples and limitations;
- `docs/RELEASE_NOTES_v0.1.0.md` for the curated GitHub release notes;
- `docs/MARKETPLACE.md` with the GitHub Marketplace listing copy, categories, quick-start workflow, and limitations;
- package metadata and Action metadata aligned to the same product positioning.

The intended Marketplace listing name is **RepoVerity Code Trust Audit**, with **Code quality** as the primary category and **Continuous integration** as the secondary category.

## Marketplace publication boundary

The repository and release metadata are prepared for GitHub Marketplace. GitHub's Action Marketplace publication flow requires the repository owner to select **Publish this Action to the GitHub Marketplace** in the release UI, accept the Marketplace Developer Agreement if prompted, select categories, and complete the account's 2FA confirmation.

That account/UI confirmation is separate from code validation and cannot be represented as complete until GitHub records it. The GitHub release and PyPI package can be published programmatically; Marketplace visibility requires that owner-controlled Marketplace step.

## Release recommendation

The evidence-producing source candidate passed the full release gate. After this documentation-recording commit passes the same permanent workflows, the repository is **READY TO PUBLISH v0.1.0**.

Publication should then:

1. point tag `v0.1.0` at the exact final green `main` SHA;
2. build and check fresh wheel/sdist artifacts;
3. publish `repoverity==0.1.0` to PyPI through Trusted Publishing;
4. create the GitHub Release with the curated release notes and distribution assets;
5. verify the tag, release assets/hashes, and public PyPI project/install metadata;
6. complete the Marketplace checkbox/category/2FA step in GitHub's release UI and verify the Marketplace listing.
