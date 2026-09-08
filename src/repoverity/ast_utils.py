"""Small AST helpers shared by multiple deterministic rules."""

from __future__ import annotations

import ast
from collections.abc import Iterable
import re


_WORD_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")
_NON_WORD = re.compile(r"[^A-Za-z0-9]+")


def symbol_words(name: str) -> tuple[str, ...]:
    expanded = _WORD_BOUNDARY.sub("_", name)
    return tuple(part.lower() for part in _NON_WORD.split(expanded) if part)


def public_name(name: str) -> bool:
    return not name.startswith("_")


def strip_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if body and isinstance(body[0], ast.Expr):
        value = body[0].value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return body[1:]
    return body


def node_span(node: ast.AST) -> tuple[int | None, int | None, int | None, int | None]:
    return (
        getattr(node, "lineno", None),
        getattr(node, "col_offset", None),
        getattr(node, "end_lineno", None),
        getattr(node, "end_col_offset", None),
    )


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        left = dotted_name(node.value)
        return f"{left}.{node.attr}" if left else node.attr
    return None


def loaded_names(node: ast.AST) -> set[str]:
    return {
        item.id
        for item in ast.walk(node)
        if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)
    }


def assignment_names(node: ast.AST) -> Iterable[tuple[str, int]]:
    for item in ast.walk(node):
        targets: list[ast.expr] = []
        if isinstance(item, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            if isinstance(item, ast.Assign):
                targets.extend(item.targets)
            else:
                targets.append(item.target)
        for target in targets:
            if isinstance(target, ast.Name):
                yield target.id, getattr(target, "lineno", getattr(item, "lineno", 0))
