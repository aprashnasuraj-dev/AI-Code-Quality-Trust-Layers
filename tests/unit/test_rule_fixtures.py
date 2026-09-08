from __future__ import annotations

from pathlib import Path

import pytest

from repoverity.rules.registry import all_rules
from tests.conftest import audit_fixture, load_rule_cases, materialize_rule_case


RULE_IDS = tuple(rule.rule_id for rule in all_rules())


@pytest.mark.parametrize("rule_id", RULE_IDS)
def test_positive_fixture_detects_rule(rule_id: str, tmp_path: Path) -> None:
    project = materialize_rule_case(tmp_path, rule_id, "bad")
    result = audit_fixture(project, rules=frozenset({rule_id}))
    assert rule_id in {finding.rule_id for finding in result.findings}


@pytest.mark.parametrize("rule_id", RULE_IDS)
def test_good_fixture_is_clean_for_rule(rule_id: str, tmp_path: Path) -> None:
    project = materialize_rule_case(tmp_path, rule_id, "good")
    result = audit_fixture(project, rules=frozenset({rule_id}))
    assert rule_id not in {finding.rule_id for finding in result.findings}


@pytest.mark.parametrize("rule_id", RULE_IDS)
def test_edge_fixture_is_clean_for_rule(rule_id: str, tmp_path: Path) -> None:
    project = materialize_rule_case(tmp_path, rule_id, "edge")
    result = audit_fixture(project, rules=frozenset({rule_id}))
    assert rule_id not in {finding.rule_id for finding in result.findings}


def test_fixture_matrix_matches_registry() -> None:
    corpus = load_rule_cases()
    assert set(corpus) == set(RULE_IDS)
    for rule_id in RULE_IDS:
        assert set(corpus[rule_id]) == {"bad", "good", "edge"}
        assert all(corpus[rule_id][variant] for variant in ("bad", "good", "edge"))
