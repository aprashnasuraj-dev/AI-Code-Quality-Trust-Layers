"""Context-aware naming candidate rules."""

from __future__ import annotations

import ast
from collections import defaultdict

from repoverity.ast_utils import assignment_names, node_span, symbol_words
from repoverity.rules.base import AnalysisContext, finding


_GENERIC_LOCALS = {"data", "result", "res", "item", "obj", "value", "info", "temp", "tmp", "stuff"}
_GENERIC_PUBLIC = {
    "process",
    "process_data",
    "handle",
    "handle_data",
    "do_work",
    "run_task",
    "helper",
    "manager",
    "service",
    "utils",
}
_DOMAIN_STOP = _GENERIC_LOCALS | {
    "self",
    "cls",
    "get",
    "set",
    "run",
    "make",
    "create",
    "update",
    "list",
    "dict",
    "str",
    "int",
    "bool",
    "none",
}


def _domain_words(function: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    words = set(symbol_words(function.name))
    for arg in (*function.args.posonlyargs, *function.args.args, *function.args.kwonlyargs):
        words.update(symbol_words(arg.arg))
    for node in ast.walk(function):
        if isinstance(node, ast.Attribute):
            words.update(symbol_words(node.attr))
    return {word for word in words if len(word) >= 4 and word not in _DOMAIN_STOP}


def _usage_lines(function: ast.AST) -> dict[str, list[int]]:
    lines: dict[str, list[int]] = defaultdict(list)
    for node in ast.walk(function):
        if isinstance(node, ast.Name):
            lines[node.id].append(getattr(node, "lineno", 0))
    return lines


def analyze(context: AnalysisContext):  # type: ignore[no-untyped-def]
    findings = []
    for source in context.production_sources:
        if source.tree is None:
            continue

        for top_level in source.tree.body:
            if isinstance(top_level, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not top_level.name.startswith("_") and top_level.name.lower() in _GENERIC_PUBLIC:
                    line, col, end_line, end_col = node_span(top_level)
                    findings.append(
                        finding(
                            "NAM302",
                            source,
                            message=f"Public function '{top_level.name}' has a generic API name.",
                            evidence=(
                                "The name is in RepoVerity's intentionally narrow public-generic set and does not encode a domain operation."
                            ),
                            line=line,
                            column=col,
                            end_line=end_line,
                            end_column=end_col,
                            symbol=top_level.name,
                            anchor=top_level.name,
                        )
                    )
            elif isinstance(top_level, ast.ClassDef):
                if not top_level.name.startswith("_") and top_level.name.lower() in _GENERIC_PUBLIC:
                    line, col, end_line, end_col = node_span(top_level)
                    findings.append(
                        finding(
                            "NAM302",
                            source,
                            message=f"Public class '{top_level.name}' has a generic API name.",
                            evidence="The class name is in RepoVerity's intentionally narrow public-generic set.",
                            line=line,
                            column=col,
                            end_line=end_line,
                            end_column=end_col,
                            symbol=top_level.name,
                            anchor=top_level.name,
                        )
                    )

        for function in (
            node
            for node in ast.walk(source.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ):
            start = getattr(function, "lineno", 0)
            end = getattr(function, "end_lineno", start)
            if end - start + 1 < 12:
                continue
            domain = _domain_words(function)
            if len(domain) < 3:
                continue
            usage = _usage_lines(function)
            assigned = {name for name, _ in assignment_names(function)}
            for name in sorted(assigned.intersection(_GENERIC_LOCALS)):
                lines = [line for line in usage.get(name, []) if line]
                if len(lines) < 3 or max(lines) - min(lines) < 6:
                    continue
                findings.append(
                    finding(
                        "NAM301",
                        source,
                        message=(
                            f"Generic local '{name}' spans {max(lines) - min(lines) + 1} lines inside domain-heavy "
                            f"function '{function.name}'."
                        ),
                        evidence=(
                            f"'{name}' has {len(lines)} static references; surrounding domain terms include: "
                            f"{', '.join(sorted(domain)[:6])}."
                        ),
                        line=min(lines),
                        symbol=f"{function.name}:{name}",
                        anchor=f"{name}:{','.join(sorted(domain)[:4])}",
                        metadata={"domain_terms": sorted(domain)[:10], "reference_count": len(lines)},
                    )
                )
    return findings
