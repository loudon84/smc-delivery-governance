from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from governance_lib import ROOT
from governance_kit import build_kit, deterministic_tar_gz

def git_head() -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("cannot resolve central git HEAD")
    return r.stdout.strip()

def tag_points_at(tag: str, commit: str) -> bool:
    r = subprocess.run(["git", "rev-list", "-n", "1", tag], cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() == commit

def tag_is_annotated(tag: str) -> bool:
    r = subprocess.run(["git", "cat-file", "-t", tag], cwd=ROOT, capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() == "tag"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="1.2.1")
    ap.add_argument("--commit")
    ap.add_argument("--tag")
    ap.add_argument("--allow-untagged", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    commit = args.commit or git_head()
    tag = args.tag or f"governance-kit-v{args.version}"
    if not args.allow_untagged:
        if not tag_points_at(tag, commit):
            raise SystemExit(f"{tag} must exist and point at {commit}")
        if not tag_is_annotated(tag):
            raise SystemExit(f"{tag} must be an annotated tag")

    out_dir = ROOT / "dist" / tag
    if not args.apply:
        print(json.dumps({"version": args.version, "tag": tag, "commit": commit, "output": str(out_dir)}, indent=2))
        return

    evidence = build_kit(
        source_root=ROOT,
        version=args.version,
        commit=commit,
        tag=tag,
        output_dir=out_dir,
    )
    archive = ROOT / "dist" / f"{tag}.tar.gz"
    deterministic_tar_gz(out_dir, archive)
    evidence["archive"] = str(archive)
    import hashlib
    evidence["archive_sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
    print(json.dumps(evidence, indent=2))

if __name__ == "__main__":
    main()
