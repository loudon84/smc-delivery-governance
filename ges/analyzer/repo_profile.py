from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from ges.analyzer import detectors
from ges.analyzer.source_roots import business_source_roots
from ges.errors import REPO_NOT_SUPPORTED, GesError
from ges.stagelog import ANALYZE, emit


def analyze_repo(repo: Path) -> dict[str, Any]:
    """Build a deterministic repo profile. LLM token usage is always 0."""
    emit(ANALYZE, "start", repo=str(repo))
    root = repo.expanduser().resolve()
    if not root.is_dir():
        raise GesError(REPO_NOT_SUPPORTED, f"repository path does not exist: {repo}")

    brownfield = detectors.detect_brownfield(root)
    monorepo = detectors.detect_monorepo(root)
    if brownfield and monorepo:
        kind = "brownfield-monorepo"
    elif brownfield:
        kind = "brownfield"
    elif monorepo:
        kind = "greenfield-monorepo"
    else:
        kind = "greenfield"

    profile = {
        "schema": "ges.repo-profile.v1",
        "repository_kind": kind,
        "agents": detectors.detect_agents(root),
        "languages": detectors.detect_languages(root),
        "spec_kit": detectors.detect_spec_kit(root),
        "legacy_ges": detectors.detect_legacy_ges(root),
        "ci": detectors.detect_ci(root),
        "package_managers": detectors.detect_package_managers(root),
        "frameworks": detectors.detect_frameworks(root),
        "existing": detectors.detect_existing(root),
        "source_roots": business_source_roots(root),
        "git": _git_identity(root),
        "llm_token_usage": 0,
    }
    emit(ANALYZE, "complete", repository_kind=kind, agents=profile["agents"])
    return profile


def _git_identity(repo: Path) -> dict[str, Any]:
    info: dict[str, Any] = {"repository": (repo / ".git").exists()}
    if not info["repository"]:
        return info
    info["head"] = _git(repo, ["rev-parse", "HEAD"])
    info["remote"] = _git(repo, ["config", "--get", "remote.origin.url"])
    return info


def _git(repo: Path, args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None
