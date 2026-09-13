#!/usr/bin/env python3
"""Runtime telemetry for Harness adapters; never Final Evidence / Delivery Truth."""
from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

from common import find_repo_root, plan_id, utc_now

SCHEMA = "smc.execution.telemetry.v1"
COMPLETENESS_SCHEMA = "smc.execution.telemetry-completeness.v1"
FORBIDDEN = ("prompt", "source", "secret", "token_value", "api_key", "password")
DISPATCH_REQUIRED = ("plan_id", "todo", "phase", "requested_tier", "dispatch_id", "agent")
RESULT_REQUIRED = (
    "dispatch_id",
    "actual_tier",
    "provider",
    "model",
    "outcome",
    "retry_count",
    "latency_ms",
    "prompt_tokens",
    "completion_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
)


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
    did = fields.get("dispatch_id") or uuid.uuid4().hex
    payload = {
        "kind": "dispatch",
        "phase": fields.get("phase", "IMPLEMENT"),
        "todo": fields.get("todo", ""),
        "requested_tier": fields.get("requested_tier", ""),
        "dispatch_id": did,
        "agent": fields.get("agent", ""),
    }
    return _append(plan, payload)


def result(plan: Path, **fields) -> Path:
    payload = {"kind": "result", **fields}
    if "dispatch_id" not in payload:
        raise ValueError("TELEMETRY_REQUIRED_FIELD_MISSING: dispatch_id")
    if fields.get("actual_tier") and fields.get("requested_tier"):
        if fields["actual_tier"] != fields["requested_tier"]:
            payload["fallback"] = True
            if not fields.get("fallback_reason"):
                raise ValueError("TELEMETRY_REQUIRED_FIELD_MISSING: fallback_reason")
    usage_keys = ("prompt_tokens", "completion_tokens", "cache_read_tokens", "cache_write_tokens")
    if all(fields.get(k) in (None, "") for k in usage_keys) and not fields.get("usage_unavailable_reason"):
        # zeros alone are allowed only when explicitly provided; missing must explain
        if not any(k in fields for k in usage_keys):
            raise ValueError("TELEMETRY_USAGE_UNAVAILABLE")
    return _append(plan, payload)


def cache_hit(plan: Path, path_key_hash: str = "") -> Path:
    return _append(plan, {"kind": "cache-hit", "source_context_hits": 1, "path_key_hash": path_key_hash})


def cache_miss(plan: Path, path_key_hash: str = "") -> Path:
    return _append(plan, {"kind": "cache-miss", "source_context_misses": 1, "path_key_hash": path_key_hash})


def reviewer_seat(plan: Path, seats: int = 1, mode: str = "UNIFIED") -> Path:
    return _append(plan, {"kind": "reviewer-seat", "reviewer_seats": seats, "mode": mode})


def summarize(plan: Path) -> dict:
    # @lat: [[acceptance-hardening#Runtime Telemetry]]
    # @lat: [[acceptance-closure#Telemetry Dispatch Correlation]]
    path = telemetry_path(plan)
    if not path.is_file():
        return {
            "schema": COMPLETENESS_SCHEMA,
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
            val = ev.get(k)
            if val is None:
                continue
            if int(val) < 0:
                return {
                    "schema": COMPLETENESS_SCHEMA,
                    "complete": False,
                    "status": "TELEMETRY_INCOMPLETE",
                    "code": "TELEMETRY_INCOMPLETE",
                    "detail": "negative metric",
                }
            totals[k] += int(val)

    dispatches = {e.get("dispatch_id"): e for e in events if e.get("kind") == "dispatch" and e.get("dispatch_id")}
    results = [e for e in events if e.get("kind") == "result"]
    result_ids = {e.get("dispatch_id") for e in results if e.get("dispatch_id")}
    errors = []
    for did, d in dispatches.items():
        missing = [k for k in DISPATCH_REQUIRED if not d.get(k)]
        if missing:
            errors.append({"code": "TELEMETRY_REQUIRED_FIELD_MISSING", "detail": ",".join(missing)})
        if did not in result_ids:
            errors.append({"code": "TELEMETRY_ORPHAN_DISPATCH", "detail": did})
    for r in results:
        if r.get("dispatch_id") not in dispatches:
            errors.append({"code": "TELEMETRY_ORPHAN_RESULT", "detail": str(r.get("dispatch_id"))})
        missing = [k for k in RESULT_REQUIRED if k not in r]
        # usage may be replaced by usage_unavailable_reason
        if r.get("usage_unavailable_reason"):
            missing = [k for k in missing if k not in {
                "prompt_tokens", "completion_tokens", "cache_read_tokens", "cache_write_tokens"
            }]
        if missing:
            errors.append({"code": "TELEMETRY_REQUIRED_FIELD_MISSING", "detail": ",".join(missing)})
    kinds = {e.get("kind") for e in events}
    if kinds <= {"cache-hit", "cache-miss", "reviewer-seat"} or not dispatches:
        return {
            "schema": COMPLETENESS_SCHEMA,
            "complete": False,
            "status": "TELEMETRY_INCOMPLETE",
            "code": "TELEMETRY_INCOMPLETE",
            "events": len(events),
            **totals,
        }
    if errors:
        return {
            "schema": COMPLETENESS_SCHEMA,
            "complete": False,
            "status": "TELEMETRY_INCOMPLETE",
            "code": errors[0]["code"],
            "errors": errors,
            "events": len(events),
            **totals,
        }
    return {
        "schema": COMPLETENESS_SCHEMA,
        "complete": True,
        "status": "COMPLETE",
        "events": len(events),
        "dispatch_count": len(dispatches),
        **totals,
    }


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
            p.add_argument("--prompt-tokens", type=int, default=None)
            p.add_argument("--completion-tokens", type=int, default=None)
            p.add_argument("--cache-read-tokens", type=int, default=None)
            p.add_argument("--cache-write-tokens", type=int, default=None)
            p.add_argument("--retry-count", type=int, default=0)
            p.add_argument("--latency-ms", type=int, default=0)
            p.add_argument("--outcome", default="")
            p.add_argument("--dispatch-id", default="")
            p.add_argument("--agent", default="")
            p.add_argument("--usage-unavailable-reason", default="")
            p.add_argument("--fallback-reason", default="")
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
    fields = {
        k.replace("-", "_"): v
        for k, v in vars(a).items()
        if k not in {"cmd", "plan", "json"} and v not in ("", None)
    }
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
