from __future__ import annotations

import json
from pathlib import Path

import pytest

from repoverity.baseline import BaselineError, load_baseline
from repoverity.config import DEFAULT_EXCLUDE_PATTERNS, ConfigError, load_config
from repoverity.discovery import discover_sources
from repoverity.fingerprints import make_fingerprint


def test_default_excludes_include_virtualenv_and_build() -> None:
    assert ".venv/**" in DEFAULT_EXCLUDE_PATTERNS
    assert "dist/**" in DEFAULT_EXCLUDE_PATTERNS


def test_hidden_default_directory_is_not_crawled(tmp_path: Path) -> None:
    (tmp_path / ".venv" / "lib").mkdir(parents=True)
    (tmp_path / ".venv" / "lib" / "noise.py").write_text("import requests\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("VALUE=1\n", encoding="utf-8")
    sources, issues, _ = discover_sources(tmp_path, DEFAULT_EXCLUDE_PATTERNS)
    assert [s.relpath for s in sources] == ["main.py"]
    assert not issues


def test_symlink_is_skipped(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.py"
    outside.write_text("VALUE=1\n", encoding="utf-8")
    link = tmp_path / "link.py"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink unavailable")
    sources, issues, _ = discover_sources(tmp_path, DEFAULT_EXCLUDE_PATTERNS)
    assert not sources
    assert any(issue.kind == "symlink-skipped" for issue in issues)


def test_malformed_config_raises_config_error(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.repoverity\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(tmp_path)


def test_invalid_config_type_rejected(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[tool.repoverity]\nexclude = "bad"\n', encoding="utf-8"
    )
    with pytest.raises(ConfigError):
        load_config(tmp_path)


def test_malformed_baseline_rejected(tmp_path: Path) -> None:
    path = tmp_path / "baseline.json"
    path.write_text("not-json", encoding="utf-8")
    with pytest.raises(BaselineError):
        load_baseline(path)


def test_future_baseline_schema_rejected(tmp_path: Path) -> None:
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps({"schema_version": "99", "findings": []}), encoding="utf-8")
    with pytest.raises(BaselineError):
        load_baseline(path)


def test_duplicate_baseline_fingerprint_rejected(tmp_path: Path) -> None:
    path = tmp_path / "baseline.json"
    path.write_text(
        json.dumps(
            {"schema_version": "1.0", "findings": [{"fingerprint": "x"}, {"fingerprint": "x"}]}
        ),
        encoding="utf-8",
    )
    with pytest.raises(BaselineError):
        load_baseline(path)


def test_fingerprint_is_line_independent() -> None:
    first = make_fingerprint("NAM302", "src/a.py", symbol="process", anchor="process")
    second = make_fingerprint("NAM302", "src/a.py", symbol="process", anchor="process")
    assert first == second


def test_load_project_metadata_handles_malformed_pyproject(tmp_path: Path) -> None:
    from repoverity.project import load_project_metadata

    (tmp_path / "pyproject.toml").write_text("[project\n", encoding="utf-8")
    metadata = load_project_metadata(tmp_path)
    assert metadata.parse_error is not None
