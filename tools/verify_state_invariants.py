from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from governance_lib import ROOT, contract_catalog, load_feature, load_work_packages, load_yaml

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
    if errors:
        print("STATE INVARIANTS FAIL")
        for e in errors:print("-",e)
        raise SystemExit(1)
    print("STATE INVARIANTS PASS")
    print(f"materialized_entities={len(states)} audit_chains={len(chains)}")

if __name__=="__main__":main()
