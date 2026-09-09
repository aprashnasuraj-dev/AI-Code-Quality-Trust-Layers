"""Read project metadata without importing or executing analyzed code."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_DIST_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*")
_MIN_PYTHON = re.compile(r">=\s*3\.(\d+)")
_MAX_PYTHON = re.compile(r"<\s*3\.(\d+)")


def normalize_distribution_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def dependency_name(spec: str) -> str | None:
    stripped = spec.strip()
    match = _DIST_NAME.match(stripped)
    return normalize_distribution_name(match.group(0)) if match else None


@dataclass(frozen=True, slots=True)
class ProjectMetadata:
    name: str | None = None
    version: str | None = None
    requires_python: str | None = None
    dependencies: tuple[str, ...] = ()
    optional_dependencies: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    scripts: Mapping[str, str] = field(default_factory=dict)
    readme: str | None = None
    license_value: Any = None
    urls: Mapping[str, str] = field(default_factory=dict)
    raw: Mapping[str, Any] = field(default_factory=dict)
    parse_error: str | None = None

    @property
    def runtime_dependency_names(self) -> frozenset[str]:
        return frozenset(filter(None, (dependency_name(item) for item in self.dependencies)))

    @property
    def all_dependency_names(self) -> frozenset[str]:
        names = set(self.runtime_dependency_names)
        for values in self.optional_dependencies.values():
            names.update(filter(None, (dependency_name(item) for item in values)))
        return frozenset(names)

    @property
    def minimum_python_minor(self) -> int | None:
        if not self.requires_python:
            return None
        match = _MIN_PYTHON.search(self.requires_python)
        return int(match.group(1)) if match else None

    @property
    def maximum_python_minor_exclusive(self) -> int | None:
        if not self.requires_python:
            return None
        match = _MAX_PYTHON.search(self.requires_python)
        return int(match.group(1)) if match else None


def load_project_metadata(root: Path) -> ProjectMetadata:
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        return ProjectMetadata()
    try:
        raw = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        return ProjectMetadata(parse_error=str(exc))

    project = raw.get("project", {})
    if not isinstance(project, dict):
        return ProjectMetadata(raw=raw, parse_error="[project] is not a table")

    dependencies_raw = project.get("dependencies", [])
    dependencies = (
        tuple(item for item in dependencies_raw if isinstance(item, str))
        if isinstance(dependencies_raw, list)
        else ()
    )

    optional_raw = project.get("optional-dependencies", {})
    optional: dict[str, tuple[str, ...]] = {}
    if isinstance(optional_raw, dict):
        for group, values in optional_raw.items():
            if isinstance(values, list):
                optional[str(group)] = tuple(item for item in values if isinstance(item, str))

    scripts_raw = project.get("scripts", {})
    scripts = (
        {str(key): str(value) for key, value in scripts_raw.items() if isinstance(value, str)}
        if isinstance(scripts_raw, dict)
        else {}
    )
    urls_raw = project.get("urls", {})
    urls = (
        {str(key): str(value) for key, value in urls_raw.items() if isinstance(value, str)}
        if isinstance(urls_raw, dict)
        else {}
    )
    readme_raw = project.get("readme")
    if isinstance(readme_raw, str):
        readme = readme_raw
    elif isinstance(readme_raw, dict) and isinstance(readme_raw.get("file"), str):
        readme = str(readme_raw["file"])
    else:
        readme = None

    return ProjectMetadata(
        name=project.get("name") if isinstance(project.get("name"), str) else None,
        version=project.get("version") if isinstance(project.get("version"), str) else None,
        requires_python=(
            project.get("requires-python")
            if isinstance(project.get("requires-python"), str)
            else None
        ),
        dependencies=dependencies,
        optional_dependencies=optional,
        scripts=scripts,
        readme=readme,
        license_value=project.get("license"),
        urls=urls,
        raw=raw,
    )
