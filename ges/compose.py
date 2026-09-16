from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ges import __version__
from ges.analyzer.repo_profile import analyze_repo
from ges.catalog.loader import Catalog, load_catalog
from ges.harness_adapters.agents_md import apply_marker, read_agents
from ges.harness_adapters.codex import CodexAdapter
from ges.harness_adapters.cursor import CursorAdapter
from ges.harness_adapters.hermes import HermesAdapter
from ges.io import sha256_bytes, tree_identity
from ges.legacy.v5 import inspect_legacy
from ges.reconciler.apply import snapshot_business_sources
from ges.reconciler.plan import InstallPlan, build_plan
from ges.reconciler.state import read_project, read_receipt, write_profile
from ges.resolver.capability_graph import Resolution, assert_no_conflicts
from ges.resolver.selection import project_desired_state, resolve_selection
from ges.source_adapters.base import ProjectedFile, Projection
from ges.source_adapters.cache import ensure_source
from ges.source_adapters.matt import MattAdapter
from ges.source_adapters.speckit import SpecKitAdapter
from ges.source_adapters.superpowers import SuperpowersAdapter
from ges.stagelog import PROJECT, RESOLVE, emit

SOURCE_ADAPTERS = {
    "matt": MattAdapter(),
    "spec-kit": SpecKitAdapter(),
    "superpowers": SuperpowersAdapter(),
}
HARNESS_ADAPTERS = {
    "cursor": CursorAdapter(),
    "codex": CodexAdapter(),
    "hermes": HermesAdapter(),
}


@dataclass
class ComposeContext:
    repo: Path
    catalog: Catalog
    profile: dict[str, Any]
    product_profile: Any
    resolution: Resolution
    project: dict[str, Any]
    desired: dict[str, ProjectedFile]
    lock: dict[str, Any]
    plan: InstallPlan


def compose(
    repo: Path,
    *,
    exclude: list[str] | None = None,
    extra: list[str] | None = None,
    profile_id: str = "brownfield-product-app",
    persist_profile: bool = True,
) -> ComposeContext:
    repo = repo.expanduser().resolve()
    profile = analyze_repo(repo)
    if persist_profile:
        write_profile(repo, profile)
    catalog = load_catalog()
    existing = read_project(repo)
    stored_exclude: list[str] = []
    if existing:
        profile_id = existing.get("profile") or profile_id
        stored_exclude = list((existing.get("resolution") or {}).get("excluded") or [])
    exclude = list(dict.fromkeys([*(exclude or []), *stored_exclude]))
    product = catalog.profiles[profile_id]
    emit(RESOLVE, "start", profile=profile_id)
    resolution = resolve_selection(catalog, product, exclude=exclude, extra=extra)
    emit(RESOLVE, "complete", selected=resolution.closed, conflicts=resolution.conflicts)
    project = project_desired_state(product, resolution, profile.get("agents") or [])
    desired = project_files(repo, catalog, resolution, profile)
    lock = build_lock(catalog, resolution, desired)
    legacy = inspect_legacy(repo)
    guard = {"roots": profile.get("source_roots") or [], "fingerprint_count": len(snapshot_business_sources(repo))}
    plan = build_plan(
        repo,
        desired,
        source_shas={key: pin.commit_sha for key, pin in catalog.sources.items()},
        legacy=legacy,
        business_guard=guard,
    )
    return ComposeContext(
        repo=repo,
        catalog=catalog,
        profile=profile,
        product_profile=product,
        resolution=resolution,
        project=project,
        desired=desired,
        lock=lock,
        plan=plan,
    )


def project_files(
    repo: Path,
    catalog: Catalog,
    resolution: Resolution,
    profile: dict[str, Any],
) -> dict[str, ProjectedFile]:
    emit(PROJECT, "start")
    shared = Projection()
    by_source: dict[str, list] = {}
    for cap_id in resolution.closed:
        cap = catalog.get(cap_id)
        by_source.setdefault(cap.source, []).append(cap)
    for source_id, caps in by_source.items():
        pin = catalog.sources[source_id]
        ensure_source(pin)
        adapter = SOURCE_ADAPTERS[source_id]
        part = adapter.project(catalog, pin, caps, repo, resolution)
        for item in part.files.values():
            shared.add(item)
    agents = list(profile.get("agents") or [])
    for harness in agents:
        adapter = HARNESS_ADAPTERS.get(harness)
        if adapter is None:
            continue
        part = adapter.project(repo, agents, shared)
        for item in part.files.values():
            shared.add(item)
    _project_agents_md(repo, shared)
    emit(PROJECT, "complete", files=len(shared.files))
    return shared.files


def _project_agents_md(repo: Path, shared: Projection) -> None:
    receipt = read_receipt(repo) or {}
    last = None
    for section in receipt.get("managed_sections") or []:
        if section.get("id") == "engineering-stack":
            last = section.get("last_applied")
    current = read_agents(repo)
    text = apply_marker(current, last_applied_hash=last)
    shared.add(
        ProjectedFile(
            relpath="AGENTS.md",
            content=text.encode("utf-8"),
            capability=None,
            source="ges",
            source_sha=None,
            kind="section",
        )
    )


def build_lock(catalog: Catalog, resolution: Resolution, desired: dict[str, ProjectedFile]) -> dict[str, Any]:
    used_sources = {catalog.get(cap_id).source for cap_id in resolution.closed}
    sources = {}
    for source_id in sorted(used_sources):
        pin = catalog.sources[source_id]
        files = {
            rel: item.content
            for rel, item in desired.items()
            if item.source == source_id
        }
        sources[source_id] = {
            "repo": pin.repo,
            "commit_sha": pin.commit_sha,
            "content_identity": tree_identity(files) if files else pin.commit_sha,
        }
    return {
        "schema": "ges.lock.v1",
        "ges_version": __version__,
        "sources": sources,
        "capabilities": resolution.closed,
        "content_identity": {
            rel: sha256_bytes(item.content)
            for rel, item in desired.items()
        },
    }


def prepare_apply(ctx: ComposeContext) -> None:
    assert_no_conflicts(ctx.resolution)
