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
  # PRD §24 registry — architecture contracts only (no real Pilot/Benchmark/Harness)
  run('work facts authority',[sys.executable,str(ROOT/'.agents/skills/smc-work-router/scripts/test_work_facts.py'),'-v'])
  run('risk precedence',[sys.executable,str(ROOT/'.agents/skills/smc-plan-review/scripts/selftest.py')])
  run('domain semantic frontend',[sys.executable,str(ROOT/'.agents/skills/smc-frontend-preplan/scripts/selftest.py')])
  run('benchmark synthetic',[sys.executable,str(ROOT/'acceptance/run_benchmark.py'),'--selftest'])
  run('pilot matrix',[sys.executable,str(ROOT/'acceptance/pilot/run_pilot.py'),'--validate-matrix'])
  run('acceptance G01-G96',[sys.executable,str(ROOT/'acceptance/run_acceptance.py')])
  run('context engine',[sys.executable,str(ROOT/'tests/test_context_engine.py'),'-v'])
  # Frontend adapters present
  for name in ('react-web','react-electron','vue3-web','nextjs','nuxt','react-native','generic'):
   if not (ROOT/'frontend-adapters'/name/'adapter.json').is_file():raise ValueError('FRONTEND_ADAPTER_MISSING: '+name)
  if not (ROOT/'consumer-bootstrap'/'frontend_audit.py').is_file():raise ValueError('FRONTEND_AUDIT_MISSING')
  if not (ROOT/'context-engine'/'work_scope.py').is_file():raise ValueError('CONTEXT_ENGINE_MISSING')
  # Telemetry completeness synthetic (dispatch+result pair)
  with tempfile.TemporaryDirectory(prefix='ges-telem-') as td:
   plan=Path(td)/'telem.plan.md'
   plan.write_text('---\nplan_id: telem-syn\nplan_contract: smc.plan.v3.5\n---\n# T\n',encoding='utf-8')
   (Path(td)/'.agents').mkdir()
   rm=ROOT/'.agents/skills/smc-plan-delivery/scripts/runtime_metrics.py'
   run('telemetry dispatch',[sys.executable,str(rm),'dispatch',str(plan),'--todo','T1','--requested-tier','default','--dispatch-id','d1','--agent','a'])
   run('telemetry result',[sys.executable,str(rm),'result',str(plan),'--dispatch-id','d1','--actual-tier','default','--provider','syn','--model','m','--outcome','ok','--prompt-tokens','1','--completion-tokens','1','--cache-read-tokens','0','--cache-write-tokens','0','--latency-ms','1'])
   run('telemetry summarize',[sys.executable,str(rm),'summarize',str(plan),'--json'])
  run('package v5 integration regressions',[sys.executable,str(ROOT/'tests/test_package_v500.py'),'-v'])
  run('consumer bootstrap audit',[sys.executable,str(ROOT/'tests/test_consumer_audit.py'),'-v'])
  run('consumer bootstrap remediation',[sys.executable,str(ROOT/'tests/test_consumer_remediation.py'),'-v'])
  run('consumer bootstrap validation',[sys.executable,str(ROOT/'tests/test_consumer_validation.py'),'-v'])
  run('context engine',[sys.executable,str(ROOT/'context-engine/run_selftest.py')])
  sys.path.insert(0,str(ROOT/'tests'))
  from test_package_v500 import fixture
  with tempfile.TemporaryDirectory(prefix='ges-v5-consumer-') as td:
   project=Path(td);fixture(project)
   run('consumer install dry run',[sys.executable,str(ROOT/'install.py'),str(project),'--profile','generic'])
   run('consumer actual install',[sys.executable,str(ROOT/'install.py'),str(project),'--profile','generic','--apply'])
   lock=json.loads((project/'.smc/ges-install-lock.json').read_text(encoding='utf-8'))
   if lock['bundle']!='6.0.0':raise ValueError('INSTALL_LOCK_VERSION_INVALID')
   if lock.get('schema')!='smc.ges.install-lock.v2':raise ValueError('INSTALL_LOCK_V2_INVALID')
   if 'release_identity' not in lock or 'owned_files' not in lock:raise ValueError('INSTALL_RELEASE_IDENTITY_INVALID')
   # raw-bytes identity: must match PACKAGE-MANIFEST.json file digest, not reserialized object
   import hashlib as _hl
   manifest_path=ROOT/'PACKAGE-MANIFEST.json'
   byte_sha=installer.base.sha256(manifest_path)
   if lock['release_identity'].get('package_manifest_sha256')!=byte_sha:raise ValueError('INSTALL_MANIFEST_BYTE_DIGEST_MISMATCH')
   reserialized=_hl.sha256(json.dumps(json.loads(manifest_path.read_text(encoding='utf-8')),sort_keys=True,separators=(',',':')).encode()).hexdigest()
   if reserialized==byte_sha:
    pass  # rare but allowed if bytes already canonical
   receipt_path=project/'.smc'/'ges-install-receipt.json'
   receipts=list((project/'.smc'/'ges-install-receipts').glob('*.json')) if (project/'.smc'/'ges-install-receipts').is_dir() else []
   if not receipts and not receipt_path.is_file():raise ValueError('INSTALL_RECEIPT_INVALID')
   if 'install_receipt_sha256' not in lock or 'install_receipt_path' not in lock:raise ValueError('INSTALL_RECEIPT_HASH_MISMATCH')
   rp=project/lock['install_receipt_path']
   if not rp.is_file():raise ValueError('INSTALL_RECEIPT_INVALID')
   if lock['install_receipt_sha256']!='sha256:'+(installer.base.sha256(rp) or ''):raise ValueError('INSTALL_RECEIPT_HASH_MISMATCH')
   receipt=json.loads(rp.read_text(encoding='utf-8'))
   if receipt.get('schema')!='smc.ges.install-receipt.v1':raise ValueError('INSTALL_RECEIPT_INVALID')
   if 'release_identity' not in receipt or 'managed_file_set_sha256' not in receipt:raise ValueError('INSTALL_RECEIPT_INVALID')
   for req in ('install_id','policy_digest','validation','stale_reconciliation','finalized_at','domains','profile'):
    if req not in receipt:raise ValueError('INSTALL_RECEIPT_INVALID: missing '+req)
   if receipt.get('release_identity',{}).get('source_tree_dirty') and receipt.get('release_identity',{}).get('release_eligible') is not False:
    raise ValueError('INSTALL_SOURCE_DIRTY_NOT_RELEASE_ELIGIBLE')
   for p in (project/'.agents/skills').rglob('*'):
    if p.is_file() and '__pycache__' not in p.parts:
     mirror=project/'.cursor/skills'/p.relative_to(project/'.agents/skills')
     # Consumer-owned skills are intentionally not package-managed.
     if p.relative_to(project/'.agents/skills').parts[0] in installer.base.managed_skills(profile,selected) and (not mirror.is_file() or p.read_bytes()!=mirror.read_bytes()):raise ValueError('MIRROR_DRIFT: '+str(p))
   run('consumer rollback',[sys.executable,str(ROOT/'rollback.py'),str(project),'--apply'])
   if (project/'.agents/skills/smc-plan-delivery/SKILL.md').exists():raise ValueError('ROLLBACK_LEFTOVER')
  print('PACKAGE VALIDATION PASS — GES 6.0.0; context-engine + registered regressions + real fixture install/rollback',flush=True)
  return 0
 except (ValueError,OSError,KeyError,SyntaxError) as exc:
  print('PACKAGE VALIDATION FAILED:',exc,file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
