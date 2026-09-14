#!/usr/bin/env python3
"""Convert a Consumer Audit report into layered gap analysis + machine codes."""
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
from audit_consumer import audit, write_reports  # noqa: E402


def analyze(audit_report: dict[str, Any]) -> dict[str, Any]:
    # @lat: [[consumer-bootstrap#Gap Analysis]]
    layers_out: dict[str, Any] = {}
    codes: list[str] = []
    for name, layer in audit_report.get("layers", {}).items():
        verdict = layer.get("verdict", "MISSING")
        missing = list(layer.get("missing") or [])
        notes: list[str] = []
        if name == "spec_kit":
            notes.append(f"provider_status={layer.get('provider_status')}")
            notes.append(f"integration_status={layer.get('integration_status')}")
            if layer.get("provider_status") == "UNAVAILABLE":
                codes.append("SPEC_KIT_PROVIDER_UNAVAILABLE")
        if name == "superpowers" and verdict != "PASS":
            codes.append("SUPERPOWERS_CAPABILITY_GAP")
        if name == "ges" and verdict != "PASS":
            codes.append("GES_CAPABILITY_GAP")
        if verdict == "MISSING":
            codes.append(f"LAYER_MISSING:{name}")
        elif verdict == "PARTIAL":
            codes.append(f"LAYER_PARTIAL:{name}")
        layers_out[name] = {
            "verdict": verdict,
            "missing": missing,
            "notes": notes,
            "present": layer.get("present"),
            "total": layer.get("total"),
        }

    claims = dict(audit_report.get("claims") or {})
    for key, value in list(claims.items()):
        if value not in C.CLAIM_VOCAB:
            claims[key] = "INSPIRED"
            codes.append(f"CLAIM_NORMALIZED:{key}")

    ok = all(v.get("verdict") == "PASS" for v in layers_out.values())
    if ok:
        codes.append("CONSUMER_GAP_NONE")
    else:
        codes.append("CONSUMER_GAP_PRESENT")

    return {
        "schema": "smc.ges.consumer-gap.v1",
        "project": audit_report.get("project"),
        "analyzed_at": C.utc_now(),
        "ok": ok,
        "layers": layers_out,
        "claims": claims,
        "codes": codes,
        "audit_schema": audit_report.get("schema"),
    }


def render_markdown(gap: dict[str, Any]) -> str:
    lines = [
        "# Consumer Gap Analysis",
        "",
        f"- Project: `{gap['project']}`",
        f"- Analyzed at: `{gap['analyzed_at']}`",
        f"- Overall: `{'PASS' if gap['ok'] else 'GAPS'}`",
        "",
        "## Layers",
        "",
    ]
    for name, layer in gap["layers"].items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"- Verdict: `{layer['verdict']}`")
        if layer.get("missing"):
            lines.append("- Missing:")
            for m in layer["missing"]:
                lines.append(f"  - `{m}`")
        else:
            lines.append("- Missing: none")
        for n in layer.get("notes") or []:
            lines.append(f"- Note: {n}")
        lines.append("")
    lines.extend(["## Claims", ""])
    for k, v in sorted(gap.get("claims", {}).items()):
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(["", "## Codes", ""])
    for code in gap.get("codes", []):
        lines.append(f"- `{code}`")
    lines.append("")
    return "\n".join(lines)


def write_gap(project: Path, gap: dict[str, Any]) -> Path:
    out_dir = C.bounded(project, C.REPORT_DIR_REL)
    out_dir.mkdir(parents=True, exist_ok=True)
    md = out_dir / "consumer-gap-analysis.md"
    json_path = out_dir / "consumer-gap-analysis.json"
    md.write_text(render_markdown(gap), encoding="utf-8", newline="\n")
    C.dump_json(json_path, gap)
    return md


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project", nargs="?", default=".", type=Path)
    ap.add_argument("--audit", type=Path, help="existing audit JSON (optional)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    project = a.project.resolve()
    if a.audit:
        audit_report = C.read_json(a.audit.resolve())
    else:
        if not (project / ".git").exists():
            print("CONSUMER_GAP_FAILED: TARGET_NOT_GIT_REPO", file=sys.stderr)
            return 2
        audit_report = audit(project)
        write_reports(project, audit_report)
    gap = analyze(audit_report)
    path = write_gap(project, gap)
    print(f"GAP_ANALYSIS_MD: {path}")
    if a.json:
        print(json.dumps(gap, indent=2, ensure_ascii=False))
    else:
        for name, layer in gap["layers"].items():
            print(f"{name}: {layer['verdict']}")
        print("OVERALL:", "PASS" if gap["ok"] else "GAPS")
    return 0 if gap["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
