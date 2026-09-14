"""Normalize filesystem identity and reject paths outside the repository."""
from __future__ import annotations

import os
from pathlib import Path

from coe_common import posix

SECRET_DIR_NAMES = frozenset({".git", "node_modules", ".venv", "venv"})
SECRET_NAME_MARKERS = ("secret", "credential", ".pem", ".key", "id_rsa")


def _long_path(path: Path) -> Path:
    if os.name != "nt":
        return path
    try:
        import ctypes
        from ctypes import wintypes

        GetLongPathNameW = ctypes.windll.kernel32.GetLongPathNameW  # type: ignore[attr-defined]
        GetLongPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        GetLongPathNameW.restype = wintypes.DWORD
        buf = ctypes.create_unicode_buffer(32768)
        n = GetLongPathNameW(str(path), buf, 32768)
        if n:
            return Path(buf.value)
    except (AttributeError, OSError, ValueError):
        pass
    return path


def resolve_inside(repo: Path, raw: str | Path) -> Path:
    repo = repo.resolve()
    value = Path(str(raw))
    if value.is_absolute():
        resolved = _long_path(value).resolve()
    else:
        if ".." in value.parts:
            raise ValueError(f"CONTEXT_PATH_OUTSIDE_REPO: {raw}")
        resolved = _long_path((repo / value)).resolve()
    try:
        resolved.relative_to(repo)
    except ValueError as exc:
        raise ValueError(f"CONTEXT_PATH_OUTSIDE_REPO: {raw}") from exc
    if resolved.exists() and resolved.is_symlink():
        target = resolved.resolve()
        try:
            target.relative_to(repo)
        except ValueError as exc:
            raise ValueError(f"CONTEXT_PATH_OUTSIDE_REPO: {raw}") from exc
    return resolved


def canonical_rel(repo: Path, raw: str | Path) -> str:
    resolved = resolve_inside(repo, raw)
    rel = resolved.relative_to(repo.resolve())
    return posix(rel.as_posix())


def identity_key(repo: Path, raw: str | Path) -> str:
    resolved = resolve_inside(repo, raw)
    return os.path.normcase(str(resolved))


def same_entity(repo: Path, left: str | Path, right: str | Path) -> bool:
    return identity_key(repo, left) == identity_key(repo, right)


def is_excluded_secret(rel: str) -> bool:
    parts = posix(rel).split("/")
    if any(part in SECRET_DIR_NAMES for part in parts):
        return True
    name = parts[-1].lower() if parts else ""
    return any(marker in name for marker in SECRET_NAME_MARKERS)
