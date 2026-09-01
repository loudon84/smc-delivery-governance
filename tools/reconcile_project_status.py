from __future__ import annotations

from collections import deque

from governance_lib import ROOT, load_yaml, repository_catalog
from state_machine import allowed
from state_transaction import commit_yaml_transition

def transition_path(current: str, target: str):
    graph=load_yaml(ROOT/"contracts/lifecycle/states.yaml")["repository"]["transitions"]
    q=deque([(current,[])])
    seen={current}
    while q:
        state,path=q.popleft()
        if state==target:return path
        for nxt in graph.get(state,[]):
            if nxt not in seen:
                seen.add(nxt);q.append((nxt,path+[nxt]))
    return None

def main():
    repos=repository_catalog()
    wp_states={rid:[] for rid in repos}
    for fdir in (ROOT/"features").glob("FEAT-*"):
        for p in (fdir/"work-packages").glob("*.yaml"):
            wp=load_yaml(p);rid=wp.get("repository_id")
            if rid in wp_states and wp.get("status")!="SUPERSEDED":
                wp_states[rid].append(wp.get("sync_state","UNKNOWN"))

    for rid,repo0 in repos.items():
        states=wp_states[rid];current=repo0.get("governance_state","REGISTERED")
        if current in {"PAUSED","RETIRED"}:
            print(f"{rid}: {current}");continue
        if not states:target="REGISTERED"
        elif all(s=="SYNCED" for s in states):target="ENFORCED" if current=="ENFORCED" else "SYNCED"
        else:target="OUT_OF_SYNC"
        if target==current:
            print(f"{rid}: {current}");continue
        path=transition_path(current,target)
        if path is None:
            raise SystemExit(f"{rid}: no legal governance transition {current}->{target}")
        doc={k:v for k,v in repo0.items() if k!="_path"}
        file_path=ROOT/repo0["_path"]
        for nxt in path:
            new={**doc,"governance_state":nxt}
            commit_yaml_transition(
                path=file_path,new_doc=new,entity_type="repository",entity_id=rid,
                from_state=current,to_state=nxt,actor="smc-governance-bot",source="reconciler",
                reason=f"derived from work-package sync states: {states}",evidence=[],apply=True,
            )
            print(f"{rid}: {current}->{nxt}")
            current=nxt;doc=new

if __name__=="__main__":main()
