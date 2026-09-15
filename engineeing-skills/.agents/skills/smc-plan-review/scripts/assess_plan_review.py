"""GES 5 adaptive semantic Plan review router.

Public stdout remains NOT_REQUIRED|REQUIRED. --json exposes NONE|DELTA|FULL and reasons.
Precedence (v5.0.9 Runtime Cost Closure C09 overlays §8.2):
  1 prior REVISE without FULL re-entry → DELTA (cost default)
  1b prior unresolved non-PASS (non-REVISE) → FULL
  2 current structured contradiction/ambiguity → FULL
  3 current hard risk → FULL
  4 current risk facts missing/invalid where contract requires them → FULL
  5 fresh PASS bound to current semantic hash → NONE
  6 stale prior PASS + current low-risk (delta_eligible) → DELTA
  7 first LEAN + deterministic acceptance clearance → DELTA/LIGHT
  8 legacy low-risk compatible path → NONE
  9 unknown/FULL → FULL
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DELIVERY = Path(__file__).resolve().parents[2] / "smc-plan-delivery" / "scripts"
if str(DELIVERY) not in sys.path:
    sys.path.insert(0, str(DELIVERY))
from common import find_repo_root, parse_top_level_frontmatter, plan_id, semantic_plan_sha256  # noqa: E402
from review_record import latest_status  # noqa: E402

_PKG = Path(__file__).resolve().parents[4]
RUNTIME = _PKG / "domain-runtime"
if not RUNTIME.is_dir():
    RUNTIME = _PKG / ".agents" / "ges" / "domain-runtime"
if not RUNTIME.is_dir():
    RUNTIME = Path(__file__).resolve().parents[3] / "ges" / "domain-runtime"
sys.path.insert(0, str(RUNTIME))
from risk_signals import (  # noqa: E402
    acceptance_structure_clearance,
    parse_risk_snapshot,
    resolve_risk,
    structured_high_risk,
)

DEFAULT_FULL_CAP = 1
DEFAULT_DELTA_CAP = 2

FULL_REENTRY_KEYS = (
    "prd_semantic_hash_changed",
    "plan_scope_changed",
    "work_route_changed",
    "governance_profile_changed",
    "boundary_change",
    "owner_changed",
    "public_contract_changed",
    "feature_scope_changed",
)


def delta_eligible(
    status: str,
    rec: dict | None,
    snap_status: str,
    snapshot: dict | None,
    risk: dict,
    profile: str,
) -> tuple[bool, list[str]]:
    """PRD §8.3 six-way conjunction for STALE PASS → DELTA.

    ABSENT snapshot (legacy Plans) is treated as non-blocking completeness —
    INVALID or VALID+high-risk blocks DELTA.
    """
    reasons: list[str] = []
    if not (status == "STALE" and rec and str(rec.get("verdict", "")).upper() == "PASS"):
        reasons.append("PLAN_REVIEW_DELTA_INELIGIBLE:prior_not_stale_pass")
        return False, reasons
    if snap_status == "INVALID":
        reasons.append("PLAN_REVIEW_DELTA_INELIGIBLE:structured_facts_incomplete")
        return False, reasons
    if snap_status == "VALID" and isinstance(snapshot, dict):
        high, high_reasons = structured_high_risk(snapshot)
        if high:
            reasons.append("PLAN_REVIEW_DELTA_INELIGIBLE:current_high_risk")
            reasons.extend(high_reasons)
            return False, reasons
    if risk.get("errors"):
        real = [e for e in risk["errors"] if e.get("code") not in {"RISK_FACTS_MISSING"}]
        if real:
            reasons.append("PLAN_REVIEW_DELTA_INELIGIBLE:contradiction")
            return False, reasons
    return True, []


def _loop_path(plan: Path) -> Path:
    root = find_repo_root(plan)
    return root / ".smc" / "runs" / plan_id(plan) / "review" / "loop-accounting.json"


def load_loop_accounting(plan: Path) -> dict:
    path = _loop_path(plan)
    if not path.is_file():
        return {"schema": "smc.ges.review-loop.v1", "full_rounds": 0, "delta_rounds": 0}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": "smc.ges.review-loop.v1", "full_rounds": 0, "delta_rounds": 0}


def record_review_round(plan: Path, depth: str) -> dict:
    """Increment FULL/DELTA counters; raise REVIEW_LOOP_EXCEEDED when over cap."""
    data = load_loop_accounting(plan)
    d = (depth or "").upper()
    if d == "FULL":
        data["full_rounds"] = int(data.get("full_rounds") or 0) + 1
    elif d == "DELTA":
        data["delta_rounds"] = int(data.get("delta_rounds") or 0) + 1
    full_cap = int(data.get("full_cap") or DEFAULT_FULL_CAP)
    delta_cap = int(data.get("delta_cap") or DEFAULT_DELTA_CAP)
    data["full_cap"] = full_cap
    data["delta_cap"] = delta_cap
    if int(data.get("full_rounds") or 0) > full_cap or int(data.get("delta_rounds") or 0) > delta_cap:
        data["status"] = "REVIEW_LOOP_EXCEEDED"
        path = _loop_path(plan)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        raise ValueError("REVIEW_LOOP_EXCEEDED")
    data["status"] = "OK"
    path = _loop_path(plan)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data


def full_reentry_required(meta: dict, rec: dict | None) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    signals = meta.get("review_full_reentry") or meta.get("full_reentry_signals") or []
    if isinstance(signals, str):
        signals = [signals]
    if meta.get("review_full_reentry") in (True, "true", "TRUE", "yes"):
        reasons.append("explicit review_full_reentry")
        return True, reasons
    for key in FULL_REENTRY_KEYS:
        if key in signals or meta.get(key) in (True, "true", "TRUE"):
            reasons.append(key)
            return True, reasons
    if isinstance(rec, dict):
        for key in FULL_REENTRY_KEYS:
            if rec.get(key) in (True, "true", "TRUE") or key in (rec.get("full_reentry_signals") or []):
                reasons.append(key)
                return True, reasons
    return False, reasons


def classify(plan: Path) -> dict:
    # @lat: [[acceptance-closure#Plan Review Precedence]]
    # @lat: [[runtime-cost#Adaptive Plan Review]]
    # @lat: [[runtime-cost-closure-v509#Review Cost Closure]]
    # @lat: [[governance-architecture-closure]]
    text = plan.read_text(encoding="utf-8")
    meta = parse_top_level_frontmatter(text)
    profile = meta.get("governance_profile", "FULL").upper()
    snap_status, snapshot = parse_risk_snapshot(text)
    risk = resolve_risk(text, snapshot)
    contradictions = [e for e in risk.get("errors", []) if e.get("code") not in {"RISK_FACTS_MISSING"}]
    hard = [r for r in risk.get("reasons", []) if r not in {"RISK_FACTS_MISSING"}]
    if snap_status == "INVALID":
        hard = ["RISK_SNAPSHOT_INVALID"] + hard
    high, _ = structured_high_risk(snapshot) if snapshot else (False, [])
    risk_forces_full = bool(hard) or bool(contradictions) or high or snap_status == "INVALID"
    status, rec = latest_status(plan, "plan")
    contract_requires_facts = (
        meta.get("acceptance_contract") == "smc.acceptance.v1"
        or meta.get("plan_contract") == "smc.plan.v3.7"
    )
    facts_missing_where_required = contract_requires_facts and (
        snap_status == "INVALID"
        or (
            snap_status == "ABSENT"
            and not (
                status == "STALE"
                and rec
                and str(rec.get("verdict", "")).upper() == "PASS"
            )
        )
    )
    reasons: list[str] = []
    loop = load_loop_accounting(plan)
    if loop.get("status") == "REVIEW_LOOP_EXCEEDED":
        return {
            "schema": "smc.plan.review-route.v3",
            "plan": str(plan),
            "plan_sha256": semantic_plan_sha256(plan),
            "governance_profile": profile,
            "route": "REQUIRED",
            "depth": "FULL",
            "reasons": ["REVIEW_LOOP_EXCEEDED", "PLAN_REVISE_REQUIRED"],
            "hard_signals": hard,
            "risk_mode": risk.get("mode"),
            "snapshot_status": snap_status,
            "loop": loop,
        }

    reentry, reentry_reasons = full_reentry_required(meta, rec)
    prior_verdict = str(rec.get("verdict", "")).upper() if rec else ""

    # 1 prior REVISE → DELTA unless FULL re-entry (v5.0.9 C09)
    if rec and prior_verdict == "REVISE" and not reentry and not risk_forces_full:
        depth = "DELTA"
        reasons.append("prior REVISE defaults to DELTA review")
    elif rec and prior_verdict == "REVISE" and reentry:
        depth = "FULL"
        reasons.append("FULL re-entry after REVISE")
        reasons.extend(reentry_reasons)
    # 1b prior unresolved/non-PASS (non-REVISE)
    elif rec and prior_verdict != "PASS":
        depth = "FULL"
        reasons.append("latest prior review is unresolved, regardless of freshness")
    # 2 fresh PASS bound to current semantic hash
    elif status == "FRESH_PASS":
        depth = "NONE"
        reasons.append("fresh content-bound Plan review already PASS")
    # 3 current structured contradiction/ambiguity
    elif contradictions:
        depth = "FULL"
        reasons.append("PLAN_REVIEW_CURRENT_RISK_FULL_REQUIRED")
        reasons.append("PLAN_REVIEW_HARD_RISK_FULL_REQUIRED")
        reasons.extend(e.get("code", "contradiction") for e in contradictions)
    # 4 current hard risk
    elif risk_forces_full:
        depth = "FULL"
        reasons.append("PLAN_REVIEW_CURRENT_RISK_FULL_REQUIRED")
        reasons.append("PLAN_REVIEW_HARD_RISK_FULL_REQUIRED")
        reasons.extend("hard-risk:" + str(x) for x in hard)
    # 5 current risk facts missing/invalid where contract requires them
    elif facts_missing_where_required:
        depth = "FULL"
        reasons.append("PLAN_REVIEW_CURRENT_RISK_FULL_REQUIRED")
        reasons.append(f"risk_facts_{snap_status.lower()}_where_required")
    # 6 stale prior PASS + current low-risk
    elif status == "STALE" and rec and prior_verdict == "PASS":
        ok, delta_reasons = delta_eligible(status, rec, snap_status, snapshot, risk, profile)
        if ok:
            depth = "DELTA"
            reasons.append("prior PASS exists but semantic Plan changed")
        else:
            depth = "FULL"
            reasons.extend(delta_reasons or ["PLAN_REVIEW_DELTA_INELIGIBLE"])
    elif status.startswith("FRESH_") and status != "FRESH_PASS":
        depth = "FULL"
        reasons.append("prior review verdict was not PASS")
    # 7 first LEAN + deterministic acceptance clearance
    elif meta.get("acceptance_contract") == "smc.acceptance.v1":
        clear, clear_reasons = acceptance_structure_clearance(text, snapshot)
        if profile == "LEAN" and clear and not risk_forces_full:
            depth = "DELTA"
            reasons.append("LIGHT_FIRST_REVIEW: deterministic acceptance structure clearance")
        else:
            depth = "FULL"
            reasons.append("first acceptance-governed review requires actual semantic review")
            reasons.extend(clear_reasons)
    # 8 legacy low-risk compatible path
    elif profile == "LEAN" or meta.get("plan_contract") in {
        "smc.plan.v3.3",
        "smc.plan.v3.4",
        "smc.plan.v3.5",
        "smc.plan.v3.6",
    }:
        depth = "NONE"
        reasons.append("low-risk Plan with no prior blocking semantic trigger")
    # 9 unknown/FULL
    else:
        depth = "FULL"
        reasons.append("FULL/unknown Plan fails closed to full semantic review")

    public = "NOT_REQUIRED" if depth == "NONE" else "REQUIRED"
    return {
        "schema": "smc.plan.review-route.v3",
        "plan": str(plan),
        "plan_sha256": semantic_plan_sha256(plan),
        "governance_profile": profile,
        "route": public,
        "depth": depth,
        "reasons": reasons,
        "hard_signals": hard,
        "risk_mode": risk.get("mode"),
        "snapshot_status": snap_status,
        "loop": loop,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    p = a.plan.resolve()
    if not p.is_file():
        print(f"PLAN_NOT_FOUND: {p}", file=sys.stderr)
        return 2
    o = classify(p)
    print(json.dumps(o, ensure_ascii=False, indent=2, sort_keys=True) if a.json else o["route"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
