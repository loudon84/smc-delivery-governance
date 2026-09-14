#!/usr/bin/env python3
"""Apply Consumer Remediation Plan (dry-run default; --apply writes missing files only)."""
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
from analyze_gap import analyze, write_gap  # noqa: E402
from audit_consumer import audit, write_reports  # noqa: E402
from generate_remediation import generate, write_plan  # noqa: E402


def _normalize_rel(rel: str) -> str:
    # Do NOT use str.lstrip("./") — it strips any mix of dots/slashes and
    # would turn ".agents/..." into "agents/...".
    rel = rel.replace("\\", "/")
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def _assert_allowed(rel: str) -> None:
    rel = _normalize_rel(rel)
    if rel in C.FORBIDDEN_WRITE_RELS or rel == ".specify/spec.md":
        raise ValueError(f"BOOTSTRAP_FORBIDDEN_TARGET: {rel}")
    if rel.endswith("/spec.md") and rel.startswith(".specify/"):
        raise ValueError(f"BOOTSTRAP_FORBIDDEN_SOT: {rel}")
    if rel == ".agents/ges/profile.json":
        raise ValueError("BOOTSTRAP_FORBIDDEN_TARGET: .agents/ges/profile.json")


def apply_plan(
    project: Path,
    plan: dict[str, Any],
    *,
    do_apply: bool,
) -> dict[str, Any]:
    # @lat: [[consumer-bootstrap#Automated Remediation]]
    project = project.resolve()
    bootstrap_id = C.new_id()
    skipped: list[str] = []
    records: dict[str, dict] = {}
    backup = project / ".smc" / "skill-upgrade-backups" / f"bootstrap-{bootstrap_id}"
    status = "DRY_RUN"

    write_actions = [a for a in plan.get("actions", []) if a.get("kind") == "WRITE_TEMPLATE"]
    other_actions = [a for a in plan.get("actions", []) if a.get("kind") != "WRITE_TEMPLATE"]

    for act in other_actions:
        skipped.append(f"{act.get('id')}:{act.get('kind')}:{act.get('target')}")

    try:
        if do_apply:
            backup.mkdir(parents=True, exist_ok=True)
            for act in write_actions:
                target_rel = _normalize_rel(str(act["target"]))
                _assert_allowed(target_rel)
                tmpl_rel = str(act.get("template") or "")
                src = C.TEMPLATES / tmpl_rel
                dst = C.bounded(project, target_rel)
                if dst.is_file():
                    skipped.append(f"EXISTS:{target_rel}")
                    continue
                if target_rel.endswith("/.gitkeep"):
                    # Ensure parent dir exists; write .gitkeep only if missing.
                    if not src.is_file():
                        # Create empty marker.
                        C.write_new_file(project, dst, "", backup, records)
                    else:
                        C.copy_new_file(project, src, dst, backup, records)
                    continue
                if not src.is_file():
                    raise ValueError(f"BOOTSTRAP_TEMPLATE_MISSING: {tmpl_rel}")
                C.copy_new_file(project, src, dst, backup, records)
            status = "PASS"
        else:
            for act in write_actions:
                target_rel = _normalize_rel(str(act["target"]))
                _assert_allowed(target_rel)
                if C.exists_file(project, target_rel):
                    skipped.append(f"EXISTS:{target_rel}")
                else:
                    skipped.append(f"WOULD_WRITE:{target_rel}")
            status = "DRY_RUN"
    except Exception:
        if do_apply and records:
            C.restore(project, backup, records)
            status = "ROLLED_BACK"
        raise

    receipt = {
        "schema": "smc.ges.consumer-bootstrap-receipt.v1",
        "bootstrap_id": bootstrap_id,
        "project": str(project),
        "finalized_at": C.utc_now(),
        "status": status,
        "files": [records[k] for k in sorted(records)] if records else [],
        "skipped": skipped,
        "backup_id": backup.name if do_apply else None,
        "remediation_plan_sha256": "sha256:"
        + C.sha256_text(json.dumps(plan, sort_keys=True, separators=(",", ":"))),
    }
    return receipt


def write_receipt(project: Path, receipt: dict[str, Any]) -> Path:
    out_dir = C.bounded(project, C.RECEIPT_DIR_REL)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{receipt['bootstrap_id']}.json"
    C.dump_json(path, receipt)
    # Compat pointer
    C.dump_json(
        C.bounded(project, ".smc/ges-bootstrap-receipt.json"),
        {
            "schema": "smc.ges.consumer-bootstrap-receipt.v1",
            "bootstrap_id": receipt["bootstrap_id"],
            "receipt_path": f"{C.RECEIPT_DIR_REL}/{receipt['bootstrap_id']}.json",
            "status": receipt["status"],
            "finalized_at": receipt["finalized_at"],
        },
    )
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("--plan", type=Path, help="existing remediation plan JSON")
    ap.add_argument("--apply", action="store_true", help="write missing files (default dry-run)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    project = a.project.resolve()
    if not (project / ".git").exists():
        print("BOOTSTRAP_APPLY_FAILED: TARGET_NOT_GIT_REPO", file=sys.stderr)
        return 2
    try:
        if a.plan:
            plan = C.read_json(a.plan.resolve())
        else:
            audit_report = audit(project)
            write_reports(project, audit_report)
            gap = analyze(audit_report)
            write_gap(project, gap)
            plan = generate(project, gap, audit_report)
            write_plan(project, plan)
        receipt = apply_plan(project, plan, do_apply=a.apply)
        path = write_receipt(project, receipt)
    except Exception as exc:
        print(f"BOOTSTRAP_APPLY_FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"BOOTSTRAP_RECEIPT: {path}")
    print(f"STATUS: {receipt['status']}")
    print(f"FILES: {len(receipt['files'])}")
    print(f"SKIPPED: {len(receipt['skipped'])}")
    if a.json:
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
    if not a.apply:
        print("DRY RUN — pass --apply to write missing scaffold/contracts/shims")
    return 0 if receipt["status"] in {"PASS", "DRY_RUN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
