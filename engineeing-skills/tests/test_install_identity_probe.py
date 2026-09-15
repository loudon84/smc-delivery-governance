#!/usr/bin/env python3
"""Tests for filesystem install-identity probe."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "consumer-bootstrap"
sys.path.insert(0, str(BOOTSTRAP))

import probe_install_identity as probe_mod  # noqa: E402


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


class InstallIdentityProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.r = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.r)], check=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    # @lat: [[consumer-bootstrap#Install Identity Probe#Reports filesystem lock without git]]
    def test_reports_filesystem_lock_without_git_tracking(self) -> None:
        write(
            self.r,
            ".smc/ges-install-lock.json",
            json.dumps(
                {
                    "schema": "smc.ges.install-lock.v2",
                    "bundle": "5.0.0",
                    "release_identity": {
                        "source_commit": "abc123",
                        "source_tree_dirty": False,
                        "release_eligible": True,
                        "package_manifest_sha256": "deadbeef",
                        "package_file_count": 1,
                    },
                }
            )
            + "\n",
        )
        write(
            self.r,
            ".smc/ges-install-receipt.json",
            json.dumps(
                {
                    "schema": "smc.ges.install-receipt.v1",
                    "bundle": "5.0.0",
                    "transaction_status": "PASS",
                    "receipt_path": ".smc/ges-install-receipts/x.json",
                }
            )
            + "\n",
        )
        write(
            self.r,
            ".smc/ges-install-receipts/x.json",
            json.dumps({"schema": "smc.ges.install-receipt.v1", "bundle": "5.0.0"}) + "\n",
        )
        write(self.r, ".agents/ges/frontend-runtime/.keep", "\n")
        write(
            self.r,
            ".agents/ges/frontend/apps-registry.json",
            json.dumps({"schema": "smc.ges.frontend-app-registry.v2", "repository": "demo", "apps": []})
            + "\n",
        )
        report = probe_mod.probe(self.r)
        self.assertTrue(report["verdict"]["install_proof_found"])
        self.assertEqual(report["bundle"], "5.0.0")
        self.assertIn("5.0.7", report["feature_slices_inferred"])
        self.assertFalse(report["frontend"]["production_sot"])
        self.assertEqual(report["source"], "filesystem")
        self.assertIn("5.0.7", report["verdict"]["not_ok_to_claim_as_bundle"])

    def test_infers_509_runtime_cost_slice(self) -> None:
        write(self.r, ".agents/ges/frontend-runtime/budget_controller.py", "# budget\n")
        write(self.r, ".agents/ges/frontend-runtime/context_cache.py", "# cache\n")
        write(self.r, ".agents/ges/frontend-runtime/policies/context-budget.v1.json", "{}\n")
        write(self.r, ".agents/ges/frontend-runtime/model_dispatch.py", "def self_check_modules():\n return {'model_dispatch': True, 'context_envelope': True, 'stage_cost_closure': True, 'harness_contract': True}\n")
        write(self.r, ".agents/ges/frontend-runtime/context_envelope.py", "# env\n")
        write(self.r, ".agents/ges/frontend-runtime/stage_cost_closure.py", "# scc\n")
        write(self.r, ".agents/ges/frontend-runtime/harness_contract.py", "# harness\n")
        report = probe_mod.probe(self.r)
        self.assertIn("5.0.6", report["feature_slices_inferred"])
        self.assertIn("5.0.8", report["feature_slices_inferred"])
        self.assertIn("5.0.9", report["feature_slices_inferred"])


if __name__ == "__main__":
    raise SystemExit(unittest.main())
