from __future__ import annotations
import sys
from governance_lib import (
    ROOT, load_feature, load_work_packages, validate_jsonschema, repository_catalog,
    contract_catalog, load_yaml
)


def main():
    if len(sys.argv)!=2: raise SystemExit('usage: validate_feature.py <feature-dir-or-id>')
    fdir,feature=load_feature(sys.argv[1]); errors=[]
    errors += [f"feature.yaml {e}" for e in validate_jsonschema(feature, ROOT/'schemas/feature.schema.json')]

    repos=repository_catalog(); contracts=contract_catalog()
    participants={p['repository_id'] for p in feature.get('participants',[])}
    for rid in participants:
        if rid not in repos: errors.append(f'unregistered participant repository: {rid}')

    change_ids=[c['id'] for c in feature.get('global_changes',[])]
    if len(change_ids)!=len(set(change_ids)): errors.append('duplicate global_change id')

    for c in feature.get('contracts',[]) or []:
        cid=c['contract_id']
        if cid not in contracts: errors.append(f'unregistered contract: {cid}')
        if c['provider_repository'] not in participants: errors.append(f"contract provider not participant: {c['provider_repository']}")
        for rid in c.get('consumer_repositories',[]):
            if rid not in participants: errors.append(f'contract consumer not participant: {rid}')

    wps=load_work_packages(fdir); declared=set(feature.get('work_packages',[])); actual=set(wps)
    if declared!=actual: errors.append(f'work package set mismatch declared={sorted(declared)} actual={sorted(actual)}')
    for wid,wp in wps.items():
        data={k:v for k,v in wp.items() if k!='_path'}
        errors += [f"{wp['_path']} {e}" for e in validate_jsonschema(data, ROOT/'schemas/work-package.schema.json')]
        if wp['feature_id']!=feature['feature_id']: errors.append(f'{wid}: feature_id mismatch')
        if wp['repository_id'] not in participants: errors.append(f'{wid}: repository not participant')
        if wp.get('source_revision')!=feature.get('source_revision'): errors.append(f'{wid}: source_revision differs from feature')
        unknown=set(wp.get('global_change_ids',[]))-set(change_ids)
        if unknown: errors.append(f'{wid}: unknown global changes {sorted(unknown)}')
        if wp.get('status')=='BLOCKED' and not wp.get('blocked_by'): errors.append(f'{wid}: BLOCKED requires blocked_by')

    roadmap=load_yaml(fdir/'roadmap.yaml'); ids=[i['id'] for i in roadmap.get('items',[])]
    if len(ids)!=len(set(ids)): errors.append('duplicate roadmap item id')
    known=set(ids)
    for item in roadmap.get('items',[]):
        for dep in item.get('depends_on',[]):
            if dep not in known: errors.append(f"{item['id']}: unknown dependency {dep}")
        for wid in item.get('work_packages',[]) or []:
            if wid not in actual: errors.append(f"{item['id']}: unknown work package {wid}")
        if item.get('status')=='BLOCKED' and not item.get('blocked_by'): errors.append(f"{item['id']}: BLOCKED requires blocked_by")

    trace=fdir/'traceability.yaml'
    if trace.exists():
        t=load_yaml(trace)
        errors += [f'traceability.yaml {e}' for e in validate_jsonschema(t, ROOT/'schemas/traceability.schema.json')]
        if t.get('feature_id')!=feature.get('feature_id'): errors.append('traceability feature_id mismatch')
        twp={x['work_package_id'] for x in t.get('work_packages',[])}
        if twp!=actual: errors.append(f'traceability work package set mismatch {sorted(twp)} != {sorted(actual)}')

    if errors:
        print('FEATURE INVALID')
        for e in errors: print('-',e)
        raise SystemExit(1)
    print('FEATURE VALID')
    print(f"feature_id={feature['feature_id']}")
    print(f'participants={len(participants)}')
    print(f'global_changes={len(change_ids)}')
    print(f'work_packages={len(wps)}')
    print(f"contracts={len(feature.get('contracts',[]) or [])}")
    print(f"source_revision={feature.get('source_revision')}")

if __name__=='__main__': main()
