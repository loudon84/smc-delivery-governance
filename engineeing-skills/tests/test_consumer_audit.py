#!/usr/bin/env python3
"""Consumer audit + gap analysis tests (v5.0.5)."""
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
sys.path.insert(0, str(ROOT))

import audit_consumer as audit_mod  # noqa: E402
import analyze_gap as gap_mod  # noqa: E402
import common as C  # noqa: E402


def write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


def minimal_git(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    write(root, "AGENTS.md", "# policy\n")


class ConsumerAuditTests(unittest.TestCase):
    # @lat: [[consumer-bootstrap#Consumer Audit]]

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.r = Path(self.tmp.name)
        minimal_git(self.r)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_missing_consumer_is_gaps(self) -> None:
        report = audit_mod.audit(self.r)
        self.assertEqual(report["schema"], "smc.ges.consumer-audit.v1")
        self.assertFalse(report["ok"])
        self.assertEqual(report["layers"]["ges"]["verdict"], "MISSING")
        self.assertEqual(report["layers"]["spec_kit"]["verdict"], "MISSING")
        self.assertIn(report["layers"]["superpowers"]["verdict"], {"MISSING", "PARTIAL"})

    def test_partial_ges_surface(self) -> None:
        write(self.r, ".agents/ges/profile.json", '{"schema":"smc.ges.consumer-profile.v3","id":"generic","version":"2.0.0"}\n')
        write(self.r, ".agents/skills/smc-plan-delivery/scripts/run_selftest.py", "print('x')\n")
        report = audit_mod.audit(self.r)
        self.assertEqual(report["layers"]["ges"]["verdict"], "PARTIAL")

    def test_schema_files_exist(self) -> None:
        for name in (
            "consumer-audit.v1.json",
            "consumer-gap.v1.json",
            "consumer-remediation-plan.v1.json",
            "consumer-bootstrap-receipt.v1.json",
            "consumer-validation.v1.json",
        ):
            path = C.SCHEMAS / name
            self.assertTrue(path.is_file(), name)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("$id", data)

    def test_gap_codes_and_claims(self) -> None:
        report = audit_mod.audit(self.r)
        gap = gap_mod.analyze(report)
        self.assertEqual(gap["schema"], "smc.ges.consumer-gap.v1")
        self.assertIn("CONSUMER_GAP_PRESENT", gap["codes"])
        for value in gap["claims"].values():
            self.assertIn(value, C.CLAIM_VOCAB)

    def test_write_reports(self) -> None:
        report = audit_mod.audit(self.r)
        jp, mp = audit_mod.write_reports(self.r, report)
        self.assertTrue(jp.is_file())
        self.assertTrue(mp.is_file())
        gap = gap_mod.analyze(report)
        md = gap_mod.write_gap(self.r, gap)
        self.assertTrue(md.is_file())
        self.assertIn("Consumer Gap Analysis", md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(unittest.main())
