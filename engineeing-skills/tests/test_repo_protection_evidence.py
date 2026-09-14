#!/usr/bin/env python3
"""Strict repository protection evidence tests (C03 / R08)."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "acceptance" / "verify_repository_protection.py"
FIXTURES = ROOT / "acceptance" / "fixtures" / "repo-protection"


def load_mod():
    spec = importlib.util.spec_from_file_location("verify_repository_protection", VERIFY)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class RepoProtectionEvidenceTests(unittest.TestCase):
    # @lat: [[safety-runtime-closure-v503]]

    @classmethod
    def setUpClass(cls):
        cls.mod = load_mod()

    def _eval_fixture(self, name: str):
        data = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
        parsed = self.mod._normalize(data)
        return self.mod.evaluate(parsed)

    def test_r08_protected_only_incomplete_invalid(self):
        code, problems = self._eval_fixture("protected-only-incomplete.json")
        self.assertEqual(code, "REPO_GOVERNANCE_INVALID_EVIDENCE")
        self.assertTrue(any("missing field" in p for p in problems))

    def test_missing_checks_not_autofilled(self):
        data = json.loads((FIXTURES / "missing-checks.json").read_text(encoding="utf-8"))
        parsed = self.mod.parse_evidence(data)
        self.assertEqual(parsed["required_checks"], [])
        code, problems = self.mod.evaluate(self.mod._normalize(data))
        self.assertEqual(code, "REPO_GOVERNANCE_DRIFT")
        self.assertTrue(any("missing check" in p for p in problems))

    def test_missing_force_fields_not_default_true(self):
        data = json.loads((FIXTURES / "missing-force-fields.json").read_text(encoding="utf-8"))
        parsed = self.mod.parse_evidence(data)
        self.assertIsNone(parsed["force_push_blocked"])
        self.assertIsNone(parsed["deletion_blocked"])
        self.assertIsNone(parsed["direct_update_restricted"])
        code, _ = self.mod.evaluate(self.mod._normalize(data))
        self.assertEqual(code, "REPO_GOVERNANCE_INVALID_EVIDENCE")

    def test_not_master_drift(self):
        code, problems = self._eval_fixture("not-master.json")
        self.assertEqual(code, "REPO_GOVERNANCE_DRIFT")
        self.assertTrue(any("master" in p for p in problems))

    def test_evaluate_enforcement_not_active(self):
        code, problems = self._eval_fixture("evaluate-enforcement.json")
        self.assertEqual(code, "REPO_GOVERNANCE_DRIFT")
        self.assertTrue(any("enforcement" in p for p in problems))

    def test_bypass_actors_reported(self):
        code, problems = self._eval_fixture("with-bypass.json")
        self.assertEqual(code, "REPO_GOVERNANCE_DRIFT")
        self.assertTrue(any("bypass" in p for p in problems))

    def test_complete_pass(self):
        code, problems = self._eval_fixture("complete-pass.json")
        self.assertEqual(code, "REPO_GOVERNANCE_PASS")
        self.assertEqual(problems, [])

    def test_no_substring_inference(self):
        data = {
            "protected": True,
            "notes": "this fixture mentions pull_request in prose only",
            "required_checks": ["validate", "GES Package Gate / validate-package"],
            "force_push_blocked": True,
            "deletion_blocked": True,
            "direct_update_restricted": True,
        }
        parsed = self.mod.parse_evidence(data)
        self.assertIsNone(parsed["require_pr"])


if __name__ == "__main__":
    unittest.main()
