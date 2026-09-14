"""Token budget manager. Mandatory content cannot be truncated into READY."""
from __future__ import annotations

from typing import Any

SCOPE_CAPS = {
    "COMPONENT": 20000,
    "MODULE": 80000,
    "PROJECT": 200000,
    "ARCHITECTURE": 400000,
}


def available_tokens(
    *,
    model_window: int,
    system_tokens: int = 0,
    tool_reserve: int = 0,
    output_reserve: int = 0,
    safety_margin: int = 0,
    policy_cap: int | None = None,
    scope_level: str = "MODULE",
) -> int:
    scene = SCOPE_CAPS.get(str(scope_level).upper(), SCOPE_CAPS["MODULE"])
    window = max(0, int(model_window) - int(system_tokens) - int(tool_reserve) - int(output_reserve) - int(safety_margin))
    cap = min(scene, window)
    if policy_cap is not None:
        cap = min(cap, int(policy_cap))
    return max(0, cap)


def plan_budget(items: list[dict[str, Any]], budget: int) -> dict[str, Any]:
    mandatory = [i for i in items if i.get("mandatory")]
    optional = [i for i in items if not i.get("mandatory")]
    used = 0
    selected: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for item in mandatory:
        cost = int(item.get("estimated_tokens") or 0)
        if used + cost > budget:
            return {
                "status": "BLOCKED",
                "reason": "CONTEXT_MANDATORY_OVER_BUDGET",
                "selected": selected,
                "excluded": excluded + optional,
                "segments": _segments(mandatory, budget),
                "used": used,
                "budget": budget,
            }
        selected.append(item)
        used += cost
    for item in optional:
        cost = int(item.get("estimated_tokens") or 0)
        if used + cost > budget:
            excluded.append({**item, "exclude_reason": "budget"})
            continue
        selected.append(item)
        used += cost
    return {
        "status": "OK",
        "reason": "",
        "selected": selected,
        "excluded": excluded,
        "segments": [],
        "used": used,
        "budget": budget,
    }


def _segments(mandatory: list[dict[str, Any]], budget: int) -> list[list[str]]:
    if budget <= 0:
        return []
    groups: list[list[str]] = []
    current: list[str] = []
    used = 0
    for item in mandatory:
        cost = int(item.get("estimated_tokens") or 0)
        ident = str(item.get("id") or item.get("path") or "")
        if cost > budget:
            groups.append([ident])
            current, used = [], 0
            continue
        if used + cost > budget and current:
            groups.append(current)
            current, used = [], 0
        current.append(ident)
        used += cost
    if current:
        groups.append(current)
    return groups
