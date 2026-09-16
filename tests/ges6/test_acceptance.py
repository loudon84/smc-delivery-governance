from __future__ import annotations

import pytest

from ges.acceptance.harness import (
    SPEC_CONSTITUTION,
    THIRD_PARTY,
    USER_AGENTS,
    apply_recommended,
    business_fingerprint,
)
from ges.analyzer.repo_profile import analyze_repo
from ges.check import run_check
from ges.compose import compose, prepare_apply
from ges.errors import (
    CAPABILITY_OWNERSHIP_CONFLICT,
    GES_CHECK_PASS,
    MANAGED_CONTENT_MODIFIED,
    GesError,
)
from ges.harness_adapters.agents_md import outside_bytes
from ges.legacy.v5 import LEGACY_OWNERSHIP_UNKNOWN, OWNED_ABSENT, OWNED_UNMODIFIED, inspect_legacy
from ges.paths import AGENTS_BEGIN
from ges.reconciler.state import read_lock, read_project
from ges.remove import run_remove


# @lat: [[ges6-tests#A01 — Brownfield Detection]]
def test_a01_brownfield_detection(brownfield):
    profile = analyze_repo(brownfield)
    assert profile["repository_kind"] == "brownfield-monorepo"
    assert profile["llm_token_usage"] == 0


# @lat: [[ges6-tests#A02 — Harness Detection]]
def test_a02_harness_detection(brownfield):
    profile = analyze_repo(brownfield)
    assert "cursor" in profile["agents"]
    assert "codex" in profile["agents"]


# @lat: [[ges6-tests#A03 — Existing AGENTS Preservation]]
def test_a03_agents_preservation(brownfield, offline_cache):
    before = outside_bytes((brownfield / "AGENTS.md").read_text(encoding="utf-8"))
    apply_recommended(brownfield)
    after = outside_bytes((brownfield / "AGENTS.md").read_text(encoding="utf-8"))
    assert after == before
    assert USER_AGENTS.strip() in (brownfield / "AGENTS.md").read_text(encoding="utf-8")
    assert AGENTS_BEGIN in (brownfield / "AGENTS.md").read_text(encoding="utf-8")


# @lat: [[ges6-tests#A04 — Existing Spec Kit Preservation]]
def test_a04_specify_preservation(brownfield, offline_cache):
    apply_recommended(brownfield)
    assert (brownfield / ".specify" / "constitution.md").read_text(encoding="utf-8") == SPEC_CONSTITUTION
    assert (brownfield / ".specify" / "templates" / "spec-template.md").is_file()


# @lat: [[ges6-tests#A05 — Legacy Detection]]
def test_a05_legacy_detection(brownfield, offline_cache):
    profile = analyze_repo(brownfield)
    assert profile["legacy_ges"] is True
    report = inspect_legacy(brownfield)
    assert report.detected is True
    statuses = {entry.path: entry.status for entry in report.entries}
    assert statuses[".agents/skills/using-superpowers/SKILL.md"] == OWNED_UNMODIFIED
    assert statuses[".agents/ges/domain-packs/backend/pack.json"] == OWNED_ABSENT
    assert statuses[".cursor/skills/smc-work-router/SKILL.md"] == LEGACY_OWNERSHIP_UNKNOWN
    apply_recommended(brownfield)
    assert (brownfield / ".agents" / "skills" / "using-superpowers" / "SKILL.md").is_file()
    assert (brownfield / ".cursor" / "skills" / "smc-work-router" / "SKILL.md").is_file()


# @lat: [[ges6-tests#A06 — Capability Recommendation]]
def test_a06_capability_recommendation(brownfield, offline_cache):
    ctx = compose(brownfield)
    assert ctx.resolution.profile == "brownfield-product-app"
    assert "matt.grill-with-docs" in ctx.resolution.closed
    assert "speckit.specify" in ctx.resolution.closed
    assert "superpowers.test-driven-development" in ctx.resolution.closed


# @lat: [[ges6-tests#A07 — Capability Exclusion]]
def test_a07_capability_exclusion(brownfield, offline_cache):
    ctx, _, _ = apply_recommended(brownfield, exclude=["superpowers.executing-plans"])
    assert "superpowers.executing-plans" not in ctx.resolution.closed
    project = read_project(brownfield)
    assert "superpowers.executing-plans" in project["resolution"]["excluded"]
    assert "superpowers.test-driven-development" in project["resolution"]["selected"]


# @lat: [[ges6-tests#A08 — Dependency Closure]]
def test_a08_dependency_closure(brownfield, offline_cache):
    ctx = compose(brownfield)
    assert "matt.grill-with-docs" in ctx.resolution.closed
    assert "matt.grilling" in ctx.resolution.closed
    assert "matt.domain-modeling" in ctx.resolution.closed


