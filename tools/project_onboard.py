from __future__ import annotations
import argparse, re
from pathlib import Path
from governance_lib import ROOT, project_catalog, repository_catalog, team_catalog, dump_yaml, validate_jsonschema


def slug(value:str)->str:
    return re.sub(r'[^a-z0-9]+','-',value.lower()).strip('-')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project-id', required=True)
    ap.add_argument('--project-name', required=True)
    ap.add_argument('--repository-id', required=True)
    ap.add_argument('--repo', required=True, help='owner/name')
    ap.add_argument('--branch', required=True)
    ap.add_argument('--team', required=True)
    ap.add_argument('--domains', default='')
    ap.add_argument('--local-lat', default='lat.md/lat.md')
    ap.add_argument('--local-skills', default='.agents/skills')
    ap.add_argument('--local-roadmaps', default='docs/roadmaps')
    ap.add_argument('--local-prds', default='docs/prd')
    ap.add_argument('--local-plans', default='.cursor/plans')
    ap.add_argument('--apply', action='store_true')
    args=ap.parse_args()

    projects=project_catalog(); repos=repository_catalog(); teams=team_catalog()
    if args.project_id in projects: raise SystemExit(f'project already exists: {args.project_id}')
    if args.repository_id in repos: raise SystemExit(f'repository already exists: {args.repository_id}')
    if args.team not in teams: raise SystemExit(f'team not registered: {args.team}')
    if any(r.get('name')==args.repo for r in repos.values()): raise SystemExit(f'repository name already registered: {args.repo}')

    project={
      'project_id':args.project_id,'name':args.project_name,'status':'ACTIVE','repositories':[args.repository_id],
      'domains':[x.strip() for x in args.domains.split(',') if x.strip()],'team':args.team
    }
    repository={
      'repository_id':args.repository_id,'project_id':args.project_id,'name':args.repo,'provider':'github','default_branch':args.branch,
      'governance_state':'REGISTERED','governance_policy':'REPOSITORY-GOVERNANCE-V1',
      'governance':{
        'local_lat':args.local_lat,'local_skills':args.local_skills,'local_roadmaps':args.local_roadmaps,
        'local_prds':args.local_prds,'local_plans':args.local_plans,
        'delivery_receipts':'.agents/governance/receipts','acceptance_manifests':'.agents/governance/acceptance'
      },
      'github':{'issue_tracking':True,'pull_requests':True}
    }
    errors=[]
    errors += validate_jsonschema(project, ROOT/'schemas/project.schema.json')
    errors += validate_jsonschema(repository, ROOT/'schemas/repository.schema.json')
    if errors:
        for e in errors: print(e)
        raise SystemExit(1)

    print('PROJECT ONBOARDING PREVIEW')
    print(project)
    print(repository)
    if not args.apply:
        print('DRY RUN: add --apply to write registry files')
        return
    name=slug(args.project_name)
    dump_yaml(ROOT/'registry/projects'/f'{name}.yaml', project)
    dump_yaml(ROOT/'registry/repositories'/f'{slug(args.repo.split("/")[-1])}.yaml', repository)
    print('REGISTERED')
    print('Next: governance_sync.py --repo <local-clone> --project', args.project_id, '--apply')

if __name__=='__main__': main()
