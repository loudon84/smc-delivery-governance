from pathlib import Path
import subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]

def run(*args):
    return subprocess.run([sys.executable,*args],cwd=ROOT,capture_output=True,text=True)

def test_registry_valid_v110():
    r=run('tools/validate_registry.py')
    assert r.returncode==0, r.stdout+r.stderr
    assert 'repositories=2' in r.stdout

def test_delivery_receipt_schema():
    r=run('tools/validate_receipt.py','tests/fixtures/receipt.yaml')
    assert r.returncode==0, r.stdout+r.stderr

def test_acceptance_gate_pass():
    r=run('tools/acceptance_gate.py','--manifest','tests/fixtures/acceptance.yaml','--report','tests/fixtures/acceptance.report.json','--work-package','WP-SKILL-FIRST-SMC-COPILOT')
    assert r.returncode==0, r.stdout+r.stderr
    assert 'ACCEPTANCE GATE PASS' in r.stdout

def test_governance_sync_bootstrap_and_check():
    with tempfile.TemporaryDirectory() as td:
        r=run('tools/governance_sync.py','--repo',td,'--project','PROJECT-SMC-COPILOT','--feature','FEAT-SKILL-FIRST-001','--with-ci','--apply')
        assert r.returncode==0, r.stdout+r.stderr
        assert (Path(td)/'.agents/governance/binding.yaml').exists()
        assert (Path(td)/'.agents/governance/receipts/WP-SKILL-FIRST-SMC-COPILOT.yaml').exists()
        assert (Path(td)/'.github/workflows/smc-governance.yml').exists()
        r=run('tools/governance_sync.py','--repo',td,'--project','PROJECT-SMC-COPILOT','--feature','FEAT-SKILL-FIRST-001','--with-ci','--check')
        assert r.returncode==0, r.stdout+r.stderr

def test_project_onboarding_dry_run():
    r=run('tools/project_onboard.py','--project-id','PROJECT-DEMO','--project-name','Demo Project','--repository-id','REPO-DEMO','--repo','loudon84/demo','--branch','main','--team','TEAM-WORK-PLATFORM')
    assert r.returncode==0, r.stdout+r.stderr
    assert 'DRY RUN' in r.stdout


def test_central_state_machine_blocks_without_synced_evidence():
    r=run('tools/transition_state.py','--entity','work_package','--id','WP-SKILL-FIRST-SMC-COPILOT','--to','REVIEW')
    assert r.returncode==2
    assert 'TRANSITION BLOCKED' in r.stdout
