from __future__ import annotations

from pathlib import Path

from repoverity.rules.registry import all_rules


def main() -> None:
    lines = [
        "# Rule Reference",
        "",
        "RepoVerity v0.1 ships a small rule set. Severity, confidence and evidence level are separate dimensions.",
        "",
        "| Rule | Category | Severity | Confidence | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for rule in all_rules():
        lines.append(
            f"| {rule.rule_id} | {rule.category} | {rule.severity.value} | {rule.confidence.value} | {rule.evidence_level.value} |"
        )
    for rule in all_rules():
        lines.extend(
            [
                "",
                f"## {rule.rule_id} — {rule.title}",
                "",
                rule.summary,
                "",
                f"**Mechanism:** {rule.mechanism}",
                "",
                f"**Bad candidate:** `{rule.bad_example.replace(chr(10), ' ')}`",
                "",
                f"**Legitimate counterexample:** {rule.acceptable_example}",
                "",
                f"**Limitations:** {rule.limitations}",
                "",
                f"**Recommendation:** {rule.recommendation}",
                "",
                f"Suppress locally with `# repoverity: ignore[{rule.rule_id}] - <reason>` when the exception is intentional.",
            ]
        )
    Path("docs/RULES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
