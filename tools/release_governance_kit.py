from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from governance_lib import ROOT, load_yaml


def current_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit("cannot resolve central commit")
    return result.stdout.strip()


def current_tag_for_commit(commit: str) -> str | None:
    result = subprocess.run(
        ["git", "tag", "--points-at", commit],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    tags = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    for preferred in tags:
        if preferred.startswith("governance-kit-v"):
            return preferred
    return tags[0] if tags else None


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_kit_files(manifest: dict) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for skill_name in manifest.get("universal", []):
        base = ROOT / "skills/universal" / skill_name
        for src in sorted(base.rglob("*")):
            if src.is_file():
                rel = f"skills/{skill_name}/{src.relative_to(base).as_posix()}"
                files[rel] = src
    for schema_name in [
        "artifact-ref.schema.json",
        "delivery-receipt.schema.json",
        "acceptance-manifest.schema.json",
        "acceptance-report.schema.json",
        "project-report.schema.json",
    ]:
        files[f"schemas/{schema_name}"] = ROOT / "schemas" / schema_name
    files["tools/validate_local_governance.py"] = ROOT / "templates/project/tools/validate_local_governance.py"
    for rel in [
        "github/workflows/smc-governance.yml",
        "github/workflows/smc-governance-dispatch.yml",
        "github/workflows/smc-governance-labels.yml",
        "github/ISSUE_TEMPLATE/governed-bug.yml",
        "github/ISSUE_TEMPLATE/governed-work.yml",
        "github/pull_request_template.md",
    ]:
        src = ROOT / "templates/project" / rel.replace("github/", ".github/")
        if src.exists():
            files[rel] = src
    return files


def main() -> None:
    ap = argparse.ArgumentParser(description="Build immutable governance kit release artifacts")
    ap.add_argument("--version", default="1.2.0")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    manifest_path = ROOT / "skills/manifest.yaml"
    manifest = load_yaml(manifest_path)
    commit = current_commit()
    tag = current_tag_for_commit(commit) or f"governance-kit-v{args.version}"
    files = collect_kit_files(manifest)
    manifest_doc = {
        "kit": {
            "name": manifest["kit"]["name"],
            "version": args.version,
            "tag": tag,
            "commit": commit,
        },
        "files": {rel: sha256_file(path) for rel, path in sorted(files.items())},
    }
    manifest_sha256 = hashlib.sha256(json.dumps(manifest_doc, sort_keys=True).encode()).hexdigest()
    manifest_doc["manifest_sha256"] = manifest_sha256

    out_dir = ROOT / "dist" / f"governance-kit-v{args.version}"
    if args.apply:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "manifest.json").write_text(json.dumps(manifest_doc, indent=2) + "\n", encoding="utf-8")
        sums = []
        for rel, path in sorted(files.items()):
            target = out_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
            sums.append(f"{manifest_doc['files'][rel]}  {rel}")
        (out_dir / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
        print(f"RELEASE {tag} commit={commit} manifest_sha256={manifest_sha256}")
        print(f"OUTPUT {out_dir}")
    else:
        print(json.dumps(manifest_doc, indent=2))


if __name__ == "__main__":
    main()
