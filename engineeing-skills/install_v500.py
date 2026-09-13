#!/usr/bin/env python3
"""Transactional GES 5 installer; preserves installed v2 profile policy for in-flight Plans."""
import json,os,shlex,sys,uuid
from pathlib import Path
import install_v441 as inherited
from build_package_manifest import verify
base=inherited.suite
base.PACKAGE_VERSION='5.0.0'
PROJECT=None
SELECTOR=None
def bounded(root,rel):
 p=(root/rel).resolve()
 if not p.is_relative_to(root.resolve()):raise ValueError('INSTALL_PATH_OUTSIDE_ROOT: '+str(rel))
 return p
def resolve_profile(project,selector):
 global PROJECT,SELECTOR
 PROJECT,SELECTOR=project,selector
 installed=project/'.agents/ges/profile.json'
 path=(Path(selector).resolve() if selector and Path(selector).is_file() else base.CONSUMERS/(selector.removesuffix('.json')+'.json') if selector else installed if installed.is_file() else base.CONSUMERS/'generic.json')
 profile=base.read_json(path)
 if profile.get('schema') not in {'smc.ges.consumer-profile.v2','smc.ges.consumer-profile.v3'}:raise ValueError('CONSUMER_PROFILE_SCHEMA_INVALID')
 return path,profile
def pack_context(profile):
 # Omission of --profile means preserve installed metadata, including local pack policy.
 installed=PROJECT/'.agents/ges/domain-packs' if PROJECT else None
 root=installed if SELECTOR is None and installed and (installed/'registry.json').is_file() else base.PACKAGE/('domain-packs-v1' if profile['schema'].endswith('.v2') else 'domain-packs')
 registry=base.read_json(root/'registry.json');selected={}
 if registry.get('schema')!='smc.ges.domain-registry.v1':raise ValueError('DOMAIN_REGISTRY_SCHEMA_INVALID')
 for domain in profile.get('domains',{}):
  row=registry.get('packs',{}).get(domain)
  if not isinstance(row,dict):raise ValueError('DOMAIN_PACK_NOT_REGISTERED: '+domain)
  path=bounded(root,row['path']);pack=base.read_json(path)
  schema='smc.ges.domain-pack.v1' if profile['schema'].endswith('.v2') else 'smc.ges.domain-pack.v2'
  if pack.get('schema')!=schema or pack.get('id')!=domain:raise ValueError('DOMAIN_PACK_INVALID: '+domain)
  selected[domain]=(path,pack)
 return registry,selected
_previous_preflight=base.preflight
def preflight(project,profile,selected,names):
 errors=_previous_preflight(project,profile,selected,names)
 for rel in profile.get('project_policy_paths',[]):
  if not bounded(project,rel).is_file():errors.append('PROJECT_POLICY_MISSING: '+rel)
 for name in names:
  bounded(base.SKILLS,name);bounded(project,'.agents/skills/'+name)
 return errors
_previous_record=base.record_before
def record_before(project,target,backup,records):
 bounded(project,target.relative_to(project))
 return _previous_record(project,target,backup,records)
_previous_metadata=base.install_ges_metadata
def install_metadata(project,profile,selected,backup,records):
 # Metadata copied from the installed source onto itself would raise SameFileError.
 installed=project/'.agents/ges'
 if SELECTOR is None and (installed/'profile.json').is_file():
  return base.copy_tree(project,base.DOMAIN_RUNTIME,installed/'domain-runtime',backup,records)
 return _previous_metadata(project,profile,selected,backup,records)
_previous_commands=base.validation_commands
def validation_commands(project,profile,selected,skip):
 commands=_previous_commands(project,profile,selected,True)
 scripts=project/'.agents/skills'
 for label,relative in [('work router','using-superpowers/scripts/test_work_router.py'),('PRD profile','smc-prd-grounding/scripts/test_prd_profile.py'),('v5 runtime','smc-plan-delivery/scripts/test_engineering_method_v2.py')]:
  commands.append((label,[sys.executable,str(scripts/relative)]))
 validator=profile.get('project_validator')
 if validator and not skip:
  parts=shlex.split(str(validator),posix=True)
  if parts and parts[0].lower().startswith('python'):
   if len(parts)<2 or not bounded(project,parts[1]).is_file():raise ValueError('CONSUMER_PROJECT_VALIDATOR_MISSING')
   parts=[sys.executable,str(bounded(project,parts[1])),*parts[2:]]
  commands.append(('consumer project validator',parts))
 return commands
base.resolve_profile=resolve_profile
base.pack_context=pack_context
base.preflight=preflight
base.record_before=record_before
base.install_ges_metadata=install_metadata
base.validation_commands=validation_commands
base.now_tag=lambda:uuid.uuid4().hex
def main():
 try:verify()
 except (ValueError,OSError) as exc:print('INSTALL_INTEGRITY_BLOCKED:',exc);return 2
 os.environ.setdefault('PYTHONUTF8','1')
 return base.main()
if __name__=='__main__':raise SystemExit(main())
