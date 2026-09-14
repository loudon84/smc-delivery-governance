"""GES Context Optimization Engine — shared helpers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PARSER_VERSION = "ges.context.parser.v1"
REGISTRY_SCHEMA = "smc.context.registry.v1"
IMPACT_SCHEMA = "smc.context.impact.v1"
PACKAGE_SCHEMA = "smc.context.package.v1"
REQUEST_SCHEMA = "smc.context.request.v1"
CURRENT_PLAN_CONTRACT = "smc.plan.v4.0"
LEGACY_PLAN_CONTRACTS = frozenset(
    {
        "smc.plan.v3.3",
        "smc.plan.v3.4",
        "smc.plan.v3.5",
        "smc.plan.v3.6",
        "smc.plan.v3.7",
    }
)
CONTEXT_DIR = Path(".agents") / "ges" / "context"
ENGINE_DIR = Path(".agents") / "ges" / "context-engine"


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_json(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def find_repo_root(path: Path) -> Path:
    current = path.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() or (candidate / ".agents").is_dir():
            return candidate
    raise ValueError(f"CONTEXT_REPO_ROOT_NOT_FOUND: {path}")


def posix(rel: str) -> str:
    return str(rel).replace("\\", "/").lstrip("./")
