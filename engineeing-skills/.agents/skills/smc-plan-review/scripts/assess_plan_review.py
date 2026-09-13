#!/usr/bin/env python3
"""GES 5 adaptive semantic Plan review router.

Public stdout remains NOT_REQUIRED|REQUIRED. --json exposes NONE|DELTA|FULL and reasons.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DELIVERY = Path(__file__).resolve().parents[2] / "smc-plan-delivery" / "scripts"
if str(DELIVERY) not in sys.path:
    sys.path.insert(0, str(DELIVERY))
from common import parse_top_level_frontmatter, semantic_plan_sha256  # noqa: E402
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
    extract_risk_snapshot,
    resolve_risk,
)


def classify(plan: Path) -> dict:
    text = plan.read_text(encoding="utf-8")
    meta = parse_top_level_frontmatter(text)
    profile = meta.get("governance_profile", "FULL").upper()
    snapshot = extract_risk_snapshot(text)
    risk = resolve_risk(text, snapshot)
    # Missing snapshot alone is conservative metadata, not a hard semantic trigger.
    # Affirmative text / structured true / contradictions still force FULL.
    hard = [r for r in risk.get("reasons", []) if r != "RISK_FACTS_MISSING"]
    risk_forces_full = bool(hard) or any(
        e.get("code") not in {"RISK_FACTS_MISSING"} for e in risk.get("errors", [])
    )
    status, rec = latest_status(plan, "plan")
    reasons: list[str] = []

    if rec and str(rec.get("verdict", "")).upper() != "PASS":
        depth = "FULL"
        reasons.append("latest prior review is unresolved, regardless of freshness")
    elif status == "FRESH_PASS":
        depth = "NONE"
        reasons.append("fresh content-bound Plan review already PASS")
    elif status == "STALE" and rec and str(rec.get("verdict", "")).upper() == "PASS":
        depth = "DELTA"
        reasons.append("prior PASS exists but semantic Plan changed")
    elif risk_forces_full:
        depth = "FULL"
        reasons.extend("hard-risk:" + str(x) for x in hard)
    elif status.startswith("FRESH_") and status != "FRESH_PASS":
        depth = "FULL"
        reasons.append("prior review verdict was not PASS")
    elif meta.get("acceptance_contract") == "smc.acceptance.v1":
        clear, clear_reasons = acceptance_structure_clearance(text, snapshot)
        if profile == "LEAN" and clear and not risk_forces_full:
            depth = "DELTA"
            reasons.append("LIGHT_FIRST_REVIEW: deterministic acceptance structure clearance")
        else:
            depth = "FULL"
            reasons.append("first acceptance-governed review requires actual semantic review")
            reasons.extend(clear_reasons)
    elif profile == "LEAN" or meta.get("plan_contract") in {
        "smc.plan.v3.3",
        "smc.plan.v3.4",
        "smc.plan.v3.5",
        "smc.plan.v3.6",
    }:
        depth = "NONE"
        reasons.append("low-risk Plan with no prior blocking semantic trigger")
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
