"""Inline suppression parsing."""

from __future__ import annotations

import re
from typing import Mapping

from repoverity.discovery import SourceFile
from repoverity.models import Finding


_SUPPRESSION = re.compile(r"#\s*repoverity:\s*ignore\[([^\]]+)\](?:\s*-\s*(.*))?", re.IGNORECASE)


def is_suppressed(finding: Finding, source_by_path: Mapping[str, SourceFile]) -> bool:
    source = source_by_path.get(finding.location.path)
    line = finding.location.start_line
    if source is None or line is None:
        return False
    lines = source.text.splitlines()
    for candidate_line in (line, line - 1):
        if candidate_line < 1 or candidate_line > len(lines):
            continue
        match = _SUPPRESSION.search(lines[candidate_line - 1])
        if not match:
            continue
        rules = {item.strip().upper() for item in match.group(1).split(",")}
        if finding.rule_id in rules or "ALL" in rules:
            return True
    return False
