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
SPECKIT_CLI_VERIFY = "SPECKIT_CLI_VERIFY"
SPECKIT_OFFICIAL_RENDER = "SPECKIT_OFFICIAL_RENDER"
SPECKIT_MANIFEST_COMPARE = "SPECKIT_MANIFEST_COMPARE"
GOLDEN_RESOLVE = "GOLDEN_RESOLVE"
GOLDEN_WORKTREE_CREATE = "GOLDEN_WORKTREE_CREATE"
GES_PREFLIGHT = "GES_PREFLIGHT"
GES_INIT = "GES_INIT"
GES_CHECK = "GES_CHECK"
GES_DOCTOR = "GES_DOCTOR"
CURSOR_STRUCTURAL_DISCOVERY = "CURSOR_STRUCTURAL_DISCOVERY"
CURSOR_RUNTIME_DISCOVERY = "CURSOR_RUNTIME_DISCOVERY"
SPECKIT_FUNCTIONAL_SMOKE = "SPECKIT_FUNCTIONAL_SMOKE"
GES_SECOND_INIT = "GES_SECOND_INIT"
EVIDENCE_WRITE = "EVIDENCE_WRITE"
GOLDEN_WORKTREE_CLEANUP = "GOLDEN_WORKTREE_CLEANUP"
RELEASE_GATE = "RELEASE_GATE"

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
    SPECKIT_CLI_VERIFY,
    SPECKIT_OFFICIAL_RENDER,
    SPECKIT_MANIFEST_COMPARE,
    GOLDEN_RESOLVE,
    GOLDEN_WORKTREE_CREATE,
    GES_PREFLIGHT,
    GES_INIT,
    GES_CHECK,
    GES_DOCTOR,
    CURSOR_STRUCTURAL_DISCOVERY,
    CURSOR_RUNTIME_DISCOVERY,
    SPECKIT_FUNCTIONAL_SMOKE,
    GES_SECOND_INIT,
    EVIDENCE_WRITE,
    GOLDEN_WORKTREE_CLEANUP,
    RELEASE_GATE,
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
