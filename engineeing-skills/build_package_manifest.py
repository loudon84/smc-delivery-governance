#!/usr/bin/env python3
"""Deterministic complete package inventory; generated files exclude themselves."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def package_version(root=ROOT):
 # @lat: [[governance-architecture-closure]]
 core=root/'core'/'manifest.json'
 if core.is_file():
  return json.loads(core.read_text(encoding='utf-8')).get('bundle') or '5.0.0'
 return '5.0.0'
def inventory(root=ROOT):
 return [{'path':p.relative_to(root).as_posix(),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc','.pyo'} and p.relative_to(root).as_posix() not in {'PACKAGE-MANIFEST.json','SHA256SUMS'}]
def build(root=ROOT):
 rows=inventory(root)
 return {'schema':'smc.skills.package.manifest.v1','package':'SMC-Governed-Engineering-Skills','package_version':package_version(root),'file_count':len(rows),'files':rows}
def explain_diff(root=ROOT):
 # @lat: [[acceptance-closure#Byte Identity and EOL]]
 expected=build(root);actual=json.loads((root/'PACKAGE-MANIFEST.json').read_text(encoding='utf-8'))
 exp={f['path']:f for f in expected['files']};act={f['path']:f for f in actual.get('files',[])}
 added=sorted(set(exp)-set(act));removed=sorted(set(act)-set(exp))
 content_changed=sorted(p for p in set(exp)&set(act) if exp[p]['sha256']!=act[p]['sha256'])
 size_changed=sorted(p for p in set(exp)&set(act) if exp[p]['size']!=act[p]['size'] and p not in content_changed)
 return {'added':added,'removed':removed,'content_changed':content_changed,'size_changed':size_changed,
         'expected_file_count':expected['file_count'],'actual_file_count':actual.get('file_count')}
def verify(root=ROOT):
 expected=build(root);actual=json.loads((root/'PACKAGE-MANIFEST.json').read_text(encoding='utf-8'))
 if actual!=expected:raise ValueError('PACKAGE_MANIFEST_MISMATCH')
 sums=''.join(r['sha256']+'  '+r['path']+'\n' for r in expected['files'])
 sums+=hashlib.sha256((root/'PACKAGE-MANIFEST.json').read_bytes()).hexdigest()+'  PACKAGE-MANIFEST.json\n'
 if (root/'SHA256SUMS').read_text(encoding='utf-8')!=sums:raise ValueError('PACKAGE_CHECKSUM_MISMATCH')
 return len(expected['files'])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--explain-diff',action='store_true');a=ap.parse_args()
 if a.explain_diff:
  print(json.dumps(explain_diff(),indent=2,ensure_ascii=False));return
 if a.check:print('PACKAGE INTEGRITY PASS:',verify());return
 value=build();(ROOT/'PACKAGE-MANIFEST.json').write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
 sums=''.join(r['sha256']+'  '+r['path']+'\n' for r in value['files'])
 sums+=hashlib.sha256((ROOT/'PACKAGE-MANIFEST.json').read_bytes()).hexdigest()+'  PACKAGE-MANIFEST.json\n'
 (ROOT/'SHA256SUMS').write_text(sums,encoding='utf-8',newline='\n')
 print('PACKAGE MANIFEST GENERATED:',verify())
if __name__=='__main__':main()
