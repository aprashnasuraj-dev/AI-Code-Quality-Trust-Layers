# Known Limitations

- Static evidence cannot prove correctness, runtime behavior, authorship, or complete test coverage.
- DEP101/DEP102 cannot perfectly map arbitrary import names to distributions; known mappings and installed metadata are used conservatively.
- Non-literal dynamic imports are deliberately unresolved.
- DEP103 is a CPython grammar compatibility check, not runtime API compatibility proof.
- Environment-resolution/API-symbol rules comparable to DEP104/DEP105 are deferred because importing target modules is prohibited and environment absence is easy to misstate.
- Architecture, naming and comment findings are candidates with legitimate framework/compatibility counterexamples.
- Test-boundary rules search static test-corpus signals; indirect, generated, property-based or external tests can be missed.
- A file rename changes baseline path identity in v0.1.
- Standalone binaries and non-Python language packs are deferred.
- Remote GitHub SARIF ingestion, CodeQL and PyPI Trusted Publishing are only verified after hosted workflows actually run.
