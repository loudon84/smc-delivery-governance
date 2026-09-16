from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

from ges.errors import WORK_ALREADY_EXISTS, WORK_CLOSED_IMMUTABLE, WORK_ID_INVALID, WORK_STATE_TRANSITION_INVALID, GesError
from ges.governance.paths import work_path
from ges.governance.storage import load_work, now_rfc3339, require_governance, write_work
from ges.stagelog import WORK_VALIDATE, emit

WORK_ID_RE = re.compile(r"^[A-Z][A-Z0-9._-]{2,63}$")


def create_work(repo: Path, *, work_id: str, title: str, owner: str, risk: str) -> dict[str, Any]:
    require_governance(repo)
    if not WORK_ID_RE.fullmatch(work_id):
        raise GesError(WORK_ID_INVALID, f"invalid work id: {work_id}")
    if work_path(repo, work_id).exists():
        raise GesError(WORK_ALREADY_EXISTS, f"work already exists: {work_id}")
    stamp = now_rfc3339()
    payload = {
        "schema": "ges.work.v1",
        "id": work_id,
        "kind": "FEATURE",
        "title": title,
        "status": "OPEN",
        "owner": owner,
        "risk": risk,
        "policy": "default-v1",
        "artifacts": [],
        "created_at": stamp,
        "updated_at": stamp,
    }
    emit(WORK_VALIDATE, "complete", work_id=work_id)
    write_work(repo, payload, create=True)
    return payload


def show_work(repo: Path, work_id: str) -> dict[str, Any]:
    return load_work(repo, work_id)


def update_work(repo: Path, work_id: str, *, title: str | None = None, owner: str | None = None, risk: str | None = None, policy: str | None = None) -> dict[str, Any]:
    current = load_work(repo, work_id)
    original = copy.deepcopy(current)
    if current["status"] == "CLOSED":
        raise GesError(WORK_CLOSED_IMMUTABLE, f"closed work cannot be updated: {work_id}")
    if title is not None:
        current["title"] = title
    if owner is not None:
        current["owner"] = owner
    if risk is not None:
        current["risk"] = risk
    if policy is not None:
        current["policy"] = policy
    current["updated_at"] = now_rfc3339()
    write_work(repo, current)
    _ = original
    return current


def close_work(repo: Path, work_id: str) -> dict[str, Any]:
    current = load_work(repo, work_id)
    if current["status"] != "OPEN":
        raise GesError(WORK_STATE_TRANSITION_INVALID, "only OPEN work can be closed")
    current["status"] = "CLOSED"
    current["updated_at"] = now_rfc3339()
    write_work(repo, current)
    return current
