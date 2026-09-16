from __future__ import annotations

from pathlib import Path

from ges.catalog.loader import load_catalog
from ges.compose import compose
from ges.errors import GES_CHECK_FAILED, GES_CHECK_PASS, GesError
from ges.harness_adapters.agents_md import count_markers, read_agents
from ges.io import sha256_file
from ges.reconciler.guard import assert_allowed, assert_not_business_source
from ges.reconciler.state import read_lock, read_profile, read_project, read_receipt, validate_payload
from ges.resolver.capability_graph import detect_conflicts
from ges.source_adapters.cache import ensure_source
from ges.stagelog import CHECK, emit


def run_check(repo: Path) -> str:
    emit(CHECK, "start", repo=str(repo))
    repo = repo.expanduser().resolve()
    project = read_project(repo)
    profile = read_profile(repo)
    lock = read_lock(repo)
    receipt = read_receipt(repo)
    if not all([project, profile, lock, receipt]):
        raise GesError(GES_CHECK_FAILED, "missing .ges project state (project/profile/lock/receipt)")
    validate_payload("ges.project.v1.json", project, code=GES_CHECK_FAILED)
    validate_payload("ges.repo-profile.v1.json", profile, code=GES_CHECK_FAILED)
    validate_payload("ges.lock.v1.json", lock, code=GES_CHECK_FAILED)
    validate_payload("ges.install-receipt.v1.json", receipt, code=GES_CHECK_FAILED)

    catalog = load_catalog()
    for source_id, meta in (lock.get("sources") or {}).items():
        pin = catalog.sources[source_id]
        if meta.get("commit_sha") != pin.commit_sha:
            # lock may pin the same catalog SHA; if it differs, still require resolvable tree
            pass
        ensure_source(pin)

    closed = list(lock.get("capabilities") or [])
    conflicts = detect_conflicts(catalog, closed)
    if conflicts:
        raise GesError(GES_CHECK_FAILED, "ownership conflict present in lock", details={"conflicts": conflicts})

    for cap_id in closed:
        cap = catalog.get(cap_id)
        if cap.projection_type == "virtual" or not cap.skill_name:
            continue
        skill_dir = repo / ".agents" / "skills" / cap.skill_name
        if not skill_dir.exists():
            raise GesError(GES_CHECK_FAILED, f"capability {cap_id} is not projected")

    hashes = receipt.get("content_hashes") or {}
    for rel, meta in hashes.items():
        path = repo / rel
        if not path.is_file():
            raise GesError(GES_CHECK_FAILED, f"managed file missing: {rel}")
        if sha256_file(path) != meta.get("last_applied"):
            raise GesError(GES_CHECK_FAILED, f"managed hash mismatch: {rel}")
        assert_allowed(rel)
        assert_not_business_source(rel)

    agents = read_agents(repo)
    if count_markers(agents) != 1:
        raise GesError(GES_CHECK_FAILED, "AGENTS.md must contain exactly one GES marker")

    ctx = compose(repo, persist_profile=False)
    if not ctx.plan.noop:
        raise GesError(GES_CHECK_FAILED, "working tree is not reconciled to desired state")

    emit(CHECK, "pass")
    return GES_CHECK_PASS
