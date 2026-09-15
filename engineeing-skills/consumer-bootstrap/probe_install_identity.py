#!/usr/bin/env python3
"""Filesystem probe for GES install identity + frontend adoption readiness.

Agents must read lock/receipt from the filesystem under `.smc/`, not from
`git ls-files` alone — those proofs are often local/untracked. Bundle remains
the package version (`5.0.0`); feature PRD slices (5.0.6/5.0.7) are inferred
from installed runtime paths and are NOT the lock `bundle` field.
"""
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

import common as C  # noqa: E402

SCHEMA = "smc.ges.install-identity.v1"
LOCK_REL = ".smc/ges-install-lock.json"
RECEIPT_REL = ".smc/ges-install-receipt.json"
REPORT_REL = ".smc/consumer-bootstrap/install-identity.json"
CALIBRATION_REL = f"{C.FRONTEND_ROOT}/calibration-status.json"
ADOPTION_REL = f"{C.FRONTEND_ROOT}/adoption-mode.json"

SCAN_HINTS = [
    "Read .smc/ges-install-lock.json and .smc/ges-install-receipt.json from the filesystem; do not require them to be git-tracked.",
    "lock.bundle is the package version (currently 5.0.0). Do not expect bundle==5.0.7 for the v5.0.7 feature slice.",
    "release_eligible=false or source_tree_dirty=true means install is not a clean release attestation.",
    "Frontend baselines under .agents/ges/frontend/ are discovery until calibration-status is ACCEPTED; OBSERVE/GUIDED generated JSON is not Production SOT.",
]


