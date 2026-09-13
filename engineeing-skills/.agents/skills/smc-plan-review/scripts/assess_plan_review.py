#!/usr/bin/env python3
"""GES 5 adaptive semantic Plan review router.

Public stdout remains NOT_REQUIRED|REQUIRED. --json exposes NONE|DELTA|FULL and reasons.
"""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
DELIVERY=Path(__file__).resolve().parents[2]/'smc-plan-delivery'/'scripts'
if str(DELIVERY) not in sys.path:sys.path.insert(0,str(DELIVERY))
from common import parse_top_level_frontmatter, semantic_plan_sha256
from review_record import latest_status
HARD=(r'\b(LIVE|FAULT|EXTERNAL)\b',r'auth|authentication|authorization|trust boundary|security boundary',r'schema\s+migration|data\s+migration',r'public\s+(api|contract)|protocol change',r'concurr|idempot|lease|race|deadlock',r'new\s+(service|store|client|protocol|dependency)')
def classify(plan:Path)->dict:
 text=plan.read_text(encoding='utf-8');meta=parse_top_level_frontmatter(text);profile=meta.get('governance_profile','FULL').upper();hard=[p for p in HARD if re.search(p,text,re.I)]
 status,rec=latest_status(plan,'plan')
 reasons=[]
 if rec and str(rec.get('verdict','')).upper()!='PASS':depth='FULL';reasons.append('latest prior review is unresolved, regardless of freshness')
 elif status=='FRESH_PASS':depth='NONE';reasons.append('fresh content-bound Plan review already PASS')
 elif hard:depth='FULL';reasons.extend('hard-risk:'+x for x in hard)
 elif status=='STALE' and rec and str(rec.get('verdict','')).upper()=='PASS':depth='DELTA';reasons.append('prior PASS exists but semantic Plan changed')
 elif status.startswith('FRESH_') and status!='FRESH_PASS':depth='FULL';reasons.append('prior review verdict was not PASS')
 elif meta.get('acceptance_contract')=='smc.acceptance.v1':depth='FULL';reasons.append('first acceptance-governed review requires actual semantic review')
 elif profile=='LEAN' or meta.get('plan_contract') in {'smc.plan.v3.3','smc.plan.v3.4','smc.plan.v3.5','smc.plan.v3.6'}:depth='NONE';reasons.append('low-risk Plan with no prior blocking semantic trigger')
 else:depth='FULL';reasons.append('FULL/unknown Plan fails closed to full semantic review')
 public='NOT_REQUIRED' if depth=='NONE' else 'REQUIRED'
 return {'schema':'smc.plan.review-route.v2','plan':str(plan),'plan_sha256':semantic_plan_sha256(plan),'governance_profile':profile,'route':public,'depth':depth,'reasons':reasons,'hard_signals':hard}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('--json',action='store_true');a=ap.parse_args();p=a.plan.resolve()
 if not p.is_file():print(f'PLAN_NOT_FOUND: {p}',file=sys.stderr);return 2
 o=classify(p);print(json.dumps(o,ensure_ascii=False,indent=2,sort_keys=True) if a.json else o['route']);return 0
if __name__=='__main__':raise SystemExit(main())
