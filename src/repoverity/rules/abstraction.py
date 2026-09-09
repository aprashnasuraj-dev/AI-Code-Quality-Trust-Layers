"""Structural abstraction candidate rules."""

from __future__ import annotations

import ast
from collections import Counter

from repoverity.ast_utils import node_span, strip_docstring
from repoverity.rules.base import AnalysisContext, finding


def _delegate_target(method: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    body = strip_docstring(method.body)
    if len(body) != 1:
        return None
    statement = body[0]
    expression: ast.expr | None = None
    if isinstance(statement, ast.Return):
        expression = statement.value
    elif isinstance(statement, ast.Expr):
        expression = statement.value
    if isinstance(expression, ast.Await):
        expression = expression.value
    if not isinstance(expression, ast.Call) or not isinstance(expression.func, ast.Attribute):
        return None
    owner = expression.func.value
    if not isinstance(owner, ast.Attribute) or not isinstance(owner.value, ast.Name):
        return None
    if owner.value.id != "self":
        return None
    return owner.attr


def _public_methods(node: ast.ClassDef) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        child
        for child in node.body
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not child.name.startswith("_")
    ]


def _has_abstract_marker(node: ast.ClassDef) -> bool:
    base_names = {
        base.id
        if isinstance(base, ast.Name)
        else base.attr
        if isinstance(base, ast.Attribute)
        else ""
        for base in node.bases
    }
    return bool(base_names.intersection({"ABC", "Protocol"}))


def _self_state_count(node: ast.ClassDef) -> int:
    count = 0
    for child in node.body:
        if (
            not isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            or child.name != "__init__"
        ):
            continue
        for item in ast.walk(child):
            if isinstance(item, (ast.Assign, ast.AnnAssign)):
                targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                for target in targets:
                    if (
                        isinstance(target, ast.Attribute)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "self"
                    ):
                        count += 1
    return count


def _nested_rethrow_nodes(outer: ast.Try) -> list[ast.Try]:
    nested: list[ast.Try] = []
    for statement in outer.body:
        for node in ast.walk(statement):
            if not isinstance(node, ast.Try):
                continue
            for handler in node.handlers:
                body = strip_docstring(handler.body)
                if len(body) == 1 and isinstance(body[0], ast.Raise) and body[0].exc is None:
                    nested.append(node)
                    break
    return nested


def analyze(context: AnalysisContext):  # type: ignore[no-untyped-def]
    findings = []
    for source in context.production_sources:
        if source.tree is None:
            continue
        for node in ast.walk(source.tree):
            if isinstance(node, ast.ClassDef):
                methods = _public_methods(node)
                if len(methods) >= 2 and not _has_abstract_marker(node):
                    targets = [target for method in methods if (target := _delegate_target(method))]
                    if targets:
                        dominant, count = Counter(targets).most_common(1)[0]
                        ratio = count / len(methods)
                        if ratio >= 0.8:
                            line, col, end_line, end_col = node_span(node)
                            findings.append(
                                finding(
                                    "ABS201",
                                    source,
                                    message=(
                                        f"Class '{node.name}' delegates {count}/{len(methods)} public methods "
                                        f"({ratio:.0%}) directly to self.{dominant}."
                                    ),
                                    evidence=(
                                        f"Dominant collaborator: self.{dominant}; public methods: {len(methods)}; "
                                        f"direct delegates: {count}; no behavior was inferred for those delegated bodies."
                                    ),
                                    line=line,
                                    column=col,
                                    end_line=end_line,
                                    end_column=end_col,
                                    symbol=node.name,
                                    anchor=f"{dominant}:{count}/{len(methods)}",
                                    metadata={"delegate_ratio": ratio, "collaborator": dominant},
                                )
                            )

                if (
                    len(methods) == 1
                    and not node.bases
                    and not node.decorator_list
                    and _self_state_count(node) == 0
                ):
                    method = methods[0]
                    line, col, end_line, end_col = node_span(node)
                    findings.append(
                        finding(
                            "ABS202",
                            source,
                            message=(
                                f"Class '{node.name}' exposes one public method '{method.name}' with no visible instance state."
                            ),
                            evidence="No explicit base class, class decorator, or self-state assignment was found.",
                            line=line,
                            column=col,
                            end_line=end_line,
                            end_column=end_col,
                            symbol=node.name,
                            anchor=method.name,
                        )
                    )

            if isinstance(node, ast.Try):
                for nested in _nested_rethrow_nodes(node):
                    line, col, end_line, end_col = node_span(nested)
                    findings.append(
                        finding(
                            "ABS203",
                            source,
                            message="Nested try/except immediately re-raises without translation or recovery.",
                            evidence=(
                                "Inner exception handler contains only a bare 'raise' while already enclosed by an outer try."
                            ),
                            line=line,
                            column=col,
                            end_line=end_line,
                            end_column=end_col,
                            symbol=f"try@{line}",
                            anchor="bare-reraise-nested-try",
                        )
                    )
    return findings
