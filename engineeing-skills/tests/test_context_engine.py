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


if __name__ == "__main__":
    raise SystemExit(unittest.main())
