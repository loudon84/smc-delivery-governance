"""Scope resolver: Registry + facts override model/prompt candidates. Risk stays orthogonal."""
from __future__ import annotations

from typing import Any

from registry import Registry, write_owner


RISK_FULL = (
    "public_contract",
    "security_boundary",
    "schema_migration",
    "protocol_change",
    "new_owner",
    "lifecycle_change",
    "cross_domain_ownership",
    "live_acceptance",
)


def prompt_cannot_ungovern(facts: dict[str, Any]) -> bool:
    prompt = str(facts.get("prompt") or facts.get("task_prompt") or "").lower()
    claimed_research = "just research" in prompt or "only research" in prompt or "low risk" in prompt
    governed = facts.get("governed") is True or facts.get("retained_production_change") is True
    production = facts.get("production_write_requested") is True or facts.get("durable_product_artifact_requested") is True
    if claimed_research and (governed or production):
        return True
    return False


def suggest_scope(facts: dict[str, Any], registry: Registry | None = None, paths: list[str] | None = None) -> dict[str, Any]:
    reasons: list[str] = []
    modules: list[str] = []
    unknown = False
    for path in paths or list(facts.get("candidate_paths") or []):
        if registry is None:
            unknown = True
            continue
        owner = write_owner(registry, path)
        if owner:
            modules.append(owner)
        else:
            unknown = True
            reasons.append(f"unresolved:{path}")
    modules = sorted(set(modules))
    scope = "COMPONENT"
    if len(modules) == 1:
        scope = "MODULE"
    elif len(modules) > 1:
        scope = "PROJECT"
    if unknown or not modules:
        scope = "PROJECT"
        reasons.append("CONTEXT_SCOPE_UNRESOLVED")
    risk_full = any(facts.get(k) is True for k in RISK_FULL)
    if prompt_cannot_ungovern(facts):
        reasons.append("PROMPT_CANNOT_OVERRIDE_GOVERNED")
        risk_full = True
    production_locked = (
        facts.get("retained_production_change") is True
        or facts.get("production_write_requested") is True
        or facts.get("durable_product_artifact_requested") is True
    )
    if facts.get("governed") is False and production_locked:
        facts = dict(facts)
        facts["governed"] = True
        reasons.append("PROMPT_CANNOT_SET_GOVERNED_FALSE")
        risk_full = True
    return {
        "scope_level": scope,
        "modules": modules,
        "components": list(facts.get("components") or []),
        "confidence": "high" if modules and not unknown else "low",
        "upgrade_reasons": reasons,
        "risk_full": risk_full,
        "unknown": unknown,
    }
