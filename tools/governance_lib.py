from __future__ import annotations
from pathlib import Path
from typing import Any
import json
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

CONTRACT_ORDER = {
    "DRAFT": 0, "CANDIDATE": 1, "APPROVED": 2, "RELEASED": 3,
    "CONSUMED": 4, "CONFORMANCE_PASS": 5, "DEPRECATED": 6, "RETIRED": 7,
}
WP_ORDER = {
    "BACKLOG": 0, "READY": 1, "IN_PRD": 2, "PLANNED": 3,
    "IMPLEMENTING": 4, "REVIEW": 5, "VERIFIED": 6, "DONE": 7,
    "BLOCKED": -1, "SUPERSEDED": -2,
}

def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def validate_jsonschema(data: Any, schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    result = []
    for err in errors:
        loc = ".".join(str(x) for x in err.absolute_path) or "$"
        result.append(f"{loc}: {err.message}")
    return result

def all_yaml_files(path: Path):
    return sorted(list(path.glob("*.yaml")) + list(path.glob("*.yml")))

def index_registry(subdir: str, id_field: str) -> dict[str, dict]:
    base = ROOT / "registry" / subdir
    out = {}
    if not base.exists():
        return out
    for path in all_yaml_files(base):
        item = load_yaml(path)
        if item and id_field in item:
            item["_path"] = str(path.relative_to(ROOT))
            out[item[id_field]] = item
    return out

def contract_catalog() -> dict[str, dict]:
    return index_registry("contracts", "contract_id")

def feature_dir(feature: str | Path) -> Path:
    path = Path(feature)
    if path.exists():
        return path.resolve()
    candidate = ROOT / "features" / str(feature)
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"feature not found: {feature}")

def load_feature(feature: str | Path) -> tuple[Path, dict]:
    d = feature_dir(feature)
    return d, load_yaml(d / "feature.yaml")

def load_work_packages(feature_dir_path: Path) -> dict[str, dict]:
    out = {}
    base = feature_dir_path / "work-packages"
    for path in all_yaml_files(base):
        item = load_yaml(path)
        item["_path"] = str(path.relative_to(ROOT))
        out[item["work_package_id"]] = item
    return out

def contract_state(contract_id: str) -> str | None:
    c = contract_catalog().get(contract_id)
    if not c:
        return None
    return (c.get("current_release") or {}).get("state")

def state_at_least(current: str | None, required: str, order: dict[str, int]) -> bool:
    if current is None or current not in order or required not in order:
        return False
    return order[current] >= order[required]
