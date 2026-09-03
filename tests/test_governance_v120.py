from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import yaml

SOURCE_ROOT=Path(__file__).resolve().parents[1]
TOOLS=SOURCE_ROOT/"tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0,str(TOOLS))

def run(env,*args):
    return subprocess.run([sys.executable,*args],cwd=SOURCE_ROOT,env=env,capture_output=True,text=True)

def write_receipts(root: Path):
    d=root/"test-receipts";d.mkdir(exist_ok=True)
    kit={
      "version":"1.2.1",
      "tag":"governance-kit-v1.2.1",
      "commit":"1"*40,
      "manifest_sha256":"2"*64,
    }
    provider={
      "receipt_version":"2","feature_id":"FEAT-SKILL-FIRST-001",
      "work_package_id":"WP-SKILL-FIRST-NODESKCLAW","repository_id":"REPO-NODESKCLAW",
      "source_revision":"SKILL-FIRST-PRD@4.0.1","status":"VERIFIED",
      "sync":{"governance_kit_version":"1.2.1","central_commit":"1"*40,"kit":kit,"contract_pins":[]},
      "delivery":{"stage_prds":[],"issues":[],"bugs":[],"plans":[],"pull_requests":[],
                  "commits":["10d38f2c97739c4a55df893d1dc954fc8896f1a7"],"verification_reports":[]},
      "acceptance":{"manifest":None,"report":None,"status":"NOT_DEFINED"},
      "evidence":{"release":{"tag":"skill-run-contract-v1.2.1","commit":"10d38f2c97739c4a55df893d1dc954fc8896f1a7"}},
      "reported_at":"2026-09-01T12:00:00+00:00",
    }
    consumer={
      "receipt_version":"2","feature_id":"FEAT-SKILL-FIRST-001",
      "work_package_id":"WP-SKILL-FIRST-SMC-COPILOT","repository_id":"REPO-SMC-COPILOT",
      "source_revision":"SKILL-FIRST-PRD@4.0.1","status":"IMPLEMENTING",
      "sync":{"governance_kit_version":"1.2.1","central_commit":"1"*40,"kit":kit,
              "contract_pins":[{"contract_id":"SKILL-RUN-CONTRACT","version":"1.2.1",
                                "tag":"skill-run-contract-v1.2.1",
                                "commit":"10d38f2c97739c4a55df893d1dc954fc8896f1a7"}]},
      "delivery":{"stage_prds":[],"issues":[],"bugs":[],"plans":[],"pull_requests":[],
                  "commits":[],"verification_reports":[]},
      "acceptance":{"manifest":None,"report":None,"status":"PENDING"},
      "evidence":{},"reported_at":"2026-09-01T12:00:00+00:00",
    }
    (d/"REPO-NODESKCLAW.yaml").write_text(yaml.safe_dump(provider,sort_keys=False),encoding="utf-8")
    (d/"REPO-SMC-COPILOT.yaml").write_text(yaml.safe_dump(consumer,sort_keys=False),encoding="utf-8")
    return d

# @lat: [[tests#Sync and onboarding#Sync repo state reports all SYNCED]]
def test_exit_codes_sync_repo_state_all_synced(governance_sandbox):
    root,env=governance_sandbox
    receipts=write_receipts(root)
    r=run(env,"tools/sync_repo_state.py","features/FEAT-SKILL-FIRST-001","--apply",
          "--local-receipt-dir",str(receipts),"--offline-semantic")
    assert r.returncode==0,r.stdout+r.stderr
    assert "SYNCED" in r.stdout
    # The source repository SOT must not change.
    assert "test-receipts" not in (SOURCE_ROOT/"features/FEAT-SKILL-FIRST-001/work-packages/nodeskclaw.yaml").read_text(encoding="utf-8")

