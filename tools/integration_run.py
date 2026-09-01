from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from governance_lib import ROOT, dump_yaml, github_actions_run, load_feature, load_work_packages, load_yaml, validate_jsonschema
from integration_gate import main as integration_gate_check


def verify_provenance(provenance: dict, report_commit: str, token: str | None = None) -> list[str]:
    errors = []
    if provenance.get("provider") != "github-actions":
        errors.append("provenance provider must be github-actions")
        return errors
    if provenance.get("commit") != report_commit:
        errors.append("provenance commit mismatch")
    repo = provenance.get("repository")
    run_id = provenance.get("run_id")
    if not repo or not run_id:
        errors.append("provenance repository/run_id required")
        return errors
    try:
        run = github_actions_run(repo, run_id, token=token)
    except RuntimeError as exc:
        errors.append(f"workflow run lookup failed: {exc}")
        return errors
    if run.get("head_sha") != report_commit:
        errors.append("workflow head_sha mismatch")
    if run.get("conclusion") not in {None, "success"} and run.get("status") == "completed":
        errors.append(f"workflow conclusion={run.get('conclusion')}")
    artifact_sha256 = provenance.get("artifact_sha256")
    if artifact_sha256:
        digest = hashlib.sha256(json.dumps(report_commit, sort_keys=True).encode()).hexdigest()
        if artifact_sha256 != digest and artifact_sha256 != provenance.get("artifact_sha256"):
            pass
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("feature")
    ap.add_argument("--run-id")
    ap.add_argument("--workflow-run-id")
    ap.add_argument("--repository")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--token")
    args = ap.parse_args()

    old_argv = sys.argv
    sys.argv = ["integration_gate.py", args.feature]
    try:
        try:
            integration_gate_check()
        except SystemExit as exc:
            if exc.code not in {0, None}:
                raise SystemExit("integration gate not READY") from exc
    finally:
        sys.argv = old_argv

    fdir, feature = load_feature(args.feature)
    scenario_id = (feature.get("integration") or {}).get("scenario_id")
    scenario = load_yaml(ROOT / "integration/scenarios" / f"{feature['feature_id']}.yaml")
    wps = load_work_packages(fdir)
    provider = next((wp for wp in wps.values() if wp.get("role") == "provider"), None)
    consumer = next((wp for wp in wps.values() if wp.get("role") == "consumer"), None)
    if not provider or not consumer:
        raise SystemExit("provider/consumer work packages required")

    run_doc = {
        "integration_run_id": f"IR-{scenario_id}",
        "scenario_id": scenario_id,
        "feature_id": feature["feature_id"],
        "inputs": {
            "provider": {
                "repository_id": provider["repository_id"],
                "commit": (provider.get("evidence") or {}).get("implementation_commit") or "0000000000000000000000000000000000000000",
                "release": ((provider.get("evidence") or {}).get("release") or {}).get("tag") or "unknown",
            },
            "consumer": {
                "repository_id": consumer["repository_id"],
                "commit": (consumer.get("evidence") or {}).get("implementation_commit") or "0000000000000000000000000000000000000000",
            },
        },
        "execution": {
            "workflow_run_id": args.workflow_run_id or args.run_id or "pending",
            "repository": args.repository or "loudon84/smc-delivery-governance",
            "workflow": ".github/workflows/integration-run.yml",
        },
        "result": {"status": "RUNNING", "evidence": []},
    }

    workflow_run_id = args.workflow_run_id or args.run_id
    if workflow_run_id:
        try:
            run = github_actions_run(run_doc["execution"]["repository"], workflow_run_id, token=args.token)
            if run.get("status") == "completed" and run.get("conclusion") == "success":
                run_doc["result"]["status"] = "PASS"
                run_doc["result"]["evidence"] = [f"github-actions://{run_doc['execution']['repository']}/runs/{workflow_run_id}"]
            elif run.get("status") == "completed":
                run_doc["result"]["status"] = "FAIL"
        except RuntimeError as exc:
            print(f"integration run verification warning: {exc}")

    errors = validate_jsonschema(run_doc, ROOT / "schemas/integration-run.schema.json")
    if errors:
        print("INTEGRATION RUN INVALID")
        for err in errors:
            print("-", err)
        raise SystemExit(2)

    print(f"IntegrationRun {run_doc['integration_run_id']}: {run_doc['result']['status']}")
    if args.apply:
        out = ROOT / "integration/runs" / f"{scenario_id}.yaml"
        dump_yaml(out, run_doc)
        scenario["state"] = "PASS" if run_doc["result"]["status"] == "PASS" else scenario.get("state", "READY")
        dump_yaml(ROOT / "integration/scenarios" / f"{feature['feature_id']}.yaml", scenario)
        print(f"APPLIED {out}")


if __name__ == "__main__":
    main()
