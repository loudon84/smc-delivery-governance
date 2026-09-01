from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import yaml

from governance_lib import ROOT, load_yaml, project_catalog, repository_catalog
from governance_kit import build_kit, fetch_release_bundle, verify_kit

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def copy_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

def copy_tree(src: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)

def source_head() -> str | None:
    import subprocess
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None

def resolve_kit(args, manifest: dict) -> tuple[Path, dict]:
    version = manifest["kit"]["version"]
    expected_tag = f"governance-kit-v{version}"
    if args.kit_dir:
        kit_dir = Path(args.kit_dir).resolve()
        evidence = verify_kit(kit_dir, expected_version=version, expected_tag=expected_tag)
        return kit_dir, evidence

    local = ROOT / "dist" / expected_tag
    if local.exists():
        evidence = verify_kit(local, expected_version=version, expected_tag=expected_tag)
        return local, evidence

    if not args.offline:
        try:
            kit_dir = fetch_release_bundle(version=version, token=args.token)
            evidence = verify_kit(kit_dir, expected_version=version, expected_tag=expected_tag)
            return kit_dir, evidence
        except Exception as exc:
            if not (args.allow_source_tree or args.allow_unsigned_head):
                raise SystemExit(f"canonical governance kit unavailable: {exc}") from exc

    if not (args.allow_source_tree or args.allow_unsigned_head):
        raise SystemExit(
            "canonical governance kit required; use --kit-dir, fetch release, or explicit --allow-source-tree for development"
        )

    commit = source_head() or ("0" * 40)
    temp_root = ROOT / ".cache" / "governance-kits"
    kit_dir = temp_root / f"DEV-governance-kit-v{version}"
    build_kit(
        source_root=ROOT,
        version=version,
        commit=commit,
        tag=f"DEV-governance-kit-v{version}",
        output_dir=kit_dir,
    )
    evidence = verify_kit(kit_dir, expected_version=version)
    evidence["development_unsigned"] = True
    return kit_dir, evidence