# @lat: [[tests#Acceptance and gates#Provider role gate allows contract release]]
def test_provider_role_gate_allows_contract_release(governance_sandbox):
    root,env=governance_sandbox
    receipts=write_receipts(root)
    assert run(env,"tools/sync_repo_state.py","features/FEAT-SKILL-FIRST-001","--apply",
               "--local-receipt-dir",str(receipts),"--offline-semantic").returncode==0
    r=run(env,"tools/reconcile_states.py","features/FEAT-SKILL-FIRST-001","--apply")
    assert r.returncode in {0,2},r.stdout+r.stderr
    wp=(root/"features/FEAT-SKILL-FIRST-001/work-packages/nodeskclaw.yaml").read_text(encoding="utf-8")
    assert "status: VERIFIED" in wp or "status: DONE" in wp

# @lat: [[tests#Acceptance and gates#Contract resolver honors consumer pin]]
def test_contract_resolver_consumer_pin(governance_sandbox,monkeypatch):
    root,env=governance_sandbox
    monkeypatch.setenv("SMC_GOVERNANCE_ROOT",str(root))
    # Reload modules so ROOT picks up sandbox.
    import importlib, governance_lib
    importlib.reload(governance_lib)
    assert governance_lib.resolve_contract("SKILL-RUN-CONTRACT","1.2.1","REPO-SMC-COPILOT")=="CONFORMANCE_PASS"

# @lat: [[tests#Isolation and audit#Audit event appends ndjson]]
def test_audit_event_append(tmp_path,monkeypatch):
    monkeypatch.setenv("SMC_GOVERNANCE_ROOT",str(tmp_path))
    import importlib, governance_lib, audit_events
    importlib.reload(governance_lib);importlib.reload(audit_events)
    event=audit_events.append_transition_event(
        entity_type="work_package",entity_id="WP-TEST",from_state="REVIEW",to_state="VERIFIED",
        actor="tester",source="human",reason="unit test",evidence=["tests"],apply=True,
    )
    assert event["entity_id"]=="WP-TEST"
    assert any((tmp_path/"audit/transitions").rglob("events.ndjson"))

# @lat: [[tests#Sync and onboarding#Governance sync source-tree is explicit]]
def test_governance_sync_source_tree_is_explicit_dev_mode(governance_sandbox):
    root,env=governance_sandbox
    with tempfile.TemporaryDirectory() as td:
        r=run(env,"tools/governance_sync.py","--repo",td,"--project","PROJECT-SMC-COPILOT",
              "--feature","FEAT-SKILL-FIRST-001","--with-ci","--allow-source-tree","--offline","--apply")
        assert r.returncode==0,r.stdout+r.stderr
        binding=Path(td)/".agents/governance/binding.yaml"
        assert binding.exists()
        assert "manifest_sha256" in binding.read_text(encoding="utf-8")

# @lat: [[tests#Acceptance and gates#Acceptance gate offline mode]]
def test_acceptance_gate_offline():
    env=os.environ.copy()
    r=run(env,"tools/acceptance_gate.py","--manifest","tests/fixtures/acceptance.yaml",
          "--report","tests/fixtures/acceptance.report.json",
          "--work-package","WP-SKILL-FIRST-SMC-COPILOT","--offline")
    assert r.returncode==0,r.stdout+r.stderr

# @lat: [[tests#Isolation and audit#Kit release checksums close over manifest]]
def test_release_governance_kit_manifest_and_checksum_closure(governance_sandbox):
    root,env=governance_sandbox
    r=run(env,"tools/release_governance_kit.py","--version","1.2.1",
          "--commit","1"*40,"--tag","governance-kit-v1.2.1","--allow-untagged","--apply")
    assert r.returncode==0,r.stdout+r.stderr
    sums=(root/"dist/governance-kit-v1.2.1/SHA256SUMS").read_text(encoding="utf-8")
    assert "  manifest.json\n" in sums
    assert "\r" not in sums

# @lat: [[tests#Isolation and audit#Transition dry run is non-mutating]]
def test_transition_state_dry_run_is_non_mutating(governance_sandbox):
    root,env=governance_sandbox
    before=(root/"features/FEAT-SKILL-FIRST-001/roadmap.yaml").read_bytes()
    run(env,"tools/transition_state.py","--entity","roadmap_item","--id","GRM-01","--to","DONE",
        "--actor","tester","--reason","test")
    after=(root/"features/FEAT-SKILL-FIRST-001/roadmap.yaml").read_bytes()
    assert before==after
