from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from ges.catalog.loader import SourcePin
from ges.errors import UPSTREAM_SHA_NOT_PINNED, UPSTREAM_SOURCE_UNRESOLVED, GesError
from ges.stagelog import FETCH, emit

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def cache_root() -> Path:
    override = os.environ.get("GES_SOURCE_CACHE")
    if override:
        return Path(override)
    return Path.home() / ".cache" / "ges" / "sources"


def offline_mode() -> bool:
    return os.environ.get("GES_SOURCE_OFFLINE") == "1"


def ensure_source(pin: SourcePin) -> Path:
    if not SHA_RE.match(pin.commit_sha):
        raise GesError(UPSTREAM_SHA_NOT_PINNED, f"{pin.id} is not pinned to a 40-char SHA")
    dest = cache_root() / pin.cache_key / pin.commit_sha
    if _usable(dest):
        emit(FETCH, "cache-hit", source=pin.id, sha=pin.commit_sha)
        return dest
    if offline_mode():
        raise GesError(
            UPSTREAM_SOURCE_UNRESOLVED,
            f"source {pin.id}@{pin.commit_sha} is not in the local cache",
            details={"path": str(dest)},
        )
    emit(FETCH, "fetch", source=pin.id, sha=pin.commit_sha, repo=pin.repo)
    dest.mkdir(parents=True, exist_ok=True)
    try:
        _git_fetch(dest, pin.repo, pin.commit_sha)
    except Exception as exc:
        raise GesError(
            UPSTREAM_SOURCE_UNRESOLVED,
            f"failed to fetch {pin.id}@{pin.commit_sha}: {exc}",
        ) from exc
    if not _usable(dest):
        raise GesError(UPSTREAM_SOURCE_UNRESOLVED, f"fetched tree for {pin.id} is empty")
    return dest


def resolve_path(pin: SourcePin, source_path: str) -> Path:
    root = ensure_source(pin)
    rel = Path(source_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise GesError(UPSTREAM_SOURCE_UNRESOLVED, f"illegal source path {source_path}")
    target = (root / rel).resolve()
    if not str(target).startswith(str(root.resolve())):
        raise GesError(UPSTREAM_SOURCE_UNRESOLVED, f"path escapes source root: {source_path}")
    if not target.exists():
        raise GesError(
            UPSTREAM_SOURCE_UNRESOLVED,
            f"{pin.id} path {source_path} is missing at {pin.commit_sha}",
        )
    return target


def _usable(dest: Path) -> bool:
    if not dest.is_dir():
        return False
    for path in dest.iterdir():
        if path.name != ".git":
            return True
    return False


def _git_fetch(dest: Path, repo: str, sha: str) -> None:
    if not (dest / ".git").exists():
        _run(["git", "init"], dest)
        _run(["git", "remote", "add", "origin", repo], dest)
    _run(["git", "fetch", "--depth", "1", "origin", sha], dest)
    _run(["git", "checkout", "--force", "FETCH_HEAD"], dest)


def _run(args: list[str], cwd: Path) -> None:
    result = subprocess.run(args, cwd=cwd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git failed")


def copy_tree(src: Path, files: dict[str, bytes], dest_prefix: str) -> None:
    if src.is_file():
        files[f"{dest_prefix}/{src.name}" if dest_prefix else src.name] = src.read_bytes()
        return
    for path in src.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        rel = path.relative_to(src).as_posix()
        key = f"{dest_prefix}/{rel}" if dest_prefix else rel
        files[key] = path.read_bytes()
