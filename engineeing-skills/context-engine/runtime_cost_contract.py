"""Runtime cost contract for v5.0.9 plans (smc.ges.runtime-cost-contract.v1).

New plans declare runtime_cost_contract: smc.ges.runtime-cost.v1 in frontmatter.
Required stages must produce managed dispatches or an explicit no-model-work receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT_SCHEMA = "smc.ges.runtime-cost-contract.v1"
CONTRACT_FRONTMATTER = "smc.ges.runtime-cost.v1"
NO_MODEL_WORK_SCHEMA = "smc.ges.no-model-work.v1"
DEFAULT_REQUIRED_STAGES = ("PLANNING", "IMPLEMENTATION", "REVIEW")
ALLOWED_NO_MODEL_REASONS = {
    "deterministic-plan-seed-only",
    "deterministic-review-clearance",
    "deterministic-mechanical-step",
}


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _repo_root(plan: Path) -> Path:
    p = plan.resolve()
    for cand in (p.parent, *p.parents):
        if (cand / ".git").exists():
            return cand
    return p.parent


def _plan_id(plan: Path) -> str:
    text = plan.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("plan_id:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return plan.stem


def contract_path(plan: Path) -> Path:
    return _repo_root(plan) / ".smc" / "runs" / _plan_id(plan) / "runtime-cost-contract.json"


def no_model_work_dir(plan: Path) -> Path:
    return _repo_root(plan) / ".smc" / "runs" / _plan_id(plan) / "no-model-work"


def read_contract_frontmatter(plan: Path) -> str | None:
    text = plan.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    fm = text.split("---", 2)[1]
    for line in fm.splitlines():
        if line.startswith("runtime_cost_contract:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def has_contract(plan: Path) -> bool:
    return read_contract_frontmatter(plan) == CONTRACT_FRONTMATTER


def init_contract(plan: Path, *, required_stages: list[str] | None = None, epoch: int = 1) -> Path:
    stages = [s.upper() for s in (required_stages or list(DEFAULT_REQUIRED_STAGES))]
    rec = {
        "schema": CONTRACT_SCHEMA,
        "plan_id": _plan_id(plan),
        "required_stages": stages,
        "epoch": epoch,
        "created_from": "plan-frontmatter",
        "created_at": _utc(),
    }
    path = contract_path(plan)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_contract(plan: Path) -> dict[str, Any] | None:
    path = contract_path(plan)
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != CONTRACT_SCHEMA:
        raise ValueError("RUNTIME_COST_CONTRACT_INVALID")
    return data


def record_no_model_work(
    plan: Path,
    *,
    stage: str,
    reason: str,
    todo_id: str = "",
    deterministic_entrypoint: str = "",
    artifact_digest: str = "",
) -> Path:
    stage_u = stage.upper()
    if reason not in ALLOWED_NO_MODEL_REASONS:
        raise ValueError("NO_MODEL_WORK_REASON_INVALID")
    rec = {
        "schema": NO_MODEL_WORK_SCHEMA,
        "plan_id": _plan_id(plan),
        "stage": stage_u,
        "todo_id": todo_id,
        "reason": reason,
        "deterministic_entrypoint": deterministic_entrypoint,
        "artifact_digest": artifact_digest,
        "created_at": _utc(),
    }
    digest = hashlib.sha256(
        json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    out = no_model_work_dir(plan) / f"{stage_u.lower()}-{digest[:12]}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def no_model_work_receipt(plan: Path, stage: str) -> dict[str, Any] | None:
    stage_u = stage.upper()
    d = no_model_work_dir(plan)
    if not d.is_dir():
        return None
    for path in sorted(d.glob(f"{stage_u.lower()}-*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if rec.get("schema") == NO_MODEL_WORK_SCHEMA and rec.get("stage") == stage_u:
            return rec
    return None


def migrate(plan: Path) -> Path:
    """Attach runtime cost contract to an existing plan (no fake telemetry)."""
    text = plan.read_text(encoding="utf-8")
    if "runtime_cost_contract:" not in text.split("---", 2)[1] if text.startswith("---") else True:
        lines = text.splitlines()
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    lines.insert(i, f"runtime_cost_contract: {CONTRACT_FRONTMATTER}")
                    lines.insert(i + 1, "runtime_cost_epoch: 1")
                    plan.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
                    break
    return init_contract(plan)


def main() -> int:
    ap = argparse.ArgumentParser(description="Runtime cost contract")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init")
    p.add_argument("plan", type=Path)
    p = sub.add_parser("migrate")
    p.add_argument("plan", type=Path)
    p = sub.add_parser("no-model-work")
    p.add_argument("plan", type=Path)
    p.add_argument("--stage", required=True)
    p.add_argument("--reason", required=True)
    p.add_argument("--todo-id", default="")
    p.add_argument("--json", action="store_true")
    a = ap.parse_args()
    plan = a.plan.resolve()
    if a.cmd == "init":
        out = init_contract(plan)
        print(out)
        return 0
    if a.cmd == "migrate":
        out = migrate(plan)
        print(out)
        return 0
    out = record_no_model_work(plan, stage=a.stage, reason=a.reason, todo_id=a.todo_id)
    print(json.dumps({"path": str(out)}, indent=2) if a.json else out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
