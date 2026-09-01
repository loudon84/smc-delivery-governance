from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

PATCH_ROOT = Path(__file__).resolve().parent
MANIFEST = PATCH_ROOT / "PATCH-MANIFEST.json"

def git_head(repo: Path) -> str | None:
    r=subprocess.run(["git","rev-parse","HEAD"],cwd=repo,capture_output=True,text=True)
    return r.stdout.strip() if r.returncode==0 else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True)
    ap.add_argument("--force",action="store_true")
    ap.add_argument("--dry-run",action="store_true")
    args=ap.parse_args()

    repo=Path(args.repo).resolve()
    if not (repo/".git").exists():
        raise SystemExit("target is not a Git repository")
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    base=manifest["base_commit"]
    head=git_head(repo)
    if head!=base and not args.force:
        raise SystemExit(
            f"target HEAD {head} != patch base {base}. "
            "Rebase/review the patch or use --force only after manual conflict review."
        )

    for item in manifest["files"]:
        rel=item["path"]
        src=PATCH_ROOT/rel
        dst=repo/rel
        print(f"{item['action'].upper():7} {rel}")
        if args.dry_run:
            continue
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)

    print("PATCH APPLIED" if not args.dry_run else "DRY RUN COMPLETE")
    print("Next: follow PATCH-README.md migration order before committing.")

if __name__=="__main__":
    main()
