from __future__ import annotations
import argparse
from governance_lib import ROOT, load_yaml, load_work_packages


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('program'); args=ap.parse_args()
    pdir=ROOT/'programs'/args.program
    if not pdir.exists(): raise SystemExit('program not found')
    program=load_yaml(pdir/'program.yaml'); print(f"Program {program['program_id']} — {program['name']} [{program['status']}]")
    for fid in program.get('features',[]):
        fdir=ROOT/'features'/fid; f=load_yaml(fdir/'feature.yaml'); print(f"\n{fid} [{f['status']}] {f['title']}")
        for wid,wp in load_work_packages(fdir).items(): print(f"  {wid} {wp['repository_id']} status={wp['status']} sync={wp.get('sync_state')}")
        sp=ROOT/'integration/scenarios'/f'{fid}.yaml'
        if sp.exists():
            s=load_yaml(sp); print(f"  Integration {s['scenario_id']} state={s['state']}")

if __name__=='__main__': main()
