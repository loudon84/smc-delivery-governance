from __future__ import annotations

import argparse

from governance_lib import (
    dump_yaml,
    github_content_metadata,
    github_resolve_ref,
    load_feature,
    load_yaml,
    repository_catalog,
)

def build_source_prd_artifact(
    *,
    repository_id: str,
    path: str,
    artifact_id: str,
    status: str,
    source_revision: str,
    ref: str | None = None,
    commit: str | None = None,
    blob_sha: str | None = None,
    sha256: str | None = None,
    token: str | None = None,
) -> dict:
    if not repository_id or not path:
        raise SystemExit("source_prd.repository_id/path required")
    repo = repository_catalog().get(repository_id)
    if not repo:
        raise SystemExit(f"unknown repository: {repository_id}")

    if commit and blob_sha and sha256:
        resolved_commit = commit
        resolved_blob = blob_sha
        resolved_sha256 = sha256
    else:
        if not ref:
            raise SystemExit("Source PRD requires --ref or explicit commit/blob_sha/sha256")
        resolved_commit = github_resolve_ref(repo["name"], ref, token=token)
        meta = github_content_metadata(repo["name"], path, resolved_commit, token=token)
        if not meta:
            raise SystemExit(f"Source PRD missing: {repo['name']}:{path}@{resolved_commit}")
        resolved_blob = meta["sha"]
        resolved_sha256 = meta["sha256"]

    return {
        "repository_id": repository_id,
        "path": path,
        "commit": resolved_commit,
        "blob_sha": resolved_blob,
        "sha256": resolved_sha256,
        "artifact_type": "SOURCE_PRD",
        "artifact_id": artifact_id,
        "status": status or "APPROVED",
        "source_revision": source_revision,
    }


def apply_source_prd(fdir, feature: dict, upgraded: dict) -> None:
    feature["source_prd"] = upgraded
    for contract in feature.get("contracts", []) or []:
        contract.pop("current_state", None)
    dump_yaml(fdir / "feature.yaml", feature)
    trace_path = fdir / "traceability.yaml"
    if trace_path.exists():
        trace = load_yaml(trace_path)
        trace["source_prd"] = upgraded
        dump_yaml(trace_path, trace)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("feature")
    ap.add_argument("--ref", help="branch/tag/commit containing the approved Source PRD")
    ap.add_argument("--commit")
    ap.add_argument("--blob-sha")
    ap.add_argument("--sha256")
    ap.add_argument("--token")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    fdir, feature = load_feature(args.feature)
    source = feature.get("source_prd") or {}
    upgraded = build_source_prd_artifact(
        repository_id=source.get("repository_id"),
        path=source.get("path"),
        artifact_id=source.get("artifact_id") or source.get("id") or feature["feature_id"] + "-SOURCE-PRD",
        status=source.get("status") or "APPROVED",
        source_revision=feature["source_revision"],
        ref=args.ref,
        commit=args.commit,
        blob_sha=args.blob_sha,
        sha256=args.sha256,
        token=args.token,
    )
    print(f"SOURCE PRD {upgraded['repository_id']}:{upgraded['path']}")
    print(f"commit={upgraded['commit']}")
    print(f"blob_sha={upgraded['blob_sha']}")
    print(f"sha256={upgraded['sha256']}")
    if args.apply:
        apply_source_prd(fdir, feature, upgraded)
        print("APPLIED")

if __name__ == "__main__":
    main()
