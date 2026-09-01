from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import yaml

from governance_lib import ROOT, load_yaml, project_catalog, repository_catalog


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_commit() -> str | None:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def current_tag_for_commit(commit: str) -> str | None:
    result = subprocess.run(["git", "tag", "--points-at", commit], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    for tag in result.stdout.splitlines():
        tag = tag.strip()
        if tag.startswith("governance-kit-v"):
            return tag
    tags = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return tags[0] if tags else None


def kit_pin(version: str) -> dict:
    commit = current_commit()
    tag = current_tag_for_commit(commit or "") if commit else None
    manifest_path = ROOT / "dist" / f"governance-kit-v{version}" / "manifest.json"
    manifest_sha256 = None
    if manifest_path.exists():
        manifest_sha256 = json.loads(manifest_path.read_text(encoding="utf-8")).get("manifest_sha256")
    return {
        "version": version,
        "tag": tag,
        "commit": commit,
        "manifest_sha256": manifest_sha256,
    }


def copy_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--project", required=True)
    ap.add_argument("--repository-id")
    ap.add_argument("--feature", action="append", default=[])
    ap.add_argument("--with-ci", action="store_true")
    ap.add_argument("--allow-unsigned-head", action="store_true")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        raise SystemExit(f"repo not found: {repo}")
    projects = project_catalog()
    repos = repository_catalog()
    project = projects.get(args.project)
    if not project:
        raise SystemExit(f"unknown project: {args.project}")
    repo_ids = project.get("repositories", [])
    rid = args.repository_id or (repo_ids[0] if len(repo_ids) == 1 else None)
    if not rid or rid not in repos:
        raise SystemExit("repository-id required or invalid")
    repo_def = repos[rid]

    manifest = load_yaml(ROOT / "skills/manifest.yaml")
    kit_version = manifest["kit"]["version"]
    pin = kit_pin(kit_version)
    if not pin.get("tag") and not args.allow_unsigned_head:
        raise SystemExit("governance kit tag missing; create governance-kit-v* tag or use --allow-unsigned-head")

    dest = repo / manifest["sync"]["destination"]
    lock_file = repo / manifest["sync"]["lock_file"]
    central_commit = pin.get("commit")
    feature_bindings = []
    matching_wps = []
    contract_ids = set()
    for feature_id in args.feature:
        fdir = ROOT / "features" / feature_id
        if not fdir.exists():
            raise SystemExit(f"feature not found: {feature_id}")
        feature_doc = load_yaml(fdir / "feature.yaml")
        matched = None
        for p in (fdir / "work-packages").glob("*.yaml"):
            wp = load_yaml(p)
            if wp.get("repository_id") == rid:
                matched = (p, wp)
                break
        if not matched:
            raise SystemExit(f"no work package for {rid} in {feature_id}")
        p, wp = matched
        matching_wps.append((feature_id, p, wp))
        for c in feature_doc.get("contracts", []):
            contract_ids.add(c["contract_id"])
        feature_bindings.append(
            {
                "feature_id": feature_id,
                "work_package_id": wp["work_package_id"],
                "source_revision": wp["source_revision"],
            }
        )

    binding = {
        "binding_version": "2",
        "central_repository": "loudon84/smc-delivery-governance",
        "kit": {
            "name": manifest["kit"]["name"],
            "version": kit_version,
            "tag": pin.get("tag"),
            "commit": central_commit,
            "manifest_sha256": pin.get("manifest_sha256"),
        },
        "project_id": args.project,
        "repository_id": rid,
        "governance_policy": repo_def.get("governance_policy", "REPOSITORY-GOVERNANCE-V1"),
        "features": feature_bindings,
    }

    generated_binding = yaml.safe_dump(binding, sort_keys=False, allow_unicode=True).encode("utf-8")
    project_status = {
        "report_version": "2",
        "project_id": args.project,
        "repository_id": rid,
        "kit_version": kit_version,
        "kit": binding["kit"],
        "governance_policy": repo_def.get("governance_policy", "REPOSITORY-GOVERNANCE-V1"),
        "central_commit": central_commit,
        "enforcement": bool(args.with_ci),
        "reported_at": None,
    }
    generated_project_status = yaml.safe_dump(project_status, sort_keys=False, allow_unicode=True).encode("utf-8")
    expected = {
        "binding.yaml": hashlib.sha256(generated_binding).hexdigest(),
        "project-status.yaml": hashlib.sha256(generated_project_status).hexdigest(),
    }
    for skill_name in manifest.get("universal", []):
        for src in sorted((ROOT / "skills/universal" / skill_name).rglob("*")):
            if src.is_file():
                expected[f"skills/{skill_name}/{src.relative_to(ROOT / 'skills/universal' / skill_name).as_posix()}"] = sha256(src)
    for schema_name in [
        "artifact-ref.schema.json",
        "delivery-receipt.schema.json",
        "acceptance-manifest.schema.json",
        "acceptance-report.schema.json",
        "project-report.schema.json",
    ]:
        expected[f"schemas/{schema_name}"] = sha256(ROOT / "schemas" / schema_name)
    expected["tools/validate_local_governance.py"] = sha256(ROOT / "templates/project/tools/validate_local_governance.py")
    for feature_id, p, wp in matching_wps:
        expected[f"work-packages/{feature_id}.yaml"] = sha256(p)
    for cid in sorted(contract_ids):
        for p in (ROOT / "registry/contracts").glob("*.yaml"):
            c = load_yaml(p)
            if c.get("contract_id") == cid:
                expected[f"contracts/{cid}.yaml"] = sha256(p)
    if args.with_ci:
        for rel in [
            "github/workflows/smc-governance.yml",
            "github/workflows/smc-governance-dispatch.yml",
            "github/workflows/smc-governance-labels.yml",
            "github/ISSUE_TEMPLATE/governed-bug.yml",
            "github/ISSUE_TEMPLATE/governed-work.yml",
            "github/pull_request_template.md",
        ]:
            src = ROOT / "templates/project" / rel.replace("github/", ".github/")
            if src.exists():
                expected[rel] = sha256(src)

    lock = {
        "kit": manifest["kit"]["name"],
        "version": kit_version,
        "tag": pin.get("tag"),
        "commit": central_commit,
        "manifest_sha256": pin.get("manifest_sha256"),
        "project_id": args.project,
        "repository_id": rid,
        "features": [x["feature_id"] for x in feature_bindings],
        "files": expected,
    }

    if args.check:
        if not lock_file.exists():
            print("OUT_OF_SYNC: governance.lock missing")
            raise SystemExit(2)
        current = json.loads(lock_file.read_text(encoding="utf-8"))
        if current != lock:
            print("OUT_OF_SYNC: governance.lock differs")
            raise SystemExit(2)
        for rel, digest in expected.items():
            target = repo / ".github" / rel[len("github/") :] if rel.startswith("github/") else dest / rel
            if not target.exists() or sha256(target) != digest:
                print(f"OUT_OF_SYNC: {rel}")
                raise SystemExit(2)
        print("GOVERNANCE SYNC OK")
        return

    dest.mkdir(parents=True, exist_ok=True)
    (dest / "binding.yaml").write_bytes(generated_binding)
    (dest / "project-status.yaml").write_bytes(generated_project_status)
    for skill_name in manifest.get("universal", []):
        copy_tree(ROOT / "skills/universal" / skill_name, dest / "skills" / skill_name)
    for schema_name in [
        "artifact-ref.schema.json",
        "delivery-receipt.schema.json",
        "acceptance-manifest.schema.json",
        "acceptance-report.schema.json",
        "project-report.schema.json",
    ]:
        copy_file(ROOT / "schemas" / schema_name, dest / "schemas" / schema_name)
    copy_file(ROOT / "templates/project/tools/validate_local_governance.py", dest / "tools/validate_local_governance.py")
    for feature_id, p, wp in matching_wps:
        copy_file(p, dest / "work-packages" / f"{feature_id}.yaml")
        receipt = dest / "receipts" / f"{wp['work_package_id']}.yaml"
        if not receipt.exists():
            receipt.parent.mkdir(parents=True, exist_ok=True)
            skeleton = {
                "receipt_version": "2",
                "feature_id": feature_id,
                "work_package_id": wp["work_package_id"],
                "repository_id": rid,
                "source_revision": wp["source_revision"],
                "status": "BACKLOG",
                "sync": {
                    "governance_kit_version": kit_version,
                    "central_commit": central_commit,
                    "kit": binding["kit"],
                    "contract_pins": [
                        {
                            "contract_id": x["contract_id"],
                            "version": x.get("version") or x.get("required_version", ""),
                            "tag": None,
                            "commit": None,
                        }
                        for x in wp.get("contract_inputs", [])
                    ],
                },
                "delivery": {
                    "stage_prds": [],
                    "issues": [],
                    "bugs": [],
                    "plans": [],
                    "pull_requests": [],
                    "commits": [],
                    "verification_reports": [],
                },
                "acceptance": {"manifest": None, "report": None, "status": "NOT_DEFINED"},
                "evidence": {},
                "reported_at": "1970-01-01T00:00:00+00:00",
            }
            receipt.write_text(yaml.safe_dump(skeleton, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n")
    for cid in sorted(contract_ids):
        for p in (ROOT / "registry/contracts").glob("*.yaml"):
            c = load_yaml(p)
            if c.get("contract_id") == cid:
                copy_file(p, dest / "contracts" / f"{cid}.yaml")
    if args.with_ci:
        for rel in [
            "workflows/smc-governance.yml",
            "workflows/smc-governance-dispatch.yml",
            "workflows/smc-governance-labels.yml",
            "ISSUE_TEMPLATE/governed-bug.yml",
            "ISSUE_TEMPLATE/governed-work.yml",
            "pull_request_template.md",
        ]:
            src = ROOT / "templates/project/.github" / rel
            if src.exists():
                copy_file(src, repo / ".github" / rel)
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_file.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"SYNCED {args.project}/{rid} -> {dest}")
    print(f"LOCK {lock_file}")


if __name__ == "__main__":
    main()
