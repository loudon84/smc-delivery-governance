"""Deterministic risk routing from explicit, reviewable work facts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED = (
    "existing_owner",
    "existing_capability",
    "bounded_writes",
    "deterministic_verification",
)
RISKS = (
    "new_owner",
    "public_contract",
    "security_boundary",
    "schema_migration",
    "protocol_change",
    "external_dependency",
    "lifecycle_change",
    "cross_domain_ownership",
    "live_acceptance",
)
RESEARCH_AUTHORITY = (
    "governed",
    "retained_production_change",
    "production_write_requested",
    "durable_product_artifact_requested",
)


def _tri(value: Any) -> bool | None:
    if value is True:
        return True
    if value is False:
        return False
    return None


def _research_intent(facts: dict[str, Any]) -> bool | None:
    if "research_intent" in facts:
        return _tri(facts.get("research_intent"))
    if "research_only" in facts:
        return _tri(facts.get("research_only"))
    return None


def effective_research_only(facts: dict[str, Any], previous: str | None) -> tuple[bool, list[str]]:
    # @lat: [[acceptance-hardening#Work Router Research Trust]]
    """research_only is a hint; authority facts decide SPIKE/NONE eligibility."""
    reasons: list[str] = []
    intent = _research_intent(facts)
    if intent is not True:
        return False, reasons
    if previous not in {None, "NONE"}:
        reasons.append("RESEARCH_ONLY_PREVIOUS_PROFILE_BLOCKS")
        return False, reasons

    governed = _tri(facts.get("governed"))
    retained = _tri(facts.get("retained_production_change"))
    write_req = _tri(facts.get("production_write_requested"))
    durable = _tri(facts.get("durable_product_artifact_requested"))

    # Legacy callers that only set research_only without authority facts fail closed.
    authority_present = any(k in facts for k in RESEARCH_AUTHORITY)
    if not authority_present and "research_intent" not in facts:
        reasons.append("WORK_RESEARCH_AUTHORITY_MISSING")
        return False, reasons

    if governed is True:
        reasons.append("RESEARCH_ONLY_CONTRADICTS_GOVERNED_WORK")
        return False, reasons
    if write_req is True:
        reasons.append("RESEARCH_ONLY_PRODUCTION_WRITE_CONFLICT")
        return False, reasons
    if retained is True:
        reasons.append("RESEARCH_ONLY_RETAINED_PRODUCTION_CHANGE")
        return False, reasons
    if durable is True:
        reasons.append("RESEARCH_ONLY_DURABLE_ARTIFACT_CONFLICT")
        return False, reasons

    for key, value in (
        ("governed", governed),
        ("retained_production_change", retained),
        ("production_write_requested", write_req),
        ("durable_product_artifact_requested", durable),
    ):
        if value is None and key in facts:
            reasons.append("WORK_RESEARCH_AUTHORITY_MISSING")
            return False, reasons
        if value is None and key not in facts and authority_present:
            reasons.append("WORK_RESEARCH_AUTHORITY_MISSING")
            return False, reasons

    if governed is False and retained is False and write_req is False and durable is False:
        return True, reasons

    reasons.append("WORK_RESEARCH_AUTHORITY_MISSING")
    return False, reasons


def route(
    facts: dict[str, Any],
    previous: str | None = None,
    *,
    authority: dict[str, Any] | None = None,
    authority_status: str | None = None,
    require_authority_for_none: bool = False,
    work_facts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Library-compatible router. Production orchestrators should call route_bound()."""
    if not isinstance(facts, dict):
        raise ValueError("WORK_FACTS_INVALID")
    if previous is not None and previous not in {"NONE", "LEAN", "FULL"}:
        raise ValueError("PREVIOUS_PROFILE_INVALID")

    auth_status = authority_status or ("UNBOUND" if authority is None and work_facts is None else "VERIFIED")
    auth_sha = None
    merged = dict(facts)
    research_block: list[str] = []

    if work_facts is not None:
        from work_facts import envelope_facts, verify_envelope

        status, auth_reasons = verify_envelope(work_facts)
        auth_status = status if status == "VERIFIED" else status
        auth_sha = work_facts.get("facts_digest")
        if status != "VERIFIED":
            for k in RESEARCH_AUTHORITY:
                merged.pop(k, None)
            research_block = auth_reasons or ["WORK_FACTS_AUTHORITY_MISSING"]
            # map unbound/stale to production block codes
            if status == "UNBOUND":
                research_block = ["WORK_FACTS_UNBOUND"]
            elif status == "STALE":
                research_block = ["WORK_FACTS_STALE"]
        else:
            merged = {**merged, **envelope_facts(work_facts)}
    elif authority is not None:
        from work_authority import merge_route_facts, verify_authority

        legacy_status, legacy_reasons = verify_authority(authority)
        auth_sha = authority.get("authority_sha256")
        if legacy_status == "VERIFIED":
            merged = merge_route_facts(facts, authority)
            auth_status = "VERIFIED"
        else:
            for k in RESEARCH_AUTHORITY:
                merged.pop(k, None)
            research_block = legacy_reasons or ["WORK_AUTHORITY_MISSING"]
            auth_status = legacy_status
    else:
        pass
    known = all(merged.get(k) is True for k in REQUIRED)
    safe = all(merged.get(k) is False for k in RISKS)
    reasons = [k for k in RISKS if merged.get(k) is not False]
    reasons += [k for k in REQUIRED if merged.get(k) is not True]

    research_ok, research_reasons = effective_research_only(merged, previous)
    reasons.extend(research_reasons)
    reasons.extend(research_block)

    authority_blocked_none = False
    bound_required = require_authority_for_none or authority is not None or work_facts is not None
    if research_ok and bound_required:
        if auth_status != "VERIFIED":
            research_ok = False
            authority_blocked_none = True
            if "WORK_FACTS_UNBOUND" not in reasons and "WORK_FACTS_STALE" not in reasons:
                reasons.append("WORK_AUTHORITY_MISSING" if work_facts is None else "WORK_FACTS_AUTHORITY_MISSING")
    if research_ok and require_authority_for_none and authority is None and work_facts is None:
        research_ok = False
        authority_blocked_none = True
        reasons.append("WORK_AUTHORITY_MISSING")

    if research_ok:
        work, profile = "SPIKE", "NONE"
    elif authority_blocked_none or (
        (research_reasons or research_block) and _research_intent(merged) is True and previous in {None, "NONE"}
    ):
        work, profile = "ARCHITECTURAL", "FULL"
    elif known and safe and previous != "FULL":
        work = "BOUNDED"
        profile = "LEAN" if merged.get("governed") is True or previous == "LEAN" else "NONE"
        if profile == "NONE" and require_authority_for_none and auth_status != "VERIFIED":
            work, profile = "BOUNDED", "LEAN"
            reasons.append("WORK_AUTHORITY_MISSING")
    else:
        work, profile = "ARCHITECTURAL", "FULL"

    return {
        "schema": "smc.ges.work-route.v2",
        "work_class": work,
        "governance_profile": profile,
        "reasons": reasons,
        "facts": merged,
        "effective_research_only": research_ok,
        "authority_sha256": auth_sha,
        "authority_status": auth_status if bound_required else "UNBOUND",
        "facts_digest": auth_sha if work_facts is not None else None,
    }


