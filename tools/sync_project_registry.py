from __future__ import annotations
import argparse, yaml
from governance_lib import ROOT, repository_catalog, project_catalog, github_file, load_yaml, dump_yaml, validate_jsonschema


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--apply',action='store_true'); ap.add_argument('--token'); args=ap.parse_args()
    repos=repository_catalog(); projects=project_catalog(); bad=False
    for rid,r0 in repos.items():
        text=github_file(r0['name'], '.agents/governance/project-status.yaml', r0['default_branch'], token=args.token)
        current=r0.get('governance_state','REGISTERED')
        if text is None:
            target='REGISTERED'; print(f'{rid}: project-status missing -> {target}'); continue
        try: report=yaml.safe_load(text)
        except Exception as e: print(f'{rid}: invalid project-status: {e}'); bad=True; continue
        errors=validate_jsonschema(report, ROOT/'schemas/project-report.schema.json')
        if errors or report.get('repository_id')!=rid or report.get('project_id')!=r0.get('project_id'):
            print(f'{rid}: invalid project-status identity/schema'); bad=True; continue
        target='ENFORCED' if report.get('enforcement') else 'BOOTSTRAPPED'
        if current in {'SYNCED','ENFORCED'} and target=='BOOTSTRAPPED': target=current
        print(f'{rid}: remote bootstrap={target} kit={report.get("kit_version")}')
        if args.apply and current!=target and current not in {'OUT_OF_SYNC','SYNCED','ENFORCED'}:
            path=ROOT/r0['_path']; r={k:v for k,v in r0.items() if k!='_path'}; r['governance_state']=target; dump_yaml(path,r)
    if bad: raise SystemExit(2)

if __name__=='__main__': main()
