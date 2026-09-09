from __future__ import annotations

import argparse
import json
import platform
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate(root: Path, loc: int) -> None:
    (root / "README.md").write_text("# benchmark\n", encoding="utf-8")
    (root / "LICENSE").write_text("benchmark fixture\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        '[project]\nname="benchmark"\nversion="0"\nrequires-python=">=3.11"\nreadme="README.md"\nlicense="MIT"\ndependencies=[]\n',
        encoding="utf-8",
    )
    pkg = root / "src" / "bench"
    pkg.mkdir(parents=True)
    lines_per_file = 500
    for index, start in enumerate(range(0, loc, lines_per_file)):
        count = min(lines_per_file, loc - start)
        lines = [f"value_{start + i} = {start + i}" for i in range(count)]
        (pkg / f"module_{index:04d}.py").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _rss_mib(raw_value: int | float) -> float:
    # Linux reports ru_maxrss in KiB; macOS reports bytes.
    divisor = 1024**2 if sys.platform == "darwin" else 1024
    return round(raw_value / divisor, 1)


def _current_sha() -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def one(loc: int) -> dict[str, float | int]:
    with tempfile.TemporaryDirectory(prefix="repoverity-bench-") as raw:
        target = Path(raw)
        generate(target, loc)
        before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        started = time.perf_counter()
        completed = subprocess.run(
            [sys.executable, "-m", "repoverity", "audit", str(target), "--format", "json"],
            cwd=ROOT,
            env={"PYTHONPATH": str(ROOT / "src")},
            capture_output=True,
            text=True,
            check=True,
        )
        elapsed = time.perf_counter() - started
        payload = json.loads(completed.stdout)
        after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        return {
            "requested_loc": loc,
            "analyzed_loc": payload["timing"]["python_loc"],
            "seconds": round(elapsed, 4),
            "max_rss_mib": _rss_mib(max(before, after)),
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--loc", nargs="*", type=int, default=[1000, 10000, 50000])
    args = parser.parse_args()
    print(
        json.dumps(
            {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "repoverity_sha": _current_sha(),
                "memory_note": (
                    "ru_maxrss converted from bytes on macOS and KiB on other supported benchmark hosts"
                ),
                "results": [one(loc) for loc in args.loc],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
