import pathlib,tempfile,subprocess,sys
HERE=pathlib.Path(__file__).parent
text='''## Frontend Design Intent\n\n| Change ID | Surface | Framework | Layout | Component Map | State Ownership | Interaction States | Design System | Responsive | Visual Verification |\n|---|---|---|---|---|---|---|---|---|---|\n| C01 | Settings | Vue | split | REUSE Settings + NEW Editor | Panel | default/loading/error | existing tokens | stacked narrow | LIVE_VISUAL |\n'''
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'p.md';p.write_text(text,encoding='utf-8');r=subprocess.run([sys.executable,str(HERE/'validate_prd_intent.py'),str(p)]);raise SystemExit(r.returncode)
