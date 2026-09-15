"""Canonical GES model dispatch runtime (smc.ges.model-dispatch.v1).

Budget → Envelope → Permit → telemetry.dispatch → harness → telemetry.result.
No parallel product root; lives under context-engine and installs into frontend-runtime.
"""
from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from budget_controller import decide_budget, policy_digest, trim_candidates  # noqa: E402
from context_cache import CapsuleStore  # noqa: E402
from context_envelope import build_envelope, estimate_tokens  # noqa: E402
from harness_contract import (  # noqa: E402
    MODE_ENFORCED,
    MODE_OBSERVABLE,
    MODE_UNMANAGED,
    HarnessAdapter,
    classify_mode,
    fake_enforced_adapter,
)

DISPATCH_SCHEMA = "smc.ges.model-dispatch.v1"
PERMIT_SCHEMA = "smc.ges.model-dispatch-permit.v1"

# Delivery scripts for telemetry (optional import)
_DELIVERY = HERE.parent / ".agents" / "skills" / "smc-plan-delivery" / "scripts"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _import_runtime_metrics():
    if str(_DELIVERY) not in sys.path:
        sys.path.insert(0, str(_DELIVERY))
    import runtime_metrics as rm  # noqa: WPS433

    return rm


def resolve_capsules(
    store: CapsuleStore | None,
    candidates: list[dict[str, Any]],
    *,
    repo_identity: str,
    scope_digest: str,
    policy_digest_value: str,
    extractor_version: str = "1.0.0",
) -> tuple[list[dict[str, Any]], int, int, int]:
    """Resolve candidates against CapsuleStore; return capsules + hit/miss/stale."""
    hits = misses = stale = 0
    out: list[dict[str, Any]] = []
    for c in candidates:
        identity = str(c.get("path") or c.get("identity") or "")
        content = c.get("content")
        sha = str(c.get("content_sha256") or "")
        if content is not None and not sha:
            from context_cache import content_sha256 as csha

            sha = csha(content if isinstance(content, (str, bytes)) else json.dumps(content))
        raw_kind = str(c.get("artifact_kind") or c.get("kind") or "SOURCE").upper()
        from context_cache import ARTIFACT_KINDS

        kind = raw_kind if raw_kind in ARTIFACT_KINDS else "SOURCE"
        if store is None:
            misses += 1
            out.append({**c, "identity": identity, "content_sha256": sha, "cache": "miss"})
            continue
        key = {
            "repo_identity": repo_identity,
            "artifact_kind": kind,
            "scope_digest": scope_digest,
            "identity": identity,
            "content_sha256": sha,
            "extractor_version": extractor_version,
            "policy_digest": policy_digest_value,
        }
        hit = store.get_capsule(**key)
        if hit is not None:
            hits += 1
            out.append({**c, "identity": identity, "content_sha256": sha, "cache": "hit", "capsule": hit})
            continue
        # Stale if same identity exists with different sha handled by store counters
        if content is not None:
            store.put_capsule(**key, value={"summary": c.get("summary") or identity, "tokens": c.get("tokens") or 200})
        misses += 1
        out.append({**c, "identity": identity, "content_sha256": sha, "cache": "miss"})
    if store is not None:
        stale = int(getattr(store, "stale", 0) or 0)
    return out, hits, misses, stale


def issue_permit(
    *,
    dispatch_id: str,
    envelope: dict[str, Any],
    budget: dict[str, Any],
    status: str,
    reason: str | None = None,
) -> dict[str, Any]:
    st = status.upper()
    if st not in {"PERMITTED", "BLOCKED"}:
        raise ValueError("MODEL_DISPATCH_PERMIT_INVALID")
    permit = {
        "schema": PERMIT_SCHEMA,
        "dispatch_id": dispatch_id,
        "status": st,
        "context_envelope_digest": envelope.get("content_digest"),
        "budget_decision_digest": _sha(
            {k: budget[k] for k in ("schema", "policy_digest", "governance_profile", "status", "phases") if k in budget}
        ),
        "reason": reason,
        "created_at": _utc(),
    }
    permit["permit_digest"] = _sha(permit)
    return permit


