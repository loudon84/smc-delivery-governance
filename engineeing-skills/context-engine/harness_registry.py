"""Harness adapter registry (smc.ges.harness-registry.v1).

Production model calls must resolve a real adapter; fake adapters are test-only.
"""
from __future__ import annotations

import os
from typing import Callable

from harness_contract import (
    MODE_ENFORCED,
    MODE_OBSERVABLE,
    HarnessAdapter,
    classify_mode,
    cursor_observable_adapter,
    fake_enforced_adapter,
)

_REGISTRY: dict[str, Callable[[], HarnessAdapter]] = {
    "cursor-observable": cursor_observable_adapter,
}


def register_adapter(name: str, factory: Callable[[], HarnessAdapter]) -> None:
    if not name or not callable(factory):
        raise ValueError("HARNESS_ADAPTER_INVALID")
    _REGISTRY[name] = factory


def resolve_adapter(name: str | None = None, *, environment: str | None = None) -> HarnessAdapter:
    """Resolve an adapter by name; never silently returns a fake in production."""
    if name is None:
        name = os.environ.get("GES_HARNESS_ADAPTER") or "cursor-observable"
    if name == "fake-enforced":
        if os.environ.get("GES_TEST_MODE") != "1":
            raise ValueError("HARNESS_ADAPTER_REQUIRED")
        return fake_enforced_adapter()
    factory = _REGISTRY.get(name)
    if factory is None:
        raise ValueError("HARNESS_ADAPTER_NOT_FOUND")
    return factory()


def require_enforced_adapter(name: str | None = None) -> HarnessAdapter:
    adapter = resolve_adapter(name)
    mode = classify_mode(adapter.capability_map())
    if mode != MODE_ENFORCED:
        if mode == MODE_OBSERVABLE:
            raise ValueError("RUNTIME_COST_OBSERVABLE_NOT_ENFORCED")
        raise ValueError("RUNTIME_COST_UNMANAGED")
    return adapter


def list_adapters() -> list[str]:
    return sorted(_REGISTRY)


def self_check() -> dict:
    return {
        "ok": True,
        "registered": list_adapters(),
        "fake_isolated": "fake-enforced" not in _REGISTRY,
    }
