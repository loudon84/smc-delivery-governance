#!/usr/bin/env python3
"""Read-only Spec Kit capability probe (never init / never write Consumer root)."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROVIDER = json.loads((HERE / "provider.json").read_text(encoding="utf-8"))


def _digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def probe(executable: str | None = None) -> dict:
    # @lat: [[safety-runtime-closure-v503]]
    exe = executable or shutil.which("specify")
    probed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not exe:
        return {
            "provider": "spec-kit",
            "provider_status": "UNAVAILABLE",
            "integration_status": "NATIVE_ONLY",
            "code": "SPEC_KIT_UNAVAILABLE",
            "probed_at": probed_at,
        }
    cmd = [exe, "version", "--features", "--json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "provider": "spec-kit",
            "provider_status": "UNAVAILABLE",
            "integration_status": "NATIVE_ONLY",
            "code": "SPEC_KIT_UNAVAILABLE",
            "detail": str(exc),
            "probed_at": probed_at,
        }
    stdout = proc.stdout or ""
    features = None
    version = None
    try:
        payload = json.loads(stdout) if stdout.strip().startswith("{") else None
        if isinstance(payload, dict):
            version = payload.get("version")
            features = payload.get("features")
    except json.JSONDecodeError:
        version = stdout.strip().splitlines()[0] if stdout.strip() else None
    status = "EXTERNAL_VERIFIED" if proc.returncode == 0 and version else "INCOMPATIBLE"
    return {
        "provider": "spec-kit",
        "executable": exe,
        "version": version,
        "feature_set": features,
        "probe_command": cmd,
        "probe_exit_code": proc.returncode,
        "stdout_digest": _digest(stdout),
        "probed_at": probed_at,
        "provider_status": "AVAILABLE" if proc.returncode == 0 else "INCOMPATIBLE",
        "integration_status": status if proc.returncode == 0 else "ADAPTER_READY",
        "code": None if proc.returncode == 0 else "SPEC_KIT_INCOMPATIBLE",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    result = probe(a.exe)
    # Never claim EXTERNAL_VERIFIED from mock; probe only records facts.
    if result.get("provider_status") == "UNAVAILABLE":
        result["integration_status"] = PROVIDER.get("integration_status", "ADAPTER_READY")
        # Honest offline default from provider.json when CLI absent.
        result["integration_status"] = "NATIVE_ONLY"
    print(json.dumps(result, indent=2) if a.json else result.get("code") or result.get("integration_status"))
    return 0 if result.get("provider_status") in {"AVAILABLE", "UNAVAILABLE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
