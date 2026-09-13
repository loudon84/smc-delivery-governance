"""Package integration fixtures; consumer legacy-validator stub tests adapter contract, not business validation."""
import importlib.util,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import install_v500 as installer
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
domain=module('domain_runtime_test',ROOT/'domain-runtime/domain_runtime.py')
def write(root,rel,text):
 p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8');return p
def fixture(root):
 subprocess.run(['git','init','-q',str(root)],check=True)
 write(root,'AGENTS.md','# Project policy\nPreserve existing ownership.\n')
 for skill in ('code-review-and-quality','verification-before-completion'):write(root,'.agents/skills/'+skill+'/SKILL.md','# consumer-owned\n')
 write(root,'.agents/skills/smc-plan-validator/scripts/validate_plan.py',"def validate_plan(path):\n    assert 'plan_contract: smc.plan.v3.2' in path.read_text(encoding='utf-8'), 'legacy adapter received wrong contract'\n    return []\n")
 (root/'.cursor/skills').mkdir(parents=True)
def install_fixture(root,legacy=False):
 fixture(root)
 profile=json.loads((ROOT/'consumers/generic.json').read_text(encoding='utf-8'))
 if legacy:
  profile={'schema':'smc.ges.consumer-profile.v2','id':'legacy','version':'1.0.0','domains':{'frontend':{'activation':'auto'}},'mirror_policy':'declared-managed-set'}
  shutil.copytree(ROOT/'domain-packs-v1',root/'.agents/ges/domain-packs')
 else:shutil.copytree(ROOT/'domain-packs',root/'.agents/ges/domain-packs')
 write(root,'.agents/ges/profile.json',json.dumps(profile))
 shutil.copytree(ROOT/'domain-runtime',root/'.agents/ges/domain-runtime')
 shutil.copytree(ROOT/'.agents/skills',root/'.agents/skills',dirs_exist_ok=True)
 shutil.copytree(ROOT/'project-integration',root,dirs_exist_ok=True)
 return profile
