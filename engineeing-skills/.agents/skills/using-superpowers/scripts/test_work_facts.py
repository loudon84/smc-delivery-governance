#!/usr/bin/env python3
"""Work facts authority binding tests (PRD Architecture Closure C04)."""
from __future__ import annotations

import unittest

from work_facts import (
    build_envelope,
    from_work_authority,
    verify_envelope,
)
from work_authority import build_authority
from work_router import REQUIRED, RISKS, route, route_bound


def safe(**extra):
    return {**dict.fromkeys(REQUIRED, True), **dict.fromkeys(RISKS, False), **extra}


class WorkFactsTests(unittest.TestCase):
    def test_ac12_production_requires_provenance(self):
        env = build_envelope(
            "RM-1",
            safe(
                research_intent=True,
                governed=False,
                retained_production_change=False,
                production_write_requested=False,
                durable_product_artifact_requested=False,
            ),
            provenance={},
        )
        status, reasons = verify_envelope(env)
        self.assertEqual(status, "UNBOUND")
        self.assertIn("WORK_FACTS_UNBOUND", reasons)
        out = route_bound(env)
        self.assertNotEqual(out["governance_profile"], "NONE")

    def test_ac13_plan_forces_governed_true(self):
        env = build_envelope(
            "RM-1",
            safe(
                research_intent=True,
                governed=False,
                retained_production_change=False,
                production_write_requested=False,
                durable_product_artifact_requested=False,
            ),
            provenance={
                "governed": {
                    "source_kind": "PLAN",
                    "source_ref": "plans/x.plan.md",
                    "source_sha256": "sha256:abc",
                    "authority": "AUTHORITATIVE",
                }
            },
        )
        status, reasons = verify_envelope(env)
        self.assertEqual(status, "CONFLICT")
        self.assertIn("WORK_FACTS_CONFLICT", reasons)

    def test_ac14_source_hash_change_stales(self):
        env = build_envelope(
            "RM-1",
            safe(
                research_intent=True,
                governed=False,
                retained_production_change=False,
                production_write_requested=False,
                durable_product_artifact_requested=False,
            ),
            provenance={
                "governed": {
                    "source_kind": "ORCHESTRATOR_REQUEST",
                    "source_ref": "",
                    "source_sha256": "",
                    "authority": "AUTHORITATIVE",
                }
            },
        )
        env["facts_digest"] = "sha256:dead"
        status, reasons = verify_envelope(env)
        self.assertEqual(status, "STALE")
        self.assertIn("WORK_FACTS_STALE", reasons)

    def test_ac15_worker_assertion_cannot_none(self):
        env = build_envelope(
            "RM-1",
            safe(
                research_intent=True,
                governed=False,
                retained_production_change=False,
                production_write_requested=False,
                durable_product_artifact_requested=False,
            ),
            provenance={
                "governed": {
                    "source_kind": "WORKER_ASSERTION",
                    "source_ref": "",
                    "source_sha256": "",
                    "authority": "WORKER",
                }
            },
        )
        status, reasons = verify_envelope(env)
        self.assertEqual(status, "INVALID")
        self.assertIn("WORK_FACTS_AUTHORITY_MISSING", reasons)

    def test_verified_orchestrator_research_none(self):
        env = build_envelope(
            "RM-1",
            safe(
                research_intent=True,
                governed=False,
                retained_production_change=False,
                production_write_requested=False,
                durable_product_artifact_requested=False,
            ),
            provenance={
                "governed": {
                    "source_kind": "ORCHESTRATOR_REQUEST",
                    "source_ref": "",
                    "source_sha256": "",
                    "authority": "AUTHORITATIVE",
                },
                "retained_production_change": {
                    "source_kind": "ORCHESTRATOR_REQUEST",
                    "source_ref": "",
                    "source_sha256": "",
                    "authority": "AUTHORITATIVE",
                },
                "production_write_requested": {
                    "source_kind": "ORCHESTRATOR_REQUEST",
                    "source_ref": "",
                    "source_sha256": "",
                    "authority": "AUTHORITATIVE",
                },
                "durable_product_artifact_requested": {
                    "source_kind": "ORCHESTRATOR_REQUEST",
                    "source_ref": "",
                    "source_sha256": "",
                    "authority": "AUTHORITATIVE",
                },
            },
        )
        status, _ = verify_envelope(env)
        self.assertEqual(status, "VERIFIED")
        out = route_bound(env)
        self.assertEqual(out["governance_profile"], "NONE")

    def test_authority_compat_shim(self):
        auth = build_authority(
            "RM-1",
            {
                "governed": False,
                "retained_production_change": False,
                "production_write_requested": False,
                "durable_product_artifact_requested": False,
            },
            [{"type": "ORCHESTRATOR_REQUEST", "path": "", "sha256": "", "authority": "ORCHESTRATOR"}],
        )
        env = from_work_authority(auth)
        self.assertEqual(env["schema"], "smc.ges.work-facts.v1")
        out = route(safe(research_intent=True), authority=auth, require_authority_for_none=True)
        self.assertEqual(out["governance_profile"], "NONE")


if __name__ == "__main__":
    unittest.main()
