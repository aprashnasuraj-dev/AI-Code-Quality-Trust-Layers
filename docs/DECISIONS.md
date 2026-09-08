# Architecture and Product Decisions

## D001 — Project name: RepoVerity

**Decision**
Use **RepoVerity** as the project/package name and `repoverity` as the CLI command.

**Context**
The name must be pronounceable, neutral to future language packs, and must not claim AI authorship detection or perfect trust.

**Options considered**
- RepoReceipt — rejected: an active GitHub project already uses `repo-receipt` for GitHub repository receipts.
- ReviewRay — rejected: active AI-powered code review project/name collision.
- CodeWitness — rejected: archived Consensys project plus newer code-review/witness uses.
- RepoLens — rejected: multiple established/current projects already use the name.
- CodeVerity — rejected: established software consultancy/brand, confusingly close.
- CodeTruss — rejected: current adjacent commercial deterministic AI-code verification product.
- RepoVerity — selected: PyPI project URL returned 404 during the 2026-09-08 collision check and exact-name web/GitHub search surfaced no established project.

**Chosen option**
RepoVerity.

**Why**
It communicates repository-level evidence/truthfulness without saying the tool can prove authorship or guarantee correctness. It remains usable if future rule packs support other languages.

**Tradeoff / downside**
“Verity” is less immediately descriptive than “lint” or “audit,” so the README subtitle must explain the category in one sentence.

**What would cause reversal**
Discovery of a materially conflicting package/trademark before publication.

---

## D002 — Python 3.11–3.14, stdlib-first runtime

**Decision**
Implement v0.1 in Python with `requires-python = ">=3.11,<3.15"` and no mandatory third-party runtime dependency.

**Context**
Python 3.14.7 is the latest stable maintenance release observed on python.org on 2026-09-08; Python 3.15 is still release-candidate stage. Python 3.11 provides `tomllib`, modern AST support, dataclasses, `importlib.metadata`, and broad contributor availability.

**Options considered**
- Python + CLI/rendering frameworks — nicer ergonomics but larger supply-chain/runtime surface.
- Rust — excellent distribution/performance but slower rule iteration and less direct Python AST access.
- Python stdlib-first — selected.

**Chosen option**
Python 3.11–3.14, standard library for runtime; pytest/Ruff/mypy/build tooling only for development.

**Why**
Fast implementation, deterministic AST/token analysis, low install friction, no runtime dependency security surface, and easy `pipx run` activation.

**Tradeoff / downside**
Terminal UX is less polished than Rich/Typer, and standalone binaries are not part of v0.1.

**What would cause reversal**
Measured installation latency or terminal usability materially misses the product targets.

---

## D003 — Small canonical rule registry, no plugin framework in v0.1

**Decision**
Rules implement a small internal analyzer protocol and declare all user-facing metadata in one registry.

**Context**
The product needs independently testable rules and future language growth, but a third-party plugin framework is speculative for v0.1.

**Options considered**
- Dynamic entry-point plugin framework.
- YAML rule DSL.
- Small static registry — selected.

**Chosen option**
Static registry + explicit analyzer functions/classes.

**Why**
Fewer moving parts, deterministic startup, simple packaging, and adding a rule touches only its analyzer, canonical metadata, fixtures, tests, and docs.

**Tradeoff / downside**
External rules require contributing to the repository until a plugin contract is justified.

**What would cause reversal**
Multiple credible external rule-pack contributors needing independent release cycles.

---

## D004 — Evidence and status over global score

**Decision**
Do not ship a single numeric “trust score” in v0.1. Summaries are category/severity counts plus new/existing/resolved baseline status.

**Context**
A numeric trust score would imply precision the analyzer cannot defend.

**Chosen option**
Evidence-first findings, category summary, and regression gate.

**Tradeoff / downside**
Less screenshot-friendly than a 0–100 score, but more technically credible.

**What would cause reversal**
A validated, explainable calibration study with known error bars and clear decision value.

---

## D005 — SARIF generated directly from a verified subset

**Decision**
Generate SARIF 2.1.0 with the standard library rather than depend on a SARIF helper library.

**Context**
GitHub code scanning accepts a supported subset of SARIF 2.1.0. The required structure is small enough to generate deterministically.

**Chosen option**
Direct JSON generation with schema/version/tool/rule/result/location fields and fixture validation.

**Tradeoff / downside**
RepoVerity owns correctness of its serializer and must keep tests aligned with GitHub’s documented subset.

**What would cause reversal**
A mature, lightweight helper demonstrably reduces maintenance without adding substantial dependencies.

---

## D006 — Composite GitHub Action, pipx/pip package path first

**Decision**
Ship a composite repository Action that sets up Python and invokes the same CLI directly from the Action checkout; no package install is required.

**Context**
A Docker action adds image build/release overhead; standalone binaries are not needed to meet the initial activation target.

**Chosen option**
Composite Action using `PYTHONPATH=<action>/src` + PyPI-ready package.

**Tradeoff / downside**
Action startup includes Python setup, but avoids a package-install/network step and therefore runs the exact checked-out Action source.

**What would cause reversal**
Measured Action latency or platform compatibility becomes a material adoption problem.

---

## D007 — Changed-only is contextual analysis followed by path filtering

**Decision**
Analyze repository context first, then filter findings to Git-changed paths. The changed set unions committed three-dot branch delta, staged/unstaged changes, and untracked files.

**Context**
Cross-file rules become incorrect if discovery itself is restricted to changed files; pre-commit users also expect staged/untracked files to count.

**Tradeoff / downside**
Changed-only reduces report scope, not parse cost. This is deliberate correctness-over-micro-optimization for v0.1.

**What would cause reversal**
A dependency graph/cache can prove equivalent context with materially lower cost on very large repositories.

---

## D008 — `fix-preview` is recommendation-only in v0.1

**Decision**
Do not emit speculative source patches for structural findings.

**Context**
None of the differentiated v0.1 architecture/test-boundary rules has a generally safe mechanical rewrite. A fake patch would violate the no-blind-rewrite principle.

**Tradeoff / downside**
The command is less flashy, but it is truthful: it previews remediation and explicitly marks auto-apply unavailable.

**What would cause reversal**
A rule is added with a semantics-preserving, mechanically verifiable transformation and dedicated round-trip tests.
