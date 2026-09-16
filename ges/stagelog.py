from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from typing import Any, TextIO

ANALYZE = "ANALYZE"
RESOLVE = "RESOLVE"
FETCH = "FETCH"
PROJECT = "PROJECT"
RECONCILE = "RECONCILE"
CHECK = "CHECK"
REMOVE = "REMOVE"

STAGES = (ANALYZE, RESOLVE, FETCH, PROJECT, RECONCILE, CHECK, REMOVE)


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
