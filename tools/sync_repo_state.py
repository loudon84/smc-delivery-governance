from __future__ import annotations
import argparse, urllib.parse, yaml
from datetime import datetime, timezone
from governance_lib import (
    ROOT, load_feature, load_work_packages, repository_catalog, contract_catalog,
    validate_jsonschema, github_file, github_api, dump_yaml, WP_ORDER
)


def discover_github(repo_name:str, wp_id:str, token=None):
    q=f'repo:{repo_name} label:"gov:wp:{wp_id}"'
    data=github_api('/search/issues?q='+urllib.parse.quote(q)+'&per_page=100', token=token)
    issues=[]; bugs=[]; prs=[]
    for item in data.get('items',[]):
        labels=[x['name'] for x in item.get('labels',[])]
        ref={'number':item['number'],'state':item['state'],'title':item['title'],'url':item['html_url'],'labels':labels}
        if item.get('pull_request'):
            ref['state']='merged' if item.get('pull_request',{}).get('merged_at') else item['state']
            prs.append(ref)
        elif 'gov:type:bug' in labels: bugs.append(ref)
        else: issues.append(ref)
    return issues,bugs,prs


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('feature')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--discover-github', action='store_true')
    ap.add_argument('--token')
    args=ap.parse_args()
    fdir,feature=load_feature(args.feature); wps=load_work_packages(fdir); repos=repository_catalog(); contracts=contract_catalog()
    any_bad=False

    for wid,wp in wps.items():
        repo=repos.get(wp['repository_id'])
        if not repo:
            print(f'{wid}: DIVERGED unknown repository'); any_bad=True; continue
        receipt_dir=repo['governance']['delivery_receipts']
        receipt_path=f"{receipt_dir.rstrip('/')}/{wid}.yaml"
        text=github_file(repo['name'], receipt_path, repo['default_branch'], token=args.token)
        if text is None:
            print(f'{wid}: MISSING_RECEIPT {receipt_path}')
            if args.apply:
                path=fdir/'work-packages'/Path(wp['_path']).name
                clean={k:v for k,v in wp.items() if k!='_path'}; clean['sync_state']='MISSING_RECEIPT'; dump_yaml(path,clean)
            any_bad=True; continue
        try: receipt=yaml.safe_load(text)
        except Exception as e:
            print(f'{wid}: DIVERGED invalid yaml: {e}'); any_bad=True; continue
        errors=validate_jsonschema(receipt, ROOT/'schemas/delivery-receipt.schema.json')
        if errors:
            print(f'{wid}: DIVERGED invalid receipt: {errors[0]}'); any_bad=True; continue
        if receipt['feature_id'] != feature['feature_id'] or receipt['work_package_id'] != wid or receipt['repository_id'] != wp['repository_id']:
            print(f'{wid}: DIVERGED identity mismatch'); any_bad=True; continue
        sync_state='SYNCED'
        if receipt['source_revision'] != feature['source_revision'] or receipt['source_revision'] != wp['source_revision']:
            sync_state='STALE_FEATURE'
        # Contract pin check only compares declared version; release identity remains consumer-local evidence.
        expected={x['contract_id']:x.get('version') or x.get('required_version') for x in wp.get('contract_inputs',[])}
        actual={x['contract_id']:x.get('version') for x in (receipt.get('sync') or {}).get('contract_pins',[])}
        for cid,ver in expected.items():
            if ver and actual.get(cid) != ver: sync_state='STALE_CONTRACT'
        # VERIFIED/DONE cannot be accepted without commit + acceptance PASS.
        claimed=receipt['status']
        if claimed in {'VERIFIED','DONE'}:
            if not receipt['delivery'].get('commits') or (receipt.get('acceptance') or {}).get('status')!='PASS': sync_state='DIVERGED'

        if args.discover_github:
            try:
                issues,bugs,prs=discover_github(repo['name'], wid, args.token)
                receipt['delivery']['issues']=issues; receipt['delivery']['bugs']=bugs; receipt['delivery']['pull_requests']=prs
            except Exception as e:
                print(f'{wid}: GitHub discovery warning: {e}')

        print(f'{wid}: {sync_state} local={claimed} central={wp["status"]}')
        if args.apply:
            ledger={
              'feature_id':feature['feature_id'],'work_package_id':wid,'repository_id':wp['repository_id'],
              'source_revision':receipt['source_revision'],'observed_at':datetime.now(timezone.utc).isoformat(),
              'receipt_path':receipt_path,'status':claimed,'sync_state':sync_state,
              'delivery':receipt['delivery'],'acceptance':receipt.get('acceptance'), 'evidence':receipt.get('evidence',{})
            }
            dump_yaml(fdir/'delivery-ledger'/f"{wp['repository_id']}.yaml", ledger)
            path=fdir/'work-packages'/Path(wp['_path']).name
            clean={k:v for k,v in wp.items() if k!='_path'}
            clean['sync_state']=sync_state
            clean['delivery_receipt']=f"repo://{repo['name']}/{receipt_path}@{repo['default_branch']}"
            clean['observed']={'reported_status':claimed,'reported_at':receipt['reported_at'],'receipt_path':receipt_path}
            # Remote receipt updates observed facts only. Central lifecycle state remains governed by transition_state/reconcile_states.
            dump_yaml(path,clean)
        if sync_state!='SYNCED': any_bad=True
    if any_bad: raise SystemExit(2)

if __name__=='__main__': main()
