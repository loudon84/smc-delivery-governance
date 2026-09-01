from __future__ import annotations

import argparse
from governance_lib import (
    dump_yaml,
    github_content_metadata,
    github_resolve_ref,
    load_feature,
    repository_catalog,
)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("feature")
    ap.add_argument("--ref", required=True, help="Provider repository branch/tag/commit containing the approved Source PRD")
    ap.add_argument("--token")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    fdir, feature = load_feature(args.feature)
    source = feature.get("source_prd") or {}
    repository_id = source.get("repository_id")
    path = source.get("path")
    if not repository_id or not path:
        raise SystemExit("source_prd.repository_id/path required")
    repo = repository_catalog().get(repository_id)
    if not repo:
        raise SystemExit(f"unknown repository: {repository_id}")

    commit = github_resolve_ref(repo["name"], args.ref, token=args.token)
    meta = github_content_metadata(repo["name"], path, commit, token=args.token)
    if not meta:
        raise SystemExit(f"Source PRD missing: {repo['name']}:{path}@{commit}")

    artifact_id = source.get("artifact_id") or source.get("id") or feature["feature_id"] + "-SOURCE-PRD"
    upgraded = {
        "repository_id": repository_id,
        "path": path,
        "commit": commit,
        "blob_sha": meta["sha"],
        "sha256": meta["sha256"],
        "artifact_type": "SOURCE_PRD",
        "artifact_id": artifact_id,
        "status": source.get("status") or "APPROVED",
        "source_revision": feature["source_revision"],
    }
    feature["source_prd"] = upgraded
    for contract in feature.get("contracts", []) or []:
        contract.pop("current_state", None)

    print(f"SOURCE PRD {repo['name']}:{path}")
    print(f"commit={commit}")
    print(f"blob_sha={meta['sha']}")
    print(f"sha256={meta['sha256']}")
    if args.apply:
        dump_yaml(fdir / "feature.yaml", feature)
        print("APPLIED")

if __name__ == "__main__":
    main()
