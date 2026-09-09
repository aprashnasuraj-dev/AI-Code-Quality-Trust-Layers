from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from repoverity.config import load_config
from repoverity.engine import AuditOptions, audit_repository

FIXTURE_CORPUS_FILES = (
    Path(__file__).parent / "fixtures" / "rule_cases_a.json",
    Path(__file__).parent / "fixtures" / "rule_cases_b.json",
)


def load_rule_cases() -> dict[str, dict[str, dict[str, str]]]:
    cases: dict[str, dict[str, dict[str, str]]] = {}
    for corpus in FIXTURE_CORPUS_FILES:
        cases.update(json.loads(corpus.read_text(encoding="utf-8")))
    return cases


def materialize_rule_case(tmp_path: Path, rule_id: str, variant: str) -> Path:
    project = tmp_path / f"{rule_id.lower()}-{variant}"
    files = load_rule_cases()[rule_id][variant]
    for relative, content in files.items():
        path = project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return project


def audit_fixture(path: Path, *, rules: frozenset[str] | None = None):
    return audit_repository(path, load_config(path), AuditOptions(selected_rules=rules))


@pytest.fixture
def copy_project(tmp_path: Path):
    def _copy(source: Path) -> Path:
        target = tmp_path / source.name
        shutil.copytree(source, target)
        return target

    return _copy
