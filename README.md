# RepoVerity

**Deterministic, evidence-based code trust audits for Python repositories.**

RepoVerity helps answer a practical review question: **“What concrete evidence says this repository is ready to review, merge, run, or release—and where are the trust gaps?”**

It is a local-first static analyzer. It does not execute the target repository, does not upload source code, does not require an account, and does not try to guess whether code was written by a person or an AI system.

RepoVerity complements linters, type checkers, security scanners, and tests. Its focus is different: it looks for repository-level inconsistencies and weak evidence across dependency declarations, abstractions, test boundaries, dead/speculative surface area, and release metadata.

## Why RepoVerity exists

A repository can be beautifully formatted and still be difficult to trust. Examples include:

- source code imports a package that is not declared in project metadata;
- package metadata claims a Python compatibility floor that the source syntax contradicts;
- a class adds indirection but almost no contract or behavior;
- an explicit error path exists without direct test evidence;
- a placeholder or unused private helper remains reachable in production code;
- CI does not exercise the oldest/newest Python versions claimed by the package;
- a mature repository gains new findings but has no baseline-aware way to separate regressions from historical debt.

RepoVerity turns those conditions into deterministic findings with enough context for a reviewer to decide whether a finding is actionable, acceptable, or should be explicitly suppressed.

## Try it in 60 seconds

### Install

```bash
python -m pip install repoverity
```

For one-off use without a permanent install:

```bash
pipx run repoverity audit .
```

The source repository is also directly installable:

```bash
python -m pip install git+https://github.com/aprashnasuraj-dev/AI-Code-Quality-Trust-Layers.git
```

RepoVerity supports Python **3.11 through 3.14**.

### Audit your repository

From the project root:

```bash
repoverity audit .
```

The default terminal report groups findings by trust area, highlights higher-value findings, and includes locations plus remediation guidance.

Example output from the intentionally-bad fixture:

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

The complete machine-generated example is committed at [`examples/generated_reports/demo-terminal.txt`](examples/generated_reports/demo-terminal.txt).

### Understand a finding before changing code

```bash
repoverity explain ABS201
```

Every rule explanation includes what it detects, why it can matter, severity, confidence, evidence level, an intentionally-bad example, a legitimate counterexample, limitations, a recommended action, and the exact suppression form.

That distinction matters: a static finding is **evidence for review, not proof of a defect**.

## What RepoVerity checks

v0.1 ships **18 deterministic rules** across seven trust areas.

| Area | What RepoVerity looks for | Review question |
| --- | --- | --- |
| Dependency / runtime reality | undeclared third-party imports, apparently unused declared dependencies, syntax newer than the claimed Python floor | Will a clean environment actually contain what this code imports? |
| Architecture | quantified pass-through wrappers, weak single-method abstractions, nested exception shells | Does this abstraction add a meaningful contract or only indirection? |
| Naming | narrow generic identifier/public-API candidates with contextual evidence | Does this public surface communicate enough intent? |
| Comments | syntax-restating narration and narration clusters | Does the comment explain rationale or merely translate syntax into prose? |
| Dead/speculative surface | unused parameters/private helpers and reachable placeholders | Is this code part of a real contract or abandoned/speculative surface area? |
| Test boundaries | direct error-path, malformed-input, and CLI integration-test signals | Do important failure boundaries have direct executable evidence? |
| Release hygiene | package metadata consistency and CI coverage of claimed Python range edges | Do release claims match what CI actually verifies? |

See [`docs/RULES.md`](docs/RULES.md) for the complete catalog, examples, counterexamples, and rule-specific limitations.

## How to read a finding

RepoVerity deliberately separates dimensions that are often collapsed into one opaque score.

- **Severity** describes expected review priority.
- **Confidence** describes how directly the repository evidence supports the inference.
- **Evidence level** distinguishes `verified`, `inferred`, and `heuristic` findings.
- **Mechanism** explains why the detected condition can create risk.
- **Counterexample** shows a legitimate design that can look similar.
- **Recommendation** gives a concrete next step.
- **Fingerprint** keeps baselines stable across unrelated line movement.
- **Suppression path** makes intentional exceptions explicit and reviewable.

RepoVerity intentionally does **not** emit a global “trust score.” A single number would hide why a repository passed or failed.

## Practical workflows

### Local pre-review gate

```bash
repoverity audit . --fail-on high
```

Exit code `1` means the configured finding gate failed; it does not mean RepoVerity crashed.

### Focus on selected rules

```bash
repoverity audit . --rules DEP101,TST602
```

### Generate a Markdown review artifact

```bash
repoverity audit . --format markdown --output trust-report.md
```

### Generate machine-readable JSON

```bash
repoverity audit . --format json --output trust.json
```

### Generate SARIF for GitHub code scanning

```bash
repoverity audit . --format sarif --output trust.sarif
```

### Adopt incrementally with a baseline

Create a baseline once:

```bash
repoverity baseline create . --output .trust-baseline.json
```

Then fail only on **new** high-severity findings:

```bash
repoverity audit . --baseline .trust-baseline.json --fail-on high
```

RepoVerity fingerprints findings from rule/path/semantic anchors rather than raw line numbers, reducing false regressions from unrelated line movement.

### Audit changed work only

