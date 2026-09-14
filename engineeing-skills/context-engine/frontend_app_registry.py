"""Frontend Application Registry — discover apps and shared UI packages."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from stack_classifier import classify

SCHEMA = "smc.ges.frontend-app-registry.v1"
SHARED_SCHEMA = "smc.ges.shared-ui-registry.v1"
FRONTEND_ROOT = Path(".agents") / "ges" / "frontend"
APPS_REGISTRY_REL = FRONTEND_ROOT / "apps-registry.json"
SHARED_REGISTRY_REL = FRONTEND_ROOT / "shared" / "shared-ui-registry.json"

_FRONTEND_MARKERS = (
    "package.json",
    "vite.config.ts",
    "vite.config.js",
    "vite.config.mjs",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "nuxt.config.ts",
    "nuxt.config.js",
    "src/main.tsx",
    "src/main.ts",
    "src/App.tsx",
    "src/App.vue",
    "index.html",
)


def _norm(rel: str) -> str:
    return rel.replace("\\", "/")


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _looks_frontend(root: Path) -> bool:
    for marker in _FRONTEND_MARKERS:
        if (root / marker).exists():
            return True
    return False


def _is_shared_ui_name(name: str) -> bool:
    return name == "ui" or name.endswith("-ui")


def _pkg_name(repo: Path, app_root: Path) -> str | None:
    for candidate in (app_root / "package.json", repo / "package.json"):
        data = _read_json(candidate)
        if data and isinstance(data.get("name"), str) and data["name"].strip():
            name = data["name"].strip()
            # strip scope
            if "/" in name:
                name = name.rsplit("/", 1)[-1]
            return name
    return None


def _app_entry(repo: Path, app_id: str, root_rel: str) -> dict[str, Any]:
    classified = classify(repo, root_rel)
    return {
        "app_id": app_id,
        "root": _norm(root_rel),
        "runtime": classified["runtime"],
        "framework": classified["framework"],
        "stack_adapter": classified["stack_adapter"],
    }


def _discover_shared_ui(repo: Path) -> list[dict[str, Any]]:
    packages = repo / "packages"
    found: list[dict[str, Any]] = []
    if not packages.is_dir():
        return found
    for child in sorted(packages.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if not _is_shared_ui_name(child.name):
            continue
        components = _scan_shared_components(repo, child)
        found.append(
            {
                "package_id": child.name,
                "root": _norm(str(child.relative_to(repo))),
                "kind": "shared-ui-library",
                "components": components,
            }
        )
    return found


def _scan_shared_components(repo: Path, pkg_root: Path) -> list[dict[str, Any]]:
    components: list[dict[str, Any]] = []
    patterns = ("**/*.tsx", "**/*.jsx", "**/*.vue", "**/*.ts", "**/*.js")
    seen: set[str] = set()
    for pattern in patterns:
        for path in sorted(pkg_root.glob(pattern)):
            if not path.is_file():
                continue
            if path.name.startswith(".") or path.name.endswith(".d.ts"):
                continue
            if "node_modules" in path.parts or "__tests__" in path.parts or path.name.endswith(".test.tsx"):
                continue
            rel = _norm(str(path.relative_to(repo)))
            stem = path.stem
            if stem in {"index", "main"}:
                continue
            if stem in seen:
                continue
            seen.add(stem)
            components.append(
                {
                    "name": stem,
                    "path": rel,
                    "reuse": "REUSE",
                }
            )
    return components


# @lat: [[frontend-context#Frontend Application Registry]]
def discover(repo: str | Path, *, persist: bool = True) -> dict[str, Any]:
    """Discover frontend apps and shared UI packages under a consumer repo."""
    root = Path(repo).resolve()
    apps: list[dict[str, Any]] = []
    seen_roots: set[str] = set()

    def add_app(app_id: str, root_rel: str) -> None:
        key = _norm(root_rel)
        if key in seen_roots:
            return
        seen_roots.add(key)
        apps.append(_app_entry(root, app_id, key))

    # Monorepo apps/*
    apps_dir = root / "apps"
    if apps_dir.is_dir():
        for child in sorted(apps_dir.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            if _looks_frontend(child) or (child / "src").is_dir():
                add_app(child.name, str(child.relative_to(root)))

    # packages/* frontend apps (exclude shared UI)
    packages_dir = root / "packages"
    if packages_dir.is_dir():
        for child in sorted(packages_dir.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            if _is_shared_ui_name(child.name):
                continue
            if _looks_frontend(child):
                add_app(child.name, str(child.relative_to(root)))

    # Single-package electron: src/renderer (+ optional src/main)
    renderer = root / "src" / "renderer"
    if renderer.is_dir():
        pkg_name = _pkg_name(root, root) or "desktop"
        add_app(pkg_name, "src/renderer")

    # Electron main alone does not create a second app; fold into existing if present
    # Already covered by renderer discovery for single-package.

    # Root single-package SPA (no apps/, no src/renderer)
    if not apps and _looks_frontend(root):
        pkg_name = _pkg_name(root, root) or "app"
        add_app(pkg_name, ".")

    shared = _discover_shared_ui(root)
    data = {
        "schema": SCHEMA,
        "apps": apps,
        "shared_ui": [{"package_id": s["package_id"], "root": s["root"], "kind": s["kind"]} for s in shared],
    }
    shared_payload = {
        "schema": SHARED_SCHEMA,
        "packages": shared,
    }
    if persist:
        save_registry(root, data)
        _write_json(root / SHARED_REGISTRY_REL, shared_payload)
    return data


def load_registry(repo: str | Path) -> dict[str, Any] | None:
    root = Path(repo).resolve()
    return _read_json(root / APPS_REGISTRY_REL)


def save_registry(repo: str | Path, data: dict[str, Any]) -> Path:
    root = Path(repo).resolve()
    path = root / APPS_REGISTRY_REL
    payload = dict(data)
    payload.setdefault("schema", SCHEMA)
    _write_json(path, payload)
    return path


# @lat: [[frontend-context#Shared UI Registry]]
def resolve_shared_components(repo: str | Path) -> dict[str, Any]:
    """Load or discover shared UI component registry (no business surfaces)."""
    root = Path(repo).resolve()
    existing = _read_json(root / SHARED_REGISTRY_REL)
    if existing and existing.get("schema") == SHARED_SCHEMA:
        return existing
    discover(root)
    return _read_json(root / SHARED_REGISTRY_REL) or {
        "schema": SHARED_SCHEMA,
        "packages": [],
    }


def shared_ui_reuse_decision(repo: str | Path, component_name: str) -> dict[str, Any]:
    """Return REUSE when a named shared UI component exists."""
    registry = resolve_shared_components(repo)
    needle = component_name.strip()
    for pkg in registry.get("packages") or []:
        for comp in pkg.get("components") or []:
            if comp.get("name") == needle or needle in str(comp.get("path") or ""):
                return {
                    "decision": "REUSE",
                    "component": comp,
                    "package_id": pkg.get("package_id"),
                    "reason": "SHARED_UI_COMPONENT_FOUND",
                }
    return {
        "decision": "ADD_NEW",
        "component": None,
        "package_id": None,
        "reason": "SHARED_UI_COMPONENT_MISSING",
    }


def cross_app_surface_allowed(source_app: str, target_app: str) -> bool:
    """Surfaces are never shared across apps (monorepo isolation)."""
    _ = (source_app, target_app)
    return False


def component_reuse_automatic(
    source_stack: str,
    target_stack: str,
    *,
    via_shared_package: bool = False,
) -> dict[str, Any]:
    """Component reuse is automatic only for same stack or shared UI package.

    Different stacks still allow UX Pattern Reuse, but not automatic Component Reuse.
    """
    same = bool(source_stack) and source_stack == target_stack
    component = bool(via_shared_package) or same
    return {
        "component_reuse": component,
        "ux_pattern_reuse": True,
        "automatic": component,
        "reason": (
            "SHARED_PACKAGE"
            if via_shared_package
            else ("SAME_STACK" if same else "DIFFERENT_STACK")
        ),
    }


def find_app_for_path(repo: str | Path, rel_path: str) -> str | None:
    """Map a changed path to an owning app_id, or None for shared/unknown."""
    root = Path(repo).resolve()
    registry = load_registry(root) or discover(root)
    norm = _norm(rel_path)
    # shared UI first
    for shared in registry.get("shared_ui") or []:
        shared_root = _norm(str(shared.get("root") or ""))
        if shared_root and (norm == shared_root or norm.startswith(shared_root.rstrip("/") + "/")):
            return None  # shared, not an app
    best: tuple[int, str] | None = None
    for app in registry.get("apps") or []:
        app_root = _norm(str(app.get("root") or ""))
        app_id = str(app.get("app_id") or "")
        if not app_id:
            continue
        if app_root in {".", ""}:
            # root app owns everything that is not another app's prefix
            continue
        if norm == app_root or norm.startswith(app_root.rstrip("/") + "/"):
            score = len(app_root)
            if best is None or score > best[0]:
                best = (score, app_id)
    if best:
        return best[1]
    # single-package electron: src/renderer maps to that app
    for app in registry.get("apps") or []:
        app_root = _norm(str(app.get("root") or ""))
        if app_root.startswith("src/") and norm.startswith("src/"):
            return str(app.get("app_id"))
    return None


def is_shared_ui_path(repo: str | Path, rel_path: str) -> bool:
    root = Path(repo).resolve()
    registry = load_registry(root) or discover(root)
    norm = _norm(rel_path)
    for shared in registry.get("shared_ui") or []:
        shared_root = _norm(str(shared.get("root") or ""))
        if shared_root and (norm == shared_root or norm.startswith(shared_root.rstrip("/") + "/")):
            return True
    # fallback pattern
    parts = Path(norm).parts
    if len(parts) >= 2 and parts[0] == "packages" and _is_shared_ui_name(parts[1]):
        return True
    return False
