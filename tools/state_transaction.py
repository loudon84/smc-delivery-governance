from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Callable

import yaml

from audit_events import append_transition_event

def _yaml_bytes(doc: dict) -> bytes:
    return yaml.safe_dump(doc, sort_keys=False, allow_unicode=True).encode("utf-8")

def commit_yaml_transition(
    *,
    path: Path,
    new_doc: dict,
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
) -> dict | None:
    if not apply:
        return None

    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_bytes() if path.exists() else None
    data = _yaml_bytes(new_doc)

    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    os.close(fd)
    temp = Path(temp_name)
    try:
        temp.write_bytes(data)
        # Verify the materialized YAML before replacing the current state.
        yaml.safe_load(temp.read_text(encoding="utf-8"))
        os.replace(temp, path)
        try:
            event = append_transition_event(
                entity_type=entity_type,
                entity_id=entity_id,
                from_state=from_state,
                to_state=to_state,
                actor=actor,
                source=source,
                reason=reason,
                evidence=evidence or [],
                idempotency_key=idempotency_key,
                apply=True,
            )
            return event
        except Exception:
            # Local transaction rollback. Git commit remains the outer transaction boundary.
            if old is None:
                path.unlink(missing_ok=True)
            else:
                rollback = path.with_name(path.name + ".rollback")
                rollback.write_bytes(old)
                os.replace(rollback, path)
            raise
    finally:
        temp.unlink(missing_ok=True)
