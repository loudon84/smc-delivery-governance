"""Stage cost closure gate (smc.ges.stage-cost-closure.v1).

PLANNING / IMPLEMENTATION / REVIEW must prove paired telemetry, budget permit,
envelope presence, and no unmanaged model calls before claiming cost PASS.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
_DELIVERY = HERE.parent / ".agents" / "skills" / "smc-plan-delivery" / "scripts"

SCHEMA = "smc.ges.stage-cost-closure.v1"
STAGES = frozenset({"PLANNING", "IMPLEMENTATION", "REVIEW"})


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _import_runtime_metrics():
    if str(_DELIVERY) not in sys.path:
        sys.path.insert(0, str(_DELIVERY))
    import runtime_metrics as rm  # noqa: WPS433

    return rm


def evaluate_stage(
    *,
    plan: Path,
    stage: str,
    context_envelope_digest: str | None = None,
    policy_digest: str | None = None,
    budget_status: str | None = None,
    allocated_tokens: int | None = None,
    allow_observable: bool = False,
) -> dict[str, Any]:
    """Return stage-cost-closure.v1 with PASS / PASS_USAGE_UNAVAILABLE / BLOCKED."""
    stage_u = stage.strip().upper()
    if stage_u not in STAGES:
        raise ValueError("STAGE_COST_CLOSURE_STAGE_INVALID")
    rm = _import_runtime_metrics()
    path = rm.telemetry_path(plan)
    events: list[dict[str, Any]] = []
    if path.is_file():
        events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    phase_aliases = {
        "PLANNING": {"PLAN", "GROUNDING", "PLANNING"},
        "IMPLEMENTATION": {"IMPLEMENT", "IMPLEMENTATION", "TDD", "DEBUG"},
        "REVIEW": {"REVIEW"},
    }
    aliases = phase_aliases[stage_u]
    stage_dispatches = {
        e.get("dispatch_id"): e
        for e in events
        if e.get("kind") == "dispatch"
        and e.get("dispatch_id")
        and (
            str(e.get("phase") or "").upper() in aliases
            or str(e.get("cost_bucket") or "").upper() in aliases
        )
    }
    if not stage_dispatches:
        # Fall back to all dispatches when stage tags are absent.
        stage_dispatches = {
            e.get("dispatch_id"): e for e in events if e.get("kind") == "dispatch" and e.get("dispatch_id")
        }
    dispatches = stage_dispatches
    results = [
        e
        for e in events
        if e.get("kind") == "result" and e.get("dispatch_id") in dispatches
    ]
    scoped = list(dispatches.values()) + results
    result_ids = {e.get("dispatch_id") for e in results if e.get("dispatch_id")}
    unpaired_dispatches = [did for did in dispatches if did not in result_ids]
    orphan_results = []  # results already filtered to known stage dispatches
    unmanaged_calls = [
        e
        for e in scoped
        if e.get("unmanaged_call") or e.get("harness_mode") == "UNMANAGED" or e.get("managed") is False
    ]
    observable = [e for e in scoped if e.get("harness_mode") == "OBSERVABLE"]
    cache_hits = sum(int(e.get("context_cache_hits") or e.get("source_context_hits") or 0) for e in scoped)
    cache_misses = sum(int(e.get("context_cache_misses") or e.get("source_context_misses") or 0) for e in scoped)
    cache_stale = sum(int(e.get("context_cache_stale") or 0) for e in scoped)
    env_digest = context_envelope_digest or next(
        (e.get("context_envelope_digest") for e in scoped if e.get("context_envelope_digest")), None
    )
    pol_digest = policy_digest or next((e.get("policy_digest") for e in scoped if e.get("policy_digest")), None)
    allocated = allocated_tokens
    if allocated is None:
        allocated = sum(int(e.get("phase_allocated_tokens") or e.get("estimated_context_tokens") or 0) for e in scoped)
    actual = sum(int(e.get("phase_actual_tokens") or 0) for e in scoped)
    for e in results:
        if e.get("prompt_tokens") is not None:
            actual += int(e.get("prompt_tokens") or 0) + int(e.get("completion_tokens") or 0)

    usage_unavailable = all(
        bool(e.get("usage_unavailable_reason")) for e in results
    ) if results else False
    usage_status = "UNAVAILABLE" if usage_unavailable else ("AVAILABLE" if results else "UNAVAILABLE")

    reasons: list[str] = []
    status = "PASS"
    if unpaired_dispatches or orphan_results:
        status = "BLOCKED"
        reasons.append("TELEMETRY_DISPATCH_UNPAIRED")
    if unmanaged_calls:
        status = "BLOCKED"
        reasons.append("RUNTIME_COST_UNMANAGED")
    if observable and not allow_observable:
        status = "BLOCKED"
        reasons.append("RUNTIME_COST_OBSERVABLE_NOT_ENFORCED")
    if not env_digest and dispatches:
        status = "BLOCKED"
        reasons.append("CONTEXT_ENVELOPE_MISSING")
    if budget_status == "BLOCKED":
        status = "BLOCKED"
        reasons.append("CONTEXT_BUDGET_INSUFFICIENT")
    if not dispatches:
        status = "BLOCKED"
        reasons.append("MODEL_DISPATCH_PERMIT_MISSING")
    for e in results:
        if not e.get("provider") and not e.get("model") and not e.get("model_identity_unavailable"):
            status = "BLOCKED"
            reasons.append("TELEMETRY_MODEL_IDENTITY_MISSING")
            break
    if status == "PASS" and usage_unavailable:
        if allocated and unpaired_dispatches == []:
            status = "PASS_USAGE_UNAVAILABLE"
        else:
            status = "BLOCKED"
            reasons.append("TELEMETRY_USAGE_UNAVAILABLE")

    out = {
        "schema": SCHEMA,
        "stage": stage_u,
        "dispatch_count": len(dispatches),
        "result_count": len(results),
        "unpaired_dispatches": unpaired_dispatches,
        "unmanaged_calls": len(unmanaged_calls),
        "budget_status": budget_status or ("OK" if status.startswith("PASS") else "BLOCKED"),
        "allocated_tokens": allocated,
        "actual_tokens": actual if usage_status == "AVAILABLE" else None,
        "usage_status": usage_status,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "cache_stale": cache_stale,
        "context_envelope_digest": env_digest,
        "policy_digest": pol_digest,
        "status": status,
        "reasons": reasons,
        "generated_at": _utc(),
    }
    if status == "BLOCKED":
        out["error"] = reasons[0] if reasons else "STAGE_COST_CLOSURE_FAILED"
    return out


def persist_closure(repo: Path, work_item_id: str, closure: dict[str, Any]) -> Path:
    stage = str(closure.get("stage") or "STAGE").lower()
    out = repo / ".smc" / "runs" / work_item_id / f"stage-cost-closure-{stage}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(closure, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def require_pass(closure: dict[str, Any]) -> None:
    if closure.get("status") not in {"PASS", "PASS_USAGE_UNAVAILABLE"}:
        raise ValueError(closure.get("error") or "STAGE_COST_CLOSURE_FAILED")
