"""Load and validate the Consumer Context Registry."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from coe_common import CONTEXT_DIR, PARSER_VERSION, REGISTRY_SCHEMA, find_repo_root, posix, sha256_json
from path_identity import canonical_rel, identity_key, resolve_inside
from yaml_lite import load as load_yaml

RECORD_STATUSES = {"PROPOSED", "REVIEWED"}


@dataclass
class Record:
    kind: str
    rec_id: str
    owner: str
    status: str
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    contracts: list[str] = field(default_factory=list)
    allowed_dependencies: list[str] = field(default_factory=list)
    host_module: str = ""
    uses: list[str] = field(default_factory=list)
    source: str = ""


@dataclass
class Registry:
    registry_id: str
    revision: str
    repo: Path
    records: list[Record]
    errors: list[dict[str, str]]
    payload: dict[str, Any]

    @property
    def digest(self) -> str:
        return sha256_json(self.payload)

    def modules(self) -> list[Record]:
        return [r for r in self.records if r.kind == "module"]

    def components(self) -> list[Record]:
        return [r for r in self.records if r.kind == "component"]


def context_root(repo: Path) -> Path:
    return repo / CONTEXT_DIR


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value if x is not None and str(x).strip()]
    return [str(value)]


def _load_record(path: Path, kind: str) -> Record:
    data = load_yaml(path) or {}
    rec_id = str(data.get("id") or path.stem)
    return Record(
        kind=kind,
        rec_id=rec_id,
        owner=str(data.get("owner") or "").strip(),
        status=str(data.get("status") or "PROPOSED").upper(),
        include=_as_list(data.get("include")),
        exclude=_as_list(data.get("exclude")),
        exports=_as_list(data.get("exports")),
        contracts=_as_list(data.get("contracts")),
        allowed_dependencies=_as_list(data.get("allowed_dependencies") or data.get("dependencies")),
        host_module=str(data.get("module") or data.get("host_module") or "").strip(),
        uses=_as_list(data.get("uses") or data.get("modules")),
        source=posix(str(path)),
    )


def _match(path: str, pattern: str) -> bool:
    from fnmatch import fnmatch

    norm = posix(path)
    pat = posix(pattern)
    if pat.endswith("/**"):
        prefix = pat[:-3].rstrip("/")
        return norm == prefix or norm.startswith(prefix + "/")
    return fnmatch(norm, pat) or norm == pat or norm.startswith(pat.rstrip("/") + "/")


def _covers(record: Record, rel: str) -> bool:
    if any(_match(rel, ex) for ex in record.exclude):
        return False
    if not record.include:
        return False
    return any(_match(rel, inc) for inc in record.include)


def validate_records(repo: Path, records: list[Record]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    module_ids = {r.rec_id for r in records if r.kind == "module"}
    owners: dict[str, list[str]] = {}
    identities: dict[str, str] = {}

    for rec in records:
        if rec.status not in RECORD_STATUSES:
            errors.append({"code": "CONTEXT_REGISTRY_INVALID", "detail": f"status:{rec.rec_id}"})
        if rec.kind in {"module", "component"} and not rec.owner:
            errors.append({"code": "CONTEXT_REGISTRY_INVALID", "detail": f"missing_owner:{rec.rec_id}"})
        if rec.kind == "component" and rec.host_module and rec.host_module not in module_ids:
            errors.append({"code": "CONTEXT_REGISTRY_INVALID", "detail": f"host_module:{rec.rec_id}"})
        for rel in rec.include + rec.exclude + rec.exports + rec.contracts:
            try:
                canonical = canonical_rel(repo, rel.replace("/**", ""))
                key = identity_key(repo, rel.replace("/**", ""))
                identities[canonical] = key
            except ValueError:
                if any(part == ".." for part in Path(rel).parts) or Path(rel).is_absolute():
                    errors.append({"code": "CONTEXT_PATH_OUTSIDE_REPO", "detail": rel})
        for contract in rec.contracts:
            target = repo / contract
            if not target.exists():
                errors.append({"code": "CONTEXT_REGISTRY_INVALID", "detail": f"dangling_contract:{contract}"})

    write_modules = [r for r in records if r.kind == "module"]
    sample_files: set[str] = set()
    for rec in write_modules:
        for inc in rec.include:
            sample_files.add(posix(inc.replace("/**", "").rstrip("/")))
    for rec in write_modules:
        for ex in rec.exports:
            sample_files.add(posix(ex))

    for sample in sorted(sample_files):
        hits = [r.rec_id for r in write_modules if _covers(r, sample)]
        if len(hits) > 1:
            owners.setdefault(sample, hits)

    for path, mods in owners.items():
        errors.append(
            {
                "code": "CONTEXT_REGISTRY_INVALID",
                "detail": f"duplicate_owner:{path}:{','.join(sorted(set(mods)))}",
            }
        )
    return errors


def load_registry(repo: Path | None = None, *, path: Path | None = None) -> Registry:
    root = path or (find_repo_root(repo) if repo else None)
    if root is None:
        raise ValueError("CONTEXT_REPO_ROOT_NOT_FOUND")
    repo = Path(root).resolve()
    base = context_root(repo)
    records: list[Record] = []
    if (base / "architecture.yaml").is_file():
        records.append(_load_record(base / "architecture.yaml", "architecture"))
    if (base / "project.yaml").is_file():
        records.append(_load_record(base / "project.yaml", "project"))
    for folder, kind in (("modules", "module"), ("components", "component"), ("applications", "application")):
        d = base / folder
        if d.is_dir():
            for p in sorted(d.glob("*.yaml")):
                records.append(_load_record(p, kind))
    errors = validate_records(repo, records)
    payload = {
        "schema": REGISTRY_SCHEMA,
        "registry_id": repo.name,
        "revision": PARSER_VERSION,
        "repo_identity": str(repo),
        "parser_version": PARSER_VERSION,
        "records": [
            {
                "kind": r.kind,
                "id": r.rec_id,
                "owner": r.owner,
                "status": r.status,
                "include": r.include,
                "exclude": r.exclude,
                "exports": r.exports,
                "contracts": r.contracts,
                "allowed_dependencies": r.allowed_dependencies,
                "host_module": r.host_module,
                "uses": r.uses,
            }
            for r in records
        ],
        "source_refs": [r.source for r in records],
        "projects": [r.rec_id for r in records if r.kind == "project"],
        "modules": [r.rec_id for r in records if r.kind == "module"],
        "components": [r.rec_id for r in records if r.kind == "component"],
        "applications": [r.rec_id for r in records if r.kind == "application"],
        "constraints": [c for r in records for c in r.contracts],
        "dependencies": [
            {"from": r.rec_id, "to": dep} for r in records for dep in r.allowed_dependencies
        ],
    }
    return Registry(
        registry_id=repo.name,
        revision=PARSER_VERSION,
        repo=repo,
        records=records,
        errors=errors,
        payload=payload,
    )


def can_enforce(registry: Registry) -> bool:
    if registry.errors:
        return False
    if not registry.modules():
        return False
    return all(r.status == "REVIEWED" and r.owner for r in registry.modules() + registry.components())


def write_owner(registry: Registry, rel: str) -> str | None:
    hits = [r.rec_id for r in registry.modules() if _covers(r, posix(rel))]
    if len(hits) == 1:
        return hits[0]
    return None
