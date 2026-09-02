from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from governance_lib import ROOT, dump_yaml, load_feature, load_work_packages, load_yaml, validate_jsonschema
from integration_gate import main as integration_gate_main

def _effective_commit(fdir: Path, wp: dict) -> str | None:
    evidence=(wp.get("evidence") or {})
    direct=evidence.get("implementation_commit")
    if direct and len(direct)==40:
        return direct
    ledger=fdir/"delivery-ledger"/f"{wp['repository_id']}.yaml"
    if ledger.exists():
        commits=(load_yaml(ledger).get("delivery") or {}).get("commits") or []
        return commits[-1] if commits else None
    return None

def _provider_release(wp: dict) -> str | None:
    return ((wp.get("evidence") or {}).get("release") or {}).get("tag")

def _run_id(scenario_id: str) -> str:
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"IR-{scenario_id}-{stamp}-{uuid.uuid4().hex[:8]}"

def execute_runner(command: str, env: dict[str,str], timeout: int) -> tuple[int,int,str,str]:
    started=time.monotonic()
    p=subprocess.run(command,shell=True,cwd=ROOT,env={**os.environ,**env},
                     capture_output=True,text=True,timeout=timeout)
    dur=int((time.monotonic()-started)*1000)
    return p.returncode,dur,p.stdout,p.stderr

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--feature",required=True)
    ap.add_argument("--workflow-run-id",required=True)
    ap.add_argument("--repository",default="loudon84/smc-delivery-governance")
    ap.add_argument("--workflow",default=".github/workflows/integration-run.yml")
    ap.add_argument("--apply",action="store_true")
    args=ap.parse_args()

    fdir,feature=load_feature(args.feature)
    scenario_id=(feature.get("integration") or {}).get("scenario_id")
    if not scenario_id: raise SystemExit("feature integration.scenario_id required")
    scenario_path=ROOT/"integration/scenarios"/f"{feature['feature_id']}.yaml"
    scenario=load_yaml(scenario_path)
    runner=scenario.get("runner") or {}
    command=runner.get("command")
    if not command:
        raise SystemExit("integration scenario runner.command required; no synthetic PASS is allowed")
    timeout=int(runner.get("timeout_seconds",1800))

    # Fail closed on readiness.
    import sys
    old=sys.argv
    sys.argv=["integration_gate.py",args.feature]
    try:
        try: integration_gate_main()
        except SystemExit as exc:
            if exc.code not in {0,None}: raise SystemExit("integration gate not READY") from exc
    finally:
        sys.argv=old

    wps=load_work_packages(fdir)
    provider=next((w for w in wps.values() if w.get("role")=="provider"),None)
    consumer=next((w for w in wps.values() if w.get("role")=="consumer"),None)
    if not provider or not consumer: raise SystemExit("provider and consumer work packages required")
    provider_commit=_effective_commit(fdir,provider);consumer_commit=_effective_commit(fdir,consumer)
    if not provider_commit or not consumer_commit:
        raise SystemExit("integration inputs require real provider/consumer implementation commits")

    contracts=[]
    for cref in feature.get("contracts",[]) or []:
        contracts.append({"contract_id":cref["contract_id"],"version":cref["required_version"]})

    ir=_run_id(scenario_id)
    run_doc={
      "integration_run_id":ir,
      "scenario_id":scenario_id,
      "feature_id":feature["feature_id"],
      "created_at":datetime.now(timezone.utc).isoformat(),
      "completed_at":None,
      "inputs":{
        "provider":{"repository_id":provider["repository_id"],"commit":provider_commit,"release":_provider_release(provider)},
        "consumer":{"repository_id":consumer["repository_id"],"commit":consumer_commit,"release":None},
        "contracts":contracts,
      },
      "environment":scenario.get("environment") or {},
      "execution":{"repository":args.repository,"workflow":args.workflow,"workflow_run_id":args.workflow_run_id,"runner":command},
      "result":{"status":"RUNNING","evidence":[],"exit_code":None,"stdout_sha256":None,"stderr_sha256":None},
    }
    run_dir=ROOT/"integration/runs"/scenario_id
    run_path=run_dir/f"{ir}.yaml"
    if run_path.exists(): raise SystemExit("integration run id collision")
    if args.apply:
        run_dir.mkdir(parents=True,exist_ok=True);dump_yaml(run_path,run_doc)

    env={
      "SMC_FEATURE_ID":feature["feature_id"],"SMC_INTEGRATION_RUN_ID":ir,
      "SMC_PROVIDER_COMMIT":provider_commit,"SMC_CONSUMER_COMMIT":consumer_commit,
      "SMC_PROVIDER_RELEASE":_provider_release(provider) or "",
      "SMC_CONTRACTS_JSON":json.dumps(contracts),
    }
    try:
        code,dur,out,err=execute_runner(command,env,timeout)
    except subprocess.TimeoutExpired as exc:
        code=124;dur=timeout*1000;out=exc.stdout or "";err=exc.stderr or ""

    status="PASS" if code==0 else "FAIL"
    report={
      "integration_run_id":ir,"scenario_id":scenario_id,"feature_id":feature["feature_id"],
      "status":status,"exit_code":code,"duration_ms":dur,
      "stdout_sha256":hashlib.sha256(out.encode("utf-8",errors="replace")).hexdigest(),
      "stderr_sha256":hashlib.sha256(err.encode("utf-8",errors="replace")).hexdigest(),
      "generated_at":datetime.now(timezone.utc).isoformat(),
    }
    report_path=run_dir/f"{ir}.report.json"
    run_doc["completed_at"]=report["generated_at"]
    run_doc["result"]={
      "status":status,"exit_code":code,"stdout_sha256":report["stdout_sha256"],
      "stderr_sha256":report["stderr_sha256"],
      "evidence":[str(report_path.relative_to(ROOT)).replace("\\","/"),f"github-actions://{args.repository}/runs/{args.workflow_run_id}"],
    }
    latest={"integration_run_id":ir,"path":str(run_path.relative_to(ROOT)).replace("\\","/"),"status":status}
    errors=[]
    errors += [f"run {e}" for e in validate_jsonschema(run_doc,ROOT/"schemas/integration-run.schema.json")]
    errors += [f"report {e}" for e in validate_jsonschema(report,ROOT/"schemas/integration-report.schema.json")]
    history_path=run_dir/"history.yaml"
    history=load_yaml(history_path) if history_path.exists() else {
        "history_version":"1","scenario_id":scenario_id,"feature_id":feature["feature_id"],
        "state":status,"latest_run_id":None,"runs":[],
    }
    history["runs"]=list(history.get("runs") or [])
    history["runs"].append({"integration_run_id":ir,"path":latest["path"],"status":status})
    history["latest_run_id"]=ir
    history["state"]=status
    history["updated_at"]=report["generated_at"]
    history.pop("blocked_by",None)
    history.pop("notes",None)
    errors += [f"history {e}" for e in validate_jsonschema(history,ROOT/"schemas/integration-run-history.schema.json")]
    if errors:
        for e in errors: print("INTEGRATION EVIDENCE INVALID:",e)
        raise SystemExit(2)
    if args.apply:
        report_path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8",newline="\n")
        dump_yaml(run_path,run_doc)
        dump_yaml(run_dir/"latest.yaml",latest)
        dump_yaml(history_path,history)
    print(f"IntegrationRun {ir}: {status}")
    print(f"runner={command}")
    raise SystemExit(0 if status=="PASS" else 2)

if __name__=="__main__": main()
