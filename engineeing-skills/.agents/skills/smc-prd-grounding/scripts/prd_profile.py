#!/usr/bin/env python3
"""Validate GES 5 PRD governance profile and clarification readiness."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
PROFILES={'LEAN','FULL'}
HARD=(r'new\s+(service|store|client|protocol)',r'auth|trust boundary|security boundary',r'schema\s+migration|data\s+migration',r'concurr|idempot|lease',r'public\s+(api|contract)|protocol change',r'new external dependency')

def fm(t):
 out={};lines=t.splitlines()
 if not lines or lines[0].strip()!='---':return out
 for line in lines[1:]:
  if line.strip()=='---':break
  if line and not line[0].isspace() and ':' in line:
   k,v=line.split(':',1);out[k.strip()]=v.strip().strip('"\'')
 return out

def section(t,h):
 m=re.search(rf'^##\s+{re.escape(h)}\s*$\n?(.*?)(?=^##\s+|\Z)',t,re.M|re.S);return m.group(1).strip() if m else ''
def table(body):
 lines=[x.strip() for x in body.splitlines() if x.strip().startswith('|')]
 if len(lines)<2:return []
 hdr=[x.strip() for x in lines[0].strip('|').split('|')]
 rows=[]
 for raw in lines[2:]:
  vals=[x.strip() for x in raw.strip('|').split('|')]
  if len(vals)==len(hdr):rows.append(dict(zip(hdr,vals)))
 return rows

def scan(path):
 t=path.read_text(encoding='utf-8');meta=fm(t);profile=meta.get('governance_profile','').upper();errors=[];warnings=[]
 if profile not in PROFILES:errors.append({'code':'PRD_GOVERNANCE_PROFILE_INVALID','detail':profile or 'missing'})
 for heading in ('Objective','Out of Scope','Production Owner','Change Classification','Acceptance Criteria','Source Anchors'):
  if not section(t,heading):errors.append({'code':'PRD_MINIMUM_SECTION_MISSING','detail':heading})
 if not re.fullmatch(r'[0-9a-fA-F]{7,64}',meta.get('grounded_commit','')):errors.append({'code':'PRD_GROUNDED_COMMIT_MISSING','detail':'grounded_commit'})
 if meta.get('previous_governance_profile','').upper()=='FULL' and profile!='FULL':errors.append({'code':'PRD_PROFILE_DOWNGRADE_FORBIDDEN','detail':profile})
 if profile=='LEAN':
  router=Path(__file__).resolve().parents[2]/'using-superpowers/scripts'
  sys.path.insert(0,str(router))
  from work_router import route
  try:
   facts=json.loads(section(t,'Routing Facts').removeprefix('```json').removesuffix('```').strip())
   if route(facts).get('governance_profile')=='FULL':errors.append({'code':'PRD_LEAN_FULL_REQUIRED','detail':'routing facts'})
  except (ValueError,TypeError):errors.append({'code':'PRD_ROUTING_FACTS_INVALID','detail':'LEAN needs explicit booleans'})
 hard=[p for p in HARD if re.search(p,t,re.I)]
 if profile=='LEAN' and hard:errors.append({'code':'PRD_LEAN_FULL_REQUIRED','detail':', '.join(hard)})
 rows=table(section(t,'Clarification Ledger'))
 if section(t,'Clarification Ledger') and not rows:errors.append({'code':'PRD_CLARIFICATION_TABLE_INVALID','detail':'nonempty ledger must have rows'})
 for r in rows:
  if r.get('Impact','').upper() not in {'HIGH','MEDIUM','LOW'} or r.get('Status','').upper() not in {'OPEN','CLOSED'}:errors.append({'code':'PRD_CLARIFICATION_ROW_INVALID','detail':str(r)})
 open_high=[r for r in rows if r.get('Impact','').upper()=='HIGH' and r.get('Status','').upper()!='CLOSED']
 if open_high:errors.append({'code':'PRD_CLARIFICATION_OPEN_HIGH','detail':','.join(r.get('ID','?') for r in open_high)})
 placeholders=[]
 for token in ('NEEDS CLARIFICATION','<DECIDE>','TBD','???'):
  if token.lower() in t.lower():placeholders.append(token)
 if placeholders:warnings.append({'code':'PRD_AMBIGUITY_MARKERS','detail':','.join(placeholders)})
 return {'schema':'smc.ges.prd-profile-check.v1','valid':not errors,'profile':profile,'hard_full_signals':hard,'errors':errors,'warnings':warnings,'clarification_rows':len(rows)}
def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='cmd',required=True);p=sub.add_parser('scan');p.add_argument('prd',type=Path);p.add_argument('--json',action='store_true');a=ap.parse_args();o=scan(a.prd)
 print(json.dumps(o,ensure_ascii=False,indent=2) if a.json else ('PRD profile ready' if o['valid'] else '\n'.join(x['code']+': '+x['detail'] for x in o['errors'])))
 return 0 if o['valid'] else 1
if __name__=='__main__':raise SystemExit(main())
