#!/usr/bin/env python3
"""Transactional GES 5 installer; preserves installed v2 profile policy for in-flight Plans."""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import install_v441 as inherited
from build_package_manifest import ROOT as PACKAGE_ROOT
from build_package_manifest import build as build_manifest
from build_package_manifest import verify

base = inherited.suite
base.PACKAGE_VERSION = "5.0.0"
PROJECT = None
SELECTOR = None


def bounded(root, rel):
    p = (root / rel).resolve()
    if not p.is_relative_to(root.resolve()):
        raise ValueError("INSTALL_PATH_OUTSIDE_ROOT: " + str(rel))
    return p


def resolve_profile(project, selector):
    global PROJECT, SELECTOR
    PROJECT, SELECTOR = project, selector
    installed = project / ".agents/ges/profile.json"
    path = (
        Path(selector).resolve()
        if selector and Path(selector).is_file()
        else base.CONSUMERS / (selector.removesuffix(".json") + ".json")
        if selector
        else installed
        if installed.is_file()
        else base.CONSUMERS / "generic.json"
    )
    profile = base.read_json(path)
    if profile.get("schema") not in {"smc.ges.consumer-profile.v2", "smc.ges.consumer-profile.v3"}:
        raise ValueError("CONSUMER_PROFILE_SCHEMA_INVALID")
    return path, profile


def pack_context(profile):
    installed = PROJECT / ".agents/ges/domain-packs" if PROJECT else None
    root = (
        installed
        if SELECTOR is None and installed and (installed / "registry.json").is_file()
        else base.PACKAGE / ("domain-packs-v1" if profile["schema"].endswith(".v2") else "domain-packs")
    )
    registry = base.read_json(root / "registry.json")
    selected = {}
    if registry.get("schema") != "smc.ges.domain-registry.v1":
        raise ValueError("DOMAIN_REGISTRY_SCHEMA_INVALID")
    for domain in profile.get("domains", {}):
        row = registry.get("packs", {}).get(domain)
        if not isinstance(row, dict):
            raise ValueError("DOMAIN_PACK_NOT_REGISTERED: " + domain)
        path = bounded(root, row["path"])
        pack = base.read_json(path)
        schema = "smc.ges.domain-pack.v1" if profile["schema"].endswith(".v2") else "smc.ges.domain-pack.v2"
        if pack.get("schema") != schema or pack.get("id") != domain:
            raise ValueError("DOMAIN_PACK_INVALID: " + domain)
        selected[domain] = (path, pack)
    return registry, selected


_previous_preflight = base.preflight


def preflight(project, profile, selected, names):
    errors = _previous_preflight(project, profile, selected, names)
    for rel in profile.get("project_policy_paths", []):
        if not bounded(project, rel).is_file():
            errors.append("PROJECT_POLICY_MISSING: " + rel)
    for name in names:
        bounded(base.SKILLS, name)
        bounded(project, ".agents/skills/" + name)
    return errors


_previous_record = base.record_before


def record_before(project, target, backup, records):
    bounded(project, target.relative_to(project))
    return _previous_record(project, target, backup, records)


_previous_metadata = base.install_ges_metadata


def install_metadata(project, profile, selected, backup, records):
    installed = project / ".agents/ges"
    if SELECTOR is None and (installed / "profile.json").is_file():
        return base.copy_tree(project, base.DOMAIN_RUNTIME, installed / "domain-runtime", backup, records)
    return _previous_metadata(project, profile, selected, backup, records)


_previous_commands = base.validation_commands


def validation_commands(project, profile, selected, skip):
    commands = _previous_commands(project, profile, selected, True)
    scripts = project / ".agents/skills"
    for label, relative in [
        ("work router", "using-superpowers/scripts/test_work_router.py"),
        ("PRD profile", "smc-prd-grounding/scripts/test_prd_profile.py"),
        ("v5 runtime", "smc-plan-delivery/scripts/test_engineering_method_v2.py"),
    ]:
        commands.append((label, [sys.executable, str(scripts / relative)]))
    validator = profile.get("project_validator")
    if validator and not skip:
        parts = shlex.split(str(validator), posix=True)
        if parts and parts[0].lower().startswith("python"):
            if len(parts) < 2 or not bounded(project, parts[1]).is_file():
                raise ValueError("CONSUMER_PROJECT_VALIDATOR_MISSING")
            parts = [sys.executable, str(bounded(project, parts[1])), *parts[2:]]
        commands.append(("consumer project validator", parts))
    return commands


