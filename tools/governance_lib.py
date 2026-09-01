from __future__ import annotations
from pathlib import Path
from typing import Any
import json
import os
import urllib.error
import urllib.parse
import urllib.request
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
FEATURE_ORDER = {
    "PROPOSED": 0, "ARCHITECTURE": 1, "PLANNED": 2, "IMPLEMENTING": 3,
    "INTEGRATING": 4, "VERIFYING": 5, "DONE": 6,
    "BLOCKED": -1, "CANCELLED": -2,
}


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n")


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


def project_catalog() -> dict[str, dict]:
    return index_registry("projects", "project_id")


def repository_catalog() -> dict[str, dict]:
    return index_registry("repositories", "repository_id")


def team_catalog() -> dict[str, dict]:
    return index_registry("teams", "team_id")


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


def find_work_package(work_package_id: str) -> tuple[Path, dict] | tuple[None, None]:
    for fdir in (ROOT / "features").glob("FEAT-*"):
        if not fdir.is_dir():
            continue
        for path in all_yaml_files(fdir / "work-packages"):
            doc = load_yaml(path)
            if doc.get("work_package_id") == work_package_id:
                return path, doc
    return None, None


def contract_state(contract_id: str) -> str | None:
    c = contract_catalog().get(contract_id)
    if not c:
        return None
    return (c.get("current_release") or {}).get("state")


def state_at_least(current: str | None, required: str, order: dict[str, int]) -> bool:
    if current is None or current not in order or required not in order:
        return False
    if current in {"BLOCKED", "SUPERSEDED", "CANCELLED"}:
        return current == required
    return order[current] >= order[required]


def github_api(path: str, *, token: str | None = None, accept: str = "application/vnd.github+json") -> Any:
    url = path if path.startswith("http") else f"https://api.github.com{path}"
    req = urllib.request.Request(url)
    req.add_header("Accept", accept)
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    token = token or os.getenv("SMC_GOVERNANCE_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {e.code}: {url}: {detail[:500]}") from e


def github_file(repo_full_name: str, path: str, ref: str, token: str | None = None) -> str | None:
    import base64
    qpath = urllib.parse.quote(path.strip("/"), safe="/")
    qref = urllib.parse.quote(ref, safe="")
    try:
        data = github_api(f"/repos/{repo_full_name}/contents/{qpath}?ref={qref}", token=token)
    except RuntimeError as e:
        if "GitHub API 404" in str(e):
            return None
        raise
    if not isinstance(data, dict) or data.get("type") != "file":
        return None
    content = data.get("content") or ""
    if data.get("encoding") == "base64":
        return base64.b64decode(content).decode("utf-8")
    return content
