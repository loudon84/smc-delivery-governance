from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from governance_lib import (
    ROOT,
    find_work_package,
    github_actions_jobs,
    github_actions_run,
    github_commit_exists,
    github_content_metadata,
    validate_jsonschema,
)
import yaml

# @lat: [[ADR-006-prd-acceptance#ADR-006 — PRD Acceptance Contract]]
def verify_attestation(att: dict, manifest_bytes: bytes, report_bytes: bytes, report: dict, token=None) -> list[str]:
    errors = validate_jsonschema(att, ROOT / "schemas/acceptance-attestation.schema.json")
    if errors:
        return [f"attestation {e}" for e in errors]
    if att["commit"] != report["repository_commit"]:
        errors.append("attestation/report commit mismatch")
    if hashlib.sha256(report_bytes).hexdigest() != att["report_sha256"]:
        errors.append("report sha256 mismatch")
    if hashlib.sha256(manifest_bytes).hexdigest() != att["manifest_sha256"]:
        errors.append("manifest sha256 mismatch")

    try:
        run = github_actions_run(att["repository"], att["run_id"], token=token)
    except RuntimeError as exc:
        return errors + [f"workflow run lookup failed: {exc}"]
    if run.get("head_sha") != report["repository_commit"]:
        errors.append("workflow head_sha mismatch")
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        errors.append(f"workflow not successful: status={run.get('status')} conclusion={run.get('conclusion')}")
    workflow_path = (run.get("path") or "").split("@",1)[0]
    if workflow_path and att.get("workflow") and att["workflow"] not in {run.get("name"), workflow_path}:
        # GITHUB_WORKFLOW is normally workflow name, so accept name or path only.
        errors.append(f"workflow identity mismatch attested={att['workflow']} actual={run.get('name')}/{workflow_path}")
    workflow_sha=att.get("workflow_sha")
    if not workflow_sha or not github_commit_exists(att["repository"],workflow_sha,token=token):
        errors.append("workflow_sha does not resolve to a Git commit")
    elif workflow_path and not github_content_metadata(att["repository"],workflow_path,workflow_sha,token=token):
        errors.append("workflow file missing at workflow_sha")
    jobs = github_actions_jobs(att["repository"], att["run_id"], token=token)
    if att.get("job_id"):
        job = next((j for j in jobs if str(j.get("id")) == str(att["job_id"]) or j.get("name") == att["job_id"]), None)
        if job and job.get("conclusion") != "success":
            errors.append("attested job did not succeed")
    return errors

def validate_acceptance(manifest: dict, report: dict) -> list[str]:
    errors = []
    if manifest.get("feature_id") != report.get("feature_id"):
        errors.append("feature_id mismatch")
    if manifest.get("work_package_id") != report.get("work_package_id"):
        errors.append("work_package_id mismatch")
    if manifest.get("prd", {}).get("source_revision") != report.get("source_revision"):
        errors.append("source_revision mismatch")

    vids = {v["id"] for v in manifest.get("verifications", [])}
    mapped = set()
    for req in manifest.get("requirements", []):
        mapped.update(req.get("verification_ids", []))
    if vids - mapped:
        errors.append(f"unmapped verifications: {sorted(vids-mapped)}")
    if mapped - vids:
        errors.append(f"unknown verification ids: {sorted(mapped-vids)}")
    result = {r["verification_id"]: r for r in report.get("results", [])}
    for v in manifest.get("verifications", []):
        if v.get("blocking", True) and result.get(v["id"], {}).get("status") != "PASS":
            errors.append(f"blocking verification not PASS: {v['id']}")
    if report.get("status") != "PASS":
        errors.append(f"report status is {report.get('status')}")
    return errors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--attestation")
    ap.add_argument("--work-package")
    ap.add_argument("--token")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    report_path = Path(args.report)
    manifest_bytes = manifest_path.read_bytes()
    report_bytes = report_path.read_bytes()
    manifest = yaml.safe_load(manifest_bytes.decode("utf-8"))
    report = json.loads(report_bytes.decode("utf-8"))

    errors = []
    errors += [f"manifest {e}" for e in validate_jsonschema(manifest, ROOT / "schemas/acceptance-manifest.schema.json")]
    errors += [f"report {e}" for e in validate_jsonschema(report, ROOT / "schemas/acceptance-report.schema.json")]
    errors += validate_acceptance(manifest, report)

    if args.work_package:
        _, wp = find_work_package(args.work_package)
        if not wp:
            errors.append("central work package not found")
        elif wp.get("source_revision") != report.get("source_revision"):
            errors.append("central work package source_revision mismatch")

    if not args.offline:
        if not args.attestation:
            errors.append("trusted acceptance requires --attestation")
        else:
            att = json.loads(Path(args.attestation).read_text(encoding="utf-8"))
            errors += verify_attestation(att, manifest_bytes, report_bytes, report, token=args.token)

    if errors:
        print("ACCEPTANCE GATE FAIL")
        for e in errors:
            print("-", e)
        raise SystemExit(2)
    print("ACCEPTANCE GATE PASS")
    print(f"requirements={len(manifest.get('requirements', []))} commit={report['repository_commit']}")

if __name__ == "__main__":
    main()
