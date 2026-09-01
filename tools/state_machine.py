from __future__ import annotations

from pathlib import Path

from governance_lib import (
    ROOT,
    contract_release,
    load_feature,
    load_work_packages,
    load_yaml,
    resolve_contract,
)


def transitions(kind: str) -> dict[str, list[str]]:
    doc = load_yaml(ROOT / "contracts/lifecycle/states.yaml")
    return doc[kind]["transitions"]


def allowed(kind: str, current: str, target: str) -> bool:
    return target in transitions(kind).get(current, [])


def _provider_contract_evidence(observed: dict, wp: dict) -> bool:
    evidence = observed.get("evidence") or wp.get("evidence") or {}
    release = evidence.get("release") or {}
    commits = (observed.get("delivery") or {}).get("commits") or []
    if not (release.get("tag") and release.get("commit")):
        return False
    for output in wp.get("contract_outputs", []):
        rel = contract_release(output["contract_id"], output.get("version"))
        if not rel or rel.get("state") not in {"RELEASED", "CONSUMED", "CONFORMANCE_PASS"}:
            return False
    return bool(commits)


def work_package_gate(feature_dir: Path, wp: dict, target: str) -> list[str]:
    errors = []
    ledger = feature_dir / "delivery-ledger" / f"{wp['repository_id']}.yaml"
    observed = load_yaml(ledger) if ledger.exists() else {}
    is_provider = wp.get("role") == "provider" and bool(wp.get("contract_outputs"))

    if target in {"PLANNED", "IMPLEMENTING", "REVIEW", "VERIFIED", "DONE"}:
        if wp.get("sync_state") not in {"SYNCED"}:
            errors.append(f"sync_state must be SYNCED, current={wp.get('sync_state')}")

    delivery = observed.get("delivery") or {}
    if target in {"PLANNED", "IMPLEMENTING", "REVIEW", "VERIFIED", "DONE"}:
        if is_provider:
            if target in {"VERIFIED", "DONE"} and not _provider_contract_evidence(observed, wp):
                errors.append("provider contract release evidence required")
        else:
            if not delivery.get("stage_prds"):
                errors.append("Stage PRD reference required")
            if not delivery.get("plans"):
                errors.append("Plan reference required")

    if target in {"REVIEW", "VERIFIED", "DONE"}:
        if not delivery.get("commits"):
            errors.append("implementation commit required")

    if target in {"VERIFIED", "DONE"} and not is_provider:
        if (observed.get("acceptance") or {}).get("status") != "PASS":
            errors.append("Acceptance PASS required")

    return errors


def feature_gate(feature_dir: Path, feature: dict, target: str) -> list[str]:
    errors = []
    wps = load_work_packages(feature_dir)
    roadmap = load_yaml(feature_dir / "roadmap.yaml") if (feature_dir / "roadmap.yaml").exists() else {"items": []}

    if target in {"INTEGRATING", "VERIFYING", "DONE"}:
        not_ready = [wid for wid, wp in wps.items() if wp.get("status") not in {"VERIFIED", "DONE"}]
        if not_ready:
            errors.append(f"work packages not VERIFIED/DONE: {not_ready}")

    if target in {"INTEGRATING", "VERIFYING", "DONE"}:
        for item in roadmap.get("items", []):
            if item.get("id") == "GRM-05":
                continue
            if item.get("status") not in {"DONE", "CANCELLED"}:
                errors.append(f"roadmap item not DONE: {item['id']}")

    if target == "DONE":
        scenario_id = (feature.get("integration") or {}).get("scenario_id")
        if scenario_id:
            run_path = ROOT / "integration" / "runs" / f"{scenario_id}.yaml"
            if run_path.exists():
                run = load_yaml(run_path)
                if run.get("result", {}).get("status") != "PASS":
                    errors.append(f"integration run {scenario_id} not PASS")
            else:
                scenario = load_yaml(ROOT / "integration" / "scenarios" / f"{feature['feature_id']}.yaml")
                if scenario.get("state") != "PASS":
                    errors.append(f"integration {scenario_id} not PASS")
    return errors


def contract_gate(contract: dict, target: str, version: str | None = None) -> list[str]:
    errors = []
    rel = contract_release(contract["contract_id"], version) if version else contract.get("current_release") or {}
    if not rel and contract.get("releases"):
        rel = contract["releases"][0]
    if target in {"RELEASED", "CONSUMED", "CONFORMANCE_PASS"}:
        if not rel.get("version"):
            errors.append("release version required")
        if not rel.get("tag"):
            errors.append("release tag required")
        if not rel.get("peeled_commit"):
            errors.append("peeled commit required")
    return errors


def roadmap_item_gate(feature_dir: Path, item: dict, target: str) -> list[str]:
    errors = []
    wps = load_work_packages(feature_dir)
    for exit_req in item.get("exit", []):
        if exit_req.startswith("contract:"):
            _, rest = exit_req.split(":", 1)
            contract_id, minimum = rest.split(">=", 1)
            current = resolve_contract(contract_id)
            from governance_lib import CONTRACT_ORDER, state_at_least

            if not state_at_least(current, minimum, CONTRACT_ORDER):
                errors.append(f"exit not met: {exit_req}")
        elif exit_req.startswith("work_package:"):
            _, rest = exit_req.split(":", 1)
            wp_id, minimum = rest.split(">=", 1)
            current = (wps.get(wp_id) or {}).get("status")
            from governance_lib import WP_ORDER, state_at_least

            if not state_at_least(current, minimum, WP_ORDER):
                errors.append(f"exit not met: {exit_req}")
        elif exit_req.startswith("integration:"):
            _, rest = exit_req.split(":", 1)
            scenario_id, required = rest.split("=", 1)
            run_path = ROOT / "integration" / "runs" / f"{scenario_id}.yaml"
            current = "PASS" if run_path.exists() and load_yaml(run_path).get("result", {}).get("status") == "PASS" else "OPEN"
            if current != required:
                errors.append(f"exit not met: {exit_req}")
    if target == "DONE" and errors:
        return errors
    return [] if target != "DONE" else errors