# @lat: [[ges6-tests#A09 — Ownership Conflict]]
def test_a09_ownership_conflict(brownfield, offline_cache):
    ctx = compose(brownfield, extra=["matt.to-spec"])
    with pytest.raises(GesError) as captured:
        prepare_apply(ctx)
    assert captured.value.code == CAPABILITY_OWNERSHIP_CONFLICT


# @lat: [[ges6-tests#A10 — Selective Install]]
def test_a10_selective_install(brownfield, offline_cache):
    ctx, _, _ = apply_recommended(brownfield)
    skills = {path.name for path in (brownfield / ".agents" / "skills").iterdir() if path.is_dir()}
    assert "brainstorming" not in skills
    assert "to-spec" not in skills
    assert "using-superpowers" in skills  # pre-existing user/legacy, not GES-installed
    assert "grill-with-docs" in skills
    assert "writing-plans" in skills
    assert "speckit-specify" in skills
    for cap_id in ("matt.to-spec", "matt.implement", "speckit.implement", "superpowers.brainstorming"):
        assert cap_id not in ctx.resolution.closed


# @lat: [[ges6-tests#A11 — Upstream Lock]]
def test_a11_upstream_lock(brownfield, offline_cache):
    apply_recommended(brownfield)
    lock = read_lock(brownfield)
    for source in ("matt", "spec-kit", "superpowers"):
        sha = lock["sources"][source]["commit_sha"]
        assert len(sha) == 40
        assert all(ch in "0123456789abcdef" for ch in sha)


# @lat: [[ges6-tests#A12 — Idempotent Apply]]
def test_a12_idempotent_apply(brownfield, offline_cache):
    ctx1, _, noop1 = apply_recommended(brownfield)
    assert noop1 is False
    assert any(entry.action in {"ADD", "UPDATE"} for entry in ctx1.plan.entries)
    ctx2, _, noop2 = apply_recommended(brownfield)
    assert noop2 is True
    assert ctx2.plan.noop is True


# @lat: [[ges6-tests#A13 — Managed Update]]
def test_a13_managed_update(brownfield, offline_cache):
    apply_recommended(brownfield)
    business = business_fingerprint(brownfield)
    outside = outside_bytes((brownfield / "AGENTS.md").read_text(encoding="utf-8"))
    skill = offline_cache / "mattpocock-skills" / "959a8e9f1edc3adbe2f7e3054bb6fbefa6696260" / "skills" / "engineering" / "grill-with-docs" / "SKILL.md"
    skill.write_bytes(skill.read_bytes() + b"\n# upgraded\n")
    ctx, _, noop = apply_recommended(brownfield)
    assert noop is False
    updated = [entry.path for entry in ctx.plan.entries if entry.action == "UPDATE"]
    assert any(path.startswith(".agents/skills/grill-with-docs/") for path in updated)
    assert all(not path.startswith("apps/") for path in updated)
    assert business_fingerprint(brownfield) == business
    assert outside_bytes((brownfield / "AGENTS.md").read_text(encoding="utf-8")) == outside


# @lat: [[ges6-tests#A14 — User Modification Conflict]]
def test_a14_user_modification_conflict(brownfield, offline_cache):
    apply_recommended(brownfield)
    text = (brownfield / "AGENTS.md").read_text(encoding="utf-8")
    (brownfield / "AGENTS.md").write_text(
        text.replace("use Matt Pocock engineering skills.", "USER CHANGED THIS"),
        encoding="utf-8",
    )
    with pytest.raises(GesError) as captured:
        compose(brownfield)
    assert captured.value.code == MANAGED_CONTENT_MODIFIED


# @lat: [[ges6-tests#A15 — Remove]]
def test_a15_remove(brownfield, offline_cache):
    apply_recommended(brownfield)
    run_remove(brownfield)
    assert not (brownfield / ".ges").exists()
    assert not (brownfield / ".agents" / "skills" / "grill-with-docs").exists()
    assert not (brownfield / ".cursor" / "ges").exists()
    assert (brownfield / ".agents" / "skills" / "third-party" / "SKILL.md").read_text(encoding="utf-8") == THIRD_PARTY
    assert (brownfield / ".agents" / "governance" / "kit.md").is_file()
    assert (brownfield / ".specify" / "constitution.md").read_text(encoding="utf-8") == SPEC_CONSTITUTION
    agents = (brownfield / "AGENTS.md").read_text(encoding="utf-8")
    assert AGENTS_BEGIN not in agents
    assert "User-owned routing rules." in agents


# @lat: [[ges6-tests#A16 — Business Source Guard]]
def test_a16_business_source_guard(brownfield, offline_cache):
    before = business_fingerprint(brownfield)
    apply_recommended(brownfield)
    assert business_fingerprint(brownfield) == before
    apply_recommended(brownfield)
    assert business_fingerprint(brownfield) == before
    run_remove(brownfield)
    assert business_fingerprint(brownfield) == before
    apply_recommended(brownfield)
    assert run_check(brownfield) == GES_CHECK_PASS
