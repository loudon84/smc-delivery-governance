#!/usr/bin/env python3
"""GES Plan v3.7 validator: v3.6 invariants + adaptive governance profile."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DELIVERY = HERE.parents[1] / "smc-plan-delivery" / "scripts"
sys.path.insert(0, str(DELIVERY))
from acceptance import validate_contract as validate_acceptance  # noqa: E402
from common import parse_top_level_frontmatter  # noqa: E402
from test_assets import validate_plan as validate_test_assets  # noqa: E402
from validate_plan_v33 import validate_plan  # noqa: E402

RUNTIME = HERE.parents[3] / "domain-runtime"
if not RUNTIME.is_dir():
    RUNTIME = HERE.parents[3] / ".agents" / "ges" / "domain-runtime"
sys.path.insert(0, str(RUNTIME))
from risk_signals import extract_risk_snapshot, resolve_risk  # noqa: E402


def repo_root(plan: Path) -> Path:
    for c in (plan.resolve().parent, *plan.resolve().parents):
        if (c / ".agents").is_dir() or (c / ".git").exists():
            return c
    raise ValueError("DOMAIN_REPO_ROOT_NOT_FOUND")


def domain_module(plan: Path):
    t = repo_root(plan) / ".agents/ges/domain-runtime/domain_runtime.py"
    if not t.is_file():
        raise ValueError(f"DOMAIN_RUNTIME_MISSING: {t}")
    s = importlib.util.spec_from_file_location("ges_domain_runtime_v37", t)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def profile_errors(plan: Path) -> list[dict[str, str]]:
    text = plan.read_text(encoding="utf-8")
    meta = parse_top_level_frontmatter(text)
    errs: list[dict[str, str]] = []
    profile = meta.get("governance_profile", "").upper()
    if profile not in {"LEAN", "FULL"}:
        errs.append({"code": "PLAN_GOVERNANCE_PROFILE_INVALID", "detail": profile or "missing"})
        return errs
    snapshot = extract_risk_snapshot(text)
    risk = resolve_risk(text, snapshot)
    if profile == "LEAN" and risk["high_risk"]:
        errs.append({"code": "PLAN_LEAN_FULL_REQUIRED", "detail": ",".join(risk["reasons"])})
    for err in risk.get("errors", []):
        if err["code"] in {"RISK_FACT_CONTRADICTION", "RISK_TEXT_AMBIGUOUS"}:
            errs.append(err)
        if snapshot is None and profile == "LEAN":
            # Old plans without snapshot: conservative legacy fallback already sets high_risk.
            pass
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    p = a.plan.resolve()
    if not p.is_file():
        out = {"valid": False, "plan": str(p), "errors": [{"code": "PLAN_NOT_FOUND", "detail": str(p)}]}
        print(json.dumps(out, indent=2) if a.json else f"PLAN_NOT_FOUND: {p}")
        return 2
    errors = validate_plan(p, "smc.plan.v3.7")
    errors.extend(validate_acceptance(p))
    errors.extend(validate_test_assets(p))
    errors.extend(profile_errors(p))
    try:
        errors.extend(domain_module(p).validate_plan(p))
    except ValueError as e:
        errors.append({"code": str(e).split(":", 1)[0], "detail": str(e)})
    out = {"valid": not errors, "plan": str(p), "errors": errors}
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    elif errors:
        print("\n".join(f"{x['code']}: {x['detail']}" for x in errors), file=sys.stderr)
    else:
        print("Plan v3.7 validation passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
