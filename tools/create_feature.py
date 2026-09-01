from __future__ import annotations
import argparse
from pathlib import Path
from governance_lib import ROOT, repository_catalog, dump_yaml


def pair(value:str):
    if ':' not in value: raise argparse.ArgumentTypeError('expected KEY:VALUE')
    return value.split(':',1)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--feature-id',required=True); ap.add_argument('--title',required=True); ap.add_argument('--program-id',required=True)
    ap.add_argument('--source-prd-id',required=True); ap.add_argument('--source-prd-repo'); ap.add_argument('--source-prd-path'); ap.add_argument('--source-revision',required=True)
    ap.add_argument('--feature-owner',required=True); ap.add_argument('--integration-owner',required=True)
    ap.add_argument('--participant',action='append',type=pair,required=True,help='REPO-ID:provider|consumer|shared|observer')
    ap.add_argument('--change',action='append',type=pair,required=True,help='XR-C01:Title')
    ap.add_argument('--apply',action='store_true')
    args=ap.parse_args()
    repos=repository_catalog(); participants=[]
    for rid,role in args.participant:
        if rid not in repos: raise SystemExit(f'unknown repository: {rid}')
        if role not in {'provider','consumer','shared','observer'}: raise SystemExit(f'invalid role: {role}')
        participants.append({'repository_id':rid,'role':role})
    fdir=ROOT/'features'/args.feature_id
    if fdir.exists(): raise SystemExit(f'feature already exists: {args.feature_id}')
    changes=[{'id':cid,'title':title} for cid,title in args.change]
    work_packages=[]; wp_docs=[]
    for p in participants:
        if p['role']=='observer': continue
        suffix=p['repository_id'].removeprefix('REPO-')
        wid=f"WP-{args.feature_id.removeprefix('FEAT-')}-{suffix}"
        work_packages.append(wid)
        wp_docs.append((wid,{
          'work_package_id':wid,'feature_id':args.feature_id,'repository_id':p['repository_id'],'role':p['role'],'status':'BACKLOG',
          'owner':repos[p['repository_id']].get('project_id'),'outcome':f"Deliver {args.title} responsibilities owned by {p['repository_id']}",
          'source_revision':args.source_revision,'sync_state':'MISSING_RECEIPT','global_change_ids':[x['id'] for x in changes],
          'contract_inputs':[],'contract_outputs':[],'dependencies':[],'local_delivery':{'roadmap':None,'prd':None,'plan':None},
          'acceptance':['Local Stage PRD maps all assigned global changes to verifiable acceptance evidence.'],
          'evidence_required':['implementation_commit','verification_evidence'],'delivery_receipt':None,'observed':{},'evidence':{}
        }))
    feature={
      'feature_id':args.feature_id,'title':args.title,'program_id':args.program_id,'status':'PROPOSED','source_revision':args.source_revision,
      'source_prd':{'id':args.source_prd_id,'repository_id':args.source_prd_repo,'path':args.source_prd_path,'revision':args.source_revision,'status':'APPROVED'},
      'feature_owner':args.feature_owner,'integration_owner':args.integration_owner,'participants':participants,'global_changes':changes,'contracts':[],
      'work_packages':work_packages,'integration':{'scenario_id':f"INT-{args.feature_id.removeprefix('FEAT-')}-001",'state':'WAITING_PROVIDER','required_repo_states':{},'required_contract_states':{}}
    }
    print('FEATURE CREATE PREVIEW')
    print(feature)
    if not args.apply:
        print('DRY RUN: add --apply')
        return
    fdir.mkdir(parents=True)
    dump_yaml(fdir/'feature.yaml',feature)
    dump_yaml(fdir/'roadmap.yaml',{'feature_id':args.feature_id,'items':[]})
    dump_yaml(fdir/'dependencies.yaml',{'feature_id':args.feature_id,'dependencies':[]})
    dump_yaml(fdir/'traceability.yaml',{'feature_id':args.feature_id,'source_prd':{'id':args.source_prd_id,'repository_id':args.source_prd_repo,'path':args.source_prd_path,'revision':args.source_revision},'work_packages':[{'work_package_id':wid,'repository_id':doc['repository_id'],'stage_prds':[],'issues':[],'bugs':[],'plans':[],'commits':[],'verification':[]} for wid,doc in wp_docs]})
    dump_yaml(fdir/'acceptance.yaml',{'feature_id':args.feature_id,'source_revision':args.source_revision,'requirements':[]})
    for wid,doc in wp_docs:
        filename=doc['repository_id'].removeprefix('REPO-').lower()+'.yaml'; dump_yaml(fdir/'work-packages'/filename,doc)
    (fdir/'architecture.md').write_text(f"# {args.feature_id} Architecture\n\nSource PRD: `{args.source_prd_id}` @ `{args.source_revision}`.\n\nDefine cross-repo ownership and interface boundaries here; do not write repository implementation details.\n",encoding='utf-8',newline='\n')
    (fdir/'evidence').mkdir(parents=True,exist_ok=True)
    dump_yaml(fdir/'evidence/index.yaml',{'feature_id':args.feature_id,'evidence':{}})
    print(f'CREATED {fdir}')

if __name__=='__main__': main()