def build_dispatch_record(
    *,
    dispatch_id: str,
    work_item_id: str,
    plan_id: str,
    todo_id: str,
    phase: str,
    cost_bucket: str,
    governance_profile: str,
    requested_tier: str,
    max_model_tier: str,
    agent_role: str,
    envelope: dict[str, Any],
    work_route_digest: str | None,
    policy_digest_value: str,
    budget_decision_digest: str,
    harness_adapter: str,
) -> dict[str, Any]:
    return {
        "schema": DISPATCH_SCHEMA,
        "dispatch_id": dispatch_id,
        "work_item_id": work_item_id,
        "plan_id": plan_id,
        "todo_id": todo_id,
        "phase": phase.upper(),
        "cost_bucket": cost_bucket.upper(),
        "governance_profile": governance_profile.upper(),
        "requested_tier": requested_tier,
        "max_model_tier": max_model_tier,
        "agent_role": agent_role,
        "context_envelope_digest": envelope.get("content_digest"),
        "work_route_digest": work_route_digest,
        "policy_digest": policy_digest_value,
        "budget_decision_digest": budget_decision_digest,
        "harness_adapter": harness_adapter,
        "created_at": _utc(),
    }


def prepare_dispatch(
    *,
    work_item_id: str,
    plan_id: str = "",
    todo_id: str = "",
    phase: str,
    governance_profile: str = "FULL",
    requested_tier: str = "STANDARD",
    agent_role: str = "worker",
    candidates: list[dict[str, Any]] | None = None,
    allowed_roots: list[str] | None = None,
    required_artifacts: list[dict[str, Any]] | None = None,
    structured_constraints: list[str] | None = None,
    review_depth: str | None = None,
    work_route_digest: str | None = None,
    feature_scope_digest: str | None = None,
    repo_identity: str | None = None,
    repo: Path | None = None,
    store: CapsuleStore | None = None,
    cost_bucket: str | None = None,
) -> dict[str, Any]:
    """Run trim → cache → budget → envelope → permit (no harness call yet)."""
    phase_u = phase.upper()
    bucket = (cost_bucket or phase_u).upper()
    if bucket == "IMPLEMENTATION":
        bucket = "IMPLEMENT"
    if phase_u == "IMPLEMENTATION":
        phase_u = "IMPLEMENT"
    cand = trim_candidates(list(candidates or []), allowed_roots=allowed_roots)
    pol_dig = policy_digest()
    scope = feature_scope_digest or work_route_digest or "scope:none"
    rid = repo_identity or "repo:unknown"
    capsule_store = store
    if capsule_store is None and repo is not None:
        capsule_store = CapsuleStore(repo=repo, work_item_id=work_item_id)
    capsules, hits, misses, stale = resolve_capsules(
        capsule_store,
        cand,
        repo_identity=rid,
        scope_digest=str(scope),
        policy_digest_value=pol_dig,
    )
    budget = decide_budget(
        work_item_id=work_item_id,
        repo_identity=rid,
        governance_profile=governance_profile,
        work_route_digest=work_route_digest,
        feature_scope_digest=feature_scope_digest,
        candidates=capsules,
    )
    envelope = build_envelope(
        phase=phase_u if phase_u in {"PLAN", "IMPLEMENT", "REVIEW", "GROUNDING", "ROUTING"} else "IMPLEMENT",
        plan_id=plan_id,
        todo_id=todo_id,
        governance_profile=budget.get("governance_profile") or governance_profile,
        required_artifacts=required_artifacts,
        source_capsules=[{"identity": c.get("identity"), "content_sha256": c.get("content_sha256"), "tokens": c.get("tokens") or 200} for c in capsules],
        structured_constraints=structured_constraints,
        allowed_roots=allowed_roots,
        cache_hits=hits,
        cache_misses=misses,
        review_depth=review_depth,
    )
    dispatch_id = uuid.uuid4().hex
    budget_dig = _sha(
        {k: budget[k] for k in ("schema", "policy_digest", "governance_profile", "status", "phases") if k in budget}
    )
    if budget.get("status") == "BLOCKED":
        permit = issue_permit(
            dispatch_id=dispatch_id,
            envelope=envelope,
            budget=budget,
            status="BLOCKED",
            reason=budget.get("error") or "CONTEXT_BUDGET_INSUFFICIENT",
        )
    else:
        permit = issue_permit(
            dispatch_id=dispatch_id,
            envelope=envelope,
            budget=budget,
            status="PERMITTED",
        )
    phase_limits = {p["name"]: p for p in budget.get("phases") or []}
    planning = phase_limits.get("planning") or phase_limits.get("implementation") or phase_limits.get("review") or {}
    max_tier = str(planning.get("max_model_tier") or requested_tier or "STANDARD")
    record = build_dispatch_record(
        dispatch_id=dispatch_id,
        work_item_id=work_item_id,
        plan_id=plan_id,
        todo_id=todo_id,
        phase=phase_u,
        cost_bucket=bucket,
        governance_profile=str(budget.get("governance_profile") or governance_profile),
        requested_tier=requested_tier,
        max_model_tier=max_tier,
        agent_role=agent_role,
        envelope=envelope,
        work_route_digest=work_route_digest,
        policy_digest_value=pol_dig,
        budget_decision_digest=budget_dig,
        harness_adapter="",
    )
    return {
        "dispatch": record,
        "permit": permit,
        "envelope": envelope,
        "budget": budget,
        "cache": {"hits": hits, "misses": misses, "stale": stale},
        "candidates": capsules,
    }


