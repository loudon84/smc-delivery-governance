#!/usr/bin/env python3
"""Read-only Consumer Installation Audit for GES + Spec Kit + Superpowers."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))

import common as C  # noqa: E402


def _check_id(layer: str, path: str) -> str:
    cleaned = path.replace("\\", "/").lstrip("./").replace("/", ".")
    return f"{layer}.{cleaned}"


def _check(checks: list[dict], cid: str, layer: str, path: str, present: bool, detail: str = "") -> None:
    checks.append(
        {
            "id": cid,
            "layer": layer,
            "path": path,
            "present": present,
            "detail": detail,
        }
    )


def _audit_ges(project: Path, checks: list[dict]) -> dict[str, Any]:
    items = [
        ("ges.install_lock", ".smc/ges-install-lock.json", "file"),
        ("ges.install_receipt_pointer", ".smc/ges-install-receipt.json", "file"),
        ("ges.profile", ".agents/ges/profile.json", "file"),
        ("ges.domain_registry", ".agents/ges/domain-packs/registry.json", "file"),
        ("ges.domain_runtime", ".agents/ges/domain-runtime/domain_runtime.py", "file"),
        ("ges.plan_validator", ".agents/skills/smc-plan-validator/scripts/validate_plan_v37.py", "file"),
        ("ges.delivery_runtime", ".agents/skills/smc-plan-delivery/scripts/run_selftest.py", "file"),
        ("ges.acceptance_surface", ".agents/skills/smc-plan-delivery/scripts/acceptance.py", "file"),
        ("ges.telemetry", ".agents/skills/smc-plan-delivery/scripts/runtime_metrics.py", "file"),
        ("ges.work_router", ".agents/skills/smc-work-router/SKILL.md", "file"),
    ]
    for cid, rel, kind in items:
        present = C.exists_file(project, rel) if kind == "file" else C.exists_dir(project, rel)
        detail = ""
        if cid == "ges.install_lock" and present:
            try:
                lock = C.read_json(C.bounded(project, rel))
                schema = lock.get("schema")
                detail = f"schema={schema}"
                if schema != "smc.ges.install-lock.v2":
                    present = False
                    detail = f"expected smc.ges.install-lock.v2 got {schema}"
            except Exception as exc:
                present = False
                detail = str(exc)
        if cid == "ges.install_receipt_pointer" and present:
            try:
                ptr = C.read_json(C.bounded(project, rel))
                if ptr.get("schema") != "smc.ges.install-receipt.v1":
                    present = False
                    detail = f"schema={ptr.get('schema')}"
                else:
                    # Prefer immutable receipt when path declared.
                    rp = ptr.get("receipt_path")
                    if rp and not C.exists_file(project, str(rp)):
                        # Also accept directory receipts.
                        receipts = list((project / ".smc" / "ges-install-receipts").glob("*.json")) if (
                            project / ".smc" / "ges-install-receipts"
                        ).is_dir() else []
                        if not receipts:
                            present = False
                            detail = "receipt_path missing"
            except Exception as exc:
                present = False
                detail = str(exc)
        _check(checks, cid, "ges", rel, present, detail)

    # Managed skills presence (SKILL.md)
    for name in C.managed_skills():
        rel = f".agents/skills/{name}/SKILL.md"
        _check(checks, f"ges.managed.{name}", "ges", rel, C.exists_file(project, rel))

    # Consumer-required skills
    core = C.read_json(C.CORE_MANIFEST)
    for name in core.get("consumer_required_skills", []):
        rel = f".agents/skills/{name}/SKILL.md"
        _check(checks, f"ges.consumer_required.{name}", "ges", rel, C.exists_file(project, rel))

    layer_checks = [c for c in checks if c["layer"] == "ges"]
    present_n = sum(1 for c in layer_checks if c["present"])
    missing = [c["id"] for c in layer_checks if not c["present"]]
    return {
        "verdict": C.layer_verdict(present_n, len(layer_checks)),
        "present": present_n,
        "total": len(layer_checks),
        "missing": missing,
    }


def _audit_spec_kit(project: Path, checks: list[dict]) -> tuple[dict[str, Any], dict[str, Any]]:
    for rel in C.SPEC_KIT_SCAFFOLD:
        # .gitkeep may be absent if dir has other files — treat dir presence as enough for templates/scripts.
        if rel.endswith("/.gitkeep"):
            drel = rel.rsplit("/", 1)[0]
            present = C.exists_dir(project, drel)
            _check(checks, _check_id("spec_kit", drel), "spec_kit", drel, present, "directory")
        else:
            _check(checks, _check_id("spec_kit", rel), "spec_kit", rel, C.exists_file(project, rel))

    # Probe Spec Kit CLI (read-only).
    probe_result: dict[str, Any] = {}
    try:
        from integrations.spec_kit.probe import probe  # type: ignore

        probe_result = probe()
    except Exception:
        # Fallback: import by path.
        try:
            import importlib.util

            probe_path = PACKAGE / "integrations" / "spec-kit" / "probe.py"
            spec = importlib.util.spec_from_file_location("ges_spec_kit_probe", probe_path)
            assert spec and spec.loader
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            probe_result = mod.probe()
        except Exception as exc:
            probe_result = {
                "provider": "spec-kit",
                "provider_status": "UNAVAILABLE",
                "integration_status": "NATIVE_ONLY",
                "code": "SPEC_KIT_UNAVAILABLE",
                "detail": str(exc),
            }

    _check(
        checks,
        "spec_kit.probe",
        "spec_kit",
        "integrations/spec-kit/probe.py",
        probe_result.get("provider_status") in {"AVAILABLE", "UNAVAILABLE", "INCOMPATIBLE"},
        detail=json.dumps(
            {
                "provider_status": probe_result.get("provider_status"),
                "integration_status": probe_result.get("integration_status"),
                "code": probe_result.get("code"),
            },
            sort_keys=True,
        ),
    )

    layer_checks = [c for c in checks if c["layer"] == "spec_kit" and c["id"] != "spec_kit.probe"]
    present_n = sum(1 for c in layer_checks if c["present"])
    missing = [c["id"] for c in layer_checks if not c["present"]]
    layer = {
        "verdict": C.layer_verdict(present_n, len(layer_checks)),
        "present": present_n,
        "total": len(layer_checks),
        "missing": missing,
        "provider_status": probe_result.get("provider_status"),
        "integration_status": probe_result.get("integration_status"),
    }
    return layer, probe_result


def _audit_superpowers(project: Path, checks: list[dict]) -> dict[str, Any]:
    for name in C.pinned_capabilities():
        rel = f".agents/skills/{name}/SKILL.md"
        _check(checks, f"superpowers.pinned.{name}", "superpowers", rel, C.exists_file(project, rel))
    for name in C.SUPERPOWERS_SHIMS:
        rel = f".agents/skills/{name}/SKILL.md"
        _check(checks, f"superpowers.shim.{name}", "superpowers", rel, C.exists_file(project, rel))

    layer_checks = [c for c in checks if c["layer"] == "superpowers"]
    present_n = sum(1 for c in layer_checks if c["present"])
    missing = [c["id"] for c in layer_checks if not c["present"]]
    return {
        "verdict": C.layer_verdict(present_n, len(layer_checks)),
        "present": present_n,
        "total": len(layer_checks),
        "missing": missing,
    }


def audit(project: Path) -> dict[str, Any]:
    # @lat: [[consumer-bootstrap#Consumer Audit]]
    project = project.resolve()
    checks: list[dict] = []
    ges = _audit_ges(project, checks)
    spec_kit, probe = _audit_spec_kit(project, checks)
    superpowers = _audit_superpowers(project, checks)

    claims = {
        "ges": "GES_NATIVE" if ges["verdict"] == "PASS" else "UNAVAILABLE",
        "spec_kit_scaffold": "ADAPTER_READY" if spec_kit["verdict"] != "MISSING" else "UNAVAILABLE",
        "spec_kit_provider": str(probe.get("integration_status") or "NATIVE_ONLY"),
        "superpowers_pinned": "UPSTREAM_PINNED"
        if all(
            C.exists_file(project, f".agents/skills/{n}/SKILL.md") for n in C.pinned_capabilities()
        )
        else "GES_NATIVE",
        "superpowers_shims": "GES_NATIVE",
    }

    report = {
        "schema": "smc.ges.consumer-audit.v1",
        "project": str(project),
        "audited_at": C.utc_now(),
        "ok": all(layer["verdict"] == "PASS" for layer in (ges, spec_kit, superpowers)),
        "layers": {
            "ges": ges,
            "spec_kit": spec_kit,
            "superpowers": superpowers,
        },
        "checks": checks,
        "claims": claims,
        "probe": probe,
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Consumer Audit Report",
        "",
        f"- Project: `{report['project']}`",
        f"- Audited at: `{report['audited_at']}`",
        f"- Overall: `{'PASS' if report['ok'] else 'GAPS'}`",
        "",
        "## Layers",
        "",
    ]
    for name, layer in report["layers"].items():
        lines.append(
            f"- **{name}**: `{layer['verdict']}` ({layer['present']}/{layer['total']})"
        )
        if layer.get("missing"):
            for m in layer["missing"]:
                lines.append(f"  - missing: `{m}`")
    lines.extend(["", "## Claims", ""])
    for k, v in sorted(report.get("claims", {}).items()):
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Checks", ""])
    for c in report["checks"]:
        mark = "PASS" if c["present"] else "MISS"
        lines.append(f"- [{mark}] `{c['id']}` → `{c['path']}`")
        if c.get("detail"):
            lines.append(f"  - {c['detail']}")
    lines.append("")
    return "\n".join(lines)


def write_reports(project: Path, report: dict[str, Any]) -> tuple[Path, Path]:
    out_dir = C.bounded(project, C.REPORT_DIR_REL)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "consumer-audit-report.json"
    md_path = out_dir / "consumer-audit-report.md"
    C.dump_json(json_path, report)
    md_path.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    return json_path, md_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("--json", action="store_true", help="print JSON to stdout")
    ap.add_argument("--no-write", action="store_true", help="do not write report files")
    a = ap.parse_args()
    project = a.project.resolve()
    if not (project / ".git").exists():
        print("CONSUMER_AUDIT_FAILED: TARGET_NOT_GIT_REPO", file=sys.stderr)
        return 2
    report = audit(project)
    if not a.no_write:
        jp, mp = write_reports(project, report)
        print(f"AUDIT_REPORT_JSON: {jp}")
        print(f"AUDIT_REPORT_MD: {mp}")
    if a.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for name, layer in report["layers"].items():
            print(f"{name}: {layer['verdict']} ({layer['present']}/{layer['total']})")
        print("OVERALL:", "PASS" if report["ok"] else "GAPS")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
