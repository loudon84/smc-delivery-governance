#!/usr/bin/env python3
"""Superpowers method-provider conformance tests (C07 / R14–R15)."""
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "superpowers"))
import dispatch  # noqa: E402
import verify_result as vr  # noqa: E402


def _digest(obj: dict) -> str:
    body = {k: v for k, v in obj.items() if k != "result_digest"}
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


class SuperpowersProviderTests(unittest.TestCase):
    # @lat: [[safety-runtime-closure-v503]]

    def test_provenance_present(self):
        prov = json.loads(
            (ROOT / "integrations/superpowers/upstream-provenance.json").read_text(encoding="utf-8")
        )
        self.assertEqual(prov["schema"], "smc.ges.provider-provenance.v1")
        caps = {c["capability_id"]: c for c in prov["capabilities"]}
        for need in (
            "executing-plans",
            "subagent-driven-development",
            "test-driven-development",
            "systematic-debugging",
            "verification-before-completion",
        ):
            self.assertIn(need, caps)
            self.assertTrue(caps[need]["upstream_sha256"])
            self.assertEqual(caps[need]["provider_state"], "UPSTREAM_PINNED")

    def test_r14_out_of_scope_write_blocked(self):
        packet = dispatch.build_task_packet(
            plan_id="P1",
            plan_semantic_hash="sha256:plan",
            todo_id="T01",
            write_ownership=["src/app.ts"],
            read_scope=["src/"],
            source_context_capsule_ids=[],
            engineering_method_policy="UPSTREAM_PINNED",
            required_tdd_debug_gates=[],
            focused_verification_command=["pytest", "-q"],
        )
        result = {
            "schema": "smc.ges.method-result.v1",
            "provider": "superpowers",
            "provider_version": "pinned",
            "capability": "executing-plans",
            "plan_id": "P1",
            "plan_semantic_hash": "sha256:plan",
            "todo_id": "T01",
            "changed_paths": ["docs/prd/secret.md"],
            "provider_self_pass": False,
        }
        result["result_digest"] = _digest(result)
        code, reasons = vr.verify_result(result, packet=packet, allowed_writes=packet["write_ownership"])
        self.assertEqual(code, "SUPERPOWERS_SCOPE_VIOLATION")
        self.assertTrue(reasons)

    def test_r15_provider_pass_not_evidence(self):
        packet = dispatch.build_task_packet(
            plan_id="P1",
            plan_semantic_hash="sha256:plan",
            todo_id="T01",
            write_ownership=["src/app.ts"],
            read_scope=[],
            source_context_capsule_ids=[],
            engineering_method_policy="UPSTREAM_PINNED",
            required_tdd_debug_gates=[],
            focused_verification_command=["pytest", "-q"],
        )
        result = {
            "schema": "smc.ges.method-result.v1",
            "provider": "superpowers",
            "provider_version": "pinned",
            "capability": "verification-before-completion",
            "plan_id": "P1",
            "plan_semantic_hash": "sha256:plan",
            "todo_id": "T01",
            "changed_paths": ["src/app.ts"],
            "provider_self_pass": True,
        }
        result["result_digest"] = _digest(result)
        code, reasons = vr.verify_result(result, packet=packet, allowed_writes=packet["write_ownership"])
        self.assertEqual(code, "OK_PROVIDER_PASS_NOT_EVIDENCE")
        self.assertIn("provider_self_pass_ignored", reasons)

    def test_stale_plan_hash_rejected(self):
        packet = dispatch.build_task_packet(
            plan_id="P1",
            plan_semantic_hash="sha256:plan",
            todo_id="T01",
            write_ownership=["src/app.ts"],
            read_scope=[],
            source_context_capsule_ids=[],
            engineering_method_policy="UPSTREAM_PINNED",
            required_tdd_debug_gates=[],
            focused_verification_command=["pytest", "-q"],
        )
        result = {
            "schema": "smc.ges.method-result.v1",
            "provider": "superpowers",
            "provider_version": "pinned",
            "capability": "executing-plans",
            "plan_id": "P1",
            "plan_semantic_hash": "sha256:other",
            "todo_id": "T01",
            "changed_paths": ["src/app.ts"],
            "provider_self_pass": False,
        }
        result["result_digest"] = _digest(result)
        code, _ = vr.verify_result(result, packet=packet, allowed_writes=packet["write_ownership"])
        self.assertEqual(code, "SUPERPOWERS_RESULT_STALE")


if __name__ == "__main__":
    unittest.main()
