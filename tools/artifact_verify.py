from __future__ import annotations

import argparse
import re
from pathlib import Path
import yaml

from governance_lib import (
    ROOT,
    contract_release,
    github_commit_exists,
    github_content_metadata,
    repository_catalog,
    validate_jsonschema,
)

STRONG_TYPES = {"SOURCE_PRD", "STAGE_PRD", "PLAN", "VERIFICATION"}

def verify_artifact_ref(ref: dict, token: str | None = None) -> list[str]:
    errors = validate_jsonschema(ref, ROOT / "schemas/artifact-ref.schema.json")
    if errors:
        return errors
    repos = repository_catalog()
    repo = repos.get(ref["repository_id"])
    if not repo:
        return [f"unknown repository_id {ref['repository_id']}"]

    commit = ref["commit"]
    if not github_commit_exists(repo["name"], commit, token=token):
        return [f"commit not found: {commit}"]

    meta = github_content_metadata(repo["name"], ref["path"], commit, token=token)
    if meta is None:
        return [f"path missing at commit: {ref['path']}@{commit}"]
    if meta.get("sha") != ref["blob_sha"]:
        errors.append(f"blob_sha mismatch expected={ref['blob_sha']} actual={meta.get('sha')}")
    if meta.get("sha256") != ref["sha256"]:
        errors.append(f"content sha256 mismatch expected={ref['sha256']} actual={meta.get('sha256')}")

    artifact_type = ref["artifact_type"]
    status = ref["status"]
    if artifact_type in {"SOURCE_PRD", "STAGE_PRD"} and status != "APPROVED":
        errors.append(f"{artifact_type} must be APPROVED")
    if artifact_type == "PLAN" and status not in {"VALIDATED", "PASS"}:
        errors.append("PLAN must be VALIDATED/PASS")
    return errors

def verify_receipt_semantics(receipt: dict, token: str | None = None) -> list[str]:
    errors = []
    for key in ("stage_prds", "plans", "verification_reports"):
        for item in receipt.get("delivery", {}).get(key, []):
            errors.extend(f"{key}: {e}" for e in verify_artifact_ref(item, token=token))
    repo = repository_catalog().get(receipt.get("repository_id"))
    for commit in receipt.get("delivery", {}).get("commits", []):
        if not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
            errors.append(f"commit must be full SHA: {commit}")
        elif repo and not github_commit_exists(repo["name"], commit, token=token):
            errors.append(f"implementation commit not found: {commit}")

    # Contract pins must match the canonical release identity, not only version text.
    for pin in (receipt.get("sync") or {}).get("contract_pins", []):
        rel = contract_release(pin["contract_id"], pin["version"])
        if not rel:
            errors.append(f"unknown contract release {pin['contract_id']}@{pin['version']}")
            continue
        if pin.get("tag") != rel.get("tag"):
            errors.append(f"contract tag mismatch {pin['contract_id']}@{pin['version']}")
        if pin.get("commit") != rel.get("peeled_commit"):
            errors.append(f"contract commit mismatch {pin['contract_id']}@{pin['version']}")

    # Governance Kit pin must resolve to the canonical release Bundle.
    kit = ((receipt.get("sync") or {}).get("kit") or {})
    if receipt.get("receipt_version") == "2" and kit:
        try:
            from governance_kit import fetch_release_bundle, verify_kit
            path = fetch_release_bundle(version=kit["version"], token=token)
            canonical = verify_kit(
                path,
                expected_version=kit["version"],
                expected_tag=kit["tag"],
                expected_commit=kit["commit"],
            )
            if canonical["manifest_sha256"] != kit["manifest_sha256"]:
                errors.append("governance kit manifest_sha256 mismatch")
        except Exception as exc:
            errors.append(f"governance kit canonical verification failed: {exc}")
    return errors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("receipt")
    ap.add_argument("--token")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    receipt = yaml.safe_load(Path(args.receipt).read_text(encoding="utf-8"))
    errors = validate_jsonschema(receipt, ROOT / "schemas/delivery-receipt.schema.json")
    if not args.offline and not errors:
        errors.extend(verify_receipt_semantics(receipt, token=args.token))
    if errors:
        print("ARTIFACT VERIFY FAIL")
        for err in errors:
            print("-", err)
        raise SystemExit(2)
    print("ARTIFACT VERIFY PASS")

if __name__ == "__main__":
    main()
