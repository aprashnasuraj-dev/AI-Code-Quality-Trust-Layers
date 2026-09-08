"""Reporter-only summary helpers."""

from __future__ import annotations

from collections import Counter
from typing import Any

from repoverity.models import AuditResult, Severity


def summary_dict(result: AuditResult) -> dict[str, Any]:
    severity_counts = Counter(finding.severity.value for finding in result.findings)
    category_counts = Counter(finding.category for finding in result.findings)
    new_severity = Counter(finding.severity.value for finding in result.new_findings)
    return {
        "total_findings": len(result.findings),
        "new_findings": len(result.new_findings),
        "existing_findings": len(result.existing_findings),
        "resolved_findings": len(result.resolved_fingerprints),
        "by_severity": {severity.value: severity_counts.get(severity.value, 0) for severity in Severity},
        "new_by_severity": {severity.value: new_severity.get(severity.value, 0) for severity in Severity},
        "by_category": dict(sorted(category_counts.items())),
        "analysis_issues": len(result.issues),
    }
