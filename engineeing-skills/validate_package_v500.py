#!/usr/bin/env python3
"""Complete v5 package gate: integrity, contracts, regressions, real consumer installation and rollback."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
from build_package_manifest import verify
ROOT=Path(__file__).resolve().parent
def run(label,args,cwd=ROOT):
 print('VALIDATING:',label,flush=True)
 result=subprocess.run(args,cwd=cwd,env={**os.environ,'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1'})
 if result.returncode:raise ValueError('PACKAGE_TEST_FAILED: '+label)
def main():
 try:
  print('PACKAGE INTEGRITY PASS:',verify(),flush=True)
  count=0
  for p in ROOT.rglob('*.py'):
   if '__pycache__' not in p.parts:compile(p.read_text(encoding='utf-8'),str(p),'exec');count+=1
  print('PYTHON COMPILE PASS:',count,flush=True)
  # Use the installer-owned test registry so installed and source validation cannot drift.
  import install_v500 as installer
  _,profile=installer.resolve_profile(ROOT,'generic');_,selected=installer.pack_context(profile)
  core=json.loads((ROOT/'core/manifest.json').read_text(encoding='utf-8'))
  for skill in installer.base.managed_skills(profile,selected):
   path=ROOT/'.agents/skills'/skill/'SKILL.md'
   if not path.is_file() or 'name: '+skill not in path.read_text(encoding='utf-8'):raise ValueError('MANAGED_SKILL_INVALID: '+skill)
  for _,pack in selected.values():
   for field in ('preplan_validator','plan_validator','selftest','verification_preflight'):
    if pack.get(field) and not (ROOT/pack[field]).is_file():raise ValueError('DOMAIN_PROVIDER_MISSING: '+str(pack[field]))
  for label,cmd in installer.validation_commands(ROOT,profile,selected,True):run(label,cmd)
  run('package v5 integration regressions',[sys.executable,str(ROOT/'tests/test_package_v500.py'),'-v'])
  sys.path.insert(0,str(ROOT/'tests'))
  from test_package_v500 import fixture
  with tempfile.TemporaryDirectory(prefix='ges-v5-consumer-') as td:
   project=Path(td);fixture(project)
   run('consumer install dry run',[sys.executable,str(ROOT/'install.py'),str(project),'--profile','generic'])
   run('consumer actual install',[sys.executable,str(ROOT/'install.py'),str(project),'--profile','generic','--apply'])
   lock=json.loads((project/'.smc/ges-install-lock.json').read_text(encoding='utf-8'))
   if lock['bundle']!='5.0.0':raise ValueError('INSTALL_LOCK_VERSION_INVALID')
   if lock.get('schema')!='smc.ges.install-lock.v2':raise ValueError('INSTALL_LOCK_V2_INVALID')
   if 'release_identity' not in lock or 'owned_files' not in lock:raise ValueError('INSTALL_RELEASE_IDENTITY_INVALID')
   for p in (project/'.agents/skills').rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts:
     mirror=project/'.cursor/skills'/p.relative_to(project/'.agents/skills')
     # Consumer-owned skills are intentionally not package-managed.
     if p.relative_to(project/'.agents/skills').parts[0] in installer.base.managed_skills(profile,selected) and (not mirror.is_file() or p.read_bytes()!=mirror.read_bytes()):raise ValueError('MIRROR_DRIFT: '+str(p))
   run('consumer rollback',[sys.executable,str(ROOT/'rollback.py'),str(project),'--apply'])
   if (project/'.agents/skills/smc-plan-delivery/SKILL.md').exists():raise ValueError('ROLLBACK_LEFTOVER')
  print('PACKAGE VALIDATION PASS — GES 5.0.0; full registered regressions + real fixture install/rollback',flush=True)
  return 0
 except (ValueError,OSError,KeyError,SyntaxError) as exc:
  print('PACKAGE VALIDATION FAILED:',exc,file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
