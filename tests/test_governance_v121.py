from pathlib import Path
import json
import os
import subprocess
import sys
import yaml

SOURCE_ROOT=Path(__file__).resolve().parents[1]

def run(env,*args):
    return subprocess.run([sys.executable,*args],cwd=SOURCE_ROOT,env=env,capture_output=True,text=True)

def test_state_invariant_tool_does_not_write(governance_sandbox):
    root,env=governance_sandbox
    r=run(env,"tools/verify_state_invariants.py")
    assert r.returncode==0, r.stdout+r.stderr
    assert not list(root.rglob("*.tmp"))

def test_strong_artifact_schema_requires_hashes():
    schema=json.loads((SOURCE_ROOT/"schemas/artifact-ref.schema.json").read_text(encoding="utf-8"))
    required=set(schema["required"])
    assert {"commit","blob_sha","sha256","source_revision"} <= required

def test_traceability_schema_requires_strong_source_prd():
    schema=json.loads((SOURCE_ROOT/"schemas/traceability.schema.json").read_text(encoding="utf-8"))
    required=set(schema["$defs"]["artifactRef"]["required"])
    assert {"commit","blob_sha","sha256"} <= required

def test_acceptance_attestation_schema_exists():
    schema=json.loads((SOURCE_ROOT/"schemas/acceptance-attestation.schema.json").read_text(encoding="utf-8"))
    assert "report_sha256" in schema["required"]
    assert "manifest_sha256" in schema["required"]

def test_integration_run_history_schema_requires_real_commits():
    schema=json.loads((SOURCE_ROOT/"schemas/integration-run.schema.json").read_text(encoding="utf-8"))
    repo_input=schema["$defs"]["repoInput"]
    assert repo_input["properties"]["commit"]["pattern"]=="^[0-9a-fA-F]{40}$"

def test_create_feature_writes_strong_source_prd(governance_sandbox):
    root,env=governance_sandbox
    r=run(env,"tools/create_feature.py",
          "--feature-id","FEAT-GENERATOR-001",
          "--title","Generator isolation feature",
          "--program-id","PROGRAM-AGENT-PLATFORM",
          "--source-prd-id","PRD-GENERATOR-v1",
          "--source-prd-repo","REPO-SMC-COPILOT",
          "--source-prd-path","docs/work/generated.md",
          "--source-revision","GEN@1",
          "--source-prd-commit","a"*40,
          "--source-prd-blob-sha","b"*40,
          "--source-prd-sha256","c"*64,
          "--feature-owner","TEAM-AGENT-PLATFORM",
          "--integration-owner","TEAM-WORK-PLATFORM",
          "--participant","REPO-NODESKCLAW:provider",
          "--participant","REPO-SMC-COPILOT:consumer",
          "--change","XR-C01:Generated",
          "--apply")
    assert r.returncode==0, r.stdout+r.stderr
    feature=yaml.safe_load((root/"features/FEAT-GENERATOR-001/feature.yaml").read_text(encoding="utf-8"))
    src=feature["source_prd"]
    assert src["artifact_type"]=="SOURCE_PRD"
    assert src["commit"]=="a"*40
    assert src["blob_sha"]=="b"*40
    assert "current_state" not in str(feature.get("contracts"))
    r=run(env,"tools/validate_feature.py","features/FEAT-GENERATOR-001","--offline")
    assert r.returncode==0, r.stdout+r.stderr

