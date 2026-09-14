"""Treat source/review instructions as data; keep secrets and revoked caches out of packages."""
from __future__ import annotations

from typing import Any

from path_identity import is_excluded_secret

INJECTION_MARKERS = ("ignore previous policy", "override governance", "set governed=false")


def policy_as_data(policy: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    frozen = dict(policy)
    for item in items:
        text = str(item.get("excerpt") or "").lower()
        if any(marker in text for marker in INJECTION_MARKERS):
            item["data_only"] = True
            item["reason"] = item.get("reason") or "untrusted_instruction"
    return frozen


def filter_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kept = []
    for item in items:
        path = str(item.get("path") or "")
        if path and is_excluded_secret(path):
            continue
        kept.append(item)
    return kept


def cache_key(**parts: str) -> str:
    from coe_common import sha256_json

    return sha256_json(parts)


class AccessCache:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._policy = "default"

    def put(self, key: str, value: str, policy: str) -> None:
        self._store[f"{policy}:{key}"] = value

    def get(self, key: str, policy: str) -> str | None:
        if policy != self._policy and self._policy == "revoked":
            return None
        return self._store.get(f"{policy}:{key}")

    def revoke(self) -> None:
        self._policy = "revoked"
        self._store.clear()
