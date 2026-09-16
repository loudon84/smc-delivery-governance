from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    return subprocess.call(
        [sys.executable, "-m", "pytest", "-q", str(root / "tests" / "ges6")],
        cwd=root,
    )


if __name__ == "__main__":
    raise SystemExit(main())
