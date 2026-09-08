"""Release-hygiene rules."""

from __future__ import annotations

from pathlib import Path

from repoverity.rules.base import AnalysisContext, finding


def _project_dynamic(context: AnalysisContext) -> set[str]:
    project = context.metadata.raw.get("project", {})
    if not isinstance(project, dict):
        return set()
    raw = project.get("dynamic", [])
    if not isinstance(raw, list):
        return set()
    return {str(item) for item in raw}


def _metadata_gaps(context: AnalysisContext) -> list[str]:
    gaps: list[str] = []
    metadata = context.metadata
    dynamic = _project_dynamic(context)
    if metadata.parse_error:
        return [f"pyproject metadata parse error: {metadata.parse_error}"]
    if not metadata.name:
        gaps.append("project.name missing")
    if not metadata.version and "version" not in dynamic:
        gaps.append("project.version missing and not dynamic")
    if not metadata.requires_python:
        gaps.append("project.requires-python missing")
    if not metadata.readme:
        gaps.append("project.readme missing")
    elif not (context.root / metadata.readme).is_file():
        gaps.append(f"declared readme file '{metadata.readme}' does not exist")
    if metadata.license_value is None and not any(
        (context.root / candidate).is_file()
        for candidate in ("LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING")
    ):
        gaps.append("license metadata/file missing")
    return gaps


def _workflow_text(root: Path) -> str:
    workflow_dir = root / ".github" / "workflows"
    if not workflow_dir.is_dir():
        return ""
    chunks: list[str] = []
    for path in sorted((*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml"))):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            chunks.append(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    return "\n".join(chunks)


def analyze(context: AnalysisContext):  # type: ignore[no-untyped-def]
    findings = []
    gaps = _metadata_gaps(context)
    if gaps:
        findings.append(
            finding(
                "REL701",
                None,
                message=f"Package metadata has {len(gaps)} release-readiness gap(s).",
                evidence="; ".join(gaps),
                line=1,
                symbol="project-metadata",
                anchor="|".join(gaps),
                metadata={"gaps": gaps},
            )
        )

    minimum = context.metadata.minimum_python_minor
    maximum_exclusive = context.metadata.maximum_python_minor_exclusive
    if minimum is not None and maximum_exclusive is not None and maximum_exclusive > minimum:
        highest = maximum_exclusive - 1
        workflows = _workflow_text(context.root)
        minimum_signal = f"3.{minimum}" in workflows
        highest_signal = f"3.{highest}" in workflows
        if not (minimum_signal and highest_signal):
            findings.append(
                finding(
                    "REL704",
                    None,
                    message=(
                        f"CI does not visibly exercise both Python 3.{minimum} and 3.{highest}, the declared range edges."
                    ),
                    evidence=(
                        f"requires-python={context.metadata.requires_python!r}; workflow text contains 3.{minimum}="
                        f"{'yes' if minimum_signal else 'no'}, 3.{highest}={'yes' if highest_signal else 'no'}."
                    ),
                    line=1,
                    symbol="python-ci-range",
                    anchor=f"3.{minimum}-3.{highest}",
                )
            )
    return findings
