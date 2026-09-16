#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from common import find_repo_root, parse_first_table, parse_top_level_frontmatter, plan_id, section, strip_md, repo_relative_path
from completion_audit import check as audit_status
from delivery_state import load as load_run
from evidence import current_status as evidence_status
from execution_context import latest as execution_resume
from plan_state import cursor_todos, smc_todo_id, validate as todo_validate
from review_record import latest_status as review_status
from workspace import inspect as workspace_inspect
from contract_resolver import validator_name


def blocking_verifications(plan: Path) -> list[str]:
    _, rows = parse_first_table(section(plan.read_text(encoding="utf-8"), "Verification Ledger"))
    return [strip_md(r.get("Verification ID", "")).upper() for r in rows if strip_md(r.get("Blocking", "")).lower() == "yes"]


def static_status(plan: Path, root: Path) -> tuple[str, str]:
    contract = parse_top_level_frontmatter(plan.read_text(encoding="utf-8")).get("plan_contract", "")
    name = validator_name(contract)
    if not name:
        return "FAIL", f"unsupported plan contract: {contract or 'missing'}"
    validator = root / ".agents/skills/smc-plan-validator/scripts" / name
    if not validator.is_file(): return "MISSING", f"validator missing: {validator_name}"
    r = subprocess.run([sys.executable, str(validator), str(plan)], cwd=root, capture_output=True, text=True)
    detail = (r.stdout + r.stderr).strip().replace("\n", " | ")
    return ("PASS" if r.returncode == 0 else "FAIL"), detail


def collect(plan: Path) -> dict:
    root = find_repo_root(plan); ws = workspace_inspect(plan)
    static, static_detail = static_status(plan, root)
    plan_review, _ = review_status(plan, "plan"); implementation_review, _ = review_status(plan, "implementation"); completion, _ = audit_status(plan)
    todo_errors = todo_validate(plan)
    todo_rows = [{"todo": smc_todo_id(str(x["id"])), "cursor_id": x["id"], "content": x.get("content"), "status": x["status"]} for x in cursor_todos(plan.read_text(encoding="utf-8"))]
    done = sum(1 for x in todo_rows if x["status"] == "completed")
    evid = {vid: evidence_status(plan, vid)[0] for vid in blocking_verifications(plan)}
    run = load_run(plan) or {}; resume = execution_resume(plan)
    cost_closure = None
    cost_closure_blocking = False
    try:
        here = Path(__file__).resolve().parent
        if str(here) not in sys.path:
            sys.path.insert(0, str(here))
        from runtime_locator import locate

        paths = locate(here)
        if str(paths.runtime_root) not in sys.path:
            sys.path.insert(0, str(paths.runtime_root))
        from stage_cost_closure import assert_managed_cost_closure, evaluate_stage

        for stage in ("PLANNING", "IMPLEMENTATION", "REVIEW"):
            try:
                closure = evaluate_stage(plan=plan, stage=stage, strict_stage=True)
                if closure.get("dispatch_count", 0) > 0 or closure.get("orphan_results"):
                    cost_closure = cost_closure or {}
                    cost_closure[stage] = closure.get("status")
                    if closure.get("status") not in {"PASS", "PASS_USAGE_UNAVAILABLE", "PASS_NO_MODEL_WORK"}:
                        cost_closure_blocking = True
            except Exception:
                pass
        try:
            assert_managed_cost_closure(plan)
        except ValueError:
            cost_closure_blocking = True
    except Exception:
        cost_closure = None
        cost_closure_blocking = True
    return {
        "schema": "smc.delivery.readiness.v2",
        "plan_id": plan_id(plan), "plan": repo_relative_path(plan, root),
        "scope_fingerprint": ws["scope_fingerprint"], "ambient_fingerprint": ws["ambient_fingerprint"],
        "workspace": {"ambient_stable": ws["ambient_stable"], "ambient_mutated": ws["ambient_mutated"], "unexpected_dirty": ws["unexpected_dirty"], "scope_changed_files": ws["scope_changed_files"]},
        "run_state": run.get("state", "UNINITIALIZED"), "last_valid_state": run.get("last_valid_state", "UNINITIALIZED"),
        "static_gate": static, "static_detail": static_detail, "semantic_gate": plan_review,
        "todos": {"completed": done, "total": len(todo_rows), "rows": todo_rows, "errors": todo_errors},
        "execution_context": {"active_todo": resume.get("active_todo"), "next_step": resume.get("next_step"), "last_event": resume.get("last_event")},
        "completion_audit": completion, "implementation_review": implementation_review, "verification": evid,
        "implementation_commit": run.get("implementation_commit"), "roadmap": "DONE" if run.get("state") == "ROADMAP_DONE" else "PENDING",
        "stage_cost_closure": cost_closure,
        "stage_cost_closure_blocking": cost_closure_blocking,
    }


def print_table(data: dict) -> None:
    ev = ", ".join(f"{k}={v}" for k, v in data["verification"].items()) or "none"; todo = data["todos"]
    print("SMC DELIVERY READINESS")
    print(f"Plan                 : {data['plan']} ({data['plan_id']})")
    print(f"Run state            : {data['run_state']}")
    print(f"Static Gate          : {data['static_gate']}")
    print(f"Semantic Gate        : {data['semantic_gate']}")
    print(f"Todos                : {todo['completed']}/{todo['total']} completed")
    print(f"Active Todo          : {(data['execution_context']['active_todo'] or {}).get('id','-')}")
    print(f"Next Step            : {data['execution_context']['next_step']}")
    print(f"Workspace Ambient    : {'STABLE' if data['workspace']['ambient_stable'] else 'MUTATED'}")
    print(f"Workspace Drift      : {', '.join(data['workspace']['unexpected_dirty']) or '-'}")
    print(f"Completion Audit     : {data['completion_audit']}")
    print(f"Implementation Review: {data['implementation_review']}")
    print(f"Verification         : {ev}")
    print(f"Implementation Commit: {data['implementation_commit'] or '-'}")
    print(f"Roadmap              : {data['roadmap']}")
    print(f"Scope Fingerprint    : {data['scope_fingerprint']}")
    if data.get("stage_cost_closure"):
        print(f"Stage Cost Closure   : {data['stage_cost_closure']}")
        print(f"Cost Closure Block   : {'YES' if data.get('stage_cost_closure_blocking') else 'NO'}")


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("plan", type=Path); ap.add_argument("--json", action="store_true"); args = ap.parse_args()
    plan = args.plan.resolve()
    if not plan.is_file(): print(f"PLAN_NOT_FOUND: {plan}", file=sys.stderr); return 2
    try: data = collect(plan)
    except (ValueError, RuntimeError) as exc: print(str(exc), file=sys.stderr); return 1
    if args.json: print(json.dumps(data, ensure_ascii=False, indent=2))
    else: print_table(data)
    if data.get("stage_cost_closure_blocking"):
        return 1
    return 0


if __name__ == "__main__": raise SystemExit(main())
