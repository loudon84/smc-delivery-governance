from __future__ import annotations

from typing import Any

from ges.io import sha256_bytes
from ges.source_adapters.base import ProjectedFile


def file_hash(content: bytes) -> str:
    return sha256_bytes(content)


def hash_record(item: ProjectedFile) -> dict[str, Any]:
    return {
        "generated": file_hash(item.content),
        "last_applied": file_hash(item.content),
        "upstream_sha": item.source_sha,
        "kind": item.kind,
        "capability": item.capability,
    }
