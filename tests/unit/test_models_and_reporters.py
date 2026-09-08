from __future__ import annotations

import json
from pathlib import Path

from repoverity.config import Config
from repoverity.engine import AuditOptions, audit_repository
from repoverity.models import AnalysisIssue, AuditResult, Confidence, EvidenceLevel, Finding, Location, RepositoryStats, Severity
from repoverity.reporters import render_json, render_markdown, render_sarif, render_terminal
from repoverity.reporters.sarif import sarif_payload


def sample_result(path: str = "src/a b`c.py") -> AuditResult:
    finding = Finding(
        rule_id="NAM302", category="naming", severity=Severity.LOW,
        confidence=Confidence.MEDIUM, evidence_level=EvidenceLevel.HEURISTIC,
        title="Generic API", message="line one\n| injected", mechanism="mechanism\n# heading",
        location=Location(path, 1, 0, 1, 4), evidence="evidence\n```", recommendation="rename\nnow",
        exception_note="framework\ncontract", fingerprint="abc123", tags=("maintainability",),
    )
    return AuditResult("repo`name", (finding,), (AnalysisIssue("odd|path", "parse-error", "bad\ntext"),), RepositoryStats(1, 1, 0.01))


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
    uri = payload["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
    assert "%20" in uri and "%60" in uri
    assert json.loads(render_sarif(sample_result()))["version"] == "2.1.0"


def test_terminal_no_color_has_no_ansi() -> None:
    assert "\x1b[" not in render_terminal(sample_result(), no_color=True)


def test_repository_reporters_on_clean_project(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text("VALUE = 1\n")
    result = audit_repository(tmp_path, Config(), AuditOptions())
    json.loads(render_json(result))
    json.loads(render_sarif(result))
    assert "RepoVerity Code Trust Report" in render_markdown(result)
