"""External execution adapter capability reports. Unverified adapters stay planned."""
from __future__ import annotations

from typing import Any

STATUSES = {"planned", "adapter_ready", "verified"}


def report(
    name: str,
    *,
    version: str = "",
    request_id: str = "",
    result_id: str = "",
    output_digest: str = "",
    tool_access: str = "ADVISORY",
    token_availability: str = "missing",
    status: str = "planned",
) -> dict[str, Any]:
    if status not in STATUSES:
        status = "planned"
    return {
        "adapter": name,
        "version": version,
        "request_id": request_id,
        "result_id": result_id,
        "output_digest": output_digest,
        "tool_access": tool_access,
        "token_availability": token_availability,
        "status": status,
        "claim": "ADAPTER_READY" if status == "adapter_ready" else "PLANNED" if status == "planned" else "EXTERNAL_VERIFIED",
    }
