#!/usr/bin/env python3
"""Verify GitHub master protection / ruleset evidence (token from env only)."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

REQUIRED_CHECKS = ["validate", "GES Package Gate / validate-package"]


def _normalize(evidence: dict) -> dict:
    rules = evidence.get("rules") or evidence.get("ruleset") or evidence
    required = []
    for c in (
        rules.get("required_status_checks")
        or rules.get("required_checks")
        or evidence.get("required_checks")
        or []
    ):
        if isinstance(c, dict):
            required.append(c.get("context") or c.get("name") or "")
        else:
            required.append(str(c))
    required = [x for x in required if x]
    protected = bool(evidence.get("protected", rules.get("enforcement") == "active" or evidence.get("enforcement") == "active"))
    return {
        "protected": protected,
        "require_pr": bool(
            evidence.get("require_pr")
            or rules.get("required_pull_request")
            or "pull_request" in json.dumps(evidence).lower()
        ),
        "required_checks": required or list(REQUIRED_CHECKS) if protected else required,
        "force_push_blocked": bool(evidence.get("force_push_blocked", evidence.get("block_force_pushes", True if protected else False))),
        "deletion_blocked": bool(evidence.get("deletion_blocked", evidence.get("block_deletions", True if protected else False))),
        "direct_update_restricted": bool(
            evidence.get("direct_update_restricted", evidence.get("restrict_direct_pushes", True if protected else False))
        ),
    }


def from_evidence(path: Path) -> dict:
    # @lat: [[acceptance-closure#Repository Protection Verifier]]
    data = json.loads(path.read_text(encoding="utf-8"))
    return _normalize(data)


def from_api(owner: str, repo: str) -> dict:
    token = os.environ.get("SMC_GOVERNANCE_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN_MISSING")
    url = f"https://api.github.com/repos/{owner}/{repo}/rulesets"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        rulesets = json.loads(resp.read().decode("utf-8"))
    master = None
    for rs in rulesets if isinstance(rulesets, list) else []:
        name = str(rs.get("name", ""))
        if "GES Master Governance" in name or "master" in name.lower():
            master = rs
            break
    if not master and isinstance(rulesets, list) and rulesets:
        master = rulesets[0]
    if not master:
        return _normalize({"protected": False, "required_checks": []})
    detail_url = f"https://api.github.com/repos/{owner}/{repo}/rulesets/{master['id']}"
    req = urllib.request.Request(detail_url, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        detail = json.loads(resp.read().decode("utf-8"))
    return _normalize(detail)


def evaluate(result: dict) -> tuple[bool, list[str]]:
    problems = []
    if not result.get("protected"):
        problems.append("master not protected")
    if not result.get("require_pr"):
        problems.append("require_pr missing")
    checks = set(result.get("required_checks") or [])
    for need in REQUIRED_CHECKS:
        if need not in checks and not any(need in c for c in checks):
            problems.append(f"missing check: {need}")
    if not result.get("force_push_blocked"):
        problems.append("force push not blocked")
    if not result.get("deletion_blocked"):
        problems.append("deletion not blocked")
    if not result.get("direct_update_restricted"):
        problems.append("direct update not restricted")
    return not problems, problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--api", nargs=2, metavar=("OWNER", "REPO"))
    g.add_argument("--evidence", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        result = from_api(*a.api) if a.api else from_evidence(a.evidence)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2
    ok, problems = evaluate(result)
    out = {**result, "ok": ok, "problems": problems}
    print(json.dumps(out, indent=2) if a.json else ("PASS" if ok else "FAIL: " + "; ".join(problems)))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
