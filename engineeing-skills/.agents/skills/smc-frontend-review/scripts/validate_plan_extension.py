#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
RUNTIME=ROOT/'.agents/ges/domain-runtime'
if not RUNTIME.is_dir():RUNTIME=ROOT/'domain-runtime'
sys.path.insert(0,str(RUNTIME))
from domain_table import validate_table
REQ=["Change ID","Surface","Framework","Composition","State Ownership","Design System","Accessibility","Interaction States","Performance","Visual Verification"]
def validate(p):
 required=list(REQ)
 if 'smc.plan.v3.7' not in p.read_text(encoding='utf-8'):required.remove('Framework')
 return validate_table(p,"Frontend Quality Ledger",required,"FRONTEND_REVIEW")
val=validate
def main():
 ap=argparse.ArgumentParser();ap.add_argument('path',type=Path);ap.add_argument('--json',action='store_true');a=ap.parse_args()
 errors=validate(a.path);print(json.dumps({'valid':not errors,'errors':errors},indent=2));return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
