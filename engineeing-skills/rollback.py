#!/usr/bin/env python3
"""Rollback a completed SMC Skills overlay transaction safely."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath


class RollbackError(ValueError):
    """Fail-closed rollback boundary violation."""


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _norm_key(path: Path) -> str:
    return os.path.normcase(str(path.resolve()))


def _is_unc(logical: str) -> bool:
    return logical.startswith("\\\\") or logical.startswith("//")


def _is_drive_qualified(logical: str) -> bool:
    pure = PureWindowsPath(logical)
    return bool(pure.drive) or bool(pure.root)


def _segments(logical: str) -> list[str]:
    # Do not use Path.parts — it collapses "." and may hide illegal segments.
    posix = logical.replace("\\", "/")
    return posix.split("/")


def _validate_logical(logical: object, *, code_invalid: str = "ROLLBACK_PATH_INVALID") -> str:
    if not isinstance(logical, str) or not logical.strip():
        raise RollbackError(code_invalid)
    text = logical.strip()
    if _is_unc(text) or _is_drive_qualified(text) or PurePosixPath(text.replace("\\", "/")).is_absolute():
        raise RollbackError("ROLLBACK_PATH_ESCAPE")
    segs = _segments(text)
    if not segs or any(s in {"", ".", ".."} for s in segs):
        raise RollbackError("ROLLBACK_PATH_ESCAPE" if any(s == ".." for s in segs) else code_invalid)
    return "/".join(segs)


def _inside(root_key: str, candidate_key: str) -> bool:
    return candidate_key == root_key or candidate_key.startswith(root_key + os.sep)


def _inside(root_key: str, candidate_key: str) -> bool:
    return candidate_key == root_key or candidate_key.startswith(root_key + os.sep)


def _resolve_under(root: Path, rel_posix: str, *, escape_code: str) -> Path:
    """Join package-relative posix path under root and enforce containment + symlink safety."""
    root_res = root.resolve()
    root_key = _norm_key(root_res)
    parts = PurePosixPath(rel_posix).parts
    if not parts:
        raise RollbackError(escape_code)
    cursor = root_res
    for part in parts:
        cursor = cursor / part
        if cursor.exists() or cursor.is_symlink():
            try:
                resolved = cursor.resolve()
            except OSError as exc:
                raise RollbackError("ROLLBACK_SYMLINK_ESCAPE") from exc
            if not _inside(root_key, _norm_key(resolved)):
                raise RollbackError("ROLLBACK_SYMLINK_ESCAPE")
    final = cursor.resolve(strict=False)
    final_key = _norm_key(final)
    if final_key == root_key or not _inside(root_key, final_key):
        raise RollbackError(escape_code)
    return final


def resolve_record_target(project: Path, logical: object) -> Path:
    # @lat: [[safety-runtime-closure-v503]]
    """Resolve a package-relative rollback target inside project (not project root)."""
    rel = _validate_logical(logical)
    return _resolve_under(project.resolve(), rel, escape_code="ROLLBACK_PATH_ESCAPE")


def resolve_backup_source(backup_root: Path, logical: object) -> Path:
    """Resolve a package-relative backup source inside the backup transaction root."""
    rel = _validate_logical(logical, code_invalid="ROLLBACK_BACKUP_ESCAPE")
    return _resolve_under(backup_root.resolve(), rel, escape_code="ROLLBACK_BACKUP_ESCAPE")


def resolve_backup_dir(project: Path, backup: Path | None) -> Path:
    """Require backup under <project>/.smc/skill-upgrade-backups/<tx>/."""
    project = project.resolve()
    allowed = (project / ".smc" / "skill-upgrade-backups").resolve()
    if backup is None:
        raise RollbackError("ROLLBACK_TRANSACTION_NOT_FOUND")
    # If caller passed a relative path, resolve against cwd then re-check containment.
    candidate = backup if backup.is_absolute() else (Path.cwd() / backup)
    try:
        resolved = candidate.resolve()
    except OSError as exc:
        raise RollbackError("ROLLBACK_BACKUP_ESCAPE") from exc
    key = _norm_key(resolved)
    allowed_key = _norm_key(allowed)
    if key == allowed_key or not key.startswith(allowed_key + os.sep):
        raise RollbackError("ROLLBACK_BACKUP_ESCAPE")
    if not (resolved / "upgrade-manifest.json").is_file():
        raise RollbackError("ROLLBACK_TRANSACTION_NOT_FOUND")
    return resolved


def latest_backup(project: Path) -> Path | None:
    root = project / ".smc" / "skill-upgrade-backups"
    candidates = (
        sorted(
            (p for p in root.iterdir() if p.is_dir() and (p / "upgrade-manifest.json").is_file()),
            reverse=True,
        )
        if root.is_dir()
        else []
    )
    return candidates[0] if candidates else None


def validate_manifest(project: Path, backup: Path, files: list) -> list[dict]:
    """Validate every record before any filesystem mutation. Raises RollbackError."""
    if not isinstance(files, list) or not files:
        raise RollbackError("ROLLBACK_MANIFEST_INVALID")
    seen: set[str] = set()
    validated: list[dict] = []
    for rec in files:
        if not isinstance(rec, dict) or "path" not in rec:
            raise RollbackError("ROLLBACK_MANIFEST_INVALID")
        target = resolve_record_target(project, rec["path"])
        key = _norm_key(target)
        if key in seen:
            raise RollbackError("ROLLBACK_DUPLICATE_TARGET")
        seen.add(key)
        # Always resolve backup source path for containment even when existed_before is false
        # (preflight must reject escape in either branch).
        resolve_backup_source(backup, rec["path"])
        validated.append(rec)
    return validated


def main() -> int:
    # @lat: [[install#Rollback]]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("--backup", type=Path, help="specific backup transaction; default latest")
    ap.add_argument("--apply", action="store_true", help="perform rollback; default dry-run")
    ap.add_argument("--force", action="store_true", help="rollback even when files changed after install")
    args = ap.parse_args()
    project = args.project.resolve()
    try:
        if args.backup is not None:
            backup = resolve_backup_dir(project, args.backup)
        else:
            latest = latest_backup(project)
            if latest is None:
                print("ROLLBACK_TRANSACTION_NOT_FOUND", file=sys.stderr)
                return 2
            backup = resolve_backup_dir(project, latest)
        manifest_path = backup / "upgrade-manifest.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        files = validate_manifest(project, backup, data.get("files") or [])
    except RollbackError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as exc:
        print("ROLLBACK_MANIFEST_INVALID", file=sys.stderr)
        return 2

    drift: list[str] = []
    for rec in files:
        try:
            target = resolve_record_target(project, rec["path"])
        except RollbackError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        expected = rec.get("installed_sha256")
        current = sha256(target)
        if current != expected:
            drift.append(f"{rec['path']}: installed={expected} current={current}")
    print(f"Rollback transaction: {backup}")
    print(f"Files: {len(files)}")
    if drift:
        print("Post-install drift detected:")
        for row in drift:
            print("  " + row)
        if not args.force:
            print(
                "ROLLBACK_BLOCKED_BY_POST_INSTALL_DRIFT — use --force only after reviewing the listed files.",
                file=sys.stderr,
            )
            return 3
    if not args.apply:
        print("DRY RUN PASS — rerun with --apply to rollback.")
        return 0

    for rec in reversed(files):
        rel = rec["path"]
        try:
            target = resolve_record_target(project, rel)
        except RollbackError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if rec.get("existed_before"):
            try:
                source = resolve_backup_source(backup, rel)
            except RollbackError as exc:
                print(str(exc), file=sys.stderr)
                return 2
            if not source.is_file():
                print(f"ROLLBACK_BACKUP_MISSING: {rel}", file=sys.stderr)
                return 4
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        elif target.is_file() or target.is_symlink():
            target.unlink()

    # Remove install receipts matching this backup / transaction.
    tx_sha = "sha256:" + (sha256(manifest_path) or "")
    backup_id = backup.name
    receipt_dirs = [project / ".smc" / "ges-install-receipts"]
    for rdir in receipt_dirs:
        if not rdir.is_dir():
            continue
        for receipt in rdir.glob("*.json"):
            try:
                rec = json.loads(receipt.read_text(encoding="utf-8"))
                if rec.get("install_id") == backup_id or rec.get("backup_id") == backup_id:
                    receipt.unlink()
            except (OSError, json.JSONDecodeError):
                pass
    # Legacy single-file receipt
    receipt = project / ".smc" / "ges-install-receipt.json"
    if receipt.is_file():
        try:
            rec = json.loads(receipt.read_text(encoding="utf-8"))
            if (
                rec.get("transaction_manifest_sha256") == tx_sha
                or rec.get("install_id") == backup_id
                or (rec.get("receipt_path") or "").endswith(f"{backup_id}.json")
            ):
                receipt.unlink()
        except (OSError, json.JSONDecodeError):
            pass

    data["rollback_status"] = "ROLLED_BACK_MANUALLY"
    manifest_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("ROLLBACK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
