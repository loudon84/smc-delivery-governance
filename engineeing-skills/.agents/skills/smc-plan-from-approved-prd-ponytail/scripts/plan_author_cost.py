#!/usr/bin/env python3
"""Bounded Plan Author helpers: structured patches + grounding externalization.

Does not replace create_plan_seed_v37.py. Model calls must go through model_dispatch.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PKG = HERE.parents[3]  # engineeing-skills (.agents/skills/<skill>/scripts)
CTX = PKG / "context-engine"
if str(CTX) not in sys.path:
    sys.path.insert(0, str(CTX))

from context_envelope import plan_envelope, persist_envelope  # noqa: E402
from model_dispatch import prepare_dispatch, run_managed_call  # noqa: E402
from harness_contract import fake_enforced_adapter  # noqa: E402
from runtime_locator import locate  # noqa: E402


def grounding_dir(repo: Path, plan_id: str) -> Path:
    return repo / ".smc" / "runs" / plan_id / "grounding"


def write_grounding_capsule(repo: Path, plan_id: str, change_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Externalize bulky grounding evidence; return digest ref for Plan body."""
    root = grounding_dir(repo, plan_id)
    root.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    path = root / f"{change_id}-{digest[7:15]}.json"
    path.write_text(json.dumps({"digest": digest, "change_id": change_id, "payload": payload}, indent=2) + "\n", encoding="utf-8")
    return {"change_id": change_id, "evidence_digest": digest, "evidence_ref": str(path.relative_to(repo)).replace("\\", "/")}


def apply_structured_patches(plan_text: str, patches: list[dict[str, Any]]) -> str:
    """Apply unresolved-decision patches without regenerating the full Plan markdown.

    Patches are recorded as a machine appendix; renderer keeps seed body intact.
    """
    if not patches:
        return plan_text
    block_lines = [
        "",
        "## Structured Decision Patches",
        "",
        "| Change ID | Owner | Action | Decision | Evidence |",
        "|---|---|---|---|---|",
    ]
    for p in patches:
        block_lines.append(
            "| {change_id} | {owner} | {action} | {decision} | {evidence} |".format(
                change_id=p.get("change_id") or "",
                owner=p.get("owner") or "",
                action=p.get("action") or "",
                decision=p.get("decision") or "",
                evidence=p.get("evidence_digest") or p.get("evidence_ref") or "",
            )
        )
    marker = "## Structured Decision Patches"
    if marker in plan_text:
        pre = plan_text.split(marker)[0].rstrip()
        return pre + "\n" + "\n".join(block_lines) + "\n"
    return plan_text.rstrip() + "\n" + "\n".join(block_lines) + "\n"


def author_unresolved_via_dispatch(
    *,
    repo: Path,
    plan: Path,
    plan_id: str,
    governance_profile: str,
    unresolved: list[dict[str, Any]],
    candidates: list[dict[str, Any]] | None = None,
    adapter=None,
) -> dict[str, Any]:
    """Force Plan Author model work through Budget→Envelope→Permit→dispatch."""
    if not unresolved:
        raise ValueError("PLAN_AUTHOR_NO_UNRESOLVED")
    prepared = prepare_dispatch(
        work_item_id=plan_id,
        plan_id=plan_id,
        phase="PLAN",
        governance_profile=governance_profile,
        requested_tier="STANDARD",
        agent_role="plan-author",
        candidates=candidates or [{"path": f"decision/{u.get('change_id')}", "tokens": 100, "artifact_kind": "FEATURE_SCOPE"} for u in unresolved],
        required_artifacts=[{"kind": "UNRESOLVED_DECISION", **u} for u in unresolved],
        structured_constraints=["structured_patch_only", "no_full_plan_reauthor"],
        allowed_roots=[],
        repo=repo,
        cost_bucket="PLAN",
    )
    if prepared["permit"]["status"] != "PERMITTED":
        raise ValueError(prepared["permit"].get("reason") or "CONTEXT_BUDGET_INSUFFICIENT")
    persist_envelope(repo, plan_id, prepared["envelope"], "plan-context-envelope.json")
    # Fake adapter returns the patches as structured response
    patches = []
    for u in unresolved:
        ref = write_grounding_capsule(repo, plan_id, str(u.get("change_id") or "C00"), {"decision": u})
        patches.append({**u, **ref})
    if adapter is None:
        raise ValueError("HARNESS_ADAPTER_REQUIRED")
    out = run_managed_call(plan=plan, prepared=prepared, adapter=adapter, prompt_meta={"unresolved": unresolved})
    out["patches"] = patches
    return out


def require_dispatch_for_model_call(permit: dict[str, Any] | None) -> None:
    if not permit or permit.get("status") != "PERMITTED":
        raise ValueError("MODEL_DISPATCH_PERMIT_MISSING")
