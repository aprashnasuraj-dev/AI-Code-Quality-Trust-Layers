# Release Checklist — v0.1.0

## Local source candidate
- [ ] Full pytest passes from the final source tree.
- [ ] `compileall` passes.
- [ ] Final self-audit is triaged.
- [ ] Every YAML file parses.
- [ ] Public-source secret/private-path/TODO scan reviewed.
- [ ] Benchmark rerun and recorded.
- [ ] Clean Git-index candidate passes `git diff --cached --check`.
- [ ] Wheel and sdist rebuild from the final candidate.
- [ ] Fresh no-index wheel install and installed CLI smoke pass.
- [ ] Sdist reconstruction path passes.
- [ ] Final candidate artifact SHA-256 values recorded.

## Hosted validation before tag
- [ ] CI core tests green on Python 3.11 and 3.14.
- [ ] Ruff check/format green.
- [ ] mypy green.
- [ ] `python -m build` green.
- [ ] `twine check dist/*` green.
- [ ] Composite Action smoke green on GitHub runner.
- [ ] RepoVerity SARIF upload accepted or exact external blocker documented.
- [ ] CodeQL hosted run inspected.

## Publication setup
- [ ] PyPI distribution name/ownership rechecked.
- [ ] PyPI Trusted Publisher configured for the repository/environment `pypi`.
- [ ] Tag `v0.1.0` only after hosted gates are green and owner authorizes release.
