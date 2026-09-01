from __future__ import annotations
import sys
from governance_lib import project_catalog, repository_catalog, ROOT, load_yaml


def main():
    projects=project_catalog(); repos=repository_catalog(); ids=sys.argv[1:] or sorted(projects)
    for pid in ids:
        p=projects.get(pid)
        if not p: print('UNKNOWN',pid); continue
        print(f"{pid} — {p['name']} [{p['status']}]")
        for rid in p.get('repositories',[]):
            r=repos.get(rid); print(f"  {rid} {r.get('name')} governance={r.get('governance_state')} branch={r.get('default_branch')}")
            for fdir in (ROOT/'features').glob('FEAT-*'):
                for wp_path in (fdir/'work-packages').glob('*.yaml'):
                    wp=load_yaml(wp_path)
                    if wp.get('repository_id')==rid:
                        print(f"    {wp['feature_id']} {wp['work_package_id']} status={wp['status']} sync={wp.get('sync_state')}")

if __name__=='__main__': main()
