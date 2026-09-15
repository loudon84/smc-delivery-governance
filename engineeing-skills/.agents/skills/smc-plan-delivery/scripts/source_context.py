#!/usr/bin/env python3
"""Content-bound Source Context Capsule cache for GES Harness workers."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from common import atomic_write,find_repo_root,plan_id,utc_now

def key(path,symbol):return hashlib.sha256((path+'#'+symbol).encode()).hexdigest()[:20]
def cdir(plan):return find_repo_root(plan)/'.smc/runs'/plan_id(plan)/'source-context'
def content_sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
def capsule_path(plan,path,symbol):return cdir(plan)/f'{key(path,symbol)}.json'
def capture(plan,path,symbol='',summary=''):
 repo=find_repo_root(plan);rel=Path(path).as_posix();p=(repo/rel).resolve()
 try:p.relative_to(repo.resolve())
 except ValueError:raise ValueError('SOURCE_CONTEXT_OUTSIDE_REPO')
 if not p.is_file():raise ValueError(f'SOURCE_CONTEXT_FILE_MISSING: {rel}')
 cap={'schema':'smc.execution.source-context.v1','plan_id':plan_id(plan),'path':rel,'symbol':symbol,'content_sha256':content_sha(p),'summary':re.sub(r'\s+',' ',summary.strip())[:6000],'captured_at':utc_now(),'working_memory_only':True}
 out=capsule_path(plan,rel,symbol);atomic_write(out,json.dumps(cap,ensure_ascii=False,indent=2,sort_keys=True)+'\n');return out,cap
def get(plan,path,symbol=''):
 repo=find_repo_root(plan);rel=Path(path).as_posix();out=capsule_path(plan,rel,symbol)
 path_key=key(rel,symbol)
 try:
  if not out.is_file():raise ValueError('SOURCE_CONTEXT_MISSING')
  cap=json.loads(out.read_text(encoding='utf-8'));cur=content_sha(repo/rel)
  if cap.get('content_sha256')!=cur:raise ValueError('SOURCE_CONTEXT_STALE')
  try:
   from runtime_metrics import cache_hit
   cache_hit(plan,path_key)
  except Exception:
   pass
  _bridge_capsule(plan,rel,symbol,cap,state='hit')
  return out,cap
 except ValueError:
  try:
   from runtime_metrics import cache_miss
   cache_miss(plan,path_key)
  except Exception:
   pass
  _bridge_capsule(plan,rel,symbol,None,state='miss')
  raise


def _bridge_capsule(plan,rel,symbol,cap,state):
 """Bridge plan-scoped source capsules into work-item CapsuleStore accounting."""
 try:
  import sys
  from pathlib import Path as _P
  ctx=_P(__file__).resolve().parents[3]/'context-engine'
  if not ctx.is_dir():
   ctx=_P(__file__).resolve().parents[4]/'context-engine'
  if str(ctx) not in sys.path:
   sys.path.insert(0,str(ctx))
  from context_cache import CapsuleStore
  from budget_controller import policy_digest
  store=CapsuleStore(repo=find_repo_root(plan),work_item_id=plan_id(plan))
  sha=(cap or {}).get('content_sha256') or ''
  key_args=dict(repo_identity=str(find_repo_root(plan)),artifact_kind='SOURCE',scope_digest=plan_id(plan),identity=rel,content_sha256=sha,extractor_version='1.0.0',policy_digest=policy_digest())
  if state=='hit':
   store.get_capsule(**key_args)
  else:
   store.put_capsule(**key_args,value={'summary':(cap or {}).get('summary') or rel,'tokens':200},persist=True)
 except Exception:
  pass
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True)
 for n in ('capture','get'):
  p=sub.add_parser(n);p.add_argument('plan',type=Path);p.add_argument('--path',required=True);p.add_argument('--symbol',default='');p.add_argument('--json',action='store_true');p.add_argument('--summary',default='')
 a=ap.parse_args()
 try:
  out,cap=(capture(a.plan.resolve(),a.path,a.symbol,a.summary) if a.cmd=='capture' else get(a.plan.resolve(),a.path,a.symbol));print(json.dumps({'capsule':str(out),**cap},ensure_ascii=False,indent=2) if a.json else out);return 0
 except ValueError as e:print(str(e));return 2
if __name__=='__main__':raise SystemExit(main())
