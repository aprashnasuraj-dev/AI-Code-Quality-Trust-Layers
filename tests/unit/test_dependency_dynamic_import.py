from __future__ import annotations

from pathlib import Path

from tests.conftest import audit_fixture, materialize_rule_case


def test_literal_importlib_dynamic_import_counts_as_dependency_use(tmp_path: Path) -> None:
    project = materialize_rule_case(tmp_path, "DEP102", "edge")
    result = audit_fixture(project, rules=frozenset({"DEP102"}))
    assert not result.findings


def test_nonliteral_dynamic_import_does_not_fabricate_usage(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# x\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("x\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text('[project]\nname="x"\nversion="0"\nrequires-python=">=3.11,<3.15"\nreadme="README.md"\nlicense="MIT"\ndependencies=["requests"]\n', encoding="utf-8")
    (tmp_path / "main.py").write_text('import importlib\nname="requests"\nmodule=importlib.import_module(name)\n', encoding="utf-8")
    result = audit_fixture(tmp_path, rules=frozenset({"DEP102"}))
    assert [f.rule_id for f in result.findings] == ["DEP102"]
