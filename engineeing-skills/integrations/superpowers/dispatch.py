#!/usr/bin/env python3
"""Build a minimal Superpowers method-provider task packet (GES-owned)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

FORBIDDEN_WRITES = [
    "canonical Plan structure or Todo identity",
    "Delivery State ledger",
    "Completion Audit verdict",
    "Implementation Review verdict",
    "Final Evidence verdict",
    "implementation commit",
    "Roadmap status",
    "install/rollback receipt",
]


def build_task_packet(
    *,
    plan_id: str,
    plan_semantic_hash: str,
    todo_id: str,
    write_ownership: list[str],
    read_scope: list[str],
    source_context_capsule_ids: list[str],
    engineering_method_policy: str,
    required_tdd_debug_gates: list[str],
    focused_verification_command: list[str],
) -> dict:
    # @lat: [[safety-runtime-closure-v503]]
    return {
        "schema": "smc.ges.method-task-packet.v1",
        "plan_id": plan_id,
        "plan_semantic_hash": plan_semantic_hash,
        "todo_id": todo_id,
        "write_ownership": write_ownership,
        "read_scope": read_scope,
        "source_context_capsule_ids": source_context_capsule_ids,
        "engineering_method_policy": engineering_method_policy,
        "required_tdd_debug_gates": required_tdd_debug_gates,
        "focused_verification_command": focused_verification_command,
        "forbidden_state_writes": list(FORBIDDEN_WRITES),
        "orchestrator": "smc-plan-delivery",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan-id", required=True)
    ap.add_argument("--plan-semantic-hash", required=True)
    ap.add_argument("--todo-id", required=True)
    ap.add_argument("--write", action="append", default=[])
    ap.add_argument("--read", action="append", default=[])
    ap.add_argument("--capsule", action="append", default=[])
    ap.add_argument("--policy", default="UPSTREAM_PINNED")
    ap.add_argument("--gate", action="append", default=[])
    ap.add_argument("--verify-cmd", nargs="+", default=["python", "-m", "pytest", "-q"])
    a = ap.parse_args()
    packet = build_task_packet(
        plan_id=a.plan_id,
        plan_semantic_hash=a.plan_semantic_hash,
        todo_id=a.todo_id,
        write_ownership=a.write,
        read_scope=a.read,
        source_context_capsule_ids=a.capsule,
        engineering_method_policy=a.policy,
        required_tdd_debug_gates=a.gate,
        focused_verification_command=a.verify_cmd,
    )
    print(json.dumps(packet, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
