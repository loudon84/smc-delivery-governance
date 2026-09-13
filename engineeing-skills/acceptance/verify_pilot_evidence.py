#!/usr/bin/env python3
"""Deprecated shim — pilot evidence verification moved to acceptance/pilot/run_pilot.py."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "pilot"))
from run_pilot import summarize, validate_matrix  # noqa: E402


def verify(root: Path) -> dict:
    """Compat entry: summarize evidence layout + matrix contract."""
    matrix = validate_matrix()
    summary = summarize(root)
    return {
        "ok": bool(matrix.get("ok")) and bool(summary.get("ok")),
        "code": "PILOT_EVIDENCE_INCOMPLETE" if not summary.get("ok") else "PILOT_EVIDENCE_PASS",
        "status": "NOT_EXECUTED",
        "deprecated": "use acceptance/pilot/run_pilot.py",
        "matrix": matrix,
        "summary": summary,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path, nargs="?", default=Path("audit/ges/acceptance/candidate/pilots"))
    a = ap.parse_args()
    out = verify(a.path)
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
