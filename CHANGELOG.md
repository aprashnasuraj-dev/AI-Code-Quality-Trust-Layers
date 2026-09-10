# Changelog

All notable changes follow semantic versioning principles.

## 0.1.0 — 2026-09-10

### Added
- Deterministic local Python repository audit with 18 evidence-based rules across seven trust categories.
- Terminal, versioned JSON, Markdown Code Trust Receipt, and SARIF 2.1.0 output.
- Stable finding fingerprints and baseline classification for new, existing, and resolved findings.
- Git changed-only mode covering committed, staged, unstaged, renamed, deleted, and untracked paths.
- Inline/project suppressions, offline rule explanations, rule discovery, and non-mutating remediation preview.
- Composite GitHub Action requiring no RepoVerity API key or hosted service.
- GitHub code-scanning SARIF workflow, CodeQL, multi-version CI, Windows CI, reproducible release validation, and benchmark evidence.
- Detailed getting-started, security, architecture, baseline, output-format, and release-audit documentation.

### Release quality
- Python support verified at the declared 3.11 and 3.14 edges, with the main suite also exercised on the release runner.
- Strict mypy, Ruff lint, Ruff formatting, pytest, compileall, build, Twine, clean wheel install, and sdist reconstruction gates.
- Self-audit required to report zero findings and zero analysis issues for the repository's configured scope.
- Distribution SHA-256 hashes and 1k/10k/50k LOC benchmark evidence captured by the release-validation workflow.
- CLI smoke coverage for `repoverity --version`, `repoverity version`, `--help`, and a known-good repository audit.

### Security and behavior
- Target repositories are parsed statically; RepoVerity does not import or execute analyzed project modules.
- No source upload, telemetry, or network requirement during an audit.
- Symlink-boundary, hostile-path, malformed-source, encoding, large-file, deterministic-report, and Git edge-case regression coverage.

### Known scope
- v0.1 focuses on Python repositories.
- Static evidence cannot prove runtime correctness, framework contracts, reflection behavior, plugin registration, or measured test coverage.
- Heuristic findings intentionally include counterexamples and should be reviewed rather than treated as automatic defects.
