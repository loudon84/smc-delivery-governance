from __future__ import annotations

import argparse
from pathlib import Path

from audit_events import append_transition_event
from governance_lib import (
    EXIT_EXPECTED_NON_READY,
    EXIT_OK,
    EXIT_SYSTEM_ERROR,
    ROOT,
    contract_catalog,
    dump_yaml,
    load_feature,
    load_work_packages,
    load_yaml,
    resolve_contract,
    state_at_least,
    CONTRACT_ORDER,
    WP_ORDER,
)
from state_machine import allowed, contract_gate, feature_gate, roadmap_item_gate, work_package_gate

WP_SEQUENCE = ["BACKLOG", "READY", "IN_PRD", "PLANNED", "IMPLEMENTING", "REVIEW", "VERIFIED", "DONE"]
FEATURE_SEQUENCE = ["PROPOSED", "ARCHITECTURE", "PLANNED", "IMPLEMENTING", "INTEGRATING", "VERIFYING", "DONE"]
ROADMAP_SEQUENCE = ["PLANNED", "ACTIVE", "DONE", "BLOCKED"]


def apply_transition(entity_type, entity_id, current, nxt, actor, source, reason, evidence, apply):
    append_transition_event(
        entity_type=entity_type,
        entity_id=entity_id,
        from_state=current,
        to_state=nxt,
        actor=actor,
        source=source,
        reason=reason,
        evidence=evidence,
        apply=apply,
    )


def promote_wp(fdir, path, wp, observed_target, apply, actor="smc-governance-bot", source="reconciler"):
    if wp.get("status") in {"BLOCKED", "SUPERSEDED"} or observed_target not in WP_SEQUENCE:
        return wp["status"], False
    current = wp["status"]
    target_index = WP_SEQUENCE.index(observed_target)
    blocked = False
    while current in WP_SEQUENCE and WP_SEQUENCE.index(current) < target_index:
        nxt = WP_SEQUENCE[WP_SEQUENCE.index(current) + 1]
        if not allowed("work_package", current, nxt):
            break
        errors = work_package_gate(fdir, {**wp, "status": current}, nxt)
        if errors:
            print(f"{wp['work_package_id']}: stop {current}->{nxt}: {errors[0]}")
            blocked = True
            break
        print(f"{wp['work_package_id']}: {current}->{nxt}")
        apply_transition(
            "work_package",
            wp["work_package_id"],
            current,
            nxt,
            actor,
            source,
            f"observed receipt status {observed_target}",
            [f"delivery-ledger/{wp['repository_id']}.yaml"],
            apply,
        )
        current = nxt
        if apply:
            wp["status"] = current
            dump_yaml(path, wp)
    return current, blocked


def derive_roadmap_status(item, feature_dir) -> str | None:
    wps = load_work_packages(feature_dir)
    exits_met = True
    for exit_req in item.get("exit", []):
        if exit_req.startswith("contract:"):
            _, rest = exit_req.split(":", 1)
            contract_id, minimum = rest.split(">=", 1)
            if not state_at_least(resolve_contract(contract_id), minimum, CONTRACT_ORDER):
                exits_met = False
        elif exit_req.startswith("work_package:"):
            _, rest = exit_req.split(":", 1)
            wp_id, minimum = rest.split(">=", 1)
            if not state_at_least((wps.get(wp_id) or {}).get("status"), minimum, WP_ORDER):
                exits_met = False
        elif exit_req.startswith("integration:"):
            _, rest = exit_req.split(":", 1)
            scenario_id, required = rest.split("=", 1)
            run_path = ROOT / "integration" / "runs" / f"{scenario_id}.yaml"
            current = (
                "PASS"
                if run_path.exists() and load_yaml(run_path).get("result", {}).get("status") == "PASS"
                else "OPEN"
            )
            if current != required:
                exits_met = False
    if exits_met:
        return "DONE"
    if item.get("blocked_by"):
        return "BLOCKED"
    if item.get("work_packages"):
        active = any((wps.get(wid) or {}).get("status") not in {"DONE", "VERIFIED"} for wid in item["work_packages"])
        return "ACTIVE" if active else item.get("status", "ACTIVE")
    return "ACTIVE"


