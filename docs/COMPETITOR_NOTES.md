# Competitor Notes

| Tool | What it already does well | What RepoVerity should not duplicate | Gap RepoVerity addresses |
| --- | --- | --- | --- |
| Ruff / Flake8 | fast linting, style and many correctness checks | formatting/style catalog | cross-category trust evidence and baselines |
| Pylint | broad Python diagnostics | generic lint taxonomy | compact reviewer-oriented evidence |
| Radon / Xenon | complexity metrics | complexity scoring | mechanism-specific structural candidates |
| Vulture | unused code discovery | broad dead-code engine | combine dead surface with context/counterexamples |
| mypy / Pyright | type checking | type inference | trust audit beyond typing |
| Bandit | Python security patterns | security linter replacement | release/test/abstraction evidence |
| Semgrep | programmable structural matching | general pattern framework | zero-config Python trust rules |
| Sonar-style platforms | dashboards and broad quality management | hosted platform/account model | local-first one-command review receipt |

RepoVerity is intentionally complementary. A project that uses RepoVerity should generally keep its existing linter, type checker, security scanner and runtime tests.
