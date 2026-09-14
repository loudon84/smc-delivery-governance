#!/usr/bin/env python3
"""Run Context Optimization Engine unit tests."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    env = {**os.environ, "PYTHONPATH": str(HERE) + os.pathsep + env_path(os.environ.get("PYTHONPATH"))}
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", str(HERE / "tests"), "-p", "test_*.py", "-v"]
    return subprocess.call(cmd, cwd=str(HERE), env=env)


def env_path(value: str | None) -> str:
    return value or ""


if __name__ == "__main__":
    raise SystemExit(main())
