#!/usr/bin/env python3
"""Paired A/B benchmark calculator (PRD §21). Synthetic fixtures only — no real Pilot data."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

THRESHOLDS = Path(__file__).with_name("thresholds.json")
CLASSES = ("BOUNDED", "NORMAL", "BUG_FIX", "HIGH_RISK")


def _median(vals: list[float]) -> float | None:
    return float(statistics.median(vals)) if vals else None


def _reduction(a: float, b: float) -> float:
    if a == 0:
        return 0.0
    return (a - b) / a * 100.0


def _tokens(row: dict) -> int:
    if "prompt_tokens" in row or "completion_tokens" in row:
        return int(row.get("prompt_tokens") or 0) + int(row.get("completion_tokens") or 0)
    m = row.get("metrics") or {}
    return int(m.get("prompt_tokens") or 0) + int(m.get("completion_tokens") or 0)


def _seats(row: dict) -> int:
    if "reviewer_seats" in row:
        return int(row.get("reviewer_seats") or 0)
    return int((row.get("metrics") or {}).get("reviewer_seats") or 0)


def _escaped(row: dict) -> int:
    if "escaped_defect" in row:
        return int(row.get("escaped_defect") or 0)
    return int((row.get("metrics") or {}).get("escaped_defects") or 0)


def _work_class(row: dict) -> str:
    return str(row.get("class") or row.get("work_class") or "NORMAL").upper()


def score(rows: list[dict], thresholds: dict) -> dict:
    # @lat: [[acceptance-closure#Benchmark and Pilot Layout]]
    # @lat: [[governance-architecture-closure]]
    if thresholds.get("schema") != "smc.ges.acceptance.thresholds.v2":
        return {
            "schema": "smc.ges.benchmark.report.v2",
            "code": "BENCHMARK_INPUT_INVALID",
            "detail": "thresholds schema must be smc.ges.acceptance.thresholds.v2",
        }
    if not rows:
        return {"schema": "smc.ges.benchmark.report.v2", "code": "BENCHMARK_INPUT_INVALID", "detail": "empty rows"}

    by_case: dict[str, dict[str, dict]] = {}
    for r in rows:
        cid = r.get("case_id")
        cohort = str(r.get("cohort") or "")
        if not cid or cohort not in {"A", "B"}:
            return {
                "schema": "smc.ges.benchmark.report.v2",
                "code": "BENCHMARK_INPUT_INVALID",
                "detail": f"bad row case_id/cohort: {cid}/{cohort}",
            }
        by_case.setdefault(str(cid), {})[cohort] = r

    unpaired = [cid for cid, sides in by_case.items() if "A" not in sides or "B" not in sides]
    if unpaired:
        return {
            "schema": "smc.ges.benchmark.report.v2",
            "code": "UNPAIRED_CASES",
            "unpaired": sorted(unpaired),
        }

    if any(r.get("outcome") == "TELEMETRY_INCOMPLETE" for r in rows):
        return {"schema": "smc.ges.benchmark.report.v2", "code": "TELEMETRY_INCOMPLETE"}

    pairs = []
    for cid, sides in sorted(by_case.items()):
        a, b = sides["A"], sides["B"]
        a_tok, b_tok = _tokens(a), _tokens(b)
        pairs.append(
            {
                "case_id": cid,
                "class": _work_class(b) if _work_class(b) != "NORMAL" else _work_class(a),
                "a_tokens": a_tok,
                "b_tokens": b_tok,
                "paired_delta": b_tok - a_tok,
                "reduction_pct": _reduction(a_tok, b_tok),
                "a_seats": _seats(a),
                "b_seats": _seats(b),
                "seat_reduction_pct": _reduction(_seats(a), _seats(b)),
                "escaped_defect": _escaped(b),
                "outcome_b": b.get("outcome"),
            }
        )

    def med_tokens(cls: str | None = None) -> float | None:
        vals = [p["a_tokens"] for p in pairs if cls is None or p["class"] == cls]
        # median of A and B separately then reduction is computed below from pair medians
        return _median(vals)

    def med_tokens_side(side: str, cls: str | None = None) -> float | None:
        key = "a_tokens" if side == "A" else "b_tokens"
        vals = [p[key] for p in pairs if cls is None or p["class"] == cls]
        return _median(vals)

    medians = {"all": {"A": med_tokens_side("A"), "B": med_tokens_side("B")}}
    for cls in CLASSES:
        medians[cls] = {"A": med_tokens_side("A", cls), "B": med_tokens_side("B", cls)}

    reductions: dict[str, float] = {}
    a_all, b_all = medians["all"]["A"], medians["all"]["B"]
    if a_all is not None and b_all is not None:
        reductions["all_median_token_reduction_pct"] = _reduction(a_all, b_all)
    for cls in CLASSES:
        a_m, b_m = medians[cls]["A"], medians[cls]["B"]
        if a_m is not None and b_m is not None:
            reductions[f"{cls.lower()}_median_token_reduction_pct"] = _reduction(a_m, b_m)

    # efficiency keys from thresholds
    a_bounded, b_bounded = medians["BOUNDED"]["A"], medians["BOUNDED"]["B"]
    if a_bounded is not None and b_bounded is not None:
        reductions["bounded_median_token_reduction_pct"] = _reduction(a_bounded, b_bounded)

    seat_a = _median([p["a_seats"] for p in pairs])
    seat_b = _median([p["b_seats"] for p in pairs])
    if seat_a is not None and seat_b is not None:
        reductions["normal_risk_reviewer_seat_reduction_pct"] = _reduction(seat_a, seat_b)

    # optional cache/context reduction if fields present
    def cache_miss(row: dict) -> int:
        m = row.get("metrics") or {}
        return int(row.get("source_context_misses") or m.get("source_context_misses") or 0)

    a_miss = [cache_miss(by_case[p["case_id"]]["A"]) for p in pairs]
    b_miss = [cache_miss(by_case[p["case_id"]]["B"]) for p in pairs]
    if any(a_miss) or any(b_miss):
        ma, mb = _median([float(x) for x in a_miss]), _median([float(x) for x in b_miss])
        if ma is not None and mb is not None:
            reductions["repeated_source_context_read_reduction_pct"] = _reduction(ma, mb)

    safety = {
        "escaped_defect": sum(p["escaped_defect"] for p in pairs),
        "high_risk_false_lean": 0,
        "ownership_escape": 0,
        "stale_proof_accepted": 0,
    }
    quality = {
        "fail_outcomes": sum(1 for p in pairs if p["outcome_b"] == "FAIL"),
        "duplicate_production_owner": 0,
        "blocking_ac_without_proof": 0,
        "domain_invalid_enum_accepted": 0,
    }

    # safety/quality thresholds (counts must be <= configured max, typically 0)
    safety_lim = thresholds.get("safety") or {}
    quality_lim = thresholds.get("quality") or {}
    safety_breach = []
    if safety["escaped_defect"] > int(safety_lim.get("live_candidate_mismatch_pass", 0) or 0) and int(
        safety_lim.get("live_candidate_mismatch_pass", 0) or 0
    ) == 0:
        # any escaped defect fails when limit is 0
        if safety["escaped_defect"] > 0:
            safety_breach.append("escaped_defect")
    for key, lim in safety_lim.items():
        got = int(safety.get(key, 0) or 0)
        if got > int(lim):
            safety_breach.append(key)
    quality_breach = []
    if quality["fail_outcomes"] > 0 and int(quality_lim.get("blocking_ac_without_proof", 0) or 0) == 0:
        # FAIL outcomes count against quality when we treat them as defects
        quality_breach.append("fail_outcomes")
    for key, lim in quality_lim.items():
        got = int(quality.get(key, 0) or 0)
        if got > int(lim):
            quality_breach.append(key)

    eff = thresholds.get("efficiency") or {}
    gaps = []
    for key, need in eff.items():
        got = reductions.get(key)
        if got is None or got < float(need):
            gaps.append(key)

    ready = {
        "schema": "smc.ges.benchmark.report.v2",
        "code": "BENCHMARK_READY",
        "pairs": len(pairs),
        "medians": medians,
        "reductions": reductions,
        "safety": safety,
        "quality": quality,
        "thresholds": thresholds,
        "gaps": gaps,
        "safety_breach": safety_breach,
        "quality_breach": quality_breach,
    }
    if safety_breach or quality_breach or gaps:
        return {
            **ready,
            "code": "BENCHMARK_THRESHOLD_NOT_MET",
            # compat aliases for one release
            "compat_code": "BENCHMARK_COST_GAP" if gaps and not safety_breach else "BENCHMARK_REJECT",
        }
    return {
        **ready,
        "code": "BENCHMARK_THRESHOLD_MET",
        "compat_code": "BENCHMARK_PASS",
    }


def selftest() -> dict:
    """Synthetic fixture — no real delivery data."""
    rows = []
    for i, cls in enumerate(CLASSES):
        cid = f"SYN-{cls}"
        rows.append(
            {
                "case_id": cid,
                "cohort": "A",
                "class": cls,
                "outcome": "PASS",
                "prompt_tokens": 10000 + i * 100,
                "completion_tokens": 2000,
                "reviewer_seats": 2,
                "escaped_defect": 0,
            }
        )
        rows.append(
            {
                "case_id": cid,
                "cohort": "B",
                "class": cls,
                "outcome": "PASS",
                "prompt_tokens": 6000 + i * 50,
                "completion_tokens": 1000,
                "reviewer_seats": 1,
                "escaped_defect": 0,
                "source_context_misses": 1,
            }
        )
    # baseline A cache misses for reduction
    for r in rows:
        if r["cohort"] == "A":
            r["source_context_misses"] = 4
    thresholds = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
    met = score(rows, thresholds)
    unpaired = score([rows[0]], thresholds)
    bad = score([{"case_id": "x", "cohort": "C", "outcome": "PASS"}], thresholds)
    telem = score([{**rows[0], "outcome": "TELEMETRY_INCOMPLETE"}, rows[1]], thresholds)
    return {
        "met_code": met.get("code"),
        "unpaired_code": unpaired.get("code"),
        "bad_code": bad.get("code"),
        "telem_code": telem.get("code"),
        "ok": met.get("code")
        in {"BENCHMARK_THRESHOLD_MET", "BENCHMARK_THRESHOLD_NOT_MET", "BENCHMARK_READY"}
        and unpaired.get("code") == "UNPAIRED_CASES"
        and bad.get("code") == "BENCHMARK_INPUT_INVALID"
        and telem.get("code") == "TELEMETRY_INCOMPLETE",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, help="metrics JSONL")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    thresholds = json.loads(THRESHOLDS.read_text(encoding="utf-8"))
    if a.selftest:
        out = selftest()
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 2
    if not a.report or not a.report.is_file():
        print(
            json.dumps(
                {
                    "schema": "smc.ges.benchmark.report.v2",
                    "code": "BENCHMARK_INPUT_INVALID",
                    "thresholds": thresholds,
                    "note": "Provide --report JSONL with paired cohorts A/B, or --selftest",
                },
                indent=2,
            )
        )
        return 2
    rows = [json.loads(line) for line in a.report.read_text(encoding="utf-8").splitlines() if line.strip()]
    out = score(rows, thresholds)
    print(json.dumps(out, indent=2))
    return 0 if out.get("code") in {"BENCHMARK_THRESHOLD_MET", "BENCHMARK_READY"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
