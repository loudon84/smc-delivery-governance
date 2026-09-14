#!/usr/bin/env python3
"""Verify Superpowers method results — never advances Delivery State."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "smc.ges.method-result.v1"


def _sha_payload(obj: dict) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def verify_result(
    result: dict,
    *,
    packet: dict,
    allowed_writes: list[str],
) -> tuple[str, list[str]]:
    # @lat: [[safety-runtime-closure-v503]]
    if not isinstance(result, dict) or result.get("schema") != SCHEMA:
        return "SUPERPOWERS_RESULT_INVALID", ["schema"]
    if result.get("provider") != "superpowers":
        return "SUPERPOWERS_RESULT_INVALID", ["provider"]
    if result.get("plan_semantic_hash") != packet.get("plan_semantic_hash"):
        return "SUPERPOWERS_RESULT_STALE", ["plan_semantic_hash"]
    if result.get("todo_id") != packet.get("todo_id"):
        return "SUPERPOWERS_RESULT_STALE", ["todo_id"]
    body = {k: v for k, v in result.items() if k != "result_digest"}
    if result.get("result_digest") != _sha_payload(body):
        return "SUPERPOWERS_RESULT_INVALID", ["result_digest"]
    changed = result.get("changed_paths") or []
    for path in changed:
        if not any(str(path).startswith(own) or str(path) == own for own in allowed_writes):
            return "SUPERPOWERS_SCOPE_VIOLATION", [str(path)]
    # Provider self-reported PASS never substitutes for GES final evidence.
    if result.get("provider_self_pass") is True:
        return "OK_PROVIDER_PASS_NOT_EVIDENCE", ["provider_self_pass_ignored"]
    return "OK", []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("result", type=Path)
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--allow-write", action="append", default=[])
    a = ap.parse_args()
    result = json.loads(a.result.read_text(encoding="utf-8"))
    packet = json.loads(a.packet.read_text(encoding="utf-8"))
    code, reasons = verify_result(result, packet=packet, allowed_writes=a.allow_write)
    print(json.dumps({"code": code, "reasons": reasons}, indent=2))
    if code.startswith("SUPERPOWERS_") or code == "DELIVERY_SCOPE_DRIFT":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
