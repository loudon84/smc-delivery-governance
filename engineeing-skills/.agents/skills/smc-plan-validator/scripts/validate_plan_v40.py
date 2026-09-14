#!/usr/bin/env python3
"""GES Plan v4.0 validator: v3.7 invariants + required context_binding."""
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
from validate_plan_v37 import (  # noqa: E402
    domain_module,
    intent_binding_errors,
    ownership_errors,
    profile_errors,
)

ENGINE = HERE.parents[3] / "context-engine"
if not ENGINE.is_dir():
    ENGINE = HERE.parents[3] / ".agents" / "ges" / "context-engine"
sys.path.insert(0, str(ENGINE))
from contract import context_binding_errors  # noqa: E402


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
    errors = validate_plan(p, "smc.plan.v4.0")
    errors.extend(validate_acceptance(p))
    errors.extend(validate_test_assets(p))
    errors.extend(profile_errors(p))
    errors.extend(ownership_errors(p))
    errors.extend(intent_binding_errors(p))
    errors.extend(context_binding_errors(parse_top_level_frontmatter(p.read_text(encoding="utf-8"))))
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
        print("Plan v4.0 validation passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
