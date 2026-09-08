# Rule Reference

RepoVerity v0.1 ships a small rule set. Severity, confidence and evidence level are separate dimensions.

| Rule | Category | Severity | Confidence | Evidence |
| --- | --- | --- | --- | --- |
| DEP101 | dependency-reality | high | high | verified |
| DEP102 | dependency-reality | low | medium | inferred |
| DEP103 | dependency-reality | high | high | verified |
| ABS201 | architecture | medium | medium | inferred |
| ABS202 | architecture | low | medium | inferred |
| ABS203 | architecture | medium | high | verified |
| NAM301 | naming | low | low | heuristic |
| NAM302 | naming | low | medium | heuristic |
| COM401 | comments | low | low | heuristic |
| COM402 | comments | info | low | heuristic |
| DEAD501 | dead-surface | low | medium | inferred |
| DEAD502 | dead-surface | low | medium | inferred |
| DEAD504 | dead-surface | medium | high | verified |
| TST602 | test-boundaries | medium | medium | inferred |
| TST603 | test-boundaries | medium | medium | inferred |
| TST604 | test-boundaries | medium | high | inferred |
| REL701 | release-hygiene | medium | high | verified |
| REL704 | release-hygiene | medium | high | verified |

## DEP101 — Third-party import is not declared

A production import appears to come from a third-party distribution absent from project dependency metadata.

**Mechanism:** Clean installs can fail at import time when a dependency is only present on the author machine.

**Bad candidate:** `import requests  # but requests is absent from project dependencies`

**Legitimate counterexample:** # pyproject.toml declares requests; source imports requests

**Limitations:** RepoVerity uses stdlib/local-module detection, installed package metadata, and a small verified alias map; unknown aliases can still create false positives.

**Recommendation:** Declare the distribution in project dependencies, or document/configure why the import is provided out-of-band.

Suppress locally with `# repoverity: ignore[DEP101] - <reason>` when the exception is intentional.

## DEP102 — Declared runtime dependency has no static import evidence

A runtime dependency is declared but no analyzed production source imports its known top-level package.

**Mechanism:** Unused dependencies increase install surface, supply-chain exposure, and maintenance burden.

**Bad candidate:** `dependencies = ["requests"]  # source never imports requests`

**Legitimate counterexample:** A plugin distribution loaded through entry points is documented and suppressed with rationale.

**Limitations:** Static import absence is evidence, not proof of non-use; this rule is deliberately low severity.

**Recommendation:** Confirm whether the dependency is dynamically loaded or packaging-only; remove it if it has no runtime role.

Suppress locally with `# repoverity: ignore[DEP102] - <reason>` when the exception is intentional.

## DEP103 — Declared Python minimum conflicts with source syntax

Source parses on the analyzer runtime but fails when parsed using the project's declared minimum Python grammar.

**Mechanism:** Users on a claimed-supported Python version can fail before application logic runs.

**Bad candidate:** `requires-python = ">=3.9" while code uses Python 3.10-only match syntax`

**Legitimate counterexample:** requires-python matches the oldest grammar actually used and CI runs that interpreter.

**Limitations:** This rule detects syntax-level incompatibility only; library/API availability requires separate checks.

**Recommendation:** Raise the declared minimum Python version or rewrite the incompatible syntax and test the minimum version in CI.

Suppress locally with `# repoverity: ignore[DEP103] - <reason>` when the exception is intentional.

## ABS201 — Pass-through wrapper candidate

Most public methods directly delegate to one collaborator and add little observable behavior.

**Mechanism:** Layers that do not validate, translate, cache, retry, enforce policy, or define a contract can add cognitive and debugging hops.

**Bad candidate:** `class Client: methods only return self._inner.same_method(...)`

**Legitimate counterexample:** An adapter translates errors, validates input, records metrics, or implements an external contract.

**Limitations:** RepoVerity only flags wrappers with multiple public methods and a high direct-delegation ratio; it does not auto-remove them.

**Recommendation:** Keep the boundary if it is intentional; otherwise consider exposing the collaborator or collapsing the wrapper.

Suppress locally with `# repoverity: ignore[ABS201] - <reason>` when the exception is intentional.

## ABS202 — Single-method class candidate

A class exposes one public behavior without visible inheritance, registration, or meaningful state contract.

**Mechanism:** A class can impose construction and navigation overhead when a function would express the same behavior more directly.

**Bad candidate:** `class Formatter: def format(self, text): ...  # no state or contract`

**Legitimate counterexample:** class Plugin(BasePlugin): def run(self): ...  # framework contract

**Limitations:** Decorated classes and classes with explicit bases are excluded to reduce framework false positives.

**Recommendation:** Confirm whether framework/runtime identity is required; otherwise consider a function or a more explicit abstraction.

Suppress locally with `# repoverity: ignore[ABS202] - <reason>` when the exception is intentional.

