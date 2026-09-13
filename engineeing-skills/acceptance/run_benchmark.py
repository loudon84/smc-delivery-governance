#!/usr/bin/env python3
"""Benchmark harness stub: requires telemetry completeness for scored cases."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

THRESHOLDS = Path(__file__).with_name("thresholds.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, help="optional metrics JSONL")
    a = ap.parse_args()
    thresholds = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
    if not a.report or not a.report.is_file():
        print(
            json.dumps(
                {
                    "schema": "smc.ges.benchmark.report.v1",
                    "code": "TELEMETRY_INCOMPLETE",
                    "thresholds": thresholds,
                    "note": "Provide --report with complete telemetry to score efficiency gates",
                },
                indent=2,
            )
        )
        return 2
    rows = [json.loads(line) for line in a.report.read_text(encoding="utf-8").splitlines() if line.strip()]
    incomplete = [r for r in rows if r.get("outcome") == "TELEMETRY_INCOMPLETE"]
    if incomplete:
        print(json.dumps({"code": "TELEMETRY_INCOMPLETE", "count": len(incomplete)}, indent=2))
        return 2
    print(json.dumps({"code": "BENCHMARK_READY", "cases": len(rows), "thresholds": thresholds}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
