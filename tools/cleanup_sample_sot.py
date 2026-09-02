from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from governance_lib import ROOT, dump_yaml, load_feature, load_work_packages, load_yaml

SAMPLE_MARKERS = ("examples/sample-receipts", "examples\\sample-receipts")

def contaminated_path(value) -> bool:
    text = str(value or "")
    return any(marker in text for marker in SAMPLE_MARKERS)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("feature")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    fdir, feature = load_feature(args.feature)
    wps = load_work_packages(fdir)
    affected = []
    for wid, wp0 in wps.items():
        ledger = fdir / "delivery-ledger" / f"{wp0['repository_id']}.yaml"
        wp = {k:v for k,v in wp0.items() if k != "_path"}
        observed = wp.get("observed") or {}
        contaminated = contaminated_path(observed.get("receipt_path"))
        if ledger.exists():
            ld = load_yaml(ledger)
            contaminated = contaminated or contaminated_path(ld.get("receipt_path"))
        if contaminated:
            affected.append((wid, wp0["repository_id"], ledger))
            print(f"CONTAMINATED {wid} repo={wp0['repository_id']}")
            if args.apply:
                if ledger.exists():
                    quarantine = ROOT / "audit/quarantine/sample-contaminated" / feature["feature_id"]
                    quarantine.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(ledger), quarantine / f"{wp0['repository_id']}.yaml")
                wp["sync_state"] = "MISSING_RECEIPT"
                wp.pop("delivery_receipt", None)
                wp.pop("observed", None)
                # Sample-backed VERIFIED/DONE is not evidence. Demote before a real receipt exists.
                if wp.get("status") in {"VERIFIED", "DONE"}:
                    wp["status"] = "IMPLEMENTING"
                dump_yaml(fdir / "work-packages" / Path(wp0["_path"]).name, wp)

    if args.apply and affected:
        trace_path = fdir / "traceability.yaml"
        if trace_path.exists():
            trace = load_yaml(trace_path)
            affected_ids = {wid for wid,_,_ in affected}
            for item in trace.get("work_packages", []):
                if item.get("work_package_id") in affected_ids:
                    for key in ("stage_prds","issues","bugs","plans","commits","verification"):
                        item[key] = []
            dump_yaml(trace_path, trace)


        # Quarantine transition facts for entities whose observed source was the test Sample.
        # This removes test-generated lifecycle facts without pretending they are production evidence.
        affected_ids={wid for wid,_,_ in affected}
        roadmap_ids=set()
        rp=fdir/"roadmap.yaml"
        if rp.exists():
            roadmap_ids={x.get("id") for x in (load_yaml(rp).get("items") or []) if x.get("id")}
        scenario_id=(feature.get("integration") or {}).get("scenario_id")
        quarantine_events=[]
        audit_root=ROOT/"audit/transitions"
        if audit_root.exists():
            for event_file in sorted(audit_root.rglob("events.ndjson")):
                kept=[]
                for line in event_file.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    event=json.loads(line)
                    contaminated_event=(
                        (event.get("entity_type")=="work_package" and event.get("entity_id") in affected_ids)
                        or (event.get("entity_type")=="feature" and event.get("entity_id")==feature["feature_id"])
                        or (event.get("entity_type")=="roadmap_item" and event.get("entity_id") in roadmap_ids)
                        or (event.get("entity_type")=="integration" and event.get("entity_id")==scenario_id)
                    )
                    if contaminated_event:
                        quarantine_events.append(event)
                    else:
                        kept.append(line)
                event_file.write_text(("\n".join(kept)+"\n") if kept else "",encoding="utf-8",newline="\n")
        if quarantine_events:
            q=ROOT/"audit/quarantine/sample-contaminated"/feature["feature_id"]/"transition-events.ndjson"
            q.parent.mkdir(parents=True,exist_ok=True)
            q.write_text("\n".join(json.dumps(e,ensure_ascii=False) for e in quarantine_events)+"\n",encoding="utf-8",newline="\n")

        repos = {rid for _,rid,_ in affected}
        for reg in (ROOT / "registry/repositories").glob("*.yaml"):
            doc = load_yaml(reg)
            if doc.get("repository_id") in repos:
                doc["governance_state"] = "OUT_OF_SYNC"
                dump_yaml(reg, doc)

    if not affected:
        print("NO SAMPLE CONTAMINATION")
    elif args.apply:
        print("SAMPLE CONTAMINATION QUARANTINED; real remote receipts are now required")
    else:
        print("DRY RUN; use --apply")

if __name__ == "__main__":
    main()
