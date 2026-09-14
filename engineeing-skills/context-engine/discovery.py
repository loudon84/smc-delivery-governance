"""Directory/import discovery produces PROPOSED records only."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from coe_common import posix
from path_identity import canonical_rel


SKIP_DIRS = {".git", ".smc", ".agents", "node_modules", "__pycache__", ".venv"}


def discover(repo: Path) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    src = repo / "src"
    roots = [src] if src.is_dir() else [p for p in repo.iterdir() if p.is_dir() and p.name not in SKIP_DIRS]
    for root in roots:
        for child in sorted(root.iterdir() if root.is_dir() else []):
            if not child.is_dir() or child.name in SKIP_DIRS:
                continue
            try:
                rel = canonical_rel(repo, child)
            except ValueError:
                continue
            proposals.append(
                {
                    "id": child.name,
                    "kind": "module",
                    "status": "PROPOSED",
                    "owner": "",
                    "include": [posix(rel) + "/**"],
                    "source": "directory-scan",
                }
            )
    return proposals
