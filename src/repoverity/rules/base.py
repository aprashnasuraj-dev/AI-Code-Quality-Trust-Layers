"""Shared analysis context and finding construction helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from repoverity.discovery import SourceFile
from repoverity.fingerprints import make_fingerprint
from repoverity.models import Finding, Location
from repoverity.project import ProjectMetadata
from repoverity.rules.registry import get_rule


@dataclass(frozen=True, slots=True)
class AnalysisContext:
    root: Path
    sources: tuple[SourceFile, ...]
    metadata: ProjectMetadata
    test_text: str
    all_text: str
    local_modules: frozenset[str]

    @property
    def production_sources(self) -> tuple[SourceFile, ...]:
        return tuple(source for source in self.sources if not source.is_test)

    @property
    def test_sources(self) -> tuple[SourceFile, ...]:
        return tuple(source for source in self.sources if source.is_test)


def finding(
    rule_id: str,
    source: SourceFile | None,
    *,
    message: str,
    evidence: str,
    line: int | None = None,
    column: int | None = None,
    end_line: int | None = None,
    end_column: int | None = None,
    symbol: str | None = None,
    anchor: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> Finding:
    meta = get_rule(rule_id)
    if meta is None:  # internal programmer error
        raise KeyError(f"unknown rule metadata: {rule_id}")
    path = source.relpath if source is not None else "pyproject.toml"
    finding_metadata: dict[str, Any] = dict(metadata or {})
    if symbol:
        finding_metadata.setdefault("symbol", symbol)
    fingerprint = make_fingerprint(
        rule_id,
        path,
        symbol=symbol,
        anchor=anchor or message,
        extra={key: finding_metadata[key] for key in sorted(finding_metadata) if key.startswith("fp_")},
    )
    return Finding(
        rule_id=rule_id,
        category=meta.category,
        severity=meta.severity,
        confidence=meta.confidence,
        evidence_level=meta.evidence_level,
        title=meta.title,
        message=message,
        mechanism=meta.mechanism,
        location=Location(path, line, column, end_line, end_column),
        evidence=evidence,
        recommendation=meta.recommendation,
        exception_note=meta.exception_note,
        fingerprint=fingerprint,
        tags=meta.tags,
        metadata=finding_metadata,
    )
