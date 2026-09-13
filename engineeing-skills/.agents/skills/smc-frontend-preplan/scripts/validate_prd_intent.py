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
    parse_table,
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
LAYOUT = {"UNCHANGED", "EXTEND_EXISTING", "NEW_HIERARCHY", "NAVIGATION_CHANGE", "MULTI_PANEL", "N/A", "NA"}
COMPONENT = {"REUSE", "EXTEND", "NEW", "REMOVE", "N/A", "NA"}
STATE = {"UNCHANGED", "LOCAL_EXISTING", "EXTEND_OWNER", "NEW_OWNER", "STORE_CHANGE", "N/A", "NA"}
RESPONSIVE = {"UNCHANGED", "EXTEND", "ARCHITECTURE_CHANGE", "N/A", "NA"}
VISUAL = {"STATIC", "COMPONENT", "INTERACTION", "LIVE_VISUAL", "N/A", "NA"}
FULL_LAYOUT = {"NEW_HIERARCHY", "NAVIGATION_CHANGE", "MULTI_PANEL"}
FULL_STATE = {"NEW_OWNER", "STORE_CHANGE"}


def _profile(path: Path) -> str:
    m = re.search(r"^governance_profile:\s*(\w+)", path.read_text(encoding="utf-8"), re.M)
    return (m.group(1) if m else "FULL").upper()


def _component_token(raw: str) -> str:
    return _token(raw.split()[0] if raw.strip() else "")


def semantic(row: dict[str, str], index: int) -> list[dict[str, str]]:
    errors = []
    errors.extend(validate_enum_or_na(row, "Framework", FRAMEWORKS, "FRONTEND_PREPLAN", index))
    errors.extend(validate_enum_or_na(row, "Layout", LAYOUT, "FRONTEND_PREPLAN", index))
    errors.extend(validate_enum_or_na(row, "State Ownership", STATE, "FRONTEND_PREPLAN", index))
    errors.extend(validate_enum_or_na(row, "Responsive", RESPONSIVE, "FRONTEND_PREPLAN", index))
    errors.extend(validate_enum_or_na(row, "Visual Verification", VISUAL, "FRONTEND_PREPLAN", index))
    cmap = row.get("Component Map", "")
    ctok = _component_token(cmap)
    if ctok not in COMPONENT:
        # distinguish free-text new artifacts vs missing token
        if cmap.strip() and ctok not in {"", "N/A", "NA"}:
            errors.append(
                {"code": "DOMAIN_SEMANTIC_TOKEN_INVALID", "detail": f"row={index} Component Map={cmap}"}
            )
        else:
            errors.append(
                {"code": "FRONTEND_PREPLAN_ENUM_INVALID", "detail": f"row={index} Component Map missing action token"}
            )
    if ctok == "NEW":
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
    _, rows = parse_table(p, "Frontend Design Intent")
    if not rows and errors:
        # legacy free-text section without structured rows → fail closed
        text = p.read_text(encoding="utf-8")
        if "## Frontend Design Intent" in text:
            errors.append({"code": "DOMAIN_SEMANTIC_LEGACY_FULL_REQUIRED", "detail": "unstructured frontend intent"})
        return errors
    errors.extend(apply_row_rules(p, "Frontend Design Intent", "FRONTEND_PREPLAN", semantic))
    if _profile(p) == "LEAN":
        for index, row in enumerate(rows, 1):
            layout = _token(row.get("Layout", ""))
            state = _token(row.get("State Ownership", ""))
            responsive = _token(row.get("Responsive", ""))
            if layout in FULL_LAYOUT or state in FULL_STATE or responsive == "ARCHITECTURE_CHANGE":
                errors.append({"code": "FRONTEND_PREPLAN_FULL_REQUIRED", "detail": f"row={index} structured FULL trigger"})
                break
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
