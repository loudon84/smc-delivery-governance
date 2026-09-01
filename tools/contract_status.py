from __future__ import annotations
import sys
from governance_lib import contract_catalog, CONTRACT_ORDER

def main():
    contracts = contract_catalog()
    ids = sys.argv[1:] or sorted(contracts)
    failed = False
    for cid in ids:
        c = contracts.get(cid)
        if not c:
            print(f"UNKNOWN {cid}")
            failed = True
            continue
        release = c.get("current_release") or {}
        print(cid)
        print(f"  scope: {c.get('scope')}")
        print(f"  provider: {c.get('provider_repository')}")
        print(f"  version: {release.get('version')}")
        print(f"  state: {release.get('state')}")
        print(f"  tag: {release.get('tag')}")
        print(f"  peeled_commit: {release.get('peeled_commit')}")
        print(f"  consumers: {', '.join(c.get('primary_consumers', []))}")
        if release.get("state") not in CONTRACT_ORDER:
            failed = True
    if failed:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
