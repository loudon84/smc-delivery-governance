from __future__ import annotations
import argparse
from pathlib import Path
from governance_lib import ROOT, load_feature, load_work_packages, load_yaml, dump_yaml, contract_catalog, find_work_package
from state_machine import allowed, work_package_gate, feature_gate, contract_gate


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--entity',choices=['feature','work_package','contract','integration'],required=True)
    ap.add_argument('--id',required=True); ap.add_argument('--to',required=True); ap.add_argument('--apply',action='store_true')
    args=ap.parse_args(); errors=[]
    if args.entity=='feature':
        fdir,doc=load_feature(args.id); current=doc['status']; kind='feature'; errors+=feature_gate(fdir,doc,args.to); path=fdir/'feature.yaml'
    elif args.entity=='work_package':
        path,doc=find_work_package(args.id)
        if not doc: raise SystemExit('work package not found')
        fdir=path.parents[1]; current=doc['status']; kind='work_package'; errors+=work_package_gate(fdir,doc,args.to)
    elif args.entity=='contract':
        catalog=contract_catalog(); doc=catalog.get(args.id)
        if not doc: raise SystemExit('contract not found')
        path=ROOT/doc['_path']; current=doc['current_release']['state']; kind='contract'; errors+=contract_gate(doc,args.to)
    else:
        found=None
        for p in (ROOT/'integration/scenarios').glob('*.yaml'):
            d=load_yaml(p)
            if d.get('scenario_id')==args.id: found=(p,d); break
        if not found: raise SystemExit('integration not found')
        path,doc=found; current=doc['state']; kind='integration'
    if not allowed(kind,current,args.to): errors.append(f'illegal transition {current} -> {args.to}')
    if errors:
        print('TRANSITION BLOCKED')
        for e in errors: print('-',e)
        raise SystemExit(2)
    print(f'TRANSITION OK {args.entity}:{args.id} {current} -> {args.to}')
    if not args.apply: return
    clean={k:v for k,v in doc.items() if k!='_path'}
    if args.entity=='contract': clean['current_release']['state']=args.to
    else: clean['status' if args.entity!='integration' else 'state']=args.to
    dump_yaml(path,clean); print('APPLIED')

if __name__=='__main__': main()
