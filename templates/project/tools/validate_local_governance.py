from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import yaml

from governance_lib import ROOT, validate_jsonschema


def repo_root() -> Path:
    git = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if git.returncode == 0:
        return Path(git.stdout.strip())
    return Path(".").resolve()


def validate_semantics(root: Path) -> list[str]:
    errors = []
    binding = yaml.safe_load((root / ".agents/governance/binding.yaml").read_text(encoding="utf-8"))
    for receipt_path in (root / ".agents/governance/receipts").glob("*.yaml"):
        receipt = yaml.safe_load(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("source_revision") != binding["features"][0].get("source_revision"):
            for feat in binding.get("features", []):
                if feat.get("work_package_id") == receipt.get("work_package_id"):
                    if receipt.get("source_revision") != feat.get("source_revision"):
                        errors.append(f"{receipt_path}: source_revision mismatch with binding")
        for key in ("stage_prds", "plans"):
            for item in receipt.get("delivery", {}).get(key, []):
                path = root / item.get("path", "")
                if item.get("path") and not path.exists():
                    errors.append(f"{receipt_path}: missing local path {item['path']}")
                if key == "stage_prds" and item.get("status") != "APPROVED":
                    errors.append(f"{receipt_path}: stage PRD must be APPROVED")
                if key == "plans" and item.get("status") not in {"VALIDATED", "PASS"}:
                    errors.append(f"{receipt_path}: plan must be VALIDATED")
        commits = receipt.get("delivery", {}).get("commits", [])
        if commits:
            head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
            if head.returncode == 0:
                known = {line.split()[0] for line in subprocess.run(["git", "rev-list", "--all"], cwd=root, capture_output=True, text=True).stdout.splitlines()}
                for commit in commits:
                    if commit not in known and not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
                        errors.append(f"{receipt_path}: invalid commit {commit}")
        acceptance = receipt.get("acceptance") or {}
        report_rel = acceptance.get("report")
        if report_rel:
            report_path = root / report_rel
            if report_path.exists():
                report = json.loads(report_path.read_text(encoding="utf-8"))
                if commits and report.get("repository_commit") not in commits:
                    errors.append(f"{report_path}: repository_commit must match implementation commit")
                provenance = report.get("provenance") or {}
                if provenance and provenance.get("commit") and provenance.get("commit") != report.get("repository_commit"):
                    errors.append(f"{report_path}: provenance commit mismatch")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--semantic", action="store_true", default=True)
    args = ap.parse_args()
    root = repo_root()
    gov = root / ".agents/governance"
    errors = []
    ps = gov / "project-status.yaml"
    if ps.exists():
        errors += [f"{ps}: {msg}" for msg in _schema_errors(ps, gov / "schemas/project-report.schema.json")]
    for p in (gov / "receipts").glob("*.yaml"):
        errors += [f"{p}: {msg}" for msg in _schema_errors(p, gov / "schemas/delivery-receipt.schema.json")]
    for p in (gov / "acceptance").glob("*.yaml"):
        errors += [f"{p}: {msg}" for msg in _schema_errors(p, gov / "schemas/acceptance-manifest.schema.json")]
    for p in (gov / "acceptance").glob("*.report.json"):
        errors += [f"{p}: {msg}" for msg in _schema_errors(p, gov / "schemas/acceptance-report.schema.json")]
    if args.semantic:
        errors.extend(validate_semantics(root))
    if errors:
        print("LOCAL GOVERNANCE INVALID")
        for err in errors:
            print("-", err)
        raise SystemExit(1)
    print("LOCAL GOVERNANCE VALID")


def _schema_errors(path: Path, schema: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.suffix in {".yaml", ".yml"} else json.loads(path.read_text(encoding="utf-8"))
    return validate_jsonschema(data, schema)


if __name__ == "__main__":
    main()
