"""Static test-boundary evidence mapping rules."""

from __future__ import annotations

import ast

from repoverity.ast_utils import dotted_name, node_span
from repoverity.rules.base import AnalysisContext, finding


_BOUNDARY_TERMS = ("parse", "load", "read", "decode", "validate", "config", "command", "cli", "input")
_PARSER_TERMS = ("parse", "decode", "load", "read", "validate", "from_")
_INVALID_TERMS = ("invalid", "malformed", "bad", "empty", "raises", "error", "reject", "missing")


def _is_public_boundary(name: str) -> bool:
    lowered = name.lower()
    return not name.startswith("_") and any(term in lowered for term in _BOUNDARY_TERMS)


def _is_parser_boundary(name: str) -> bool:
    lowered = name.lower()
    return not name.startswith("_") and any(term in lowered for term in _PARSER_TERMS)


def _raised_exception_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Raise) or child.exc is None:
            continue
        if isinstance(child.exc, ast.Call):
            name = dotted_name(child.exc.func)
        else:
            name = dotted_name(child.exc)
        if name:
            names.add(name.split(".")[-1])
    return names


def _has_branching(node: ast.AST) -> bool:
    return any(isinstance(child, (ast.If, ast.Match, ast.Try)) for child in ast.walk(node))


def analyze(context: AnalysisContext):  # type: ignore[no-untyped-def]
    findings = []
    test_text_lower = context.test_text.lower()

    for source in context.production_sources:
        if source.tree is None:
            continue
        for node in ast.walk(source.tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            if _is_public_boundary(node.name):
                exceptions = _raised_exception_names(node)
                if exceptions:
                    symbol_signal = node.name.lower() in test_text_lower
                    exception_signal = any(name.lower() in test_text_lower for name in exceptions)
                    raises_signal = "raises" in test_text_lower
                    if not (symbol_signal and (exception_signal or raises_signal)):
                        line, col, end_line, end_col = node_span(node)
                        findings.append(
                            finding(
                                "TST602",
                                source,
                                message=f"Boundary '{node.name}' raises explicit errors without direct test evidence.",
                                evidence=(
                                    f"Static exceptions: {', '.join(sorted(exceptions))}. Test corpus signal: "
                                    f"symbol={'yes' if symbol_signal else 'no'}, exception/raises="
                                    f"{'yes' if (exception_signal or raises_signal) else 'no'}."
                                ),
                                line=line,
                                column=col,
                                end_line=end_line,
                                end_column=end_col,
                                symbol=node.name,
                                anchor=",".join(sorted(exceptions)),
                                metadata={"exceptions": sorted(exceptions)},
                            )
                        )

            if _is_parser_boundary(node.name) and (_has_branching(node) or _raised_exception_names(node)):
                symbol_signal = node.name.lower() in test_text_lower
                malformed_signal = any(term in test_text_lower for term in _INVALID_TERMS)
                if not (symbol_signal and malformed_signal):
                    line, col, end_line, end_col = node_span(node)
                    findings.append(
                        finding(
                            "TST603",
                            source,
                            message=f"Parser/input boundary '{node.name}' lacks malformed-input fixture evidence.",
                            evidence=(
                                f"Boundary contains branching/error logic. Test corpus signal: symbol="
                                f"{'yes' if symbol_signal else 'no'}, malformed-input vocabulary="
                                f"{'yes' if malformed_signal else 'no'}."
                            ),
                            line=line,
                            column=col,
                            end_line=end_line,
                            end_column=end_col,
                            symbol=node.name,
                            anchor="malformed-input-signal",
                        )
                    )

    for script_name, target in sorted(context.metadata.scripts.items()):
        lower_script = script_name.lower()
        has_script = lower_script in test_text_lower or target.lower() in test_text_lower
        has_runner = any(
            marker in test_text_lower
            for marker in ("subprocess", "runner.invoke", "clirunner", "--help", "python -m")
        )
        if not (has_script and has_runner):
            findings.append(
                finding(
                    "TST604",
                    None,
                    message=f"Console script '{script_name}' has no direct integration smoke-test signal.",
                    evidence=(
                        f"Entry point is '{target}'. Test corpus signal: script/target="
                        f"{'yes' if has_script else 'no'}, runner/--help={'yes' if has_runner else 'no'}."
                    ),
                    line=1,
                    symbol=script_name,
                    anchor=target,
                )
            )

    return findings
