from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(env, *args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, env=env, capture_output=True, text=True)


# @lat: [[tests#Feature and registry#Feature skeleton validates offline]]
def test_feature_valid(governance_sandbox):
    root, env = governance_sandbox
    r = run(env, "tools/validate_feature.py", "features/FEAT-SKILL-FIRST-001", "--offline")
    assert r.returncode == 0, r.stdout + r.stderr


# @lat: [[tests#Feature and registry#Contract status reports pinned release]]
def test_contract_status(governance_sandbox):
    root, env = governance_sandbox
    r = run(env, "tools/contract_status.py", "SKILL-RUN-CONTRACT")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "1.2.1" in r.stdout


# @lat: [[tests#Acceptance and gates#Integration gate waits for consumer]]
def test_integration_gate_waits_for_consumer(governance_sandbox):
    root, env = governance_sandbox
    r = run(env, "tools/integration_gate.py", "features/FEAT-SKILL-FIRST-001")
    assert r.returncode == 2, r.stdout + r.stderr
    assert "WAITING_" in r.stdout
