from __future__ import annotations
import argparse
from governance_lib import ROOT, load_feature, load_work_packages, load_yaml


def fmt(items, key=None):
    if not items: return '-'
    vals=[]
    for x in items:
        if isinstance(x,str): vals.append(x)
        elif key and x.get(key) is not None: vals.append(str(x[key]))
        else: vals.append(str(x))
    return ', '.join(vals)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('feature'); args=ap.parse_args()
    fdir,feature=load_feature(args.feature); wps=load_work_packages(fdir)
    print(f"Feature {feature['feature_id']}: {feature['title']}")
    src=feature.get('source_prd') or {}
    print(f"Source PRD: {src.get('id')} revision={feature.get('source_revision')} path={src.get('path')}")
    print()
    for wid,wp in wps.items():
        ledger=fdir/'delivery-ledger'/f"{wp['repository_id']}.yaml"
        obs=load_yaml(ledger) if ledger.exists() else {}
        delivery=obs.get('delivery',{})
        print(f"{wid} [{wp.get('status')}] repo={wp['repository_id']} sync={wp.get('sync_state')}")
        print(f"  Stage PRDs: {fmt(delivery.get('stage_prds'), 'path')}")
        print(f"  Issues: {fmt(delivery.get('issues'), 'number')}")
        print(f"  Bugs: {fmt(delivery.get('bugs'), 'number')}")
        print(f"  Plans: {fmt(delivery.get('plans'), 'path')}")
        print(f"  PRs: {fmt(delivery.get('pull_requests'), 'number')}")
        print(f"  Commits: {fmt(delivery.get('commits'))}")
        print(f"  Acceptance: {(obs.get('acceptance') or {}).get('status','UNKNOWN')}")
        print()

if __name__=='__main__': main()
