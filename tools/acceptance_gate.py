from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from governance_lib import ROOT, find_work_package, github_actions_run, load_yaml, validate_jsonschema


def verify_provenance(provenance: dict, report_commit: str, token: str | None = None) -> list[str]:
    errors = []
    if provenance.get("provider") != "github-actions":
        return ["provenance provider must be github-actions"]
    if provenance.get("commit") != report_commit:
        errors.append("provenance commit mismatch")
    repo = provenance.get("repository")
    run_id = provenance.get("run_id")
    if not repo or not run_id:
        return errors + ["provenance repository/run_id required"]
    try:
        run = github_actions_run(repo, run_id, token=token)
    except RuntimeError as exc:
        return errors + [f"workflow run lookup failed: {exc}"]
    if run.get("head_sha") != report_commit:
        errors.append("workflow head_sha mismatch")
    if run.get("status") == "completed" and run.get("conclusion") != "success":
        errors.append(f"workflow conclusion={run.get('conclusion')}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--work-package")
    ap.add_argument("--token")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()
    manifest = load_yaml(Path(args.manifest))
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    errors = []
    errors += [f"manifest {e}" for e in validate_jsonschema(manifest, ROOT / "schemas/acceptance-manifest.schema.json")]
    errors += [f"report {e}" for e in validate_jsonschema(report, ROOT / "schemas/acceptance-report.schema.json")]
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
    missing = vids - mapped
    unknown = mapped - vids
    if missing:
        errors.append(f"unmapped verifications: {sorted(missing)}")
    if unknown:
        errors.append(f"unknown verification ids: {sorted(unknown)}")
    result = {r["verification_id"]: r for r in report.get("results", [])}
    for v in manifest.get("verifications", []):
        if v.get("blocking", True) and result.get(v["id"], {}).get("status") != "PASS":
            errors.append(f"blocking verification not PASS: {v['id']}")
    if report.get("status") != "PASS":
        errors.append(f"report status is {report.get('status')}")

    provenance = report.get("provenance")
    if provenance and not args.offline:
        errors.extend(verify_provenance(provenance, report.get("repository_commit", ""), token=args.token))
    elif report.get("report_version") == "2" and not provenance:
        errors.append("report v2 requires provenance")

    if args.work_package:
        _, wp = find_work_package(args.work_package)
        if not wp:
            errors.append("central work package not found")
        elif wp.get("source_revision") != report.get("source_revision"):
            errors.append("central work package source_revision mismatch")

    if errors:
        print("ACCEPTANCE GATE FAIL")
        for e in errors:
            print("-", e)
        raise SystemExit(2)
    print("ACCEPTANCE GATE PASS")
    print(f"requirements={len(manifest['requirements'])} verifications={len(vids)} commit={report['repository_commit']}")


if __name__ == "__main__":
    main()
