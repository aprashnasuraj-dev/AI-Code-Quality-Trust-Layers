# Architecture

RepoVerity separates repository I/O, static analysis, rule metadata, baselines, Git diffing, and reporting.

- `discovery.py` reads bounded Python source without following symlinks.
- `project.py` parses `pyproject.toml` with `tomllib`; it never imports target packages.
- `engine.py` builds a deterministic analysis context and runs registered analyzers.
- `rules/` contains independently testable category analyzers; `registry.py` is the canonical metadata source.
- `fingerprints.py` creates stable semantic fingerprints independent of line numbers.
- `baseline.py` classifies current findings as new/existing and reports resolved fingerprints.
- `reporters/` contains presentation only; no analyzer logic belongs there.
- `cli.py` is the process boundary and owns stable exit-code translation.

The analyzer deliberately does not load user plugins in v0.1. Adding a rule means adding metadata, analyzer logic, positive/good/edge fixture coverage, and documentation generated from the registry.
