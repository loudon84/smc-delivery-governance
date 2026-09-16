"""Deterministic GES runtime locator (smc.ges.runtime-location.v1).

Provider layout: engineeing-skills/context-engine/runtime_locator.py
Consumer layout: <repo>/.agents/ges/frontend-runtime/runtime_locator.py

All runtime/skill path resolution must go through this module; scripts must not
guess with Path.parents[n].
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

SCHEMA = "smc.ges.runtime-location.v1"
CONSUMER_RUNTIME_REL = Path(".agents") / "ges" / "frontend-runtime"
PROVIDER_CONTEXT_ENGINE_REL = Path("engineeing-skills") / "context-engine"


class RuntimeLocationError(RuntimeError):
    """Raised when runtime/skill roots cannot be resolved deterministically."""


@dataclass(frozen=True)
class RuntimePaths:
    schema: str
    repo_root: Path
    runtime_root: Path
    skills_root: Path
    delivery_scripts: Path
    plan_author_scripts: Path
    review_scripts: Path
    domain_runtime: Path
    frontend_context: Path
    layout: Literal["PROVIDER", "CONSUMER"]

    def as_dict(self) -> dict:
        return {
            "schema": self.schema,
            "repo_root": str(self.repo_root),
            "runtime_root": str(self.runtime_root),
            "skills_root": str(self.skills_root),
            "delivery_scripts": str(self.delivery_scripts),
            "plan_author_scripts": str(self.plan_author_scripts),
            "review_scripts": str(self.review_scripts),
            "domain_runtime": str(self.domain_runtime),
            "frontend_context": str(self.frontend_context),
            "layout": self.layout,
        }


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _consumer_repo_from_runtime(runtime: Path) -> Path | None:
    # runtime = <repo>/.agents/ges/frontend-runtime
    if runtime.name != "frontend-runtime":
        return None
    ges = runtime.parent
    agents = ges.parent if ges.name == "ges" else None
    if agents is None or agents.name != ".agents":
        return None
    return agents.parent


def _build(repo_root: Path, runtime_root: Path, layout: str) -> RuntimePaths:
    repo_root = repo_root.resolve()
    runtime_root = runtime_root.resolve()
    if not _is_within(runtime_root, repo_root):
        raise RuntimeLocationError("GES_RUNTIME_PATH_ESCAPE")
    if not runtime_root.is_dir():
        raise RuntimeLocationError("GES_RUNTIME_ROOT_NOT_FOUND")

    if layout == "PROVIDER":
        skills_root = repo_root / ".agents" / "skills"
        domain_runtime = repo_root / "domain-runtime"
        frontend_context = repo_root / "frontend-adapters"
    else:
        skills_root = repo_root / ".agents" / "skills"
        domain_runtime = repo_root / ".agents" / "ges" / "domain-runtime"
        frontend_context = repo_root / ".agents" / "ges" / "frontend"

    delivery = skills_root / "smc-plan-delivery" / "scripts"
    author = skills_root / "smc-plan-from-approved-prd-ponytail" / "scripts"
    review = skills_root / "smc-plan-review" / "scripts"

    if not skills_root.is_dir():
        raise RuntimeLocationError("GES_SKILLS_ROOT_NOT_FOUND")
    if not delivery.is_dir():
        raise RuntimeLocationError("GES_DELIVERY_RUNTIME_NOT_FOUND")
    if not (runtime_root / "model_dispatch.py").is_file():
        raise RuntimeLocationError("GES_CONTEXT_ENGINE_NOT_FOUND")

    return RuntimePaths(
        schema=SCHEMA,
        repo_root=repo_root,
        runtime_root=runtime_root,
        skills_root=skills_root,
        delivery_scripts=delivery,
        plan_author_scripts=author,
        review_scripts=review,
        domain_runtime=domain_runtime,
        frontend_context=frontend_context,
        layout=layout,  # type: ignore[arg-type]
    )


def locate(from_path: Path | None = None) -> RuntimePaths:
    """Resolve runtime paths for Provider or Consumer layout.

    Priority: GES_RUNTIME_ROOT/GES_REPO_ROOT env > consumer marker > provider marker > repo search.
    """
    env_runtime = os.environ.get("GES_RUNTIME_ROOT")
    env_repo = os.environ.get("GES_REPO_ROOT")
    if env_runtime or env_repo:
        if not (env_runtime and env_repo):
            raise RuntimeLocationError("GES_RUNTIME_LAYOUT_AMBIGUOUS")
        runtime = Path(env_runtime).resolve()
        repo = Path(env_repo).resolve()
        if not _is_within(runtime, repo):
            raise RuntimeLocationError("GES_RUNTIME_PATH_ESCAPE")
        layout = "CONSUMER" if runtime.name == "frontend-runtime" else "PROVIDER"
        return _build(repo, runtime, layout)

    start = (from_path or Path(__file__)).resolve()
    candidates = [start] if start.is_dir() else [start.parent]
    candidates.extend(start.parents)

    for base in candidates:
        consumer_runtime = base / CONSUMER_RUNTIME_REL
        if consumer_runtime.is_dir() and (consumer_runtime / "runtime_locator.py").is_file():
            return _build(base, consumer_runtime, "CONSUMER")
        provider_runtime = base / PROVIDER_CONTEXT_ENGINE_REL
        if provider_runtime.is_dir() and (provider_runtime / "runtime_locator.py").is_file():
            return _build(base / "engineeing-skills", provider_runtime, "PROVIDER")

    # Direct invocation from inside a runtime directory
    consumer_repo = _consumer_repo_from_runtime(start if start.is_dir() else start.parent)
    if consumer_repo is not None:
        return _build(consumer_repo, start if start.is_dir() else start.parent, "CONSUMER")
    if (start if start.is_dir() else start.parent).name == "context-engine":
        runtime = start if start.is_dir() else start.parent
        if runtime.parent.name == "engineeing-skills":
            return _build(runtime.parent, runtime, "PROVIDER")

    raise RuntimeLocationError("GES_RUNTIME_ROOT_NOT_FOUND")


def require_runtime() -> RuntimePaths:
    return locate()


def self_check() -> dict:
    try:
        paths = locate()
        return {
            "ok": True,
            "layout": paths.layout,
            "repo_root": str(paths.repo_root),
            "runtime_root": str(paths.runtime_root),
            "skills_root": str(paths.skills_root),
            "delivery_scripts": str(paths.delivery_scripts),
        }
    except RuntimeLocationError as exc:
        return {"ok": False, "error": str(exc)}


def main() -> int:
    import argparse
    import json

    ap = argparse.ArgumentParser(description="GES runtime locator")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("self-check")
    p.add_argument("--json", action="store_true")
    a = ap.parse_args()
    out = self_check()
    print(json.dumps(out, indent=2, ensure_ascii=False) if a.json else out)
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
