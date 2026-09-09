from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "examples" / "intentionally_bad"
OUT = ROOT / "examples" / "generated_reports"


def run(*args: str) -> str:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    completed = subprocess.run(
        [sys.executable, "-m", "repoverity", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "demo-terminal.txt").write_text(
        run("audit", str(TARGET), "--no-color", "--verbose"), encoding="utf-8"
    )
    (OUT / "demo.json").write_text(run("audit", str(TARGET), "--format", "json"), encoding="utf-8")
    (OUT / "demo.md").write_text(
        run("audit", str(TARGET), "--format", "markdown"), encoding="utf-8"
    )
    (OUT / "demo.sarif").write_text(
        run("audit", str(TARGET), "--format", "sarif"), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
