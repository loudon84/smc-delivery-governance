from __future__ import annotations

from pathlib import Path

from ges.paths import BUSINESS_SOURCE_ROOTS


def business_source_roots(repo: Path) -> list[str]:
    roots: list[str] = []
    for name in BUSINESS_SOURCE_ROOTS:
        if (repo / name).is_dir():
            roots.append(name)
    return roots


def iter_business_files(repo: Path) -> list[Path]:
    files: list[Path] = []
    for root in business_source_roots(repo):
        base = repo / root
        for path in base.rglob("*"):
            if path.is_file() and ".git" not in path.parts:
                files.append(path)
    return files
