from __future__ import annotations

import json
from pathlib import Path

from repoverity.config import Config
from repoverity.engine import AuditOptions, audit_repository
from repoverity.models import (
    AnalysisIssue,
    AuditResult,
    Confidence,
    EvidenceLevel,
    Finding,
    Location,
    RepositoryStats,
    Severity,
)
from repoverity.reporters import render_json, render_markdown, render_sarif, render_terminal
from repoverity.reporters.sarif import sarif_payload


def sample_result(path: str = "src/a b`c.py") -> AuditResult:
    finding = Finding(
        rule_id="NAM302",
        category="naming",
        severity=Severity.LOW,
        confidence=Confidence.MEDIUM,
        evidence_level=EvidenceLevel.HEURISTIC,
        title="Generic API",
        message="line one\n| injected",
        mechanism="mechanism\n# heading",
        location=Location(path, 1, 0, 1, 4),
        evidence="evidence\n```",
        recommendation="rename\nnow",
        exception_note="framework\ncontract",
        fingerprint="abc123",
        tags=("maintainability",),
    )
    return AuditResult(
        "repo`name",
        (finding,),
        (AnalysisIssue("odd|path", "parse-error", "bad\ntext"),),
        RepositoryStats(1, 1, 0.01),
    )


def test_json_is_parseable_and_versioned() -> None:
    payload = json.loads(render_json(sample_result()))
    assert payload["schema_version"] == "1.0"
    assert payload["findings"][0]["rule_id"] == "NAM302"


def test_markdown_sanitizes_multiline_untrusted_text() -> None:
    report = render_markdown(sample_result())
    assert "line one | injected" in report
    assert "mechanism # heading" in report
    assert "``repo`name``" in report


def test_sarif_is_21_and_uri_encodes_path() -> None:
    payload = sarif_payload(sample_result())
    assert payload["version"] == "2.1.0"
    uri = payload["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"][
        "uri"
    ]
    assert "%20" in uri and "%60" in uri
    assert json.loads(render_sarif(sample_result()))["version"] == "2.1.0"


def test_terminal_no_color_has_no_ansi() -> None:
    assert "\x1b[" not in render_terminal(sample_result(), no_color=True)


def test_repository_reporters_on_clean_project(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    result = audit_repository(tmp_path, Config(), AuditOptions())
    json.loads(render_json(result))
    json.loads(render_sarif(result))
    assert "RepoVerity Code Trust Report" in render_markdown(result)


def test_reporters_and_finding_order_are_deterministic(tmp_path: Path) -> None:
    (tmp_path / "b.py").write_text("import requests\n", encoding="utf-8")
    (tmp_path / "a.py").write_text("import yaml\n", encoding="utf-8")

    first = audit_repository(tmp_path, Config(), AuditOptions())
    second = audit_repository(tmp_path, Config(), AuditOptions())

    assert [item.fingerprint for item in first.findings] == [
        item.fingerprint for item in second.findings
    ]
    first_json = json.loads(render_json(first))
    second_json = json.loads(render_json(second))
    first_json.pop("timing")
    second_json.pop("timing")
    assert first_json == second_json
    assert render_markdown(first) == render_markdown(second)
    assert render_sarif(first) == render_sarif(second)


def test_sarif_rule_mapping_locations_and_fingerprints_are_valid() -> None:
    payload = sarif_payload(sample_result("src/pkg/module.py"))
    run = payload["runs"][0]
    rule_ids = [rule["id"] for rule in run["tool"]["driver"]["rules"]]
    assert len(rule_ids) == len(set(rule_ids))
    result = run["results"][0]
    assert result["ruleId"] in rule_ids
    region = result["locations"][0]["physicalLocation"]["region"]
    assert region["startLine"] > 0
    artifact = result["locations"][0]["physicalLocation"]["artifactLocation"]
    assert not artifact["uri"].startswith("/")
    assert "\\" not in artifact["uri"]
    assert result["partialFingerprints"]["repoverityFingerprint"] == "abc123"
