#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SKILLS=ROOT/'.agents/skills'
PACKAGE_VERSION='4.3.1'
EXPECTED={
 'smc-plan-delivery':'1.3.0',
 'smc-plan-from-approved-prd-ponytail':'3.7.0',
 'smc-plan-validator':'1.6.0',
 'smc-plan-review':'1.1.0',
 'executing-plans':'4.2.0',
 'subagent-driven-development':'4.2.0',
 'smc-roadmap':'1.2.0',
 'using-superpowers':'4.3.1',
 'smc-architecture-decision':'1.0.0',
 'smc-architecture-review':'1.0.0',
 'smc-prd-grounding':'4.0.0',
 'smc-prd-review':'4.0.0',
 'smc-prd-converge':'3.0.0',
 'smc-frontend-engineering':'1.0.0',
 'smc-frontend-review':'1.0.0',
 'smc-frontend-visual-verification':'1.0.0',
}
REQUIRED=[
 'core/manifest.json','domain-runtime/domain_runtime.py','domain-packs/registry.json','domain-packs/frontend/pack.json','domain-packs/frontend/activation.json','domain-packs/frontend/policy-lock.json',
 'consumers/generic.json','consumers/nodeskclaw.json','consumers/smc-copilot-work.json','install_v430.py',
 '.agents/skills/smc-plan-validator/scripts/validate_plan_v35.py','.agents/skills/smc-plan-validator/scripts/validate_plan_v36.py','.agents/skills/smc-plan-validator/scripts/validate_plan_current.py','.agents/skills/smc-plan-from-approved-prd-ponytail/scripts/create_plan_seed_v35.py','.agents/skills/smc-plan-from-approved-prd-ponytail/scripts/create_plan_seed_v36.py','.agents/skills/smc-plan-delivery/scripts/domain_hooks.py','.agents/skills/smc-plan-delivery/scripts/contract_resolver.py','.agents/skills/smc-plan-delivery/scripts/test_assets.py','.agents/skills/smc-plan-delivery/references/test-asset-contract.md',
]
FORBIDDEN_DOMAIN_IDS=('frontend','backend','electron','mobile','data')
CORE_GENERIC_FILES=('domain-runtime/domain_runtime.py','.agents/skills/smc-plan-delivery/scripts/domain_hooks.py','install_v430.py')

def fm(path:Path):
    lines=path.read_text(encoding='utf-8').splitlines();out={}
    if not lines or lines[0].strip()!='---':raise ValueError('missing frontmatter')
    for line in lines[1:]:
        if line.strip()=='---':break
        if ':' in line:
            k,v=line.split(':',1);out[k.strip()]=v.strip().strip('"\'')
    return out

def run(cmd,cwd,capture=False):
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';env.setdefault('PYTHONUTF8','1')
    return subprocess.run(cmd,cwd=cwd,text=True,encoding='utf-8',errors='replace',capture_output=capture,env=env)

def copy_tree(src:Path,dst:Path):
    if not src.is_dir():return
    for p in src.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
        rel=p.relative_to(src);out=dst/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)

def load_runtime(path:Path):
    spec=importlib.util.spec_from_file_location('domain_runtime_test',path)
    if spec is None or spec.loader is None:raise RuntimeError('cannot import domain runtime')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def framework_tests(errors):
    # Production reference pack activation.
    with tempfile.TemporaryDirectory() as td:
        repo=Path(td)/'repo';(repo/'.git').mkdir(parents=True);ges=repo/'.agents/ges';
        copy_tree(ROOT/'domain-runtime',ges/'domain-runtime');copy_tree(ROOT/'domain-packs',ges/'domain-packs')
        shutil.copy2(ROOT/'consumers/smc-copilot-work.json',ges/'profile.json')
        plan=repo/'x.plan.md';plan.write_text('''---\nplan_contract: smc.plan.v3.5\n---\n## Change Matrix\n\n| Change ID | File / Symbol | Kind | Action | Existing Owner | Todo Owner | Target State | PRD Capability | New File? |\n|---|---|---|---|---|---|---|---|---|\n| C01 | `src/renderer/src/screens/X.tsx#X` | PROD | MODIFY | x | T1 | RENDERER_UI | x | no |\n| C02 | `src/main/x.ts#x` | PROD | MODIFY | x | T2 | MAIN | x | no |\n''',encoding='utf-8')
        mod=load_runtime(ges/'domain-runtime/domain_runtime.py');resolved=mod.resolve(plan)
        rows={x['id']:x for x in resolved['domains']}
        if len(rows)!=1 or next(iter(rows.values()))['trigger_changes']!=['C01']:errors.append('reference domain activation did not isolate renderer change')
        providers=mod.providers(plan,'engineering')
        if len(providers)!=1:errors.append('reference engineering provider not resolved')

    # Extension proof: a new domain is registered entirely as data; Core files are unchanged.
    with tempfile.TemporaryDirectory() as td:
        repo=Path(td)/'repo';(repo/'.git').mkdir(parents=True);ges=repo/'.agents/ges';copy_tree(ROOT/'domain-runtime',ges/'domain-runtime')
        packs=ges/'domain-packs';(packs/'fixture').mkdir(parents=True)
        (packs/'registry.json').write_text(json.dumps({'schema':'smc.ges.domain-registry.v1','packs':{'fixture':{'path':'fixture/pack.json','status':'test'}}}),encoding='utf-8')
        (packs/'fixture/pack.json').write_text(json.dumps({'schema':'smc.ges.domain-pack.v1','id':'fixture','version':'1.0.0','activation_rules':'activation.json','capabilities':{'engineering':{'skill':'fixture-engineering'}}}),encoding='utf-8')
        (packs/'fixture/activation.json').write_text(json.dumps({'schema':'smc.ges.domain-activation-rules.v1','extensions':['.fixture'],'exclude_globs':[]}),encoding='utf-8')
        (ges/'profile.json').write_text(json.dumps({'schema':'smc.ges.consumer-profile.v2','id':'fixture-consumer','version':'1.0.0','domains':{'fixture':{'activation':'auto'}}}),encoding='utf-8')
        plan=repo/'fixture.plan.md';plan.write_text('''---\nplan_contract: smc.plan.v3.5\n---\n## Change Matrix\n\n| Change ID | File / Symbol | Kind | Action | Existing Owner | Todo Owner | Target State | PRD Capability | New File? |\n|---|---|---|---|---|---|---|---|---|\n| C01 | `src/a.fixture#x` | PROD | MODIFY | x | T1 | x | x | no |\n''',encoding='utf-8')
        mod=load_runtime(ges/'domain-runtime/domain_runtime.py');r=mod.resolve(plan)
        if r['domains'][0]['status']!='REQUIRED':errors.append('fixture domain was not activated without Core change')
        p=mod.providers(plan,'engineering')
        if not p or p[0]['skill']!='fixture-engineering':errors.append('fixture domain provider did not load generically')

