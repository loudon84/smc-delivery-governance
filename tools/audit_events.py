from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from governance_lib import ROOT

def _events_path(when: datetime | None = None) -> Path:
    ts=when or datetime.now(timezone.utc)
    return ROOT/"audit"/"transitions"/f"{ts.year:04d}"/f"{ts.month:02d}"/"events.ndjson"

def _find_idempotency_key(key: str) -> dict | None:
    base=ROOT/"audit"/"transitions"
    if not base.exists():return None
    for path in sorted(base.rglob("events.ndjson")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():continue
            event=json.loads(line)
            if event.get("idempotency_key")==key:return event
    return None

# @lat: [[facts-and-evidence#Audit Event]]
def append_transition_event(
    *,
    entity_type:str,
    entity_id:str,
    from_state:str,
    to_state:str,
    actor:str,
    source:str,
    reason:str,
    evidence:list[str]|None=None,
    idempotency_key:str|None=None,
    apply:bool=True,
)->dict:
    now=datetime.now(timezone.utc)
    # Default keys are unique. Callers that need retry idempotency must provide a
    # source-derived key (for example dispatch delivery id / workflow run id).
    key=idempotency_key or f"auto-{uuid.uuid4()}"
    event={
      "event_id":f"GOV-EVT-{uuid.uuid4()}",
      "entity_type":entity_type,"entity_id":entity_id,
      "from":from_state,"to":to_state,
      "actor":actor,"source":source,"reason":reason,
      "evidence":evidence or [],
      "timestamp":now.isoformat(),
      "idempotency_key":key,
    }
    if not apply:return event
    if idempotency_key:
        existing=_find_idempotency_key(key)
        if existing:return existing
    path=_events_path(now);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a",encoding="utf-8",newline="\n") as h:
        h.write(json.dumps(event,ensure_ascii=False)+"\n")
    return event
