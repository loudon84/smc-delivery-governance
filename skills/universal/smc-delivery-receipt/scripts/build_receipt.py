from __future__ import annotations
import argparse, subprocess
from datetime import datetime, timezone
from pathlib import Path
import yaml


def run(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else ""


def file_ref(repo: Path, item_id: str, path_value: str | None, status: str) -> dict | None:
    if not path_value:
        return None
    path = repo / path_value
    if not path.exists():
        return None
    commit = run(repo, "log", "-1", "--format=%H", "--", path_value) or None
    return {"id": item_id, "path": path_value.replace("\\", "/"), "status": status, "commit": commit, "source_revision": None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--work-package", required=True, help="synced work package yaml")
    ap.add_argument("--status", required=True)
    ap.add_argument("--acceptance-report")
    ap.add_argument("--output")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    wp_path = Path(args.work_package)
    wp = yaml.safe_load(wp_path.read_text(encoding="utf-8"))
    head = run(repo, "rev-parse", "HEAD")
    delivery = wp.get("local_delivery") or {}

    prds=[]
    if delivery.get("prd"):
        ref=file_ref(repo, f"PRD-{wp['work_package_id']}", delivery.get("prd"), "APPROVED")
        if ref: prds.append(ref)
    plans=[]
    if delivery.get("plan"):
        ref=file_ref(repo, f"PLAN-{wp['work_package_id']}", delivery.get("plan"), "VALIDATED")
        if ref: plans.append(ref)

    # Commit trailers are the authoritative automatic link for implementation commits.
    log = run(repo, "log", "--format=%H%x00%B%x00", "-n", "500")
    commits=[]
    chunks=log.split("\x00")
    for i in range(0, len(chunks)-1, 2):
        sha, body = chunks[i].strip(), chunks[i+1]
        if f"SMC-Work-Package: {wp['work_package_id']}" in body:
            commits.append(sha)

    acceptance = {"manifest": None, "report": None, "status": "NOT_DEFINED"}
    if args.acceptance_report:
        ar=Path(args.acceptance_report)
        if ar.exists():
            import json
            report=json.loads(ar.read_text(encoding="utf-8"))
            acceptance={"manifest": None, "report": str(ar).replace("\\", "/"), "status": report.get("status", "PARTIAL")}

    receipt={
      "receipt_version":"1",
      "feature_id":wp["feature_id"],
      "work_package_id":wp["work_package_id"],
      "repository_id":wp["repository_id"],
      "source_revision":wp["source_revision"],
      "status":args.status,
      "sync":{
        "governance_kit_version":"1.1.0",
        "central_commit":None,
        "contract_pins":[{"contract_id":x["contract_id"],"version":x.get("version") or x.get("required_version", ""),"tag":None,"commit":None} for x in wp.get("contract_inputs", [])]
      },
      "delivery":{
        "stage_prds":prds,
        "issues":[],
        "bugs":[],
        "plans":plans,
        "pull_requests":[],
        "commits":commits or ([head] if args.status in {"REVIEW","VERIFIED","DONE"} and head else []),
        "verification_reports":[]
      },
      "acceptance":acceptance,
      "evidence":{},
      "reported_at":datetime.now(timezone.utc).isoformat()
    }
    output=Path(args.output) if args.output else repo / ".agents/governance/receipts" / f"{wp['work_package_id']}.yaml"
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(yaml.safe_dump(receipt,sort_keys=False,allow_unicode=True),encoding="utf-8",newline="\n")
    print(output)

if __name__ == "__main__": main()
