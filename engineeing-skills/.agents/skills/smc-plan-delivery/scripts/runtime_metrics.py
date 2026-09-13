#!/usr/bin/env python3
"""Runtime telemetry for Harness adapters; never Final Evidence / Delivery Truth."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import atomic_write, find_repo_root, plan_id, utc_now

SCHEMA = "smc.execution.telemetry.v1"
FORBIDDEN = ("prompt", "source", "secret", "token_value", "api_key", "password")


def telemetry_path(plan: Path) -> Path:
    root = find_repo_root(plan)
    return root / ".smc" / "runs" / plan_id(plan) / "telemetry" / "events.jsonl"


def _append(plan: Path, event: dict) -> Path:
    for key in FORBIDDEN:
        if key in event:
            raise ValueError("TELEMETRY_SCHEMA_INVALID: forbidden field " + key)
    event = {"schema": SCHEMA, "at": utc_now(), "plan_id": plan_id(plan), **event}
    path = telemetry_path(plan)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def dispatch(plan: Path, **fields) -> Path:
    return _append(plan, {"phase": fields.get("phase", "IMPLEMENT"), "kind": "dispatch", **fields})


def result(plan: Path, **fields) -> Path:
    return _append(plan, {"kind": "result", **fields})


def cache_hit(plan: Path, path_key_hash: str = "") -> Path:
    return _append(plan, {"kind": "cache-hit", "source_context_hits": 1, "path_key_hash": path_key_hash})


def cache_miss(plan: Path, path_key_hash: str = "") -> Path:
    return _append(plan, {"kind": "cache-miss", "source_context_misses": 1, "path_key_hash": path_key_hash})


def reviewer_seat(plan: Path, seats: int = 1, mode: str = "UNIFIED") -> Path:
    return _append(plan, {"kind": "reviewer-seat", "reviewer_seats": seats, "mode": mode})


def summarize(plan: Path) -> dict:
    # @lat: [[acceptance-hardening#Runtime Telemetry]]
    path = telemetry_path(plan)
    if not path.is_file():
        return {
            "schema": SCHEMA,
            "complete": False,
            "status": "TELEMETRY_INCOMPLETE",
            "code": "TELEMETRY_INCOMPLETE",
            "events": 0,
        }
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    totals = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "retry_count": 0,
        "source_context_hits": 0,
        "source_context_misses": 0,
        "reviewer_seats": 0,
    }
    for ev in events:
        for k in totals:
            totals[k] += int(ev.get(k) or 0)
    return {"schema": SCHEMA, "complete": True, "events": len(events), **totals}


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("dispatch", "result", "cache-hit", "cache-miss", "reviewer-seat", "summarize"):
        p = sub.add_parser(name)
        p.add_argument("plan", type=Path)
        if name in {"dispatch", "result"}:
            p.add_argument("--phase", default="IMPLEMENT")
            p.add_argument("--todo", default="")
            p.add_argument("--requested-tier", default="")
            p.add_argument("--actual-tier", default="")
            p.add_argument("--provider", default="")
            p.add_argument("--model", default="")
            p.add_argument("--prompt-tokens", type=int, default=0)
            p.add_argument("--completion-tokens", type=int, default=0)
            p.add_argument("--outcome", default="")
        if name in {"cache-hit", "cache-miss"}:
            p.add_argument("--path-key-hash", default="")
        if name == "reviewer-seat":
            p.add_argument("--seats", type=int, default=1)
            p.add_argument("--mode", default="UNIFIED")
        p.add_argument("--json", action="store_true")
    a = ap.parse_args()
    plan = a.plan.resolve()
    if a.cmd == "summarize":
        out = summarize(plan)
        print(json.dumps(out, indent=2) if a.json else out)
        return 0 if out.get("complete") else 2
    fields = {k.replace("-", "_"): v for k, v in vars(a).items() if k not in {"cmd", "plan", "json"} and v not in ("", None)}
    fn = {
        "dispatch": dispatch,
        "result": result,
        "cache-hit": cache_hit,
        "cache-miss": cache_miss,
        "reviewer-seat": reviewer_seat,
    }[a.cmd]
    path = fn(plan, **fields)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
