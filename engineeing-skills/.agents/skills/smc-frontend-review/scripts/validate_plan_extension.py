#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

SECTION = "Frontend Quality Ledger"
COLUMNS = ["Change ID","Surface","Composition","State Ownership","Design System","Accessibility","Interaction States","Performance","Visual Verification"]
ALLOWED = {"REQUIRED","REVIEW","NOT_REQUIRED","BLOCKING"}

def section(text: str, heading: str):
    m=re.search(rf"^##\s+{re.escape(heading)}\s*$\n?(.*?)(?=^##\s+|\Z)",text,re.M|re.S);return m.group(1).strip() if m else None

def cells(line): return [x.strip() for x in line.strip().strip('|').split('|')]
def table(body):
    if not body:return []
    lines=[x.strip() for x in body.splitlines() if x.strip().startswith('|')]
    if len(lines)<2:return []
    h=cells(lines[0]);rows=[]
    for raw in lines[2:]:
        v=cells(raw)
        if len(v)!=len(h):break
        rows.append(dict(zip(h,v)))
    return h,rows

def validate(plan: Path):
    text=plan.read_text(encoding='utf-8'); parsed=table(section(text,SECTION)); errors=[]
    if not parsed:return [{"code":"FRONTEND_QUALITY_LEDGER_MISSING","detail":SECTION}]
    header,rows=parsed
    if header!=COLUMNS: errors.append({"code":"FRONTEND_QUALITY_LEDGER_HEADER_INVALID","detail":str(header)})
    seen=set()
    for row in rows:
        cid=row.get('Change ID','')
        if not re.fullmatch(r'C\d{2,}(?:\.\d+)?',cid):errors.append({"code":"FRONTEND_CHANGE_ID_INVALID","detail":cid})
        if cid in seen:errors.append({"code":"FRONTEND_CHANGE_DUPLICATE","detail":cid})
        seen.add(cid)
        if not row.get('Surface','').strip():errors.append({"code":"FRONTEND_SURFACE_MISSING","detail":cid})
        for key in COLUMNS[2:-1]:
            value=row.get(key,'').strip().upper()
            if value not in ALLOWED:errors.append({"code":"FRONTEND_QUALITY_CLASS_INVALID","detail":f"{cid}:{key}={value}"})
        if not row.get('Visual Verification','').strip():errors.append({"code":"FRONTEND_VISUAL_VERIFICATION_MISSING","detail":cid})
    return errors

def main():
    ap=argparse.ArgumentParser();ap.add_argument('plan',type=Path);ap.add_argument('--json',action='store_true');a=ap.parse_args();e=validate(a.plan)
    if a.json:print(json.dumps({"valid":not e,"errors":e},ensure_ascii=False,indent=2))
    elif e:print('\n'.join(f"{x['code']}: {x['detail']}" for x in e),file=sys.stderr)
    else:print('Frontend Quality Ledger validation passed')
    return 1 if e else 0
if __name__=='__main__':raise SystemExit(main())
