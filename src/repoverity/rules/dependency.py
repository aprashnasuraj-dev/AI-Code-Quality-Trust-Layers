"""Dependency and runtime-reality rules."""

from __future__ import annotations

import ast
import importlib.metadata
import sys
from collections.abc import Iterable
from functools import lru_cache

from repoverity.ast_utils import node_span
from repoverity.project import normalize_distribution_name
from repoverity.rules.base import AnalysisContext, finding

_KNOWN_IMPORT_TO_DIST: dict[str, tuple[str, ...]] = {
    "PIL": ("pillow",),
    "bs4": ("beautifulsoup4",),
    "cv2": ("opencv-python", "opencv-python-headless"),
    "Crypto": ("pycryptodome",),
    "dateutil": ("python-dateutil",),
    "google": ("google",),
    "jwt": ("pyjwt",),
    "sklearn": ("scikit-learn",),
    "yaml": ("pyyaml",),
}


@lru_cache(maxsize=1)
def _installed_mapping() -> dict[str, tuple[str, ...]]:
    try:
        mapping = importlib.metadata.packages_distributions()
    except Exception:  # metadata providers are outside the analyzed source tree
        return {}
    result: dict[str, tuple[str, ...]] = {}
    for import_name, distributions in mapping.items():
        result[import_name] = tuple(normalize_distribution_name(name) for name in distributions)
    return result


def _candidate_distributions(
    import_name: str, installed: dict[str, tuple[str, ...]]
) -> tuple[str, ...]:
    if import_name in _KNOWN_IMPORT_TO_DIST:
        return _KNOWN_IMPORT_TO_DIST[import_name]
    if import_name in installed and installed[import_name]:
        return installed[import_name]
    return (normalize_distribution_name(import_name),)


def _iter_imports(context: AnalysisContext) -> Iterable[tuple[object, ast.AST, str]]:
    """Yield imports that can be identified without executing project code.

    Literal-string dynamic imports are included because they are deterministic evidence
    for declared-dependency use. Non-literal imports remain deliberately unresolved.
    """
    for source in context.production_sources:
        if source.tree is None:
            continue
        for node in ast.walk(source.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    yield source, node, alias.name.split(".")[0]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                yield source, node, node.module.split(".")[0]
            elif isinstance(node, ast.Call) and node.args:
                target = node.func
                is_import_module = (
                    isinstance(target, ast.Attribute)
                    and target.attr == "import_module"
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "importlib"
                )
                is_dunder_import = isinstance(target, ast.Name) and target.id == "__import__"
                if not (is_import_module or is_dunder_import):
                    continue
                first_arg = node.args[0]
                if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                    module_name = first_arg.value.lstrip(".").split(".")[0]
                    if module_name:
                        yield source, node, module_name


def analyze(context: AnalysisContext):  # type: ignore[no-untyped-def]
    findings = []
    installed = _installed_mapping()
    declared = context.metadata.all_dependency_names
    stdlib = getattr(sys, "stdlib_module_names", frozenset())
    imported_distributions: set[str] = set()
    seen_dep101: set[tuple[str, str]] = set()

    for source_obj, node, top_name in _iter_imports(context):
        source = source_obj
        if top_name in stdlib or top_name in context.local_modules:
            continue
        candidates = tuple(
            normalize_distribution_name(name)
            for name in _candidate_distributions(top_name, installed)
        )
        imported_distributions.update(candidates)
        if declared.intersection(candidates):
            continue
        key = (source.relpath, top_name)
        if key in seen_dep101:
            continue
        seen_dep101.add(key)
        line, col, end_line, end_col = node_span(node)
        findings.append(
            finding(
                "DEP101",
                source,
                message=f"Import '{top_name}' has no matching declared dependency.",
                evidence=(
                    f"Static import '{top_name}' maps to candidate distribution(s): "
                    f"{', '.join(candidates)}; none appear in project dependencies or optional groups."
                ),
                line=line,
                column=col,
                end_line=end_line,
                end_column=end_col,
                symbol=top_name,
                anchor=top_name,
                metadata={"candidate_distributions": list(candidates)},
            )
        )

    for dependency in sorted(context.metadata.runtime_dependency_names):
        if dependency in imported_distributions:
            continue
        findings.append(
            finding(
                "DEP102",
                None,
                message=f"Runtime dependency '{dependency}' has no static production import evidence.",
                evidence=(
                    f"'{dependency}' is declared in project.dependencies but no analyzed production import "
                    "maps to that distribution."
                ),
                line=1,
                symbol=dependency,
                anchor=dependency,
            )
        )

    minimum_minor = context.metadata.minimum_python_minor
    runtime_minor = sys.version_info.minor
    if minimum_minor is not None and 7 <= minimum_minor < runtime_minor:
        for source in context.production_sources:
            if source.tree is None:
                continue
            try:
                ast.parse(source.text, filename=source.relpath, feature_version=(3, minimum_minor))
            except SyntaxError as exc:
                findings.append(
                    finding(
                        "DEP103",
                        source,
                        message=(
                            f"Source is incompatible with declared minimum Python 3.{minimum_minor} syntax."
                        ),
                        evidence=(
                            f"CPython feature-version parser for 3.{minimum_minor} rejected the file: "
                            f"{exc.msg}."
                        ),
                        line=exc.lineno,
                        column=(exc.offset - 1) if exc.offset else None,
                        symbol=source.relpath,
                        anchor=exc.msg,
                    )
                )
            except (ValueError, MemoryError, RecursionError):
                continue

    return findings
