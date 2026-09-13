#!/usr/bin/env python3
"""Validate GES v4.4.1 Candidate on top of the v4.4.0 package suite."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import validate_package_v440 as v440  # noqa: E402

suite = v440.base
suite.PACKAGE_VERSION = "4.4.1"
suite.EXPECTED.update({
    "smc-plan-delivery": "1.4.0",
    "executing-plans": "4.3.0",
    "subagent-driven-development": "4.4.0",
})
suite.REQUIRED.extend([
    "install_v441.py",
    "validate_package_v441.py",
    ".agents/skills/smc-plan-delivery/scripts/engineering_method.py",
    ".agents/skills/smc-plan-delivery/scripts/test_engineering_method.py",
    ".agents/skills/smc-plan-delivery/references/engineering-method-contract.md",
    ".agents/skills/smc-plan-delivery/references/tdd-method.md",
    ".agents/skills/smc-plan-delivery/references/systematic-debugging.md",
])
suite.CORE_GENERIC_FILES = tuple(suite.CORE_GENERIC_FILES) + (
    "install_v441.py",
    "validate_package_v441.py",
    ".agents/skills/smc-plan-delivery/scripts/engineering_method.py",
)


def installer_smoke(errors):
    with tempfile.TemporaryDirectory() as td:
        project = Path(td) / "repo"
        project.mkdir()
        subprocess.run(["git", "init", "-q", str(project)], check=True)
        (project / ".agents/skills/code-review-and-quality").mkdir(parents=True)
        (project / ".agents/skills/code-review-and-quality/SKILL.md").write_text("# local review\n", encoding="utf-8")
        (project / ".agents/skills/verification-before-completion").mkdir(parents=True)
        (project / ".agents/skills/verification-before-completion/SKILL.md").write_text("# local verification\n", encoding="utf-8")
        legacy_validator = project / ".agents/skills/smc-plan-validator/scripts/validate_plan.py"
        legacy_validator.parent.mkdir(parents=True)
        legacy_validator.write_text("def validate_plan(path): return []\n", encoding="utf-8")
        (project / ".cursor/skills").mkdir(parents=True)
        (project / "package.json").write_text("{}\n", encoding="utf-8")
        result = suite.run(
            [
                sys.executable,
                str(ROOT / "install_v441.py"),
                str(project),
                "--profile",
                "smc-copilot-work",
                "--apply",
                "--skip-project-validator",
            ],
            ROOT,
            capture=True,
        )
        if result.returncode:
            errors.append("v4.4.1 installer smoke failed: " + (result.stdout + result.stderr).replace("\n", " | "))
            return
        required = (
            ".agents/skills/smc-plan-delivery/scripts/engineering_method.py",
            ".agents/skills/smc-plan-delivery/scripts/test_engineering_method.py",
            ".agents/skills/smc-plan-delivery/references/engineering-method-contract.md",
            ".agents/skills/smc-plan-delivery/references/tdd-method.md",
            ".agents/skills/smc-plan-delivery/references/systematic-debugging.md",
        )
        for rel in required:
            if not (project / rel).is_file():
                errors.append(f"v4.4.1 installer smoke missing {rel}")
        lock = project / ".smc/ges-install-lock.json"
        if not lock.is_file() or '"bundle": "4.4.1"' not in lock.read_text(encoding="utf-8"):
            errors.append("v4.4.1 installer smoke did not record bundle 4.4.1")
        if (project / ".agents/skills/code-review-and-quality/SKILL.md").read_text(encoding="utf-8") != "# local review\n":
            errors.append("consumer-local review skill was overwritten")


suite.installer_smoke = installer_smoke


def main() -> int:
    method = suite.run(
        [sys.executable, str(ROOT / ".agents/skills/smc-plan-delivery/scripts/test_engineering_method.py"), "-q"],
        ROOT,
        capture=True,
    )
    if method.returncode:
        print("ENGINEERING METHOD SELFTEST FAILED", file=sys.stderr)
        print((method.stdout + method.stderr).strip(), file=sys.stderr)
        return 1
    return suite.main()


if __name__ == "__main__":
    raise SystemExit(main())
