#!/usr/bin/env python3
"""Pilot evidence layout verifier — fails closed when evidence incomplete."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = (
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


def verify(root: Path) -> dict:
    if not root.is_dir():
        return {"ok": False, "code": "PILOT_EVIDENCE_INCOMPLETE", "detail": str(root)}
    deliveries = [p for p in root.iterdir() if p.is_dir()]
    if len(deliveries) < 12:
        return {
            "ok": False,
            "code": "PILOT_EVIDENCE_INCOMPLETE",
            "detail": f"need>=12 deliveries got={len(deliveries)}",
        }
    missing = []
    for d in deliveries:
        for name in REQUIRED:
            if not (d / name).is_file():
                missing.append(f"{d.name}/{name}")
    if missing:
        return {"ok": False, "code": "PILOT_EVIDENCE_INCOMPLETE", "missing": missing[:20]}
    return {"ok": True, "code": "PILOT_EVIDENCE_PASS", "deliveries": len(deliveries)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path, nargs="?", default=Path("audit/ges/acceptance/candidate/pilots"))
    a = ap.parse_args()
    out = verify(a.path)
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
