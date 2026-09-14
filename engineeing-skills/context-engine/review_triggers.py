"""Review provider triggers. Canonical review owners stay unchanged."""
from __future__ import annotations

from typing import Any

PROVIDERS = {
    "MODULE": "smc-plan-review",
    "INTEGRATION": "smc-plan-review",
    "ARCHITECTURE": "smc-architecture-review",
}


def triggers(impact: dict[str, Any]) -> list[dict[str, str]]:
    reviews = list((impact.get("affected") or {}).get("reviews") or [])
    out = []
    for kind in ("MODULE", "INTEGRATION", "ARCHITECTURE"):
        if kind in reviews:
            out.append({"kind": kind, "provider": PROVIDERS[kind], "owner": PROVIDERS[kind]})
    return out


def release_blocked(impact: dict[str, Any], completed: set[str]) -> bool:
    needed = {row["kind"] for row in triggers(impact)}
    return not needed.issubset(completed)
