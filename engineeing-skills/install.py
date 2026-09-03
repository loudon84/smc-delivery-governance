#!/usr/bin/env python3
"""Install SMC Governed Engineering Skills v4.1.1 as a transactional overlay.

Dry-run by default. Use --apply to write. Every touched file is recorded and
backed up under .smc/skill-upgrade-backups/<timestamp>/. If post-install
validation fails, the installer automatically restores the pre-upgrade state.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
OVERLAY = PACKAGE / ".agents" / "skills"
INTEGRATION = PACKAGE / "project-integration"
PACKAGE_VERSION = "4.1.1"
IGNORE_LINES = [
    ".smc/evidence/",
    ".smc/reviews/",
    ".smc/runs/",
    ".smc/skill-upgrade-backups/",
    "__pycache__/",
    "*.py[cod]",
]

REQUIRED_BASELINE = [
    ".agents/skills/smc-plan-validator/scripts/validate_plan.py",
    ".agents/skills/smc-plan-review/scripts/assess_plan_review.py",
    ".agents/skills/smc-plan-from-approved-prd-ponytail/scripts/validate_generation_integrity.py",
    ".agents/skills/smc-plan-from-approved-prd-ponytail/references/ponytail-minimality.md",
    ".agents/skills/smc-plan-from-approved-prd-ponytail/references/ownership-aware-slicing.md",
    ".agents/skills/smc-plan-from-approved-prd-ponytail/references/generation-integrity-gates.md",
    ".agents/skills/smc-plan-from-approved-prd-ponytail/references/source-basis.md",
    ".agents/skills/smc-roadmap/scripts/validate_roadmap.py",
    ".agents/skills/smc-roadmap/scripts/roadmap_update.py",
    ".agents/skills/code-review-and-quality/SKILL.md",
    ".agents/references/prd-contract.md",
    ".agents/references/evidence-contract.md",
    ".agents/references/architecture-convergence.md",
    ".cursor/skills",
]


def now_tag() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def rel_files(root: Path) -> list[Path]:
    return sorted(
        p.relative_to(root)
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    )


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(x) for x in cmd))
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(cmd, cwd=cwd, text=True, encoding="utf-8", errors="replace", env=env)


def record_before(project: Path, target: Path, backup_root: Path, records: dict[str, dict]) -> dict:
    try:
        rel = target.relative_to(project).as_posix()
    except ValueError as exc:
        raise RuntimeError(f"TARGET_OUTSIDE_PROJECT: {target}") from exc
    if rel in records:
        return records[rel]
    existed = target.is_file()
    record = {
        "path": rel,
        "existed_before": existed,
        "original_sha256": sha256(target) if existed else None,
        "installed_sha256": None,
    }
    records[rel] = record
    if existed:
        dest = backup_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, dest)
    return record


def mark_after(target: Path, record: dict) -> None:
    record["installed_sha256"] = sha256(target)


def copy_overlay(project: Path, backup_root: Path, records: dict[str, dict]) -> int:
    count = 0
    for rel in rel_files(OVERLAY):
        src = OVERLAY / rel
        for dest in (project / ".agents" / "skills" / rel, project / ".cursor" / "skills" / rel):
            rec = record_before(project, dest, backup_root, records)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            mark_after(dest, rec)
        count += 1
    return count


def copy_integration(project: Path, backup_root: Path, records: dict[str, dict]) -> int:
    count = 0
    if not INTEGRATION.is_dir():
        return count
    for rel in rel_files(INTEGRATION):
        src = INTEGRATION / rel
        dest = project / rel
        rec = record_before(project, dest, backup_root, records)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        mark_after(dest, rec)
        count += 1
    return count


def patch_governed_skills(project: Path, backup_root: Path, records: dict[str, dict]) -> bool:
    path = project / "tools" / "agent-skills" / "validate_agent_skills.py"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    if '"smc-plan-delivery"' in text:
        return False
    marker = '    "executing-plans",\n'
    if marker not in text:
        print("WARN: validate_agent_skills.py GOVERNED_SKILLS marker not found; skip managed patch")
        return False
    rec = record_before(project, path, backup_root, records)
    path.write_text(text.replace(marker, marker + '    "smc-plan-delivery",\n', 1), encoding="utf-8")
    mark_after(path, rec)
    return True


def update_gitignore(project: Path, backup_root: Path, records: dict[str, dict]) -> bool:
    path = project / ".gitignore"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    current = {line.strip() for line in text.splitlines()}
    missing = [x for x in IGNORE_LINES if x not in current]
    if not missing:
        return False
    rec = record_before(project, path, backup_root, records)
    suffix = "\n" if text and not text.endswith("\n") else ""
    block = "# SMC governed delivery local state/evidence\n" + "\n".join(missing) + "\n"
    path.write_text(text + suffix + ("\n" if text else "") + block, encoding="utf-8")
    mark_after(path, rec)
    return True


def write_transaction_manifest(project: Path, backup_root: Path, records: dict[str, dict], status: str) -> Path:
    payload = {
        "schema": "smc.skill.upgrade.transaction.v1",
        "package": PACKAGE.name,
        "package_version": PACKAGE_VERSION,
        "project": str(project),
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "files": [records[key] for key in sorted(records)],
    }
    path = backup_root / "upgrade-manifest.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def restore(project: Path, backup_root: Path, records: dict[str, dict]) -> None:
    for rel in reversed(sorted(records)):
        rec = records[rel]
        target = project / rel
        if rec["existed_before"]:
            source = backup_root / rel
            if not source.is_file():
                raise RuntimeError(f"ROLLBACK_BACKUP_MISSING: {rel}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        else:
            if target.is_file() or target.is_symlink():
                target.unlink()
    # Prune only newly-created empty directories under known upgrade roots.
    for base in (project / ".agents" / "skills", project / ".cursor" / "skills", project / "tools" / "agent-skills"):
        if not base.exists():
            continue
        for directory in sorted((p for p in base.rglob("*") if p.is_dir()), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass



def verify_package_integrity() -> list[str]:
    sums = PACKAGE / "SHA256SUMS"
    if not sums.is_file():
        return ["PACKAGE_SHA256SUMS_MISSING"]
    errors: list[str] = []
    seen: set[str] = set()
    for line in sums.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            digest, rel = line.split("  ", 1)
        except ValueError:
            errors.append(f"PACKAGE_SHA256SUMS_INVALID_LINE: {line}")
            continue
        rel = rel.strip().replace("\\", "/")
        if rel in seen:
            errors.append(f"PACKAGE_SHA256SUMS_DUPLICATE: {rel}")
            continue
        seen.add(rel)
        target = (PACKAGE / rel).resolve()
        try:
            target.relative_to(PACKAGE.resolve())
        except ValueError:
            errors.append(f"PACKAGE_SHA256SUMS_PATH_ESCAPE: {rel}")
            continue
        actual = sha256(target)
        if actual != digest:
            errors.append(f"PACKAGE_INTEGRITY_MISMATCH: {rel}: expected={digest} actual={actual}")
    for rel in ("install.py", "rollback.py", ".agents/skills/smc-plan-delivery/SKILL.md", ".agents/skills/smc-roadmap/scripts/validate_roadmap_v11.py"):
        if rel not in seen:
            errors.append(f"PACKAGE_SHA256SUMS_REQUIRED_FILE_MISSING: {rel}")
    return errors

def preflight(project: Path) -> list[str]:
    errors: list[str] = verify_package_integrity()
    if not (project / ".agents" / "skills").is_dir():
        errors.append("TARGET_NOT_SMC_REPO: .agents/skills missing")
    for rel in REQUIRED_BASELINE:
        if not (project / rel).exists():
            errors.append(f"BASELINE_DEPENDENCY_MISSING: {rel}")
    if not (project / ".git").exists():
        errors.append("TARGET_NOT_GIT_REPO: .git missing")
    return errors


def preview(project: Path) -> None:
    print(f"Package: {PACKAGE.name}")
    print(f"Target : {project}")
    print(f"Overlay files: {len(rel_files(OVERLAY))}")
    print("Writes:")
    for rel in rel_files(OVERLAY):
        print(f"  .agents/skills/{rel}")
        print(f"  .cursor/skills/{rel}  [mirror]")
    for rel in rel_files(INTEGRATION):
        print(f"  {rel}  [project integration]")
    print("  tools/agent-skills/validate_agent_skills.py  [managed set patch if needed]")
    print("  .gitignore  [append local .smc state paths if needed]")


def validation_commands(project: Path, skip_project_validator: bool) -> list[tuple[str, list[str]]]:
    commands = [
        ("delivery self-test", [sys.executable, str(project / ".agents/skills/smc-plan-delivery/scripts/run_selftest.py")]),
        ("roadmap v1.1 self-test", [sys.executable, str(project / ".agents/skills/smc-roadmap/scripts/test_roadmap_v11.py"), "-q"]),
    ]
    project_validator = project / "tools" / "agent-skills" / "validate_agent_skills.py"
    if project_validator.is_file() and not skip_project_validator:
        commands.append(("project skill validator", [sys.executable, str(project_validator)]))
    return commands


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("--apply", action="store_true", help="apply the overlay; default is dry-run")
    ap.add_argument("--skip-project-validator", action="store_true", help="installer smoke/test escape hatch; production should not use")
    args = ap.parse_args()
    project = args.project.resolve()
    errors = preflight(project)
    preview(project)
    if errors:
        print("\nPRECHECK FAILED", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 2
    if not args.apply:
        print("\nDRY RUN PASS — rerun with --apply to install.")
        return 0

    backup_root = project / ".smc" / "skill-upgrade-backups" / now_tag()
    backup_root.mkdir(parents=True, exist_ok=False)
    records: dict[str, dict] = {}
    try:
        overlay_count = copy_overlay(project, backup_root, records)
        integration_count = copy_integration(project, backup_root, records)
        patched = patch_governed_skills(project, backup_root, records)
        ignored = update_gitignore(project, backup_root, records)
        manifest = write_transaction_manifest(project, backup_root, records, "VALIDATING")
    except Exception as exc:
        try:
            restore(project, backup_root, records)
            write_transaction_manifest(project, backup_root, records, "ROLLED_BACK_AFTER_WRITE_FAILURE")
        except Exception as rollback_exc:
            print(f"ROLLBACK_FAILED: {rollback_exc}", file=sys.stderr)
        print(f"INSTALL_FAILED: {exc}", file=sys.stderr)
        print(f"Backup transaction: {backup_root}", file=sys.stderr)
        return 3

    for label, command in validation_commands(project, args.skip_project_validator):
        result = run(command, project)
        if result.returncode:
            print(f"INSTALL_VALIDATION_FAILED: {label}; automatic rollback starting", file=sys.stderr)
            try:
                restore(project, backup_root, records)
                manifest = write_transaction_manifest(project, backup_root, records, f"ROLLED_BACK_AFTER_{label.replace(' ', '_').upper()}")
                print(f"ROLLBACK PASS — original project files restored. Transaction retained at {backup_root}", file=sys.stderr)
            except Exception as exc:
                write_transaction_manifest(project, backup_root, records, "ROLLBACK_FAILED")
                print(f"ROLLBACK_FAILED: {exc}; manual recovery required from {backup_root}", file=sys.stderr)
            return 4

    manifest = write_transaction_manifest(project, backup_root, records, "INSTALLED")
    print("\nINSTALL PASS")
    print(f"Overlay source files : {overlay_count}")
    print(f"Integration files    : {integration_count}")
    print(f"Governed set patched : {patched}")
    print(f".gitignore updated   : {ignored}")
    print(f"Backup transaction   : {backup_root}")
    print(f"Transaction manifest : {manifest}")
    print("No git commit was created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
