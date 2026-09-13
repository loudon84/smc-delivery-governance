#!/usr/bin/env python3
"""Pilot matrix/result contract runner — specification only; no real Consumer execution."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MATRIX = HERE / "pilot-matrix.json"
CONSUMERS = {"Frontend", "Backend", "Ops"}
CLASSES = {"LEAN", "BEHAVIOR_CHANGE", "BUG_FIX", "HIGH_RISK"}
STATUSES = {"NOT_EXECUTED", "NOT_PROVEN", "PASS", "FAIL", "BLOCKED"}

# Legacy evidence filenames from verify_pilot_evidence (kept for summarize of future dirs)
REQUIRED_EVIDENCE = (
    "route_summary.json",
    "authority_digest.json",
    "prd_review.json",
    "domain_intent.json",
    "plan_review_depth.json",
    "engineering_method.json",
    "telemetry_summary.json",
    "completion_audit.json",
    "implementation_review.json",
    "blocking_verification.json",
    "implementation_commit.json",
    "roadmap_done_commit.json",
    "post_delivery_observation.json",
)


def validate_matrix(path: Path = MATRIX) -> dict:
    # @lat: [[governance-architecture-closure]]
    data = json.loads(path.read_text(encoding="utf-8"))
    slots = data.get("slots") or []
    errors = []
    if data.get("schema") != "smc.ges.pilot.matrix.v1":
        errors.append("PILOT_MATRIX_SCHEMA_INVALID")
    if len(slots) != 12:
        errors.append(f"PILOT_MATRIX_SLOT_COUNT:{len(slots)}")
    seen = set()
    for s in slots:
        key = (s.get("consumer"), s.get("class"))
        if key in seen:
            errors.append(f"PILOT_MATRIX_DUP:{key}")
        seen.add(key)
        if s.get("consumer") not in CONSUMERS:
            errors.append(f"PILOT_MATRIX_CONSUMER:{s.get('consumer')}")
        if s.get("class") not in CLASSES:
            errors.append(f"PILOT_MATRIX_CLASS:{s.get('class')}")
        if s.get("status") not in STATUSES:
            errors.append(f"PILOT_MATRIX_STATUS:{s.get('status')}")
    expected = {(c, k) for c in CONSUMERS for k in CLASSES}
    if seen != expected:
        errors.append("PILOT_MATRIX_COVERAGE_INCOMPLETE")
    if errors:
        return {"ok": False, "code": "PILOT_MATRIX_INVALID", "errors": errors, "status": "NOT_EXECUTED"}
    return {
        "ok": True,
        "code": "PILOT_MATRIX_VALID",
        "slots": 12,
        "status": data.get("status") or "NOT_EXECUTED",
    }


def validate_result(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    if data.get("schema") and data.get("schema") != "smc.ges.pilot.result.v1":
        errors.append("PILOT_RESULT_SCHEMA_INVALID")
    for key in ("slot_id", "consumer", "class", "status"):
        if key not in data:
            errors.append(f"PILOT_RESULT_MISSING:{key}")
    if data.get("consumer") not in CONSUMERS:
        errors.append("PILOT_RESULT_CONSUMER")
    if data.get("class") not in CLASSES:
        errors.append("PILOT_RESULT_CLASS")
    if data.get("status") not in STATUSES:
        errors.append("PILOT_RESULT_STATUS")
    if errors:
        return {"ok": False, "code": "PILOT_RESULT_INVALID", "errors": errors}
    return {"ok": True, "code": "PILOT_RESULT_VALID", "slot_id": data.get("slot_id"), "status": data.get("status")}


def summarize(results_dir: Path) -> dict:
    """Summarize result JSON files and/or legacy evidence layout. Never executes pilots."""
    if not results_dir.is_dir():
        return {"ok": False, "code": "PILOT_EVIDENCE_INCOMPLETE", "detail": str(results_dir), "status": "NOT_EXECUTED"}
    results = list(results_dir.glob("*.json"))
    deliveries = [p for p in results_dir.iterdir() if p.is_dir()]
    by_status: dict[str, int] = {}
    for rp in results:
        try:
            data = json.loads(rp.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        st = str(data.get("status") or "UNKNOWN")
        by_status[st] = by_status.get(st, 0) + 1
    missing = []
    for d in deliveries:
        for name in REQUIRED_EVIDENCE:
            if not (d / name).is_file():
                missing.append(f"{d.name}/{name}")
    status = "NOT_EXECUTED"
    if results and all(st in {"PASS"} for st in by_status) and len(results) >= 12:
        status = "PASS"
    elif by_status.get("FAIL") or by_status.get("BLOCKED"):
        status = "NOT_PROVEN"
    return {
        "ok": len(missing) == 0 and (not deliveries or len(deliveries) >= 12),
        "code": "PILOT_SUMMARY",
        "status": status,
        "result_files": len(results),
        "deliveries": len(deliveries),
        "by_status": by_status,
        "missing_evidence_sample": missing[:20],
        "matrix": validate_matrix(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Pilot contract tools (no real execution)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--validate-matrix", action="store_true")
    g.add_argument("--validate-result", type=Path)
    g.add_argument("--summarize", type=Path)
    a = ap.parse_args()
    if a.validate_matrix:
        out = validate_matrix()
    elif a.validate_result:
        out = validate_result(a.validate_result)
    else:
        out = summarize(a.summarize)
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
