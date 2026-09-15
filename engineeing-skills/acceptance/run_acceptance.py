#!/usr/bin/env python3
"""Deterministic Acceptance Closure golden + chaos cases (G01–G60 real behavior)."""
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
from work_router import REQUIRED, RISKS, derive_feature_complexity, route  # noqa: E402
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
import budget_controller as budget_ctrl  # noqa: E402
import context_cache as cache_mod  # noqa: E402
import classification_state as class_state  # noqa: E402
import contract_resolver  # noqa: E402
import work_facts as wf  # noqa: E402


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

    def _seed_dual_apps(self, root: Path) -> None:
        _write(
            root,
            "apps/work/package.json",
            json.dumps({"name": "work", "dependencies": {"react": "18.0.0", "electron": "28.0.0"}}) + "\n",
        )
        _write(root, "apps/work/src/Layout.tsx", "export function Layout(){return null}\n")
        _write(root, "apps/work/src/ProfileSwitcher.tsx", "export function ProfileSwitcher(){return null}\n")
        _write(root, "apps/work/src/UserCenter.tsx", "export function UserCenter(){return null}\n")
        _write(
            root,
            "apps/admin/package.json",
            json.dumps({"name": "admin", "dependencies": {"vue": "3.4.0"}}) + "\n",
        )
        _write(root, "apps/admin/src/App.vue", "<template><div/></template>\n")
        _write(root, "apps/admin/src/UserCenter.vue", "<template><div/></template>\n")

    def _frontend_audit(self, root: Path, *extra: str) -> subprocess.CompletedProcess:
        cmd = [sys.executable, str(ROOT / "consumer-bootstrap" / "frontend_audit.py"), str(root), *extra]
        return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)

    def test_g43_scoped_init_single_app(self):
        # @lat: [[frontend-context#Acceptance G43–G50#G43 Scoped Init Single App]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            self._seed_dual_apps(root)
            proc = self._frontend_audit(root, "--app", "work", "--apply")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue((root / ".agents/ges/frontend/apps/work/surface-registry.json").is_file())
            self.assertFalse((root / ".agents/ges/frontend/apps/admin").exists())
            reg = json.loads((root / ".agents/ges/frontend/apps-registry.json").read_text(encoding="utf-8"))
            ids = {a["app_id"]: a for a in reg["apps"]}
            self.assertIn("work", ids)
            self.assertIn("admin", ids)
            self.assertEqual(ids["work"]["baseline_status"], "INITIALIZED")
            self.assertEqual(ids["admin"]["baseline_status"], "NOT_INITIALIZED")

    def test_g44_scoped_init_idempotent(self):
        # @lat: [[frontend-context#Acceptance G43–G50#G44 Scoped Init Idempotent]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            self._seed_dual_apps(root)
            self.assertEqual(self._frontend_audit(root, "--app", "work", "--apply").returncode, 0)
            p = root / ".agents/ges/frontend/apps/work/surface-registry.json"
            first = p.read_bytes()
            self.assertEqual(self._frontend_audit(root, "--app", "work", "--apply").returncode, 0)
            second = p.read_bytes()
            self.assertEqual(first, second)

    def test_g45_scoped_init_preserves_siblings(self):
        # @lat: [[frontend-context#Acceptance G43–G50#G45 Scoped Init Preserves Siblings]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            self._seed_dual_apps(root)
            self.assertEqual(self._frontend_audit(root, "--app", "work", "--apply").returncode, 0)
            work_surf = (root / ".agents/ges/frontend/apps/work/surface-registry.json").read_bytes()
            self.assertEqual(self._frontend_audit(root, "--app", "admin", "--apply").returncode, 0)
            self.assertTrue((root / ".agents/ges/frontend/apps/admin/surface-registry.json").is_file())
            self.assertEqual(
                work_surf,
                (root / ".agents/ges/frontend/apps/work/surface-registry.json").read_bytes(),
            )

    def test_g46_scope_identifier_normalization(self):
        # @lat: [[frontend-context#Acceptance G43–G50#G46 Scope Identifier Normalization]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            self._seed_dual_apps(root)
            registry_mod.discover(root, persist=True)
            a = registry_mod.resolve_scope_identifiers(root, ["work"])
            b = registry_mod.resolve_scope_identifiers(root, ["apps/work"])
            c = registry_mod.resolve_scope_identifiers(root, ["apps/work/"])
            self.assertEqual(a, b)
            self.assertEqual(b, c)
            self.assertEqual(a, ["work"])
            with self.assertRaises(ValueError) as ctx:
                registry_mod.resolve_scope_identifiers(root, ["does-not-exist"])
            self.assertIn("FRONTEND_SCOPE_APP_UNKNOWN", str(ctx.exception))
            before = list((root / ".agents/ges/frontend").rglob("*")) if (root / ".agents/ges/frontend").exists() else []
            proc = self._frontend_audit(root, "--app", "nope", "--apply")
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("FRONTEND_SCOPE_APP_UNKNOWN", proc.stderr)
            after = list((root / ".agents/ges/frontend").rglob("*")) if (root / ".agents/ges/frontend").exists() else []
            self.assertEqual(len(before), len(after))

    def test_g47_nested_shared_ui_discovery(self):
        # @lat: [[frontend-context#Acceptance G43–G50#G47 Nested Shared UI Discovery]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            _write(
                root,
                "apps/work/package.json",
                json.dumps({"name": "work", "dependencies": {"react": "18.0.0"}}) + "\n",
            )
            _write(root, "apps/work/src/App.tsx", "export default function App(){return null}\n")
            _write(root, "packages/shared/ui/package.json", json.dumps({"name": "@smc/shared-ui"}) + "\n")
            _write(root, "packages/shared/ui/Button.tsx", "export function Button(){return null}\n")
            data = registry_mod.discover(root)
            roots = [s["root"] for s in data.get("shared_ui") or []]
            self.assertIn("packages/shared/ui", roots)
            app_ids = [a["app_id"] for a in data.get("apps") or []]
            self.assertNotIn("ui", app_ids)
            self.assertNotIn("shared", app_ids)

    def test_g48_application_boundary_deny(self):
        # @lat: [[frontend-context#Acceptance G43–G50#G48 Application Boundary Deny]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            self._seed_dual_apps(root)
            registry_mod.discover(root)
            ux_mod.generate_baseline(root, "work")
            profile = json.loads(
                (root / ".agents/ges/frontend/apps/work/app-profile.json").read_text(encoding="utf-8")
            )
            self.assertEqual(profile["schema"], "smc.ges.app-profile.v2")
            self.assertIn("apps/work", profile["boundary"]["allowed_roots"])
            self.assertIn("apps/admin", profile["boundary"]["forbidden_roots"])
            surf = json.loads(
                (root / ".agents/ges/frontend/apps/work/surface-registry.json").read_text(encoding="utf-8")
            )
            for s in surf.get("surfaces") or []:
                self.assertNotIn("apps/admin", str(s.get("owner") or ""))

    def test_g49_frontend_runtime_installed(self):
        # @lat: [[frontend-context#Acceptance G43–G50#G49 Frontend Runtime Installed]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            _write(root, "AGENTS.md", "# policy\n")
            for name in ("code-review-and-quality", "verification-before-completion"):
                _write(root, f".agents/skills/{name}/SKILL.md", f"---\nname: {name}\n---\n# stub\n")
            # Minimal profile + domain packs via install_metadata path
            backup = root / ".smc" / "skill-upgrade-backups" / "g49"
            backup.mkdir(parents=True)
            records: dict = {}
            _, profile = installer.resolve_profile(root, "generic")
            _, selected = installer.pack_context(profile)
            installer.install_metadata(root, profile, selected, backup, records)
            self.assertTrue((root / ".agents/ges/frontend-runtime/frontend_app_registry.py").is_file())
            self.assertTrue((root / ".agents/ges/frontend-adapters/react-web/adapter.json").is_file())
            owned = [
                r
                for r in records
                if str(r).replace("\\", "/").startswith(".agents/ges/frontend-runtime/")
                or str(r).replace("\\", "/").startswith(".agents/ges/frontend-adapters/")
            ]
            self.assertTrue(owned)

    def test_g50_feature_scope_pipeline(self):
        # @lat: [[frontend-context#Acceptance G43–G50#G50 Feature Scope Pipeline]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            self._seed_dual_apps(root)
            registry_mod.discover(root)
            ux_mod.generate_baseline(root, "work")
            result = ux_mod.resolve_feature_scope(
                root,
                app_id="work",
                ux_role="identity_control",
                component_name="ProfileSwitcher",
            )
            self.assertEqual(result["schema"], "smc.ges.feature-scope.v1")
            for key in ("application", "surface", "layout_owner", "component_reuse"):
                self.assertIn(key, result)
                self.assertIsNotNone(result[key])
            self.assertEqual(result["decision"], "EXTEND")
            self.assertTrue(result["ok"])

    def test_g51_deterministic_complexity_receipt(self):
        # @lat: [[adaptive-governance-context-v508#Acceptance G51–G60#G51 Deterministic Complexity Receipt]]
        routed = route(safe_facts())
        scope = {
            "schema": "smc.ges.feature-scope.v1",
            "app_id": "work",
            "surface_id": "work:sidebar.footer.identity",
            "layout_owner": "apps/work/src/Layout.tsx",
            "decision": "EXTEND",
            "ok": True,
        }
        a = derive_feature_complexity(routed, work_item_id="g51", feature_scope=scope)
        b = derive_feature_complexity(routed, work_item_id="g51", feature_scope=scope)
        self.assertEqual(a["schema"], "smc.ges.feature-complexity.v1")
        self.assertEqual(a["work_route_digest"], b["work_route_digest"])
        self.assertEqual(a["feature_scope_digest"], b["feature_scope_digest"])
        self.assertEqual(a["governance_profile"], routed["governance_profile"])

    def test_g52_missing_provenance_not_lean(self):
        # @lat: [[adaptive-governance-context-v508#Acceptance G51–G60#G52 Missing Provenance Not Lean]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            env = {
                "schema": "smc.ges.work-facts.v1",
                "work_item_id": "g52",
                "facts": safe_facts(),
                "provenance": {},
                "facts_digest": "sha256:" + ("0" * 64),
            }
            status, reasons = wf.verify_envelope(env, repo=root)
            self.assertNotEqual(status, "VERIFIED")
            self.assertTrue(reasons)
            self.assertTrue(
                any(
                    r
                    in {
                        "WORK_FACTS_UNBOUND",
                        "WORK_FACTS_PROVENANCE_MISSING",
                        "WORK_FACTS_FIELD_MISSING",
                        "WORK_FACTS_INVALID",
                    }
                    for r in reasons
                )
            )
            out = route(safe_facts(), work_facts=env, repo=root, require_authority_for_none=True)
            self.assertNotEqual(out["governance_profile"], "LEAN")
            receipt = derive_feature_complexity(out, work_item_id="g52")
            self.assertNotEqual(receipt["governance_profile"], "LEAN")

    def test_g53_production_text_never_spike(self):
        # @lat: [[adaptive-governance-context-v508#Acceptance G51–G60#G53 Production Text Never Spike]]
        f = safe_facts(
            research_intent=True,
            governed=False,
            retained_production_change=True,
            production_write_requested=False,
            durable_product_artifact_requested=False,
        )
        out = route(f)
        self.assertNotEqual(out["work_class"], "SPIKE")
        self.assertNotEqual(out["governance_profile"], "NONE")

    def test_g54_frozen_downgrade_denied(self):
        # @lat: [[adaptive-governance-context-v508#Acceptance G51–G60#G54 Downgrade Denied]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            class_state.apply_profile(root, "g54", "FULL")
            class_state.freeze(root, "g54")
            with self.assertRaises(ValueError) as ctx:
                class_state.apply_profile(root, "g54", "LEAN")
            self.assertEqual(str(ctx.exception), "CLASSIFICATION_DOWNGRADE_DENIED")

    def test_g55_lean_v37_ledger_and_delivery_gates(self):
        # @lat: [[adaptive-governance-context-v508#Acceptance G51–G60#G55 Lean Plan Delivery Gates]]
        self.assertEqual(contract_resolver.CURRENT_PLAN_CONTRACT, "smc.plan.v3.7")
        self.assertEqual(contract_resolver.validator_name("smc.plan.v3.7"), "validate_plan_v37.py")
        lean_plan = (
            MIN_PLAN.replace("governance_profile: FULL", "governance_profile: LEAN")
            + """
## Ownership Ledger

| Change ID | Owner | Authority |
|---|---|---|
| C01 | app.py#main | EXISTING |

## Verification Ledger

| Change ID | Evidence | Freshness |
|---|---|---|
| C01 | tests/test_app.py | REQUIRED |
"""
        )
        self.assertIn("plan_contract: smc.plan.v3.7", lean_plan)
        self.assertIn("governance_profile: LEAN", lean_plan)
        for heading in ("## Change Matrix", "## Ownership Ledger", "## Verification Ledger"):
            self.assertIn(heading, lean_plan)
            # LEAN public ledgers must not be N/A placeholders.
            block = lean_plan.split(heading, 1)[1].split("## ", 1)[0]
            self.assertNotIn("| N/A |", block)
        delivery_skill = (ROOT / ".agents/skills/smc-plan-delivery/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("smc.plan.v3.7", delivery_skill)
        self.assertIn("canonical Plan delivery", delivery_skill)

    def test_g56_context_cache_hit(self):
        # @lat: [[adaptive-governance-context-v508#Acceptance G51–G60#G56 Cache Hit]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = cache_mod.CapsuleStore(root, "g56")
            kw = dict(
                repo_identity=str(root),
                artifact_kind="SOURCE",
                scope_digest="sha256:scope",
                identity="apps/work/src/A.tsx",
                content_sha256=cache_mod.content_sha256("alpha"),
                extractor_version="1.0.0",
                policy_digest=budget_ctrl.policy_digest(),
            )
            store.put_capsule(**kw, value={"ok": True})
            self.assertEqual(store.get_capsule(**kw), {"ok": True})
            self.assertGreaterEqual(store.hits, 1)

    def test_g57_context_cache_stale_on_policy_change(self):
        # @lat: [[adaptive-governance-context-v508#Acceptance G51–G60#G57 Cache Stale]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = cache_mod.CapsuleStore(root, "g57")
            kw = dict(
                repo_identity=str(root),
                artifact_kind="SOURCE",
                scope_digest="sha256:scope",
                identity="apps/work/src/A.tsx",
                content_sha256=cache_mod.content_sha256("alpha"),
                extractor_version="1.0.0",
                policy_digest="sha256:old",
            )
            store.put_capsule(**kw, value={"ok": True})
            # Policy change → different key → miss (no cross-policy reuse).
            miss = store.get_capsule(**{**kw, "policy_digest": "sha256:new"})
            self.assertIsNone(miss)
            # Expired binding on the original key → stale.
            key = cache_mod.make_capsule_key(**kw)
            store._memory[key]["stored_at"] = 0
            stale = store.get_capsule(**kw)
            self.assertIsNone(stale)
            self.assertGreaterEqual(store.stale, 1)

    def test_g58_budget_escalate_then_block(self):
        # @lat: [[adaptive-governance-context-v508#Acceptance G51–G60#G58 Budget Escalate Or Block]]
        candidates = [{"path": f"src/{i}.ts", "tokens": 3000} for i in range(40)]
        trimmed = budget_ctrl.trim_candidates(candidates + candidates, allowed_roots=["src"])
        self.assertLess(len(trimmed), len(candidates) * 2)
        decision = budget_ctrl.decide_budget(
            work_item_id="g58",
            repo_identity="repo",
            governance_profile="LEAN",
            candidates=candidates,
        )
        self.assertIn("LEAN_TO_FULL", decision.get("upgrades") or [])
        blocked = budget_ctrl.decide_budget(
            work_item_id="g58",
            repo_identity="repo",
            governance_profile="FULL",
            candidates=[{"path": f"src/{i}.ts", "tokens": 50000} for i in range(200)],
        )
        self.assertEqual(blocked["status"], "BLOCKED")
        self.assertEqual(blocked.get("error"), "CONTEXT_BUDGET_INSUFFICIENT")

    def test_g59_install_fault_rollback_preserves_sibling(self):
        # @lat: [[adaptive-governance-context-v508#Acceptance G51–G60#G59 Install Rollback Sibling]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            self._seed_dual_apps(root)
            self.assertEqual(self._frontend_audit(root, "--app", "work", "--apply").returncode, 0)
            sibling = (root / ".agents/ges/frontend/apps/work/surface-registry.json").read_bytes()
            _write(root, "AGENTS.md", "# Project policy\n")
            for skill in ("code-review-and-quality", "verification-before-completion"):
                _write(root, f".agents/skills/{skill}/SKILL.md", "# consumer-owned\n")
            (root / ".cursor/skills").mkdir(parents=True, exist_ok=True)
            shutil.copytree(ROOT / "domain-packs", root / ".agents/ges/domain-packs")
            profile = json.loads((ROOT / "consumers/generic.json").read_text(encoding="utf-8"))
            _write(root, ".agents/ges/profile.json", json.dumps(profile))
            shutil.copytree(ROOT / "domain-runtime", root / ".agents/ges/domain-runtime")
            shutil.copytree(ROOT / ".agents/skills", root / ".agents/skills", dirs_exist_ok=True)
            _, loaded = installer.resolve_profile(root, None)
            _, packs = installer.pack_context(loaded)
            backup = root / ".smc" / "skill-upgrade-backups" / "g59"
            backup.mkdir(parents=True)
            records: dict = {}
            installer._FINALIZATION_FAULT = "receipt"
            try:
                with self.assertRaises(RuntimeError):
                    installer.build_install_lock(root, loaded, packs, records, backup)
                installer.base.restore(root, backup, records)
            finally:
                installer._FINALIZATION_FAULT = None
            self.assertFalse((root / ".smc/ges-install-lock.json").is_file())
            self.assertFalse((root / ".smc/ges-install-receipt.json").is_file())
            receipts = root / ".smc" / "ges-install-receipts"
            if receipts.is_dir():
                self.assertFalse(any(receipts.glob("*.json")))
            self.assertFalse((root / ".agents/ges/frontend-runtime").exists())
            self.assertEqual(
                sibling,
                (root / ".agents/ges/frontend/apps/work/surface-registry.json").read_bytes(),
            )

    def test_g60_telemetry_redacted(self):
        # @lat: [[adaptive-governance-context-v508#Acceptance G51–G60#G60 Telemetry Redacted]]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _git_init(root)
            plan = _write(root, "p.plan.md", MIN_PLAN)
            with self.assertRaises(ValueError):
                telemetry.dispatch(
                    plan,
                    phase="IMPLEMENT",
                    todo="T1",
                    requested_tier="STANDARD",
                    dispatch_id="g60-bad",
                    agent="acc",
                    prompt="secret prompt text",
                )
            telemetry.dispatch(
                plan,
                phase="IMPLEMENT",
                todo="T1",
                requested_tier="STANDARD",
                dispatch_id="g60",
                agent="acc",
                cost_bucket="IMPLEMENT",
                work_route_digest="sha256:route",
                policy_digest="sha256:policy",
                phase_allocated_tokens=100,
                phase_actual_tokens=40,
                context_cache_hits=1,
                context_cache_misses=0,
                context_cache_stale=0,
                budget_upgrade_reason="LEAN_TO_FULL",
            )
            telemetry.result(
                plan,
                dispatch_id="g60",
                actual_tier="STANDARD",
                provider="test",
                model="test-model",
                outcome="ok",
                retry_count=0,
                latency_ms=1,
                prompt_tokens=2,
                completion_tokens=2,
                cache_read_tokens=0,
                cache_write_tokens=0,
                cost_bucket="IMPLEMENT",
            )
            summary = telemetry.summarize(plan)
            self.assertTrue(summary.get("complete"))
            self.assertEqual(summary.get("work_route_digest"), "sha256:route")
            self.assertEqual(summary.get("budget_upgrade_reason"), "LEAN_TO_FULL")
            blob = json.dumps(summary)
            self.assertNotIn("secret prompt", blob)
            self.assertNotIn("password", blob)

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
        "golden": "G01-G60",
        "chaos": True,
    }
    print(json.dumps(report, indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
