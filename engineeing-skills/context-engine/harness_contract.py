"""Harness adapter capability contract (smc.ges.harness-adapter.v1).

GES does not assume Cursor/Hermes expose identical token or tool APIs.
Adapters declare capabilities; modes are ENFORCED / OBSERVABLE / UNMANAGED.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

SCHEMA = "smc.ges.harness-adapter.v1"

CAPABILITY_KEYS = (
    "supports_usage_tokens",
    "supports_cache_usage",
    "supports_model_identity",
    "supports_tool_policy",
    "supports_allowed_roots",
    "supports_result_correlation",
    "supports_latency",
    "supports_retry_count",
)

MODE_ENFORCED = "ENFORCED"
MODE_OBSERVABLE = "OBSERVABLE"
MODE_UNMANAGED = "UNMANAGED"


@dataclass
class HarnessAdapter:
    """Declarative adapter; call() is optional for acceptance fakes."""

    name: str
    capabilities: dict[str, bool] = field(default_factory=dict)
    call: Callable[..., dict[str, Any]] | None = None

    def capability_map(self) -> dict[str, bool]:
        out = {k: False for k in CAPABILITY_KEYS}
        for k, v in (self.capabilities or {}).items():
            if k in out:
                out[k] = bool(v)
        return out

    def describe(self) -> dict[str, Any]:
        caps = self.capability_map()
        return {
            "schema": SCHEMA,
            "adapter": self.name,
            "capabilities": caps,
            "mode": classify_mode(caps),
        }


def classify_mode(capabilities: dict[str, bool]) -> str:
    """Return ENFORCED / OBSERVABLE / UNMANAGED from capability flags."""
    caps = {k: bool(capabilities.get(k)) for k in CAPABILITY_KEYS}
    if not caps.get("supports_result_correlation"):
        return MODE_UNMANAGED
    enforced_needed = (
        caps.get("supports_allowed_roots")
        and caps.get("supports_tool_policy")
        and caps.get("supports_model_identity")
        and (caps.get("supports_usage_tokens") or True)  # usage may be unavailable with reason
    )
    if enforced_needed and caps.get("supports_result_correlation"):
        if caps.get("supports_allowed_roots") and caps.get("supports_tool_policy"):
            return MODE_ENFORCED
    if caps.get("supports_result_correlation"):
        return MODE_OBSERVABLE
    return MODE_UNMANAGED


def fake_enforced_adapter(
    *,
    response: dict[str, Any] | None = None,
    usage: dict[str, Any] | None = None,
) -> HarnessAdapter:
    """Acceptance harness that can enforce roots and return correlated results."""

    def _call(**kwargs: Any) -> dict[str, Any]:
        out = {
            "provider": "fake",
            "model": "fake-model",
            "actual_tier": kwargs.get("requested_tier") or "STANDARD",
            "outcome": "OK",
            "retry_count": 0,
            "latency_ms": 1,
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
        }
        if usage is not None:
            out.update(usage)
        if response is not None:
            out["response"] = response
            out.update({k: v for k, v in response.items() if k not in {"response"}})
        return out

    return HarnessAdapter(
        name="fake-enforced",
        capabilities={k: True for k in CAPABILITY_KEYS},
        call=_call,
    )


def cursor_observable_adapter() -> HarnessAdapter:
    """Cursor-like adapter: correlatable but cannot hard-limit repo reads."""
    return HarnessAdapter(
        name="cursor-observable",
        capabilities={
            "supports_usage_tokens": False,
            "supports_cache_usage": False,
            "supports_model_identity": True,
            "supports_tool_policy": False,
            "supports_allowed_roots": False,
            "supports_result_correlation": True,
            "supports_latency": True,
            "supports_retry_count": True,
        },
        call=None,
    )


def self_check(adapter: HarnessAdapter) -> tuple[bool, list[str]]:
    desc = adapter.describe()
    reasons: list[str] = []
    if desc["mode"] == MODE_UNMANAGED:
        reasons.append("HARNESS_COST_CAPABILITY_MISSING")
        return False, reasons
    if desc["mode"] == MODE_OBSERVABLE:
        reasons.append("RUNTIME_COST_OBSERVABLE_NOT_ENFORCED")
        return False, reasons
    return True, []
