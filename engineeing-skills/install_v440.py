#!/usr/bin/env python3
"""Install GES v4.4.0 Candidate with adaptive review/execution optimizations.

This is a compatibility wrapper over the v4.3 transactional installer. It keeps
Consumer Profile v2, Domain Pack v1, mirror policy, rollback and install-lock
semantics unchanged while adding v4.4 runtime self-tests and release identity.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))

import install_v430 as base  # noqa: E402

PACKAGE_VERSION = "4.4.0"
base.PACKAGE_VERSION = PACKAGE_VERSION
base.__doc__ = __doc__
_v430_validation_commands = base.validation_commands


def validation_commands(project, profile, selected, skip):
    commands = _v430_validation_commands(project, profile, selected, skip)
    extras = [
        (
            "adaptive plan-review self-test",
            [sys.executable, str(project / ".agents/skills/smc-plan-review/scripts/selftest.py"), "-q"],
        ),
        (
            "execution-context artifact self-test",
            [sys.executable, str(project / ".agents/skills/smc-plan-delivery/scripts/test_context_artifacts.py"), "-q"],
        ),
    ]
    # Run v4.4-specific checks immediately after the core delivery self-test,
    # before domain/consumer validators can obscure a core regression.
    return commands[:1] + extras + commands[1:]


base.validation_commands = validation_commands


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUTF8", "1")
    raise SystemExit(base.main())
