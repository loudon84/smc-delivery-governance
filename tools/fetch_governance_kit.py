from __future__ import annotations
import argparse
from governance_kit import fetch_release_bundle, verify_kit

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="1.2.1")
    ap.add_argument("--token")
    args = ap.parse_args()
    path = fetch_release_bundle(version=args.version, token=args.token)
    evidence = verify_kit(path, expected_version=args.version, expected_tag=f"governance-kit-v{args.version}")
    print(f"KIT READY: {path}")
    print(f"manifest_sha256={evidence['manifest_sha256']}")
    print(f"sha256sums_sha256={evidence['sha256sums_sha256']}")

if __name__ == "__main__":
    main()
