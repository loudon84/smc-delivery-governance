from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ges.errors import MANAGED_CONTENT_MODIFIED, GesError
from ges.io import sha256_bytes, sha256_file
from ges.legacy.v5 import LegacyReport
from ges.paths import PRESERVE_ALWAYS, to_posix
from ges.reconciler.guard import assert_allowed, assert_not_business_source
from ges.reconciler.state import read_receipt
from ges.source_adapters.base import ProjectedFile

ADD = "ADD"
UPDATE = "UPDATE"
REMOVE = "REMOVE"
PRESERVE = "PRESERVE"
CONFLICT = "CONFLICT"


@dataclass
class PlanEntry:
    path: str
    action: str
    kind: str
    capability: str | None = None


@dataclass
class InstallPlan:
    entries: list[PlanEntry] = field(default_factory=list)
    source_shas: dict[str, str] = field(default_factory=dict)
    legacy_report: dict[str, Any] = field(default_factory=dict)
    business_source_guard: dict[str, Any] = field(default_factory=dict)
    skills_to_add: list[str] = field(default_factory=list)
    skills_to_remove: list[str] = field(default_factory=list)
    managed_sections_to_add: list[str] = field(default_factory=list)

    @property
    def noop(self) -> bool:
        return not any(entry.action in {ADD, UPDATE, REMOVE} for entry in self.entries)

    def changing(self) -> list[PlanEntry]:
        return [entry for entry in self.entries if entry.action in {ADD, UPDATE, REMOVE}]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "ges.install-plan.v1",
            "files_to_create": [e.path for e in self.entries if e.action == ADD],
            "files_to_update": [e.path for e in self.entries if e.action == UPDATE],
            "managed_sections_to_add": self.managed_sections_to_add,
            "skills_to_add": self.skills_to_add,
            "skills_to_remove": self.skills_to_remove,
            "source_shas": self.source_shas,
            "legacy_report": self.legacy_report,
            "business_source_guard": self.business_source_guard,
            "entries": [entry.__dict__ for entry in self.entries],
            "noop": self.noop,
        }


def build_plan(
    repo: Path,
    desired: dict[str, ProjectedFile],
    *,
    source_shas: dict[str, str],
    legacy: LegacyReport,
    business_guard: dict[str, Any],
) -> InstallPlan:
    receipt = read_receipt(repo) or {}
    hashes = receipt.get("content_hashes") or {}
    managed_files = set(receipt.get("managed_files") or [])
    plan = InstallPlan(
        source_shas=source_shas,
        legacy_report=legacy.to_dict(),
        business_source_guard=business_guard,
    )
    for rel, item in sorted(desired.items()):
        assert_allowed(rel)
        assert_not_business_source(rel)
        if any(to_posix(rel).startswith(prefix) for prefix in PRESERVE_ALWAYS):
            plan.entries.append(PlanEntry(rel, PRESERVE, item.kind, item.capability))
            continue
        current = repo / rel
        last = (hashes.get(rel) or {}).get("last_applied")
        generated = sha256_bytes(item.content)
        if not current.exists():
            plan.entries.append(PlanEntry(rel, ADD, item.kind, item.capability))
            if item.kind == "skill" and item.capability:
                skill = rel.split("/")[2] if rel.startswith(".agents/skills/") else item.capability
                if skill not in plan.skills_to_add:
                    plan.skills_to_add.append(skill)
            if rel == "AGENTS.md":
                plan.managed_sections_to_add.append("engineering-stack")
            continue
        current_hash = sha256_file(current)
        if current_hash == generated:
            plan.entries.append(PlanEntry(rel, PRESERVE, item.kind, item.capability))
            continue
        if last and current_hash != last:
            raise GesError(
                MANAGED_CONTENT_MODIFIED,
                f"managed content was modified: {rel}",
            )
        if last == generated:
            plan.entries.append(PlanEntry(rel, PRESERVE, item.kind, item.capability))
            continue
        plan.entries.append(PlanEntry(rel, UPDATE, item.kind, item.capability))

    for rel in sorted(managed_files):
        if rel in desired:
            continue
        if (repo / rel).exists():
            plan.entries.append(PlanEntry(rel, REMOVE, "managed", None))
            if rel.startswith(".agents/skills/"):
                skill = rel.split("/")[2]
                if skill not in plan.skills_to_remove:
                    plan.skills_to_remove.append(skill)
    return plan
