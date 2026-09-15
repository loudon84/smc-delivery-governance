#!/usr/bin/env python3
"""Unit tests for GES v5.0.6 Frontend Context Engine."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "context-engine"
sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(ROOT))

import context_cache as cache_mod  # noqa: E402
import frontend_app_registry as registry_mod  # noqa: E402
import stack_classifier as stack_mod  # noqa: E402
import token_budget as budget_mod  # noqa: E402
import ux_context_resolver as ux_mod  # noqa: E402
import work_scope as scope_mod  # noqa: E402


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def minimal_git(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)


class ContextEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.r = Path(self.tmp.name)
        minimal_git(self.r)
        cache_mod.reset_default()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    # @lat: [[frontend-context#Tests#Discover single electron app]]
    def test_discover_single_electron_app(self) -> None:
        write(
            self.r,
            "package.json",
            json.dumps(
                {
                    "name": "desktop",
                    "dependencies": {"react": "18.0.0", "electron": "28.0.0"},
                }
            )
            + "\n",
        )
        write(self.r, "src/renderer/App.tsx", "export default function App(){return null}\n")
        write(self.r, "src/main/index.ts", "console.log('main')\n")
        data = registry_mod.discover(self.r)
        self.assertEqual(data["schema"], "smc.ges.frontend-app-registry.v2")
        self.assertIn("repository", data)
        self.assertEqual(len(data["apps"]), 1)
        app = data["apps"][0]
        self.assertEqual(app["app_id"], "desktop")
        self.assertEqual(app["root"], "src/renderer")
        self.assertEqual(app["stack_adapter"], "react-electron")
        self.assertIn(app.get("baseline_status"), {"INITIALIZED", "NOT_INITIALIZED", "STALE"})
        self.assertTrue((self.r / ".agents/ges/frontend/apps-registry.json").is_file())

    # @lat: [[frontend-context#Tests#Monorepo app isolation]]
    def test_monorepo_two_apps_isolation(self) -> None:
        write(
            self.r,
            "apps/desktop/package.json",
            json.dumps({"name": "desktop", "dependencies": {"react": "18.0.0", "electron": "28.0.0"}}) + "\n",
        )
        write(self.r, "apps/desktop/src/App.tsx", "export default function App(){return null}\n")
        write(
            self.r,
            "apps/web/package.json",
            json.dumps({"name": "web", "dependencies": {"vue": "3.4.0"}}) + "\n",
        )
        write(self.r, "apps/web/src/App.vue", "<template><div/></template>\n")
        data = registry_mod.discover(self.r)
        ids = sorted(a["app_id"] for a in data["apps"])
        self.assertEqual(ids, ["desktop", "web"])
        self.assertFalse(registry_mod.cross_app_surface_allowed("desktop", "web"))
        self.assertFalse(registry_mod.cross_app_surface_allowed("web", "desktop"))

    # @lat: [[frontend-context#Tests#Reuse gate decisions]]
    def test_reuse_gate_extend_and_add_new_blocked(self) -> None:
        extend = ux_mod.reuse_gate(
            {
                "same_ux_role": True,
                "existing_surface": {"surface_id": "desktop:sidebar.footer.identity"},
                "decision": "ADD_NEW",
            }
        )
        self.assertTrue(extend["ok"])
        self.assertEqual(extend["decision"], "EXTEND")

        blocked = ux_mod.reuse_gate({"decision": "ADD_NEW"})
        self.assertFalse(blocked["ok"])
        self.assertEqual(blocked["code"], "UX_SURFACE_REUSE_REQUIRED")

        allowed = ux_mod.reuse_gate(
            {
                "decision": "ADD_NEW",
                "NEW_SURFACE_JUSTIFICATION": "no existing identity surface",
            }
        )
        self.assertTrue(allowed["ok"])
        self.assertEqual(allowed["decision"], "ADD_NEW")

    # @lat: [[frontend-context#Tests#Incremental refresh scoped]]
    def test_incremental_refresh_only_desktop(self) -> None:
        write(
            self.r,
            "apps/desktop/package.json",
            json.dumps({"name": "desktop", "dependencies": {"react": "18.0.0"}}) + "\n",
        )
        write(
            self.r,
            "apps/desktop/src/Layout.tsx",
            "export function Layout(){return null}\n",
        )
        write(
            self.r,
            "apps/desktop/src/ProfileSwitcher.tsx",
            "export function ProfileSwitcher(){return null}\n",
        )
        write(
            self.r,
            "apps/web/package.json",
            json.dumps({"name": "web", "dependencies": {"vue": "3.4.0"}}) + "\n",
        )
        write(self.r, "apps/web/src/App.vue", "<template><div/></template>\n")
        registry_mod.discover(self.r)
        ux_mod.generate_baseline(self.r, "desktop")
        ux_mod.generate_baseline(self.r, "web")

        result = ux_mod.incremental_refresh(self.r, ["apps/desktop/src/ProfileSwitcher.tsx"])
        self.assertFalse(result["full_rescan"])
        self.assertEqual(result["refreshed_apps"], ["desktop"])
        self.assertIn("web", result["untouched_apps"])
        self.assertNotIn("web", result["refreshed_apps"])

    # @lat: [[frontend-context#Tests#Shared UI reuse]]
    def test_shared_ui_reuse_decision(self) -> None:
        write(
            self.r,
            "apps/desktop/package.json",
            json.dumps({"name": "desktop", "dependencies": {"react": "18.0.0"}}) + "\n",
        )
        write(self.r, "apps/desktop/src/App.tsx", "export default function App(){return null}\n")
        write(
            self.r,
            "packages/ui/package.json",
            json.dumps({"name": "@smc/ui"}) + "\n",
        )
        write(
            self.r,
            "packages/ui/ProfileAvatar.tsx",
            "export function ProfileAvatar(){return null}\n",
        )
        registry_mod.discover(self.r)
        decision = registry_mod.shared_ui_reuse_decision(self.r, "ProfileAvatar")
        self.assertEqual(decision["decision"], "REUSE")
        shared = registry_mod.resolve_shared_components(self.r)
        self.assertEqual(shared["schema"], "smc.ges.shared-ui-registry.v1")
        self.assertTrue((self.r / ".agents/ges/frontend/shared/shared-ui-registry.json").is_file())

    # @lat: [[frontend-context#Tests#Stack classifier electron]]
    def test_stack_classifier_react_electron(self) -> None:
        write(
            self.r,
            "package.json",
            json.dumps(
                {
                    "name": "desktop",
                    "dependencies": {"react": "18.0.0", "electron": "28.0.0"},
                }
            )
            + "\n",
        )
        write(self.r, "src/renderer/App.tsx", "export default function App(){return null}\n")
        result = stack_mod.classify(self.r, "src/renderer")
        self.assertEqual(result["stack_adapter"], "react-electron")

    # @lat: [[frontend-context#Tests#Token budget lean full]]
    def test_token_budget_lean_vs_full(self) -> None:
        lean = budget_mod.budget_for("LEAN")
        self.assertEqual(lean["model_max_tier"], "STANDARD")
        self.assertFalse(lean["independent_review"])
        self.assertEqual(lean["max_review_rounds"], 1)
        self.assertEqual(lean["context_mode"], "targeted")
        self.assertEqual(lean["repeated_context_read"], "cache_first")

        full = budget_mod.budget_for("FULL")
        self.assertEqual(full["model_max_tier"], "REASONING")
        self.assertTrue(full["independent_review"])
        self.assertEqual(full["context_mode"], "expanded")

    # @lat: [[frontend-context#Tests#Context cache hit]]
    def test_context_cache_hit_on_same_sha(self) -> None:
        content = "export const x = 1\n"
        sha = cache_mod.content_sha256(content)
        cache_mod.put("desktop", "src/App.tsx", sha, {"parsed": True})
        hit = cache_mod.get("desktop", "src/App.tsx", sha)
        self.assertEqual(hit, {"parsed": True})
        value, was_hit = cache_mod._DEFAULT.cache_first_read("desktop", "src/App.tsx", content)
        self.assertTrue(was_hit)
        self.assertEqual(value, {"parsed": True})
        self.assertGreaterEqual(cache_mod._DEFAULT.hits, 2)

    # @lat: [[frontend-context#Tests#Component scan excludes build artifacts]]
    def test_component_scan_excludes_dist_and_uses_adapter_globs(self) -> None:
        write(
            self.r,
            "apps/work/package.json",
            json.dumps(
                {
                    "name": "work",
                    "dependencies": {"react": "18.0.0", "electron": "28.0.0"},
                    "devDependencies": {"electron-vite": "5.0.0"},
                }
            )
            + "\n",
        )
        write(self.r, "apps/work/src/renderer/src/App.tsx", "export default function App(){return null}\n")
        write(self.r, "apps/work/src/main/index.ts", "console.log('main')\n")
        write(self.r, "apps/work/out/renderer/chunk.js", "console.log('built')\n")
        write(self.r, "apps/work/dist/win/app.js", "console.log('dist')\n")
        write(self.r, "apps/work/references/chatbox/src/renderer/App.tsx", "export default function Ref(){return null}\n")
        registry_mod.discover(self.r)
        ux_mod.generate_baseline(self.r, "work")
        comps = json.loads(
            (self.r / ".agents/ges/frontend/apps/work/component-registry.json").read_text(encoding="utf-8")
        )["components"]
        paths = [c["path"].replace("\\", "/") for c in comps]
        self.assertTrue(any(p.endswith("src/renderer/src/App.tsx") for p in paths))
        self.assertFalse(any("/out/" in p for p in paths))
        self.assertFalse(any("/dist/" in p for p in paths))
        self.assertFalse(any("/references/" in p for p in paths))
        baseline = json.loads(
            (self.r / ".agents/ges/frontend/apps/work/ui-baseline.json").read_text(encoding="utf-8")
        )
        self.assertEqual(baseline.get("provenance"), "generated")
        self.assertEqual(baseline.get("calibration_status"), "PENDING")
        # Unavailable must not become navigation via substring "nav"
        write(self.r, "apps/work/src/renderer/src/UnavailableBanner.tsx", "export default function X(){return null}\n")
        write(self.r, "apps/work/src/renderer/src/ProfileSwitcher.tsx", "export function ProfileSwitcher(){return null}\n")
        ux_mod.generate_baseline(self.r, "work")
        surfaces2 = json.loads(
            (self.r / ".agents/ges/frontend/apps/work/surface-registry.json").read_text(encoding="utf-8")
        )["surfaces"]
        for s in surfaces2:
            self.assertFalse(
                s["owner"].replace("\\", "/").endswith("UnavailableBanner.tsx")
                and s["ux_role"] == "navigation"
            )
        self.assertTrue(any("ProfileSwitcher" in s["owner"] for s in surfaces2))

    def test_work_scope_schema(self) -> None:
        write(
            self.r,
            "apps/web/package.json",
            json.dumps({"name": "web", "dependencies": {"react": "18.0.0"}}) + "\n",
        )
        write(self.r, "apps/web/src/App.tsx", "export default function App(){return null}\n")
        scope = scope_mod.resolve_work_scope(self.r, governance_profile="LEAN")
        self.assertEqual(scope["schema"], "smc.ges.work-scope.v1")
        self.assertEqual(scope["governance_tip"], "LEAN")
        self.assertEqual(scope["token_budget"]["model_max_tier"], "STANDARD")
        self.assertIn("web", scope["target_apps"])

    # @lat: [[adaptive-governance-context-v508#上下文预算与缓存]]
    def test_context_budget_lean_to_full_then_block(self) -> None:
        import budget_controller as budget_ctrl

        policy = budget_ctrl.load_policy()
        self.assertEqual(policy["schema"], "smc.ges.context-budget-policy.v1")
        ok = budget_ctrl.decide_budget(
            work_item_id="wi-budget",
            repo_identity=str(self.r),
            governance_profile="LEAN",
            candidates=[{"path": f"src/a{i}.ts", "tokens": 100} for i in range(3)],
        )
        self.assertEqual(ok["status"], "OK")
        self.assertEqual(ok["governance_profile"], "LEAN")

        huge = [{"path": f"src/f{i}.ts", "tokens": 5000} for i in range(50)]
        upgraded = budget_ctrl.decide_budget(
            work_item_id="wi-budget",
            repo_identity=str(self.r),
            governance_profile="LEAN",
            candidates=huge,
        )
        self.assertIn("LEAN_TO_FULL", upgraded.get("upgrades") or [])
        # FULL still insufficient → block
        blocked = budget_ctrl.decide_budget(
            work_item_id="wi-budget",
            repo_identity=str(self.r),
            governance_profile="LEAN",
            candidates=[{"path": f"src/x{i}.ts", "tokens": 20000} for i in range(200)],
        )
        self.assertEqual(blocked["status"], "BLOCKED")
        self.assertEqual(blocked.get("error"), "CONTEXT_BUDGET_INSUFFICIENT")

        trimmed = budget_ctrl.trim_candidates(
            [{"path": "apps/work/a.ts"}, {"path": "apps/other/b.ts"}, {"path": "apps/work/a.ts"}],
            allowed_roots=["apps/work"],
        )
        self.assertEqual(len(trimmed), 1)

    def test_capsule_cache_hit_and_stale(self) -> None:
        store = cache_mod.CapsuleStore(self.r, "wi-cache", ttl_seconds=3600)
        key_kw = dict(
            repo_identity=str(self.r),
            artifact_kind="SOURCE",
            scope_digest="sha256:scope1",
            identity="apps/work/src/App.tsx",
            content_sha256=cache_mod.content_sha256(" const x=1 "),
            extractor_version="1.0.0",
            policy_digest="sha256:policy1",
        )
        store.put_capsule(**key_kw, value={"excerpt": "x=1"}, persist=True)
        hit = store.get_capsule(**key_kw)
        self.assertEqual(hit, {"excerpt": "x=1"})
        self.assertGreaterEqual(store.hits, 1)

        # Same key with expired TTL → CONTEXT_CACHE_STALE path.
        mem_key = cache_mod.make_capsule_key(**key_kw)
        store._memory[mem_key]["stored_at"] = 0
        stale = store.get_capsule(**key_kw)
        self.assertIsNone(stale)
        self.assertGreaterEqual(store.stale, 1)

        miss = store.get_capsule(**{**key_kw, "policy_digest": "sha256:other"})
        self.assertIsNone(miss)
        self.assertGreaterEqual(store.misses, 1)

        with self.assertRaises(ValueError):
            store.put_capsule(**key_kw, value={"api_key": "x"})

        escaped = cache_mod.CapsuleStore(self.r, "../escape")
        with self.assertRaises(ValueError):
            escaped.root()


if __name__ == "__main__":
    raise SystemExit(unittest.main())
