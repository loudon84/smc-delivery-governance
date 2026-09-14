#!/usr/bin/env python3
"""Deterministic Acceptance Closure golden + chaos cases (G01–G42 real behavior)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / ".agents/skills/smc-plan-delivery/scripts"
CONTEXT_ENGINE = ROOT / "context-engine"
sys.path.insert(0, str(ROOT / ".agents/skills/smc-work-router/scripts"))
sys.path.insert(0, str(ROOT / "domain-runtime"))
sys.path.insert(0, str(DELIVERY))
sys.path.insert(0, str(CONTEXT_ENGINE))
sys.path.insert(0, str(ROOT))
from risk_signals import classify_text_hint, parse_risk_snapshot, resolve_risk  # noqa: E402
from work_router import REQUIRED, RISKS, route  # noqa: E402
import install_v500 as installer  # noqa: E402
import engineering_method as em  # noqa: E402
import review_record  # noqa: E402
import evidence  # noqa: E402
import workspace  # noqa: E402
import acceptance as acc  # noqa: E402
import commit_guard  # noqa: E402
import runtime_metrics as telemetry  # noqa: E402
import frontend_app_registry as registry_mod  # noqa: E402
import ux_context_resolver as ux_mod  # noqa: E402


def safe_facts(**extra):
    return {**dict.fromkeys(REQUIRED, True), **dict.fromkeys(RISKS, False), "governed": True, **extra}


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _git_init(root: Path):
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "t@example.com"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True)


MIN_PLAN = """---
name: GES-ACC
overview: acceptance
todos:
  - id: t1
    content: "T1 — change app [C01]"
    status: pending
isProject: false
plan_contract: smc.plan.v3.7
plan_id: GES-ACC
commit_policy: post_review
governance_profile: FULL
---

# Plan

## Change Matrix

| Change ID | File / Symbol | Kind | Action | Existing Owner | Todo Owner | Target State | PRD Capability | New File? |
|---|---|---|---|---|---|---|---|---|
| C01 | `app.py#main` | PROD | MODIFY | app.py#main | T1 | ok | app | no |

## Todo T1 — change app

**Owns Changes**
- C01

**Writes:** `app.py#main`

