from __future__ import annotations

import argparse
import json
import yaml

from governance_lib import github_content_metadata, repository_catalog, load_feature, load_work_packages

def get_yaml(repo_name: str, path: str, ref: str, token=None):
    meta = github_content_metadata(repo_name, path, ref, token=token)
    if not meta:
        return None
    return yaml.safe_load(meta["bytes"].decode("utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repository_id")
    ap.add_argument("feature")
    ap.add_argument("--token")
    args = ap.parse_args()

    repo = repository_catalog().get(args.repository_id)
    if not repo:
        raise SystemExit("unknown repository")
    fdir, feature = load_feature(args.feature)
    wps = load_work_packages(fdir)
    wp = next((x for x in wps.values() if x["repository_id"] == args.repository_id), None)
    if not wp:
        raise SystemExit("feature has no work package for repository")

    ref = repo["default_branch"]
    binding = get_yaml(repo["name"], ".agents/governance/binding.yaml", ref, args.token)
    status = get_yaml(repo["name"], ".agents/governance/project-status.yaml", ref, args.token)
    receipt_path = f"{repo['governance']['delivery_receipts'].rstrip('/')}/{wp['work_package_id']}.yaml"
    receipt = get_yaml(repo["name"], receipt_path, ref, args.token)

    errors = []
    if not binding:
        errors.append("binding.yaml missing")
    else:
        if binding.get("repository_id") != args.repository_id:
            errors.append("binding repository_id mismatch")
        matched = next((x for x in binding.get("features", []) if x.get("work_package_id") == wp["work_package_id"]), None)
        if not matched:
            errors.append("feature/work-package missing from binding")
        elif matched.get("source_revision") != wp.get("source_revision"):
            errors.append("binding source_revision stale")
        kit = binding.get("kit") or {}
        for key in ("version","tag","commit","manifest_sha256"):
            if not kit.get(key):
                errors.append(f"binding kit.{key} missing")

    if not status:
        errors.append("project-status.yaml missing")
    if not receipt:
        errors.append(f"receipt missing: {receipt_path}")
    else:
        if receipt.get("feature_id") != feature["feature_id"] or receipt.get("work_package_id") != wp["work_package_id"]:
            errors.append("receipt identity mismatch")
        if receipt.get("source_revision") != wp.get("source_revision"):
            errors.append("receipt source_revision stale")

    if errors:
        print("REMOTE BOOTSTRAP FAIL")
        for e in errors:
            print("-", e)
        raise SystemExit(2)
    print("REMOTE BOOTSTRAP PASS")
    print(f"{args.repository_id} {repo['name']}@{ref} work_package={wp['work_package_id']}")

if __name__ == "__main__":
    main()
