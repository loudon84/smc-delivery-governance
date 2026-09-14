"""Declared + Python import dependency graph with reverse closure and INCOMPLETE coverage."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any

from coe_common import posix, sha256_json
from registry import Registry, load_registry


def _module_from_file(repo: Path, path: Path) -> str:
    rel = path.relative_to(repo)
    parts = list(rel.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def parse_python_imports(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return []
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""


def build_graph(repo: Path, registry: Registry | None = None, *, changed: list[str] | None = None, previous: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = registry or load_registry(repo)
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    incomplete: list[str] = []
    scanned = 0

    for rec in registry.records:
        nodes[rec.rec_id] = {"id": rec.rec_id, "kind": rec.kind, "files": list(rec.include)}
        for dep in rec.allowed_dependencies:
            edges.append(
                {
                    "from": rec.rec_id,
                    "to": dep,
                    "type": "declared",
                    "source": rec.source,
                    "confidence": "high",
                }
            )
            if not any(r.rec_id == dep for r in registry.records):
                incomplete.append(f"unresolved_declared:{rec.rec_id}->{dep}")

    py_files = sorted(p for p in repo.rglob("*.py") if ".git" not in p.parts and "__pycache__" not in p.parts and ".agents" not in p.parts)
    if changed and previous and previous.get("file_index"):
        index = dict(previous["file_index"])
        changed_set = {posix(c) for c in changed}
        py_files = [p for p in py_files if posix(p.relative_to(repo).as_posix()) in changed_set or any(posix(p.relative_to(repo).as_posix()).startswith(c.rstrip("/") + "/") for c in changed_set)]
        scanned = len(py_files)
        for path in py_files:
            rel = posix(path.relative_to(repo).as_posix())
            index[rel] = {"hash": _file_hash(path), "imports": parse_python_imports(path)}
    else:
        index = {}
        for path in py_files:
            rel = posix(path.relative_to(repo).as_posix())
            index[rel] = {"hash": _file_hash(path), "imports": parse_python_imports(path)}
            scanned += 1

    name_to_file = { _module_from_file(repo, repo / rel): rel for rel in index }

    for rel, meta in index.items():
        owner = _owner(registry, rel)
        for imported in meta.get("imports") or []:
            target_file = name_to_file.get(imported)
            if target_file is None:
                if imported.startswith(".") or imported.split(".")[0] in {"src"}:
                    incomplete.append(f"unresolved_import:{rel}:{imported}")
                continue
            target_owner = _owner(registry, target_file)
            if owner and target_owner and owner != target_owner:
                edges.append(
                    {
                        "from": owner,
                        "to": target_owner,
                        "type": "python_import",
                        "source": rel,
                        "confidence": "medium",
                    }
                )

    manifest_edges = _manifest_deps(repo)
    edges.extend(manifest_edges["edges"])
    incomplete.extend(manifest_edges["incomplete"])

    unique = []
    seen = set()
    for edge in edges:
        key = (edge["from"], edge["to"], edge["type"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(edge)

    payload = {
        "nodes": nodes,
        "edges": unique,
        "coverage": "INCOMPLETE" if incomplete else "COMPLETE",
        "incomplete_reasons": sorted(set(incomplete)),
        "file_index": {k: {"hash": v["hash"]} for k, v in index.items()},
        "scanned_files": scanned,
        "incremental": bool(changed and previous),
    }
    payload["digest"] = sha256_json({"nodes": sorted(nodes), "edges": unique, "coverage": payload["coverage"]})
    return payload


def _owner(registry: Registry, rel: str) -> str | None:
    from registry import write_owner

    return write_owner(registry, rel)


def _manifest_deps(repo: Path) -> dict[str, Any]:
    edges = []
    incomplete: list[str] = []
    pyproject = repo / "pyproject.toml"
    req = repo / "requirements.txt"
    pkg = repo / "package.json"
    if req.is_file():
        for line in req.read_text(encoding="utf-8").splitlines():
            name = line.strip().split("==")[0].split(">=")[0].strip()
            if name and not name.startswith("#"):
                edges.append({"from": "repo", "to": name, "type": "requirements", "source": "requirements.txt", "confidence": "high"})
    if pkg.is_file():
        try:
            import json

            data = json.loads(pkg.read_text(encoding="utf-8"))
            for name in dict(data.get("dependencies") or {}):
                edges.append({"from": "repo", "to": name, "type": "package_json", "source": "package.json", "confidence": "high"})
        except json.JSONDecodeError:
            incomplete.append("unresolved_manifest:package.json")
    if pyproject.is_file():
        text = pyproject.read_text(encoding="utf-8")
        if "dynamic" in text.lower() and "importlib" in text.lower():
            incomplete.append("dynamic_manifest:pyproject.toml")
    return {"edges": edges, "incomplete": incomplete}


def reverse_closure(graph: dict[str, Any], start: str) -> list[str]:
    incoming: dict[str, list[str]] = {}
    for edge in graph.get("edges") or []:
        incoming.setdefault(edge["to"], []).append(edge["from"])
    seen: set[str] = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        for src in incoming.get(node, []):
            if src not in seen:
                stack.append(src)
    seen.discard(start)
    return sorted(seen)