def route_bound(
    envelope: dict[str, Any],
    previous: str | None = None,
    *,
    caller_facts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Production entry: requires verified smc.ges.work-facts.v1 envelope."""
    # @lat: [[governance-architecture-closure]]
    from work_facts import envelope_facts

    base = dict(caller_facts or {})
    base.update(envelope_facts(envelope))
    return route(base, previous, work_facts=envelope, require_authority_for_none=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("facts", type=Path, nargs="?", help="raw facts JSON (requires --unsafe-raw-facts) or work-facts envelope")
    p.add_argument("--previous-profile", choices=("NONE", "LEAN", "FULL"))
    p.add_argument("--authority", type=Path, help="legacy smc.ges.work-authority.v1 (compat)")
    p.add_argument("--work-facts", type=Path, help="smc.ges.work-facts.v1 envelope (production default)")
    p.add_argument(
        "--unsafe-raw-facts",
        action="store_true",
        help="dev/selftest only: allow unbound raw facts JSON; forbidden for production orchestrators",
    )
    a = p.parse_args()
    if a.work_facts:
        from work_facts import load_envelope

        env = load_envelope(a.work_facts)
        print(json.dumps(route_bound(env, a.previous_profile), indent=2, ensure_ascii=False))
        return
    if a.authority:
        from work_authority import load_authority
        from work_facts import from_work_authority

        authority = load_authority(a.authority)
        # prefer converted work-facts path
        env = from_work_authority(authority)
        caller = {}
        if a.facts:
            caller = json.loads(a.facts.read_text(encoding="utf-8"))
        print(
            json.dumps(
                route(caller, a.previous_profile, authority=authority, require_authority_for_none=True),
                indent=2,
                ensure_ascii=False,
            )
        )
        return
    if not a.facts:
        raise SystemExit("facts path or --work-facts required")
    raw = json.loads(a.facts.read_text(encoding="utf-8"))
    if raw.get("schema") == "smc.ges.work-facts.v1":
        print(json.dumps(route_bound(raw, a.previous_profile), indent=2, ensure_ascii=False))
        return
    if not a.unsafe_raw_facts:
        raise SystemExit("production CLI requires --work-facts (or pass envelope JSON); use --unsafe-raw-facts only for dev/selftest")
    print(
        json.dumps(
            route(raw, a.previous_profile, require_authority_for_none=True),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
