from __future__ import annotations

import argparse
from pathlib import Path

from governance_lib import ROOT, contract_catalog, find_work_package, load_feature, load_yaml
from state_machine import allowed, contract_gate, feature_gate, roadmap_item_gate, work_package_gate
from state_transaction import commit_yaml_transition

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--entity",choices=["feature","work_package","contract","integration","roadmap_item","repository"],required=True)
    ap.add_argument("--id",required=True)
    ap.add_argument("--to",required=True)
    ap.add_argument("--version")
    ap.add_argument("--actor",default="human")
    ap.add_argument("--reason",default="manual transition")
    ap.add_argument("--evidence",action="append",default=[])
    ap.add_argument("--apply",action="store_true")
    args=ap.parse_args()
    errors=[]

    if args.entity=="feature":
        fdir,container=load_feature(args.id); current=container["status"]; kind="feature"; path=fdir/"feature.yaml"
        errors += feature_gate(fdir,container,args.to)
        new_doc=dict(container); new_doc["status"]=args.to
    elif args.entity=="work_package":
        path,container=find_work_package(args.id)
        if not container: raise SystemExit("work package not found")
        fdir=path.parents[1]; current=container["status"]; kind="work_package"
        errors += work_package_gate(fdir,container,args.to)
        new_doc={k:v for k,v in container.items() if k!="_path"}; new_doc["status"]=args.to
    elif args.entity=="contract":
        catalog=contract_catalog(); container=catalog.get(args.id)
        if not container: raise SystemExit("contract not found")
        path=ROOT/container["_path"]; version=args.version or (container.get("current_release") or {}).get("version")
        rel=next((r for r in container.get("releases",[]) if r.get("version")==version),None)
        if not rel: raise SystemExit("contract release not found")
        current=rel["state"]; kind="contract"; errors += contract_gate(container,args.to,version)
        new_doc={k:v for k,v in container.items() if k!="_path"}
        for r in new_doc.get("releases",[]):
            if r.get("version")==version: r["state"]=args.to
        if (new_doc.get("current_release") or {}).get("version")==version:
            new_doc["current_release"]["state"]=args.to
    elif args.entity=="roadmap_item":
        found=None
        for fdir in (ROOT/"features").glob("FEAT-*"):
            rp=fdir/"roadmap.yaml"
            if not rp.exists(): continue
            roadmap=load_yaml(rp)
            for item in roadmap.get("items",[]):
                if item.get("id")==args.id:
                    found=(fdir,rp,roadmap,item);break
            if found: break
        if not found: raise SystemExit("roadmap item not found")
        fdir,path,roadmap,item=found; current=item.get("status","PLANNED"); kind="roadmap_item"
        errors += roadmap_item_gate(fdir,item,args.to)
        new_doc=roadmap
        for it in new_doc.get("items",[]):
            if it.get("id")==args.id: it["status"]=args.to
    elif args.entity=="repository":
        from governance_lib import repository_catalog
        repo=repository_catalog().get(args.id)
        if not repo: raise SystemExit("repository not found")
        path=ROOT/repo["_path"];current=repo.get("governance_state","REGISTERED");kind="repository"
        new_doc={k:v for k,v in repo.items() if k!="_path"};new_doc["governance_state"]=args.to
    else:
        found=None
        for p in (ROOT/"integration/scenarios").glob("*.yaml"):
            d=load_yaml(p)
            if d.get("scenario_id")==args.id: found=(p,d);break
        if not found: raise SystemExit("integration not found")
        path,container=found; current=container["state"]; kind="integration"
        new_doc=dict(container); new_doc["state"]=args.to

    if not allowed(kind,current,args.to):
        errors.append(f"illegal transition {current} -> {args.to}")
    if errors:
        print("TRANSITION BLOCKED")
        for e in errors: print("-",e)
        raise SystemExit(2)
    print(f"TRANSITION OK {args.entity}:{args.id} {current} -> {args.to}")
    if args.apply:
        commit_yaml_transition(
            path=path,new_doc=new_doc,entity_type=args.entity,entity_id=args.id,
            from_state=current,to_state=args.to,actor=args.actor,
            source="human" if args.actor!="smc-governance-bot" else "reconciler",
            reason=args.reason,evidence=args.evidence,apply=True,
        )
        print("APPLIED")

if __name__=="__main__": main()
