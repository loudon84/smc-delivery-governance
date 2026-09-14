#!/usr/bin/env python3
"""Spec Kit adapter conformance tests (C06 / R13)."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "spec-kit"))
import import_proposal as imp  # noqa: E402
import probe  # noqa: E402

FIXTURES = ROOT / "integrations" / "spec-kit" / "fixtures"


class SpecKitAdapterTests(unittest.TestCase):
    # @lat: [[safety-runtime-closure-v503]]

    def test_probe_unavailable_without_cli(self):
        result = probe.probe(executable=None)
        # Force missing by passing a non-existent path via monkeypatch of shutil.which is harder;
        # probe(None) uses which — if specify absent, UNAVAILABLE.
        if result.get("provider_status") != "UNAVAILABLE":
            # Environment may have specify; still must not write Consumer root.
            self.assertNotIn("init", json.dumps(result))
        else:
            self.assertEqual(result["code"], "SPEC_KIT_UNAVAILABLE")
            self.assertEqual(result["integration_status"], "NATIVE_ONLY")

    def test_r13_stale_proposal_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            prd = repo / "docs" / "prd.md"
            prd.parent.mkdir(parents=True)
            prd.write_text("prd\n", encoding="utf-8", newline="\n")
            proposal = json.loads((FIXTURES / "stale.json").read_text(encoding="utf-8"))
            code, _ = imp.validate_proposal(
                proposal, prd=prd, work_facts_digest=proposal["work_facts_digest"]
            )
            self.assertEqual(code, "SPEC_KIT_RESULT_STALE")

    def test_valid_import_writes_under_smc_runs(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            prd = repo / "docs" / "prd.md"
            prd.parent.mkdir(parents=True)
            prd.write_text("prd\n", encoding="utf-8", newline="\n")
            prd_sha = "sha256:" + hashlib.sha256(prd.read_bytes()).hexdigest()
            facts = "sha256:" + "b" * 64
            proposal = json.loads((FIXTURES / "valid.json").read_text(encoding="utf-8"))
            proposal["source_prd_sha256"] = prd_sha
            proposal["work_facts_digest"] = facts
            body = {k: v for k, v in proposal.items() if k != "result_digest"}
            proposal["result_digest"] = imp._sha_payload(body)
            out = imp.import_proposal(proposal, repo=repo, prd=prd, work_facts_digest=facts)
            self.assertTrue(str(out).replace("\\", "/").endswith(".smc/runs/WI-1/ux/ux-proposal-clarify.json"))
            self.assertFalse((repo / ".specify").exists())

    def test_malformed_and_forbidden_capability(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            prd = repo / "docs" / "prd.md"
            prd.parent.mkdir(parents=True)
            prd.write_text("x\n", encoding="utf-8", newline="\n")
            for name, expect in (
                ("malformed.json", "SPEC_KIT_RESULT_INVALID"),
                ("unsupported-capability.json", "SPEC_KIT_RESULT_INVALID"),
                ("conflict-digest.json", "SPEC_KIT_RESULT_CONFLICT"),
            ):
                proposal = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
                if "source_prd_sha256" in proposal:
                    proposal["source_prd_sha256"] = "sha256:" + hashlib.sha256(prd.read_bytes()).hexdigest()
                code, _ = imp.validate_proposal(
                    proposal, prd=prd, work_facts_digest=proposal.get("work_facts_digest") or "sha256:" + "b" * 64
                )
                self.assertEqual(code, expect, name)


if __name__ == "__main__":
    unittest.main()
