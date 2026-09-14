#!/usr/bin/env python3
"""Import Spec Kit UX proposals into working memory — never edits Canonical PRD."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ALLOWED = {"clarify", "checklist", "analyze"}
SCHEMA = "smc.ges.ux-proposal.v1"


def _sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _sha_payload(obj: dict) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def validate_proposal(
    proposal: dict,
    *,
    prd: Path,
    work_facts_digest: str,
) -> tuple[str, list[str]]:
    # @lat: [[safety-runtime-closure-v503]]
    reasons: list[str] = []
    if not isinstance(proposal, dict) or proposal.get("schema") != SCHEMA:
        return "SPEC_KIT_RESULT_INVALID", ["schema"]
    if proposal.get("provider") != "spec-kit":
        return "SPEC_KIT_RESULT_INVALID", ["provider"]
    if proposal.get("capability") not in ALLOWED:
        return "SPEC_KIT_RESULT_INVALID", ["capability"]
    if not proposal.get("provider_version"):
        return "SPEC_KIT_RESULT_INVALID", ["provider_version"]
    if not prd.is_file():
        return "SPEC_KIT_RESULT_STALE", ["prd_missing"]
    current_prd = _sha_file(prd)
    if proposal.get("source_prd_sha256") != current_prd:
        return "SPEC_KIT_RESULT_STALE", ["source_prd_sha256"]
    if proposal.get("work_facts_digest") != work_facts_digest:
        return "SPEC_KIT_RESULT_STALE", ["work_facts_digest"]
    body = {k: v for k, v in proposal.items() if k != "result_digest"}
    if proposal.get("result_digest") != _sha_payload(body):
        return "SPEC_KIT_RESULT_CONFLICT", ["result_digest"]
    return "OK", reasons


def import_proposal(
    proposal: dict,
    *,
    repo: Path,
    prd: Path,
    work_facts_digest: str,
) -> Path:
    code, reasons = validate_proposal(proposal, prd=prd, work_facts_digest=work_facts_digest)
    if code != "OK":
        raise ValueError(f"{code}: {','.join(reasons)}")
    work_item_id = str(proposal.get("work_item_id") or "unknown")
    out_dir = repo / ".smc" / "runs" / work_item_id / "ux"
    # Must stay under repo .smc/runs — never Consumer-root .specify/
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"ux-proposal-{proposal.get('capability')}.json"
    out.write_text(json.dumps(proposal, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("proposal", type=Path)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--prd", type=Path, required=True)
    ap.add_argument("--work-facts-digest", required=True)
    a = ap.parse_args()
    proposal = json.loads(a.proposal.read_text(encoding="utf-8"))
    try:
        out = import_proposal(
            proposal, repo=a.repo.resolve(), prd=a.prd.resolve(), work_facts_digest=a.work_facts_digest
        )
    except ValueError as exc:
        print(str(exc))
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
