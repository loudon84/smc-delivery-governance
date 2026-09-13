#!/usr/bin/env python3
"""Bound Work Facts — content-bound routing receipt (not a second SOT)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "smc.ges.work-facts.v1"
ALLOWED_KINDS = frozenset(
    {"ROADMAP", "FEATURE", "PRD", "PLAN", "ORCHESTRATOR_REQUEST", "DERIVED"}
)
FORBIDDEN_ALONE = frozenset({"WORKER_ASSERTION", "MODEL_GUESS", "PROMPT_TEXT_ONLY"})
AUTHORITY_FACTS = (
    "governed",
    "retained_production_change",
    "production_write_requested",
    "durable_product_artifact_requested",
)
ALL_FACTS = (
    "existing_owner",
    "existing_capability",
    "bounded_writes",
    "deterministic_verification",
    "new_owner",
    "public_contract",
    "security_boundary",
    "schema_migration",
    "protocol_change",
    "external_dependency",
    "lifecycle_change",
    "cross_domain_ownership",
    "live_acceptance",
    "research_intent",
    *AUTHORITY_FACTS,
)
RISK_OR_PRODUCTION = frozenset(
    {
        "new_owner",
        "public_contract",
        "security_boundary",
        "schema_migration",
        "protocol_change",
        "external_dependency",
        "lifecycle_change",
        "cross_domain_ownership",
        "live_acceptance",
        "retained_production_change",
        "production_write_requested",
        "durable_product_artifact_requested",
        "governed",
    }
)


def _sha_payload(value: dict[str, Any]) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def facts_path(repo: Path, work_item_id: str) -> Path:
    return repo / ".smc" / "runs" / work_item_id / "routing" / "work-facts.json"


def compute_facts_digest(work_item_id: str, facts: dict[str, Any], provenance: dict[str, Any]) -> str:
    body = {"schema": SCHEMA, "work_item_id": work_item_id, "facts": facts, "provenance": provenance}
    return _sha_payload(body)


def build_envelope(
    work_item_id: str,
    facts: dict[str, Any],
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    # @lat: [[governance-architecture-closure]]
    normalized = {k: facts.get(k) for k in ALL_FACTS if k in facts}
    prov = provenance or {}
    digest = compute_facts_digest(work_item_id, normalized, prov)
    return {
        "schema": SCHEMA,
        "work_item_id": work_item_id,
        "facts": normalized,
        "provenance": prov,
        "facts_digest": digest,
    }


def from_work_authority(authority: dict[str, Any]) -> dict[str, Any]:
    """Read-only compat: work-authority.v1 → work-facts.v1 (not production-bound by itself)."""
    sources = authority.get("sources") or []
    provenance: dict[str, Any] = {}
    for src in sources:
        if not isinstance(src, dict):
            continue
        kind = str(src.get("type") or src.get("source_kind") or "DERIVED").upper()
        for key in AUTHORITY_FACTS:
            if key not in provenance:
                provenance[key] = {
                    "source_kind": kind,
                    "source_ref": src.get("path") or src.get("source_ref") or "",
                    "source_sha256": src.get("sha256") or src.get("source_sha256") or "",
                    "authority": src.get("authority") or "COMPAT",
                }
    facts = dict(authority.get("facts") or {})
    return build_envelope(str(authority.get("work_item_id") or "unknown"), facts, provenance)


def verify_envelope(data: dict[str, Any], repo: Path | None = None) -> tuple[str, list[str]]:
    """Return (VERIFIED|UNBOUND|STALE|INVALID|CONFLICT, reasons) with WORK_FACTS_* codes."""
    reasons: list[str] = []
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        return "INVALID", ["WORK_FACTS_INVALID"]
    facts = data.get("facts")
    provenance = data.get("provenance")
    if not isinstance(facts, dict):
        return "INVALID", ["WORK_FACTS_INVALID"]
    if not isinstance(provenance, dict) or not provenance:
        return "UNBOUND", ["WORK_FACTS_UNBOUND"]
    for key, prov in provenance.items():
        if not isinstance(prov, dict):
            return "INVALID", ["WORK_FACTS_INVALID"]
        kind = str(prov.get("source_kind") or "").upper()
        if kind in FORBIDDEN_ALONE and key == "governed" and facts.get("governed") is False:
            # forbidden kinds alone cannot support governed=false
            if not any(
                isinstance(p, dict) and str(p.get("source_kind", "")).upper() in ALLOWED_KINDS
                for p in provenance.values()
            ):
                return "INVALID", ["WORK_FACTS_AUTHORITY_MISSING"]
        if kind and kind not in ALLOWED_KINDS and kind not in FORBIDDEN_ALONE:
            reasons.append(f"WORK_FACTS_INVALID:{kind}")
    if reasons:
        return "INVALID", reasons
    expected = compute_facts_digest(
        str(data.get("work_item_id") or ""),
        {k: facts.get(k) for k in ALL_FACTS if k in facts},
        provenance,
    )
    if data.get("facts_digest") != expected:
        return "STALE", ["WORK_FACTS_STALE"]
    if repo is not None:
        for prov in provenance.values():
            if not isinstance(prov, dict):
                continue
            rel = prov.get("source_ref") or ""
            if not rel:
                continue
            path = repo / str(rel)
            if not path.is_file():
                return "STALE", ["WORK_FACTS_STALE"]
            dig = prov.get("source_sha256")
            if dig and dig != _sha_file(path):
                return "STALE", ["WORK_FACTS_STALE"]
    # governed=false requires authoritative orchestrator + no governed artifact signal
    if facts.get("governed") is False:
        kinds = {
            str(p.get("source_kind", "")).upper()
            for p in provenance.values()
            if isinstance(p, dict)
        }
        if kinds & {"PLAN", "PRD", "ROADMAP", "FEATURE"}:
            return "CONFLICT", ["WORK_FACTS_CONFLICT"]
        if not (kinds & ALLOWED_KINDS):
            return "INVALID", ["WORK_FACTS_AUTHORITY_MISSING"]
    return "VERIFIED", []


def conservative_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Risk/production fields: true wins; governed true if any canonical artifact says so."""
    merged = dict(base)
    for key, value in overlay.items():
        if key in RISK_OR_PRODUCTION:
            if value is True or merged.get(key) is True:
                merged[key] = True
            elif key not in merged or merged.get(key) is None:
                merged[key] = value
            elif value is False and merged.get(key) is not True:
                merged[key] = False
        else:
            merged[key] = value
    return merged


