#!/usr/bin/env python3
"""Create smc.plan.v4.0 seed from the current v3.7 seed generator."""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
V37 = HERE / "create_plan_seed_v37.py"


def upgrade(text: str) -> str:
    text = text.replace("plan_contract: smc.plan.v3.7", "plan_contract: smc.plan.v4.0")
    if re.search(r"^context_binding\s*:", text, re.M) is None:
        text = re.sub(
            r"^(plan_contract:\s*smc\.plan\.v4\.0\s*)$",
            r"\1\ncontext_binding: required",
            text,
            count=1,
            flags=re.M,
        )
    if "## Context Binding" not in text:
        text = text.replace(
            "## Governance Profile",
            "## Context Binding\n\n- Package phase: `EXECUTION`\n- Enforcement mode: `ADVISORY`\n\n## Governance Profile",
            1,
        )
    return text


def _repo_root(path: Path) -> Path:
    for candidate in (path.resolve().parent, *path.resolve().parents):
        if (candidate / ".git").exists() or (candidate / ".agents" / "ges").is_dir():
            return candidate
    return path.resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("prd", type=Path, nargs="?")
    ap.add_argument("output", type=Path, nargs="?")
    known, passthrough = ap.parse_known_args()
    if known.prd is None or known.output is None:
        return subprocess.call([sys.executable, str(V37), *sys.argv[1:]])
    repo = _repo_root(known.prd)
    mid_dir = repo / ".smc" / "tmp-seed-v40"
    mid_dir.mkdir(parents=True, exist_ok=True)
    mid = mid_dir / "v37.plan.md"
    try:
        cmd = [sys.executable, str(V37), str(known.prd), str(mid), *passthrough]
        rc = subprocess.call(cmd)
        if rc != 0:
            return rc
        text = upgrade(mid.read_text(encoding="utf-8"))
        known.output.parent.mkdir(parents=True, exist_ok=True)
        known.output.write_text(text, encoding="utf-8", newline="\n")
    finally:
        shutil.rmtree(mid_dir, ignore_errors=True)
    print(f"PLAN_SEED_V40: {known.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
