# RepoVerity

**Evidence-based code trust audit for Python repositories.** RepoVerity answers: *“Can I trust this codebase enough to review, run, merge, or release it — and what concrete evidence supports that answer?”*

It is deterministic, local-first, zero-configuration on the primary path, and does **not** attempt to detect whether code was written by AI.

```text
RepoVerity 0.1.0 — Code Trust Audit
Repository: intentionally_bad
Files analyzed: 3 | Python LOC: 29 | Duration: <machine-dependent>

TRUST SUMMARY
Runtime reality        2 finding(s)
Architecture           1 finding(s)
Dead surface           2 finding(s)
Test boundaries        3 finding(s)
Release hygiene        2 finding(s)

HIGH-VALUE FINDINGS
DEP101  HIGH    src/inventory/audit.py:1   Import 'requests' has no matching declared dependency.
ABS201  MEDIUM  src/inventory/audit.py:4   Class 'InventoryClient' delegates 3/3 public methods...
TST602  MEDIUM  src/inventory/audit.py:28  Boundary 'parse_manifest' raises explicit errors without direct test evidence.
```

The complete, machine-generated demo output is committed at [`examples/generated_reports/demo-terminal.txt`](examples/generated_reports/demo-terminal.txt).

## Try it

Before the first PyPI release, install directly from the public source repository:

```bash
python -m pip install git+https://github.com/aprashnasuraj-dev/AI-Code-Quality-Trust-Layers.git
repoverity audit .
```

From a clone, no runtime dependency installation is needed:

```bash
PYTHONPATH=src python -m repoverity audit examples/intentionally_bad
```

After the first PyPI release, the intended one-command path will be:

```bash
pipx run repoverity audit .
```

Useful follow-ups:

```bash
repoverity explain ABS201
repoverity audit . --format markdown --output trust-report.md
repoverity audit . --format sarif --output trust.sarif
repoverity baseline create . --output .trust-baseline.json
repoverity audit . --baseline .trust-baseline.json --fail-on high
```

## What it catches

| Area | Evidence RepoVerity looks for |
| --- | --- |
| Dependency / runtime reality | undeclared third-party imports, apparently unused declared dependencies, syntax newer than the claimed Python floor |
| Architecture | quantified pass-through wrappers, weak single-method classes, nested exception shells |
| Naming | narrow generic identifier/public API candidates with contextual evidence |
| Comments | syntax-restating narration and narration clusters |
| Dead/speculative surface | unused parameters/private helpers and reachable placeholders |
| Test boundaries | direct error-path, malformed-input, and CLI integration-test signals |
| Release hygiene | package metadata consistency and CI coverage of claimed Python range edges |

v0.1 contains **18 rules**. Each finding carries severity, confidence, evidence level (`verified`, `inferred`, or `heuristic`), mechanism, counterexample, recommendation, stable fingerprint, and suppression path. See [docs/RULES.md](docs/RULES.md).

## Why this exists

AI-assisted and human-written code can both look plausible during a shallow review while retaining structural risks: a dependency that only exists on the author machine, a wrapper that adds indirection without a contract, a parser whose failure path has no direct test evidence, or release metadata that claims compatibility CI never exercises.

RepoVerity sits **above ordinary linters and below heavyweight code-quality platforms**. It intentionally complements Ruff, mypy/Pyright, Bandit, Semgrep, and similar tools rather than cloning their strongest capabilities. See [competitor notes](docs/COMPETITOR_NOTES.md).

## What it does **not** do

- does not estimate “AI-written probability” or disguise AI authorship;
- does not upload source, require an account, emit telemetry, or make network calls during the audit;
- does not import or execute analyzed project modules;
- does not replace Ruff/Pylint, type checkers, Bandit, Semgrep, or runtime tests;
- does not auto-delete classes, hooks, interfaces, or error handling;
- does not claim absence of findings proves correctness.

## Baseline: fail only on regressions

A mature repository can adopt RepoVerity without cleaning every historical issue first:

```bash
repoverity baseline create . --output .trust-baseline.json
repoverity audit . --baseline .trust-baseline.json --fail-on high
```

Findings are fingerprinted from rule/path/semantic anchors rather than raw line numbers. A later audit distinguishes **new**, **existing**, and **resolved** findings; the quality gate considers only **new** findings.

For PR-local analysis:

```bash
repoverity audit . --changed-only origin/main --baseline .trust-baseline.json --fail-on high
```

Changed-only includes committed branch changes plus staged, unstaged, and untracked files. Outside Git, RepoVerity warns and performs a full audit rather than silently returning nothing.

## CI / GitHub Action

Development usage before the first release tag exists:

```yaml
- uses: aprashnasuraj-dev/AI-Code-Quality-Trust-Layers@main
  with:
    path: .
    fail-on: high
    baseline: .trust-baseline.json
```

The composite Action runs the checked-out RepoVerity source directly and needs no secrets or package install. Once v0.1.0 is released, production workflows should pin a released tag or immutable commit rather than `main`. For SARIF/code-scanning upload, see [docs/GITHUB_ACTION.md](docs/GITHUB_ACTION.md).

## Output formats

`terminal`, `json`, `markdown`, and `sarif` are first-class outputs. Markdown includes a compact **Code Trust Receipt** suitable for a PR or release note. JSON schema version is `1.0`; SARIF uses 2.1.0 fields supported by GitHub code scanning. Paths are repository-relative in shareable outputs.

## Suppressions and configuration

Inline suppression is explicit and reviewable:

```python
# repoverity: ignore[ABS201] - adapter boundary required by framework contract
```

Minimal `pyproject.toml` configuration is supported:

```toml
[tool.repoverity]
exclude = ["generated/**"]
fail-on = "high"

[tool.repoverity.rules]
ABS201 = "warn"
COM402 = "off"
```

Precedence is **CLI > project configuration > defaults**. Zero configuration remains the default path.

## Security / privacy

RepoVerity treats the target tree as untrusted input: no user-code imports, no user-code execution, no `shell=True`, no source upload, no symlink traversal, bounded file/repository sizes, and parse/decode failures isolated as analysis issues. See [SECURITY.md](SECURITY.md) and [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md).

## Development

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
pytest
ruff check .
mypy src/repoverity
python -m build
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the rule fixture contract and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for internals.

## Limitations

RepoVerity uses static evidence, not whole-program proof or measured coverage. Plugin loading, reflection, framework contracts, external CI, and indirect test paths can produce legitimate exceptions. Low-confidence heuristics are deliberately low severity and should not fail CI by default. Detailed limitations and deferred rules are in [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md).

## Benchmark snapshot

Performance targets and **measured local results** are recorded in [docs/BENCHMARKS.md](docs/BENCHMARKS.md). Re-run with:

```bash
PYTHONPATH=src python scripts/benchmark.py
```

## Project

- Version policy: semantic versioning; v0.x rule semantics may still evolve.
- License: MIT.
- Release checklist: [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md).
- Roadmap: [ROADMAP.md](ROADMAP.md).