def test_build_receipt_emits_v2_strong_identity(tmp_path):
    repo=tmp_path/"project"
    repo.mkdir()
    subprocess.run(["git","init"],cwd=repo,check=True,capture_output=True)
    subprocess.run(["git","config","user.email","test@example.com"],cwd=repo,check=True,capture_output=True)
    subprocess.run(["git","config","user.name","tester"],cwd=repo,check=True,capture_output=True)
    prd=repo/"docs/work/prd.md"
    prd.parent.mkdir(parents=True)
    prd.write_text("# PRD\n",encoding="utf-8")
    subprocess.run(["git","add","docs/work/prd.md"],cwd=repo,check=True,capture_output=True)
    subprocess.run(["git","commit","-m","init"],cwd=repo,check=True,capture_output=True)
    (repo/".agents/governance").mkdir(parents=True)
    lock={
      "version":"1.2.1","tag":"governance-kit-v1.2.1","commit":"1"*40,
      "manifest_sha256":"2"*64,"kit":"smc-delivery-governance-kit",
    }
    (repo/".agents/governance.lock").write_text(json.dumps(lock),encoding="utf-8")
    wp={
      "work_package_id":"WP-SKILL-FIRST-SMC-COPILOT",
      "feature_id":"FEAT-SKILL-FIRST-001",
      "repository_id":"REPO-SMC-COPILOT",
      "source_revision":"SKILL-FIRST-PRD@4.0.1",
      "local_delivery":{"prd":"docs/work/prd.md","plan":None},
      "contract_inputs":[],
      "evidence":{},
    }
    wp_path=repo/"wp.yaml"
    wp_path.write_text(yaml.safe_dump(wp,sort_keys=False),encoding="utf-8")
    out=repo/"receipt.yaml"
    env=os.environ.copy()
    r=run(env,"skills/universal/smc-delivery-receipt/scripts/build_receipt.py",
          "--repo",str(repo),"--work-package",str(wp_path),
          "--status","IMPLEMENTING","--output",str(out))
    assert r.returncode==0, r.stdout+r.stderr
    receipt=yaml.safe_load(out.read_text(encoding="utf-8"))
    assert receipt["receipt_version"]=="2"
    assert receipt["sync"]["kit"]["version"]=="1.2.1"
    assert receipt["delivery"]["stage_prds"][0]["blob_sha"]
    assert receipt["delivery"]["stage_prds"][0]["sha256"]
    r=run(env,"tools/validate_receipt.py",str(out))
    assert r.returncode==0, r.stdout+r.stderr

def test_load_env_file_does_not_override_process_env(tmp_path,monkeypatch):
    tools=str(SOURCE_ROOT/"tools")
    if tools not in sys.path:
        sys.path.insert(0,tools)
    import governance_lib
    env_path=tmp_path/".env"
    monkeypatch.setenv("SMC_GOVERNANCE_GITHUB_TOKEN","from-process")
    monkeypatch.delenv("SMC_DOTENV_TEST_ONLY",raising=False)
    env_path.write_text("SMC_GOVERNANCE_GITHUB_TOKEN=from-file\nSMC_DOTENV_TEST_ONLY=from-file\n",encoding="utf-8")
    governance_lib.load_env_file(env_path)
    assert os.environ["SMC_GOVERNANCE_GITHUB_TOKEN"]=="from-process"
    assert os.environ["SMC_DOTENV_TEST_ONLY"]=="from-file"
    os.environ.pop("SMC_DOTENV_TEST_ONLY",None)

def test_empty_integration_history_is_not_pass(governance_sandbox):
    root,env=governance_sandbox
    history=yaml.safe_load((root/"integration/runs/INT-SKILL-FIRST-001/history.yaml").read_text(encoding="utf-8"))
    assert history["runs"]==[]
    assert history["latest_run_id"] is None
    assert history["state"]=="WAITING_CONSUMER"
    assert history["blocked_by"]["id"]=="WP-SKILL-FIRST-SMC-COPILOT"
    assert history["blocked_by"]["current_state"]=="IMPLEMENTING"
    wp=yaml.safe_load((root/"features/FEAT-SKILL-FIRST-001/work-packages/smc-copilot.yaml").read_text(encoding="utf-8"))
    assert wp["status"]=="IMPLEMENTING"
    scenario=yaml.safe_load((root/"integration/scenarios/FEAT-SKILL-FIRST-001.yaml").read_text(encoding="utf-8"))
    assert scenario["state"]=="WAITING_CONSUMER"
    assert list((root/"integration/runs/INT-SKILL-FIRST-001").glob("IR-*.yaml"))==[]
    r=run(env,"tools/integration_run.py","--feature","FEAT-SKILL-FIRST-001","--workflow-run-id","1","--apply")
    assert r.returncode!=0, r.stdout+r.stderr
    combined=r.stdout+r.stderr
    assert "integration gate not READY" in combined or "Gate:" in combined or "not READY" in combined
    assert list((root/"integration/runs/INT-SKILL-FIRST-001").glob("IR-*.yaml"))==[]
    r=run(env,"tools/verify_state_invariants.py")
    assert r.returncode==0, r.stdout+r.stderr
