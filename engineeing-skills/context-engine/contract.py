"""Plan contract negotiation: required context_binding and legacy execution rejection."""
from __future__ import annotations

from typing import Any

from coe_common import CURRENT_PLAN_CONTRACT, LEGACY_PLAN_CONTRACTS

REQUIRED_CAPABILITY = "context_binding"


def frontmatter_capabilities(fm: dict[str, str]) -> list[str]:
    caps: list[str] = []
    raw = str(fm.get("required_extensions") or fm.get("required_capabilities") or "").strip()
    if raw:
        caps.extend(x.strip() for x in raw.replace(";", ",").split(",") if x.strip())
    binding = str(fm.get(REQUIRED_CAPABILITY) or "").strip().lower()
    if binding in {"required", "true", "1", "yes"}:
        caps.append(REQUIRED_CAPABILITY)
    return caps


def validator_capability_errors(fm: dict[str, str], expected_contract: str) -> list[dict[str, str]]:
    caps = frontmatter_capabilities(fm)
    if REQUIRED_CAPABILITY in caps and expected_contract != CURRENT_PLAN_CONTRACT:
        return [
            {
                "code": "PLAN_REQUIRED_CAPABILITY_UNSUPPORTED",
                "detail": REQUIRED_CAPABILITY,
            }
        ]
    return []


def runtime_plan_errors(contract: str) -> list[str]:
    if contract == CURRENT_PLAN_CONTRACT:
        return []
    if contract in LEGACY_PLAN_CONTRACTS or contract:
        return [f"CONTEXT_LEGACY_PLAN_UNSUPPORTED: {contract or 'missing'}"]
    return ["CONTEXT_LEGACY_PLAN_UNSUPPORTED: missing"]


def context_binding_errors(fm: dict[str, str]) -> list[dict[str, str]]:
    if fm.get("plan_contract") != CURRENT_PLAN_CONTRACT:
        return []
    if str(fm.get(REQUIRED_CAPABILITY) or "").strip().lower() not in {"required", "true", "1", "yes"}:
        return [{"code": "PLAN_CONTEXT_BINDING_MISSING", "detail": REQUIRED_CAPABILITY}]
    return []
