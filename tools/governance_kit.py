from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tarfile
import tempfile
import urllib.parse

from governance_lib import ROOT, github_api, github_request, load_yaml, sha256_bytes, sha256_file

KIT_REPOSITORY = "loudon84/smc-delivery-governance"

KIT_SCHEMAS = [
    "artifact-ref.schema.json",
    "delivery-receipt.schema.json",
    "acceptance-manifest.schema.json",
    "acceptance-report.schema.json",
    "acceptance-attestation.schema.json",
    "project-report.schema.json",
]

KIT_PROJECT_FILES = [
    "github/workflows/smc-governance.yml",
    "github/workflows/smc-governance-dispatch.yml",
    "github/workflows/smc-governance-acceptance.yml",
    "github/workflows/smc-governance-labels.yml",
    "github/ISSUE_TEMPLATE/governed-bug.yml",
    "github/ISSUE_TEMPLATE/governed-work.yml",
    "github/pull_request_template.md",
]

def _manifest_bytes(doc: dict) -> bytes:
    return (json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")

def collect_source_files(source_root: Path, skills_manifest: dict) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for skill_name in skills_manifest.get("universal", []):
        base = source_root / "skills" / "universal" / skill_name
        if not base.exists():
            raise RuntimeError(f"missing universal skill: {skill_name}")
        for src in sorted(base.rglob("*")):
            if src.is_file():
                files[f"skills/{skill_name}/{src.relative_to(base).as_posix()}"] = src
    for schema_name in KIT_SCHEMAS:
        src = source_root / "schemas" / schema_name
        if not src.exists():
            raise RuntimeError(f"missing kit schema: {schema_name}")
        files[f"schemas/{schema_name}"] = src
    src = source_root / "templates/project/tools/validate_local_governance.py"
    files["tools/validate_local_governance.py"] = src
    for rel in KIT_PROJECT_FILES:
        src = source_root / "templates/project" / rel.replace("github/", ".github/")
        if src.exists():
            files[rel] = src
    return files

def build_kit(
    *,
    source_root: Path,
    version: str,
    commit: str,
    tag: str,
    output_dir: Path,
) -> dict:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    skills_manifest = load_yaml(source_root / "skills/manifest.yaml")
    files = collect_source_files(source_root, skills_manifest)

    file_hashes: dict[str, str] = {}
    for rel, src in sorted(files.items()):
        dst = output_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        dst.write_bytes(data)
        file_hashes[rel] = sha256_bytes(data)

    manifest = {
        "kit": {
            "name": skills_manifest["kit"]["name"],
            "version": version,
            "tag": tag,
            "commit": commit,
        },
        "bundle_format_version": "1",
        "files": file_hashes,
    }
    manifest_data = _manifest_bytes(manifest)
    (output_dir / "manifest.json").write_bytes(manifest_data)

    checksum_targets = {"manifest.json": sha256_bytes(manifest_data), **file_hashes}
    sums = "".join(f"{digest}  {rel}\n" for rel, digest in sorted(checksum_targets.items()))
    (output_dir / "SHA256SUMS").write_bytes(sums.encode("utf-8"))

    verify_kit(output_dir, expected_version=version, expected_tag=tag, expected_commit=commit)
    return {
        "version": version,
        "tag": tag,
        "commit": commit,
        "manifest_sha256": sha256_bytes(manifest_data),
        "sha256sums_sha256": sha256_file(output_dir / "SHA256SUMS"),
        "file_count": len(checksum_targets),
    }

def parse_sums(path: Path) -> dict[str, str]:
    raw = path.read_bytes()
    if b"\r" in raw:
        raise RuntimeError("SHA256SUMS contains CR bytes")
    out = {}
    for line in raw.decode("utf-8").splitlines():
        if not line:
            continue
        try:
            digest, rel = line.split("  ", 1)
        except ValueError as e:
            raise RuntimeError(f"invalid SHA256SUMS line: {line}") from e
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise RuntimeError(f"invalid SHA256: {digest}")
        rel = rel.replace("\\", "/")
        if rel.startswith("/") or ".." in Path(rel).parts:
            raise RuntimeError(f"unsafe checksum path: {rel}")
        out[rel] = digest
    return out

# @lat: [[ADR-008-canonical-governance-kit#ADR-008 — Canonical Governance Kit Release]]
def verify_kit(
    kit_dir: Path,
    *,
    expected_version: str | None = None,
    expected_tag: str | None = None,
    expected_commit: str | None = None,
) -> dict:
    manifest_path = kit_dir / "manifest.json"
    sums_path = kit_dir / "SHA256SUMS"
    if not manifest_path.exists() or not sums_path.exists():
        raise RuntimeError("canonical kit requires manifest.json and SHA256SUMS")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    kit = manifest.get("kit") or {}
    if expected_version and kit.get("version") != expected_version:
        raise RuntimeError(f"kit version mismatch: {kit.get('version')} != {expected_version}")
    if expected_tag and kit.get("tag") != expected_tag:
        raise RuntimeError("kit tag mismatch")
    if expected_commit and kit.get("commit") != expected_commit:
        raise RuntimeError("kit commit mismatch")

    listed = parse_sums(sums_path)
    actual_files = {
        p.relative_to(kit_dir).as_posix()
        for p in kit_dir.rglob("*")
        if p.is_file() and p.name != "SHA256SUMS"
    }
    if set(listed) != actual_files:
        raise RuntimeError(
            f"kit checksum closure mismatch missing={sorted(actual_files-set(listed))} "
            f"extra={sorted(set(listed)-actual_files)}"
        )
    for rel, digest in listed.items():
        if sha256_file(kit_dir / rel) != digest:
            raise RuntimeError(f"kit checksum mismatch: {rel}")

    manifest_files = manifest.get("files") or {}
    for rel, digest in manifest_files.items():
        if rel not in listed or listed[rel] != digest:
            raise RuntimeError(f"manifest/checksum disagreement: {rel}")

    return {
        "kit": kit,
        "manifest_sha256": sha256_file(manifest_path),
        "sha256sums_sha256": sha256_file(sums_path),
        "file_count": len(listed),
    }

def deterministic_tar_gz(source_dir: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tf:
                for path in sorted(source_dir.rglob("*")):
                    rel = path.relative_to(source_dir.parent).as_posix()
                    info = tf.gettarinfo(str(path), arcname=rel)
                    info.mtime = 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    if path.is_file():
                        with path.open("rb") as fh:
                            tf.addfile(info, fh)
                    else:
                        tf.addfile(info)

def safe_extract_tar_gz(blob: bytes, target: Path) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    with gzip.GzipFile(fileobj=io.BytesIO(blob), mode="rb") as gz:
        with tarfile.open(fileobj=gz, mode="r:") as tf:
            members = tf.getmembers()
            for member in members:
                parts = Path(member.name).parts
                if member.name.startswith("/") or ".." in parts:
                    raise RuntimeError(f"unsafe kit archive entry: {member.name}")
            tf.extractall(target)
    dirs = [p for p in target.iterdir() if p.is_dir()]
    if len(dirs) != 1:
        raise RuntimeError("kit archive must contain one top-level directory")
    return dirs[0]



def resolve_remote_tag_commit(repository: str, tag: str, token: str | None = None) -> str:
    ref = github_api(
        f"/repos/{repository}/git/ref/tags/{urllib.parse.quote(tag, safe='')}",
        token=token,
    )
    obj = ref.get("object") or {}
    if obj.get("type") == "commit":
        # Lightweight tags are not accepted for governance releases.
        raise RuntimeError(f"governance kit tag must be annotated: {tag}")
    if obj.get("type") != "tag":
        raise RuntimeError(f"unsupported tag object type for {tag}: {obj.get('type')}")
    tag_obj = github_api(f"/repos/{repository}/git/tags/{obj['sha']}", token=token)
    peeled = tag_obj.get("object") or {}
    if peeled.get("type") != "commit" or not peeled.get("sha"):
        raise RuntimeError(f"annotated tag does not peel to commit: {tag}")
    return peeled["sha"]

def fetch_release_bundle(
    *,
    version: str,
    cache_root: Path | None = None,
    repository: str = KIT_REPOSITORY,
    token: str | None = None,
) -> Path:
    tag = f"governance-kit-v{version}"
    cache_root = cache_root or ROOT / ".cache" / "governance-kits"
    target = cache_root / tag
    if target.exists():
        try:
            verify_kit(target, expected_version=version, expected_tag=tag)
            manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
            peeled = resolve_remote_tag_commit(repository, tag, token=token)
            if manifest.get("kit", {}).get("commit") != peeled:
                raise RuntimeError("cached kit/tag commit mismatch")
            return target
        except Exception:
            shutil.rmtree(target)

    release = github_api(
        f"/repos/{repository}/releases/tags/{urllib.parse.quote(tag, safe='')}",
        token=token,
    )
    asset_name = f"{tag}.tar.gz"
    assets = [a for a in release.get("assets", []) if a.get("name") == asset_name]
    if len(assets) != 1:
        raise RuntimeError(f"release asset not found: {asset_name}")
    blob = github_request(
        f"/repos/{repository}/releases/assets/{assets[0]['id']}",
        token=token,
        accept="application/octet-stream",
        raw=True,
    )
    with tempfile.TemporaryDirectory() as td:
        extracted = safe_extract_tar_gz(blob, Path(td))
        evidence = verify_kit(extracted, expected_version=version, expected_tag=tag)
        peeled = resolve_remote_tag_commit(repository, tag, token=token)
        manifest = json.loads((extracted / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("kit", {}).get("commit") != peeled:
            raise RuntimeError(
                f"kit manifest/tag commit mismatch manifest={manifest.get('kit', {}).get('commit')} tag={peeled}"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(extracted, target)
    return target
