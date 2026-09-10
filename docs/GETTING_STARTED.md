# Getting Started with RepoVerity

RepoVerity is designed to be useful in three stages: first as a local reviewer, then as a regression gate, and finally as a CI/code-scanning signal.

## 1. Install and verify

Install from PyPI:

```bash
python -m pip install repoverity
repoverity --version
```

Expected first-release output:

```text
RepoVerity 0.1.0
```

For environment details:

```bash
repoverity version
```

That command also prints the active Python and platform, which is useful when reproducing a report.

## 2. Run the first audit

From the root of a Python repository:

```bash
repoverity audit .
```

Start by reading the highest-severity findings, but do not treat severity as certainty. For every unfamiliar rule, inspect its rationale and counterexample:

```bash
repoverity explain DEP101
```

A finding is intended to answer four reviewer questions:

1. **What did RepoVerity observe?**
2. **Why can that condition matter?**
3. **How certain is the inference from static evidence?**
4. **What legitimate design could look similar?**

This prevents a heuristic signal from being presented as proof.

## 3. Narrow the audit while adopting it

If a large existing repository produces more findings than you want to review at once, start with a narrow rule set:

```bash
repoverity audit . --rules DEP101,REL801,TST602
```

Or filter by severity:

```bash
repoverity audit . --severity medium
```

The objective is not to reach an arbitrary score. It is to decide which findings represent real repository risk, which are intentional, and which require an explicit exception.

## 4. Establish a baseline

A baseline lets an established codebase adopt RepoVerity without requiring an immediate cleanup of all historical findings.

```bash
repoverity baseline create . --output .trust-baseline.json
```

Commit that baseline after reviewing it. Future audits can then distinguish new, existing, and resolved findings:

```bash
repoverity audit . --baseline .trust-baseline.json --fail-on high
```

The CI gate evaluates new findings rather than failing because historical findings still exist.

## 5. Review only changed work

For pull-request-oriented analysis:

```bash
repoverity audit . \
  --changed-only origin/main \
  --baseline .trust-baseline.json \
  --fail-on high
```

Changed-only mode includes branch commits plus staged, unstaged, and untracked paths. Deleted and renamed paths are handled as Git changes rather than guessed from timestamps.

If Git information is unavailable, RepoVerity emits a warning and performs a full audit instead of silently reporting nothing.

## 6. Use the output that matches the workflow

Terminal output is best for local work:

```bash
repoverity audit .
```

Markdown is useful in reviews and release evidence:

```bash
repoverity audit . --format markdown --output trust-report.md
```

JSON is intended for automation:

```bash
repoverity audit . --format json --output trust.json
```

SARIF can be uploaded to GitHub code scanning:

```bash
repoverity audit . --format sarif --output trust.sarif
```

## 7. Add the GitHub Action

A minimal workflow step is:

```yaml
- uses: aprashnasuraj-dev/AI-Code-Quality-Trust-Layers@v0.1.0
  with:
    path: .
    fail-on: high
```

For an existing repository, baseline-aware use is usually more practical:

```yaml
- uses: aprashnasuraj-dev/AI-Code-Quality-Trust-Layers@v0.1.0
  with:
    path: .
    fail-on: high
    baseline: .trust-baseline.json
    changed-only: origin/main
```

The composite Action executes the checked-out RepoVerity source directly. It does not require a RepoVerity account, API key, hosted service, or network upload of the audited source.

## 8. Suppress only intentional exceptions

If a finding is legitimate by design, prefer documenting why rather than disabling an entire category:

```python
# repoverity: ignore[ABS201] - adapter boundary required by framework contract
```

That makes the exception visible to reviewers and keeps the rest of the rule active.

Project-level exclusions and rule policy can be configured in `pyproject.toml`:

```toml
[tool.repoverity]
exclude = ["generated/**"]
fail-on = "high"

[tool.repoverity.rules]
ABS201 = "warn"
COM402 = "off"
```

CLI options take precedence over project configuration, which takes precedence over defaults.

## 9. Interpret results conservatively

RepoVerity uses static evidence. It cannot see every runtime contract, framework convention, plugin registration path, dependency injected externally, or indirect test path.

A useful review pattern is:

- **verified finding**: fix or explain it first;
- **inferred finding**: inspect the surrounding contract before changing code;
- **heuristic finding**: treat it as a prompt for review rather than an automatic defect.

The counterexample included with each rule is part of the product contract, not decoration.

## 10. Report a false positive well

A useful false-positive report includes:

```bash
repoverity version
repoverity explain RULE_ID
```

Then provide the smallest repository example that reproduces the finding, explain the real contract RepoVerity could not observe, and state whether the case should be recognized automatically or remain an explicit suppression.

Issue templates are included for bugs, false positives, and rule proposals.

## Next steps

- Rule catalog: [`RULES.md`](RULES.md)
- Architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Security boundaries: [`SECURITY_MODEL.md`](SECURITY_MODEL.md)
- Baseline behavior: [`BASELINE.md`](BASELINE.md)
- GitHub Action: [`GITHUB_ACTION.md`](GITHUB_ACTION.md)
- Output contracts: [`OUTPUT_FORMATS.md`](OUTPUT_FORMATS.md)
- Known limitations: [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md)
