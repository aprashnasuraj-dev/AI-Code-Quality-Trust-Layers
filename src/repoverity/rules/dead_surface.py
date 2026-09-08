"""Dead and speculative surface rules."""

from __future__ import annotations

import ast

from repoverity.ast_utils import dotted_name, loaded_names, node_span, strip_docstring
from repoverity.rules.base import AnalysisContext, finding


_CALLBACK_NAMES = {"event", "request", "context", "sender", "signal"}


def _decorator_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    return {name for deco in node.decorator_list if (name := dotted_name(deco))}


def _class_base_names(node: ast.ClassDef) -> set[str]:
    return {name for base in node.bases if (name := dotted_name(base))}


def _is_abstract_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(name.endswith("abstractmethod") for name in _decorator_names(node))


def _placeholder_body(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    body = strip_docstring(node.body)
    if len(body) != 1:
        return None
    statement = body[0]
    if isinstance(statement, ast.Pass):
        return "function body contains only pass"
    if isinstance(statement, ast.Raise):
        name = dotted_name(statement.exc.func) if isinstance(statement.exc, ast.Call) else dotted_name(statement.exc) if statement.exc else None
        if name and name.endswith("NotImplementedError"):
            return "function raises NotImplementedError"
    return None


def analyze(context: AnalysisContext):  # type: ignore[no-untyped-def]
    findings = []

    all_references: set[str] = set()
    for source in context.sources:
        if source.tree is None:
            continue
        for node in ast.walk(source.tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                all_references.add(node.id)
            elif isinstance(node, ast.Attribute):
                all_references.add(node.attr)

    for source in context.production_sources:
        if source.tree is None:
            continue

        for top_level in source.tree.body:
            if (
                isinstance(top_level, (ast.FunctionDef, ast.AsyncFunctionDef))
                and top_level.name.startswith("_")
                and not top_level.name.startswith("__")
                and not top_level.decorator_list
                and top_level.name not in all_references
            ):
                line, col, end_line, end_col = node_span(top_level)
                findings.append(
                    finding(
                        "DEAD502",
                        source,
                        message=f"Private helper '{top_level.name}' has no static reference in analyzed Python source.",
                        evidence="No Name-load or Attribute reference to this private top-level symbol was found.",
                        line=line,
                        column=col,
                        end_line=end_line,
                        end_column=end_col,
                        symbol=top_level.name,
                        anchor=top_level.name,
                    )
                )

        class_stack: list[ast.ClassDef] = []

        class Visitor(ast.NodeVisitor):
            def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
                class_stack.append(node)
                self.generic_visit(node)
                class_stack.pop()

            def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
                decorators = _decorator_names(node)
                in_based_class = bool(class_stack and _class_base_names(class_stack[-1]))
                if not decorators and not in_based_class and not node.name.startswith("on_"):
                    used = loaded_names(node)
                    args = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
                    for arg in args:
                        name = arg.arg
                        if (
                            name in {"self", "cls"}
                            or name.startswith("_")
                            or name in _CALLBACK_NAMES
                            or name in used
                        ):
                            continue
                        findings.append(
                            finding(
                                "DEAD501",
                                source,
                                message=f"Parameter '{name}' in '{node.name}' has no static load reference.",
                                evidence=(
                                    "The parameter is present in the signature but no Name-load for it occurs in the function body."
                                ),
                                line=getattr(arg, "lineno", getattr(node, "lineno", None)),
                                column=getattr(arg, "col_offset", None),
                                symbol=f"{node.name}:{name}",
                                anchor=f"{node.name}:{name}",
                            )
                        )

                abstract_context = _is_abstract_function(node) or bool(
                    class_stack and _class_base_names(class_stack[-1]).intersection({"ABC", "Protocol"})
                )
                placeholder = _placeholder_body(node)
                if placeholder and not abstract_context:
                    line, col, end_line, end_col = node_span(node)
                    findings.append(
                        finding(
                            "DEAD504",
                            source,
                            message=f"Production function '{node.name}' is a placeholder: {placeholder}.",
                            evidence="The function is not visibly abstract and is outside the test tree.",
                            line=line,
                            column=col,
                            end_line=end_line,
                            end_column=end_col,
                            symbol=node.name,
                            anchor=placeholder,
                        )
                    )

                for child in node.body:
                    if isinstance(child, ast.If) and child.body and all(isinstance(item, ast.Pass) for item in child.body):
                        line, col, end_line, end_col = node_span(child)
                        findings.append(
                            finding(
                                "DEAD504",
                                source,
                                message=f"Function '{node.name}' contains a pass-only conditional branch.",
                                evidence="The conditional branch body contains only pass and no visible effect.",
                                line=line,
                                column=col,
                                end_line=end_line,
                                end_column=end_col,
                                symbol=f"{node.name}:if",
                                anchor="pass-only-if",
                            )
                        )

                self.generic_visit(node)

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
                self._visit_function(node)

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
                self._visit_function(node)

        Visitor().visit(source.tree)

    return findings
