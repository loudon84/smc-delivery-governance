#!/usr/bin/env python3
"""Deterministic complete package inventory; generated files exclude themselves."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def inventory(root=ROOT):
 return [{'path':p.relative_to(root).as_posix(),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc','.pyo'} and p.relative_to(root).as_posix() not in {'PACKAGE-MANIFEST.json','SHA256SUMS'}]
def build(root=ROOT):
 rows=inventory(root)
 return {'schema':'smc.skills.package.manifest.v1','package':'SMC-Governed-Engineering-Skills','package_version':'5.0.0','file_count':len(rows),'files':rows}
def verify(root=ROOT):
 expected=build(root);actual=json.loads((root/'PACKAGE-MANIFEST.json').read_text(encoding='utf-8'))
 if actual!=expected:raise ValueError('PACKAGE_MANIFEST_MISMATCH')
 sums=''.join(r['sha256']+'  '+r['path']+'\n' for r in expected['files'])
 sums+=hashlib.sha256((root/'PACKAGE-MANIFEST.json').read_bytes()).hexdigest()+'  PACKAGE-MANIFEST.json\n'
 if (root/'SHA256SUMS').read_text(encoding='utf-8')!=sums:raise ValueError('PACKAGE_CHECKSUM_MISMATCH')
 return len(expected['files'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
 if a.check:print('PACKAGE INTEGRITY PASS:',verify());return
 value=build();(ROOT/'PACKAGE-MANIFEST.json').write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
 sums=''.join(r['sha256']+'  '+r['path']+'\n' for r in value['files'])
 sums+=hashlib.sha256((ROOT/'PACKAGE-MANIFEST.json').read_bytes()).hexdigest()+'  PACKAGE-MANIFEST.json\n'
 (ROOT/'SHA256SUMS').write_text(sums,encoding='utf-8',newline='\n')
 print('PACKAGE MANIFEST GENERATED:',verify())
if __name__=='__main__':main()
