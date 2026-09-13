#!/usr/bin/env python3
"""Benchmark aggregator: median/reduction vs thresholds; never invents cohort A."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

THRESHOLDS = Path(__file__).with_name("thresholds.json")


def _median(vals: list[float]) -> float | None:
    return float(statistics.median(vals)) if vals else None


def _reduction(a: float, c: float) -> float:
    if a == 0:
        return 0.0
    return (a - c) / a * 100.0


def score(rows: list[dict], thresholds: dict) -> dict:
    # @lat: [[acceptance-closure#Benchmark and Pilot Layout]]
    by_cohort: dict[str, list[dict]] = {"A": [], "B": [], "C": []}
    for r in rows:
        by_cohort.setdefault(str(r.get("cohort")), []).append(r)
    if any(r.get("outcome") == "TELEMETRY_INCOMPLETE" for r in rows):
        return {"code": "TELEMETRY_INCOMPLETE", "schema": "smc.ges.benchmark.report.v1"}
    if not by_cohort["A"]:
        return {
            "code": "BENCHMARK_BASELINE_NOT_REPRODUCIBLE",
            "schema": "smc.ges.benchmark.report.v1",
            "detail": "cohort A (GES 4.4.1) missing",
        }
    if not by_cohort["C"]:
        return {"code": "BENCHMARK_REJECT", "detail": "cohort C missing"}

    def tokens(row: dict) -> int:
        m = row.get("metrics") or {}
        return int(m.get("prompt_tokens") or 0) + int(m.get("completion_tokens") or 0)

    def seats(row: dict) -> int:
        return int((row.get("metrics") or {}).get("reviewer_seats") or 0)

    a_tok = [tokens(r) for r in by_cohort["A"] if (r.get("work_class") or "").upper() == "BOUNDED"]
    c_tok = [tokens(r) for r in by_cohort["C"] if (r.get("work_class") or "").upper() == "BOUNDED"]
    a_seat = [seats(r) for r in by_cohort["A"]]
    c_seat = [seats(r) for r in by_cohort["C"]]
    med_a, med_c = _median(a_tok), _median(c_tok)
    seat_a, seat_c = _median(a_seat), _median(c_seat)
    eff = thresholds.get("efficiency", {})
    safety_fail = any(
        int((r.get("metrics") or {}).get("escaped_defects") or 0) > 0 for r in by_cohort["C"]
    )
    quality_fail = any(r.get("outcome") == "FAIL" for r in by_cohort["C"])
    reductions = {}
    if med_a is not None and med_c is not None:
        reductions["bounded_median_token_reduction_pct"] = _reduction(med_a, med_c)
    if seat_a is not None and seat_c is not None:
        reductions["normal_risk_reviewer_seat_reduction_pct"] = _reduction(seat_a, seat_c)
    if safety_fail or quality_fail:
        return {
            "code": "BENCHMARK_REJECT",
            "schema": "smc.ges.benchmark.report.v1",
            "reductions": reductions,
            "reason": "safety_or_quality_fail",
        }
    gaps = []
    for key, need in eff.items():
        got = reductions.get(key)
        if got is None or got < float(need):
            gaps.append(key)
    if gaps:
        return {
            "code": "BENCHMARK_COST_GAP",
            "schema": "smc.ges.benchmark.report.v1",
            "reductions": reductions,
            "gaps": gaps,
            "thresholds": thresholds,
        }
    return {
        "code": "BENCHMARK_PASS",
        "schema": "smc.ges.benchmark.report.v1",
        "reductions": reductions,
        "thresholds": thresholds,
        "cases": len(rows),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, help="metrics JSONL")
    a = ap.parse_args()
    thresholds = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
    if not a.report or not a.report.is_file():
        print(
            json.dumps(
                {
                    "schema": "smc.ges.benchmark.report.v1",
                    "code": "BENCHMARK_BASELINE_NOT_REPRODUCIBLE",
                    "thresholds": thresholds,
                    "note": "Provide --report JSONL with cohorts A/B/C",
                },
                indent=2,
            )
        )
        return 2
    rows = [json.loads(line) for line in a.report.read_text(encoding="utf-8").splitlines() if line.strip()]
    out = score(rows, thresholds)
    print(json.dumps(out, indent=2))
    return 0 if out.get("code") == "BENCHMARK_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