def kit_manifest(kit_dir: Path) -> dict:
    return json.loads((kit_dir / "manifest.json").read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--project", required=True)
    ap.add_argument("--repository-id")
    ap.add_argument("--feature", action="append", default=[])
    ap.add_argument("--with-ci", action="store_true")
    ap.add_argument("--kit-dir")
    ap.add_argument("--token")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--allow-source-tree", action="store_true")
    # v1.1/v1.2 compatibility alias; production behavior is identical to --allow-source-tree.
    ap.add_argument("--allow-unsigned-head", action="store_true", help=argparse.SUPPRESS)
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
    kit_dir, kit_evidence = resolve_kit(args, manifest)
    kmanifest = kit_manifest(kit_dir)
    kit_meta = kmanifest["kit"]
    if kit_evidence.get("development_unsigned"):
        kit_tag = kit_meta["tag"]
    else:
        expected = f"governance-kit-v{manifest['kit']['version']}"
        if kit_meta.get("tag") != expected:
            raise SystemExit(f"canonical kit tag mismatch: {kit_meta.get('tag')} != {expected}")
        kit_tag = kit_meta["tag"]

    pin = {
        "version": kit_meta["version"],
        "tag": kit_tag,
        "commit": kit_meta["commit"],
        "manifest_sha256": kit_evidence["manifest_sha256"],
    }

    dest = repo / manifest["sync"]["destination"]
    lock_file = repo / manifest["sync"]["lock_file"]
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
        feature_bindings.append({
            "feature_id": feature_id,
            "work_package_id": wp["work_package_id"],
            "source_revision": wp["source_revision"],
        })

    binding = {
        "binding_version": "2",
        "central_repository": "loudon84/smc-delivery-governance",
        "kit": pin,
        "project_id": args.project,
        "repository_id": rid,
        "governance_policy": repo_def.get("governance_policy", "REPOSITORY-GOVERNANCE-V1"),
        "features": feature_bindings,
    }
    binding_bytes = yaml.safe_dump(binding, sort_keys=False, allow_unicode=True).encode("utf-8")

    project_status = {
        "report_version": "2",
        "project_id": args.project,
        "repository_id": rid,
        "kit_version": pin["version"],
        "kit": pin,
        "governance_policy": binding["governance_policy"],
        "central_commit": pin["commit"],
        "enforcement": bool(args.with_ci),
        "reported_at": None,
    }
    status_bytes = yaml.safe_dump(project_status, sort_keys=False, allow_unicode=True).encode("utf-8")

    expected = {
        "binding.yaml": hashlib.sha256(binding_bytes).hexdigest(),
        "project-status.yaml": hashlib.sha256(status_bytes).hexdigest(),
        "kit/manifest.json": sha256(kit_dir / "manifest.json"),
        "kit/SHA256SUMS": sha256(kit_dir / "SHA256SUMS"),
    }

    # Canonical kit files are copied from the verified release bundle, never from ROOT.
    canonical_files = kmanifest.get("files") or {}
    for rel, digest in canonical_files.items():
        if rel.startswith("github/") and not args.with_ci:
            continue
        expected[rel] = digest

    for feature_id, p, wp in matching_wps:
        expected[f"work-packages/{feature_id}.yaml"] = sha256(p)
    contract_sources = {}
    for cid in sorted(contract_ids):
        for p in (ROOT / "registry/contracts").glob("*.yaml"):
            c = load_yaml(p)
            if c.get("contract_id") == cid:
                expected[f"contracts/{cid}.yaml"] = sha256(p)
                contract_sources[cid] = p
                break

    lock = {
        "kit": manifest["kit"]["name"],
        "version": pin["version"],
        "tag": pin["tag"],
        "commit": pin["commit"],
        "manifest_sha256": pin["manifest_sha256"],
        "project_id": args.project,
        "repository_id": rid,
        "features": [x["feature_id"] for x in feature_bindings],
        "files": expected,
    }

    def target_for(rel: str) -> Path:
        return repo / ".github" / rel[len("github/"):] if rel.startswith("github/") else dest / rel

    if args.check:
        if not lock_file.exists():
            print("OUT_OF_SYNC: governance.lock missing")
            raise SystemExit(2)
        current = json.loads(lock_file.read_text(encoding="utf-8"))
        if current != lock:
            print("OUT_OF_SYNC: governance.lock differs")
            raise SystemExit(2)
        for rel, digest in expected.items():
            target = target_for(rel)
            if not target.exists() or sha256(target) != digest:
                print(f"OUT_OF_SYNC: {rel}")
                raise SystemExit(2)
        print("GOVERNANCE SYNC OK")
        return

    dest.mkdir(parents=True, exist_ok=True)
    (dest / "binding.yaml").write_bytes(binding_bytes)
    (dest / "project-status.yaml").write_bytes(status_bytes)
    copy_file(kit_dir / "manifest.json", dest / "kit" / "manifest.json")
    copy_file(kit_dir / "SHA256SUMS", dest / "kit" / "SHA256SUMS")

    for rel in canonical_files:
        if rel.startswith("github/") and not args.with_ci:
            continue
        copy_file(kit_dir / rel, target_for(rel))

    for feature_id, p, wp in matching_wps:
        copy_file(p, dest / "work-packages" / f"{feature_id}.yaml")
        receipt = dest / "receipts" / f"{wp['work_package_id']}.yaml"
        if not receipt.exists():
            receipt.parent.mkdir(parents=True, exist_ok=True)
            contract_pins = []
            for x in wp.get("contract_inputs", []):
                cid = x["contract_id"]
                version = x.get("version") or x.get("required_version")
                contract_doc = load_yaml(contract_sources[cid]) if cid in contract_sources else {}
                release = next((r for r in contract_doc.get("releases", []) if r.get("version") == version), None)
                if not release:
                    raise SystemExit(f"contract release not found for pin: {cid}@{version}")
                contract_pins.append({
                    "contract_id": cid,
                    "version": version,
                    "tag": release.get("tag"),
                    "commit": release.get("peeled_commit"),
                })
            if any(not p.get("tag") or not p.get("commit") for p in contract_pins):
                raise SystemExit("contract pin requires immutable tag and commit")

            skeleton = {
                "receipt_version": "2",
                "feature_id": feature_id,
                "work_package_id": wp["work_package_id"],
                "repository_id": rid,
                "source_revision": wp["source_revision"],
                "status": "BACKLOG",
                "sync": {
                    "governance_kit_version": pin["version"],
                    "central_commit": pin["commit"],
                    "kit": pin,
                    "contract_pins": contract_pins,
                },
                "delivery": {
                    "stage_prds": [], "issues": [], "bugs": [], "plans": [],
                    "pull_requests": [], "commits": [], "verification_reports": [],
                },
                "acceptance": {"manifest": None, "report": None, "status": "NOT_DEFINED"},
                "evidence": {},
                "reported_at": "1970-01-01T00:00:00+00:00",
            }
            receipt.write_text(
                yaml.safe_dump(skeleton, sort_keys=False, allow_unicode=True),
                encoding="utf-8", newline="\n"
            )

    for cid, p in contract_sources.items():
        copy_file(p, dest / "contracts" / f"{cid}.yaml")

    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_file.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"SYNCED {args.project}/{rid} -> {dest}")
    print(f"KIT {pin['tag']} commit={pin['commit']} manifest={pin['manifest_sha256']}")
    print(f"LOCK {lock_file}")

if __name__ == "__main__":
    main()