## ABS203 — Nested exception shell immediately re-raises

A nested try/except catches an exception only to issue a bare re-raise while an outer try already encloses it.

**Mechanism:** Redundant exception shells increase nesting without changing recovery, translation, cleanup, or observability.

**Bad candidate:** `try:     try: work()     except Exception:         raise except Exception: recover()`

**Legitimate counterexample:** except ProtocolError as exc: raise DomainError(...) from exc

**Limitations:** The rule intentionally ignores translated exceptions, finally cleanup, retries, logging, and non-trivial handlers.

**Recommendation:** Remove the redundant inner shell or add the boundary behavior that justifies it.

Suppress locally with `# repoverity: ignore[ABS203] - <reason>` when the exception is intentional.

## NAM301 — Generic identifier in domain-heavy function

A long-lived generic local name is used in a function whose surrounding symbols expose more specific domain vocabulary.

**Mechanism:** Generic names increase rereading cost because meaning must be reconstructed from assignments and call sites.

**Bad candidate:** `def reconcile_invoice(...): data = ...; ... many lines using data ...`

**Legitimate counterexample:** for item in items: ...  # tiny conventional scope

**Limitations:** This is a heuristic and is never a high-severity claim; short-lived loop variables are excluded.

**Recommendation:** Rename the long-lived value to the domain concept it represents if that name remains accurate across its lifetime.

Suppress locally with `# repoverity: ignore[NAM301] - <reason>` when the exception is intentional.

## NAM302 — Public API name is too generic

A public top-level symbol uses a generic name that does not communicate its observable operation.

**Mechanism:** Public names become navigation and documentation surfaces; vague names push semantic cost onto every caller.

**Bad candidate:** `def process_data(...): ...`

**Legitimate counterexample:** def parse_invoice_rows(...): ...

**Limitations:** The candidate name set is intentionally narrow to avoid policing naming style generally.

**Recommendation:** Prefer a verb/noun phrase that states the domain operation or returned abstraction.

Suppress locally with `# repoverity: ignore[NAM302] - <reason>` when the exception is intentional.

## COM401 — Comment appears to restate nearby syntax

A narrow comment pattern describes the immediately following operation without visible rationale or constraint language.

**Mechanism:** Narration comments can become stale while adding little information beyond readable code.

**Bad candidate:** `# return users return users`

**Legitimate counterexample:** # Keep ordering stable because the downstream signature includes list position.

**Limitations:** Only a small set of narration patterns is detected; rationale/security/spec/TODO comments are explicitly excluded.

**Recommendation:** Remove the comment or replace it with the reason, invariant, unit, protocol constraint, or tradeoff that is not obvious from code.

Suppress locally with `# repoverity: ignore[COM401] - <reason>` when the exception is intentional.

## COM402 — Narration comment cluster

Several syntax-restating comments occur in a small line window.

**Mechanism:** Line-by-line narration increases visual noise and often signals that code structure or naming carries too little intent.

**Bad candidate:** `# get user ... # check user ... # return result ...`

**Legitimate counterexample:** A compact rationale block explains a protocol edge case before non-obvious code.

**Limitations:** The cluster is derived from COM401-style narrow candidates and should not gate CI by default.

**Recommendation:** Consider removing narration and strengthening names/structure; keep comments that preserve rationale or constraints.

Suppress locally with `# repoverity: ignore[COM402] - <reason>` when the exception is intentional.

## DEAD501 — Unused parameter candidate

A function parameter has no load reference in its body and is not recognized as a compatibility/callback placeholder.

**Mechanism:** Unused parameters can indicate speculative API surface, stale contracts, or incomplete implementation.

**Bad candidate:** `def transform(payload, options): return payload  # options unused`

**Legitimate counterexample:** def on_event(event, _context): ...  # explicit ignored compatibility parameter

**Limitations:** Methods on classes with explicit bases and common callback signatures are excluded; dynamic framework behavior can still be missed.

**Recommendation:** Remove it when the signature is private and controlled, or document/suppress the compatibility contract that requires it.

Suppress locally with `# repoverity: ignore[DEAD501] - <reason>` when the exception is intentional.

## DEAD502 — Unused private helper candidate

A private top-level function has no static name or attribute reference elsewhere in analyzed Python source.

**Mechanism:** Dead helpers preserve obsolete concepts, enlarge review surface, and can mislead maintainers about supported paths.

**Bad candidate:** `def _legacy_parse(...): ...  # no references`

**Legitimate counterexample:** @registry.register
def _plugin_hook(...): ...  # decorated, dynamically consumed

**Limitations:** The rule intentionally targets private top-level functions only and is lower severity than a proven unreachable path.

**Recommendation:** Remove the helper if it is truly dead, or document/suppress dynamic registration/reflection use.

