#!/usr/bin/env python3
"""Verify GitHub master protection / ruleset evidence (token from env only).

Fail-closed: missing fields stay MISSING/UNKNOWN — never positive defaults.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_CHECKS = ["validate", "GES Package Gate / validate-package"]
SCHEMA = "smc.repo.protection-evidence.v1"


def _tri(value: Any) -> bool | None:
    if value is True:
        return True
    if value is False:
        return False
    return None


def _sha_bytes(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def parse_evidence(raw: dict[str, Any], *, source: str = "OFFLINE_FIXTURE") -> dict[str, Any]:
    # @lat: [[safety-runtime-closure-v503]]
    """Strict smc.repo.protection-evidence.v1 parser — no positive defaults."""
    if not isinstance(raw, dict):
        raise ValueError("REPO_GOVERNANCE_INVALID_EVIDENCE")

    # Prefer explicit schema envelope; otherwise treat as ruleset detail / fixture.
    body = raw
    if raw.get("schema") == SCHEMA:
        body = raw

    rules = body.get("rules") if isinstance(body.get("rules"), list) else None
    required: list[str] | None = None
    require_pr: bool | None = None
    force_push_blocked: bool | None = None
    deletion_blocked: bool | None = None
    direct_update_restricted: bool | None = None
    bypass_actors: list[Any] | None = None

    if "required_checks" in body:
        raw_checks = body.get("required_checks")
        if raw_checks is None:
            required = None
        elif isinstance(raw_checks, list):
            required = []
            for c in raw_checks:
                if isinstance(c, dict):
                    name = c.get("context") or c.get("name")
                    if name:
                        required.append(str(name))
                elif c:
                    required.append(str(c))
        else:
            raise ValueError("REPO_GOVERNANCE_INVALID_EVIDENCE")

    if isinstance(rules, list):
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            rtype = str(rule.get("type") or "")
            params = rule.get("parameters") if isinstance(rule.get("parameters"), dict) else {}
            if rtype == "pull_request":
                require_pr = True
            elif rtype == "required_status_checks":
                contexts = params.get("required_status_checks") or params.get("contexts") or []
                required = []
                for c in contexts:
                    if isinstance(c, dict):
                        name = c.get("context") or c.get("name")
                        if name:
                            required.append(str(name))
                    elif c:
                        required.append(str(c))
            elif rtype == "non_fast_forward":
                force_push_blocked = True
            elif rtype == "deletion":
                deletion_blocked = True
            elif rtype == "update":
                # GitHub "update" restriction blocks direct pushes when present.
                direct_update_restricted = True

    if "require_pr" in body:
        require_pr = _tri(body.get("require_pr"))
    if "force_push_blocked" in body:
        force_push_blocked = _tri(body.get("force_push_blocked"))
    elif "block_force_pushes" in body:
        force_push_blocked = _tri(body.get("block_force_pushes"))
    if "deletion_blocked" in body:
        deletion_blocked = _tri(body.get("deletion_blocked"))
    elif "block_deletions" in body:
        deletion_blocked = _tri(body.get("block_deletions"))
    if "direct_update_restricted" in body:
        direct_update_restricted = _tri(body.get("direct_update_restricted"))
    elif "restrict_direct_pushes" in body:
        direct_update_restricted = _tri(body.get("restrict_direct_pushes"))

    if "bypass_actors" in body:
        bypass_actors = body.get("bypass_actors") if isinstance(body.get("bypass_actors"), list) else None
    elif isinstance(body.get("bypass_actors"), list):
        bypass_actors = body["bypass_actors"]

    enforcement = body.get("enforcement")
    if enforcement is not None:
        enforcement = str(enforcement)

    include_refs = body.get("include_refs")
    if include_refs is None and isinstance(body.get("conditions"), dict):
        ref_name = body["conditions"].get("ref_name")
        if isinstance(ref_name, dict):
            include_refs = ref_name.get("include")

    protected: bool | None
    if "protected" in body:
        protected = _tri(body.get("protected"))
    elif enforcement == "active":
        protected = True
    elif enforcement in {"disabled", "evaluate"}:
        protected = False
    else:
        protected = None

    raw_bytes = json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema": SCHEMA,
        "source": source,
        "repository": body.get("repository") or body.get("repo") or "",
        "repository_id": body.get("repository_id") or body.get("node_id") or 0,
        "branch": body.get("branch") or "master",
        "ruleset_id": body.get("ruleset_id") or body.get("id") or 0,
        "ruleset_target": body.get("ruleset_target") or body.get("target") or "",
        "enforcement": enforcement,
        "include_refs": include_refs if isinstance(include_refs, list) else None,
        "require_pr": require_pr,
        "required_checks": required,
        "force_push_blocked": force_push_blocked,
        "deletion_blocked": deletion_blocked,
        "direct_update_restricted": direct_update_restricted,
        "bypass_actors": bypass_actors if bypass_actors is not None else [],
        "fetched_at": body.get("fetched_at") or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "raw_evidence_sha256": body.get("raw_evidence_sha256") or _sha_bytes(raw_bytes),
        # Compat projection used by evaluate()
        "protected": protected,
    }


# Back-compat alias used by tools/check_repo_governance.py
def _normalize(evidence: dict) -> dict:
    parsed = parse_evidence(evidence)
    return {
        "protected": parsed.get("protected"),
        "require_pr": parsed.get("require_pr"),
        "required_checks": parsed.get("required_checks") if parsed.get("required_checks") is not None else [],
        "force_push_blocked": parsed.get("force_push_blocked"),
        "deletion_blocked": parsed.get("deletion_blocked"),
        "direct_update_restricted": parsed.get("direct_update_restricted"),
        "evidence": parsed,
    }


def from_evidence(path: Path) -> dict:
    # @lat: [[acceptance-closure#Repository Protection Verifier]]
    data = json.loads(path.read_text(encoding="utf-8"))
    return _normalize(data)


def from_api(owner: str, repo: str) -> dict:
    token = os.environ.get("SMC_GOVERNANCE_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("REPO_GOVERNANCE_UNAVAILABLE: GITHUB_TOKEN_MISSING")
    url = f"https://api.github.com/repos/{owner}/{repo}/rulesets"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            rulesets = json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise ValueError(f"REPO_GOVERNANCE_UNAVAILABLE: HTTP_{exc.code}") from exc
    except Exception as exc:
        raise ValueError(f"REPO_GOVERNANCE_UNAVAILABLE: {exc}") from exc

    master = None
    for rs in rulesets if isinstance(rulesets, list) else []:
        name = str(rs.get("name", ""))
        if "GES Master Governance" in name:
            master = rs
            break
    if master is None:
        # Do NOT fall back to rulesets[0] — that manufactures false confidence.
        return _normalize(
            {
                "protected": False,
                "enforcement": None,
                "required_checks": None,
                "require_pr": None,
                "force_push_blocked": None,
                "deletion_blocked": None,
                "direct_update_restricted": None,
                "repository": f"{owner}/{repo}",
            }
        )

    detail_url = f"https://api.github.com/repos/{owner}/{repo}/rulesets/{master['id']}"
    req = urllib.request.Request(
        detail_url, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            detail = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        raise ValueError(f"REPO_GOVERNANCE_UNAVAILABLE: {exc}") from exc
    detail.setdefault("repository", f"{owner}/{repo}")
    return _normalize(detail)


def evaluate(result: dict) -> tuple[str, list[str]]:
    """Return (verdict, problems). Verdicts: PASS|DRIFT|INVALID_EVIDENCE."""
    evidence = result.get("evidence") if isinstance(result.get("evidence"), dict) else result
    problems: list[str] = []

    protected = evidence.get("protected") if "protected" in evidence else result.get("protected")
    require_pr = evidence.get("require_pr") if "require_pr" in evidence else result.get("require_pr")
    checks = evidence.get("required_checks") if "required_checks" in evidence else result.get("required_checks")
    force = evidence.get("force_push_blocked") if "force_push_blocked" in evidence else result.get("force_push_blocked")
    deletion = evidence.get("deletion_blocked") if "deletion_blocked" in evidence else result.get("deletion_blocked")
    direct = (
        evidence.get("direct_update_restricted")
        if "direct_update_restricted" in evidence
        else result.get("direct_update_restricted")
    )
    enforcement = evidence.get("enforcement")
    include_refs = evidence.get("include_refs")
    target = evidence.get("ruleset_target") or evidence.get("target")

    missing_fields = []
    for name, value in (
        ("protected", protected),
        ("require_pr", require_pr),
        ("required_checks", checks),
        ("force_push_blocked", force),
        ("deletion_blocked", deletion),
        ("direct_update_restricted", direct),
    ):
        if value is None:
            missing_fields.append(name)

    if missing_fields:
        # protected=true alone with missing required fields is INVALID, not PASS.
        if protected is True:
            return "REPO_GOVERNANCE_INVALID_EVIDENCE", [
                f"missing field: {f}" for f in missing_fields
            ]
        return "REPO_GOVERNANCE_DRIFT", [f"missing field: {f}" for f in missing_fields]

    if protected is not True:
        problems.append("master not protected")
    if enforcement and enforcement != "active":
        problems.append(f"enforcement not active: {enforcement}")
    if target and target not in {"branch", "BRANCH"}:
        problems.append(f"ruleset target not branch: {target}")
    if isinstance(include_refs, list) and include_refs:
        if not any("master" in str(r) or str(r).endswith("/master") for r in include_refs):
            problems.append("ruleset does not target master")
    if require_pr is not True:
        problems.append("require_pr missing")
    check_set = set(checks or [])
    for need in REQUIRED_CHECKS:
        if need not in check_set and not any(need in c for c in check_set):
            problems.append(f"missing check: {need}")
    if force is not True:
        problems.append("force push not blocked")
    if deletion is not True:
        problems.append("deletion not blocked")
    if direct is not True:
        problems.append("direct update not restricted")

    bypass = evidence.get("bypass_actors") or []
    if bypass:
        problems.append(f"bypass actors present: {len(bypass)}")

    if problems:
        return "REPO_GOVERNANCE_DRIFT", problems
    return "REPO_GOVERNANCE_PASS", []


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
        out = {
            "code": "REPO_GOVERNANCE_UNAVAILABLE",
            "detail": str(exc),
            "verifier_implementation": "PASS",
            "live_master_protection": "UNAVAILABLE",
        }
        print(json.dumps(out, indent=2) if a.json else out["code"])
        return 2
    code, problems = evaluate(result)
    live = "PASS" if code == "REPO_GOVERNANCE_PASS" else ("DRIFT" if code.endswith("DRIFT") else "UNAVAILABLE")
    if code == "REPO_GOVERNANCE_INVALID_EVIDENCE":
        live = "DRIFT"
    out = {
        **result,
        "code": code,
        "problems": problems,
        "ok": code == "REPO_GOVERNANCE_PASS",
        "verifier_implementation": "PASS",
        "live_master_protection": live,
    }
    if a.json:
        print(json.dumps(out, indent=2))
    else:
        print(code if code != "REPO_GOVERNANCE_PASS" else "PASS")
        if problems:
            print("; ".join(problems), file=sys.stderr)
    return 0 if code == "REPO_GOVERNANCE_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
