from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]

def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)

def test_feature_valid():
    r = run("tools/validate_feature.py", "features/FEAT-SKILL-FIRST-001")
    assert r.returncode == 0, r.stdout + r.stderr

def test_contract_status():
    r = run("tools/contract_status.py", "SKILL-RUN-CONTRACT")
    assert r.returncode == 0
    assert "1.2.1" in r.stdout

def test_integration_gate_waits_for_consumer():
    r = run("tools/integration_gate.py", "features/FEAT-SKILL-FIRST-001")
    assert r.returncode == 2
    assert "WAITING_CONSUMER" in r.stdout
