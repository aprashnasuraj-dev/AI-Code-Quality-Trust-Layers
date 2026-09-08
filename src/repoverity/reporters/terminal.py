"""Concise terminal reporter."""

from __future__ import annotations

from collections import Counter
import os
import sys

from repoverity import __version__
from repoverity.models import AuditResult, Severity
from repoverity.rules.registry import all_rules


_CATEGORY_ORDER = (
    "dependency-reality",
    "architecture",
    "naming",
    "comments",
    "dead-surface",
    "test-boundaries",
    "release-hygiene",
)


def _color_enabled(no_color: bool) -> bool:
    return not no_color and "NO_COLOR" not in os.environ and sys.stdout.isatty()


def _paint(text: str, code: str, enabled: bool) -> str:
    return f"\x1b[{code}m{text}\x1b[0m" if enabled else text


def _severity_label(severity: Severity, color: bool) -> str:
    code = {
        Severity.CRITICAL: "1;31",
        Severity.HIGH: "31",
        Severity.MEDIUM: "33",
        Severity.LOW: "36",
        Severity.INFO: "37",
    }[severity]
    return _paint(severity.value.upper(), code, color)


def render_terminal(result: AuditResult, *, no_color: bool = False, verbose: bool = False) -> str:
    color = _color_enabled(no_color)
    lines = [
        f"RepoVerity {__version__} — Code Trust Audit",
        f"Repository: {result.root_display}",
        (
            f"Files analyzed: {result.stats.files_analyzed} | Python LOC: {result.stats.python_loc:,} | "
            f"Duration: {result.stats.duration_seconds:.2f}s"
        ),
        "",
        "TRUST SUMMARY",
    ]

    by_category: dict[str, Counter[str]] = {}
    for category in _CATEGORY_ORDER:
        by_category[category] = Counter(
            finding.severity.value for finding in result.findings if finding.category == category
        )
    display_names = {
        "dependency-reality": "Runtime reality",
        "architecture": "Architecture",
        "naming": "Naming",
        "comments": "Comments",
        "dead-surface": "Dead surface",
        "test-boundaries": "Test boundaries",
        "release-hygiene": "Release hygiene",
    }
    for category in _CATEGORY_ORDER:
        counts = by_category[category]
        total = sum(counts.values())
        high = counts.get("critical", 0) + counts.get("high", 0)
        medium = counts.get("medium", 0)
        low = counts.get("low", 0) + counts.get("info", 0)
        lines.append(
            f"{display_names[category]:<20} {total:>3} finding(s)  "
            f"{high} high+ / {medium} medium / {low} low-info"
        )

    lines.extend(
        [
            "",
            (
                f"Baseline: {len(result.new_findings)} new / {len(result.existing_findings)} existing / "
                f"{len(result.resolved_fingerprints)} resolved"
            ),
            "",
            "HIGH-VALUE FINDINGS",
        ]
    )
    high_value = list(result.findings[:8])
    if not high_value:
        lines.append("No findings at the selected severity/rule scope.")
    else:
        for item in high_value:
            location = item.location.path
            if item.location.start_line is not None:
                location += f":{item.location.start_line}"
            status = "EXISTING" if item.baseline_status.value == "existing" else "NEW"
            lines.append(
                f"{item.rule_id:<7} {_severity_label(item.severity, color):<8} {status:<8} "
                f"{location}  {item.message}"
            )
            if verbose:
                lines.append(f"         evidence: {item.evidence}")
                lines.append(f"         next: {item.recommendation}")

    if result.issues:
        lines.extend(["", f"ANALYSIS ISSUES ({len(result.issues)})"])
        for issue in result.issues[:5]:
            lines.append(f"{issue.kind}: {issue.path}: {issue.message}")
        if len(result.issues) > 5:
            lines.append(f"... {len(result.issues) - 5} more; use --verbose with JSON for full details")
    if result.warnings:
        lines.extend(["", "WARNINGS"])
        lines.extend(result.warnings)

    lines.extend(
        [
            "",
            "Run:",
            "  repoverity explain RULE_ID",
            "  repoverity audit . --format markdown --output trust-report.md",
            "  repoverity audit . --format sarif --output trust.sarif",
        ]
    )
    return "\n".join(lines) + "\n"
