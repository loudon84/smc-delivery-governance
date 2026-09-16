from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ges import __version__
from ges.errors import (
    BUSINESS_SOURCE_MODIFICATION_FORBIDDEN,
    GES_RECONCILE_NOOP,
    GesError,
)
from ges.harness_adapters.agents_md import section_hash
from ges.io import sha256_file, write_bytes
from ges.reconciler.guard import assert_allowed, assert_not_business_source, contain
from ges.reconciler.hashes import hash_record
from ges.reconciler.plan import ADD, REMOVE, UPDATE, InstallPlan
from ges.reconciler.state import write_lock, write_project, write_receipt
from ges.source_adapters.base import ProjectedFile
from ges.stagelog import RECONCILE, emit


def snapshot_business_sources(repo: Path) -> dict[str, dict[str, Any]]:
    from ges.analyzer.source_roots import iter_business_files

    snap: dict[str, dict[str, Any]] = {}
    for path in iter_business_files(repo):
        rel = path.relative_to(repo).as_posix()
        snap[rel] = {"size": path.stat().st_size, "sha256": sha256_file(path)}
    return snap


def assert_business_unchanged(repo: Path, before: dict[str, dict[str, Any]]) -> None:
    after = snapshot_business_sources(repo)
    if after != before:
        raise GesError(
            BUSINESS_SOURCE_MODIFICATION_FORBIDDEN,
            "business source bytes changed during Composer apply",
        )


def apply_plan(
    repo: Path,
    plan: InstallPlan,
    desired: dict[str, ProjectedFile],
    *,
    project: dict[str, Any],
    profile: dict[str, Any],
    lock: dict[str, Any],
    force_noop_code: bool = True,
) -> dict[str, Any]:
    emit(RECONCILE, "start", repo=str(repo), noop=plan.noop)
    if plan.noop:
        if force_noop_code:
            raise GesError(GES_RECONCILE_NOOP, "desired state already matches current state")
        return read_or_empty_receipt(repo)

    before = snapshot_business_sources(repo)
    backups: dict[str, bytes | None] = {}
    created: list[str] = []
    try:
        for entry in plan.changing():
            assert_allowed(entry.path)
            assert_not_business_source(entry.path)
            target = contain(repo, entry.path)
            if target.exists() and target.is_file():
                backups[entry.path] = target.read_bytes()
            else:
                backups[entry.path] = None
            if entry.action == REMOVE:
                if target.exists():
                    target.unlink()
                continue
            item = desired[entry.path]
            write_bytes(target, item.content)
            if backups[entry.path] is None:
                created.append(entry.path)
        write_project(repo, project)
        write_lock(repo, lock)
        receipt = build_receipt(repo, desired, profile, lock)
        write_receipt(repo, receipt)
        assert_business_unchanged(repo, before)
    except Exception:
        _rollback(repo, backups, created)
        raise
    emit(RECONCILE, "applied", changed=len(plan.changing()))
    return receipt


def build_receipt(
    repo: Path,
    desired: dict[str, ProjectedFile],
    profile: dict[str, Any],
    lock: dict[str, Any],
) -> dict[str, Any]:
    hashes = {rel: hash_record(item) for rel, item in desired.items()}
    sections = []
    if "AGENTS.md" in desired:
        text = desired["AGENTS.md"].content.decode("utf-8")
        sections.append(
            {
                "id": "engineering-stack",
                "path": "AGENTS.md",
                "last_applied": section_hash(text),
            }
        )
    return {
        "schema": "ges.install-receipt.v1",
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "ges_version": __version__,
        "repo_identity": {
            "path": str(repo.resolve()),
            "kind": profile.get("repository_kind"),
            "git_head": (profile.get("git") or {}).get("head"),
        },
        "managed_files": sorted(desired),
        "managed_sections": sections,
        "content_hashes": hashes,
        "source_commits": lock.get("sources") or {},
        "capability_set": lock.get("capabilities") or [],
    }


def read_or_empty_receipt(repo: Path) -> dict[str, Any]:
    from ges.reconciler.state import read_receipt

    return read_receipt(repo) or {}


def _rollback(repo: Path, backups: dict[str, bytes | None], created: list[str]) -> None:
    for rel, content in backups.items():
        target = repo / rel
        if content is None:
            if target.exists():
                target.unlink()
            continue
        write_bytes(target, content)
    for rel in created:
        target = repo / rel
        if target.exists():
            target.unlink()
    # drop empty leftover dirs created for new files
    for rel in created:
        parent = (repo / rel).parent
        while parent != repo and parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent
    shutil.rmtree(repo / ".ges", ignore_errors=True)
