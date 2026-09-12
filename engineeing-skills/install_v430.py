#!/usr/bin/env python3
"""Install GES v4.3.1 Core + selected Domain Packs transactionally.

Key rule: Consumer Profile declares available domains; Plan Change Scope activates
those domains later. Installer never hardcodes domain ids or framework names.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
from typing import Any

PACKAGE=Path(__file__).resolve().parent
SKILLS=PACKAGE/'.agents/skills'
CORE_MANIFEST=PACKAGE/'core/manifest.json'
DOMAIN_RUNTIME=PACKAGE/'domain-runtime'
DOMAIN_PACKS=PACKAGE/'domain-packs'
CONSUMERS=PACKAGE/'consumers'
INTEGRATION=PACKAGE/'project-integration'
PACKAGE_VERSION='4.3.1'
IGNORE_LINES=['.smc/evidence/','.smc/reviews/','.smc/runs/','.smc/skill-upgrade-backups/','__pycache__/','*.py[cod]']


def read_json(path:Path)->dict[str,Any]:
    value=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict): raise ValueError(f'JSON_OBJECT_REQUIRED: {path}')
    return value

def now_tag(): return dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
def sha256(path:Path):
    if not path.is_file(): return None
    h=hashlib.sha256();
    with path.open('rb') as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def rel_files(root:Path):
    if not root.is_dir(): return []
    return sorted(p.relative_to(root) for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
def tree_files(root:Path):
    if not root.is_dir(): return {}
    return {p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
def prune(root:Path):
    if not root.exists():return
    for p in sorted((x for x in root.rglob('*') if x.is_dir()),reverse=True):
        try:p.rmdir()
        except OSError:pass

def run(cmd:list[str],cwd:Path,capture=False):
    print('+',' '.join(str(x) for x in cmd));env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env.setdefault('PYTHONUTF8','1')
    return subprocess.run(cmd,cwd=cwd,text=True,encoding='utf-8',errors='replace',capture_output=capture,env=env)

def resolve_profile(project:Path,selector:str|None)->tuple[Path,dict[str,Any]]:
    installed=project/'.agents/ges/profile.json'
    if selector:
        candidate=Path(selector)
        if candidate.is_file(): path=candidate.resolve()
        else:
            name=selector[:-5] if selector.endswith('.json') else selector
            path=CONSUMERS/f'{name}.json'
    elif installed.is_file(): path=installed
    else:path=CONSUMERS/'generic.json'
    if not path.is_file(): raise ValueError(f'CONSUMER_PROFILE_NOT_FOUND: {path}')
    profile=read_json(path)
    if profile.get('schema')!='smc.ges.consumer-profile.v2': raise ValueError(f'CONSUMER_PROFILE_SCHEMA_INVALID: {profile.get("schema")}')
    return path,profile

def pack_context(profile:dict[str,Any]):
    registry=read_json(DOMAIN_PACKS/'registry.json')
    if registry.get('schema')!='smc.ges.domain-registry.v1': raise ValueError('DOMAIN_REGISTRY_SCHEMA_INVALID')
    selected={}
    for domain_id in sorted(profile.get('domains',{})):
        entry=registry.get('packs',{}).get(domain_id)
        if not isinstance(entry,dict): raise ValueError(f'DOMAIN_PACK_NOT_REGISTERED: {domain_id}')
        pack_path=DOMAIN_PACKS/str(entry.get('path',f'{domain_id}/pack.json'))
        pack=read_json(pack_path)
        if pack.get('schema')!='smc.ges.domain-pack.v1' or pack.get('id')!=domain_id: raise ValueError(f'DOMAIN_PACK_INVALID: {domain_id}')
        selected[domain_id]=(pack_path,pack)
    return registry,selected

def managed_skills(profile:dict[str,Any],selected:dict[str,tuple[Path,dict[str,Any]]]):
    core=read_json(CORE_MANIFEST);names=list(core.get('managed_skills',[]))
    for _,pack in selected.values():
        for capability in pack.get('capabilities',{}).values():
            skill=capability if isinstance(capability,str) else capability.get('skill') if isinstance(capability,dict) else None
            if skill and skill not in names:names.append(skill)
    return names

def record_before(project:Path,target:Path,backup:Path,records:dict[str,dict]):
    rel=target.relative_to(project).as_posix()
    if rel in records:return records[rel]
    existed=target.is_file();rec={'path':rel,'existed_before':existed,'original_sha256':sha256(target) if existed else None,'installed_sha256':None};records[rel]=rec
    if existed:
        dst=backup/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,dst)
    return rec

def write_file(project:Path,src:Path,dst:Path,backup:Path,records:dict[str,dict]):
    rec=record_before(project,dst,backup,records);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);rec['installed_sha256']=sha256(dst)
def write_text(project:Path,dst:Path,text:str,backup:Path,records:dict[str,dict]):
    rec=record_before(project,dst,backup,records);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(text,encoding='utf-8');rec['installed_sha256']=sha256(dst)
def copy_tree(project:Path,src:Path,dst:Path,backup:Path,records:dict[str,dict]):
    count=0
    for rel in rel_files(src):write_file(project,src/rel,dst/rel,backup,records);count+=1
    return count

def remove_file(project:Path,target:Path,backup:Path,records:dict[str,dict]):
    rec=record_before(project,target,backup,records)
    if target.exists():target.unlink()
    rec['installed_sha256']=None

def mirror_managed(project:Path,names:list[str],policy:str,backup:Path,records:dict[str,dict]):
    cursor=project/'.cursor/skills';canonical=project/'.agents/skills'
    if policy=='none':return 0
    if policy=='declared-managed-set' and not cursor.is_dir():return 0
    if policy not in {'managed-set','declared-managed-set','full-tree'}:raise ValueError(f'MIRROR_POLICY_INVALID: {policy}')
    cursor.mkdir(parents=True,exist_ok=True);count=0
    if policy=='full-tree':
        srcs=tree_files(canonical);dsts=tree_files(cursor)
        for rel,src in srcs.items():
            dst=cursor/rel
            if sha256(src)!=sha256(dst):write_file(project,src,dst,backup,records);count+=1
        for rel in sorted(set(dsts)-set(srcs)):remove_file(project,cursor/rel,backup,records);count+=1
        prune(cursor);return count
    for name in names:
        src_root=canonical/name
        if not src_root.is_dir():continue
        for rel in rel_files(src_root):
            src=src_root/rel;dst=cursor/name/rel
            if sha256(src)!=sha256(dst):write_file(project,src,dst,backup,records);count+=1
    return count

def install_ges_metadata(project:Path,profile:dict[str,Any],selected,backup,records):
    target=project/'.agents/ges';count=0
    count+=copy_tree(project,DOMAIN_RUNTIME,target/'domain-runtime',backup,records)
    registry={'schema':'smc.ges.domain-registry.v1','packs':{}}
    for domain_id,(pack_path,pack) in selected.items():
        src_dir=pack_path.parent;dst_dir=target/'domain-packs'/domain_id
        count+=copy_tree(project,src_dir,dst_dir,backup,records)
        registry['packs'][domain_id]={'path':f'{domain_id}/pack.json','status':'installed'}
    write_text(project,target/'domain-packs/registry.json',json.dumps(registry,ensure_ascii=False,indent=2,sort_keys=True)+'\n',backup,records);count+=1
    write_text(project,target/'profile.json',json.dumps(profile,ensure_ascii=False,indent=2,sort_keys=True)+'\n',backup,records);count+=1
    return count

def update_gitignore(project,backup,records):
    path=project/'.gitignore';text=path.read_text(encoding='utf-8') if path.is_file() else '';current={x.strip() for x in text.splitlines()};missing=[x for x in IGNORE_LINES if x not in current]
    if not missing:return False
    suffix='\n' if text and not text.endswith('\n') else '';block='# SMC governed delivery local state/evidence\n'+'\n'.join(missing)+'\n';write_text(project,path,text+suffix+('\n' if text else '')+block,backup,records);return True

def restore(project,backup,records):
    for rel in reversed(sorted(records)):
        rec=records[rel];target=project/rel
        if rec['existed_before']:
            src=backup/rel
            if not src.is_file():raise RuntimeError(f'ROLLBACK_BACKUP_MISSING: {rel}')
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
        elif target.is_file() or target.is_symlink():target.unlink()
    for base in (project/'.agents/skills',project/'.agents/ges',project/'.cursor/skills',project/'tools/agent-skills'):prune(base)
def transaction_manifest(project,backup,profile,selected,records,status):
    payload={'schema':'smc.ges.install.transaction.v2','bundle':PACKAGE_VERSION,'profile':f"{profile.get('id')}@{profile.get('version')}",'domains':{k:v[1].get('version') for k,v in selected.items()},'project':str(project),'created_at':dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z'),'status':status,'files':[records[k] for k in sorted(records)]}
    path=backup/'upgrade-manifest.json';path.write_text(json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8');return path

def preflight(project,profile,selected,names):
    errors=[]
    if not (project/'.git').exists():errors.append('TARGET_NOT_GIT_REPO: .git missing')
    for rel in profile.get('required_paths',[]):
        if not (project/rel).exists():errors.append(f'CONSUMER_REQUIRED_PATH_MISSING: {rel}')
    for name in names:
        if not (SKILLS/name/'SKILL.md').is_file():errors.append(f'PACKAGE_MANAGED_SKILL_MISSING: {name}')
    core=read_json(CORE_MANIFEST)
    for name in core.get('consumer_required_skills',[]):
        if not (project/'.agents/skills'/str(name)/'SKILL.md').is_file():errors.append(f'CONSUMER_REQUIRED_SKILL_MISSING: {name}')
    if not (DOMAIN_RUNTIME/'domain_runtime.py').is_file():errors.append('DOMAIN_RUNTIME_MISSING')
    return errors

def validation_commands(project,profile,selected,skip):
    commands=[('delivery self-test',[sys.executable,str(project/'.agents/skills/smc-plan-delivery/scripts/run_selftest.py')]),('roadmap self-test',[sys.executable,str(project/'.agents/skills/smc-roadmap/scripts/test_roadmap_v11.py'),'-q'])]
    for domain_id,(_,pack) in selected.items():
        selftest=pack.get('selftest')
        if selftest:commands.append((f'domain {domain_id} self-test',[sys.executable,str(project/selftest)]))
    validator=profile.get('project_validator')
    if validator and not skip:
        parts=str(validator).split();target=project/parts[-1]
        if target.is_file():commands.append(('consumer project validator',[sys.executable,str(target)] if parts[0].lower().startswith('python') else parts))
    return commands

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('project',nargs='?',default='.',type=Path);ap.add_argument('--profile');ap.add_argument('--apply',action='store_true');ap.add_argument('--skip-project-validator',action='store_true');a=ap.parse_args();project=a.project.resolve()
    try:
        _,profile=resolve_profile(project,a.profile);registry,selected=pack_context(profile);names=managed_skills(profile,selected);errors=preflight(project,profile,selected,names)
    except Exception as exc:print(f'PRECHECK FAILED\n{exc}',file=sys.stderr);return 2
    print(f'GES v{PACKAGE_VERSION}');print('Target :',project);print('Profile:',f"{profile.get('id')}@{profile.get('version')}");print('Domains:',', '.join(selected) if selected else 'none');print('Managed skills:',len(names))
    if errors:print('\nPRECHECK FAILED\n'+'\n'.join(errors),file=sys.stderr);return 2
    if not a.apply:print('\nDRY RUN PASS — no files written');return 0
    backup=project/'.smc/skill-upgrade-backups'/now_tag();backup.mkdir(parents=True,exist_ok=True);records={}
    try:
        count=0
        for name in names:count+=copy_tree(project,SKILLS/name,project/'.agents/skills'/name,backup,records)
        count+=copy_tree(project,INTEGRATION,project,backup,records)
        meta_count=install_ges_metadata(project,profile,selected,backup,records)
        mirror_count=mirror_managed(project,names,str(profile.get('mirror_policy','declared-managed-set')),backup,records)
        ignored=update_gitignore(project,backup,records)
        transaction_manifest(project,backup,profile,selected,records,'INSTALLED_PENDING_VALIDATION')
        for label,cmd in validation_commands(project,profile,selected,a.skip_project_validator):
            result=run(cmd,project)
            if result.returncode:raise RuntimeError(f'INSTALL_VALIDATION_FAILED: {label}')
        lock={'schema':'smc.ges.install-lock.v1','bundle':PACKAGE_VERSION,'profile':f"{profile.get('id')}@{profile.get('version')}",'domains':{k:v[1].get('version') for k,v in selected.items()}}
        write_text(project,project/'.smc/ges-install-lock.json',json.dumps(lock,ensure_ascii=False,indent=2,sort_keys=True)+'\n',backup,records)
        manifest=transaction_manifest(project,backup,profile,selected,records,'PASS')
    except Exception as exc:
        print(f'{exc}; automatic rollback starting',file=sys.stderr);restore(project,backup,records);transaction_manifest(project,backup,profile,selected,records,'ROLLED_BACK');return 1
    print('\nINSTALL PASS');print('Overlay source files :',count);print('GES metadata files   :',meta_count);print('Mirror repairs       :',mirror_count);print('.gitignore updated   :',ignored);print('Backup transaction   :',backup);print('Transaction manifest :',manifest);print('No git commit was created.')
    return 0
if __name__=='__main__':raise SystemExit(main())
