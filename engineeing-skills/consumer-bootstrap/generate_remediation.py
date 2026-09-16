#!/usr/bin/env python3
"""Generate an ordered Consumer Remediation Plan from gap / audit data."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import common as C  # noqa: E402
from analyze_gap import analyze, write_gap  # noqa: E402
from audit_consumer import audit, write_reports  # noqa: E402


def _action(aid: str, kind: str, target: str, reason: str, **extra: Any) -> dict[str, Any]:
    row = {"id": aid, "kind": kind, "target": target, "reason": reason}
    row.update(extra)
    return row


def generate(project: Path, gap: dict[str, Any], audit_report: dict[str, Any] | None = None) -> dict[str, Any]:
    # @lat: [[consumer-bootstrap#Automated Remediation]]
    project = project.resolve()
    actions: list[dict[str, Any]] = []
    n = 0

    def next_id(prefix: str) -> str:
        nonlocal n
        n += 1
        return f"{prefix}-{n:03d}"

    # Spec Kit scaffold (never .specify/spec.md)
    for rel in C.SPEC_KIT_SCAFFOLD:
        if rel.endswith("/.gitkeep"):
            drel = rel.rsplit("/", 1)[0]
            if not C.exists_dir(project, drel):
                actions.append(
                    _action(
                        next_id("SK"),
                        "WRITE_TEMPLATE",
                        rel,
                        "Spec Kit scaffold directory marker missing",
                        template=f"spec-kit/{rel[len('.specify/'):]}",
                        claim="ADAPTER_READY",
                    )
                )
            continue
        if not C.exists_file(project, rel):
            tmpl = "spec-kit/" + rel[len(".specify/") :]
            actions.append(
                _action(
                    next_id("SK"),
                    "WRITE_TEMPLATE",
                    rel,
                    "Spec Kit scaffold file missing",
                    template=tmpl,
                    claim="ADAPTER_READY",
                )
            )

    # Superpowers shims + missing pinned skills (GES templates only)
    for name in C.SUPERPOWERS_SHIMS:
        rel = f".agents/skills/{name}/SKILL.md"
        if not C.exists_file(project, rel):
            actions.append(
                _action(
                    next_id("SP"),
                    "WRITE_TEMPLATE",
                    rel,
                    f"Superpowers shim skill missing: {name}",
                    template=f"superpowers/{name}/SKILL.md",
                    claim="GES_NATIVE",
                )
            )

    for name in ("systematic-debugging", "test-driven-development"):
        rel = f".agents/skills/{name}/SKILL.md"
        if not C.exists_file(project, rel):
            tmpl = C.TEMPLATES / "superpowers" / name / "SKILL.md"
            if tmpl.is_file():
                actions.append(
                    _action(
                        next_id("SP"),
                        "WRITE_TEMPLATE",
                        rel,
                        f"Method skill missing; seeding GES_NATIVE shim: {name}",
                        template=f"superpowers/{name}/SKILL.md",
                        claim="GES_NATIVE",
                    )
                )

    # Bridge contracts under .agents/ges/ (never profile.json)
    for rel in C.BRIDGE_CONTRACTS:
        if not C.exists_file(project, rel):
            name = Path(rel).name
            actions.append(
                _action(
                    next_id("BR"),
                    "WRITE_TEMPLATE",
                    rel,
                    f"GES bridge contract missing: {name}",
                    template=f"ges/{name}",
                    claim="GES_NATIVE",
                )
            )

    # Context Registry templates (missing-only; never overwrite Consumer Registry)
    context_templates = (
        (".agents/ges/context/architecture.yaml", "ges/context/architecture.yaml"),
        (".agents/ges/context/project.yaml", "ges/context/project.yaml"),
        (".agents/ges/context/modules/example.yaml", "ges/context/modules/example.yaml"),
        (".agents/ges/context/components/example.yaml", "ges/context/components/example.yaml"),
        (".agents/ges/context/applications/example.yaml", "ges/context/applications/example.yaml"),
    )
    for rel, tmpl in context_templates:
        if not C.exists_file(project, rel):
            actions.append(
                _action(
                    next_id("CTX"),
                    "WRITE_TEMPLATE",
                    rel,
                    "Context Registry template missing",
                    template=tmpl,
                    claim="GES_NATIVE",
                )
            )

    # GES gaps that bootstrap cannot invent — advise install
    # (profile.json + domain-packs/registry.json are installer-owned; bootstrap must not write them)
    ges_layer = (gap.get("layers") or {}).get("ges") or {}
    ges_missing = list(ges_layer.get("missing") or [])
    if ges_layer.get("verdict") != "PASS":
        reason = "GES runtime incomplete; run package installer (optionally with --seed-consumer-skills)"
        if any(x in ges_missing for x in ("ges.profile", "ges.domain_registry")):
            reason = (
                "Missing installer-owned GES metadata (profile.json and/or domain-packs/registry.json); "
                "re-run installer — bootstrap cannot write these paths"
            )
        actions.append(
            _action(
                next_id("GES"),
                "RUN_COMMAND",
                ".",
                reason,
                command="python install.py <project> --apply",
                claim="GES_NATIVE",
            )
        )

    # Optional: advise specify CLI install (never auto-run specify init)
    probe = (audit_report or {}).get("probe") or {}
    if probe.get("provider_status") == "UNAVAILABLE":
        actions.append(
            _action(
                next_id("SK"),
                "MANUAL",
                "specify",
                "Spec Kit CLI unavailable; install specify on PATH for EXTERNAL_VERIFIED (optional)",
                claim="NATIVE_ONLY",
            )
        )

    # Frontend Context System (v5.0.6)
    registry_rel = f"{C.FRONTEND_ROOT}/apps-registry.json"
    if not C.exists_file(project, registry_rel):
        actions.append(
            _action(
                next_id("FE"),
                "WRITE_TEMPLATE",
                registry_rel,
                "Frontend apps-registry.json missing",
                template="frontend/apps-registry.json",
                claim="GES_NATIVE",
            )
        )
        shared_rel = f"{C.FRONTEND_ROOT}/shared/shared-ui-registry.json"
        if not C.exists_file(project, shared_rel):
            actions.append(
                _action(
                    next_id("FE"),
                    "WRITE_TEMPLATE",
                    shared_rel,
                    "Shared UI registry missing",
                    template="frontend/shared-ui-registry.json",
                    claim="GES_NATIVE",
                )
            )
        # Seed per-app template stubs under apps/_template/ for guided adoption.
        for name in C.FRONTEND_APP_LEVEL_TEMPLATES:
            target = f"{C.FRONTEND_ROOT}/apps/_template/{name}"
            if not C.exists_file(project, target):
                actions.append(
                    _action(
                        next_id("FE"),
                        "WRITE_TEMPLATE",
                        target,
                        f"Frontend template stub missing: {name}",
                        template=f"frontend/{name}",
                        claim="GES_NATIVE",
                    )
                )
        actions.append(
            _action(
                next_id("FE"),
                "RUN_COMMAND",
                ".",
                "Run frontend audit --apply to discover apps and write baselines",
                command="python consumer-bootstrap/frontend_audit.py <project> --apply",
                claim="GES_NATIVE",
            )
        )

    return {
        "schema": "smc.ges.consumer-remediation-plan.v1",
        "project": str(project),
        "created_at": C.utc_now(),
        "ok": len([a for a in actions if a["kind"] == "WRITE_TEMPLATE"]) == 0
        and ges_layer.get("verdict") == "PASS",
        "actions": actions,
        "forbidden": sorted(C.FORBIDDEN_WRITE_RELS) + [".specify/spec.md"],
    }


def write_plan(project: Path, plan: dict[str, Any]) -> Path:
    out_dir = C.bounded(project, C.REPORT_DIR_REL)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "consumer-remediation-plan.json"
    C.dump_json(path, plan)
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("--gap", type=Path)
    ap.add_argument("--audit", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    project = a.project.resolve()
    audit_report = C.read_json(a.audit.resolve()) if a.audit else None
    if a.gap:
        gap = C.read_json(a.gap.resolve())
    else:
        if audit_report is None:
            if not (project / ".git").exists():
                print("REMEDIATION_FAILED: TARGET_NOT_GIT_REPO", file=sys.stderr)
                return 2
            audit_report = audit(project)
            write_reports(project, audit_report)
        gap = analyze(audit_report)
        write_gap(project, gap)
    plan = generate(project, gap, audit_report)
    path = write_plan(project, plan)
    print(f"REMEDIATION_PLAN: {path}")
    print(f"ACTIONS: {len(plan['actions'])}")
    if a.json:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    else:
        for act in plan["actions"]:
            print(f"- {act['id']} {act['kind']} {act['target']}")
    return 0 if plan["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
