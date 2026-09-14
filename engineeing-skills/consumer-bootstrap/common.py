#!/usr/bin/env python3
"""Shared helpers for GES Consumer Bootstrap (v5.0.5)."""
from __future__ import annotations

import hashlib
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BOOTSTRAP = Path(__file__).resolve().parent
PACKAGE = BOOTSTRAP.parent
TEMPLATES = BOOTSTRAP / "templates"
SCHEMAS = BOOTSTRAP / "schemas"
CORE_MANIFEST = PACKAGE / "core" / "manifest.json"
PROVENANCE = PACKAGE / "integrations" / "superpowers" / "upstream-provenance.json"

CLAIM_VOCAB = frozenset(
    {
        "INSPIRED",
        "ADAPTER_READY",
        "UPSTREAM_PINNED",
        "EXTERNAL_VERIFIED",
        "GES_NATIVE",
        "NATIVE_ONLY",
        "UNAVAILABLE",
        "INCOMPATIBLE",
        "AVAILABLE",
    }
)

# Scaffold paths only — never .specify/spec.md (requirements SOT forbidden).
SPEC_KIT_SCAFFOLD = (
    ".specify/constitution.md",
    ".specify/templates/.gitkeep",
    ".specify/scripts/.gitkeep",
    ".specify/specs/README.md",
)

# Upstream-pinned capability ids (from provenance) + PRD supplement shims.
SUPERPOWERS_PINNED = (
    "executing-plans",
    "subagent-driven-development",
    "test-driven-development",
    "systematic-debugging",
    "verification-before-completion",
)
SUPERPOWERS_SHIMS = (
    "brainstorming",
    "writing-plans",
    "finishing-branch",
)

BRIDGE_CONTRACTS = (
    ".agents/ges/spec-kit-binding.json",
    ".agents/ges/superpowers-binding.json",
    ".agents/ges/governance-policy.json",
    ".agents/ges/spec-superpower-ges.json",
)

FORBIDDEN_WRITE_RELS = frozenset(
    {
        ".specify/spec.md",
        ".agents/ges/profile.json",  # installer-owned
    }
)

REPORT_DIR_REL = ".smc/consumer-bootstrap"
RECEIPT_DIR_REL = ".smc/ges-bootstrap-receipts"

# Frontend Context System (v5.0.6) — consumer data root under .agents/ges/frontend/
FRONTEND_ROOT = ".agents/ges/frontend"
FRONTEND_TEMPLATES = (
    "apps-registry.json",
    "app-profile.json",
    "ui-baseline.json",
    "surface-registry.json",
    "layout-map.json",
    "navigation-map.json",
    "component-registry.json",
    "state-owner-map.json",
    "design-system.json",
    "baseline.lock.json",
    "shared-ui-registry.json",
)
FRONTEND_APP_LEVEL_TEMPLATES = (
    "app-profile.json",
    "ui-baseline.json",
    "surface-registry.json",
    "layout-map.json",
    "navigation-map.json",
    "component-registry.json",
    "state-owner-map.json",
    "design-system.json",
    "baseline.lock.json",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON_OBJECT_REQUIRED: {path}")
    return value


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def bounded(root: Path, rel: str) -> Path:
    """Resolve rel under root; reject escape."""
    root = root.resolve()
    target = (root / rel).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"BOOTSTRAP_PATH_OUTSIDE_ROOT: {rel}")
    return target


def exists_file(project: Path, rel: str) -> bool:
    return bounded(project, rel).is_file()


def exists_dir(project: Path, rel: str) -> bool:
    return bounded(project, rel).is_dir()


def managed_skills() -> list[str]:
    core = read_json(CORE_MANIFEST)
    return [str(x) for x in core.get("managed_skills", [])]


def pinned_capabilities() -> list[str]:
    if PROVENANCE.is_file():
        data = read_json(PROVENANCE)
        caps = [
            str(c.get("capability_id"))
            for c in data.get("capabilities", [])
            if isinstance(c, dict) and c.get("capability_id")
        ]
        if caps:
            return caps
    return list(SUPERPOWERS_PINNED)


def layer_verdict(present: int, total: int) -> str:
    if total <= 0:
        return "MISSING"
    if present >= total:
        return "PASS"
    if present == 0:
        return "MISSING"
    return "PARTIAL"


def record_before(project: Path, target: Path, backup: Path, records: dict[str, dict]) -> dict:
    rel = target.relative_to(project).as_posix()
    if rel in records:
        return records[rel]
    existed = target.is_file()
    rec = {
        "path": rel,
        "existed_before": existed,
        "original_sha256": sha256_file(target) if existed else None,
        "installed_sha256": None,
    }
    records[rel] = rec
    if existed:
        dst = backup / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, dst)
    return rec


def write_new_file(project: Path, dst: Path, text: str, backup: Path, records: dict[str, dict]) -> None:
    """Write only if missing; never overwrite."""
    bounded(project, dst.relative_to(project).as_posix())
    if dst.is_file():
        raise ValueError(f"BOOTSTRAP_REFUSES_OVERWRITE: {dst.relative_to(project).as_posix()}")
    rec = record_before(project, dst, backup, records)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8", newline="\n")
    rec["installed_sha256"] = sha256_file(dst)


def copy_new_file(project: Path, src: Path, dst: Path, backup: Path, records: dict[str, dict]) -> None:
    if dst.is_file():
        raise ValueError(f"BOOTSTRAP_REFUSES_OVERWRITE: {dst.relative_to(project).as_posix()}")
    rec = record_before(project, dst, backup, records)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    rec["installed_sha256"] = sha256_file(dst)


def restore(project: Path, backup: Path, records: dict[str, dict]) -> None:
    for rel in reversed(sorted(records)):
        rec = records[rel]
        target = project / rel
        if rec["existed_before"]:
            src = backup / rel
            if not src.is_file():
                raise RuntimeError(f"BOOTSTRAP_ROLLBACK_BACKUP_MISSING: {rel}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
        elif target.is_file() or target.is_symlink():
            target.unlink()


def new_id() -> str:
    return uuid.uuid4().hex
