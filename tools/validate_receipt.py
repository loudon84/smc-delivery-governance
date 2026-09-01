from __future__ import annotations
import sys
from pathlib import Path
from governance_lib import ROOT, load_yaml, validate_jsonschema


def main():
    if len(sys.argv)!=2: raise SystemExit('usage: validate_receipt.py <receipt.yaml>')
    path=Path(sys.argv[1]); doc=load_yaml(path)
    errors=validate_jsonschema(doc, ROOT/'schemas/delivery-receipt.schema.json')
    if errors:
        print('RECEIPT INVALID')
        for e in errors: print('-',e)
        raise SystemExit(1)
    print('RECEIPT VALID')
    print(f"feature_id={doc['feature_id']} work_package_id={doc['work_package_id']} status={doc['status']}")

if __name__=='__main__': main()
