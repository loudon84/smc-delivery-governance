"""Pin Registry snapshot to source, config and parser versions."""
from __future__ import annotations

import hashlib
from pathlib import Path

from coe_common import PARSER_VERSION, sha256_json
from registry import Registry, context_root, load_registry


def content_digest(repo: Path, paths: list[str] | None = None) -> str:
    h = hashlib.sha256()
    if paths:
        files = [repo / p for p in paths]
    else:
        files = []
        ctx = context_root(repo)
        if ctx.is_dir():
            files.extend(sorted(p for p in ctx.rglob("*") if p.is_file()))
    for path in files:
        if not path.is_file():
            continue
        h.update(path.as_posix().encode("utf-8"))
        h.update(path.read_bytes())
    return "sha256:" + h.hexdigest()


def snapshot(registry: Registry, *, head: str = "", extra: dict | None = None) -> dict:
    payload = {
        "parser_version": PARSER_VERSION,
        "registry_digest": registry.digest,
        "config_digest": content_digest(registry.repo),
        "head": head,
        "errors": registry.errors,
        **(extra or {}),
    }
    payload["snapshot_digest"] = sha256_json(payload)
    return payload


def load_snapshot(repo: Path, head: str = "") -> dict:
    return snapshot(load_registry(repo), head=head)
