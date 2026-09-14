#!/usr/bin/env python3
"""Path identity focused regressions (AC-02)."""
from __future__ import annotations

import unittest

from test_ac_suite import RegistryTests  # noqa: F401


class PathIdentityOnly(RegistryTests):
    def test_suite(self) -> None:
        self.test_ac02_path_identity_and_outside()


if __name__ == "__main__":
    unittest.main()