class PackageV5Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.r=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def test_v1_policy_digest_preserved_on_update(self):
  profile=install_fixture(self.r,legacy=True)
  before=domain.policy_digest(domain.load_context(self.r))
  _,loaded=installer.resolve_profile(self.r,None);_,packs=installer.pack_context(loaded)
  self.assertEqual('smc.ges.domain-pack.v1',packs['frontend'][1]['schema'])
  backup=self.r/'.smc/backup';backup.mkdir(parents=True)
  installer.install_metadata(self.r,loaded,packs,backup,{})
  self.assertEqual(before,domain.policy_digest(domain.load_context(self.r)))
 def test_v3_project_policy_is_digest_bound(self):
  install_fixture(self.r)
  before=domain.policy_digest(domain.load_context(self.r))
  write(self.r,'AGENTS.md','# Changed project policy\n')
  self.assertNotEqual(before,domain.policy_digest(domain.load_context(self.r)))
 def test_domain_activation_vue_backend_ops(self):
  install_fixture(self.r)
  plan=write(self.r,'demo.plan.md','---\nplan_contract: smc.plan.v3.7\n---\n## Change Matrix\n\n| Change ID | File / Symbol |\n|---|---|\n| C01 | src/app.vue |\n| C02 | src/api/handler.ts |\n| C03 | Dockerfile |\n')
  result=domain.resolve(plan)
  self.assertEqual('smc.ges.domain-activation.v2',result['schema'])
  self.assertEqual({'frontend':['C01'],'backend':['C02'],'ops':['C03']},{r['id']:r['trigger_changes'] for r in result['domains']})
  self.assertEqual(3,len(domain.providers(plan,'preplan')))
  self.assertTrue(domain.validate_preplan(plan))
 def test_malformed_domain_row_is_not_skipped(self):
  sys.path.insert(0,str(ROOT/'domain-runtime'))
  from domain_table import validate_table
  plan=write(self.r,'prd.md','## Design\n\n| Change ID | Owner |\n|---|---|\n| C01 | existing |\n| C02 |\n')
  self.assertTrue(validate_table(plan,'Design',['Change ID','Owner'],'TEST'))
 def test_v37_seed_stable_dispatch_and_legacy_bridge(self):
  install_fixture(self.r)
  prd=write(self.r,'prd.md','---\nstatus: APPROVED\nreview_verdict: PASS\napproved_at: now\nwork_item_id: RM-02\nversion: 1.0\nsource_revision: RM-02@1.0\ngovernance_profile: FULL\ngrounded_commit: abcdef01234567\n---\n'+''.join('## '+h+'\n\nGrounded existing scope.\n\n' for h in ('Objective','Out of Scope','Production Owner','Source Anchors'))+'## Change Classification\n\n| Change ID | Capability | Action | Source Anchor |\n|---|---|---|---|\n| C01 | Existing text | MODIFY | docs/a.md |\n\n## Acceptance Criteria\n\n1. text changes\n\n## Definition of Done\n\n1. checks pass\n')
  seed=self.r/'.agents/skills/smc-plan-from-approved-prd-ponytail/scripts/create_plan_seed.py'
  out=self.r/'.cursor/plans/rm02.plan.md'
  result=subprocess.run([sys.executable,str(seed),str(prd),str(out),'--plan-id','RM-02'],capture_output=True,text=True,encoding='utf-8')
  self.assertEqual(0,result.returncode,result.stdout+result.stderr)
  self.assertIn('plan_contract: smc.plan.v3.7',out.read_text(encoding='utf-8'))
  # Seeds intentionally contain placeholders and must fail static gates.
  result=subprocess.run([sys.executable,str(self.r/'tools/agent-skills/validate_plan.py'),str(out),'--json'],capture_output=True,text=True,encoding='utf-8')
  self.assertNotEqual(0,result.returncode)
  self.assertNotIn('legacy adapter received wrong contract',result.stderr)
  self.assertNotIn('ModuleNotFoundError',result.stderr)
  payload=json.loads(result.stdout)
  self.assertFalse(payload['valid'])
 def test_rollback_restores_files_after_failed_validation(self):
  fixture(self.r);before={p.relative_to(self.r).as_posix():p.read_bytes() for p in self.r.rglob('*') if p.is_file() and '.git' not in p.parts}
  # Fault injection specifically tests the real transaction writer/restore, not validation quality.
  with patch.object(sys,'argv',['install.py',str(self.r),'--apply']),patch.object(installer.base,'validation_commands',return_value=[('injected failure',[sys.executable,'-c','raise SystemExit(7)'])]):
   self.assertEqual(1,installer.main())
  after={p.relative_to(self.r).as_posix():p.read_bytes() for p in self.r.rglob('*') if p.is_file() and '.git' not in p.parts and '.smc' not in p.parts}
  self.assertEqual(before,after)
 def test_install_lock_v2_fields(self):
  install_fixture(self.r)
  _,loaded=installer.resolve_profile(self.r,None);_,packs=installer.pack_context(loaded)
  backup=self.r/'.smc/backup';backup.mkdir(parents=True)
  lock=installer.build_install_lock(self.r,loaded,packs,{},backup)
  self.assertEqual('smc.ges.install-lock.v2',lock['schema'])
  self.assertIn('release_identity',lock);self.assertIn('owned_files',lock)
  self.assertIn('source_tree_dirty',lock['release_identity'])
  self.assertIn('install_receipt_path',lock);self.assertIn('install_receipt_sha256',lock)
  rp=self.r/lock['install_receipt_path']
  self.assertTrue(rp.is_file())
  self.assertEqual(lock['install_receipt_sha256'],'sha256:'+(installer.base.sha256(rp) or ''))
  receipt=json.loads(rp.read_text(encoding='utf-8'))
  self.assertEqual('smc.ges.install-receipt.v1',receipt['schema'])
  for key in ('install_id','managed_file_set_sha256','policy_digest','validation','stale_reconciliation','finalized_at'):
   self.assertIn(key,receipt)
  if receipt['release_identity'].get('source_tree_dirty'):
   self.assertIs(receipt['release_identity'].get('release_eligible'),False)
 def test_stale_reconciliation_v1_skip(self):
  write(self.r,'.smc/ges-install-lock.json',json.dumps({'schema':'smc.ges.install-lock.v1'}))
  notes=installer.reconcile_stale_owned_files(self.r,self.r/'.smc/backup',{},['x'])
  self.assertEqual(['INSTALL_LEGACY_RECONCILIATION_SKIPPED'],notes)
 def test_stale_reconciliation_modified_blocks(self):
  path='.agents/skills/smc-plan-delivery/SKILL.md'
  write(self.r,path,'local-edit\n')
  write(self.r,'.smc/ges-install-lock.json',json.dumps({'schema':'smc.ges.install-lock.v2','owned_files':[{'path':path,'installed_sha256':'00'}]}))
  with self.assertRaisesRegex(RuntimeError,'INSTALL_STALE_OWNED_FILE_MODIFIED'):
   installer.reconcile_stale_owned_files(self.r,self.r/'.smc/backup',{},['other'])
if __name__=='__main__':unittest.main()
