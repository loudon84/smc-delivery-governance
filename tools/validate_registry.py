from __future__ import annotations
from governance_lib import ROOT, project_catalog, repository_catalog, team_catalog, contract_catalog, validate_jsonschema


# @lat: [[registry#Registry]]
def main():
    errors=[]
    projects=project_catalog(); repos=repository_catalog(); teams=team_catalog(); contracts=contract_catalog()

    for pid,p in projects.items():
        data={k:v for k,v in p.items() if k!='_path'}
        errors += [f"{p['_path']} {e}" for e in validate_jsonschema(data, ROOT/'schemas/project.schema.json')]
        for rid in p.get('repositories',[]):
            if rid not in repos: errors.append(f"{pid}: unknown repository {rid}")
        if p.get('team') and p['team'] not in teams: errors.append(f"{pid}: unknown team {p['team']}")
        for cid in p.get('interfaces_provided',[]) + p.get('interfaces_consumed',[]):
            if cid not in contracts: errors.append(f"{pid}: unknown contract {cid}")

    seen_names={}
    for rid,r in repos.items():
        data={k:v for k,v in r.items() if k!='_path'}
        errors += [f"{r['_path']} {e}" for e in validate_jsonschema(data, ROOT/'schemas/repository.schema.json')]
        if r.get('project_id') not in projects: errors.append(f"{rid}: unknown project {r.get('project_id')}")
        name=r.get('name')
        if name in seen_names: errors.append(f"duplicate repository name {name}: {seen_names[name]}, {rid}")
        seen_names[name]=rid

    for cid,c in contracts.items():
        data={k:v for k,v in c.items() if k!='_path'}
        errors += [f"{c['_path']} {e}" for e in validate_jsonschema(data, ROOT/'schemas/contract.schema.json')]
        if c.get('provider_repository') not in repos: errors.append(f"{cid}: unknown provider {c.get('provider_repository')}")
        for rid in c.get('primary_consumers',[]):
            if rid not in repos: errors.append(f"{cid}: unknown consumer {rid}")

    if errors:
        print('REGISTRY INVALID')
        for e in errors: print(f'- {e}')
        raise SystemExit(1)
    print('REGISTRY VALID')
    print(f'projects={len(projects)} repositories={len(repos)} teams={len(teams)} contracts={len(contracts)}')

if __name__=='__main__': main()