def reconcile_roadmap(fdir, apply, actor="smc-governance-bot", source="reconciler") -> bool:
    roadmap_path = fdir / "roadmap.yaml"
    if not roadmap_path.exists():
        return False
    roadmap = load_yaml(roadmap_path)
    blocked = False
    for item in roadmap.get("items", []):
        current = item.get("status", "PLANNED")
        desired = derive_roadmap_status(item, fdir)
        if not desired or desired == current:
            continue
        if desired == "DONE":
            errors = roadmap_item_gate(fdir, item, "DONE")
            if errors:
                print(f"{item['id']}: stop -> DONE: {errors[0]}")
                blocked = True
                continue
        if current in ROADMAP_SEQUENCE and desired in ROADMAP_SEQUENCE:
            print(f"{item['id']}: {current}->{desired}")
            apply_transition(
                "roadmap_item",
                item["id"],
                current,
                desired,
                actor,
                source,
                "derived from work package / contract / integration exits",
                [],
                apply,
            )
            item["status"] = desired
    if apply:
        dump_yaml(roadmap_path, roadmap)
    return blocked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("feature")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--actor", default="smc-governance-bot")
    args = ap.parse_args()

    try:
        fdir, feature = load_feature(args.feature)
        wps = load_work_packages(fdir)
        blocked = False

        for wid, wp0 in wps.items():
            path = fdir / "work-packages" / Path(wp0["_path"]).name
            wp = {k: v for k, v in wp0.items() if k != "_path"}
            ledger = fdir / "delivery-ledger" / f"{wp['repository_id']}.yaml"
            if not ledger.exists():
                continue
            obs = load_yaml(ledger)
            _, wp_blocked = promote_wp(fdir, path, wp, obs.get("status"), args.apply, args.actor)
            blocked = blocked or wp_blocked

        blocked = reconcile_roadmap(fdir, args.apply, args.actor) or blocked

        fdir, feature = load_feature(args.feature)
        wps = load_work_packages(fdir)
        current = feature["status"]
        desired = None
        if all(wp.get("status") in {"VERIFIED", "DONE"} for wp in wps.values()):
            desired = "INTEGRATING"
        run_path = ROOT / "integration" / "runs" / f"{feature.get('integration', {}).get('scenario_id', '')}.yaml"
        integration_pass = run_path.exists() and load_yaml(run_path).get("result", {}).get("status") == "PASS"
        if integration_pass and all(wp.get("status") in {"VERIFIED", "DONE"} for wp in wps.values()):
            desired = "DONE"

        if desired and current in FEATURE_SEQUENCE:
            while FEATURE_SEQUENCE.index(current) < FEATURE_SEQUENCE.index(desired):
                nxt = FEATURE_SEQUENCE[FEATURE_SEQUENCE.index(current) + 1]
                if not allowed("feature", current, nxt):
                    break
                errors = feature_gate(fdir, {**feature, "status": current}, nxt)
                if errors:
                    print(f"Feature stop {current}->{nxt}: {errors[0]}")
                    blocked = True
                    break
                print(f"Feature {current}->{nxt}")
                apply_transition(
                    "feature",
                    feature["feature_id"],
                    current,
                    nxt,
                    args.actor,
                    "reconciler",
                    f"work packages and roadmap satisfied for {desired}",
                    [],
                    args.apply,
                )
                current = nxt
                if args.apply:
                    feature["status"] = current
                    dump_yaml(fdir / "feature.yaml", feature)

        if blocked:
            raise SystemExit(EXIT_EXPECTED_NON_READY)
        raise SystemExit(EXIT_OK)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"RECONCILER SYSTEM_ERROR: {exc}")
        raise SystemExit(EXIT_SYSTEM_ERROR) from exc


if __name__ == "__main__":
    main()
