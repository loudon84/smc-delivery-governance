#!/usr/bin/env python3
"""Frontend Context Audit — static scan + adoption modes (OBSERVE/GUIDED/ENFORCED)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
CONTEXT_ENGINE = PACKAGE / "context-engine"
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))
if str(CONTEXT_ENGINE) not in sys.path:
    sys.path.insert(0, str(CONTEXT_ENGINE))

import common as C  # noqa: E402
import frontend_app_registry as registry_mod  # noqa: E402
import ux_context_resolver as ux_mod  # noqa: E402

ADOPTION_MODES = ("OBSERVE", "GUIDED", "ENFORCED")
ADOPTION_SCHEMA = "smc.ges.frontend-adoption.v1"
ADOPTION_REL = f"{C.FRONTEND_ROOT}/adoption-mode.json"
ENFORCED_MARKER_REL = f"{C.FRONTEND_ROOT}/ENFORCED"
REGISTRY_REL = f"{C.FRONTEND_ROOT}/apps-registry.json"


def _load_adoption(project: Path) -> str:
    marker = C.bounded(project, ENFORCED_MARKER_REL)
    if marker.is_file():
        return "ENFORCED"
    path = C.bounded(project, ADOPTION_REL)
    if path.is_file():
        try:
            data = C.read_json(path)
            mode = str(data.get("mode") or "OBSERVE").upper()
            if mode in ADOPTION_MODES:
                return mode
        except Exception:
            return "OBSERVE"
    return "OBSERVE"


def _write_adoption(project: Path, mode: str) -> Path:
    mode = mode.upper()
    if mode not in ADOPTION_MODES:
        raise ValueError(f"FRONTEND_ADOPTION_MODE_INVALID: {mode}")
    path = C.bounded(project, ADOPTION_REL)
    C.dump_json(
        path,
        {
            "schema": ADOPTION_SCHEMA,
            "mode": mode,
            "updated_at": C.utc_now(),
        },
    )
    marker = C.bounded(project, ENFORCED_MARKER_REL)
    if mode == "ENFORCED":
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("ENFORCED\n", encoding="utf-8", newline="\n")
    elif marker.is_file():
        marker.unlink()
    return path


def _adapter_available(stack_adapter: str) -> bool:
    if not stack_adapter:
        return False
    path = PACKAGE / "frontend-adapters" / stack_adapter / "adapter.json"
    return path.is_file()


def _scan(project: Path) -> dict[str, Any]:
    """Layer-1 static scan via context-engine (no LLM, no persist)."""
    discovered = registry_mod.discover(project, persist=False)
    apps = list(discovered.get("apps") or [])
    adapters: dict[str, bool] = {}
    for app in apps:
        adapter = str(app.get("stack_adapter") or "generic")
        adapters[adapter] = _adapter_available(adapter)
    shared = list(discovered.get("shared_ui") or [])
    return {
        "apps": apps,
        "shared_ui": shared,
        "adapters": adapters,
        "registry_schema": discovered.get("schema"),
    }


def _semantic_roles(project: Path, apps: list[dict[str, Any]]) -> dict[str, Any]:
    """Layer-2 limited UX role classification from existing registries (read-only)."""
    roles: dict[str, list[str]] = {}
    for app in apps:
        app_id = str(app.get("app_id") or "")
        if not app_id:
            continue
        found: list[str] = []
        reg_path = project / C.FRONTEND_ROOT / "apps" / app_id / "surface-registry.json"
        if reg_path.is_file():
            try:
                data = C.read_json(reg_path)
                for s in data.get("surfaces") or []:
                    role = s.get("ux_role")
                    if role and role not in found:
                        found.append(str(role))
            except Exception as exc:
                roles[app_id] = [f"error:{exc}"]
                continue
        roles[app_id] = found
    return {"ux_roles_by_app": roles}


def _calibration_checklist(scan: dict[str, Any]) -> list[str]:
    """Layer-3 human/visual calibration prompts (reported, not auto-applied)."""
    items = [
        "Confirm Sidebar / Header / Workspace / Settings / Account / Navigation regions",
        "Confirm identity_control surfaces match product UX (avatar/profile/logout)",
        "Confirm shared UI packages are correctly classified (no business surfaces)",
    ]
    if not scan.get("apps"):
        items.insert(0, "No frontend apps discovered — confirm repo layout or stack markers")
    return items


def audit(
    project: Path,
    *,
    mode: str | None = None,
    apply: bool = False,
    app_specs: list[str] | None = None,
) -> dict[str, Any]:
    # @lat: [[consumer-bootstrap#Frontend Audit]]
    # @lat: [[frontend-context#Scoped Install]]
    project = project.resolve()
    adoption = (mode or _load_adoption(project)).upper()
    if adoption not in ADOPTION_MODES:
        raise ValueError(f"FRONTEND_ADOPTION_MODE_INVALID: {adoption}")

    # Resolve scope before any writes (fail-closed, zero writes on unknown)
    selected_ids: list[str] | None = None
    if app_specs:
        try:
            selected_ids = registry_mod.resolve_scope_identifiers(project, app_specs)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc

    applied: list[str] = []
    if apply:
        _write_adoption(project, adoption)
        applied.append(ADOPTION_REL)
        # Discover + write full repository registry (never scoped-down)
        discovered = registry_mod.discover(project)
        applied.append(REGISTRY_REL)
        apps = list(discovered.get("apps") or [])
        targets = apps
        if selected_ids is not None:
            wanted = set(selected_ids)
            targets = [a for a in apps if a.get("app_id") in wanted]
        for app in targets:
            app_id = str(app.get("app_id") or "")
            if not app_id:
                continue
            ux_mod.generate_baseline(project, app_id)
            applied.append(f"{C.FRONTEND_ROOT}/apps/{app_id}/")
        # Shared UI always refreshed on any scoped or full apply
        registry_mod.resolve_shared_components(project)
        # Force rewrite shared registry even if already present
        registry_mod.discover(project)
        applied.append(f"{C.FRONTEND_ROOT}/shared/shared-ui-registry.json")
        registry_mod.refresh_baseline_statuses(project)

    scan = _scan(project)
    # Prefer loaded registry after apply / existing install.
    existing = registry_mod.load_registry(project)
    registry_present = existing is not None and C.exists_file(project, REGISTRY_REL)

    app_list = list((existing or scan).get("apps") or [])
    semantic = _semantic_roles(project, app_list)
    if not registry_present and adoption in {"GUIDED", "ENFORCED"} and not apply:
        semantic["note"] = "baselines require --apply"

    calibration = _calibration_checklist(scan)

    missing: list[str] = []
    if not registry_present:
        missing.append("apps-registry.json")
    for app in scan.get("apps") or []:
        adapter = str(app.get("stack_adapter") or "")
        if adapter and not _adapter_available(adapter):
            missing.append(f"adapter:{adapter}")

    not_initialized = [
        str(a.get("app_id"))
        for a in app_list
        if a.get("baseline_status") == "NOT_INITIALIZED" and a.get("app_id")
    ]

    layer_present = 1 if registry_present else 0
    layer_total = 1
    verdict = C.layer_verdict(layer_present, layer_total)
    if missing and adoption == "ENFORCED":
        verdict = "MISSING" if not registry_present else "PARTIAL"

    report = {
        "schema": "smc.ges.frontend-audit.v1",
        "project": str(project),
        "audited_at": C.utc_now(),
        "adoption_mode": adoption,
        "applied": apply,
        "applied_paths": applied if apply else [],
        "scope_apps": selected_ids,
        "not_initialized_apps": not_initialized,
        "ok": bool(registry_present) or adoption == "OBSERVE",
        "layers": {
            "static_scan": {
                "verdict": "PASS" if scan.get("apps") is not None else "MISSING",
                "apps_found": len(scan.get("apps") or []),
            },
            "semantic_roles": {
                "verdict": "PASS" if semantic.get("ux_roles_by_app") else "PARTIAL",
                "detail": semantic,
            },
            "calibration": {
                "verdict": "OBSERVE",
                "checklist": calibration,
            },
            "frontend_context": {
                "verdict": verdict,
                "present": layer_present,
                "total": layer_total,
                "missing": missing,
                "registry_present": registry_present,
            },
        },
        "scan": {
            "apps": scan.get("apps") or [],
            "adapters": scan.get("adapters") or {},
            "shared_ui_count": len(scan.get("shared_ui") or []),
        },
        "claims": {
            "frontend_context": (
                "GES_NATIVE"
                if registry_present
                else ("UNAVAILABLE" if adoption == "ENFORCED" else "ADAPTER_READY")
            )
        },
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Frontend Audit Report",
        "",
        f"- Project: `{report['project']}`",
        f"- Audited at: `{report['audited_at']}`",
        f"- Adoption mode: `{report['adoption_mode']}`",
        f"- Overall: `{'PASS' if report['ok'] else 'GAPS'}`",
        f"- Applied: `{report['applied']}`",
        "",
        "## Layers",
        "",
    ]
    for name, layer in report.get("layers", {}).items():
        lines.append(f"- **{name}**: `{layer.get('verdict')}`")
        if layer.get("missing"):
            for m in layer["missing"]:
                lines.append(f"  - missing: `{m}`")
        if layer.get("checklist"):
            for item in layer["checklist"]:
                lines.append(f"  - [ ] {item}")
    lines.extend(["", "## Apps", ""])
    for app in report.get("scan", {}).get("apps") or []:
        lines.append(
            f"- `{app.get('app_id')}` root=`{app.get('root')}` "
            f"adapter=`{app.get('stack_adapter')}`"
        )
    if not report.get("scan", {}).get("apps"):
        lines.append("- *(none discovered)*")
    lines.append("")
    return "\n".join(lines)


def write_reports(project: Path, report: dict[str, Any]) -> tuple[Path, Path]:
    out_dir = C.bounded(project, C.REPORT_DIR_REL)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "frontend-audit.json"
    md_path = out_dir / "frontend-audit.md"
    C.dump_json(json_path, report)
    md_path.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    return json_path, md_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("repo", type=Path, help="consumer repository root")
    ap.add_argument(
        "--mode",
        choices=ADOPTION_MODES,
        default=None,
        help="adoption mode (default: OBSERVE or existing adoption-mode.json)",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="write registry + per-app baselines (dry-run by default)",
    )
    ap.add_argument(
        "--app",
        action="append",
        dest="apps",
        default=None,
        help="target app_id or path (repeatable); omit for full-repo apply",
    )
    ap.add_argument("--json", action="store_true", help="print JSON to stdout")
    a = ap.parse_args()
    project = a.repo.resolve()
    if not (project / ".git").exists():
        print("FRONTEND_AUDIT_FAILED: TARGET_NOT_GIT_REPO", file=sys.stderr)
        return 2
    try:
        report = audit(project, mode=a.mode, apply=a.apply, app_specs=a.apps)
    except ValueError as exc:
        msg = str(exc)
        print(msg, file=sys.stderr)
        if msg.startswith("FRONTEND_SCOPE_APP_UNKNOWN"):
            return 2
        return 1
    jp, mp = write_reports(project, report)
    print(f"FRONTEND_AUDIT_JSON: {jp}")
    print(f"FRONTEND_AUDIT_MD: {mp}")
    if a.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        fc = report["layers"]["frontend_context"]
        scope = ",".join(report.get("scope_apps") or []) or "(all)"
        print(
            f"frontend_context: {fc['verdict']} "
            f"mode={report['adoption_mode']} apps={len(report['scan']['apps'])} "
            f"scope={scope}"
        )
        if report.get("not_initialized_apps"):
            print("not_initialized:", ",".join(report["not_initialized_apps"]))
        print("OVERALL:", "PASS" if report["ok"] else "GAPS")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
