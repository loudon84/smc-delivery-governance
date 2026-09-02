from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from governance_lib import ROOT, contract_catalog, load_feature, load_work_packages, load_yaml, validate_jsonschema
from state_machine import latest_integration_run

def materialized_states():
    out={}
    for fdir in (ROOT/"features").glob("FEAT-*"):
        if not fdir.is_dir():continue
        feature=load_yaml(fdir/"feature.yaml");out[("feature",feature["feature_id"])]=feature["status"]
        for wid,wp in load_work_packages(fdir).items():out[("work_package",wid)]=wp["status"]
        rp=fdir/"roadmap.yaml"
        if rp.exists():
            for item in load_yaml(rp).get("items",[]):out[("roadmap_item",item["id"])]=item.get("status")
    for cid,c in contract_catalog().items():
        for r in c.get("releases",[]) or []:out[("contract",f"{cid}@{r['version']}")]=r["state"]
    from governance_lib import repository_catalog
    for rid,repo in repository_catalog().items():
        out[("repository",rid)]=repo.get("governance_state","REGISTERED")
    for sp in (ROOT/"integration/scenarios").glob("*.yaml"):
        d=load_yaml(sp);out[("integration",d["scenario_id"])]=d["state"]
    return out

def audit_events():
    events=[]
    for p in sorted((ROOT/"audit/transitions").rglob("events.ndjson")) if (ROOT/"audit/transitions").exists() else []:
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():events.append(json.loads(line))
    return events

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--allow-sample",action="store_true");args=ap.parse_args()
    errors=[];states=materialized_states();chains=defaultdict(list)
    for e in audit_events():chains[(e["entity_type"],e["entity_id"])].append(e)
    for key,events in chains.items():
        events.sort(key=lambda x:x["timestamp"])
        prev=None
        for e in events:
            if prev and e["from"]!=prev["to"]:
                errors.append(f"audit chain gap {key}: {prev['to']} -> {e['from']}")
            prev=e
        if key in states and prev and states[key]!=prev["to"]:
            errors.append(f"audit/materialized mismatch {key}: audit={prev['to']} state={states[key]}")
    if not args.allow_sample:
        for fdir in (ROOT/"features").glob("FEAT-*"):
            for p in list((fdir/"delivery-ledger").glob("*.yaml")) + list((fdir/"work-packages").glob("*.yaml")):
                text=p.read_text(encoding="utf-8")
                if "examples/sample-receipts" in text or "examples\\\\sample-receipts" in text:
                    errors.append(f"sample SOT contamination: {p.relative_to(ROOT)}")
    for fdir in (ROOT/"features").glob("FEAT-*"):
        feature=load_yaml(fdir/"feature.yaml")
        for c in feature.get("contracts",[]) or []:
            if "current_state" in c:errors.append(f"{feature['feature_id']}: contract current_state cache forbidden")
        scenario_id=(feature.get("integration") or {}).get("scenario_id")
        if scenario_id:
            history_path=ROOT/"integration"/"runs"/scenario_id/"history.yaml"
            if not history_path.exists():
                errors.append(f"{scenario_id}: IntegrationRun history.yaml required")
            else:
                history=load_yaml(history_path)
                errors += [f"{scenario_id} history {e}" for e in validate_jsonschema(history,ROOT/"schemas/integration-run-history.schema.json")]
                run_files=sorted(p for p in (ROOT/"integration"/"runs"/scenario_id).glob("IR-*.yaml"))
                if history.get("runs")==[] and run_files:
                    errors.append(f"{scenario_id}: empty history must not have IntegrationRun attempt files")
                if history.get("latest_run_id") and not latest_integration_run(scenario_id):
                    errors.append(f"{scenario_id}: latest_run_id does not resolve to an immutable run")
                scenario=load_yaml(ROOT/"integration"/"scenarios"/f"{feature['feature_id']}.yaml")
                if scenario.get("state")!=history.get("state") and not history.get("runs"):
                    errors.append(f"{scenario_id}: empty history state {history.get('state')} != scenario {scenario.get('state')}")
                if (history.get("runs") or [])==[] and scenario.get("state")=="PASS":
                    errors.append(f"{scenario_id}: empty history cannot claim PASS")
                blocker=history.get("blocked_by") or {}
                if not history.get("runs") and blocker.get("type")=="work_package":
                    wps=load_work_packages(fdir)
                    current=(wps.get(blocker.get("id")) or {}).get("status")
                    if current and current!=blocker.get("current_state"):
                        errors.append(f"{scenario_id}: history blocked_by.current_state {blocker.get('current_state')} != WP {current}")
                if feature.get("status")=="DONE":
                    run=latest_integration_run(scenario_id)
                    if not run or run.get("result",{}).get("status")!="PASS":
                        errors.append(f"{feature['feature_id']}: DONE requires IntegrationRun PASS")
    if errors:
        print("STATE INVARIANTS FAIL")
        for e in errors:print("-",e)
        raise SystemExit(1)
    print("STATE INVARIANTS PASS")
    print(f"materialized_entities={len(states)} audit_chains={len(chains)}")

if __name__=="__main__":main()
