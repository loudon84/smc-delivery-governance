#!/usr/bin/env python3
"""Install receipt finalization failure-injection tests (C04 / R09–R10)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import install_v500 as installer  # noqa: E402


def write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


def fixture(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    write(root, "AGENTS.md", "# Project policy\n")
    for skill in ("code-review-and-quality", "verification-before-completion"):
        write(root, f".agents/skills/{skill}/SKILL.md", "# consumer-owned\n")
    (root / ".cursor/skills").mkdir(parents=True)


class InstallFinalizationTests(unittest.TestCase):
    # @lat: [[safety-runtime-closure-v503]]

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.r = Path(self.tmp.name)
        installer._FINALIZATION_FAULT = None

    def tearDown(self) -> None:
        installer._FINALIZATION_FAULT = None
        self.tmp.cleanup()

    def _snapshot(self) -> dict[str, bytes]:
        return {
            p.relative_to(self.r).as_posix(): p.read_bytes()
            for p in self.r.rglob("*")
            if p.is_file() and ".git" not in p.parts and ".smc" not in p.parts
        }

    def _receipt_paths(self) -> list[Path]:
        out = []
        d = self.r / ".smc" / "ges-install-receipts"
        if d.is_dir():
            out.extend(d.glob("*.json"))
        for name in ("ges-install-receipt.json", "ges-install-lock.json"):
            p = self.r / ".smc" / name
            if p.is_file():
                out.append(p)
        return out

    def test_receipt_and_pointer_enter_transaction_records(self) -> None:
        fixture(self.r)
        shutil.copytree(ROOT / "domain-packs", self.r / ".agents/ges/domain-packs")
        profile = json.loads((ROOT / "consumers/generic.json").read_text(encoding="utf-8"))
        write(self.r, ".agents/ges/profile.json", json.dumps(profile))
        shutil.copytree(ROOT / "domain-runtime", self.r / ".agents/ges/domain-runtime")
        shutil.copytree(ROOT / ".agents/skills", self.r / ".agents/skills", dirs_exist_ok=True)
        _, loaded = installer.resolve_profile(self.r, None)
        _, packs = installer.pack_context(loaded)
        backup = self.r / ".smc" / "skill-upgrade-backups" / "tx-final"
        backup.mkdir(parents=True)
        records: dict = {}
        installer.build_install_lock(self.r, loaded, packs, records, backup)
        self.assertIn(".smc/ges-install-receipts/tx-final.json", records)
        self.assertIn(".smc/ges-install-receipt.json", records)
        self.assertTrue((self.r / ".smc/ges-install-receipts/tx-final.json").is_file())

    def test_r09_receipt_then_fault_restores(self) -> None:
        fixture(self.r)
        shutil.copytree(ROOT / "domain-packs", self.r / ".agents/ges/domain-packs")
        profile = json.loads((ROOT / "consumers/generic.json").read_text(encoding="utf-8"))
        write(self.r, ".agents/ges/profile.json", json.dumps(profile))
        shutil.copytree(ROOT / "domain-runtime", self.r / ".agents/ges/domain-runtime")
        shutil.copytree(ROOT / ".agents/skills", self.r / ".agents/skills", dirs_exist_ok=True)
        before = self._snapshot()
        _, loaded = installer.resolve_profile(self.r, None)
        _, packs = installer.pack_context(loaded)
        backup = self.r / ".smc" / "skill-upgrade-backups" / "tx-r09"
        backup.mkdir(parents=True)
        records: dict = {}
        installer._FINALIZATION_FAULT = "receipt"
        with self.assertRaises(RuntimeError):
            installer.build_install_lock(self.r, loaded, packs, records, backup)
        installer.base.restore(self.r, backup, records)
        self.assertFalse(any(p.exists() for p in self._receipt_paths()))
        after = self._snapshot()
        self.assertEqual(before, after)

    def test_r10_pointer_then_fault_restores(self) -> None:
        fixture(self.r)
        shutil.copytree(ROOT / "domain-packs", self.r / ".agents/ges/domain-packs")
        profile = json.loads((ROOT / "consumers/generic.json").read_text(encoding="utf-8"))
        write(self.r, ".agents/ges/profile.json", json.dumps(profile))
        shutil.copytree(ROOT / "domain-runtime", self.r / ".agents/ges/domain-runtime")
        shutil.copytree(ROOT / ".agents/skills", self.r / ".agents/skills", dirs_exist_ok=True)
        before = self._snapshot()
        _, loaded = installer.resolve_profile(self.r, None)
        _, packs = installer.pack_context(loaded)
        backup = self.r / ".smc" / "skill-upgrade-backups" / "tx-r10"
        backup.mkdir(parents=True)
        records: dict = {}
        installer._FINALIZATION_FAULT = "pointer"
        with self.assertRaises(RuntimeError):
            installer.build_install_lock(self.r, loaded, packs, records, backup)
        installer.base.restore(self.r, backup, records)
        self.assertFalse(any(p.exists() for p in self._receipt_paths()))
        self.assertEqual(before, self._snapshot())

    def test_before_lock_fault_full_install(self) -> None:
        fixture(self.r)
        shutil.copytree(ROOT / "domain-packs", self.r / ".agents/ges/domain-packs")
        profile = json.loads((ROOT / "consumers/generic.json").read_text(encoding="utf-8"))
        write(self.r, ".agents/ges/profile.json", json.dumps(profile))
        shutil.copytree(ROOT / "domain-runtime", self.r / ".agents/ges/domain-runtime")
        shutil.copytree(ROOT / ".agents/skills", self.r / ".agents/skills", dirs_exist_ok=True)
        before = self._snapshot()
        _, loaded = installer.resolve_profile(self.r, None)
        _, packs = installer.pack_context(loaded)
        backup = self.r / ".smc" / "skill-upgrade-backups" / "tx-before-lock"
        backup.mkdir(parents=True)
        records: dict = {}
        lock = installer.build_install_lock(self.r, loaded, packs, records, backup)
        installer._FINALIZATION_FAULT = "before_lock"
        installer._FAULT_TRIGGERED = False
        with self.assertRaises(RuntimeError):
            installer.write_text(
                self.r,
                self.r / ".smc/ges-install-lock.json",
                json.dumps(lock) + "\n",
                backup,
                records,
            )
        self.assertTrue(installer._FAULT_TRIGGERED)
        installer.base.restore(self.r, backup, records)
        self.assertFalse((self.r / ".smc/ges-install-lock.json").is_file())
        receipts = (
            list((self.r / ".smc/ges-install-receipts").glob("*.json"))
            if (self.r / ".smc/ges-install-receipts").is_dir()
            else []
        )
        self.assertEqual(receipts, [])
        self.assertFalse((self.r / ".smc/ges-install-receipt.json").is_file())
        self.assertEqual(before, self._snapshot())

    def test_duplicate_install_id_rejected(self) -> None:
        fixture(self.r)
        shutil.copytree(ROOT / "domain-packs", self.r / ".agents/ges/domain-packs")
        profile = json.loads((ROOT / "consumers/generic.json").read_text(encoding="utf-8"))
        write(self.r, ".agents/ges/profile.json", json.dumps(profile))
        shutil.copytree(ROOT / "domain-runtime", self.r / ".agents/ges/domain-runtime")
        shutil.copytree(ROOT / ".agents/skills", self.r / ".agents/skills", dirs_exist_ok=True)
        _, loaded = installer.resolve_profile(self.r, None)
        _, packs = installer.pack_context(loaded)
        backup = self.r / ".smc" / "skill-upgrade-backups" / "tx-dup"
        backup.mkdir(parents=True)
        records: dict = {}
        installer.build_install_lock(self.r, loaded, packs, records, backup)
        with self.assertRaises(RuntimeError) as ctx:
            installer.build_install_lock(self.r, loaded, packs, {}, backup)
        self.assertIn("INSTALL_RECEIPT_ALREADY_EXISTS", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
