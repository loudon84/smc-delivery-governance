from __future__ import annotations

import argparse
from pathlib import Path

from governance_lib import (
    EXIT_EXPECTED_NON_READY, EXIT_OK, EXIT_SYSTEM_ERROR, ROOT,
    CONTRACT_ORDER, WP_ORDER, contract_catalog, dump_yaml, github_actions_run,
    load_feature, load_work_packages, load_yaml, resolve_contract, state_at_least,
)
from state_machine import allowed, contract_gate, feature_gate, latest_integration_run, roadmap_item_gate, work_package_gate
from state_transaction import commit_yaml_transition

WP_SEQUENCE=["BACKLOG","READY","IN_PRD","PLANNED","IMPLEMENTING","REVIEW","VERIFIED","DONE"]
FEATURE_SEQUENCE=["PROPOSED","ARCHITECTURE","PLANNED","IMPLEMENTING","INTEGRATING","VERIFYING","DONE"]

def tx(path,new_doc,kind,eid,current,nxt,reason,evidence,apply,actor="smc-governance-bot"):
    if apply:
        commit_yaml_transition(path=path,new_doc=new_doc,entity_type=kind,entity_id=eid,
            from_state=current,to_state=nxt,actor=actor,source="reconciler",reason=reason,evidence=evidence,apply=True)

def promote_wp(fdir,path,wp,observed_target,apply,actor):
    if wp.get("status") in {"BLOCKED","SUPERSEDED"} or observed_target not in WP_SEQUENCE:return wp["status"],False
    current=wp["status"];target_idx=WP_SEQUENCE.index(observed_target);blocked=False
    while current in WP_SEQUENCE and WP_SEQUENCE.index(current)<target_idx:
        nxt=WP_SEQUENCE[WP_SEQUENCE.index(current)+1]
        if not allowed("work_package",current,nxt):break
        probe={**wp,"status":current};errs=work_package_gate(fdir,probe,nxt)
        if errs:
            print(f"{wp['work_package_id']}: stop {current}->{nxt}: {errs[0]}");blocked=True;break
        new={**wp,"status":nxt}
        print(f"{wp['work_package_id']}: {current}->{nxt}")
        tx(path,new,"work_package",wp["work_package_id"],current,nxt,f"observed receipt status {observed_target}",
           [f"delivery-ledger/{wp['repository_id']}.yaml"],apply,actor)
        current=nxt;wp=new
        if not apply: continue
    return current,blocked

def contract_consumer_pin_ok(fdir,wp,contract_id,version,release):
    ledger=fdir/"delivery-ledger"/f"{wp['repository_id']}.yaml"
    if not ledger.exists():return False
    obs=load_yaml(ledger)
    if obs.get("sync_state")!="SYNCED":return False
    # contract pins are not copied into ledger delivery; read remote observed evidence if present in WP receipt not available.
    # Use central registry consumer pin plus synchronized state as the immutable consumer lock authority.
    c=contract_catalog()[contract_id]
    pin=(c.get("consumers") or {}).get(wp["repository_id"],{}).get("pinned_version")
    return pin==version and bool(release.get("tag") and release.get("peeled_commit"))

def reconcile_contracts(fdir,feature,apply,actor):
    blocked=False;wps=load_work_packages(fdir);catalog=contract_catalog()
    for cref in feature.get("contracts",[]) or []:
        cid=cref["contract_id"];version=cref["required_version"];c0=catalog.get(cid)
        if not c0: print(f"{cid}: missing registry");blocked=True;continue
        path=ROOT/c0["_path"];doc={k:v for k,v in c0.items() if k!="_path"}
        rel=next((r for r in doc.get("releases",[]) if r.get("version")==version),None)
        if not rel: print(f"{cid}@{version}: release missing");blocked=True;continue
        current=rel["state"]
        provider_wps=[w for w in wps.values() if any(o.get("contract_id")==cid and o.get("version")==version for o in w.get("contract_outputs",[]))]
        consumer_wps=[w for w in wps.values() if any(i.get("contract_id")==cid and (i.get("version") or i.get("required_version"))==version for i in w.get("contract_inputs",[]))]
        desired=current
        if current=="APPROVED" and provider_wps and all(w.get("status") in {"VERIFIED","DONE"} for w in provider_wps):
            if rel.get("tag") and rel.get("peeled_commit"): desired="RELEASED"
        if current=="RELEASED" and consumer_wps and all(contract_consumer_pin_ok(fdir,w,cid,version,rel) for w in consumer_wps):
            desired="CONSUMED"
        if current=="CONSUMED" and provider_wps and consumer_wps and all(w.get("status") in {"VERIFIED","DONE"} for w in provider_wps+consumer_wps):
            desired="CONFORMANCE_PASS"
        if desired!=current:
            if not allowed("contract",current,desired):
                print(f"{cid}@{version}: cannot auto transition {current}->{desired}");blocked=True;continue
            errs=contract_gate(doc,desired,version)
            if errs: print(f"{cid}@{version}: {errs[0]}");blocked=True;continue
            new=doc
            for r in new.get("releases",[]):
                if r.get("version")==version:r["state"]=desired
            if (new.get("current_release") or {}).get("version")==version:new["current_release"]["state"]=desired
            print(f"{cid}@{version}: {current}->{desired}")
            tx(path,new,"contract",f"{cid}@{version}",current,desired,"derived from provider release/consumer pin/conformance evidence",[],apply,actor)
    return blocked

