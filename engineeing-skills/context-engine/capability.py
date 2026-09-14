"""Host read-capability handshake. ENFORCED requires a verified gateway."""
from __future__ import annotations

from typing import Any

MODES = {"ADVISORY", "ENFORCED"}


def handshake(host: dict[str, Any] | None = None) -> dict[str, Any]:
    host = host or {}
    requested = str(host.get("requested_mode") or host.get("mode") or "ADVISORY").upper()
    gateway = bool(host.get("read_gateway_verified") or host.get("file_gateway_verified"))
    if requested not in MODES:
        requested = "ADVISORY"
    mode = "ENFORCED" if requested == "ENFORCED" and gateway else "ADVISORY"
    ok = True
    reason = ""
    if requested == "ENFORCED" and not gateway:
        ok = False
        reason = "CONTEXT_ACCESS_UNSUPPORTED"
        mode = "ADVISORY"
    return {
        "mode": mode,
        "requested": requested,
        "verified": gateway and requested == "ENFORCED",
        "ok": ok,
        "reason": reason,
    }


def assert_enforced(host: dict[str, Any]) -> dict[str, Any]:
    result = handshake({**host, "requested_mode": "ENFORCED"})
    if result["mode"] != "ENFORCED":
        raise ValueError("CONTEXT_ACCESS_UNSUPPORTED")
    return result
