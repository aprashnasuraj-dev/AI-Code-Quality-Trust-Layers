"""Core immutable data models used by analysis and reporters."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


SEVERITY_RANK: dict[Severity, int] = {
    Severity.INFO: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


class Confidence(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


CONFIDENCE_RANK: dict[Confidence, int] = {
    Confidence.LOW: 0,
    Confidence.MEDIUM: 1,
    Confidence.HIGH: 2,
}


class EvidenceLevel(StrEnum):
    VERIFIED = "verified"
    INFERRED = "inferred"
    HEURISTIC = "heuristic"


class BaselineStatus(StrEnum):
    NEW = "new"
    EXISTING = "existing"


@dataclass(frozen=True, slots=True)
class Location:
    path: str
    start_line: int | None = None
    start_column: int | None = None
    end_line: int | None = None
    end_column: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "start_line": self.start_line,
            "start_column": self.start_column,
            "end_line": self.end_line,
            "end_column": self.end_column,
        }


@dataclass(frozen=True, slots=True)
class Finding:
    rule_id: str
    category: str
    severity: Severity
    confidence: Confidence
    evidence_level: EvidenceLevel
    title: str
    message: str
    mechanism: str
    location: Location
    evidence: str
    recommendation: str
    exception_note: str
    fingerprint: str
    tags: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    baseline_status: BaselineStatus = BaselineStatus.NEW

    def with_baseline_status(self, status: BaselineStatus) -> Finding:
        return replace(self, baseline_status=status)

    def with_severity(self, severity: Severity) -> Finding:
        return replace(self, severity=severity)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "category": self.category,
            "severity": self.severity.value,
            "confidence": self.confidence.value,
            "evidence_level": self.evidence_level.value,
            "title": self.title,
            "message": self.message,
            "mechanism": self.mechanism,
            "location": self.location.to_dict(),
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "exception_note": self.exception_note,
            "fingerprint": self.fingerprint,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
            "baseline_status": self.baseline_status.value,
        }


@dataclass(frozen=True, slots=True)
class AnalysisIssue:
    path: str
    kind: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "kind": self.kind, "message": self.message}


@dataclass(frozen=True, slots=True)
class RepositoryStats:
    files_analyzed: int
    python_loc: int
    duration_seconds: float
    skipped_files: int = 0

    def to_dict(self) -> dict[str, int | float]:
        return {
            "files_analyzed": self.files_analyzed,
            "python_loc": self.python_loc,
            "duration_seconds": round(self.duration_seconds, 6),
            "skipped_files": self.skipped_files,
        }


@dataclass(frozen=True, slots=True)
class AuditResult:
    root_display: str
    findings: tuple[Finding, ...]
    issues: tuple[AnalysisIssue, ...]
    stats: RepositoryStats
    resolved_fingerprints: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    commit: str | None = None

    @property
    def new_findings(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.baseline_status is BaselineStatus.NEW)

    @property
    def existing_findings(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.baseline_status is BaselineStatus.EXISTING)
