from __future__ import annotations

from typing import Any

from ges.compose import ComposeContext
from ges.legacy.v5 import LegacyReport


def render_init(ctx: ComposeContext, legacy: LegacyReport) -> str:
    existing = ctx.profile.get("existing") or {}
    lines = [
        "Repository analysis",
        "-------------------",
        "",
        "Repository:",
        f"  {ctx.profile.get('repository_kind')}",
        "",
        "Detected agents:",
    ]
    for agent in ctx.profile.get("agents") or ["(none)"]:
        lines.append(f"  {agent.capitalize() if isinstance(agent, str) else agent}")
    lines += [
        "",
        "Existing:",
        f"  AGENTS.md        {_yes(existing.get('AGENTS.md'))}",
        f"  .agents/         {_yes(existing.get('.agents'))}",
        f"  .cursor/         {_yes(existing.get('.cursor'))}",
        f"  .codex/          {_yes(existing.get('.codex'))}",
        f"  .specify/        {_yes(existing.get('.specify'))}",
        f"  Legacy GES v5    {_yes(legacy.detected)}",
        "",
        "Recommended engineering composition",
        "------------------------------------",
        "",
        "Matt:",
    ]
    lines.extend(_group(ctx, "matt."))
    lines += ["", "Spec Kit:"]
    lines.extend(_group(ctx, "speckit."))
    lines += ["", "Superpowers:"]
    lines.extend(_group(ctx, "superpowers."))
    excluded = [
        item
        for item in ctx.resolution.excluded
        if item in ctx.catalog.capabilities and ctx.catalog.get(item).projection_type != "virtual"
    ]
    if excluded:
        lines += ["", "Excluded due to ownership overlap:"]
        for item in excluded:
            lines.append(f"  - {item}")
    if legacy.detected:
        lines += [
            "",
            "Legacy GES v5 detected.",
            "No legacy files will be removed automatically.",
        ]
    if ctx.resolution.conflicts:
        lines += ["", "CAPABILITY_OWNERSHIP_CONFLICT"]
        for item in ctx.resolution.conflicts:
            lines.append(f"  {item['left']} vs {item['right']}")
    return "\n".join(lines) + "\n"


def render_plan(plan_dict: dict[str, Any]) -> str:
    lines = ["Install plan", "------------"]
    for key in (
        "files_to_create",
        "files_to_update",
        "managed_sections_to_add",
        "skills_to_add",
        "skills_to_remove",
    ):
        items = plan_dict.get(key) or []
        lines.append(f"{key}: {len(items)}")
        for item in items[:20]:
            lines.append(f"  {item}")
    lines.append("source_shas:")
    for name, sha in (plan_dict.get("source_shas") or {}).items():
        lines.append(f"  {name}: {sha}")
    lines.append(f"noop: {plan_dict.get('noop')}")
    return "\n".join(lines) + "\n"


def _group(ctx: ComposeContext, prefix: str) -> list[str]:
    lines = []
    for cap_id in ctx.resolution.closed:
        if cap_id.startswith(prefix) and ctx.catalog.get(cap_id).projection_type != "virtual":
            short = cap_id.split(".", 1)[1]
            lines.append(f"  + {short}")
    return lines or ["  (none)"]


def _yes(value: bool) -> str:
    return "YES" if value else "NO"
