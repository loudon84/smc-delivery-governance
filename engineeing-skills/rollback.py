#!/usr/bin/env python3
"""Rollback a completed SMC Skills overlay transaction safely."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def latest_backup(project: Path) -> Path | None:
    root = project / ".smc" / "skill-upgrade-backups"
    candidates = sorted((p for p in root.iterdir() if p.is_dir() and (p / "upgrade-manifest.json").is_file()), reverse=True) if root.is_dir() else []
    return candidates[0] if candidates else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("--backup", type=Path, help="specific backup transaction; default latest")
    ap.add_argument("--apply", action="store_true", help="perform rollback; default dry-run")
    ap.add_argument("--force", action="store_true", help="rollback even when files changed after install")
    args = ap.parse_args()
    project = args.project.resolve()
    backup = args.backup.resolve() if args.backup else latest_backup(project)
    if backup is None or not (backup / "upgrade-manifest.json").is_file():
        print("ROLLBACK_TRANSACTION_NOT_FOUND", file=sys.stderr)
        return 2
    manifest_path = backup / "upgrade-manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = data.get("files") or []
    if not isinstance(files, list) or not files:
        print("ROLLBACK_MANIFEST_INVALID", file=sys.stderr)
        return 2

    drift: list[str] = []
    for rec in files:
        target = project / rec["path"]
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
            print("ROLLBACK_BLOCKED_BY_POST_INSTALL_DRIFT — use --force only after reviewing the listed files.", file=sys.stderr)
            return 3
    if not args.apply:
        print("DRY RUN PASS — rerun with --apply to rollback.")
        return 0

    for rec in reversed(files):
        rel = rec["path"]
        target = project / rel
        if rec.get("existed_before"):
            source = backup / rel
            if not source.is_file():
                print(f"ROLLBACK_BACKUP_MISSING: {rel}", file=sys.stderr)
                return 4
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        elif target.is_file() or target.is_symlink():
            target.unlink()

    data["rollback_status"] = "ROLLED_BACK_MANUALLY"
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("ROLLBACK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
