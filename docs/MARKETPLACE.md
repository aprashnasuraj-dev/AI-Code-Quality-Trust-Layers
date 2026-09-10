# GitHub Marketplace Listing Notes

RepoVerity is published as a **free GitHub Action** for Python repository trust auditing.

## Listing name

**RepoVerity Code Trust Audit**

## Short description

Audit Python repositories for dependency, abstraction, test-boundary, dead-code, and release-hygiene trust gaps—without uploading or executing target code.

## Suggested categories

- Primary: **Code quality**
- Secondary: **Continuous integration**

## Marketplace positioning

RepoVerity sits between ordinary linting and heavyweight code-quality platforms. It is designed for maintainers who already run formatters, linters, type checkers, tests, and security scanners but still need repository-level evidence about whether release claims, dependencies, abstractions, tests, and dead surfaces line up.

Unlike AI-authorship detectors, RepoVerity does not estimate who or what wrote the code. It analyzes the repository that actually exists.

## Key reasons to try it

- 18 deterministic trust rules across seven categories.
- No RepoVerity account, API key, hosted backend, or source upload.
- No target-module imports or target-code execution during the audit.
- Baselines separate historical findings from new regressions.
- Changed-only mode fits pull-request workflows.
- SARIF output integrates with GitHub code scanning.
- Every finding includes severity, confidence, evidence level, mechanism, counterexample, remediation, fingerprint, and suppression guidance.
- The Action runs directly from its checked-out source and has zero runtime package dependencies.

## Quick Marketplace example

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

For an established repository, add a reviewed baseline:

```yaml
      - uses: aprashnasuraj-dev/AI-Code-Quality-Trust-Layers@v0.1.0
        with:
          path: .
          fail-on: high
          baseline: .trust-baseline.json
          changed-only: origin/main
```

## Important limitations to state publicly

RepoVerity is a static evidence tool. It does not prove correctness, replace runtime tests, or fully understand reflection-heavy frameworks and plugin registration. A clean report means no configured RepoVerity rule matched—not that software is defect-free.

## Publication note

GitHub currently requires Marketplace publication of an Action to be selected from the release UI. The repository owner must accept the GitHub Marketplace Developer Agreement if not already accepted, select **Publish this Action to the GitHub Marketplace**, choose categories, and complete the release with two-factor authentication. The repository's `action.yml`, README, release notes, security policy, and release tag are prepared for that listing.
