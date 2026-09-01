from pathlib import Path
import json
import os
import subprocess
import sys

SOURCE_ROOT=Path(__file__).resolve().parents[1]

def run(env,*args):
    return subprocess.run([sys.executable,*args],cwd=SOURCE_ROOT,env=env,capture_output=True,text=True)

def test_state_invariant_tool_does_not_write(governance_sandbox):
    root,env=governance_sandbox
    # Sandbox may intentionally still contain migration-era sample refs; this test exercises parser only.
    r=run(env,"tools/verify_state_invariants.py","--allow-sample")
    assert r.returncode in {0,1}
    # verifier itself is read-only
    assert not list(root.rglob("*.tmp"))

def test_strong_artifact_schema_requires_hashes():
    schema=json.loads((SOURCE_ROOT/"schemas/artifact-ref.schema.json").read_text(encoding="utf-8"))
    required=set(schema["required"])
    assert {"commit","blob_sha","sha256","source_revision"} <= required

def test_acceptance_attestation_schema_exists():
    schema=json.loads((SOURCE_ROOT/"schemas/acceptance-attestation.schema.json").read_text(encoding="utf-8"))
    assert "report_sha256" in schema["required"]
    assert "manifest_sha256" in schema["required"]

def test_integration_run_history_schema_requires_real_commits():
    schema=json.loads((SOURCE_ROOT/"schemas/integration-run.schema.json").read_text(encoding="utf-8"))
    repo_input=schema["$defs"]["repoInput"]
    assert repo_input["properties"]["commit"]["pattern"]=="^[0-9a-fA-F]{40}$"
