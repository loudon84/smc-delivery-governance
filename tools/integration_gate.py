from __future__ import annotations
import sys
from governance_lib import ROOT, load_feature, load_work_packages, load_yaml, contract_state, state_at_least, CONTRACT_ORDER, WP_ORDER

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: integration_gate.py <feature-dir-or-id>")
    fdir, feature = load_feature(sys.argv[1])
    wps = load_work_packages(fdir)
    scenario = load_yaml(ROOT / "integration" / "scenarios" / f"{feature['feature_id']}.yaml")
    blockers = []
    for req in scenario.get("requires", {}).get("contracts", []):
        current = contract_state(req["contract_id"])
        if not state_at_least(current, req["minimum_state"], CONTRACT_ORDER):
            blockers.append(("contract", req["contract_id"], req["minimum_state"], current))
    for req in scenario.get("requires", {}).get("work_packages", []):
        current = (wps.get(req["work_package_id"]) or {}).get("status")
        if not state_at_least(current, req["minimum_state"], WP_ORDER):
            blockers.append(("work_package", req["work_package_id"], req["minimum_state"], current))
    print(f"Integration: {scenario['scenario_id']}")
    if blockers:
        provider_block = any(t == "work_package" and (wps.get(i) or {}).get("role") == "provider" for t,i,_,_ in blockers)
        consumer_block = any(t == "work_package" and (wps.get(i) or {}).get("role") == "consumer" for t,i,_,_ in blockers)
        state = "WAITING_PROVIDER" if provider_block else "WAITING_CONSUMER" if consumer_block else "BLOCKED"
        print(f"Gate: {state}")
        for t,i,r,c in blockers:
            print(f"- {t}:{i} required={r} current={c}")
        raise SystemExit(2)
    print("Gate: READY")
    print("All contract/work-package maturity requirements are satisfied.")

if __name__ == "__main__":
    main()
