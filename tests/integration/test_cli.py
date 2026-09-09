from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOOD = ROOT / "examples" / "intentionally_good"
BAD = ROOT / "examples" / "intentionally_bad"


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "repoverity", *args],
        cwd=cwd or ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_repoverity_help_smoke() -> None:
    result = run_cli("--help")
    assert result.returncode == 0
    assert "audit" in result.stdout


def test_version() -> None:
    result = run_cli("version")
    assert result.returncode == 0 and "RepoVerity 0.1.0" in result.stdout


def test_rules_list_and_show() -> None:
    assert run_cli("rules", "list").returncode == 0
    shown = run_cli("rules", "show", "ABS201")
    assert shown.returncode == 0 and "Legitimate counterexample" in shown.stdout


def test_unknown_rule_is_usage_error() -> None:
    result = run_cli("explain", "NOPE999")
    assert result.returncode == 2


def test_json_output_is_parseable() -> None:
    result = run_cli("audit", str(GOOD), "--format", "json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["schema_version"] == "1.0"


def test_sarif_output_is_parseable(tmp_path: Path) -> None:
    out = tmp_path / "trust.sarif"
    result = run_cli("audit", str(GOOD), "--format", "sarif", "--output", str(out))
    assert result.returncode == 0
    assert json.loads(out.read_text(encoding="utf-8"))["version"] == "2.1.0"


def test_markdown_output() -> None:
    result = run_cli("audit", str(GOOD), "--format", "markdown")
    assert result.returncode == 0 and "Code Trust Receipt" in result.stdout


def test_high_gate_fails_on_new_high() -> None:
    result = run_cli("audit", str(BAD), "--rules", "DEP101", "--fail-on", "high")
    assert result.returncode == 1


def test_fix_preview_does_not_mutate(copy_project) -> None:
    project = copy_project(BAD)
    before = (project / "src/inventory/audit.py").read_bytes()
    result = run_cli("fix-preview", str(project), "--rules", "DEP101")
    assert result.returncode == 0
    assert (project / "src/inventory/audit.py").read_bytes() == before


def test_missing_path_is_usage_error() -> None:
    result = run_cli("audit", "does-not-exist")
    assert result.returncode == 2