def _read_optional(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = C.read_json(path)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _adoption_mode(project: Path) -> str:
    if C.exists_file(project, f"{C.FRONTEND_ROOT}/ENFORCED"):
        return "ENFORCED"
    data = _read_optional(project / ADOPTION_REL)
    if not data:
        return "ABSENT"
    mode = str(data.get("mode") or "OBSERVE").upper()
    return mode if mode in {"OBSERVE", "GUIDED", "ENFORCED"} else "OBSERVE"


def _calibration_status(project: Path) -> dict[str, Any]:
    data = _read_optional(project / CALIBRATION_REL)
    if data:
        return {
            "status": str(data.get("status") or "PENDING").upper(),
            "path": CALIBRATION_REL,
            "updated_at": data.get("updated_at"),
        }
    # Infer PENDING when any app baseline exists but no explicit calibration file.
    registry = project / C.FRONTEND_ROOT / "apps-registry.json"
    if registry.is_file():
        return {"status": "PENDING", "path": None, "updated_at": None}
    return {"status": "ABSENT", "path": None, "updated_at": None}


def _feature_slices(project: Path, lock: dict[str, Any] | None) -> list[str]:
    slices: list[str] = []
    runtime = project / ".agents/ges/frontend-runtime"
    if (project / ".agents/ges/frontend-adapters").is_dir() or runtime.is_dir():
        slices.append("5.0.6")
    if (project / C.FRONTEND_ROOT / "apps-registry.json").is_file():
        try:
            reg = C.read_json(project / C.FRONTEND_ROOT / "apps-registry.json")
            if str(reg.get("schema") or "").endswith(".v2") or reg.get("repository"):
                slices.append("5.0.7")
        except Exception:
            if runtime.is_dir():
                slices.append("5.0.7")
    # v5.0.8: budget controller + capsule cache present under frontend-runtime
    if (runtime / "budget_controller.py").is_file() and (runtime / "context_cache.py").is_file():
        if (runtime / "policies" / "context-budget.v1.json").is_file() or (
            runtime / "policies"
        ).is_dir():
            slices.append("5.0.8")
    # v5.0.9: runtime cost closure markers
    if (
        (runtime / "model_dispatch.py").is_file()
        and (runtime / "context_envelope.py").is_file()
        and (runtime / "stage_cost_closure.py").is_file()
    ):
        try:
            sys_path_added = False
            import sys

            if str(runtime) not in sys.path:
                sys.path.insert(0, str(runtime))
                sys_path_added = True
            import model_dispatch as md  # noqa: WPS433

            ok = all(md.self_check_modules().values())
            if ok:
                slices.append("5.0.9")
        except Exception:
            if (runtime / "harness_contract.py").is_file():
                slices.append("5.0.9")
    # Deduplicate preserve order
    out: list[str] = []
    for s in slices:
        if s not in out:
            out.append(s)
    # Package CHANGES presence (when probing from package checkout) is advisory only
    if (PACKAGE / "CHANGES-v5.0.7-frontend-context-scoped-install.md").is_file() and "5.0.7" not in out:
        if lock and runtime.is_dir():
            out.append("5.0.7")
    if (PACKAGE / "CHANGES-v5.0.8-adaptive-governance-context-budget.md").is_file() and "5.0.8" not in out:
        if lock and (runtime / "budget_controller.py").is_file():
            out.append("5.0.8")
    if (PACKAGE / "CHANGES-v5.0.9-runtime-cost-closure.md").is_file() and "5.0.9" not in out:
        if lock and (runtime / "model_dispatch.py").is_file():
            out.append("5.0.9")
    return out


def probe(project: str | Path) -> dict[str, Any]:
    """Build install-identity report from filesystem paths (C: scan convention)."""
    root = Path(project).resolve()
    lock = _read_optional(root / LOCK_REL)
    receipt_ptr = _read_optional(root / RECEIPT_REL)
    full_receipt = None
    if receipt_ptr and receipt_ptr.get("receipt_path"):
        full_receipt = _read_optional(root / str(receipt_ptr["receipt_path"]))
    if full_receipt is None:
        receipts_dir = root / ".smc" / "ges-install-receipts"
        if receipts_dir.is_dir():
            for path in sorted(receipts_dir.glob("*.json")):
                full_receipt = _read_optional(path)
                if full_receipt:
                    break

    ri = (lock or {}).get("release_identity") or (full_receipt or {}).get("release_identity") or {}
    bundle = (lock or {}).get("bundle") or (receipt_ptr or {}).get("bundle") or (full_receipt or {}).get("bundle")
    adoption = _adoption_mode(root)
    calibration = _calibration_status(root)
    slices = _feature_slices(root, lock)
    production_sot = adoption == "ENFORCED" and calibration.get("status") == "ACCEPTED"

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "project": str(root),
        "probed_at": C.utc_now(),
        "source": "filesystem",
        "paths": {
            "lock": LOCK_REL,
            "receipt_pointer": RECEIPT_REL,
            "receipt_full": (receipt_ptr or {}).get("receipt_path"),
            "adoption": ADOPTION_REL,
            "calibration": CALIBRATION_REL,
        },
        "present": {
            "lock": lock is not None,
            "receipt_pointer": receipt_ptr is not None,
            "receipt_full": full_receipt is not None,
            "frontend_registry": (root / C.FRONTEND_ROOT / "apps-registry.json").is_file(),
            "frontend_runtime": (root / ".agents/ges/frontend-runtime").is_dir(),
            "frontend_adapters": (root / ".agents/ges/frontend-adapters").is_dir(),
        },
        "bundle": bundle,
        "feature_slices_inferred": slices,
        "release_identity": {
            "source_commit": ri.get("source_commit"),
            "source_tree_dirty": ri.get("source_tree_dirty"),
            "release_eligible": ri.get("release_eligible"),
            "package_manifest_sha256": ri.get("package_manifest_sha256"),
            "package_file_count": ri.get("package_file_count"),
            "note": ri.get("note"),
        },
        "transaction_status": (receipt_ptr or full_receipt or {}).get("transaction_status")
        or (full_receipt or {}).get("validation"),
        "frontend": {
            "adoption_mode": adoption,
            "calibration_status": calibration.get("status"),
            "production_sot": production_sot,
            "note": (
                "Generated baselines are discovery clues until calibration_status=ACCEPTED; "
                "do not treat OBSERVE/GUIDED output as Production SOT."
            ),
        },
        "verdict": {
            "install_proof_found": bool(lock and (receipt_ptr or full_receipt)),
            "release_attestation_ok": bool(ri.get("release_eligible") is True),
            "bundle_is_feature_slice": False,
            "ok_to_claim_bundle": bundle,
            "not_ok_to_claim_as_bundle": [s for s in slices if s != bundle],
        },
        "scan_hints": SCAN_HINTS,
    }
    return report


def write_report(project: Path, report: dict[str, Any]) -> Path:
    path = C.bounded(project, REPORT_REL)
    path.parent.mkdir(parents=True, exist_ok=True)
    C.dump_json(path, report)
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project", type=Path, help="consumer repo root")
    ap.add_argument("--json", action="store_true", help="print report JSON to stdout")
    args = ap.parse_args(argv)
    project = args.project.resolve()
    if not project.is_dir():
        print(f"INSTALL_IDENTITY_FAILED: not a directory: {project}", file=sys.stderr)
        return 2
    report = probe(project)
    out = write_report(project, report)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        v = report["verdict"]
        fe = report["frontend"]
        ri = report["release_identity"]
        print(f"INSTALL_IDENTITY_JSON: {out}")
        print(
            f"proof={v['install_proof_found']} bundle={report.get('bundle')} "
            f"slices={report.get('feature_slices_inferred')} "
            f"release_eligible={ri.get('release_eligible')} "
            f"source_commit={ri.get('source_commit')}"
        )
        print(
            f"frontend adoption={fe.get('adoption_mode')} "
            f"calibration={fe.get('calibration_status')} "
            f"production_sot={fe.get('production_sot')}"
        )
        if not v["install_proof_found"]:
            print(
                "HINT: lock/receipt missing on filesystem at .smc/ — "
                "re-run install; do not conclude from git-only scans.",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
