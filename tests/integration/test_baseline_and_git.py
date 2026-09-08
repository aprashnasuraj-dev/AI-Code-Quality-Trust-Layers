from __future__ import annotations

import json
from pathlib import Path
import subprocess

from repoverity.config import load_config
from repoverity.engine import AuditOptions, audit_repository
from repoverity.baseline import write_baseline
from repoverity.gitdiff import changed_paths


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)


def init_repo(root: Path) -> None:
    git(root, "init", "-b", "main")
    git(root, "config", "user.name", "RepoVerity Test")
    git(root, "config", "user.email", "test@example.invalid")
    (root / "README.md").write_text("# fixture\n")
    (root / "LICENSE").write_text("fixture\n")
    (root / "pyproject.toml").write_text('[project]\nname="fixture"\nversion="0"\nrequires-python=">=3.11"\nreadme="README.md"\nlicense="MIT"\ndependencies=[]\n')
    (root / "base.py").write_text("VALUE=1\n")
    git(root, "add", ".")
    assert git(root, "commit", "-m", "base").returncode == 0


def test_baseline_new_existing_resolved(tmp_path: Path) -> None:
    init_repo(tmp_path)
    target = tmp_path / "bad.py"
    target.write_text("import requests\n")
    first = audit_repository(tmp_path, load_config(tmp_path), AuditOptions(selected_rules=frozenset({"DEP101"})))
    baseline = tmp_path / ".trust-baseline.json"
    write_baseline(baseline, first.findings)
    same = audit_repository(tmp_path, load_config(tmp_path), AuditOptions(selected_rules=frozenset({"DEP101"}), baseline_path=baseline))
    assert len(same.existing_findings) == 1 and not same.new_findings
    target.write_text("VALUE=2\n")
    resolved = audit_repository(tmp_path, load_config(tmp_path), AuditOptions(selected_rules=frozenset({"DEP101"}), baseline_path=baseline))
    assert len(resolved.resolved_fingerprints) == 1
    target.write_text("import yaml\n")
    new = audit_repository(tmp_path, load_config(tmp_path), AuditOptions(selected_rules=frozenset({"DEP101"}), baseline_path=baseline))
    assert len(new.new_findings) == 1 and len(new.resolved_fingerprints) == 1


def test_changed_only_staged_unstaged_untracked_and_no_duplicates(tmp_path: Path) -> None:
    init_repo(tmp_path)
    (tmp_path / "base.py").write_text("VALUE=2\n")
    git(tmp_path, "add", "base.py")
    (tmp_path / "base.py").write_text("VALUE=3\n")
    (tmp_path / "new file.py").write_text("VALUE=4\n")
    paths, warning = changed_paths(tmp_path, "HEAD")
    assert warning is None
    assert paths == frozenset({"base.py", "new file.py"})


def test_changed_only_committed_branch_delta(tmp_path: Path) -> None:
    init_repo(tmp_path)
    base = git(tmp_path, "rev-parse", "HEAD").stdout.strip()
    (tmp_path / "feature.py").write_text("VALUE=2\n")
    git(tmp_path, "add", "feature.py"); git(tmp_path, "commit", "-m", "feature")
    paths, warning = changed_paths(tmp_path, base)
    assert warning is None and "feature.py" in paths


def test_changed_only_missing_base_warns_and_falls_back(tmp_path: Path) -> None:
    init_repo(tmp_path)
    paths, warning = changed_paths(tmp_path, "missing-ref")
    assert paths is None and "could not be resolved" in (warning or "")


def test_changed_only_non_git_warns(tmp_path: Path) -> None:
    paths, warning = changed_paths(tmp_path, "HEAD")
    assert paths is None and "outside a Git work tree" in (warning or "")


def test_changed_only_detached_head(tmp_path: Path) -> None:
    init_repo(tmp_path)
    base = git(tmp_path, "rev-parse", "HEAD").stdout.strip()
    git(tmp_path, "checkout", "--detach", "HEAD")
    (tmp_path / "detached.py").write_text("VALUE=1\n")
    paths, warning = changed_paths(tmp_path, base)
    assert warning is None and "detached.py" in paths
