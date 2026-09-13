#!/usr/bin/env python3
"""Install GES v4.4.1 Candidate with Engineering Method Runtime v1."""
from __future__ import annotations

import os
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))

import install_v440 as v440  # noqa: E402

PACKAGE_VERSION = "4.4.1"
suite = v440.base
suite.PACKAGE_VERSION = PACKAGE_VERSION
_prev_validation_commands = suite.validation_commands


def validation_commands(project, profile, selected, skip):
    commands = _prev_validation_commands(project, profile, selected, skip)
    method_test = (
        "engineering-method self-test",
        [sys.executable, str(project / ".agents/skills/smc-plan-delivery/scripts/test_engineering_method.py"), "-q"],
    )
    # Keep the method runtime close to the existing delivery/adaptive core tests.
    insert_at = min(3, len(commands))
    return commands[:insert_at] + [method_test] + commands[insert_at:]


suite.validation_commands = validation_commands


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUTF8", "1")
    raise SystemExit(suite.main())
