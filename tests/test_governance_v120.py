from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)


def test_exit_codes_sync_repo_state_all_synced():
    r = run(
        "tools/sync_repo_state.py",
        "features/FEAT-SKILL-FIRST-001",
        "--apply",
        "--local-receipt-dir",
        "examples/sample-receipts",
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "SYNCED" in r.stdout


def test_provider_role_gate_allows_contract_release():
    run(
        "tools/sync_repo_state.py",
        "features/FEAT-SKILL-FIRST-001",
        "--apply",
        "--local-receipt-dir",
        "examples/sample-receipts",
    )
    r = run("tools/reconcile_states.py", "features/FEAT-SKILL-FIRST-001", "--apply")
    assert r.returncode in {0, 2}
    wp = (ROOT / "features/FEAT-SKILL-FIRST-001/work-packages/nodeskclaw.yaml").read_text(encoding="utf-8")
    assert "status: VERIFIED" in wp or "status: DONE" in wp


def test_contract_resolver_consumer_pin():
    from governance_lib import resolve_contract

    assert resolve_contract("SKILL-RUN-CONTRACT", "1.2.1", "REPO-SMC-COPILOT") == "CONFORMANCE_PASS"


def test_audit_event_append(tmp_path, monkeypatch):
    import audit_events
    import governance_lib

    monkeypatch.setattr(governance_lib, "ROOT", tmp_path)
    monkeypatch.setattr(audit_events, "ROOT", tmp_path)
    event = audit_events.append_transition_event(
        entity_type="work_package",
        entity_id="WP-TEST",
        from_state="REVIEW",
        to_state="VERIFIED",
        actor="tester",
        source="human",
        reason="unit test",
        evidence=["tests"],
        apply=True,
    )
    assert event["entity_id"] == "WP-TEST"
    path = tmp_path / "audit/transitions"
    assert any(path.rglob("events.ndjson"))


def test_governance_sync_allow_unsigned_head():
    with tempfile.TemporaryDirectory() as td:
        r = run(
            "tools/governance_sync.py",
            "--repo",
            td,
            "--project",
            "PROJECT-SMC-COPILOT",
            "--feature",
            "FEAT-SKILL-FIRST-001",
            "--with-ci",
            "--allow-unsigned-head",
            "--apply",
        )
        assert r.returncode == 0, r.stdout + r.stderr
        assert (Path(td) / ".agents/governance/binding.yaml").exists()
        binding = (Path(td) / ".agents/governance/binding.yaml").read_text(encoding="utf-8")
        assert "manifest_sha256" in binding or "commit" in binding


def test_acceptance_gate_offline_provenance():
    r = run(
        "tools/acceptance_gate.py",
        "--manifest",
        "tests/fixtures/acceptance.yaml",
        "--report",
        "tests/fixtures/acceptance.report.json",
        "--work-package",
        "WP-SKILL-FIRST-SMC-COPILOT",
        "--offline",
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_release_governance_kit_manifest():
    r = run("tools/release_governance_kit.py", "--version", "1.2.0")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "manifest_sha256" in r.stdout


def test_transition_state_dry_run():
    r = run(
        "tools/transition_state.py",
        "--entity",
        "roadmap_item",
        "--id",
        "GRM-01",
        "--to",
        "DONE",
        "--actor",
        "tester",
        "--reason",
        "test audit",
    )
    assert r.returncode in {0, 2}
