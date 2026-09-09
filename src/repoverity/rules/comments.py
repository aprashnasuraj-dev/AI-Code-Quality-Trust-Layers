"""Comment-rationale heuristics with narrow false-positive controls."""

from __future__ import annotations

import re

from repoverity.discovery import SourceFile
from repoverity.rules.base import AnalysisContext, finding

_RATIONALE_MARKERS = (
    "because",
    "due to",
    "invariant",
    "workaround",
    "security",
    "spec",
    "rfc",
    "issue",
    "ticket",
    "unit",
    "must",
    "why",
    "todo",
    "fixme",
    "repoverity:",
)


def _next_code_line(lines: list[str], index: int) -> tuple[int, str] | None:
    for next_index in range(index + 1, min(len(lines), index + 4)):
        text = lines[next_index].strip()
        if text and not text.startswith("#"):
            return next_index, text
    return None


def _narration_reason(comment: str, code: str) -> str | None:
    lowered = comment.lower().strip("# ")
    if any(marker in lowered for marker in _RATIONALE_MARKERS):
        return None

    patterns: tuple[tuple[str, str], ...] = (
        (r"^return\s+([a-zA-Z_]\w*)$", "return"),
        (r"^increment\s+([a-zA-Z_]\w*)$", "increment"),
        (r"^set\s+([a-zA-Z_]\w*)$", "set"),
        (r"^check\s+([a-zA-Z_]\w*)$", "check"),
        (r"^(?:loop|iterate)\s+(?:through|over)\s+([a-zA-Z_]\w*)$", "loop"),
        (r"^call\s+([a-zA-Z_]\w*)$", "call"),
    )
    for pattern, kind in patterns:
        match = re.match(pattern, lowered)
        if not match:
            continue
        name = match.group(1)
        if kind == "return" and code.startswith("return") and name in code:
            return f"comment says 'return {name}' immediately before a return using {name}"
        if kind == "increment" and re.search(rf"\b{re.escape(name)}\s*\+=", code):
            return f"comment narrates increment of {name}"
        if kind == "set" and re.match(rf"{re.escape(name)}\s*=", code):
            return f"comment narrates assignment to {name}"
        if kind == "check" and code.startswith("if ") and name in code:
            return f"comment narrates condition check for {name}"
        if kind == "loop" and code.startswith("for ") and f" in {name}" in code:
            return f"comment narrates loop over {name}"
        if kind == "call" and re.search(rf"\b{re.escape(name)}\s*\(", code):
            return f"comment narrates call to {name}"
    return None


def _candidates(source: SourceFile) -> list[tuple[int, str, str]]:
    lines = source.text.splitlines()
    candidates: list[tuple[int, str, str]] = []
    for index, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped.startswith("#"):
            continue
        next_line = _next_code_line(lines, index)
        if next_line is None:
            continue
        _, code = next_line
        reason = _narration_reason(stripped, code)
        if reason:
            candidates.append((index + 1, stripped, reason))
    return candidates


def analyze(context: AnalysisContext):  # type: ignore[no-untyped-def]
    findings = []
    for source in context.production_sources:
        candidates = _candidates(source)
        for line, comment, reason in candidates:
            findings.append(
                finding(
                    "COM401",
                    source,
                    message="Comment appears to narrate the immediately following syntax.",
                    evidence=f"{reason}; comment text: {comment}",
                    line=line,
                    symbol=f"comment@{line}",
                    anchor=comment,
                )
            )

        for index in range(len(candidates)):
            window = [
                candidate
                for candidate in candidates[index:]
                if candidate[0] - candidates[index][0] <= 12
            ]
            if len(window) >= 3:
                start = window[0][0]
                end = window[-1][0]
                findings.append(
                    finding(
                        "COM402",
                        source,
                        message=f"Found {len(window)} narration-comment candidates within {end - start + 1} lines.",
                        evidence=f"Candidate comment lines: {', '.join(str(line) for line, _, _ in window)}.",
                        line=start,
                        end_line=end,
                        symbol=f"comment-cluster@{start}",
                        anchor=":".join(str(line) for line, _, _ in window),
                    )
                )
                break
    return findings