def envelope_facts(envelope: dict[str, Any]) -> dict[str, Any]:
    return dict(envelope.get("facts") or {})


def save_envelope(repo: Path, envelope: dict[str, Any]) -> Path:
    out = facts_path(repo, str(envelope.get("work_item_id") or "unknown"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(envelope, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def load_envelope(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("WORK_FACTS_INVALID") from exc
    if data.get("schema") == "smc.ges.work-authority.v1":
        return from_work_authority(data)
    if data.get("schema") != SCHEMA:
        raise ValueError("WORK_FACTS_INVALID")
    return data


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("verify")
    p.add_argument("path", type=Path)
    p.add_argument("--repo", type=Path)
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("build")
    p.add_argument("--work-item-id", required=True)
    p.add_argument("--facts", type=Path, required=True)
    p.add_argument("--provenance", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    if a.cmd == "verify":
        data = load_envelope(a.path)
        status, reasons = verify_envelope(data, a.repo)
        out = {"status": status, "reasons": reasons, "facts_digest": data.get("facts_digest")}
        print(json.dumps(out, indent=2) if a.json else status)
        return 0 if status == "VERIFIED" else 1
    facts = json.loads(a.facts.read_text(encoding="utf-8"))
    provenance = json.loads(a.provenance.read_text(encoding="utf-8"))
    env = build_envelope(a.work_item_id, facts, provenance)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(env, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