def require_permit(permit: dict[str, Any] | None, envelope: dict[str, Any] | None) -> None:
    if not permit or permit.get("schema") != PERMIT_SCHEMA:
        raise ValueError("MODEL_DISPATCH_PERMIT_MISSING")
    if permit.get("status") != "PERMITTED":
        raise ValueError(permit.get("reason") or "MODEL_DISPATCH_PERMIT_INVALID")
    if not envelope or not envelope.get("content_digest"):
        raise ValueError("CONTEXT_ENVELOPE_MISSING")
    if permit.get("context_envelope_digest") != envelope.get("content_digest"):
        raise ValueError("CONTEXT_ENVELOPE_STALE")


def run_managed_call(
    *,
    plan: Path,
    prepared: dict[str, Any],
    adapter: HarnessAdapter | None = None,
    prompt_meta: dict[str, Any] | None = None,
    emit_telemetry: bool = True,
) -> dict[str, Any]:
    """Execute a managed model call under permit; emit dispatch/result telemetry."""
    permit = prepared.get("permit") or {}
    envelope = prepared.get("envelope") or {}
    record = prepared.get("dispatch") or {}
    budget = prepared.get("budget") or {}
    cache = prepared.get("cache") or {}
    require_permit(permit, envelope)

    adapter = adapter or fake_enforced_adapter()
    mode = classify_mode(adapter.capability_map())
    if mode == MODE_UNMANAGED:
        raise ValueError("RUNTIME_COST_UNMANAGED")
    record = dict(record)
    record["harness_adapter"] = adapter.name

    rm = _import_runtime_metrics() if emit_telemetry else None
    dispatch_id = record["dispatch_id"]
    phase = record.get("phase") or "IMPLEMENT"
    if rm:
        rm.dispatch(
            plan,
            dispatch_id=dispatch_id,
            plan_id=record.get("plan_id") or "-",
            todo=record.get("todo_id") or "-",
            phase=phase,
            cost_bucket=record.get("cost_bucket") or phase,
            requested_tier=record.get("requested_tier") or "",
            agent=record.get("agent_role") or "",
            work_route_digest=record.get("work_route_digest"),
            policy_digest=record.get("policy_digest"),
            phase_allocated_tokens=envelope.get("estimated_tokens"),
            context_files_read=len(envelope.get("source_capsules") or []),
            unique_context_files=len(envelope.get("source_capsules") or []),
            repeated_context_reads=0,
            context_cache_hits=cache.get("hits"),
            context_cache_misses=cache.get("misses"),
            context_cache_stale=cache.get("stale"),
            context_envelope_digest=envelope.get("content_digest"),
            budget_decision_digest=record.get("budget_decision_digest"),
            permit_status=permit.get("status"),
            harness_mode=mode,
            managed=True,
            governance_profile=record.get("governance_profile"),
            review_depth=envelope.get("review_depth"),
            review_mode=envelope.get("review_depth"),
            budget_upgrade_reason=(budget.get("upgrades") or [None])[0] if budget.get("upgrades") else None,
            estimated_context_tokens=envelope.get("estimated_tokens"),
        )

    if adapter.call is None:
        if mode == MODE_OBSERVABLE:
            raise ValueError("RUNTIME_COST_OBSERVABLE_NOT_ENFORCED")
        raise ValueError("HARNESS_COST_CAPABILITY_MISSING")

    result_payload = adapter.call(
        dispatch_id=dispatch_id,
        envelope=envelope,
        requested_tier=record.get("requested_tier"),
        prompt_meta=prompt_meta or {},
        allowed_roots=envelope.get("allowed_roots") or [],
    )
    usage_unavailable = result_payload.get("usage_unavailable_reason")
    result_fields: dict[str, Any] = {
        "dispatch_id": dispatch_id,
        "actual_tier": result_payload.get("actual_tier") or record.get("requested_tier") or "STANDARD",
        "provider": result_payload.get("provider") or "unknown",
        "model": result_payload.get("model") or "unknown",
        "outcome": result_payload.get("outcome") or "OK",
        "retry_count": int(result_payload.get("retry_count") or 0),
        "latency_ms": int(result_payload.get("latency_ms") or 0),
        "phase_actual_tokens": result_payload.get("phase_actual_tokens"),
        "estimated_context_tokens": envelope.get("estimated_tokens"),
        "harness_mode": mode,
        "managed": True,
    }
    if usage_unavailable:
        result_fields["usage_unavailable_reason"] = usage_unavailable
    else:
        for k in ("prompt_tokens", "completion_tokens", "cache_read_tokens", "cache_write_tokens"):
            if k in result_payload:
                result_fields[k] = result_payload[k]
        if not any(k in result_fields for k in ("prompt_tokens", "completion_tokens", "cache_read_tokens", "cache_write_tokens")):
            result_fields["usage_unavailable_reason"] = "TOKEN_ACCOUNTING_UNAVAILABLE"

    if rm:
        rm.result(plan, **{k: v for k, v in result_fields.items() if v is not None or k == "usage_unavailable_reason"})

    return {
        "dispatch": record,
        "permit": permit,
        "envelope": envelope,
        "budget": budget,
        "harness_mode": mode,
        "result": result_fields,
        "response": result_payload.get("response"),
    }


