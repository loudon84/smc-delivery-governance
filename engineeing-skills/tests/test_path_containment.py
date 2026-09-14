#!/usr/bin/env python3
"""Shared path containment corpus for rollback + work-facts resolvers."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / ".agents/skills/smc-work-router/scripts"))

import rollback as rb  # noqa: E402
from path_containment import PathContainmentError, safe_repo_relative  # noqa: E402


class PathContainmentCorpus(unittest.TestCase):
    # @lat: [[safety-runtime-closure-v503]]

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / "a.md").write_text("x\n", encoding="utf-8", newline="\n")

    def test_both_reject_escape_corpus(self) -> None:
        bad = ["../x", "/etc/passwd", r"C:\Windows\x", r"\\server\share\x", "docs/./a.md", "docs//a.md", ""]
        for item in bad:
            with self.subTest(item=item):
                with self.assertRaises(rb.RollbackError):
                    rb.resolve_record_target(self.repo, item)
                with self.assertRaises(PathContainmentError):
                    safe_repo_relative(self.repo, item)

    def test_both_accept_safe(self) -> None:
        p1 = rb.resolve_record_target(self.repo, "docs/a.md")
        p2 = safe_repo_relative(self.repo, "docs/a.md")
        self.assertEqual(p1.resolve(), p2.resolve())


if __name__ == "__main__":
    unittest.main()
