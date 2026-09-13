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
from domain_table import apply_row_rules, validate_enum_or_na, validate_table  # noqa: E402

REQ = [
    "Change ID",
    "Owner",
    "Contract",
    "Data/Transaction",
    "Auth",
    "Idempotency/Concurrency",
    "Failure Semantics",
    "Observability",
]
CONTRACT = {"UNCHANGED", "COMPATIBLE_EXTEND", "BREAKING_CHANGE", "N/A", "NA"}
AUTH = {"UNCHANGED", "NONE", "MODIFY", "NEW_BOUNDARY", "N/A", "NA"}
DATA = {"NONE", "READ_ONLY", "WRITE", "TRANSACTIONAL", "MIGRATION", "N/A", "NA"}
IDEMP = {"NOT_APPLICABLE", "UNCHANGED", "REQUIRED", "MODIFIED", "N/A", "NA"}


def _profile(path: Path) -> str:
    m = re.search(r"^governance_profile:\s*(\w+)", path.read_text(encoding="utf-8"), re.M)
    return (m.group(1) if m else "FULL").upper()


def semantic(row: dict[str, str], index: int) -> list[dict[str, str]]:
    errors = []
    errors.extend(validate_enum_or_na(row, "Contract", CONTRACT, "BACKEND_PREPLAN", index))
    errors.extend(validate_enum_or_na(row, "Auth", AUTH, "BACKEND_PREPLAN", index))
    errors.extend(validate_enum_or_na(row, "Data/Transaction", DATA, "BACKEND_PREPLAN", index))
    errors.extend(validate_enum_or_na(row, "Idempotency/Concurrency", IDEMP, "BACKEND_PREPLAN", index))
    return errors


def validate(p: Path):
    errors = validate_table(p, "Backend Design Intent", list(REQ), "BACKEND_PREPLAN")
    errors.extend(apply_row_rules(p, "Backend Design Intent", "BACKEND_PREPLAN", semantic))
    profile = _profile(p)
    hard = False
    for err in list(errors):
        pass
    text = p.read_text(encoding="utf-8")
    if re.search(r"\b(BREAKING_CHANGE|NEW_BOUNDARY|MIGRATION)\b", text, re.I):
        hard = True
    if profile == "LEAN" and hard:
        errors.append({"code": "BACKEND_PREPLAN_FULL_REQUIRED", "detail": "breaking/auth/migration signal"})
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
