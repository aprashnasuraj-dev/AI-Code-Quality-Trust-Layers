"""Baseline persistence and finding status classification."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from repoverity import __version__
from repoverity.models import BaselineStatus, Finding


BASELINE_SCHEMA_VERSION = "1.0"


class BaselineError(ValueError):
    """Raised for malformed baseline files."""


@dataclass(frozen=True, slots=True)
class Baseline:
    fingerprints: frozenset[str]


def create_baseline_payload(findings: tuple[Finding, ...]) -> dict[str, Any]:
    entries = [
        {
            "fingerprint": finding.fingerprint,
            "rule_id": finding.rule_id,
            "path": finding.location.path,
            "title": finding.title,
        }
        for finding in sorted(findings, key=lambda item: (item.fingerprint, item.rule_id))
    ]
    return {
        "schema_version": BASELINE_SCHEMA_VERSION,
        "tool": {"name": "repoverity", "version": __version__},
        "findings": entries,
    }


def write_baseline(path: Path, findings: tuple[Finding, ...]) -> None:
    payload = create_baseline_payload(findings)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_baseline(path: Path) -> Baseline:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BaselineError(f"could not read baseline {path}: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != BASELINE_SCHEMA_VERSION:
        raise BaselineError(f"unsupported baseline schema in {path}")
    entries = payload.get("findings")
    if not isinstance(entries, list):
        raise BaselineError("baseline findings must be an array")
    fingerprints: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("fingerprint"), str):
            raise BaselineError("baseline finding is missing a string fingerprint")
        fingerprint = entry["fingerprint"]
        if fingerprint in fingerprints:
            raise BaselineError(f"baseline contains duplicate fingerprint: {fingerprint}")
        fingerprints.add(fingerprint)
    return Baseline(frozenset(fingerprints))


def classify_findings(
    findings: tuple[Finding, ...], baseline: Baseline
) -> tuple[tuple[Finding, ...], tuple[str, ...]]:
    classified = tuple(
        finding.with_baseline_status(
            BaselineStatus.EXISTING if finding.fingerprint in baseline.fingerprints else BaselineStatus.NEW
        )
        for finding in findings
    )
    current = {finding.fingerprint for finding in findings}
    resolved = tuple(sorted(baseline.fingerprints - current))
    return classified, resolved
