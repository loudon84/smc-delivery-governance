from __future__ import annotations

import argparse
from pathlib import Path

from audit_events import append_transition_event
from governance_lib import ROOT, contract_catalog, dump_yaml, find_work_package, load_feature, load_yaml
from state_machine import allowed, contract_gate, feature_gate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entity", choices=["feature", "work_package", "contract", "integration", "roadmap_item"], required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--to", required=True)
    ap.add_argument("--version", help="Contract release version when entity=contract")
    ap.add_argument("--actor", default="human")
    ap.add_argument("--reason", default="manual transition")
    ap.add_argument("--evidence", action="append", default=[])
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    errors = []

    if args.entity == "feature":
        fdir, doc = load_feature(args.id)
        current = doc["status"]
        kind = "feature"
        errors += feature_gate(fdir, doc, args.to)
        path = fdir / "feature.yaml"
    elif args.entity == "work_package":
        path, doc = find_work_package(args.id)
        if not doc:
            raise SystemExit("work package not found")
        fdir = path.parents[1]
        current = doc["status"]
        kind = "work_package"
        from state_machine import work_package_gate

        errors += work_package_gate(fdir, doc, args.to)
    elif args.entity == "contract":
        catalog = contract_catalog()
        doc = catalog.get(args.id)
        if not doc:
            raise SystemExit("contract not found")
        path = ROOT / doc["_path"]
        version = args.version or (doc.get("current_release") or {}).get("version")
        rel = None
        for release in doc.get("releases") or [doc.get("current_release")]:
            if release and release.get("version") == version:
                rel = release
                break
        if not rel:
            raise SystemExit("contract release not found")
        current = rel["state"]
        kind = "contract"
        errors += contract_gate(doc, args.to, version)
    elif args.entity == "roadmap_item":
        found = None
        for fdir in (ROOT / "features").glob("FEAT-*"):
            roadmap_path = fdir / "roadmap.yaml"
            if not roadmap_path.exists():
                continue
            roadmap = load_yaml(roadmap_path)
            for item in roadmap.get("items", []):
                if item.get("id") == args.id:
                    found = (roadmap_path, roadmap, item, fdir)
                    break
        if not found:
            raise SystemExit("roadmap item not found")
        roadmap_path, roadmap, item, fdir = found
        current = item.get("status", "PLANNED")
        kind = "roadmap_item"
        from state_machine import roadmap_item_gate

        errors += roadmap_item_gate(fdir, item, args.to)
        path = roadmap_path
        doc = item
    else:
        found = None
        for p in (ROOT / "integration/scenarios").glob("*.yaml"):
            d = load_yaml(p)
            if d.get("scenario_id") == args.id:
                found = (p, d)
                break
        if not found:
            raise SystemExit("integration not found")
        path, doc = found
        current = doc["state"]
        kind = "integration"

    if not allowed(kind, current, args.to):
        errors.append(f"illegal transition {current} -> {args.to}")
    if errors:
        print("TRANSITION BLOCKED")
        for e in errors:
            print("-", e)
        raise SystemExit(2)
    print(f"TRANSITION OK {args.entity}:{args.id} {current} -> {args.to}")
    if not args.apply:
        return

    append_transition_event(
        entity_type=args.entity,
        entity_id=args.id,
        from_state=current,
        to_state=args.to,
        actor=args.actor,
        source="human" if args.actor != "smc-governance-bot" else "reconciler",
        reason=args.reason,
        evidence=args.evidence,
        apply=True,
    )

    clean = {k: v for k, v in doc.items() if k != "_path"}
    if args.entity == "contract":
        for release in clean.get("releases") or []:
            if release.get("version") == version:
                release["state"] = args.to
        if (clean.get("current_release") or {}).get("version") == version:
            clean["current_release"]["state"] = args.to
    elif args.entity == "roadmap_item":
        for item in roadmap.get("items", []):
            if item.get("id") == args.id:
                item["status"] = args.to
        dump_yaml(path, roadmap)
        print("APPLIED")
        return
    else:
        clean["status" if args.entity != "integration" else "state"] = args.to
    dump_yaml(path, clean)
    print("APPLIED")


if __name__ == "__main__":
    main()
