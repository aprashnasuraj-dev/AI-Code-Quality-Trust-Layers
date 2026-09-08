"""Versioned deterministic JSON reporter."""

from __future__ import annotations

import json
from typing import Any

from repoverity import __version__
from repoverity.models import AuditResult
from repoverity.reporters.common import summary_dict


JSON_SCHEMA_VERSION = "1.0"


def payload(result: AuditResult) -> dict[str, Any]:
    return {
        "schema_version": JSON_SCHEMA_VERSION,
        "tool": {"name": "repoverity", "version": __version__},
        "repository": {"path": result.root_display, "commit": result.commit},
        "summary": summary_dict(result),
        "findings": [finding.to_dict() for finding in result.findings],
        "analysis_issues": [issue.to_dict() for issue in result.issues],
        "warnings": list(result.warnings),
        "timing": result.stats.to_dict(),
        "resolved_fingerprints": list(result.resolved_fingerprints),
    }


def render_json(result: AuditResult) -> str:
    return json.dumps(payload(result), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
