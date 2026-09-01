from __future__ import annotations
import sys
from governance_lib import load_feature, load_work_packages, load_yaml, contract_state, state_at_least, CONTRACT_ORDER, WP_ORDER

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: dependency_status.py <feature-dir-or-id>")
    fdir, feature = load_feature(sys.argv[1])
    wps = load_work_packages(fdir)
    deps_doc = load_yaml(fdir / "dependencies.yaml")
    blocked = False
    print(f"Feature: {feature['feature_id']} — {feature['title']}")
    for dep in deps_doc.get("dependencies", []):
        target = dep["to"]
        if target["type"] == "contract":
            current = contract_state(target["id"])
            ok = state_at_least(current, dep["required_state"], CONTRACT_ORDER)
        elif target["type"] == "work_package":
            current = (wps.get(target["id"]) or {}).get("status")
            ok = state_at_least(current, dep["required_state"], WP_ORDER)
        else:
            current, ok = None, False
        print(f"{'PASS' if ok else 'BLOCK':5} {dep['id']:8} {dep['from']} -> {target['type']}:{target['id']} required={dep['required_state']} current={current}")
        blocked |= not ok
    if blocked:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
