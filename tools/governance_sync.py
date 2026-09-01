from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--project", required=True)
    ap.add_argument("--feature")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        raise SystemExit(f"repo not found: {repo}")

    project = None
    for path in (ROOT / "registry/projects").glob("*.yaml"):
        item = load_yaml(path)
        if item.get("project_id") == args.project:
            project = item
            break
    if not project:
        raise SystemExit(f"unknown project: {args.project}")

    manifest = load_yaml(ROOT / "skills/manifest.yaml")
    destination = repo / manifest["sync"]["destination"]
    lock_file = repo / manifest["sync"]["lock_file"]

    expected = {}
    for skill_name in manifest.get("universal", []):
        src = ROOT / "skills/universal" / skill_name / "SKILL.md"
        expected[f"skills/{skill_name}/SKILL.md"] = sha256(src)

    matching_wp = None
    if args.feature:
        for path in (ROOT / "features" / args.feature / "work-packages").glob("*.yaml"):
            wp = load_yaml(path)
            if wp.get("repository_id") in project.get("repositories", []):
                matching_wp = path
                expected[f"work-packages/{args.feature}.yaml"] = sha256(path)
                break

    lock = {"kit": manifest["kit"]["name"], "version": manifest["kit"]["version"], "project_id": args.project, "feature_id": args.feature, "files": expected}

    if args.check:
        if not lock_file.exists():
            print("OUT_OF_SYNC: governance.lock missing")
            raise SystemExit(2)
        current = json.loads(lock_file.read_text(encoding="utf-8"))
        if current != lock:
            print("OUT_OF_SYNC: governance.lock differs")
            raise SystemExit(2)
        for rel, digest in expected.items():
            target = destination / rel
            if not target.exists() or sha256(target) != digest:
                print(f"OUT_OF_SYNC: {rel}")
                raise SystemExit(2)
        print("GOVERNANCE SYNC OK")
        return

    for skill_name in manifest.get("universal", []):
        src = ROOT / "skills/universal" / skill_name
        dst = destination / "skills" / skill_name
        if dst.exists(): shutil.rmtree(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst)

    if matching_wp:
        dst = destination / "work-packages" / f"{args.feature}.yaml"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(matching_wp, dst)
        feature_doc = load_yaml(ROOT / "features" / args.feature / "feature.yaml")
        cdir = destination / "contracts"
        cdir.mkdir(parents=True, exist_ok=True)
        for cref in feature_doc.get("contracts", []):
            cid = cref["contract_id"]
            for rp in (ROOT / "registry/contracts").glob("*.yaml"):
                c = load_yaml(rp)
                if c.get("contract_id") == cid:
                    shutil.copy2(rp, cdir / f"{cid}.yaml")

    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_file.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"SYNCED {args.project} -> {destination}")
    print(f"LOCK {lock_file}")

if __name__ == "__main__":
    main()
