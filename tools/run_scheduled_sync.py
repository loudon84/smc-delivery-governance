from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from governance_lib import EXIT_EXPECTED_NON_READY, EXIT_OK, EXIT_SYSTEM_ERROR, ROOT


def run_tool(args: list[str]) -> int:
    result = subprocess.run([sys.executable, *args], cwd=ROOT)
    return result.returncode


def main() -> None:
    ap = argparse.ArgumentParser(description="Orchestrate governance sync with fail-fast semantics")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--feature", action="append", default=[])
    ap.add_argument("--repository-id", help="Limit sync to features touching this repository")
    ap.add_argument("--skip-registry", action="store_true")
    args = ap.parse_args()

    features = list(args.feature)
    if not features:
        features = sorted(p.name for p in (ROOT / "features").glob("FEAT-*") if p.is_dir())

    if args.repository_id:
        filtered = []
        for feat in features:
            fdir = ROOT / "features" / feat if not feat.startswith("features/") else ROOT / feat
            for wp_path in (fdir / "work-packages").glob("*.yaml"):
                import yaml

                wp = yaml.safe_load(wp_path.read_text(encoding="utf-8"))
                if wp.get("repository_id") == args.repository_id:
                    filtered.append(feat if feat.startswith("features/") else f"features/{feat}")
                    break
        features = filtered

    system_error = False
    expected_non_ready = False

    if not args.skip_registry:
        registry_args = ["tools/sync_project_registry.py"]
        if args.apply:
            registry_args.append("--apply")
        code = run_tool(registry_args)
        if code == EXIT_SYSTEM_ERROR:
            system_error = True

    for feat in features:
        feat_arg = feat if feat.startswith("features/") else f"features/{feat}"
        sync_args = ["tools/sync_repo_state.py", feat_arg]
        if args.apply:
            sync_args.append("--apply")
        sync_args.append("--discover-github")
        code = run_tool(sync_args)
        if code == EXIT_SYSTEM_ERROR:
            system_error = True
        elif code == EXIT_EXPECTED_NON_READY:
            expected_non_ready = True

    if system_error:
        print("SYNC ABORTED: system error during repository sync")
        raise SystemExit(EXIT_SYSTEM_ERROR)

    for feat in features:
        feat_arg = feat if feat.startswith("features/") else f"features/{feat}"
        reconcile_args = ["tools/reconcile_states.py", feat_arg]
        if args.apply:
            reconcile_args.append("--apply")
        code = run_tool(reconcile_args)
        if code == EXIT_SYSTEM_ERROR:
            system_error = True
        elif code == EXIT_EXPECTED_NON_READY:
            expected_non_ready = True

    if system_error:
        print("SYNC ABORTED: system error during reconciliation")
        raise SystemExit(EXIT_SYSTEM_ERROR)

    run_tool(["tools/reconcile_project_status.py"])
    run_tool(["tools/validate_registry.py"])
    for feat in features:
        feat_arg = feat if feat.startswith("features/") else f"features/{feat}"
        code = run_tool(["tools/validate_feature.py", feat_arg])
        if code == EXIT_SYSTEM_ERROR:
            system_error = True

    if system_error:
        raise SystemExit(EXIT_SYSTEM_ERROR)

    if expected_non_ready:
        print("SYNC COMPLETE: expected non-ready repositories recorded")
        raise SystemExit(EXIT_EXPECTED_NON_READY)

    print("SYNC COMPLETE")
    raise SystemExit(EXIT_OK)


if __name__ == "__main__":
    main()
