#!/usr/bin/env python3
"""Create smc.plan.v3.7 seed from the current v3.6 seed generator."""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
V36 = HERE / "create_plan_seed_v36.py"
RUNTIME = HERE.parents[3] / "domain-runtime"
if not RUNTIME.is_dir():
    RUNTIME = HERE.parents[3] / ".agents" / "ges" / "domain-runtime"
sys.path.insert(0, str(RUNTIME))
from risk_signals import parse_routing_facts, snapshot_json  # noqa: E402


def fm(text):
    out = {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return out
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line and not line[0].isspace() and ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip("\"'")
    return out


def section(text, heading):
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$\n?(.*?)(?=^##\s+|\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def repo_root(path):
    for c in (path.resolve().parent, *path.resolve().parents):
        if (c / ".agents/ges/domain-runtime/domain_runtime.py").is_file():
            return c
    raise ValueError("DOMAIN_RUNTIME_MISSING")


def validate_preplan(prd):
    repo = repo_root(prd)
    target = repo / ".agents/ges/domain-runtime/domain_runtime.py"
    spec = importlib.util.spec_from_file_location("ges_domain_preplan", target)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if mod.load_context(repo)["profile"]["schema"] != "smc.ges.consumer-profile.v3":
        raise ValueError("V37_REQUIRES_PROFILE_V3: explicitly migrate profile or use v36 seed")
    return mod.validate_preplan(prd)


def insert_frontmatter(text, line):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("PLAN_FRONTMATTER_MISSING")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            lines.insert(i, line)
            return "\n".join(lines) + "\n"
    raise ValueError("PLAN_FRONTMATTER_UNCLOSED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prd", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--plan-id", required=True)
    ap.add_argument("--governance-profile", choices=("LEAN", "FULL"))
    a = ap.parse_args()
    out = a.output.resolve()
    if out.exists():
        print(f"PLAN_ALREADY_EXISTS: {out}", file=sys.stderr)
        return 2
    prd = a.prd.resolve()
    prd_text = prd.read_text(encoding="utf-8")
    meta = fm(prd_text)
    profile = (a.governance_profile or meta.get("governance_profile") or "FULL").upper()
    if profile not in {"LEAN", "FULL"}:
        print(f"PRD_GOVERNANCE_PROFILE_INVALID: {profile}", file=sys.stderr)
        return 2
    if meta.get("governance_profile", "").upper() == "FULL" and profile != "FULL":
        print("PRD_PROFILE_DOWNGRADE_FORBIDDEN", file=sys.stderr)
        return 2
    scanner = HERE.parents[1] / "smc-prd-grounding/scripts/prd_profile.py"
    checked = subprocess.run(
        [sys.executable, str(scanner), "scan", str(prd), "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if checked.returncode:
        print(checked.stdout + checked.stderr, file=sys.stderr)
        return 2
    try:
        pre = validate_preplan(prd)
    except Exception as e:
        print(f"DOMAIN_PREPLAN_BLOCKED: {e}", file=sys.stderr)
        return 2
    if pre:
        print("DOMAIN_PREPLAN_BLOCKED: " + str(pre), file=sys.stderr)
        return 2
    facts = parse_routing_facts(section(prd_text, "Routing Facts"))
    snapshot_line = ""
    if facts is not None:
        snapshot_line = (
            f"- Risk Facts Snapshot: `{snapshot_json(facts)}`\n"
            "- Source: approved PRD Routing Facts\n"
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=".ges-v37-", suffix=".plan.md", dir=out.parent, delete=False
    ) as h:
        tmp = Path(h.name)
    tmp.unlink(missing_ok=True)
    try:
        r = subprocess.run(
            [sys.executable, str(V36), str(prd), str(tmp), "--plan-id", a.plan_id],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )
        if r.returncode:
            print((r.stdout + r.stderr).strip(), file=sys.stderr)
            return r.returncode
        text = tmp.read_text(encoding="utf-8").replace(
            "plan_contract: smc.plan.v3.6", "plan_contract: smc.plan.v3.7", 1
        )
        text = text.replace(
            "domain_contract: smc.ges.domain-activation.v1",
            "domain_contract: smc.ges.domain-activation.v2",
            1,
        )
        if "governance_profile:" not in text.split("---", 2)[1]:
            text = insert_frontmatter(text, f"governance_profile: {profile}")
        marker = "## Requirement Coverage Ledger"
        block = (
            f"## Governance Profile\n\n"
            f"- Profile: `{profile}`\n"
            f"- Route rationale: <GROUND>\n"
            f"- Escalation triggers checked: <GROUND>\n"
            f"{snapshot_line}\n"
        )
        if marker in text and "## Governance Profile" not in text:
            text = text.replace(marker, block + marker, 1)
        out.write_text(text, encoding="utf-8")
    finally:
        tmp.unlink(missing_ok=True)
    print(f"Plan v3.7 seed created: {out}\nPlan ID: {a.plan_id}\nGovernance profile: {profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