def self_check_modules() -> dict[str, bool]:
    """Install-identity probe helper for v5.0.9 feature slice."""
    return {
        "model_dispatch": True,
        "context_envelope": (HERE / "context_envelope.py").is_file(),
        "stage_cost_closure": (HERE / "stage_cost_closure.py").is_file(),
        "harness_contract": (HERE / "harness_contract.py").is_file(),
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="GES v5.0.9 model dispatch runtime")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--work-item-id", required=True)
    p.add_argument("--plan-id", default="")
    p.add_argument("--todo-id", default="")
    p.add_argument("--phase", default="IMPLEMENT")
    p.add_argument("--governance-profile", default="FULL")
    p.add_argument("--requested-tier", default="STANDARD")
    p.add_argument("--agent-role", default="worker")
    p.add_argument("--candidates-json", type=Path)
    p.add_argument("--repo", type=Path)
    p.add_argument("--review-depth", default="")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("self-check")
    p.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.cmd == "self-check":
        out = self_check_modules()
        print(json.dumps(out, indent=2) if a.json else out)
        return 0 if all(out.values()) else 1
    candidates = json.loads(a.candidates_json.read_text(encoding="utf-8")) if a.candidates_json else []
    prepared = prepare_dispatch(
        work_item_id=a.work_item_id,
        plan_id=a.plan_id,
        todo_id=a.todo_id,
        phase=a.phase,
        governance_profile=a.governance_profile,
        requested_tier=a.requested_tier,
        agent_role=a.agent_role,
        candidates=candidates,
        repo=a.repo.resolve() if a.repo else None,
        review_depth=a.review_depth or None,
    )
    out = {
        "dispatch": prepared["dispatch"],
        "permit": prepared["permit"],
        "envelope_digest": prepared["envelope"].get("content_digest"),
        "budget_status": prepared["budget"].get("status"),
        "cache": prepared["cache"],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) if a.json else out)
    return 0 if prepared["permit"]["status"] == "PERMITTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