def _git_head(project: Path) -> tuple[str, bool]:
    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=project, text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=PACKAGE_ROOT, text=True, stderr=subprocess.DEVNULL
            ).strip()
        )
        return head, dirty
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "unknown", True


def _owned_paths(project: Path, names: list[str], records: dict) -> list[dict]:
    owned = []
    for rel, rec in sorted(records.items()):
        # package-owned: under .agents/skills/<managed>, .agents/ges/, tools from integration copies
        if rel.startswith(".agents/skills/"):
            skill = rel.split("/")[2] if len(rel.split("/")) > 2 else ""
            if skill and skill not in names:
                continue  # consumer-local skill preserved
        if not (
            rel.startswith(".agents/skills/")
            or rel.startswith(".agents/ges/")
            or rel.startswith("tools/agent-skills/")
            or rel.startswith(".cursor/skills/")
        ):
            continue
        digest = rec.get("installed_sha256") or base.sha256(project / rel)
        if digest:
            owned.append({"path": rel, "installed_sha256": digest})
    return owned


def build_install_lock(project, profile, selected, records, backup):
    # @lat: [[acceptance-hardening#Install Lock v2]]
    names = base.managed_skills(profile, selected)
    manifest = build_manifest(PACKAGE_ROOT)
    head, dirty = _git_head(PACKAGE_ROOT)
    tx = backup / "upgrade-manifest.json"
    policy = {
        "profile": f"{profile.get('id')}@{profile.get('version')}",
        "domains": {k: v[1].get("version") for k, v in selected.items()},
    }
    return {
        "schema": "smc.ges.install-lock.v2",
        "bundle": base.PACKAGE_VERSION,
        "profile": {
            "id": profile.get("id"),
            "version": profile.get("version"),
            "sha256": hashlib.sha256(
                json.dumps(profile, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
        },
        "domains": {
            k: {"version": v[1].get("version"), "sha256": base.sha256(v[0]) or ""}
            for k, v in selected.items()
        },
        "release_identity": {
            "source_commit": head,
            "source_tree_dirty": dirty,
            "package_manifest_sha256": hashlib.sha256(
                json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
            "package_file_count": manifest.get("file_count"),
            "installer_sha256": base.sha256(Path(__file__).resolve()) or "",
        },
        "policy_digest": "sha256:"
        + hashlib.sha256(json.dumps(policy, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "transaction_manifest_sha256": base.sha256(tx) if tx.is_file() else "",
        "installed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "owned_files": _owned_paths(project, names, records),
    }


def reconcile_stale_owned_files(project, backup, records, names):
    # @lat: [[acceptance-hardening#Install Lock v2]]
    lock_path = project / ".smc/ges-install-lock.json"
    if not lock_path.is_file():
        return ["INSTALL_LEGACY_RECONCILIATION_SKIPPED"]
    try:
        old = json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["INSTALL_LOCK_V2_INVALID"]
    if old.get("schema") != "smc.ges.install-lock.v2":
        return ["INSTALL_LEGACY_RECONCILIATION_SKIPPED"]
    old_owned = {row["path"]: row.get("installed_sha256") for row in old.get("owned_files", [])}
    new_owned = {row["path"] for row in _owned_paths(project, names, records)}
    notes = []
    for path, old_sha in old_owned.items():
        if path in new_owned:
            continue
        target = project / path
        if not target.is_file():
            continue
        # owned_files already excludes consumer-local skills at write time;
        # stale entries are former package-owned paths (including removed skills).
        current = base.sha256(target)
        if current == old_sha:
            base.record_before(project, target, backup, records)
            target.unlink()
            notes.append("STALE_OWNED_DELETED:" + path)
        else:
            raise RuntimeError("INSTALL_STALE_OWNED_FILE_MODIFIED: " + path)
    return notes or ["INSTALL_RECONCILIATION_NONE"]


base.resolve_profile = resolve_profile
base.pack_context = pack_context
base.preflight = preflight
base.record_before = record_before
base.install_ges_metadata = install_metadata
base.validation_commands = validation_commands
base.build_install_lock = build_install_lock
base.reconcile_stale_owned_files = reconcile_stale_owned_files
base.now_tag = lambda: uuid.uuid4().hex


def main():
    try:
        verify()
    except (ValueError, OSError) as exc:
        print("INSTALL_INTEGRITY_BLOCKED:", exc)
        return 2
    os.environ.setdefault("PYTHONUTF8", "1")
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
