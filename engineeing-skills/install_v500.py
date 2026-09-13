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
_RECONCILE_STATE: dict = {"deleted": [], "blocked": [], "notes": []}
_VALIDATION_CMDS: list = []


def validation_commands(project, profile, selected, skip):
    global _VALIDATION_CMDS
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
    _VALIDATION_CMDS = [(label, list(cmd) if isinstance(cmd, (list, tuple)) else [str(cmd)]) for label, cmd in commands]
    return commands


def _commands_digest() -> str:
    payload = [{"label": a, "cmd": b} for a, b in _VALIDATION_CMDS]
    return "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _managed_file_set_sha256(owned: list[dict]) -> str:
    payload = [{"path": r["path"], "sha256": r.get("installed_sha256")} for r in owned]
    return "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


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
        if rel.startswith(".agents/skills/"):
            skill = rel.split("/")[2] if len(rel.split("/")) > 2 else ""
            if skill and skill not in names:
                continue
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


def write_immutable_receipt(project, backup, profile, selected, records, release_identity, policy_digest, owned):
    """PRD §15/§16 step 13 — immutable receipt before lock; receipt has no self-hash."""
    # @lat: [[acceptance-closure#Install Receipt]]
    # @lat: [[install#Install Receipt]]
    # @lat: [[governance-architecture-closure]]
    install_id = backup.name if backup else uuid.uuid4().hex
    dirty = bool(release_identity.get("source_tree_dirty"))
    receipt = {
        "schema": "smc.ges.install-receipt.v1",
        "install_id": install_id,
        "bundle": base.PACKAGE_VERSION,
        "release_identity": {
            **release_identity,
            "release_eligible": not dirty,
        },
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
        "policy_digest": policy_digest,
        "managed_file_set_sha256": _managed_file_set_sha256(owned),
        "validation": {"status": "PASS", "commands_digest": _commands_digest()},
        "stale_reconciliation": {
            "deleted": list(_RECONCILE_STATE.get("deleted") or []),
            "blocked": list(_RECONCILE_STATE.get("blocked") or []),
        },
        "finalized_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "backup_id": install_id,
    }
    if dirty:
        # Record ineligibility; install may still proceed for development.
        receipt["release_identity"]["note"] = "INSTALL_SOURCE_DIRTY_NOT_RELEASE_ELIGIBLE"
    out_dir = project / ".smc" / "ges-install-receipts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{install_id}.json"
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Compat pointer for older tooling
    compat = project / ".smc" / "ges-install-receipt.json"
    compat.write_text(
        json.dumps(
            {
                "schema": "smc.ges.install-receipt.v1",
                "install_id": install_id,
                "receipt_path": f".smc/ges-install-receipts/{install_id}.json",
                "install_receipt_sha256": "sha256:" + (base.sha256(out) or ""),
                "transaction_status": "PASS",
                "bundle": base.PACKAGE_VERSION,
                "installed_at": receipt["finalized_at"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return out, receipt


def build_install_lock(project, profile, selected, records, backup):
    # @lat: [[acceptance-hardening#Install Lock v2]]
    # @lat: [[acceptance-closure#Canonical Digests]]
    # Order: receipt (13) then lock (14-15); journal PASS is written by base.main after this.
    names = base.managed_skills(profile, selected)
    manifest_path = PACKAGE_ROOT / "PACKAGE-MANIFEST.json"
    head, dirty = _git_head(PACKAGE_ROOT)
    policy = {
        "profile": f"{profile.get('id')}@{profile.get('version')}",
        "domains": {k: v[1].get("version") for k, v in selected.items()},
    }
    file_count = 0
    if manifest_path.is_file():
        try:
            file_count = json.loads(manifest_path.read_text(encoding="utf-8")).get("file_count", 0)
        except json.JSONDecodeError:
            file_count = 0
    release_identity = {
        "source_commit": head,
        "source_tree_dirty": dirty,
        "package_manifest_sha256": base.sha256(manifest_path) or "",
        "package_file_count": file_count,
        "installer_sha256": base.sha256(Path(__file__).resolve()) or "",
        "release_eligible": not dirty,
    }
    policy_digest = "sha256:" + hashlib.sha256(
        json.dumps(policy, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    owned = _owned_paths(project, names, records)
    receipt_path, _receipt = write_immutable_receipt(
        project, backup, profile, selected, records, release_identity, policy_digest, owned
    )
    rel_receipt = receipt_path.relative_to(project).as_posix()
    receipt_sha = "sha256:" + (base.sha256(receipt_path) or "")
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
        "release_identity": release_identity,
        "policy_digest": policy_digest,
        "installed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "owned_files": owned,
        "install_receipt_path": rel_receipt,
        "install_receipt_sha256": receipt_sha,
    }


def reconcile_stale_owned_files(project, backup, records, names):
    # @lat: [[acceptance-hardening#Install Lock v2]]
    global _RECONCILE_STATE
    _RECONCILE_STATE = {"deleted": [], "blocked": [], "notes": []}
    lock_path = project / ".smc/ges-install-lock.json"
    if not lock_path.is_file():
        note = ["INSTALL_LEGACY_RECONCILIATION_SKIPPED"]
        _RECONCILE_STATE["notes"] = note
        return note
    try:
        old = json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        note = ["INSTALL_LOCK_V2_INVALID"]
        _RECONCILE_STATE["notes"] = note
        return note
    if old.get("schema") != "smc.ges.install-lock.v2":
        note = ["INSTALL_LEGACY_RECONCILIATION_SKIPPED"]
        _RECONCILE_STATE["notes"] = note
        return note
    old_owned = {row["path"]: row.get("installed_sha256") for row in old.get("owned_files", [])}
    new_owned = {row["path"] for row in _owned_paths(project, names, records)}
    notes = []
    for path, old_sha in old_owned.items():
        if path in new_owned:
            continue
        target = project / path
        if not target.is_file():
            continue
        current = base.sha256(target)
        if current == old_sha:
            base.record_before(project, target, backup, records)
            target.unlink()
            notes.append("STALE_OWNED_DELETED:" + path)
            _RECONCILE_STATE["deleted"].append(path)
        else:
            _RECONCILE_STATE["blocked"].append(path)
            raise RuntimeError("INSTALL_STALE_OWNED_FILE_MODIFIED: " + path)
    _RECONCILE_STATE["notes"] = notes or ["INSTALL_RECONCILIATION_NONE"]
    return _RECONCILE_STATE["notes"]


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
    # Receipt is written inside build_install_lock (before journal PASS).
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
