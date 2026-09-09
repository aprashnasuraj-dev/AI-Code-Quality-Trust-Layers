"""Read-only Git helpers for changed-only analysis and receipts."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )


def current_commit(root: Path) -> str | None:
    result = _run_git(root, ["rev-parse", "--verify", "HEAD"])
    return result.stdout.strip() if result.returncode == 0 else None


def changed_paths(root: Path, base_ref: str) -> tuple[frozenset[str] | None, str | None]:
    """Return paths changed from a base commit, including local worktree additions.

    The committed branch delta uses three-dot semantics. Staged/unstaged changes and
    untracked files are unioned so local pre-commit audits do not silently miss work.
    """
    if not base_ref or base_ref.startswith("-"):
        return None, f"invalid Git base ref: {base_ref!r}"
    inside = _run_git(root, ["rev-parse", "--is-inside-work-tree"])
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return None, "--changed-only requested outside a Git work tree; running full audit instead"
    verify = _run_git(root, ["rev-parse", "--verify", "--end-of-options", f"{base_ref}^{{commit}}"])
    if verify.returncode != 0:
        return None, f"Git base ref {base_ref!r} could not be resolved; running full audit instead"

    commands = (
        ["diff", "--name-only", "--diff-filter=ACMRT", f"{base_ref}...HEAD", "--"],
        ["diff", "--name-only", "--diff-filter=ACMRT", "HEAD", "--"],
        ["ls-files", "--others", "--exclude-standard"],
    )
    paths: set[str] = set()
    for command in commands:
        result = _run_git(root, list(command))
        if result.returncode != 0:
            return None, "Git diff failed; running full audit instead"
        paths.update(
            line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()
        )
    return frozenset(paths), None