**Goal**
fix app
"""


class GoldenCorpus(unittest.TestCase):
    def test_g01_pure_research(self):
        f = safe_facts(
            research_intent=True,
            governed=False,
            retained_production_change=False,
            production_write_requested=False,
            durable_product_artifact_requested=False,
        )
        out = route(f)
        self.assertEqual(out["governance_profile"], "NONE")

    def test_g02_governed_research(self):
        out = route(safe_facts(research_intent=True, governed=True))
        self.assertEqual(out["governance_profile"], "FULL")

    def test_g03_production_write_research(self):
        f = safe_facts(
            research_intent=True,
            governed=False,
            retained_production_change=False,
            production_write_requested=True,
            durable_product_artifact_requested=False,
        )
        self.assertEqual(route(f)["governance_profile"], "FULL")

    def test_g04_lean_mechanical(self):
        self.assertEqual(route(safe_facts())["governance_profile"], "LEAN")

    def test_g05_existing_service_lean(self):
        self.assertEqual(route(safe_facts(governed=True))["governance_profile"], "LEAN")

    def test_g09_public_api_full(self):
        self.assertEqual(route(safe_facts(public_contract=True))["governance_profile"], "FULL")

    def test_g10_auth_boundary_full(self):
        self.assertEqual(route(safe_facts(security_boundary=True))["governance_profile"], "FULL")

    def test_g11_schema_migration_full(self):
        self.assertEqual(route(safe_facts(schema_migration=True))["governance_profile"], "FULL")

    def test_g16_duplicate_hotspot_block(self):
        # @lat: [[ges-tests#Acceptance Closure#Duplicate write owner is blocked]]
        sys.path.insert(0, str(ROOT / ".agents/skills/smc-plan-validator/scripts"))
        import validate_plan_v37 as v37  # noqa: WPS433

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = _write(
                root,
                "dup.plan.md",
                MIN_PLAN
                + "\n## Todo T2 — also writes same\n\n**Writes:** `app.py#main`\n\n**Goal**\nx\n",
            )
            errs = v37.ownership_errors(plan)
            self.assertTrue(any(e["code"] == "PLAN_WRITE_OWNERSHIP_CONFLICT" for e in errs))

    def test_g17_worker_out_of_scope(self):
        # @lat: [[ges-tests#Acceptance Closure#Worker out of scope drifts]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(root, "p.plan.md", MIN_PLAN)
            _write(root, "app.py", "def main():\n    return 1\n")
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "init"], check=True)
            workspace.init(plan)
            _write(root, "other.py", "x=1\n")  # out of scope dirty
            with self.assertRaisesRegex(ValueError, "DELIVERY_SCOPE_DRIFT"):
                workspace.assert_stable(plan)

    def test_g18_tdd_stale(self):
        # @lat: [[ges-tests#Acceptance Closure#TDD scope becomes stale]]
        from common import append_jsonl

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(root, "p.plan.md", MIN_PLAN)
            app = _write(root, "app.py", "def main():\n    return 1\n")
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "init"], check=True)
            em.classify(plan, "T1", profile_override="BUG_FIX", write=True)
            m = em.load_method(plan, "T1")
            scope = em.scope_fingerprint(plan, "T1")
            cmd = "python -c \"print('ok')\""
            red = {
                "schema": "smc.execution.tdd-event.v2",
                "phase": "RED",
                "status": "CONFIRMED",
                "command": cmd,
                "exit_code": 1,
                "output_sha256": "a" * 64,
                "plan_semantic_sha256": m["plan_semantic_sha256"],
                "method_epoch": m["method_epoch"],
                "scope_fingerprint": scope,
                "todo": "T1",
            }
            green = dict(red, phase="GREEN", status="PASS", exit_code=0)
            em.save_receipt(plan, red)
            em.save_receipt(plan, green)
            append_jsonl(em.tdd_path(plan, "T1"), red)
            append_jsonl(em.tdd_path(plan, "T1"), green)
            app.write_text("def main():\n    return 9\n", encoding="utf-8")
            rc, payload = em.tdd_check(plan, "T1")
            self.assertEqual(rc, 2)
            self.assertEqual(payload.get("reason"), "TDD_SCOPE_STALE")

    def test_g19_review_stale(self):
        # @lat: [[ges-tests#Acceptance Closure#Review becomes stale after semantic change]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(root, "p.plan.md", MIN_PLAN)
            review_record.record("plan", plan, "PASS", "tester")
            status, _ = review_record.latest_status(plan, "plan")
            self.assertEqual(status, "FRESH_PASS")
            plan.write_text(plan.read_text(encoding="utf-8") + "\n<!-- semantic -->\n", encoding="utf-8")
            status, _ = review_record.latest_status(plan, "plan")
            self.assertEqual(status, "STALE")

    def test_g20_evidence_stale(self):
        # @lat: [[ges-tests#Acceptance Closure#Evidence becomes stale after production change]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(
                root,
                "p.plan.md",
                MIN_PLAN.replace(
                    "## Change Matrix",
                    "## Verification Ledger\n\n"
                    "| Verification ID | Level | Entry Point / Command | Oracle | Negative / Regression | Evidence Policy | Environment | Blocking |\n"
                    "|---|---|---|---|---|---|---|---|\n"
                    "| V01 | UNIT | `python -c \"print('ok')\"` | exit 0 | x | LOCAL_TRANSIENT | local | yes |\n\n"
                    "## Change Matrix",
                ),
            )
            app = _write(root, "app.py", "def main():\n    return 1\n")
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "init"], check=True)
            workspace.init(plan)
            rc = evidence.run_cmd(plan, "V01", ["python", "-c", "print('ok')"])
            self.assertEqual(0, rc)
            self.assertEqual("FRESH", evidence.current_status(plan, "V01")[0])
            app.write_text("def main():\n    return 3\n", encoding="utf-8")
            self.assertEqual("STALE", evidence.current_status(plan, "V01")[0])

    def test_g21_live_candidate_mismatch(self):
        # @lat: [[ges-tests#Acceptance Closure#Live candidate mismatch]]
        from unittest import mock

        plan_text = Path(
            ROOT / ".agents/skills/smc-plan-delivery/scripts/tests/test_acceptance_governance.py"
        ).read_text(encoding="utf-8")
        start = plan_text.index('PLAN = r"""') + len('PLAN = r"""')
        end = plan_text.index('"""', start)
        body = plan_text[start:end]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(root, ".cursor/plans/rm-ac.plan.md", body)
            _write(root, "app.py", "def main():\n    return 1\n")
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "init"], check=True)
            workspace.init(plan)
            candidate = acc.capture_candidate(plan)
            with mock.patch.dict(
                os.environ,
                {"TEST_TOKEN": "set", "DEPLOYED_CANDIDATE": "sha256:not-the-current-candidate"},
                clear=False,
            ):
                result = acc.preflight_verification(plan, "V01")
            self.assertFalse(result["pass"])
            self.assertEqual("LIVE_SUT_MISMATCH", result["code"])
            self.assertEqual(candidate["candidate_id"], result["expected_candidate_id"])

    def test_g22_debug_escalation(self):
        # @lat: [[ges-tests#Acceptance Closure#Debug escalates after three failed fixes]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(root, "p.plan.md", MIN_PLAN)
            _write(root, "app.py", "def main():\n    return 1\n")
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "init"], check=True)
            em.classify(plan, "T1", profile_override="BUG_FIX", write=True)
            fail_cmd = f'{sys.executable} -c "raise SystemExit(1)"'
            # REPRODUCTION pass (expects FAIL)
            em.debug_run(plan, "T1", "REPRODUCTION", fail_cmd, expect="FAIL")
            rows = em.current_rows(plan, "T1", em.debug_path(plan, "T1"))
            repro = [r for r in rows if r.get("phase") == "REPRODUCTION"][-1]
            em.debug_event(
                plan,
                "T1",
                "ROOT_CAUSE",
                "CONFIRMED",
                summary="null deref in main",
                evidence_ref=repro.get("evidence_ref", ""),
            )
            for _ in range(3):
                em.debug_event(plan, "T1", "FIX_ATTEMPT", "FAIL", summary="still failing")
            rc, payload = em.debug_check(plan, "T1")
            self.assertEqual(rc, 3)
            self.assertEqual(payload["reason"], "DEBUG_ARCHITECTURE_ESCALATION")

    def test_g23_no_schema_migration(self):
        text = "No schema migration required."
        facts = {k: False for k in RISKS}
        out = resolve_risk(text, facts)
        self.assertFalse(out["high_risk"])
        self.assertEqual(classify_text_hint(text, "schema_migration"), "NEGATED")

    def test_g24_contradiction(self):
        text = "schema migration required for this release"
        facts = {k: False for k in RISKS}
        out = resolve_risk(text, facts)
        self.assertTrue(out["high_risk"])
        self.assertTrue(any(e["code"] == "RISK_FACT_CONTRADICTION" for e in out["errors"]))

    def test_g25_framework_banana(self):
        mod = _load("fe", ROOT / ".agents/skills/smc-frontend-preplan/scripts/validate_prd_intent.py")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "prd.md"
            p.write_text(
                """## Frontend Design Intent

| Change ID | Surface | Framework | Layout | Component Map | State Ownership | Interaction States | Design System | Responsive | Visual Verification |
|---|---|---|---|---|---|---|---|---|---|
| C01 | X | BANANA | UNCHANGED | REUSE A | UNCHANGED | default | tokens | UNCHANGED | STATIC |
""",
                encoding="utf-8",
            )
            errors = mod.validate(p)
            self.assertTrue(any(e["code"] in {"FRONTEND_PREPLAN_ENUM_INVALID", "DOMAIN_SEMANTIC_TOKEN_INVALID"} for e in errors))

    def test_g26_backend_breaking_lean(self):
        mod = _load("be", ROOT / ".agents/skills/smc-backend-preplan/scripts/validate_prd_intent.py")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "prd.md"
            p.write_text(
                """governance_profile: LEAN

## Backend Design Intent

| Change ID | Owner | Contract | Data/Transaction | Auth | Idempotency/Concurrency | Failure Semantics | Observability |
|---|---|---|---|---|---|---|---|
| C01 | svc | BREAKING_CHANGE | WRITE | UNCHANGED | UNCHANGED | fail closed | logs |
""",
                encoding="utf-8",
            )
            errors = mod.validate(p)
            self.assertTrue(any(e["code"] == "BACKEND_PREPLAN_FULL_REQUIRED" for e in errors))

    def test_g27_ops_irreversible_no_rollback(self):
        mod = _load("ops", ROOT / ".agents/skills/smc-ops-preplan/scripts/validate_prd_intent.py")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "prd.md"
            p.write_text(
                """## Ops Design Intent

| Change ID | Deployment Impact | Compatibility | Environment/Config | Health | Migration Order | Rollback | Live Verification |
|---|---|---|---|---|---|---|---|
| C01 | IRREVERSIBLE | BREAKING | cfg | health | N/A | N/A | SMOKE |
""",
                encoding="utf-8",
            )
            errors = mod.validate(p)
            self.assertTrue(any(e["code"] == "OPS_PREPLAN_ROLLBACK_REQUIRED" for e in errors))

    def test_g28_stale_untouched_deleted(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            stale = _write(project, ".agents/skills/smc-plan-delivery/SKILL.md", "old\n")
            digest = hashlib.sha256(stale.read_bytes()).hexdigest()
            _write(
                project,
                ".smc/ges-install-lock.json",
                json.dumps(
                    {
                        "schema": "smc.ges.install-lock.v2",
                        "owned_files": [{"path": ".agents/skills/smc-plan-delivery/SKILL.md", "installed_sha256": digest}],
                    }
                ),
            )
            backup = project / ".smc/backup"
            backup.mkdir(parents=True)
            notes = installer.reconcile_stale_owned_files(project, backup, {}, ["other-skill"])
            self.assertFalse(stale.exists())
            self.assertTrue(any(n.startswith("STALE_OWNED_DELETED:") for n in notes))

    def test_g29_stale_modified_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            stale = _write(project, ".agents/skills/smc-plan-delivery/SKILL.md", "old\n")
            _write(
                project,
                ".smc/ges-install-lock.json",
                json.dumps(
                    {
                        "schema": "smc.ges.install-lock.v2",
                        "owned_files": [{"path": ".agents/skills/smc-plan-delivery/SKILL.md", "installed_sha256": "00"}],
                    }
                ),
            )
            with self.assertRaisesRegex(RuntimeError, "INSTALL_STALE_OWNED_FILE_MODIFIED"):
                installer.reconcile_stale_owned_files(project, project / ".smc/backup", {}, ["other"])
            self.assertTrue(stale.exists())

    def test_g30_v1_lock_skip_destructive(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            stale = _write(project, ".agents/skills/smc-plan-delivery/SKILL.md", "old\n")
            _write(project, ".smc/ges-install-lock.json", json.dumps({"schema": "smc.ges.install-lock.v1"}))
            notes = installer.reconcile_stale_owned_files(project, project / ".smc/backup", {}, ["x"])
            self.assertEqual(notes, ["INSTALL_LEGACY_RECONCILIATION_SKIPPED"])
            self.assertTrue(stale.exists())

    def test_g31_existing_auth_read_lean(self):
        # @lat: [[frontend-context#Acceptance G31–G42#G31 Existing Auth Read]]
        f = safe_facts(
            governed=True,
            security_sensitive_touch=True,
            security_boundary_change=False,
        )
        out = route(f)
        self.assertEqual(out["work_class"], "BOUNDED")
        self.assertEqual(out["governance_profile"], "LEAN")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(
                root,
                "p.plan.md",
                MIN_PLAN.replace(
                    "## Todo T1 — change app\n\n**Owns Changes**\n- C01\n\n**Writes:** `app.py#main`\n\n**Goal**\nfix app\n",
                    "## Todo T1 — display email from existing auth\n\n**Owns Changes**\n- C01\n\n**Writes:** `app.py#main`\n\n**Goal**\n"
                    "read existing DesktopAuthState and display email; no auth contract change\n",
                ),
            )
            _write(root, "app.py", "def main():\n    return 1\n")
            classified = em.classify(plan, "T1", write=True)
            self.assertIn(classified["profile"], {"SENSITIVE_BOUNDED", "BOUNDED_BEHAVIOR"})
            self.assertEqual(classified["model_tier"], "STANDARD")
            self.assertEqual(classified["review_depth"], "UNIFIED")

    def test_g32_existing_logout_wiring(self):
        # @lat: [[frontend-context#Acceptance G31–G42#G32 Existing Logout Wiring]]
        f = safe_facts(
            governed=True,
            security_sensitive_touch=True,
            existing_lifecycle_wiring=True,
            security_boundary_change=False,
        )
        out = route(f)
        self.assertEqual(out["work_class"], "BOUNDED")
        self.assertEqual(out["governance_profile"], "LEAN")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(
                root,
                "p.plan.md",
                MIN_PLAN.replace(
                    "## Todo T1 — change app\n\n**Owns Changes**\n- C01\n\n**Writes:** `app.py#main`\n\n**Goal**\nfix app\n",
                    "## Todo T1 — wire existing logout\n\n**Owns Changes**\n- C01\n\n**Writes:** `app.py#main`\n\n**Goal**\n"
                    "call existing logout; session clear without auth contract change\n",
                ),
            )
            _write(root, "app.py", "def main():\n    return 1\n")
            classified = em.classify(plan, "T1", write=True)
            self.assertEqual(classified["profile"], "SENSITIVE_BOUNDED")
            self.assertEqual(classified["tdd_policy"], "TDD_FOCUSED_REQUIRED")

    def test_g33_security_boundary_change_full(self):
        # @lat: [[frontend-context#Acceptance G31–G42#G33 Security Boundary Change]]
        f = safe_facts(governed=True, security_boundary_change=True)
        out = route(f)
        self.assertEqual(out["work_class"], "ARCHITECTURAL")
        self.assertEqual(out["governance_profile"], "FULL")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(
                root,
                "p.plan.md",
                MIN_PLAN.replace(
                    "## Todo T1 — change app\n\n**Owns Changes**\n- C01\n\n**Writes:** `app.py#main`\n\n**Goal**\nfix app\n",
                    "## Todo T1 — change token ownership\n\n**Owns Changes**\n- C01\n\n**Writes:** `app.py#main`\n\n**Goal**\n"
                    "security boundary change: transfer token ownership and auth protocol\n",
                ),
            )
            _write(root, "app.py", "def main():\n    return 1\n")
            classified = em.classify(
                plan,
                "T1",
                write=True,
                risk_facts={"security_boundary_change": True},
            )
            self.assertEqual(classified["profile"], "HIGH_RISK")
            self.assertEqual(classified["model_tier"], "REASONING")
            self.assertEqual(classified["review_depth"], "INDEPENDENT")

    def test_g34_reuse_gate_add_new_blocked(self):
        # @lat: [[frontend-context#Acceptance G31–G42#G34 Existing Surface Candidate]]
        blocked = ux_mod.reuse_gate(
            {
                "decision": "ADD_NEW",
                "existing_surface": {"surface_id": "desktop:sidebar.footer.identity"},
            }
        )
        self.assertFalse(blocked["ok"])
        self.assertEqual(blocked["code"], "UX_SURFACE_REUSE_REQUIRED")

    def test_g35_extend_existing_surface(self):
        # @lat: [[frontend-context#Acceptance G31–G42#G35 Extend Surface]]
        gate = ux_mod.reuse_gate(
            {
                "same_ux_role": True,
                "decision": "EXTEND",
                "existing_surface": {"surface_id": "desktop:sidebar.footer.identity"},
            }
        )
        self.assertTrue(gate["ok"])
        self.assertEqual(gate["decision"], "EXTEND")

    def test_g36_cross_app_surface_isolation(self):
        # @lat: [[frontend-context#Acceptance G31–G42#G36 Different App Isolation]]
        self.assertFalse(registry_mod.cross_app_surface_allowed("desktop", "web"))

    def test_g37_different_stack_component_reuse(self):
        # @lat: [[frontend-context#Acceptance G31–G42#G37 Different Stack Isolation]]
        result = registry_mod.component_reuse_automatic("react-electron", "vue3-web")
        self.assertFalse(result["component_reuse"])
        self.assertTrue(result["ux_pattern_reuse"])
        self.assertEqual(result["reason"], "DIFFERENT_STACK")

    def test_g38_shared_ui_profile_avatar(self):
        # @lat: [[frontend-context#Acceptance G31–G42#G38 Shared UI Reuse]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            _write(
                root,
                "apps/desktop/package.json",
                json.dumps({"name": "desktop", "dependencies": {"react": "18.0.0"}}) + "\n",
            )
            _write(root, "apps/desktop/src/App.tsx", "export default function App(){return null}\n")
            _write(root, "packages/ui/package.json", json.dumps({"name": "@smc/ui"}) + "\n")
            _write(root, "packages/ui/ProfileAvatar.tsx", "export function ProfileAvatar(){return null}\n")
            registry_mod.discover(root)
            decision = registry_mod.shared_ui_reuse_decision(root, "ProfileAvatar")
            self.assertEqual(decision["decision"], "REUSE")

    def test_g39_incremental_refresh_desktop_only(self):
        # @lat: [[frontend-context#Acceptance G31–G42#G39 Incremental Refresh]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            _write(
                root,
                "apps/desktop/package.json",
                json.dumps({"name": "desktop", "dependencies": {"react": "18.0.0"}}) + "\n",
            )
            _write(root, "apps/desktop/src/Layout.tsx", "export function Layout(){return null}\n")
            _write(
                root,
                "apps/desktop/src/ProfileSwitcher.tsx",
                "export function ProfileSwitcher(){return null}\n",
            )
            _write(
                root,
                "apps/web/package.json",
                json.dumps({"name": "web", "dependencies": {"vue": "3.4.0"}}) + "\n",
            )
            _write(root, "apps/web/src/App.vue", "<template><div/></template>\n")
            registry_mod.discover(root)
            ux_mod.generate_baseline(root, "desktop")
            ux_mod.generate_baseline(root, "web")
            result = ux_mod.incremental_refresh(root, ["apps/desktop/src/ProfileSwitcher.tsx"])
            self.assertIn("desktop", result["refreshed_apps"])
            self.assertIn("web", result["untouched_apps"])
            self.assertNotIn("web", result["refreshed_apps"])
            web_lock = json.loads(
                (root / ".agents/ges/frontend/apps/web/baseline.lock").read_text(encoding="utf-8")
            )
            self.assertEqual(web_lock.get("status"), "FRESH")

    def test_g40_sensitive_bounded_tdd_policy(self):
        # @lat: [[frontend-context#Acceptance G31–G42#G40 Sensitive Bounded TDD]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(
                root,
                "p.plan.md",
                MIN_PLAN.replace(
                    "## Todo T1 — change app\n\n**Owns Changes**\n- C01\n\n**Writes:** `app.py#main`\n\n**Goal**\nfix app\n",
                    "## Todo T1 — logout side effect\n\n**Owns Changes**\n- C01\n\n**Writes:** `app.py#main`\n\n**Goal**\n"
                    "existing logout side effect focused RED/GREEN\n",
                ),
            )
            _write(root, "app.py", "def main():\n    return 1\n")
            classified = em.classify(plan, "T1", write=True)
            self.assertEqual(classified["profile"], "SENSITIVE_BOUNDED")
            self.assertEqual(classified["tdd_policy"], "TDD_FOCUSED_REQUIRED")

    def test_g41_final_commit_pending_todo_blocked(self):
        # @lat: [[frontend-context#Acceptance G31–G42#G41 Final Commit Pending Todo]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(root, "p.plan.md", MIN_PLAN)
            _write(root, "app.py", "def main():\n    return 1\n")
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "init"], check=True)
            rc = commit_guard.capture(plan, commit_kind="FINAL")
            self.assertEqual(rc, 1)

    def test_g42_telemetry_cost_buckets(self):
        # @lat: [[frontend-context#Acceptance G31–G42#G42 Telemetry Cost Buckets]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(root, "p.plan.md", MIN_PLAN)
            _write(root, "app.py", "def main():\n    return 1\n")
            buckets = (
                "ROUTING",
                "BASELINE_LOOKUP",
                "GROUNDING",
                "PLAN",
                "IMPLEMENT",
                "TDD",
                "REVIEW",
                "DELIVERY",
            )
            for bucket in buckets:
                did = f"d-{bucket.lower()}"
                telemetry.dispatch(
                    plan,
                    phase=bucket if bucket != "BASELINE_LOOKUP" else "BASELINE",
                    todo="T1",
                    requested_tier="STANDARD",
                    dispatch_id=did,
                    agent="acc",
                    cost_bucket=bucket,
                )
                telemetry.result(
                    plan,
                    dispatch_id=did,
                    actual_tier="STANDARD",
                    provider="test",
                    model="test-model",
                    outcome="ok",
                    retry_count=0,
                    latency_ms=1,
                    prompt_tokens=1,
                    completion_tokens=1,
                    cache_read_tokens=0,
                    cache_write_tokens=0,
                    cost_bucket=bucket,
                )
            summary = telemetry.summarize(plan)
            self.assertIn("cost_buckets", summary)
            for key in buckets:
                self.assertIn(key, summary["cost_buckets"])

    def test_uc_profile_gov_golden(self):
        # @lat: [[frontend-context#Acceptance G31–G42#UC-PROFILE-GOV Golden]]
        out = route(
            safe_facts(
                governed=True,
                security_sensitive_touch=True,
                security_boundary_change=False,
            )
        )
        self.assertEqual(out["work_class"], "BOUNDED")
        self.assertEqual(out["governance_profile"], "LEAN")
        gate = ux_mod.reuse_gate(
            {
                "same_ux_role": True,
                "existing_surface": {"surface_id": "desktop:sidebar.footer.identity"},
                "decision": "EXTEND",
            }
        )
        self.assertTrue(gate["ok"])
        self.assertEqual(gate["decision"], "EXTEND")


