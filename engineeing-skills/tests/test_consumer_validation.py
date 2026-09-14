#!/usr/bin/env python3
"""Consumer validation report tests (v5.0.5)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "consumer-bootstrap"
sys.path.insert(0, str(BOOTSTRAP))
sys.path.insert(0, str(ROOT))

import apply_remediation as apply_mod  # noqa: E402
import generate_remediation as gen_mod  # noqa: E402
import validate_consumer as val_mod  # noqa: E402


def write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


def seed_ges_surface(root: Path) -> None:
    """Minimal GES surfaces required by validate_consumer (not a full install)."""
    write(
        root,
        ".smc/ges-install-lock.json",
        json.dumps({"schema": "smc.ges.install-lock.v2", "bundle": "5.0.0"}) + "\n",
    )
    write(
        root,
        ".smc/ges-install-receipt.json",
        json.dumps({"schema": "smc.ges.install-receipt.v1", "install_id": "t"}) + "\n",
    )
    write(root, ".agents/ges/profile.json", '{"schema":"smc.ges.consumer-profile.v3","id":"generic","version":"2.0.0"}\n')
    write(root, ".agents/ges/domain-packs/registry.json", '{"schema":"smc.ges.domain-registry.v1","packs":{}}\n')
    write(root, ".agents/ges/domain-runtime/domain_runtime.py", "print('ok')\n")
    # Copy managed skill stubs from package for required validation paths.
    for name in (
        "smc-plan-validator",
        "smc-plan-delivery",
        "smc-prd-grounding",
        "smc-work-router",
        "executing-plans",
        "verification-before-completion",
        "subagent-driven-development",
        "using-superpowers",
    ):
        src = ROOT / ".agents" / "skills" / name
        if src.is_dir():
            shutil.copytree(src, root / ".agents" / "skills" / name, dirs_exist_ok=True)
    # Remaining managed skills as stubs so audit GES layer can PASS.
    import common as C

    for name in C.managed_skills():
        skill = root / ".agents" / "skills" / name / "SKILL.md"
        if not skill.is_file():
            write(root, f".agents/skills/{name}/SKILL.md", f"---\nname: {name}\n---\n# stub\n")
    write(root, ".agents/skills/code-review-and-quality/SKILL.md", "---\nname: code-review-and-quality\n---\n# stub\n")
    # Ensure delivery scripts exist even if package layout differs.
    for rel in (
        ".agents/skills/smc-plan-validator/scripts/validate_plan_v37.py",
        ".agents/skills/smc-plan-delivery/scripts/run_selftest.py",
        ".agents/skills/smc-plan-delivery/scripts/acceptance.py",
        ".agents/skills/smc-plan-delivery/scripts/runtime_metrics.py",
        ".agents/skills/smc-plan-delivery/scripts/evidence.py",
        ".agents/skills/smc-plan-delivery/scripts/engineering_method.py",
    ):
        if not (root / rel).is_file():
            write(root, rel, "print('stub')\n")


class ConsumerValidationTests(unittest.TestCase):
    # @lat: [[consumer-bootstrap#Consumer Validation]]

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.r = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.r)], check=True)
        write(self.r, "AGENTS.md", "# policy\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_validation_fails_on_empty(self) -> None:
        result = val_mod.validate(self.r)
        self.assertEqual(result["schema"], "smc.ges.consumer-validation.v1")
        self.assertFalse(result["ok"])
        self.assertEqual(result["code"], "CONSUMER_VALIDATION_FAILED")

    def test_validation_pass_after_seed_and_bootstrap(self) -> None:
        seed_ges_surface(self.r)
        gap = {
            "layers": {
                "ges": {"verdict": "PASS", "missing": []},
                "spec_kit": {"verdict": "MISSING", "missing": []},
                "superpowers": {"verdict": "MISSING", "missing": []},
            }
        }
        plan = gen_mod.generate(self.r, gap, {})
        receipt = apply_mod.apply_plan(self.r, plan, do_apply=True)
        self.assertEqual(receipt["status"], "PASS")
        result = val_mod.validate(self.r)
        if not result["ok"]:
            # Helpful failure dump
            self.fail(json.dumps(result, indent=2))
        self.assertEqual(result["code"], "CONSUMER_VALIDATION_PASS")


if __name__ == "__main__":
    raise SystemExit(unittest.main())
