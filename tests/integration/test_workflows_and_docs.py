from __future__ import annotations

from pathlib import Path

import yaml

from repoverity.rules.registry import all_rules

ROOT = Path(__file__).resolve().parents[2]


def test_all_yaml_parses() -> None:
    files = sorted([*ROOT.rglob("*.yml"), *ROOT.rglob("*.yaml")])
    assert files
    for path in files:
        yaml.safe_load(path.read_text(encoding="utf-8"))


def test_ci_runs_missing_local_toolchain() -> None:
    text = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    for command in (
        "ruff check .",
        "ruff format --check .",
        "mypy src/repoverity",
        "python -m build",
        "twine check dist/*",
    ):
        assert command in text


def test_ci_exercises_python_range_edges() -> None:
    text = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "3.11" in text and "3.14" in text


def test_action_smoke_uses_local_composite_action() -> None:
    assert "uses: ./" in (ROOT / ".github/workflows/action-smoke.yml").read_text(encoding="utf-8")


def test_release_requires_tag_and_trusted_publishing() -> None:
    text = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "tags: ['v*']" in text
    assert "id-token: write" in text
    assert "gh-action-pypi-publish@" in text
    assert "PYPI_API_TOKEN" not in text


def test_action_uses_argument_array_and_action_path() -> None:
    text = (ROOT / "action.yml").read_text(encoding="utf-8")
    assert 'args=(audit "$INPUT_AUDIT_PATH"' in text
    assert '"${args[@]}"' in text
    assert "GITHUB_ACTION_PATH/src" in text


def test_rules_docs_cover_registry() -> None:
    text = (ROOT / "docs/RULES.md").read_text(encoding="utf-8")
    for rule in all_rules():
        assert rule.rule_id in text


def test_readme_has_no_unreleased_action_tag() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "AI-Code-Quality-Trust-Layers@v1" not in text
    assert "AI-Code-Quality-Trust-Layers@main" in text
