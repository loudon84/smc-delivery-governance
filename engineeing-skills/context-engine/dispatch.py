"""Dispatch identity, epoch binding, and external receipt handling."""
from __future__ import annotations

from typing import Any


class DispatchLedger:
    def __init__(self) -> None:
        self.rows: dict[str, dict[str, Any]] = {}
        self.roadmap_done = False

    def dispatch(self, dispatch_id: str, epoch: int, todo: str) -> dict[str, Any]:
        existing = self.rows.get(dispatch_id)
        if existing:
            return {**existing, "duplicate": True}
        row = {
            "dispatch_id": dispatch_id,
            "epoch": int(epoch),
            "todo": todo,
            "status": "DISPATCHED",
            "duplicate": False,
        }
        self.rows[dispatch_id] = row
        return row

    def accept_receipt(self, dispatch_id: str, epoch: int, *, external_done: bool = False, current_epoch: int | None = None) -> dict[str, Any]:
        row = self.rows.get(dispatch_id)
        if row is None:
            raise ValueError("CONTEXT_DISPATCH_UNKNOWN")
        live_epoch = current_epoch if current_epoch is not None else row["epoch"]
        if int(epoch) != int(live_epoch):
            raise ValueError("CONTEXT_EPOCH_MISMATCH")
        if external_done:
            row["status"] = "EXTERNAL_REPORTED"
            return {**row, "roadmap_done": False}
        row["status"] = "ACCEPTED"
        return row

    def mark_local_done(self, dispatch_id: str) -> None:
        row = self.rows[dispatch_id]
        if row.get("status") != "ACCEPTED":
            raise ValueError("CONTEXT_DISPATCH_NOT_ACCEPTED")
        row["status"] = "LOCAL_COMPLETE"
