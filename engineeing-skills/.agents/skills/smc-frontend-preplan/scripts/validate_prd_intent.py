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
    apply_row_rules,
    validate_enum_or_na,
    validate_table,
)

REQ = [
    "Change ID",
    "Surface",
    "Framework",
    "Layout",
    "Component Map",
    "State Ownership",
    "Interaction States",
    "Design System",
    "Responsive",
    "Visual Verification",
]
FRAMEWORKS = {"REACT", "VUE", "GENERIC", "N/A", "NA"}
VISUAL = {"STATIC", "COMPONENT", "INTERACTION", "LIVE_VISUAL", "N/A", "NA"}
ACTION = re.compile(r"\b(REUSE|EXTEND|NEW|REMOVE|N/A|NA)\b", re.I)
FULL_TRIGGERS = re.compile(
    r"new\s+page|layout\s+hierarchy|navigation\s+change|state\s+owner|responsive\s+architecture|"
    r"design-system\s+primitive|multi-panel|workspace\s+structure",
    re.I,
)


def _profile(path: Path) -> str:
    m = re.search(r"^governance_profile:\s*(\w+)", path.read_text(encoding="utf-8"), re.M)
    return (m.group(1) if m else "FULL").upper()


def semantic(row: dict[str, str], index: int) -> list[dict[str, str]]:
    errors = []
    errors.extend(validate_enum_or_na(row, "Framework", FRAMEWORKS, "FRONTEND_PREPLAN", index))
    errors.extend(validate_enum_or_na(row, "Visual Verification", VISUAL, "FRONTEND_PREPLAN", index))
    cmap = row.get("Component Map", "")
    if not ACTION.search(cmap):
        errors.append(
            {"code": "FRONTEND_PREPLAN_ENUM_INVALID", "detail": f"row={index} Component Map missing action token"}
        )
    if re.search(r"\bNEW\b", cmap, re.I):
        ds = row.get("Design System", "").strip()
        if not ds or ds.upper() in {"N/A", "NA", "-", "NONE"}:
            errors.append(
                {
                    "code": "FRONTEND_PREPLAN_CONDITIONAL_INVALID",
                    "detail": f"row={index} Design System required when Component Map includes NEW",
                }
            )
    return errors


def validate(p: Path):
    errors = validate_table(p, "Frontend Design Intent", list(REQ), "FRONTEND_PREPLAN")
    errors.extend(apply_row_rules(p, "Frontend Design Intent", "FRONTEND_PREPLAN", semantic))
    text = p.read_text(encoding="utf-8")
    if _profile(p) == "LEAN" and FULL_TRIGGERS.search(text):
        errors.append({"code": "FRONTEND_PREPLAN_FULL_REQUIRED", "detail": "layout/state/navigation trigger"})
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
