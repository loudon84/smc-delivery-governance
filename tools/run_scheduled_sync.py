from __future__ import annotations

import argparse
import subprocess
import sys

from governance_lib import EXIT_EXPECTED_NON_READY, EXIT_OK, EXIT_SYSTEM_ERROR, ROOT

def run_tool(args: list[str]) -> int:
    return subprocess.run([sys.executable,*args],cwd=ROOT).returncode

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--apply",action="store_true")
    ap.add_argument("--feature",action="append",default=[])
    ap.add_argument("--repository-id")
    ap.add_argument("--skip-registry",action="store_true")
    args=ap.parse_args()

    features=list(args.feature) or sorted(p.name for p in (ROOT/"features").glob("FEAT-*") if p.is_dir())
    if args.repository_id:
        import yaml
        filtered=[]
        for feat in features:
            fdir=ROOT/(feat if feat.startswith("features/") else f"features/{feat}")
            if any(yaml.safe_load(p.read_text(encoding="utf-8")).get("repository_id")==args.repository_id for p in (fdir/"work-packages").glob("*.yaml")):
                filtered.append(feat)
        features=filtered

    system_error=False;expected_non_ready=False
    def classify(code):
        nonlocal system_error,expected_non_ready
        if code==EXIT_SYSTEM_ERROR:system_error=True
        elif code==EXIT_EXPECTED_NON_READY:expected_non_ready=True
        elif code!=EXIT_OK:system_error=True

    if not args.skip_registry:
        cmd=["tools/sync_project_registry.py"]+(["--apply"] if args.apply else [])
        classify(run_tool(cmd))
    if system_error:raise SystemExit(EXIT_SYSTEM_ERROR)

    for feat in features:
        arg=feat if feat.startswith("features/") else f"features/{feat}"
        cmd=["tools/sync_repo_state.py",arg,"--discover-github"]+(["--apply"] if args.apply else [])
        classify(run_tool(cmd))
        if system_error:break
    if system_error:raise SystemExit(EXIT_SYSTEM_ERROR)

    for feat in features:
        arg=feat if feat.startswith("features/") else f"features/{feat}"
        cmd=["tools/reconcile_states.py",arg]+(["--apply"] if args.apply else [])
        classify(run_tool(cmd))
        if system_error:break
    if system_error:raise SystemExit(EXIT_SYSTEM_ERROR)

    classify(run_tool(["tools/reconcile_project_status.py"]))
    classify(run_tool(["tools/validate_registry.py"]))
    for feat in features:
        arg=feat if feat.startswith("features/") else f"features/{feat}"
        classify(run_tool(["tools/validate_feature.py",arg]))
    classify(run_tool(["tools/verify_state_invariants.py"]))
    if system_error:raise SystemExit(EXIT_SYSTEM_ERROR)
    if expected_non_ready:
        print("SYNC COMPLETE: expected non-ready state recorded")
        raise SystemExit(EXIT_EXPECTED_NON_READY)
    print("SYNC COMPLETE")
    raise SystemExit(EXIT_OK)

if __name__=="__main__":main()
