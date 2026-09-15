"""Minimal context envelopes for GES-managed model calls (smc.ges.context-envelope.v1).

Default inputs are phase-scoped artifacts and capsules — never full repo dumps,
full Plans, or full session history.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "smc.ges.context-envelope.v1"
PHASES = frozenset({"PLAN", "IMPLEMENT", "REVIEW", "GROUNDING", "ROUTING"})


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _digest(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def estimate_tokens(candidates: list[dict[str, Any]]) -> int:
    total = sum(int(c.get("tokens") or c.get("approx_tokens") or 0) for c in candidates)
    if total <= 0:
        total = len(candidates) * 200
    return total


def build_envelope(
    *,
    phase: str,
    plan_id: str = "",
    todo_id: str = "",
    governance_profile: str = "FULL",
    required_artifacts: list[dict[str, Any]] | None = None,
    source_capsules: list[dict[str, Any]] | None = None,
    structured_constraints: list[str] | None = None,
    allowed_roots: list[str] | None = None,
    allowed_symbols: list[str] | None = None,
    forbidden_roots: list[str] | None = None,
    cache_hits: int = 0,
    cache_misses: int = 0,
    review_depth: str | None = None,
) -> dict[str, Any]:
    """Assemble a phase-scoped context envelope with content digest."""
    ph = (phase or "").strip().upper()
    if ph not in PHASES:
        raise ValueError("CONTEXT_ENVELOPE_PHASE_INVALID")
    artifacts = list(required_artifacts or [])
    capsules = list(source_capsules or [])
    # Fail closed: refuse obvious full-dump markers
    for item in artifacts + capsules:
        kind = str(item.get("kind") or item.get("artifact_kind") or "").upper()
        if kind in {"FULL_REPO", "FULL_PLAN", "FULL_HISTORY", "SESSION_DUMP"}:
            raise ValueError("CONTEXT_SCOPE_VIOLATION")
    forbidden = list(forbidden_roots or ["**/.git/**", "**/node_modules/**"])
    body = {
        "schema": SCHEMA,
        "phase": ph,
        "plan_id": plan_id or "",
        "todo_id": todo_id or "",
        "governance_profile": (governance_profile or "FULL").upper(),
        "required_artifacts": artifacts,
        "source_capsules": capsules,
        "structured_constraints": list(structured_constraints or []),
        "allowed_roots": [r.replace("\\", "/").rstrip("/") for r in (allowed_roots or [])],
        "allowed_symbols": list(allowed_symbols or []),
        "forbidden_roots": forbidden,
        "estimated_tokens": estimate_tokens(artifacts + capsules),
        "cache_hits": int(cache_hits),
        "cache_misses": int(cache_misses),
        "review_depth": (review_depth or "").upper() or None,
        "generated_at": _utc(),
    }
    body["content_digest"] = _digest({k: body[k] for k in body if k != "generated_at"})
    return body


def plan_envelope(
    *,
    plan_id: str,
    governance_profile: str,
    prd_summary: dict[str, Any] | None = None,
    routing_facts: dict[str, Any] | None = None,
    owner_capsules: list[dict[str, Any]] | None = None,
    unresolved_decisions: list[dict[str, Any]] | None = None,
    allowed_roots: list[str] | None = None,
    cache_hits: int = 0,
    cache_misses: int = 0,
) -> dict[str, Any]:
    artifacts: list[dict[str, Any]] = []
    if prd_summary:
        artifacts.append({"kind": "PRD_SUMMARY", **prd_summary})
    if routing_facts:
        artifacts.append({"kind": "ROUTING_FACTS", **routing_facts})
    for d in unresolved_decisions or []:
        artifacts.append({"kind": "UNRESOLVED_DECISION", **d})
    return build_envelope(
        phase="PLAN",
        plan_id=plan_id,
        governance_profile=governance_profile,
        required_artifacts=artifacts,
        source_capsules=list(owner_capsules or []),
        structured_constraints=["deterministic_seed_first", "structured_patch_only"],
        allowed_roots=allowed_roots,
        cache_hits=cache_hits,
        cache_misses=cache_misses,
    )


def implement_envelope(
    *,
    plan_id: str,
    todo_id: str,
    governance_profile: str,
    write_paths: list[str] | None = None,
    read_paths: list[str] | None = None,
    symbols: list[str] | None = None,
    verification: list[str] | None = None,
    engineering_method: str | None = None,
    capsules: list[dict[str, Any]] | None = None,
    cache_hits: int = 0,
    cache_misses: int = 0,
) -> dict[str, Any]:
    writes = [p.replace("\\", "/") for p in (write_paths or [])]
    reads = [p.replace("\\", "/") for p in (read_paths or [])]
    artifacts = [
        {"kind": "TASK_BRIEF", "todo_id": todo_id},
        {"kind": "WRITE_TARGETS", "paths": writes},
        {"kind": "READ_TARGETS", "paths": reads},
    ]
    if verification:
        artifacts.append({"kind": "VERIFICATION", "entries": list(verification)})
    if engineering_method:
        artifacts.append({"kind": "ENGINEERING_METHOD", "profile": engineering_method})
    roots = sorted(set(writes + reads))
    return build_envelope(
        phase="IMPLEMENT",
        plan_id=plan_id,
        todo_id=todo_id,
        governance_profile=governance_profile,
        required_artifacts=artifacts,
        source_capsules=list(capsules or []),
        structured_constraints=["task_brief_only", "no_full_plan"],
        allowed_roots=roots,
        allowed_symbols=list(symbols or []),
        cache_hits=cache_hits,
        cache_misses=cache_misses,
    )


def review_envelope(
    *,
    plan_id: str,
    governance_profile: str,
    review_depth: str,
    findings: list[dict[str, Any]] | None = None,
    changed_sections: list[str] | None = None,
    affected_capsules: list[dict[str, Any]] | None = None,
    blocking_acceptance: list[str] | None = None,
    cache_hits: int = 0,
    cache_misses: int = 0,
) -> dict[str, Any]:
    depth = (review_depth or "FULL").upper()
    artifacts = [
        {"kind": "REVIEW_MODE", "depth": depth},
        {"kind": "FINDINGS", "items": list(findings or [])},
        {"kind": "CHANGED_SECTIONS", "sections": list(changed_sections or [])},
    ]
    if blocking_acceptance:
        artifacts.append({"kind": "BLOCKING_ACCEPTANCE", "items": list(blocking_acceptance)})
    return build_envelope(
        phase="REVIEW",
        plan_id=plan_id,
        governance_profile=governance_profile,
        required_artifacts=artifacts,
        source_capsules=list(affected_capsules or []),
        structured_constraints=["delta_first" if depth == "DELTA" else "full_first"],
        review_depth=depth,
        cache_hits=cache_hits,
        cache_misses=cache_misses,
    )


def persist_envelope(repo: Path, work_item_id: str, envelope: dict[str, Any], name: str = "context-envelope.json") -> Path:
    out = repo / ".smc" / "runs" / work_item_id / name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(envelope, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def load_envelope(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError("CONTEXT_ENVELOPE_MISSING")
    return data


def assert_envelope_fresh(envelope: dict[str, Any], expected_digest: str | None) -> None:
    """Fail closed when a bound permit/digest no longer matches the envelope body."""
    if not envelope or not envelope.get("content_digest"):
        raise ValueError("CONTEXT_ENVELOPE_MISSING")
    if not expected_digest:
        raise ValueError("CONTEXT_ENVELOPE_MISSING")
    if envelope.get("content_digest") != expected_digest:
        raise ValueError("CONTEXT_ENVELOPE_STALE")
