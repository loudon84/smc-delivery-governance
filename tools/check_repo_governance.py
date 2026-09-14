#!/usr/bin/env python3
"""Read-only repository governance drift checker.

Compares live/evidence protection state against governance/github/master-ruleset.json.
Never holds admin write privileges. Token is read from env secrets only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIRED = ROOT / "governance" / "github" / "master-ruleset.json"
VERIFY = ROOT / "engineeing-skills" / "acceptance" / "verify_repository_protection.py"


def _load_normalize():
    # Reuse acceptance verifier normalization — no second parser.
    import importlib.util

    spec = importlib.util.spec_from_file_location("verify_repository_protection", VERIFY)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def load_desired(path: Path = DESIRED) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "smc.repo.ruleset.v1":
        raise ValueError("REPO_GOVERNANCE_UNAVAILABLE: desired schema")
    return data


def compare(desired: dict, actual: dict) -> tuple[str, list[str]]:
    """Return (REPO_GOVERNANCE_PASS|DRIFT|INVALID_EVIDENCE, problems)."""
    mod = _load_normalize()
    # Prefer strict evaluate on parsed evidence when available.
    if isinstance(actual.get("evidence"), dict) or actual.get("schema") == "smc.repo.protection-evidence.v1":
        code, problems = mod.evaluate(actual)
        return code, problems

    problems: list[str] = []
    # Fail closed on missing actual fields — never treat None as satisfied.
    if actual.get("protected") is not True:
        problems.append("master not protected" if actual.get("protected") is False else "protected field missing")
    if desired.get("require_pull_request") and actual.get("require_pr") is not True:
        problems.append("require_pr missing" if actual.get("require_pr") is None else "require_pr not true")
    want = set(desired.get("required_checks") or [])
    have = actual.get("required_checks")
    if have is None:
        problems.append("required_checks missing")
    else:
        have_set = set(have or [])
        for need in want:
            if need not in have_set and not any(need in c for c in have_set):
                problems.append(f"missing check: {need}")
    if desired.get("allow_force_push") is False and actual.get("force_push_blocked") is not True:
        problems.append(
            "force_push_blocked missing"
            if actual.get("force_push_blocked") is None
            else "force push not blocked"
        )
    if desired.get("allow_delete") is False and actual.get("deletion_blocked") is not True:
        problems.append(
            "deletion_blocked missing" if actual.get("deletion_blocked") is None else "deletion not blocked"
        )
    if desired.get("direct_update") == "restricted" and actual.get("direct_update_restricted") is not True:
        problems.append(
            "direct_update_restricted missing"
            if actual.get("direct_update_restricted") is None
            else "direct update not restricted"
        )
    if any("missing" in p for p in problems) and actual.get("protected") is True:
        return "REPO_GOVERNANCE_INVALID_EVIDENCE", problems
    return ("REPO_GOVERNANCE_PASS" if not problems else "REPO_GOVERNANCE_DRIFT", problems)


def main() -> int:
    # @lat: [[governance-architecture-closure]]
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--api", nargs=2, metavar=("OWNER", "REPO"))
    g.add_argument("--evidence", type=Path)
    ap.add_argument("--desired", type=Path, default=DESIRED)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        desired = load_desired(a.desired)
        mod = _load_normalize()
        actual = mod.from_api(*a.api) if a.api else mod.from_evidence(a.evidence)
    except Exception as exc:
        out = {
            "code": "REPO_GOVERNANCE_UNAVAILABLE",
            "detail": str(exc),
            "verifier_implementation": "PASS",
            "live_master_protection": "UNAVAILABLE",
        }
        print(json.dumps(out, indent=2) if a.json else out["code"])
        return 2
    code, problems = compare(desired, actual)
    live = "PASS" if code == "REPO_GOVERNANCE_PASS" else "DRIFT"
    if code == "REPO_GOVERNANCE_UNAVAILABLE":
        live = "UNAVAILABLE"
    out = {
        "code": code,
        "problems": problems,
        "actual": actual,
        "desired": desired,
        "verifier_implementation": "PASS",
        "live_master_protection": live,
    }
    print(json.dumps(out, indent=2) if a.json else code)
    return 0 if code == "REPO_GOVERNANCE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
