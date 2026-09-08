"""Shareable Markdown report and compact trust receipt."""

from __future__ import annotations

from collections import Counter

from repoverity import __version__
from repoverity.models import AuditResult


def _inline_code(value: str) -> str:
    """Render untrusted report text as stable Markdown inline code."""
    normalized = " ".join(value.splitlines())
    fence = "``" if "`" in normalized else "`"
    return f"{fence}{normalized}{fence}"


def _paragraph(value: str) -> str:
    """Keep finding text from injecting headings/tables through newlines."""
    return " ".join(value.splitlines())


_CATEGORY_NAMES = {
    "dependency-reality": "Runtime reality",
    "architecture": "Architecture",
    "naming": "Naming",
    "comments": "Comments",
    "dead-surface": "Dead surface",
    "test-boundaries": "Test boundaries",
    "release-hygiene": "Release hygiene",
}


def render_markdown(result: AuditResult) -> str:
    new_counts = Counter(finding.severity.value for finding in result.new_findings)
    lines = [
        "# RepoVerity Code Trust Report",
        "",
        "## Code Trust Receipt",
        "",
        f"- Repository: {_inline_code(result.root_display)}",
        f"- Commit: {_inline_code(result.commit or 'not available')}",
        f"- New high/critical findings: {new_counts.get('high', 0) + new_counts.get('critical', 0)}",
        f"- New medium findings: {new_counts.get('medium', 0)}",
        f"- Baseline regressions: {len(result.new_findings)}",
        f"- Existing findings: {len(result.existing_findings)}",
        f"- Resolved findings: {len(result.resolved_fingerprints)}",
        f"- Analyzer version: {_inline_code(__version__)}",
        "",
        "## Summary",
        "",
        "| Category | Critical/High | Medium | Low/Info | Total |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for category, display in _CATEGORY_NAMES.items():
        matches = [finding for finding in result.findings if finding.category == category]
        counts = Counter(finding.severity.value for finding in matches)
        high = counts.get("critical", 0) + counts.get("high", 0)
        medium = counts.get("medium", 0)
        low = counts.get("low", 0) + counts.get("info", 0)
        lines.append(f"| {display} | {high} | {medium} | {low} | {len(matches)} |")

    lines.extend(["", "## Findings", ""])
    if not result.findings:
        lines.append("No findings at the selected scope.")
    else:
        for item in result.findings[:50]:
            location = item.location.path
            if item.location.start_line is not None:
                location += f":{item.location.start_line}"
            lines.extend(
                [
                    f"### {item.rule_id} — {item.title}",
                    "",
                    f"**{item.severity.value.upper()} · {item.confidence.value} confidence · "
                    f"{item.evidence_level.value} evidence · {item.baseline_status.value}**",
                    f"Location: {_inline_code(location)}",
                    "",
                    _paragraph(item.message),
                    "",
                    f"**Evidence:** {_paragraph(item.evidence)}",
                    "",
                    f"**Mechanism:** {_paragraph(item.mechanism)}",
                    "",
                    f"**Next action:** {_paragraph(item.recommendation)}",
                    "",
                    f"**Legitimate exception:** {_paragraph(item.exception_note)}",
                    "",
                ]
            )
        if len(result.findings) > 50:
            lines.append(f"_Report truncated after 50 of {len(result.findings)} findings._")

    if result.issues:
        lines.extend(["", "## Analysis issues", ""])
        for issue in result.issues:
            lines.append(
                f"- {_inline_code(issue.kind)} {_inline_code(issue.path)} — {_paragraph(issue.message)}"
            )

    lines.extend(
        [
            "",
            "---",
            f"Generated locally by RepoVerity {__version__}. RepoVerity does not upload source code or detect AI authorship.",
            "",
        ]
    )
    return "\n".join(lines)
