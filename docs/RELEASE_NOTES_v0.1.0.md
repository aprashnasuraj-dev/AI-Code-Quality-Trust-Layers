# RepoVerity v0.1.0 — Evidence you can review

RepoVerity v0.1.0 is the first public release of a deterministic, local-first code trust auditor for Python repositories.

It is built for maintainers and reviewers who already have linters, type checkers, tests, and security scanners—but still need evidence about repository-level consistency: whether dependencies match imports, abstractions add real contracts, error boundaries have direct tests, dead/speculative surfaces remain reachable, and release claims match CI.

## Highlights

- **18 evidence-based rules** across dependency/runtime reality, architecture, naming, comments, dead surface, test boundaries, and release hygiene.
- **No AI-authorship guessing.** RepoVerity evaluates repository evidence, regardless of who or what wrote the code.
- **Local-first and zero runtime dependencies.** Audits do not upload source or require a hosted service.
- **No target-code execution.** Target modules are not imported or executed during analysis.
- **Four output formats:** terminal, versioned JSON, Markdown Code Trust Receipt, and SARIF 2.1.0.
- **Baseline-aware adoption:** classify findings as new, existing, or resolved and fail CI only on regressions.
- **Git changed-only mode:** includes committed branch changes plus staged, unstaged, and untracked files.
- **Explainable rules:** every rule documents its mechanism, confidence, evidence level, counterexample, limitation, remediation, and suppression form.
- **GitHub Action:** run RepoVerity directly from the checked-out Action source without an API key or PyPI dependency.
- **GitHub code scanning:** SARIF output is exercised by the project's own hosted workflow.

## Quick start

```bash
python -m pip install repoverity
repoverity audit .
```

Inspect a rule before changing code:

```bash
repoverity explain ABS201
```

Adopt it in an existing repository without failing on historical debt:

```bash
repoverity baseline create . --output .trust-baseline.json
repoverity audit . --baseline .trust-baseline.json --fail-on high
```

Use the GitHub Action:

```yaml
- uses: aprashnasuraj-dev/AI-Code-Quality-Trust-Layers@v0.1.0
  with:
    path: .
    fail-on: high
```

## Release validation

The release repository validates itself before publication. The release matrix includes:

- Ruff lint and formatting checks;
- strict mypy;
- pytest;
- Python 3.11 and 3.14 compatibility-edge jobs;
- Windows execution;
- compileall;
- zero-finding RepoVerity self-audit;
- wheel and sdist builds;
- Twine metadata checks;
- clean wheel installation;
- rebuilding a wheel from the sdist and installing it again;
- `repoverity --version`, help, and known-good audit smoke tests;
- composite GitHub Action smoke testing;
- SARIF generation/upload;
- CodeQL;
- recorded 1k/10k/50k LOC benchmarks and SHA-256 artifact hashes.

The exact hosted evidence for the release commit is recorded in `docs/RELEASE_AUDIT.md` and in the release-validation workflow artifact.

## Security and privacy

RepoVerity treats the target repository as untrusted input. The analyzer is designed around bounded static processing, repository-relative outputs, no source upload, no telemetry, no target-code imports, no target-code execution, and no symlink traversal outside the target tree.

See `SECURITY.md` and `docs/SECURITY_MODEL.md` for the threat model and known boundaries.

## What v0.1.0 does not claim

RepoVerity does not prove program correctness. It does not replace Ruff/Pylint, type checkers, Bandit, Semgrep, SAST, runtime tests, or measured coverage. Reflection-heavy frameworks, plugin registration, external CI, generated code, and indirect test paths can require human context.

A clean RepoVerity report means the configured rules found no matching trust gaps—not that the software is bug-free.

## Feedback wanted

The most valuable early feedback is:

- minimal reproducible false positives;
- repositories where baseline fingerprints are unexpectedly unstable;
- framework/plugin contracts that static evidence cannot currently recognize;
- high-value repository trust checks that ordinary linters and security scanners do not already cover.

Use the repository's issue templates for bugs, false positives, and rule proposals.

Thanks for testing the first public release.
