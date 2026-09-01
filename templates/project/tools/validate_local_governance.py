from __future__ import annotations
from pathlib import Path
import json, yaml
from jsonschema import Draft202012Validator

ROOT=Path('.agents/governance')

def validate(path:Path, schema:Path):
    data=yaml.safe_load(path.read_text(encoding='utf-8')) if path.suffix in {'.yaml','.yml'} else json.loads(path.read_text(encoding='utf-8'))
    spec=json.loads(schema.read_text(encoding='utf-8'))
    return [f"{path}: {e.message}" for e in Draft202012Validator(spec).iter_errors(data)]

def main():
    errors=[]
    ps=ROOT/'project-status.yaml'
    if ps.exists(): errors += validate(ps, ROOT/'schemas/project-report.schema.json')
    for p in (ROOT/'receipts').glob('*.yaml'):
        errors += validate(p, ROOT/'schemas/delivery-receipt.schema.json')
    for p in (ROOT/'acceptance').glob('*.yaml'):
        errors += validate(p, ROOT/'schemas/acceptance-manifest.schema.json')
    for p in (ROOT/'acceptance').glob('*.report.json'):
        errors += validate(p, ROOT/'schemas/acceptance-report.schema.json')
    if errors:
        print('LOCAL GOVERNANCE INVALID')
        for e in errors: print('-',e)
        raise SystemExit(1)
    print('LOCAL GOVERNANCE VALID')

if __name__=='__main__': main()
