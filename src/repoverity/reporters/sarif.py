"""SARIF 2.1.0 serializer for GitHub code scanning."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote

from repoverity import __version__
from repoverity.models import AuditResult, Severity
from repoverity.rules.registry import all_rules


SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"


def _level(severity: Severity) -> str:
    if severity in {Severity.CRITICAL, Severity.HIGH}:
        return "error"
    if severity is Severity.MEDIUM:
        return "warning"
    return "note"


def _rule_descriptor(rule) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    return {
        "id": rule.rule_id,
        "name": rule.rule_id,
        "shortDescription": {"text": rule.title},
        "fullDescription": {"text": rule.summary},
        "defaultConfiguration": {"level": _level(rule.severity)},
        "properties": {
            "tags": list(rule.tags),
            "precision": rule.confidence.value,
            "evidenceLevel": rule.evidence_level.value,
        },
    }


def _result(item) -> dict[str, Any]:  # type: ignore[no-untyped-def]
    location: dict[str, Any] = {
        "physicalLocation": {
            "artifactLocation": {
                "uri": quote(item.location.path.replace("\\", "/"), safe="/:@-._~"),
                "uriBaseId": "%SRCROOT%",
            },
        }
    }
    if item.location.start_line is not None:
        region: dict[str, int] = {"startLine": max(item.location.start_line, 1)}
        if item.location.start_column is not None:
            region["startColumn"] = max(item.location.start_column + 1, 1)
        if item.location.end_line is not None:
            region["endLine"] = max(item.location.end_line, region["startLine"])
        if item.location.end_column is not None:
            region["endColumn"] = max(item.location.end_column + 1, 1)
        location["physicalLocation"]["region"] = region
    return {
        "ruleId": item.rule_id,
        "level": _level(item.severity),
        "message": {"text": f"{item.message} Evidence: {item.evidence}"},
        "locations": [location],
        "partialFingerprints": {"repoverityFingerprint": item.fingerprint},
        "properties": {
            "confidence": item.confidence.value,
            "evidenceLevel": item.evidence_level.value,
            "baselineStatus": item.baseline_status.value,
            "tags": list(item.tags),
        },
    }


def sarif_payload(result: AuditResult) -> dict[str, Any]:
    used_rule_ids = {finding.rule_id for finding in result.findings}
    rules = [_rule_descriptor(rule) for rule in all_rules() if rule.rule_id in used_rule_ids]
    return {
        "$schema": SARIF_SCHEMA,
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "RepoVerity",
                        "semanticVersion": __version__,
                        "rules": rules,
                    }
                },
                "originalUriBaseIds": {"%SRCROOT%": {"uri": "./"}},
                "results": [_result(item) for item in result.findings],
            }
        ],
    }


def render_sarif(result: AuditResult) -> str:
    return json.dumps(sarif_payload(result), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
