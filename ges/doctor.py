from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ges import __product_version__
from ges.catalog.loader import load_catalog
from ges.check import run_check
from ges.errors import BOOTSTRAP_PREREQUISITE_FAILED, GES_CHECK_FAILED, GesError
from ges.reconciler.state import read_lock, read_project
from ges.source_adapters.speckit_render import SELECTED_COMMANDS, command_rel, leftover_tokens, script_rel
from ges.stagelog import DOCTOR, PREFLIGHT, emit


PASS = "PASS"
FAIL = "FAIL"
PENDING = "PENDING"
READY = "READY"
BOOTSTRAP_PENDING = "BOOTSTRAP_PENDING"
BLOCKED = "BLOCKED"


def run_preflight(repo: Path) -> dict[str, Any]:
    emit(PREFLIGHT, "start", repo=str(repo))
    repo = repo.expanduser().resolve()
    checks = {
        "python": PASS if sys.version_info >= (3, 11) else FAIL,
        "git": PASS if shutil.which("git") else FAIL,
        "cursor_harness": PASS if (repo / ".cursor").exists() else FAIL,
    }
    warnings = []
    if (repo / ".specify" / "constitution.md").is_file():
        warnings.append(
            "LEGACY_OR_USER_SPEC_STATE: current Spec Kit expects .specify/memory/constitution.md"
        )
    failed = [name for name, status in checks.items() if status != PASS]
    payload = {
        "schema": "ges.readiness.v1",
        "mode": "preflight",
        "ges_version": __product_version__,
        "repo_head": _git_head(repo),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "overall": PASS if not failed else BLOCKED,
        "checks": checks,
        "warnings": warnings,
    }
    emit(PREFLIGHT, "complete", overall=payload["overall"])
    if failed:
        raise GesError(
            BOOTSTRAP_PREREQUISITE_FAILED,
            f"preflight failed: {', '.join(failed)}",
            details=payload,
        )
    return payload


def run_doctor(repo: Path) -> dict[str, Any]:
    emit(DOCTOR, "start", repo=str(repo))
    repo = repo.expanduser().resolve()
    checks = {
        "ges_core": FAIL,
        "cursor_harness": PASS if (repo / ".cursor").exists() else FAIL,
        "spec_kit_runtime": FAIL,
        "matt_skills_installed": FAIL,
        "matt_project_bootstrap": PENDING,
        "superpowers_skills": FAIL,
    }
    try:
        run_check(repo)
        checks["ges_core"] = PASS
    except GesError as exc:
        if exc.code != GES_CHECK_FAILED:
            raise
        checks["ges_core"] = FAIL

    catalog = load_catalog()
    project = read_project(repo) or {}
    lock = read_lock(repo) or {}
    closed = list(lock.get("resolved_capabilities") or lock.get("capabilities") or [])
    if not closed:
        profile = catalog.profiles[project.get("profile") or "brownfield-product-app"]
        closed = list(profile.required + profile.recommended)

    checks["matt_skills_installed"] = PASS if _skills_present(repo, closed, "matt.") else FAIL
    checks["superpowers_skills"] = PASS if _skills_present(repo, closed, "superpowers.") else FAIL
    checks["spec_kit_runtime"] = PASS if _speckit_runtime_ok(repo, closed) else FAIL
    if (repo / "docs" / "agents" / "issue-tracker.md").is_file() and (repo / "docs" / "agents" / "domain.md").is_file():
        checks["matt_project_bootstrap"] = PASS
    elif not (repo / ".agents" / "skills" / "setup-matt-pocock-skills").exists():
        checks["matt_project_bootstrap"] = FAIL

    overall = _overall(checks)
    payload = {
        "schema": "ges.readiness.v1",
        "ges_version": __product_version__,
        "repo_head": _git_head(repo),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "checks": checks,
    }
    emit(DOCTOR, "complete", overall=overall)
    return payload


def _overall(checks: dict[str, str]) -> str:
    required = {key: value for key, value in checks.items() if key != "matt_project_bootstrap"}
    if any(value == FAIL for value in required.values()):
        return BLOCKED
    if checks["matt_project_bootstrap"] == PENDING:
        return BOOTSTRAP_PENDING
    if checks["matt_project_bootstrap"] == FAIL:
        return BLOCKED
    return READY


def _skills_present(repo: Path, closed: list[str], prefix: str) -> bool:
    catalog = load_catalog()
    hits = [cap_id for cap_id in closed if cap_id.startswith(prefix)]
    if not hits:
        return False
    for cap_id in hits:
        cap = catalog.get(cap_id)
        if cap.projection_type == "virtual" or not cap.skill_name:
            continue
        if not (repo / ".agents" / "skills" / cap.skill_name).exists():
            return False
    return True


def _speckit_runtime_ok(repo: Path, closed: list[str]) -> bool:
    for command in SELECTED_COMMANDS:
        if f"speckit.{command}" not in closed:
            continue
        command_path = repo / command_rel(command)
        script_path = repo / script_rel(command)
        if not command_path.is_file() or not script_path.is_file():
            return False
        if leftover_tokens(command_path.read_text(encoding="utf-8")):
            return False
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=repo,
                check=False,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
        except (OSError, json.JSONDecodeError):
            return False
        if result.returncode != 0 or payload.get("capability") != command:
            return False
    return True


def _git_head(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""
