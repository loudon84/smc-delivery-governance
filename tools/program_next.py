from __future__ import annotations
import sys
from pathlib import Path
from governance_lib import load_yaml

DONE = {"DONE", "SUPERSEDED"}

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: program_next.py <program-roadmap.yaml>")
    doc = load_yaml(Path(sys.argv[1]))
    items = doc.get("items", [])
    states = {i["id"]: i.get("status") for i in items}
    ready = []
    for item in items:
        if item.get("status") in DONE:
            continue
        if all(states.get(d) in DONE for d in item.get("depends_on", [])):
            ready.append(item)
    if not ready:
        print("NO_READY_ITEM")
        return
    for item in ready:
        print(f"{item['id']} | {item.get('status')} | {item.get('title')} | feature={item.get('feature_id')}")

if __name__ == "__main__":
    main()