def derive_roadmap_status(item,fdir):
    wps=load_work_packages(fdir);met=True
    for exit_req in item.get("exit",[]):
        if exit_req.startswith("contract:"):
            _,rest=exit_req.split(":",1);cid,minm=rest.split(">=",1)
            if not state_at_least(resolve_contract(cid),minm,CONTRACT_ORDER):met=False
        elif exit_req.startswith("work_package:"):
            _,rest=exit_req.split(":",1);wid,minm=rest.split(">=",1)
            if not state_at_least((wps.get(wid) or {}).get("status"),minm,WP_ORDER):met=False
        elif exit_req.startswith("integration:"):
            _,rest=exit_req.split(":",1);sid,required=rest.split("=",1)
            run=latest_integration_run(sid)
            if (run.get("result",{}).get("status") if run else "OPEN")!=required:met=False
    if met:return "DONE"
    if item.get("blocked_by"):return "BLOCKED"
    return "ACTIVE" if item.get("status")!="PLANNED" or item.get("work_packages") else "PLANNED"

def reconcile_roadmap(fdir,apply,actor):
    rp=fdir/"roadmap.yaml"
    if not rp.exists():return False
    roadmap=load_yaml(rp);blocked=False
    for item in roadmap.get("items",[]):
        current=item.get("status","PLANNED");desired=derive_roadmap_status(item,fdir)
        if desired==current:continue
        if not allowed("roadmap_item",current,desired):
            # PLANNED -> DONE is promoted through ACTIVE.
            if current=="PLANNED" and desired=="DONE":
                desired="ACTIVE"
            else:
                blocked=True;continue
        if desired=="DONE":
            errs=roadmap_item_gate(fdir,item,"DONE")
            if errs:blocked=True;continue
        new=load_yaml(rp)
        for x in new.get("items",[]):
            if x.get("id")==item["id"]:x["status"]=desired
        print(f"{item['id']}: {current}->{desired}")
        tx(rp,new,"roadmap_item",item["id"],current,desired,"derived from contract/work-package/integration exits",[],apply,actor)
        if apply:roadmap=new
    return blocked

def reconcile_running_integration_attempts(feature,apply):
    scenario_id=(feature.get("integration") or {}).get("scenario_id")
    if not scenario_id:return False
    run_dir=ROOT/"integration/runs"/scenario_id
    if not run_dir.exists():return False
    changed=False
    for path in sorted(run_dir.glob("IR-*.yaml")):
        run=load_yaml(path)
        if run.get("result",{}).get("status")!="RUNNING":continue
        execution=run.get("execution") or {}
        repo=execution.get("repository");run_id=execution.get("workflow_run_id")
        if not repo or not run_id:continue
        try:
            wf=github_actions_run(repo,run_id)
        except Exception as exc:
            print(f"{run.get('integration_run_id')}: workflow lookup warning: {exc}")
            continue
        if wf.get("status")!="completed":continue
        # Never synthesize PASS from workflow success. A completed RUNNING attempt means
        # the reviewed runner did not persist terminal evidence, so fail closed.
        run["completed_at"]=wf.get("updated_at") or wf.get("run_started_at")
        run["result"]["status"]="FAIL"
        run["result"]["evidence"]=(run["result"].get("evidence") or [])+[f"github-actions://{repo}/runs/{run_id}","reason://missing-terminal-runner-evidence"]
        if apply:dump_yaml(path,run)
        print(f"{run.get('integration_run_id')}: RUNNING->FAIL (workflow completed without terminal runner evidence)")
        changed=True
    return changed

