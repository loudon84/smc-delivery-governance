from __future__ import annotations
import argparse, hashlib, json, subprocess, time
from datetime import datetime, timezone
from pathlib import Path
import yaml


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def git_head(repo: Path) -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("repository_commit unavailable")
    return r.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--output", required=True)
    ap.add_argument("--allow-manual", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    doc = yaml.safe_load(Path(args.manifest).read_text(encoding="utf-8"))
    results = []
    overall = "PASS"

    for v in doc["verifications"]:
        if v["type"] == "manual" and not args.allow_manual:
            results.append({"verification_id":v["id"],"status":"SKIPPED","exit_code":None,"duration_ms":0,"stdout_sha256":None,"stderr_sha256":None})
            if v.get("blocking", True): overall = "PARTIAL"
            continue
        cwd = repo / v.get("cwd", ".")
        started = time.monotonic()
        try:
            r = subprocess.run(v["command"], cwd=cwd, shell=True, capture_output=True, text=True, timeout=v.get("timeout_seconds", 600))
            dur = int((time.monotonic()-started)*1000)
            status = "PASS" if r.returncode == 0 else "FAIL"
            if status == "FAIL" and v.get("blocking", True): overall = "FAIL"
            results.append({"verification_id":v["id"],"status":status,"exit_code":r.returncode,"duration_ms":dur,"stdout_sha256":sha(r.stdout),"stderr_sha256":sha(r.stderr)})
        except subprocess.TimeoutExpired as e:
            dur = int((time.monotonic()-started)*1000)
            if v.get("blocking", True): overall = "FAIL"
            results.append({"verification_id":v["id"],"status":"FAIL","exit_code":124,"duration_ms":dur,"stdout_sha256":sha(e.stdout or ""),"stderr_sha256":sha(e.stderr or "")})

    report = {
      "report_version":"1",
      "feature_id":doc["feature_id"],
      "work_package_id":doc["work_package_id"],
      "source_revision":doc["prd"]["source_revision"],
      "repository_commit":git_head(repo),
      "status":overall,
      "results":results,
      "generated_at":datetime.now(timezone.utc).isoformat(),
    }
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(f"ACCEPTANCE {overall}: {out}")
    raise SystemExit(0 if overall == "PASS" else 2)

if __name__ == "__main__": main()
