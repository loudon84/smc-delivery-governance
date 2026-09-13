#!/usr/bin/env python3
"""Validate GES v4.4.0 Candidate while reusing the v4.3.1 Domain Framework suite."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import validate_package_v430 as base  # noqa: E402

base.PACKAGE_VERSION = "4.4.0"
base.EXPECTED.update({
    "smc-plan-delivery": "1.3.0",
    "smc-plan-review": "1.2.0",
    "subagent-driven-development": "4.3.0",
    "using-superpowers": "4.4.0",
})
base.REQUIRED.extend([
    "install_v440.py",
    "validate_package_v440.py",
    ".agents/skills/using-superpowers/references/complexity-routing.md",
    ".agents/skills/smc-plan-review/scripts/assess_plan_review.py",
    ".agents/skills/smc-plan-review/scripts/build_review_packet.py",
    ".agents/skills/smc-plan-review/scripts/selftest.py",
    ".agents/skills/smc-plan-delivery/scripts/test_context_artifacts.py",
])
base.CORE_GENERIC_FILES = tuple(base.CORE_GENERIC_FILES) + ("install_v440.py", "validate_package_v440.py")


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
        result = base.run(
            [
                sys.executable,
                str(ROOT / "install_v440.py"),
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
            errors.append("v4.4 installer smoke failed: " + (result.stdout + result.stderr).replace("\n", " | "))
            return
        required = (
            ".agents/ges/profile.json",
            ".agents/ges/domain-runtime/domain_runtime.py",
            ".agents/skills/smc-plan-review/scripts/assess_plan_review.py",
            ".agents/skills/smc-plan-review/scripts/build_review_packet.py",
            ".agents/skills/smc-plan-delivery/scripts/test_context_artifacts.py",
            ".agents/skills/using-superpowers/references/complexity-routing.md",
        )
        for rel in required:
            if not (project / rel).is_file():
                errors.append(f"v4.4 installer smoke missing {rel}")
        lock = project / ".smc/ges-install-lock.json"
        if not lock.is_file() or '"bundle": "4.4.0"' not in lock.read_text(encoding="utf-8"):
            errors.append("v4.4 installer smoke did not record bundle 4.4.0")
        if (project / ".agents/skills/code-review-and-quality/SKILL.md").read_text(encoding="utf-8") != "# local review\n":
            errors.append("consumer-local review skill was overwritten")


base.installer_smoke = installer_smoke


if __name__ == "__main__":
    raise SystemExit(base.main())