def integration_gate_state(fdir,feature):
    wps=load_work_packages(fdir);provider=False;consumer=False;contract=False
    scenario=load_yaml(ROOT/"integration/scenarios"/f"{feature['feature_id']}.yaml")
    for req in scenario.get("requires",{}).get("work_packages",[]):
        wp=wps.get(req["work_package_id"]);cur=(wp or {}).get("status")
        if not state_at_least(cur,req["minimum_state"],WP_ORDER):
            if (wp or {}).get("role")=="provider":provider=True
            elif (wp or {}).get("role")=="consumer":consumer=True
    for req in scenario.get("requires",{}).get("contracts",[]):
        consumers=[w["repository_id"] for w in wps.values() if w.get("role")=="consumer"]
        cur=resolve_contract(req["contract_id"],req.get("required_version"),consumers[0] if consumers else None)
        if not state_at_least(cur,req["minimum_state"],CONTRACT_ORDER):contract=True
    if provider:return "WAITING_PROVIDER"
    if consumer:return "WAITING_CONSUMER"
    if contract:return "BLOCKED"
    run=latest_integration_run(scenario["scenario_id"])
    if run:
        st=run.get("result",{}).get("status")
        if st in {"PASS","FAIL"}:return st
        if st=="RUNNING":return "RUNNING"
    return "READY"

def _transition_path(kind,current,target):
    graph=load_yaml(ROOT/"contracts/lifecycle/states.yaml")[kind]["transitions"]
    queue=[(current,[])]
    seen={current}
    while queue:
        state,path=queue.pop(0)
        if state==target:return path
        for nxt in graph.get(state,[]):
            if nxt not in seen:
                seen.add(nxt);queue.append((nxt,path+[nxt]))
    return None

def reconcile_integration(fdir,feature,apply,actor):
    sp=ROOT/"integration/scenarios"/f"{feature['feature_id']}.yaml"
    if not sp.exists():return False
    scenario=load_yaml(sp);current=scenario["state"];desired=integration_gate_state(fdir,feature)
    if desired==current:return False
    path=_transition_path("integration",current,desired)
    if path is None:
        print(f"{scenario['scenario_id']}: no legal reconcile path {current}->{desired}")
        return True
    for nxt in path:
        new=dict(scenario);new["state"]=nxt
        print(f"{scenario['scenario_id']}: {current}->{nxt}")
        tx(sp,new,"integration",scenario["scenario_id"],current,nxt,
           "derived from readiness/latest immutable IntegrationRun",[],apply,actor)
        current=nxt;scenario=new
    return False

def main():
    ap=argparse.ArgumentParser();ap.add_argument("feature");ap.add_argument("--apply",action="store_true");ap.add_argument("--actor",default="smc-governance-bot");args=ap.parse_args()
    try:
        fdir,feature=load_feature(args.feature);blocked=False
        for wid,wp0 in load_work_packages(fdir).items():
            path=fdir/"work-packages"/Path(wp0["_path"]).name;wp={k:v for k,v in wp0.items() if k!="_path"}
            ledger=fdir/"delivery-ledger"/f"{wp['repository_id']}.yaml"
            if not ledger.exists():continue
            obs=load_yaml(ledger);_,b=promote_wp(fdir,path,wp,obs.get("status"),args.apply,args.actor);blocked|=b

        fdir,feature=load_feature(args.feature)
        blocked |= reconcile_contracts(fdir,feature,args.apply,args.actor)
        blocked |= reconcile_roadmap(fdir,args.apply,args.actor)
        fdir,feature=load_feature(args.feature)
        reconcile_running_integration_attempts(feature,args.apply)
        blocked |= reconcile_integration(fdir,feature,args.apply,args.actor)

        fdir,feature=load_feature(args.feature);wps=load_work_packages(fdir)
        current=feature["status"];desired=None
        if all(w.get("status") in {"VERIFIED","DONE"} for w in wps.values()):desired="INTEGRATING"
        scenario_id=(feature.get("integration") or {}).get("scenario_id")
        run=latest_integration_run(scenario_id) if scenario_id else None
        if run and run.get("result",{}).get("status")=="PASS" and all(w.get("status") in {"VERIFIED","DONE"} for w in wps.values()):desired="DONE"
        if desired and current in FEATURE_SEQUENCE:
            while FEATURE_SEQUENCE.index(current)<FEATURE_SEQUENCE.index(desired):
                nxt=FEATURE_SEQUENCE[FEATURE_SEQUENCE.index(current)+1]
                if not allowed("feature",current,nxt):break
                errs=feature_gate(fdir,{**feature,"status":current},nxt)
                if errs:print(f"Feature stop {current}->{nxt}: {errs[0]}");blocked=True;break
                new={**feature,"status":nxt};print(f"Feature {current}->{nxt}")
                tx(fdir/"feature.yaml",new,"feature",feature["feature_id"],current,nxt,f"reconciled toward {desired}",[],args.apply,args.actor)
                current=nxt;feature=new
        raise SystemExit(EXIT_EXPECTED_NON_READY if blocked else EXIT_OK)
    except SystemExit:raise
    except Exception as exc:
        print(f"RECONCILER SYSTEM_ERROR: {exc}");raise SystemExit(EXIT_SYSTEM_ERROR) from exc

if __name__=="__main__":main()
