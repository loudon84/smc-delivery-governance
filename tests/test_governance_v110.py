from pathlib import Path
import os
import subprocess
import sys
import tempfile

SOURCE_ROOT = Path(__file__).resolve().parents[1]


def run(env, *args):
    return subprocess.run([sys.executable, *args], cwd=SOURCE_ROOT, env=env, capture_output=True, text=True)


# @lat: [[tests#Feature and registry#Registry catalogs are valid]]
def test_registry_valid_v110(governance_sandbox):
    root, env = governance_sandbox
    r = run(env, "tools/validate_registry.py")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "repositories=2" in r.stdout


# @lat: [[tests#Receipts and artifacts#Receipt schema accepts fixture]]
def test_delivery_receipt_schema(governance_sandbox):
    root, env = governance_sandbox
    r = run(env, "tools/validate_receipt.py", str(SOURCE_ROOT / "tests/fixtures/receipt.yaml"))
    assert r.returncode == 0, r.stdout + r.stderr


# @lat: [[tests#Acceptance and gates#Acceptance gate passes offline fixture]]
def test_acceptance_gate_pass(governance_sandbox):
    root, env = governance_sandbox
    r = run(
        env,
        "tools/acceptance_gate.py",
        "--manifest", str(SOURCE_ROOT / "tests/fixtures/acceptance.yaml"),
        "--report", str(SOURCE_ROOT / "tests/fixtures/acceptance.report.json"),
        "--work-package", "WP-SKILL-FIRST-SMC-COPILOT",
        "--offline",
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ACCEPTANCE GATE PASS" in r.stdout


# @lat: [[tests#Sync and onboarding#Governance sync bootstraps kit and CI]]
def test_governance_sync_bootstrap_and_check(governance_sandbox):
    root, env = governance_sandbox
    with tempfile.TemporaryDirectory() as td:
        r = run(
            env,
            "tools/governance_sync.py",
            "--repo", td,
            "--project", "PROJECT-SMC-COPILOT",
            "--feature", "FEAT-SKILL-FIRST-001",
            "--with-ci",
            "--allow-source-tree",
            "--offline",
            "--apply",
        )
        assert r.returncode == 0, r.stdout + r.stderr
        assert (Path(td) / ".agents/governance/binding.yaml").exists()
        assert (Path(td) / ".agents/governance/receipts/WP-SKILL-FIRST-SMC-COPILOT.yaml").exists()
        assert (Path(td) / ".github/workflows/smc-governance.yml").exists()
        r = run(
            env,
            "tools/governance_sync.py",
            "--repo", td,
            "--project", "PROJECT-SMC-COPILOT",
            "--feature", "FEAT-SKILL-FIRST-001",
            "--with-ci",
            "--allow-source-tree",
            "--offline",
            "--check",
        )
        assert r.returncode == 0, r.stdout + r.stderr


# @lat: [[tests#Sync and onboarding#Project onboarding dry run]]
def test_project_onboarding_dry_run(governance_sandbox):
    root, env = governance_sandbox
    r = run(
        env,
        "tools/project_onboard.py",
        "--project-id", "PROJECT-DEMO",
        "--project-name", "Demo Project",
        "--repository-id", "REPO-DEMO",
        "--repo", "loudon84/demo",
        "--branch", "main",
        "--team", "TEAM-WORK-PLATFORM",
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "DRY RUN" in r.stdout


# @lat: [[tests#Acceptance and gates#State machine blocks VERIFIED without attestation]]
def test_central_state_machine_blocks_without_acceptance_pass(governance_sandbox):
    root, env = governance_sandbox
    r = run(
        env,
        "tools/transition_state.py",
        "--entity", "work_package",
        "--id", "WP-SKILL-FIRST-SMC-COPILOT",
        "--to", "VERIFIED",
        "--actor", "tester",
        "--reason", "unit test",
    )
    assert r.returncode == 2, r.stdout + r.stderr
    assert "TRANSITION BLOCKED" in r.stdout


# @lat: [[tests#Isolation and audit#Tests do not mutate source SOT]]
def test_old_v110_tests_do_not_mutate_source_sot(governance_sandbox):
    root, env = governance_sandbox
    before = (SOURCE_ROOT / "features/FEAT-SKILL-FIRST-001/work-packages/smc-copilot.yaml").read_bytes()
    run(
        env,
        "tools/transition_state.py",
        "--entity", "work_package",
        "--id", "WP-SKILL-FIRST-SMC-COPILOT",
        "--to", "VERIFIED",
        "--actor", "tester",
        "--reason", "unit test",
        "--apply",
    )
    after = (SOURCE_ROOT / "features/FEAT-SKILL-FIRST-001/work-packages/smc-copilot.yaml").read_bytes()
    assert before == after