class ChaosAndClosure(unittest.TestCase):
    def test_hard_risk_beats_stale_pass(self):
        # @lat: [[ges-tests#Acceptance Closure#Hard risk beats stale pass]]
        sys.path.insert(0, str(ROOT / ".agents/skills/smc-plan-review/scripts"))
        from assess_plan_review import classify  # noqa: WPS433

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(
                root,
                "p.plan.md",
                """---
plan_id: risk-delta
plan_contract: smc.plan.v3.5
---
# Demo
safe change
""",
            )
            review_record.record("plan", plan, "PASS", "r")
            # mutate with structured high risk snapshot
            facts = {k: False for k in RISKS}
            facts["schema_migration"] = True
            plan.write_text(
                plan.read_text(encoding="utf-8")
                + f"\n## Governance Profile\n\n- Risk Facts Snapshot: `{json.dumps(facts)}`\n",
                encoding="utf-8",
            )
            out = classify(plan)
            self.assertEqual(out["depth"], "FULL")
            reasons = out["reasons"]
            self.assertTrue(
                "PLAN_REVIEW_CURRENT_RISK_FULL_REQUIRED" in reasons
                or "PLAN_REVIEW_HARD_RISK_FULL_REQUIRED" in reasons
            )

    def test_snapshot_invalid_forces_full(self):
        # @lat: [[ges-tests#Acceptance Closure#Invalid snapshot forces full]]
        status, facts = parse_risk_snapshot("Risk Facts Snapshot: `{not-json`")
        self.assertEqual(status, "INVALID")
        self.assertIsNone(facts)

    def test_authority_required_for_cli_none(self):
        # @lat: [[ges-tests#Acceptance Closure#Authority required for production none]]
        f = safe_facts(
            research_intent=True,
            governed=False,
            retained_production_change=False,
            production_write_requested=False,
            durable_product_artifact_requested=False,
        )
        out = route(f, require_authority_for_none=True)
        self.assertNotEqual(out["governance_profile"], "NONE")
        self.assertIn("WORK_AUTHORITY_MISSING", out["reasons"])

    def test_no_fulltext_blocking_on_negation(self):
        # @lat: [[ges-tests#Acceptance Closure#No fulltext blocking on negation]]
        mod = _load("be2", ROOT / ".agents/skills/smc-backend-preplan/scripts/validate_prd_intent.py")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "prd.md"
            p.write_text(
                """governance_profile: LEAN

## Backend Design Intent

| Change ID | Owner | Contract | Data/Transaction | Auth | Idempotency/Concurrency | Failure Semantics | Observability |
|---|---|---|---|---|---|---|---|
| C01 | svc | UNCHANGED | WRITE | UNCHANGED | UNCHANGED | fail closed | logs |

No migration. No BREAKING_CHANGE. No NEW_BOUNDARY.
""",
                encoding="utf-8",
            )
            errors = mod.validate(p)
            self.assertFalse(any(e["code"] == "BACKEND_PREPLAN_FULL_REQUIRED" for e in errors))


def main() -> int:
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(GoldenCorpus))
    suite.addTests(loader.loadTestsFromTestCase(ChaosAndClosure))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "schema": "smc.ges.acceptance.report.v1",
        "passed": result.wasSuccessful(),
        "tests": result.testsRun,
        "failures": len(result.failures) + len(result.errors),
        "golden": "G01-G42",
        "chaos": True,
    }
    print(json.dumps(report, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
