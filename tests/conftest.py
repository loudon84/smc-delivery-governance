from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

SOURCE_ROOT = Path(__file__).resolve().parents[1]

# @lat: [[ADR-011-test-isolation#ADR-011 — Tests Must Not Mutate Central SOT]]
@pytest.fixture
def governance_sandbox(tmp_path):
    root = tmp_path / "governance"
    root.mkdir()
    for rel in [
        "registry", "features", "contracts", "integration", "schemas",
        "skills", "templates", "examples", "audit",
    ]:
        src = SOURCE_ROOT / rel
        if src.exists():
            shutil.copytree(src, root / rel)
    # dist/.cache intentionally omitted: every test must build/fetch its own kit.
    env = os.environ.copy()
    env["SMC_GOVERNANCE_ROOT"] = str(root)
    return root, env
