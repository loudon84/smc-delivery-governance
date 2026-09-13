import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).parent
text = """---
governance_profile: FULL
---

## Frontend Design Intent

| Change ID | Surface | Framework | Layout | Component Map | State Ownership | Interaction States | Design System | Responsive | Visual Verification |
|---|---|---|---|---|---|---|---|---|---|
| C01 | Settings | Vue | split | REUSE Settings + NEW Editor | Panel | default/loading/error | existing tokens | stacked narrow | LIVE_VISUAL |
"""
with tempfile.TemporaryDirectory() as d:
    p = pathlib.Path(d) / "p.md"
    p.write_text(text, encoding="utf-8")
    r = subprocess.run([sys.executable, str(HERE / "validate_prd_intent.py"), str(p)])
    raise SystemExit(r.returncode)
