#!/usr/bin/env python3
"""Greenfield install preflight: managed paths + optional consumer seed."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import install_v500 as installer  # noqa: E402


def write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


class GreenfieldInstallTests(unittest.TestCase):
    # @lat: [[install#Consumer Baseline Seed]]

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.r = Path(self.tmp.name)
        installer.base.SEED_CONSUMER_SKILLS = False
        subprocess.run(["git", "init", "-q", str(self.r)], check=True)
        write(self.r, "AGENTS.md", "# Project policy\n")
        (self.r / ".agents/skills").mkdir(parents=True)

    def tearDown(self) -> None:
        installer.base.SEED_CONSUMER_SKILLS = False
        self.tmp.cleanup()

    def _names(self):
        _, profile = installer.resolve_profile(self.r, "generic")
        _, selected = installer.pack_context(profile)
        return profile, selected, installer.base.managed_skills(profile, selected)

    def test_preflight_blocks_missing_consumer_skills(self) -> None:
        profile, selected, names = self._names()
        errors = installer.preflight(self.r, profile, selected, names)
        self.assertTrue(any(e.startswith("CONSUMER_REQUIRED_SKILL_MISSING:") for e in errors))
        self.assertFalse(any("smc-plan-validator" in e for e in errors))

    def test_seed_flag_clears_consumer_preflight(self) -> None:
        installer.base.SEED_CONSUMER_SKILLS = True
        profile, selected, names = self._names()
        errors = installer.preflight(self.r, profile, selected, names)
        self.assertEqual(errors, [])

    def test_seed_never_overwrites_existing(self) -> None:
        write(self.r, ".agents/skills/code-review-and-quality/SKILL.md", "# keep-me\n")
        write(self.r, ".agents/skills/verification-before-completion/SKILL.md", "# keep-v\n")
        installer.base.SEED_CONSUMER_SKILLS = True
        backup = self.r / ".smc/skill-upgrade-backups/tx"
        backup.mkdir(parents=True)
        records: dict = {}
        installer.seed_consumer_skills(self.r, backup, records)
        self.assertEqual(
            (self.r / ".agents/skills/code-review-and-quality/SKILL.md").read_text(encoding="utf-8"),
            "# keep-me\n",
        )
        self.assertEqual(records, {})

    def test_seed_copies_missing_from_baseline(self) -> None:
        installer.base.SEED_CONSUMER_SKILLS = True
        backup = self.r / ".smc/skill-upgrade-backups/tx"
        backup.mkdir(parents=True)
        records: dict = {}
        count = installer.seed_consumer_skills(self.r, backup, records)
        self.assertGreater(count, 0)
        self.assertTrue((self.r / ".agents/skills/code-review-and-quality/SKILL.md").is_file())
        self.assertTrue((self.r / ".agents/skills/verification-before-completion/SKILL.md").is_file())


if __name__ == "__main__":
    raise SystemExit(unittest.main())
