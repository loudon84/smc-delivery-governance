from __future__ import annotations
import argparse
from governance_lib import load_feature, load_work_packages, load_yaml, dump_yaml, WP_ORDER
from state_machine import allowed, work_package_gate, feature_gate

WP_SEQUENCE=['BACKLOG','READY','IN_PRD','PLANNED','IMPLEMENTING','REVIEW','VERIFIED','DONE']
FEATURE_SEQUENCE=['PROPOSED','ARCHITECTURE','PLANNED','IMPLEMENTING','INTEGRATING','VERIFYING','DONE']


def promote_wp(fdir, path, wp, observed_target, apply):
    if wp.get('status') in {'BLOCKED','SUPERSEDED'} or observed_target not in WP_SEQUENCE: return wp['status']
    current=wp['status']; target_index=WP_SEQUENCE.index(observed_target)
    while current in WP_SEQUENCE and WP_SEQUENCE.index(current)<target_index:
        nxt=WP_SEQUENCE[WP_SEQUENCE.index(current)+1]
        if not allowed('work_package',current,nxt): break
        errors=work_package_gate(fdir,{**wp,'status':current},nxt)
        if errors:
            print(f"{wp['work_package_id']}: stop {current}->{nxt}: {errors[0]}")
            break
        print(f"{wp['work_package_id']}: {current}->{nxt}")
        current=nxt
        if apply:
            wp['status']=current; dump_yaml(path,wp)
    return current


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('feature'); ap.add_argument('--apply',action='store_true'); args=ap.parse_args()
    fdir,feature=load_feature(args.feature); wps=load_work_packages(fdir)
    for wid,wp0 in wps.items():
        path=fdir/'work-packages'/__import__('pathlib').Path(wp0['_path']).name
        wp={k:v for k,v in wp0.items() if k!='_path'}
        ledger=fdir/'delivery-ledger'/f"{wp['repository_id']}.yaml"
        if not ledger.exists(): continue
        obs=load_yaml(ledger); promote_wp(fdir,path,wp,obs.get('status'),args.apply)

    # Reload after possible WP transitions.
    fdir,feature=load_feature(args.feature); wps=load_work_packages(fdir)
    current=feature['status']
    desired=None
    if all(wp.get('status') in {'VERIFIED','DONE'} for wp in wps.values()): desired='INTEGRATING'
    scenario=load_yaml(__import__('pathlib').Path(__file__).resolve().parents[1]/'integration/scenarios'/f"{feature['feature_id']}.yaml")
    if scenario.get('state')=='PASS' and all(wp.get('status') in {'VERIFIED','DONE'} for wp in wps.values()): desired='DONE'
    if desired and current in FEATURE_SEQUENCE:
        while FEATURE_SEQUENCE.index(current)<FEATURE_SEQUENCE.index(desired):
            nxt=FEATURE_SEQUENCE[FEATURE_SEQUENCE.index(current)+1]
            if not allowed('feature',current,nxt): break
            errors=feature_gate(fdir,{**feature,'status':current},nxt)
            if errors:
                print(f"Feature stop {current}->{nxt}: {errors[0]}"); break
            print(f"Feature {current}->{nxt}"); current=nxt
            if args.apply:
                feature['status']=current; dump_yaml(fdir/'feature.yaml',feature)

if __name__=='__main__': main()
