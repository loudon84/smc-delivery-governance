from __future__ import annotations
from pathlib import Path
from governance_lib import ROOT, repository_catalog, load_yaml, dump_yaml


def main():
    repos=repository_catalog()
    wp_states={rid:[] for rid in repos}
    for fdir in (ROOT/'features').glob('FEAT-*'):
        for p in (fdir/'work-packages').glob('*.yaml'):
            wp=load_yaml(p); rid=wp.get('repository_id')
            if rid in wp_states and wp.get('status')!='SUPERSEDED': wp_states[rid].append(wp.get('sync_state','UNKNOWN'))
    for rid,repo0 in repos.items():
        states=wp_states[rid]; current=repo0.get('governance_state','REGISTERED')
        if not states: target='REGISTERED'
        elif all(s=='SYNCED' for s in states): target='ENFORCED' if current=='ENFORCED' else 'SYNCED'
        else: target='OUT_OF_SYNC'
        if target!=current:
            path=ROOT/repo0['_path']; repo={k:v for k,v in repo0.items() if k!='_path'}; repo['governance_state']=target; dump_yaml(path,repo)
            print(f'{rid}: {current}->{target}')
        else: print(f'{rid}: {current}')

if __name__=='__main__': main()
