#!/usr/bin/env python3
"""Validate Consumer platform integration: GES + Spec Kit + Superpowers + handoffs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import common as C  # noqa: E402
from audit_consumer import audit  # noqa: E402


def _row(cid: str, verdict: str, detail: str) -> dict[str, str]:
    return {"id": cid, "verdict": verdict, "detail": detail}


def validate(project: Path) -> dict[str, Any]:
    # @lat: [[consumer-bootstrap#Consumer Validation]]
    project = project.resolve()
    report = audit(project)
    checks: list[dict[str, str]] = []

    ges = report["layers"]["ges"]
    ges_detail = f"{ges['present']}/{ges['total']} present"
    if ges.get("missing"):
        ges_detail += "; missing=" + ",".join(ges["missing"])
        if any(m in {"ges.profile", "ges.domain_registry"} for m in ges["missing"]):
            ges_detail += " (re-run: python install.py <project> --apply)"
    checks.append(
        _row(
            "GES Runtime",
            "PASS" if ges["verdict"] == "PASS" else "FAIL",
            ges_detail,
        )
    )

    sk = report["layers"]["spec_kit"]
    checks.append(
        _row(
            "Spec Kit",
            "PASS" if sk["verdict"] == "PASS" else "FAIL",
            f"scaffold={sk['verdict']} provider={sk.get('provider_status')}",
        )
    )

    sp = report["layers"]["superpowers"]
    # Method layer: pinned skills OR GES_NATIVE shims for gaps may still be PARTIAL.
    # Validation requires: executing-plans + verification-before-completion + work router + all shims.
    required_method = [
        "executing-plans",
        "verification-before-completion",
        "brainstorming",
        "writing-plans",
        "finishing-branch",
    ]
    method_ok = all(C.exists_file(project, f".agents/skills/{n}/SKILL.md") for n in required_method)
    checks.append(
        _row(
            "Superpowers",
            "PASS" if method_ok else "FAIL",
            f"layer={sp['verdict']} required_method_ok={method_ok}",
        )
    )

    # Spec -> Plan handoff: bridge contract + PRD grounding skill
    handoff_ok = C.exists_file(project, ".agents/ges/spec-superpower-ges.json") and C.exists_file(
        project, ".agents/skills/smc-prd-grounding/SKILL.md"
    )
    if handoff_ok:
        try:
            bridge = C.read_json(C.bounded(project, ".agents/ges/spec-superpower-ges.json"))
            handoff_ok = (
                bridge.get("schema") == "smc.ges.spec-superpower-ges.v1"
                and bool((bridge.get("handoff") or {}).get("spec_to_superpower", {}).get("enabled"))
                and bool((bridge.get("handoff") or {}).get("plan_to_ges", {}).get("enabled"))
            )
        except Exception as exc:
            handoff_ok = False
            checks.append(_row("Spec -> Plan handoff", "FAIL", str(exc)))
    if not any(c["id"] == "Spec -> Plan handoff" for c in checks):
        checks.append(
            _row(
                "Spec -> Plan handoff",
                "PASS" if handoff_ok else "FAIL",
                "spec-superpower-ges.json + smc-prd-grounding",
            )
        )

    # Plan -> Delivery
    plan_delivery_ok = C.exists_file(
        project, ".agents/skills/smc-plan-delivery/scripts/run_selftest.py"
    ) and C.exists_file(project, ".agents/skills/smc-plan-validator/scripts/validate_plan_v37.py")
    checks.append(
        _row(
            "Plan -> Delivery",
            "PASS" if plan_delivery_ok else "FAIL",
            "validator + delivery self-test entrypoints",
        )
    )

    # Evidence surface
    evidence_ok = C.exists_file(project, ".agents/skills/smc-plan-delivery/scripts/evidence.py")
    checks.append(
        _row(
            "Evidence",
            "PASS" if evidence_ok else "FAIL",
            ".agents/skills/smc-plan-delivery/scripts/evidence.py",
        )
    )

    # Release governance: lock + receipt + governance-policy
    release_ok = (
        C.exists_file(project, ".smc/ges-install-lock.json")
        and (
            C.exists_file(project, ".smc/ges-install-receipt.json")
            or (
                (project / ".smc" / "ges-install-receipts").is_dir()
                and any((project / ".smc" / "ges-install-receipts").glob("*.json"))
            )
        )
        and C.exists_file(project, ".agents/ges/governance-policy.json")
    )
    checks.append(
        _row(
            "Release Governance",
            "PASS" if release_ok else "FAIL",
            "install lock/receipt + governance-policy.json",
        )
    )

    context_ok = C.exists_file(project, ".agents/ges/context-engine/registry.py")
    checks.append(
        _row(
            "Context Engine",
            "PASS" if context_ok else "FAIL",
            ".agents/ges/context-engine/registry.py",
        )
    )

    ok = all(c["verdict"] == "PASS" for c in checks)
    return {
        "schema": "smc.ges.consumer-validation.v1",
        "project": str(project),
        "validated_at": C.utc_now(),
        "ok": ok,
        "code": "CONSUMER_VALIDATION_PASS" if ok else "CONSUMER_VALIDATION_FAILED",
        "checks": checks,
        "claims": report.get("claims") or {},
    }


def write_validation(project: Path, result: dict[str, Any]) -> Path:
    out_dir = C.bounded(project, C.REPORT_DIR_REL)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "consumer-validation.json"
    C.dump_json(path, result)
    md = out_dir / "consumer-validation.md"
    lines = [
        "# Consumer Validation",
        "",
        f"- Project: `{result['project']}`",
        f"- Validated at: `{result['validated_at']}`",
        f"- Code: `{result['code']}`",
        "",
        "## Checks",
        "",
    ]
    for c in result["checks"]:
        lines.append(f"- [{c['verdict']}] **{c['id']}** — {c['detail']}")
    lines.append("")
    md.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    project = a.project.resolve()
    if not (project / ".git").exists():
        print("CONSUMER_VALIDATION_FAILED: TARGET_NOT_GIT_REPO", file=sys.stderr)
        return 2
    result = validate(project)
    path = write_validation(project, result)
    print(f"CONSUMER_VALIDATION: {path}")
    for c in result["checks"]:
        print(f"{c['verdict']} {c['id']}")
    print(result["code"])
    if a.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