def installer_smoke(errors):
    with tempfile.TemporaryDirectory() as td:
        project=Path(td)/'repo';project.mkdir();subprocess.run(['git','init','-q',str(project)],check=True)
        (project/'.agents/skills/code-review-and-quality').mkdir(parents=True);(project/'.agents/skills/code-review-and-quality/SKILL.md').write_text('# local review\n',encoding='utf-8')
        (project/'.agents/skills/verification-before-completion').mkdir(parents=True);(project/'.agents/skills/verification-before-completion/SKILL.md').write_text('# local verification\n',encoding='utf-8')
        legacy=project/'.agents/skills/smc-plan-validator/scripts/validate_plan.py';legacy.parent.mkdir(parents=True);legacy.write_text('def validate_plan(path): return []\n',encoding='utf-8')
        (project/'.cursor/skills').mkdir(parents=True);(project/'package.json').write_text('{}\n',encoding='utf-8')
        result=run([sys.executable,str(ROOT/'install_v430.py'),str(project),'--profile','smc-copilot-work','--apply','--skip-project-validator'],ROOT,capture=True)
        if result.returncode:errors.append('v4.3 installer smoke failed: '+(result.stdout+result.stderr).replace('\n',' | '));return
        for rel in ('.agents/ges/profile.json','.agents/ges/domain-runtime/domain_runtime.py','.agents/ges/domain-packs/frontend/pack.json','.agents/skills/smc-frontend-engineering/SKILL.md','.agents/skills/smc-plan-delivery/scripts/domain_hooks.py'):
            if not (project/rel).is_file():errors.append(f'installer smoke missing {rel}')
        if (project/'.agents/skills/code-review-and-quality/SKILL.md').read_text(encoding='utf-8')!='# local review\n':errors.append('consumer-local review skill was overwritten')

def main():
    errors=[]
    for skill,version in EXPECTED.items():
        path=SKILLS/skill/'SKILL.md'
        if not path.is_file():errors.append(f'{skill}: missing');continue
        try:meta=fm(path)
        except Exception as exc:errors.append(f'{skill}: {exc}');continue
        if meta.get('name')!=skill:errors.append(f'{skill}: name mismatch')
        if meta.get('version')!=version:errors.append(f'{skill}: version={meta.get("version")} expected={version}')
    for rel in REQUIRED:
        if not (ROOT/rel).is_file():errors.append(f'required v4.3 file missing: {rel}')
    for rel in CORE_GENERIC_FILES:
        text=(ROOT/rel).read_text(encoding='utf-8').lower() if (ROOT/rel).is_file() else ''
        for token in FORBIDDEN_DOMAIN_IDS:
            # Domain ids may appear only in data/reference packs, never generic Core runtime code.
            if re.search(rf"['\"]{re.escape(token)}['\"]",text):errors.append(f'Core hardcodes domain id {token}: {rel}')
    for p in ROOT.rglob('*.py'):
        if '__pycache__' in p.parts:continue
        try:compile(p.read_text(encoding='utf-8'),str(p),'exec')
        except Exception as exc:errors.append(f'compile failed {p.relative_to(ROOT)}: {exc}')
    framework_tests(errors)
    selftest=run([sys.executable,str(SKILLS/'smc-frontend-review/scripts/selftest.py')],ROOT,capture=True)
    if selftest.returncode:errors.append('frontend domain selftest failed: '+(selftest.stdout+selftest.stderr).replace('\n',' | '))
    delivery=run([sys.executable,str(SKILLS/'smc-plan-delivery/scripts/run_selftest.py')],ROOT,capture=True)
    if delivery.returncode:errors.append('delivery self-test failed: '+(delivery.stdout+delivery.stderr).replace('\n',' | '))
    roadmap=run([sys.executable,str(SKILLS/'smc-roadmap/scripts/test_roadmap_v11.py'),'-q'],ROOT,capture=True)
    if roadmap.returncode:errors.append('roadmap self-test failed: '+(roadmap.stdout+roadmap.stderr).replace('\n',' | '))
    installer_smoke(errors)
    if errors:
        print('PACKAGE VALIDATION FAILED',file=sys.stderr);print('\n'.join(errors),file=sys.stderr);return 1
    print(f'PACKAGE VALIDATION PASS — GES {PACKAGE_VERSION}; {len(EXPECTED)} governed skills; Domain Framework fixture-extension proof PASS; frontend pack PASS; installer smoke PASS')
    return 0
if __name__=='__main__':raise SystemExit(main())
