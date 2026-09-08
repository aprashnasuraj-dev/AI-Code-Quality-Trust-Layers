# RepoVerity Code Trust Report

## Code Trust Receipt

- Repository: `intentionally_bad`
- Commit: `not available`
- New high/critical findings: 1
- New medium findings: 4
- Baseline regressions: 7
- Existing findings: 0
- Resolved findings: 0
- Analyzer version: `0.1.0`

## Summary

| Category | Critical/High | Medium | Low/Info | Total |
| --- | ---: | ---: | ---: | ---: |
| Runtime reality | 1 | 0 | 1 | 2 |
| Architecture | 0 | 1 | 0 | 1 |
| Naming | 0 | 0 | 0 | 0 |
| Comments | 0 | 0 | 0 | 0 |
| Dead surface | 0 | 0 | 1 | 1 |
| Test boundaries | 0 | 2 | 0 | 2 |
| Release hygiene | 0 | 1 | 0 | 1 |

## Findings

### DEP101 — Third-party import is not declared

**HIGH · high confidence · verified evidence · new**
Location: `src/inventory/audit.py:1`

Import 'requests' has no matching declared dependency.

**Evidence:** Static import 'requests' maps to candidate distribution(s): requests; none appear in project dependencies or optional groups.

**Mechanism:** Clean installs can fail at import time when a dependency is only present on the author machine.

**Next action:** Declare the distribution in project dependencies, or document/configure why the import is provided out-of-band.

**Legitimate exception:** Some imports are supplied by platform images, namespace packages, optional extras, vendored code, or distribution/import-name aliases.

### REL704 — CI does not exercise declared Python range edges

**MEDIUM · high confidence · verified evidence · new**
Location: `pyproject.toml:1`

CI does not visibly exercise both Python 3.11 and 3.14, the declared range edges.

**Evidence:** requires-python='>=3.11,<3.15'; workflow text contains 3.11=no, 3.14=no.

**Mechanism:** A package can claim compatibility that no automated runner verifies, allowing syntax/API drift at range edges.

**Next action:** Add CI jobs for the minimum and highest supported Python minors; keep the matrix intentionally small.

**Legitimate exception:** Compatibility may be tested in another CI provider or reusable workflow that is not visible in the repository text.

### ABS201 — Pass-through wrapper candidate

**MEDIUM · medium confidence · inferred evidence · new**
Location: `src/inventory/audit.py:4`

Class 'InventoryClient' delegates 2/2 public methods (100%) directly to self._inner.

**Evidence:** Dominant collaborator: self._inner; public methods: 2; direct delegates: 2; no behavior was inferred for those delegated bodies.

**Mechanism:** Layers that do not validate, translate, cache, retry, enforce policy, or define a contract can add cognitive and debugging hops.

**Next action:** Keep the boundary if it is intentional; otherwise consider exposing the collaborator or collapsing the wrapper.

**Legitimate exception:** Adapters, facades, dependency-injection seams, API compatibility layers, and plugin contracts may intentionally be thin.

### TST602 — Error branch lacks direct test signal

**MEDIUM · medium confidence · inferred evidence · new**
Location: `src/inventory/audit.py:19`

Boundary 'parse_manifest' raises explicit errors without direct test evidence.

**Evidence:** Static exceptions: ValueError. Test corpus signal: symbol=no, exception/raises=no.

**Mechanism:** Failure paths often survive happy-path tests and are disproportionately important at parsing, validation, configuration, and I/O boundaries.

**Next action:** Add a focused test that drives the error branch and asserts the observable failure contract.

**Legitimate exception:** Tests may reach the branch indirectly through higher-level APIs without naming the underlying symbol or exception.

### TST603 — Parser/input boundary lacks malformed-input fixture signal

**MEDIUM · medium confidence · inferred evidence · new**
Location: `src/inventory/audit.py:19`

Parser/input boundary 'parse_manifest' lacks malformed-input fixture evidence.

**Evidence:** Boundary contains branching/error logic. Test corpus signal: symbol=no, malformed-input vocabulary=no.

**Mechanism:** AI-assisted parsers often look plausible on happy paths while malformed inputs expose assumptions, crashes, or silent acceptance.

**Next action:** Add malformed, empty, boundary-size, or invalid-shape fixtures tied to the parser's documented contract.

**Legitimate exception:** Property-based tests or table-driven fixtures may provide excellent malformed-input coverage without using the searched vocabulary.

### DEP102 — Declared runtime dependency has no static import evidence

**LOW · medium confidence · inferred evidence · new**
Location: `pyproject.toml:1`

Runtime dependency 'httpx' has no static production import evidence.

**Evidence:** 'httpx' is declared in project.dependencies but no analyzed production import maps to that distribution.

**Mechanism:** Unused dependencies increase install surface, supply-chain exposure, and maintenance burden.

**Next action:** Confirm whether the dependency is dynamically loaded or packaging-only; remove it if it has no runtime role.

**Legitimate exception:** Plugins, entry points, subprocess tools, dynamic imports, and framework discovery may use a dependency without a static import.

### DEAD502 — Unused private helper candidate

**LOW · medium confidence · inferred evidence · new**
Location: `src/inventory/audit.py:15`

Private helper '_unused_helper' has no static reference in analyzed Python source.

**Evidence:** No Name-load or Attribute reference to this private top-level symbol was found.

**Mechanism:** Dead helpers preserve obsolete concepts, enlarge review surface, and can mislead maintainers about supported paths.

**Next action:** Remove the helper if it is truly dead, or document/suppress dynamic registration/reflection use.

**Legitimate exception:** String-based registration, decorators implemented outside the repository, reflection, and framework discovery may consume private symbols indirectly.


---
Generated locally by RepoVerity 0.1.0. RepoVerity does not upload source code or detect AI authorship.
