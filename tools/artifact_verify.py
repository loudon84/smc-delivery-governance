from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

import yaml

from governance_lib import ROOT, github_commit_exists, github_file, repository_catalog, validate_jsonschema


def verify_artifact_ref(ref: dict, token: str | None = None) -> list[str]:
    errors = []
    schema_errors = validate_jsonschema(ref, ROOT / "schemas/artifact-ref.schema.json")
    errors.extend(schema_errors)
    repos = repository_catalog()
    repo = repos.get(ref.get("repository_id"))
    if not repo:
        return errors + [f"unknown repository_id {ref.get('repository_id')}"]
    commit = ref.get("commit")
    if commit and not github_commit_exists(repo["name"], commit, token=token):
        errors.append(f"commit not found: {commit}")
    path = ref.get("path")
    if path and commit:
        content = github_file(repo["name"], path, commit, token=token)
        if content is None:
            errors.append(f"path missing at commit: {path}@{commit}")
        elif ref.get("sha256"):
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            if digest != ref["sha256"]:
                errors.append("content sha256 mismatch")
    artifact_type = ref.get("artifact_type")
    status = ref.get("status")
    if artifact_type == "STAGE_PRD" and status != "APPROVED":
        errors.append("stage PRD must be APPROVED")
    if artifact_type == "PLAN" and status not in {"VALIDATED", "PASS"}:
        errors.append("plan must be VALIDATED")
    return errors


def verify_receipt_semantics(receipt: dict, token: str | None = None) -> list[str]:
    errors = []
    for key in ("stage_prds", "plans", "verification_reports"):
        for item in receipt.get("delivery", {}).get(key, []):
            if "artifact_type" in item:
                errors.extend(verify_artifact_ref(item, token=token))
            elif item.get("commit") and not re.fullmatch(r"[0-9a-fA-F]{40}", item.get("commit", "")):
                errors.append(f"{key} commit must be full SHA")
    for commit in receipt.get("delivery", {}).get("commits", []):
        if not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
            errors.append(f"commit must be full SHA: {commit}")
    return errors


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("receipt")
    ap.add_argument("--token")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    receipt = yaml.safe_load(Path(args.receipt).read_text(encoding="utf-8"))
    errors = validate_jsonschema(receipt, ROOT / "schemas/delivery-receipt.schema.json")
    if not args.offline:
        errors.extend(verify_receipt_semantics(receipt, token=args.token))
    if errors:
        print("ARTIFACT VERIFY FAIL")
        for err in errors:
            print("-", err)
        raise SystemExit(2)
    print("ARTIFACT VERIFY PASS")


if __name__ == "__main__":
    main()
