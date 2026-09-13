#!/usr/bin/env python3
"""GES Plan v3.7 validator: v3.6 invariants + adaptive governance profile."""
from __future__ import annotations
import argparse,importlib.util,json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
DELIVERY=HERE.parents[1]/'smc-plan-delivery'/'scripts';sys.path.insert(0,str(DELIVERY))
from acceptance import validate_contract as validate_acceptance
from test_assets import validate_plan as validate_test_assets
from validate_plan_v33 import validate_plan
from common import parse_top_level_frontmatter

HARD=(r'new\s+(service|store|client|protocol)',r'auth|trust boundary|security boundary',r'schema\s+migration|data\s+migration',r'concurr|idempot|lease',r'public\s+(api|contract)|protocol change',r'new external dependency')
def repo_root(plan):
 for c in (plan.resolve().parent,*plan.resolve().parents):
  if (c/'.agents').is_dir() or (c/'.git').exists():return c
 raise ValueError('DOMAIN_REPO_ROOT_NOT_FOUND')
def domain_module(plan):
 t=repo_root(plan)/'.agents/ges/domain-runtime/domain_runtime.py'
 if not t.is_file():raise ValueError(f'DOMAIN_RUNTIME_MISSING: {t}')
 s=importlib.util.spec_from_file_location('ges_domain_runtime_v37',t);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def profile_errors(plan):
 text=plan.read_text(encoding='utf-8');meta=parse_top_level_frontmatter(text);errs=[];profile=meta.get('governance_profile','').upper()
 if profile not in {'LEAN','FULL'}:errs.append({'code':'PLAN_GOVERNANCE_PROFILE_INVALID','detail':profile or 'missing'});return errs
 if profile=='LEAN':
  hits=[p for p in HARD if re.search(p,text,re.I)]
  if hits:errs.append({'code':'PLAN_LEAN_FULL_REQUIRED','detail':', '.join(hits)})
 return errs

def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('--json',action='store_true');a=ap.parse_args();p=a.plan.resolve()
 if not p.is_file():
  out={'valid':False,'plan':str(p),'errors':[{'code':'PLAN_NOT_FOUND','detail':str(p)}]};print(json.dumps(out,indent=2) if a.json else f'PLAN_NOT_FOUND: {p}');return 2
 errors=validate_plan(p,'smc.plan.v3.7');errors.extend(validate_acceptance(p));errors.extend(validate_test_assets(p));errors.extend(profile_errors(p))
 try:errors.extend(domain_module(p).validate_plan(p))
 except ValueError as e:errors.append({'code':str(e).split(':',1)[0],'detail':str(e)})
 out={'valid':not errors,'plan':str(p),'errors':errors}
 if a.json:print(json.dumps(out,ensure_ascii=False,indent=2))
 elif errors:print('\n'.join(f"{x['code']}: {x['detail']}" for x in errors),file=sys.stderr)
 else:print('Plan v3.7 validation passed')
 return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
