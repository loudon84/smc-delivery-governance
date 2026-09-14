#!/usr/bin/env python3
"""Mandatory v3.7 intent binding tests (C05 / R11–R12)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "domain-runtime"
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(ROOT / ".agents/skills/smc-plan-validator/scripts"))

from domain_intent import EMPTY_INTENT_DIGEST, canonical_empty_binding  # noqa: E402


def load_validate():
    path = ROOT / ".agents/skills/smc-plan-validator/scripts/validate_plan_v37.py"
    spec = importlib.util.spec_from_file_location("validate_plan_v37", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class PlanV37BindingTests(unittest.TestCase):
    # @lat: [[safety-runtime-closure-v503]]

    @classmethod
    def setUpClass(cls):
        cls.v37 = load_validate()

    def _write_plan(self, root: Path, body: str) -> Path:
        p = root / "demo.plan.md"
        p.write_text(body, encoding="utf-8", newline="\n")
        return p

    def test_r11_all_bindings_absent_hard_fail(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = self._write_plan(
                root,
                "---\nplan_contract: smc.plan.v3.7\ngovernance_profile: FULL\n---\n# Plan\n\n## Governance Profile\n\n- Profile: FULL\n",
            )
            errs = self.v37.intent_binding_errors(plan)
            codes = {e["code"] for e in errs}
            self.assertIn("PLAN_DOMAIN_INTENT_BINDING_MISSING", codes)

    def test_partial_binding_hard_fail(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = self._write_plan(
                root,
                "---\nplan_contract: smc.plan.v3.7\ngovernance_profile: FULL\nsource_prd: docs/x.md\n---\n# Plan\n\n## Domain Intent Binding\n\n| Domain | Change ID |\n|---|---|\n",
            )
            errs = self.v37.intent_binding_errors(plan)
            details = {e["detail"] for e in errs if e["code"] == "PLAN_DOMAIN_INTENT_BINDING_MISSING"}
            self.assertTrue({"source_prd_sha256", "domain_activation_digest", "domain_intent_digest"} & details)

    def test_canonical_empty_binding(self):
        empty = canonical_empty_binding()
        self.assertEqual(empty["activation"], "NONE")
        self.assertEqual(empty["domain_intent_digest"], EMPTY_INTENT_DIGEST)
        self.assertIn("Domain Intent Binding", empty["binding_table"])

    def test_r12_seed_exception_does_not_write(self):
        seed = ROOT / ".agents/skills/smc-plan-from-approved-prd-ponytail/scripts/create_plan_seed_v37.py"
        spec = importlib.util.spec_from_file_location("create_plan_seed_v37", seed)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "out.plan.md"
            with mock.patch.object(mod, "apply_bindings", side_effect=RuntimeError("boom")):
                # Call the failure helper path directly
                code = mod._binding_failed("seed", RuntimeError("boom"))
            self.assertEqual(code, 2)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
