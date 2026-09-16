from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


ACCEPTANCES = [
    "A01",
    "A02",
    "A03",
    "A04",
    "A05",
    "A06",
    "A07",
    "A08",
    "A09",
    "A10",
    "A11",
    "A12",
    "A13",
    "A14",
    "A15",
    "A16",
    "A17",
    "A18",
    "A19",
    "A20",
    "A21",
    "A22",
    "A23",
    "A24",
    "A25",
    "A26",
    "A27",
]


def write_evidence(root: Path, exit_code: int, *, acceptances: dict[str, str] | None = None) -> Path:
    ts = datetime.now(timezone.utc)
    payload = {
        "schema": "ges.acceptance-evidence.v1",
        "ts": ts.isoformat(),
        "command": "pytest -q tests/ges6",
        "exit_code": exit_code,
        "acceptances": acceptances
        or {
            **{item: ("PASS" if exit_code == 0 else "FAIL") for item in ACCEPTANCES if item != "A27"},
            "A27": "BLOCKED",
        },
    }
    out_dir = root / "audit" / "ges6" / "acceptance"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{ts.strftime('%Y%m%dT%H%M%SZ')}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return out


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    code = subprocess.call(
        [sys.executable, "-m", "pytest", "-q", str(root / "tests" / "ges6")],
        cwd=root,
    )
    write_evidence(root, code)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
