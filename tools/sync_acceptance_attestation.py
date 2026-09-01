from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import time
from pathlib import Path

import yaml

from acceptance_gate import validate_acceptance, verify_attestation
from governance_lib import (
    ROOT,
    dump_yaml,
    github_actions_artifact,
    github_actions_run,
    github_download_artifact_zip,
    load_feature,
    read_zip_text_files,
    repository_catalog,
    validate_jsonschema,
)

def wait_for_run(repo: str, run_id: str, token=None, timeout=120):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        run = github_actions_run(repo, run_id, token=token)
        if run.get("status") == "completed":
            return run
        time.sleep(3)
    raise RuntimeError("source workflow did not complete before attestation timeout")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repository-id", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--artifact-name", required=True)
    ap.add_argument("--token")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    repo = repository_catalog().get(args.repository_id)
    if not repo:
        raise SystemExit("unknown repository")
    wait_for_run(repo["name"], args.run_id, token=args.token)
    artifact = github_actions_artifact(repo["name"], args.run_id, args.artifact_name, token=args.token)
    blob = github_download_artifact_zip(repo["name"], artifact["id"], token=args.token)
    digest=artifact.get("digest")
    if digest and digest.startswith("sha256:"):
        actual="sha256:"+hashlib.sha256(blob).hexdigest()
        if actual!=digest:
            raise SystemExit(f"GitHub artifact digest mismatch expected={digest} actual={actual}")
    files = read_zip_text_files(blob)

    manifests = {n:b for n,b in files.items() if n.endswith(".yaml") and "/manifest" not in n}
    reports = {n:b for n,b in files.items() if n.endswith(".report.json")}
    attestations = {n:b for n,b in files.items() if n.endswith(".attestation.json")}
    if not reports or not attestations:
        raise SystemExit("acceptance artifact missing report/attestation")

    accepted = 0
    for report_name, report_bytes in reports.items():
        report = json.loads(report_bytes.decode("utf-8"))
        wp_id = report["work_package_id"]
        feature_id = report["feature_id"]

        manifest_candidates = []
        for name, data in files.items():
            if not name.endswith(".yaml"):
                continue
            try:
                doc = yaml.safe_load(data.decode("utf-8"))
            except Exception:
                continue
            if isinstance(doc, dict) and doc.get("work_package_id") == wp_id and "verifications" in doc:
                manifest_candidates.append((name, data, doc))
        att_candidates = []
        for name, data in attestations.items():
            doc = json.loads(data.decode("utf-8"))
            if doc.get("report_sha256") and doc.get("repository_id") == args.repository_id:
                att_candidates.append((name, data, doc))
        if len(manifest_candidates) != 1 or len(att_candidates) != 1:
            raise SystemExit(f"{wp_id}: expected one manifest and one attestation")
        _, manifest_bytes, manifest = manifest_candidates[0]
        _, att_bytes, att = att_candidates[0]

        errors = []
        errors += [f"manifest {e}" for e in validate_jsonschema(manifest, ROOT / "schemas/acceptance-manifest.schema.json")]
        errors += [f"report {e}" for e in validate_jsonschema(report, ROOT / "schemas/acceptance-report.schema.json")]
        errors += validate_acceptance(manifest, report)
        errors += verify_attestation(att, manifest_bytes, report_bytes, report, token=args.token)
        if errors:
            print(f"{wp_id}: ACCEPTANCE ATTESTATION FAIL")
            for e in errors:
                print("-", e)
            raise SystemExit(2)

        evidence = {
            "feature_id": feature_id,
            "work_package_id": wp_id,
            "repository_id": args.repository_id,
            "repository_commit": report["repository_commit"],
            "source_revision": report["source_revision"],
            "status": "PASS",
            "workflow_run_id": args.run_id,
            "artifact_id": artifact["id"],
            "artifact_name": args.artifact_name,
            "attestation": att,
            "verified_by": "central-acceptance-gate",
        }
        print(f"{wp_id}: TRUSTED ACCEPTANCE PASS commit={report['repository_commit']}")
        accepted += 1
        if args.apply:
            fdir, _ = load_feature(feature_id)
            out = fdir / "evidence" / "acceptance" / wp_id / f"{args.run_id}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
            latest = out.parent / "latest.json"
            latest.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
            ledger_path = fdir / "delivery-ledger" / f"{args.repository_id}.yaml"
            if ledger_path.exists():
                ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
                ledger["acceptance_verified"] = {
                    "status":"PASS",
                    "run_id":args.run_id,
                    "repository_commit":report["repository_commit"],
                    "evidence":str(out.relative_to(ROOT)).replace("\\","/"),
                }
                dump_yaml(ledger_path, ledger)
    if accepted == 0:
        raise SystemExit("no acceptance reports verified")

if __name__ == "__main__":
    main()
