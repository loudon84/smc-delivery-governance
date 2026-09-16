from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from typing import Any, TextIO

PREFLIGHT = "PREFLIGHT"
ANALYZE = "ANALYZE"
RESOLVE = "RESOLVE"
FETCH = "FETCH"
RENDER = "RENDER"
PROJECT = "PROJECT"
COLLISION_CHECK = "COLLISION_CHECK"
PLAN = "PLAN"
APPLY = "APPLY"
RECONCILE = "RECONCILE"
CHECK = "CHECK"
DOCTOR = "DOCTOR"
REMOVE = "REMOVE"

STAGES = (
    PREFLIGHT,
    ANALYZE,
    RESOLVE,
    FETCH,
    RENDER,
    PROJECT,
    COLLISION_CHECK,
    PLAN,
    APPLY,
    RECONCILE,
    CHECK,
    DOCTOR,
    REMOVE,
)


def emit(stage: str, event: str, **fields: Any) -> None:
    """Emit one structured Composer operation log line. No LLM telemetry."""
    if stage not in STAGES:
        raise ValueError(f"unknown stage: {stage}")
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "event": event,
        **fields,
    }
    _write(sys.stderr, record)


def _write(stream: TextIO, record: dict[str, Any]) -> None:
    stream.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    stream.flush()