```bash
repoverity audit . --changed-only origin/main --baseline .trust-baseline.json --fail-on high
```

Changed-only analysis covers committed branch changes plus staged, unstaged, and untracked files. Outside Git, RepoVerity warns and falls back to a full audit rather than silently returning nothing.

### Preview remediation without modifying code

```bash
repoverity fix-preview .
```

`fix-preview` is intentionally conservative. It explains proposed remediation but does not perform architecture rewrites or delete code automatically.

### Inspect built-in rules

```bash
repoverity rules list
repoverity rules show DEP101
```

### Check the installed version

```bash
repoverity --version
repoverity version
```

`--version` prints the package version. The `version` command additionally reports the running Python and platform, which is useful in issue reports.

## GitHub Action

RepoVerity is also a composite GitHub Action, so a repository can use it without installing the PyPI package first:

```yaml
- uses: aprashnasuraj-dev/AI-Code-Quality-Trust-Layers@v0.1.0
  with:
    path: .
    fail-on: high
    baseline: .trust-baseline.json
```

The Action runs the checked-out RepoVerity source via `GITHUB_ACTION_PATH`. It does not require an API key, external server, source upload, or package-registry access.

A complete job can look like this:

```yaml
name: RepoVerity

on:
  pull_request:
  push:
    branches: [main]

jobs:
  trust-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aprashnasuraj-dev/AI-Code-Quality-Trust-Layers@v0.1.0
        with:
          path: .
          fail-on: high
```

For reproducible production CI, pin either a released tag or an immutable commit. See [`docs/GITHUB_ACTION.md`](docs/GITHUB_ACTION.md).

## Output formats

RepoVerity provides four first-class outputs:

| Format | Best for |
| --- | --- |
| `terminal` | local review and CI logs |
| `json` | automation, data pipelines, custom dashboards |
| `markdown` | pull requests, review notes, release evidence |
| `sarif` | GitHub code scanning and SARIF-compatible tooling |

JSON uses schema version `1.0`. SARIF output follows SARIF 2.1.0 fields used by GitHub code scanning. Shareable outputs use repository-relative paths.

## Suppressions and configuration

A justified inline exception is explicit:

```python
# repoverity: ignore[ABS201] - adapter boundary required by framework contract
```

Minimal project configuration lives in `pyproject.toml`:

```toml
[tool.repoverity]
exclude = ["generated/**"]
fail-on = "high"

[tool.repoverity.rules]
ABS201 = "warn"
COM402 = "off"
```

Precedence is **CLI > project configuration > defaults**. Zero configuration remains the default path.

## Security and privacy model

RepoVerity treats the audited repository as untrusted input.

- no target-module imports;
- no target-code execution;
- no `shell=True` processing of target data;
- no source upload or telemetry;
- no network requirement during an audit;
- no symlink traversal outside the audited tree;
- bounded file/repository processing;
- parse/decode problems isolated as analysis issues rather than arbitrary execution.

See [`SECURITY.md`](SECURITY.md) and [`docs/SECURITY_MODEL.md`](docs/SECURITY_MODEL.md) for the threat model and boundaries.

## What RepoVerity does not prove

RepoVerity is a static evidence tool, not a correctness oracle.

It does not:

- estimate an “AI-written probability” or try to disguise authorship;
- replace Ruff/Pylint, mypy/Pyright, Bandit, Semgrep, SAST, or runtime tests;
- prove that the absence of findings means the application is correct;
- execute plugin systems, reflection-heavy code, framework startup paths, or runtime configuration;
- auto-delete classes, hooks, interfaces, or error handling;
- claim measured code coverage from static test signals.

Reflection, framework contracts, generated code, plugin loading, and indirect test paths can produce legitimate exceptions. Low-confidence heuristics are deliberately low severity and should not fail CI by default.

## Performance

The release workflow benchmarks synthetic repositories at approximately 1k, 10k, and 50k Python LOC and records the exact Git SHA, Python version, platform, timing, and maximum RSS in the release-validation artifact.

Current release-candidate measurements are documented in [`docs/RELEASE_AUDIT.md`](docs/RELEASE_AUDIT.md) and can be reproduced with:

```bash
PYTHONPATH=src python scripts/benchmark.py --loc 1000 10000 50000
```

## Development

```bash
python -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
mypy src/repoverity
python -m build
python -m twine check dist/*
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the rule-fixture contract and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for implementation details.

## Release quality

RepoVerity's own repository is used as a release target. The hosted release matrix includes Ruff, Ruff formatting, strict mypy, pytest, Python 3.11 and 3.14 edge jobs, Windows, build/Twine validation, clean wheel installation, sdist reconstruction, a zero-finding self-audit, SARIF upload, CodeQL, a composite-Action smoke test, and recorded artifact hashes/benchmarks.

The release audit is public at [`docs/RELEASE_AUDIT.md`](docs/RELEASE_AUDIT.md).

## Project

- License: MIT
- Versioning: semantic versioning; v0.x rule semantics may evolve
- Issues: [GitHub Issues](https://github.com/aprashnasuraj-dev/AI-Code-Quality-Trust-Layers/issues)
- Security policy: [`SECURITY.md`](SECURITY.md)
- Roadmap: [`ROADMAP.md`](ROADMAP.md)
- Release checklist: [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md)
- Detailed getting started guide: [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md)
