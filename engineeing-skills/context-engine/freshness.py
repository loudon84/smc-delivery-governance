"""Context Package freshness: drift of plan, source, registry, graph or policy."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from coe_common import sha256_json


def binding_digest(binding: dict[str, Any]) -> str:
    return sha256_json(binding)


def content_digest_for(repo: Path, rels: list[str]) -> str:
    h = hashlib.sha256()
    for rel in sorted(set(rels)):
        path = repo / rel
        h.update(rel.encode("utf-8"))
        if path.is_file():
            h.update(path.read_bytes())
        elif path.is_dir():
            for child in sorted(p for p in path.rglob("*") if p.is_file()):
                h.update(child.relative_to(repo).as_posix().encode("utf-8"))
                h.update(child.read_bytes())
    return "sha256:" + h.hexdigest()


def current_bindings(
    repo: Path,
    package: dict[str, Any],
    *,
    plan_semantic: str = "",
    work_facts: str = "",
    registry_digest: str = "",
    graph_digest: str = "",
    policy_digest: str = "",
) -> dict[str, str]:
    read_set = list(package.get("read_set") or [])
    return {
        "plan_semantic_sha256": plan_semantic,
        "work_facts_digest": work_facts,
        "content_digest": content_digest_for(repo, read_set),
        "registry_digest": registry_digest,
        "graph_digest": graph_digest,
        "policy_digest": policy_digest,
        "compiler_version": (package.get("binding") or {}).get("compiler_version", ""),
        "tokenizer": (package.get("binding") or {}).get("tokenizer", ""),
    }


def freshness(package: dict[str, Any], current: dict[str, str]) -> dict[str, Any]:
    bound = dict(package.get("binding") or {})
    drifted = []
    for key in (
        "plan_semantic_sha256",
        "work_facts_digest",
        "content_digest",
        "registry_digest",
        "graph_digest",
        "policy_digest",
        "compiler_version",
    ):
        expected = bound.get(key) or ""
        actual = current.get(key) or ""
        if expected and actual and expected != actual:
            drifted.append(key)
    if drifted:
        return {"status": "STALE", "reason": "CONTEXT_BINDING_STALE", "drifted": drifted}
    if package.get("status") in {"BLOCKED", "INCOMPLETE", "STALE"}:
        return {"status": package["status"], "reason": ",".join(package.get("reason_codes") or []), "drifted": []}
    return {"status": "READY", "reason": "", "drifted": []}