Suppress locally with `# repoverity: ignore[DEAD502] - <reason>` when the exception is intentional.

## DEAD504 — Placeholder production branch

A non-test, non-abstract production path contains a pass-only branch/function or raises NotImplementedError.

**Mechanism:** Reachable placeholders can silently skip required behavior or fail only after deployment reaches an untested path.

**Bad candidate:** `def save(...): raise NotImplementedError`

**Legitimate counterexample:** @abstractmethod
def save(...): raise NotImplementedError

**Limitations:** Abstract methods, Protocol/ABC-style classes, tests, and ellipsis-only typing stubs are excluded where identifiable.

**Recommendation:** Implement the path, make the abstraction explicitly abstract, or remove unreachable/speculative surface.

Suppress locally with `# repoverity: ignore[DEAD504] - <reason>` when the exception is intentional.

## TST602 — Error branch lacks direct test signal

A public boundary-like function raises an explicit exception but tests do not reference both the symbol and exception/raises behavior.

**Mechanism:** Failure paths often survive happy-path tests and are disproportionately important at parsing, validation, configuration, and I/O boundaries.

**Bad candidate:** `parse_config() raises ConfigError, but tests contain no parse_config + raises/ConfigError evidence`

**Legitimate counterexample:** test_parse_config_rejects_invalid_toml uses pytest.raises(ConfigError)

**Limitations:** This is a static reference map, not coverage instrumentation; absence means 'no direct evidence found,' not 'untested with certainty.'

**Recommendation:** Add a focused test that drives the error branch and asserts the observable failure contract.

Suppress locally with `# repoverity: ignore[TST602] - <reason>` when the exception is intentional.

## TST603 — Parser/input boundary lacks malformed-input fixture signal

A parse/decode/load/validate boundary has branching or exceptions but no direct test signal using malformed/invalid/error input vocabulary.

**Mechanism:** AI-assisted parsers often look plausible on happy paths while malformed inputs expose assumptions, crashes, or silent acceptance.

**Bad candidate:** `def parse_manifest(text): ... branches ...; tests only cover valid manifest`

**Legitimate counterexample:** test_parse_manifest_invalid_header() drives malformed input and asserts failure

**Limitations:** RepoVerity looks for direct symbol references plus a narrow invalid-input vocabulary; it does not claim measured coverage.

**Recommendation:** Add malformed, empty, boundary-size, or invalid-shape fixtures tied to the parser's documented contract.

Suppress locally with `# repoverity: ignore[TST603] - <reason>` when the exception is intentional.

## TST604 — CLI entry point lacks integration smoke-test signal

Project metadata declares a console script but tests show no subprocess/runner/--help style invocation evidence for it.

**Mechanism:** Unit tests of command internals can miss packaging, entry-point wiring, argument parsing, and exit-code failures.

**Bad candidate:** `[project.scripts] tool=... but tests only call internal functions`

**Legitimate counterexample:** subprocess.run([sys.executable, '-m', 'tool', '--help'], ...) asserts exit 0

**Limitations:** Static test-text evidence cannot see remote/private acceptance systems, so suppression with rationale is appropriate there.

**Recommendation:** Add at least one installed/entry-point smoke test for --help/version and one behavior/exit-code path.

Suppress locally with `# repoverity: ignore[TST604] - <reason>` when the exception is intentional.

## REL701 — Package metadata is incomplete or inconsistent

Core packaging/release metadata expected for a distributable CLI is missing or points to absent files.

**Mechanism:** Incomplete metadata creates install, licensing, compatibility, discovery, and release ambiguity that often appears only at publication time.

**Bad candidate:** `pyproject has no requires-python or points readme to a missing file`

**Legitimate counterexample:** name/version/requires-python/license/readme/CLI entry point are internally consistent

**Limitations:** The rule checks a small packaging contract, not every PyPI metadata recommendation.

**Recommendation:** Complete the reported metadata fields and ensure referenced README/license/entry-point files exist.

Suppress locally with `# repoverity: ignore[REL701] - <reason>` when the exception is intentional.

## REL704 — CI does not exercise declared Python range edges

The project declares a bounded supported Python range, but GitHub workflow text does not include both the minimum and highest supported minor versions.

**Mechanism:** A package can claim compatibility that no automated runner verifies, allowing syntax/API drift at range edges.

**Bad candidate:** `requires-python='>=3.11,<3.15' but workflow only runs 3.13`

**Legitimate counterexample:** CI includes 3.11 and 3.14 jobs for >=3.11,<3.15

**Limitations:** The rule currently recognizes bounded requires-python ranges and GitHub workflow text; external CI requires suppression/configuration.

**Recommendation:** Add CI jobs for the minimum and highest supported Python minors; keep the matrix intentionally small.

Suppress locally with `# repoverity: ignore[REL704] - <reason>` when the exception is intentional.
