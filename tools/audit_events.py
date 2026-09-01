from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from governance_lib import ROOT


def _events_path(when: datetime | None = None) -> Path:
    ts = when or datetime.now(timezone.utc)
    return ROOT / "audit" / "transitions" / f"{ts.year:04d}" / f"{ts.month:02d}" / "events.ndjson"


def append_transition_event(
    *,
    entity_type: str,
    entity_id: str,
    from_state: str,
    to_state: str,
    actor: str,
    source: str,
    reason: str,
    evidence: list[str] | None = None,
    idempotency_key: str | None = None,
    apply: bool = True,
) -> dict:
    now = datetime.now(timezone.utc)
    key = idempotency_key or hashlib.sha256(
        f"{entity_type}:{entity_id}:{from_state}:{to_state}:{reason}".encode()
    ).hexdigest()[:32]
    event = {
        "event_id": f"GOV-EVT-{uuid.uuid4()}",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "from": from_state,
        "to": to_state,
        "actor": actor,
        "source": source,
        "reason": reason,
        "evidence": evidence or [],
        "timestamp": now.isoformat(),
        "idempotency_key": key,
    }
    if not apply:
        return event
    path = _events_path(now)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            existing = json.loads(line)
            if existing.get("idempotency_key") == key:
                return existing
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event
