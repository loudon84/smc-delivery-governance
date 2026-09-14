#!/usr/bin/env python3
"""Adversarial rollback path confinement tests (R01–R04 / C01-AC01..AC06)."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import rollback as rb  # noqa: E402


def _write_tx(project: Path, records: list[dict], *, tx_id: str = "tx1") -> Path:
    backup = project / ".smc" / "skill-upgrade-backups" / tx_id
    backup.mkdir(parents=True, exist_ok=True)
    for rec in records:
        rel = rec["path"]
        if rec.get("existed_before"):
            src = backup / rel
            src.parent.mkdir(parents=True, exist_ok=True)
            src.write_text(rec.get("_backup_body", "old\n"), encoding="utf-8", newline="\n")
            rec["original_sha256"] = rb.sha256(src)
        target = project / rel
        if rec.get("installed_sha256") is None and not rec.get("_skip_target"):
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rec.get("_installed_body", "new\n"), encoding="utf-8", newline="\n")
            rec["installed_sha256"] = rb.sha256(target)
        # Strip test-only keys before persisting
    clean = [
        {
            "path": r["path"],
            "existed_before": bool(r.get("existed_before")),
            "original_sha256": r.get("original_sha256"),
            "installed_sha256": r.get("installed_sha256"),
        }
        for r in records
    ]
    (backup / "upgrade-manifest.json").write_text(
        json.dumps({"schema": "smc.ges.install.transaction.v2", "files": clean}, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return backup


def _run(project: Path, *extra: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(ROOT / "rollback.py"), str(project), *extra]
    return subprocess.run(cmd, capture_output=True, text=True)


class RollbackSecurityTests(unittest.TestCase):
    # @lat: [[safety-runtime-closure-v503]]

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ges-rollback-"))
        self.project = self.tmp / "project"
        self.project.mkdir()
        (self.project / ".git").mkdir()
        (self.project / "safe").mkdir()
        (self.project / "safe" / "file.txt").write_text("keep\n", encoding="utf-8", newline="\n")
        self.victim = self.tmp / "victim.txt"
        self.victim.write_text("SECRET\n", encoding="utf-8", newline="\n")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_r01_relative_escape_fail_closed(self) -> None:
        backup = _write_tx(
            self.project,
            [{"path": "../victim.txt", "existed_before": False, "_skip_target": True, "installed_sha256": "x"}],
        )
        # Bypass writer helper path validation by rewriting manifest directly
        data = json.loads((backup / "upgrade-manifest.json").read_text(encoding="utf-8"))
        data["files"][0]["path"] = "../victim.txt"
        (backup / "upgrade-manifest.json").write_text(json.dumps(data) + "\n", encoding="utf-8", newline="\n")
        before = self.victim.read_bytes()
        proc = _run(self.project, "--backup", str(backup), "--apply")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("ROLLBACK_PATH_ESCAPE", proc.stderr)
        self.assertEqual(self.victim.read_bytes(), before)

    def test_r02_absolute_drive_unc_fail_closed(self) -> None:
        backup = _write_tx(self.project, [{"path": "safe/file.txt", "existed_before": True, "_backup_body": "old\n"}])
        for bad in ["/etc/passwd", "C:/Windows/System32/drivers/etc/hosts", r"\\server\share\file"]:
            data = json.loads((backup / "upgrade-manifest.json").read_text(encoding="utf-8"))
            data["files"][0]["path"] = bad
            (backup / "upgrade-manifest.json").write_text(json.dumps(data) + "\n", encoding="utf-8", newline="\n")
            proc = _run(self.project, "--backup", str(backup), "--apply")
            self.assertNotEqual(proc.returncode, 0, bad)
            self.assertTrue(
                "ROLLBACK_PATH_ESCAPE" in proc.stderr or "ROLLBACK_PATH_INVALID" in proc.stderr,
                msg=f"{bad}: {proc.stderr}",
            )

    def test_r03_symlink_escape_fail_closed(self) -> None:
        if os.name == "nt":
            # Creating directory junctions may require privileges; skip if unavailable.
            link = self.project / "escape-link"
            try:
                os.symlink(self.tmp, link, target_is_directory=True)
            except OSError:
                self.skipTest("symlink/junction creation unavailable")
        else:
            link = self.project / "escape-link"
            os.symlink(self.tmp, link, target_is_directory=True)
        backup = _write_tx(self.project, [{"path": "safe/file.txt", "existed_before": False}])
        data = json.loads((backup / "upgrade-manifest.json").read_text(encoding="utf-8"))
        data["files"][0]["path"] = "escape-link/victim.txt"
        data["files"][0]["existed_before"] = False
        (backup / "upgrade-manifest.json").write_text(json.dumps(data) + "\n", encoding="utf-8", newline="\n")
        before = self.victim.read_bytes()
        proc = _run(self.project, "--backup", str(backup), "--apply")
        self.assertNotEqual(proc.returncode, 0)
        self.assertTrue(
            "ROLLBACK_SYMLINK_ESCAPE" in proc.stderr or "ROLLBACK_PATH_ESCAPE" in proc.stderr,
            msg=proc.stderr,
        )
        self.assertEqual(self.victim.read_bytes(), before)

    def test_r04_one_invalid_among_valid_zero_mutation(self) -> None:
        backup = _write_tx(
            self.project,
            [
                {"path": "safe/file.txt", "existed_before": True, "_backup_body": "restored\n"},
                {"path": "safe/other.txt", "existed_before": False},
            ],
        )
        target = self.project / "safe" / "file.txt"
        original = target.read_bytes()
        data = json.loads((backup / "upgrade-manifest.json").read_text(encoding="utf-8"))
        data["files"].append(
            {"path": "../victim.txt", "existed_before": False, "installed_sha256": "x", "original_sha256": None}
        )
        (backup / "upgrade-manifest.json").write_text(json.dumps(data) + "\n", encoding="utf-8", newline="\n")
        other = self.project / "safe" / "other.txt"
        other_before = other.read_bytes() if other.is_file() else None
        victim_before = self.victim.read_bytes()
        proc = _run(self.project, "--backup", str(backup), "--apply", "--force")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("ROLLBACK_PATH_ESCAPE", proc.stderr)
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(other.read_bytes() if other.is_file() else None, other_before)
        self.assertEqual(self.victim.read_bytes(), victim_before)

    def test_force_does_not_bypass_containment(self) -> None:
        backup = _write_tx(self.project, [{"path": "safe/file.txt", "existed_before": False}])
        data = json.loads((backup / "upgrade-manifest.json").read_text(encoding="utf-8"))
        data["files"][0]["path"] = "../victim.txt"
        (backup / "upgrade-manifest.json").write_text(json.dumps(data) + "\n", encoding="utf-8", newline="\n")
        before = self.victim.read_bytes()
        proc = _run(self.project, "--backup", str(backup), "--apply", "--force")
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(self.victim.read_bytes(), before)

    def test_duplicate_target_rejected(self) -> None:
        backup = _write_tx(
            self.project,
            [
                {"path": "safe/file.txt", "existed_before": True, "_backup_body": "a\n"},
                {"path": "safe/file.txt", "existed_before": False},
            ],
        )
        proc = _run(self.project, "--backup", str(backup), "--apply")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("ROLLBACK_DUPLICATE_TARGET", proc.stderr)

    def test_backup_outside_allowed_root_rejected(self) -> None:
        outside = self.tmp / "evil-backup"
        outside.mkdir()
        (outside / "upgrade-manifest.json").write_text(
            json.dumps({"files": [{"path": "safe/file.txt", "existed_before": False, "installed_sha256": "x"}]})
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        proc = _run(self.project, "--backup", str(outside), "--apply")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("ROLLBACK_BACKUP_ESCAPE", proc.stderr)

    def test_legitimate_round_trip(self) -> None:
        target = self.project / "safe" / "file.txt"
        target.write_text("before-install\n", encoding="utf-8", newline="\n")
        backup = _write_tx(
            self.project,
            [
                {
                    "path": "safe/file.txt",
                    "existed_before": True,
                    "_backup_body": "before-install\n",
                    "_installed_body": "after-install\n",
                },
                {"path": "safe/new.txt", "existed_before": False, "_installed_body": "brand-new\n"},
            ],
        )
        new_file = self.project / "safe" / "new.txt"
        self.assertTrue(new_file.is_file())
        proc = _run(self.project, "--backup", str(backup), "--apply")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(target.read_text(encoding="utf-8"), "before-install\n")
        self.assertFalse(new_file.exists())

    def test_resolver_rejects_empty_and_dot(self) -> None:
        with self.assertRaises(rb.RollbackError):
            rb.resolve_record_target(self.project, "")
        with self.assertRaises(rb.RollbackError):
            rb.resolve_record_target(self.project, ".")
        with self.assertRaises(rb.RollbackError):
            rb.resolve_record_target(self.project, "safe/./file.txt")


if __name__ == "__main__":
    unittest.main()
