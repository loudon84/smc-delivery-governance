#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUNTIME = ROOT / ".agents/ges/domain-runtime"
if not RUNTIME.is_dir():
    RUNTIME = ROOT / "domain-runtime"
sys.path.insert(0, str(RUNTIME))
from domain_table import (  # noqa: E402
    _token,
    apply_row_rules,
    validate_enum,
    validate_enum_or_na,
    validate_na_with_reason,
    validate_table,
)

REQ = [
    "Change ID",
    "Deployment Impact",
    "Compatibility",
    "Environment/Config",
    "Health",
    "Migration Order",
    "Rollback",
    "Live Verification",
]
IMPACT = {"NONE", "CONFIG_ONLY", "RESTART", "ROLLING_CHANGE", "TOPOLOGY_CHANGE", "IRREVERSIBLE"}
COMPAT = {"UNCHANGED", "BACKWARD_COMPATIBLE", "WINDOW_REQUIRED", "BREAKING"}
LIVE = {"NOT_REQUIRED", "STATIC", "SMOKE", "LIVE", "EXTERNAL"}


def _profile(path: Path) -> str:
    m = re.search(r"^governance_profile:\s*(\w+)", path.read_text(encoding="utf-8"), re.M)
    return (m.group(1) if m else "FULL").upper()


def semantic(row: dict[str, str], index: int) -> list[dict[str, str]]:
    errors = []
    errors.extend(validate_enum(row, "Deployment Impact", IMPACT, "OPS_PREPLAN", index))
    errors.extend(validate_enum(row, "Compatibility", COMPAT, "OPS_PREPLAN", index))
    errors.extend(validate_enum(row, "Live Verification", LIVE, "OPS_PREPLAN", index))
    impact = _token(row.get("Deployment Impact", ""))
    rollback = row.get("Rollback", "").strip()
    if impact != "NONE":
        if not rollback or _token(rollback) in {"N/A", "NA"}:
            if not rollback.upper().startswith("NOT_POSSIBLE"):
                errors.append(
                    {
                        "code": "OPS_PREPLAN_ROLLBACK_REQUIRED",
                        "detail": f"row={index} Rollback required when Deployment Impact != NONE",
                    }
                )
    if impact == "IRREVERSIBLE":
        if not rollback.upper().startswith("NOT_POSSIBLE:"):
            errors.append(
                {
                    "code": "OPS_PREPLAN_ROLLBACK_REQUIRED",
                    "detail": f"row={index} IRREVERSIBLE requires Rollback=NOT_POSSIBLE:<reason>",
                }
            )
        errors.extend(validate_na_with_reason(row, "Migration Order", "OPS_PREPLAN", index, allow_bare_na=False))
    return errors


def validate(p: Path):
    errors = validate_table(p, "Ops Design Intent", list(REQ), "OPS_PREPLAN")
    errors.extend(apply_row_rules(p, "Ops Design Intent", "OPS_PREPLAN", semantic))
    profile = _profile(p)
    text = p.read_text(encoding="utf-8")
    if profile == "LEAN" and re.search(r"\b(TOPOLOGY_CHANGE|IRREVERSIBLE|BREAKING|LIVE|EXTERNAL)\b", text, re.I):
        errors.append({"code": "OPS_PREPLAN_FULL_REQUIRED", "detail": "topology/irreversible/live signal"})
    return errors


val = validate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    errors = validate(a.path)
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
