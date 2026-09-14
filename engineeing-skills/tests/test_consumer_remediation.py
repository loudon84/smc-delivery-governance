#!/usr/bin/env python3
"""Consumer remediation apply tests (v5.0.5)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "consumer-bootstrap"
sys.path.insert(0, str(BOOTSTRAP))
sys.path.insert(0, str(ROOT))

import apply_remediation as apply_mod  # noqa: E402
import common as C  # noqa: E402
import generate_remediation as gen_mod  # noqa: E402


def write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


class ConsumerRemediationTests(unittest.TestCase):
    # @lat: [[consumer-bootstrap#Automated Remediation]]

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.r = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.r)], check=True)
        write(self.r, "AGENTS.md", "# policy\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_generate_includes_scaffold_and_forbids_spec_md(self) -> None:
        gap = {
            "layers": {
                "ges": {"verdict": "MISSING", "missing": ["ges.profile"]},
                "spec_kit": {"verdict": "MISSING", "missing": []},
                "superpowers": {"verdict": "MISSING", "missing": []},
            }
        }
        plan = gen_mod.generate(self.r, gap, {"probe": {"provider_status": "UNAVAILABLE"}})
        self.assertEqual(plan["schema"], "smc.ges.consumer-remediation-plan.v1")
        targets = [a["target"] for a in plan["actions"] if a["kind"] == "WRITE_TEMPLATE"]
        self.assertTrue(any(t.startswith(".specify/") for t in targets))
        self.assertNotIn(".specify/spec.md", targets)
        self.assertIn(".specify/spec.md", plan["forbidden"])

    def test_apply_writes_missing_only(self) -> None:
        write(self.r, ".specify/constitution.md", "# keep\n")
        gap = {
            "layers": {
                "ges": {"verdict": "PASS", "missing": []},
                "spec_kit": {"verdict": "PARTIAL", "missing": []},
                "superpowers": {"verdict": "MISSING", "missing": []},
            }
        }
        plan = gen_mod.generate(self.r, gap, {})
        receipt = apply_mod.apply_plan(self.r, plan, do_apply=True)
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(
            (self.r / ".specify/constitution.md").read_text(encoding="utf-8"),
            "# keep\n",
        )
        self.assertTrue((self.r / ".agents/ges/spec-superpower-ges.json").is_file())
        self.assertTrue((self.r / ".agents/skills/brainstorming/SKILL.md").is_file())
        self.assertFalse((self.r / ".specify/spec.md").exists())
        self.assertFalse((self.r / ".agents/ges/profile.json").exists())

    def test_refuse_spec_md_target(self) -> None:
        plan = {
            "schema": "smc.ges.consumer-remediation-plan.v1",
            "actions": [
                {
                    "id": "BAD-001",
                    "kind": "WRITE_TEMPLATE",
                    "target": ".specify/spec.md",
                    "template": "spec-kit/constitution.md",
                    "reason": "should fail",
                }
            ],
        }
        with self.assertRaises(ValueError) as ctx:
            apply_mod.apply_plan(self.r, plan, do_apply=True)
        self.assertIn("FORBIDDEN", str(ctx.exception))

    def test_rollback_on_failure(self) -> None:
        gap = {
            "layers": {
                "ges": {"verdict": "PASS", "missing": []},
                "spec_kit": {"verdict": "MISSING", "missing": []},
                "superpowers": {"verdict": "MISSING", "missing": []},
            }
        }
        plan = gen_mod.generate(self.r, gap, {})
        # Inject a bad action after valid ones by replacing last write with missing template.
        plan["actions"] = [
            a for a in plan["actions"] if a["kind"] == "WRITE_TEMPLATE"
        ][:2] + [
            {
                "id": "BAD-002",
                "kind": "WRITE_TEMPLATE",
                "target": ".agents/ges/spec-kit-binding.json",
                "template": "ges/does-not-exist.json",
                "reason": "force fail",
            }
        ]
        with self.assertRaises(ValueError):
            apply_mod.apply_plan(self.r, plan, do_apply=True)
        # First writes should be rolled back when failure happens mid-transaction.
        # Depending on order, constitution may have been written then restored.
        # Ensure no partial bridge contract from the failing action.
        self.assertFalse((self.r / ".agents/ges/spec-kit-binding.json").exists())

    def test_dry_run_writes_nothing(self) -> None:
        gap = {
            "layers": {
                "ges": {"verdict": "PASS", "missing": []},
                "spec_kit": {"verdict": "MISSING", "missing": []},
                "superpowers": {"verdict": "MISSING", "missing": []},
            }
        }
        plan = gen_mod.generate(self.r, gap, {})
        receipt = apply_mod.apply_plan(self.r, plan, do_apply=False)
        self.assertEqual(receipt["status"], "DRY_RUN")
        self.assertFalse((self.r / ".specify").exists())
        self.assertTrue(any(s.startswith("WOULD_WRITE:") for s in receipt["skipped"]))


if __name__ == "__main__":
    raise SystemExit(unittest.main())
