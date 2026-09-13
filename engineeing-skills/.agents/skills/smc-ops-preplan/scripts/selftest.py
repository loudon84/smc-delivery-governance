import pathlib,tempfile,subprocess,sys
H=pathlib.Path(__file__).parent
text="""## Ops Design Intent

| Change ID | Deployment Impact | Compatibility | Environment/Config | Health | Migration Order | Rollback | Live Verification |
|---|---|---|---|---|---|---|---|
| C01 | compose | backward compatible | env unchanged | /health | N/A | previous image | startup+health |
"""
with tempfile.TemporaryDirectory() as d:
    p=pathlib.Path(d)/'p.md';p.write_text(text,encoding='utf-8');raise SystemExit(subprocess.run([sys.executable,str(H/'validate_prd_intent.py'),str(p)]).returncode)
