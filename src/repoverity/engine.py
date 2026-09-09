"""Repository audit orchestration; domain logic remains outside reporters and CLI."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from repoverity.baseline import classify_findings, load_baseline
from repoverity.config import Config, configured_severity
from repoverity.discovery import SourceFile, discover_sources
from repoverity.gitdiff import changed_paths, current_commit
from repoverity.models import (
    SEVERITY_RANK,
    AnalysisIssue,
    AuditResult,
    Finding,
    RepositoryStats,
    Severity,
)
from repoverity.project import load_project_metadata
from repoverity.rules import ANALYZERS, AnalysisContext
from repoverity.suppressions import is_suppressed


@dataclass(frozen=True, slots=True)
class AuditOptions:
    minimum_severity: Severity = Severity.INFO
    selected_rules: frozenset[str] | None = None
    baseline_path: Path | None = None
    changed_only_base: str | None = None


def _local_modules(root: Path, sources: tuple[SourceFile, ...]) -> frozenset[str]:
    modules: set[str] = set()
    for source in sources:
        parts = source.relpath.split("/")
        if len(parts) == 1:
            modules.add(Path(parts[0]).stem)
        elif parts[0] == "src" and len(parts) >= 2:
            modules.add(parts[1].removesuffix(".py"))
        else:
            modules.add(parts[0].removesuffix(".py"))
    for base in (root, root / "src"):
        if not base.is_dir():
            continue
        for child in base.iterdir():
            if child.is_dir() and (child / "__init__.py").is_file():
                modules.add(child.name)
    return frozenset(modules)


def _changed_filter(findings: list[Finding], paths: frozenset[str]) -> list[Finding]:
    if not paths:
        return []
    project_files_changed = "pyproject.toml" in paths or any(
        path.startswith(".github/workflows/") for path in paths
    )
    return [
        finding
        for finding in findings
        if finding.location.path in paths
        or (finding.location.path == "pyproject.toml" and project_files_changed)
    ]


def _apply_config(findings: list[Finding], config: Config) -> list[Finding]:
    configured: list[Finding] = []
    for item in findings:
        setting = config.rule_settings.get(item.rule_id)
        if setting is None:
            configured.append(item)
            continue
        severity = configured_severity(setting, item.severity)
        if severity is not None:
            configured.append(item.with_severity(severity))
    return configured


def _sort_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(
        findings,
        key=lambda item: (
            -SEVERITY_RANK[item.severity],
            item.location.path,
            item.location.start_line or 0,
            item.rule_id,
            item.fingerprint,
        ),
    )


def audit_repository(root: Path, config: Config, options: AuditOptions) -> AuditResult:
    started = time.perf_counter()
    resolved_root = root.expanduser().resolve()
    warnings: list[str] = []
    changed: frozenset[str] | None = None
    if options.changed_only_base is not None:
        changed, warning = changed_paths(resolved_root, options.changed_only_base)
        if warning:
            warnings.append(warning)

    sources, discovery_issues, skipped = discover_sources(resolved_root, config.exclude)
    metadata = load_project_metadata(resolved_root)
    test_text = "\n".join(source.text for source in sources if source.is_test)
    context = AnalysisContext(
        root=resolved_root,
        sources=sources,
        metadata=metadata,
        test_text=test_text,
        all_text="\n".join(source.text for source in sources),
        local_modules=_local_modules(resolved_root, sources),
    )

    issues = list(discovery_issues)
    raw_findings: list[Finding] = []
    for analyzer in ANALYZERS:
        try:
            raw_findings.extend(analyzer(context))
        except Exception as exc:  # converted to explicit analysis failure, never silently skipped
            issues.append(
                AnalysisIssue(
                    "<repository>",
                    "rule-error",
                    f"{analyzer.__module__}.{analyzer.__name__}: {type(exc).__name__}: {exc}",
                )
            )

    if options.selected_rules is not None:
        raw_findings = [item for item in raw_findings if item.rule_id in options.selected_rules]
    raw_findings = _apply_config(raw_findings, config)

    source_by_path = {source.relpath: source for source in sources}
    raw_findings = [item for item in raw_findings if not is_suppressed(item, source_by_path)]
    raw_findings = [
        item
        for item in raw_findings
        if SEVERITY_RANK[item.severity] >= SEVERITY_RANK[options.minimum_severity]
    ]
    if changed is not None:
        raw_findings = _changed_filter(raw_findings, changed)

    sorted_findings = tuple(_sort_findings(raw_findings))
    resolved_fingerprints: tuple[str, ...] = ()
    baseline_path = options.baseline_path
    if baseline_path is not None:
        baseline = load_baseline(baseline_path)
        sorted_findings, resolved_fingerprints = classify_findings(sorted_findings, baseline)

    duration = time.perf_counter() - started
    stats = RepositoryStats(
        files_analyzed=len(sources),
        python_loc=sum(source.loc for source in sources),
        duration_seconds=duration,
        skipped_files=skipped,
    )
    return AuditResult(
        root_display=resolved_root.name or ".",
        findings=sorted_findings,
        issues=tuple(issues),
        stats=stats,
        resolved_fingerprints=resolved_fingerprints,
        warnings=tuple(warnings),
        commit=current_commit(resolved_root),
    )
