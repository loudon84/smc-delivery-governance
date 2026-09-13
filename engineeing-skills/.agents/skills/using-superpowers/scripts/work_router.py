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

    # unknown/missing authority that could mean production work blocks NONE
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
            # missing among a partial authority set => fail closed
            reasons.append("WORK_RESEARCH_AUTHORITY_MISSING")
            return False, reasons

    if governed is False and retained is False and write_req is False and durable is False:
        return True, reasons

    reasons.append("WORK_RESEARCH_AUTHORITY_MISSING")
    return False, reasons


def route(facts: dict[str, Any], previous: str | None = None) -> dict[str, Any]:
    if not isinstance(facts, dict):
        raise ValueError("WORK_FACTS_INVALID")
    if previous is not None and previous not in {"NONE", "LEAN", "FULL"}:
        raise ValueError("PREVIOUS_PROFILE_INVALID")

    known = all(facts.get(k) is True for k in REQUIRED)
    safe = all(facts.get(k) is False for k in RISKS)
    reasons = [k for k in RISKS if facts.get(k) is not False]
    reasons += [k for k in REQUIRED if facts.get(k) is not True]

    research_ok, research_reasons = effective_research_only(facts, previous)
    reasons.extend(research_reasons)

    if research_ok:
        work, profile = "SPIKE", "NONE"
    elif research_reasons and _research_intent(facts) is True and previous in {None, "NONE"}:
        # Intent claimed research but authority failed => FULL, never NONE.
        work, profile = "ARCHITECTURAL", "FULL"
    elif known and safe and previous != "FULL":
        work = "BOUNDED"
        profile = "LEAN" if facts.get("governed") is True or previous == "LEAN" else "NONE"
    else:
        work, profile = "ARCHITECTURAL", "FULL"

    return {
        "schema": "smc.ges.work-route.v2",
        "work_class": work,
        "governance_profile": profile,
        "reasons": reasons,
        "facts": facts,
        "effective_research_only": research_ok,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("facts", type=Path)
    p.add_argument("--previous-profile", choices=("NONE", "LEAN", "FULL"))
    a = p.parse_args()
    print(
        json.dumps(
            route(json.loads(a.facts.read_text(encoding="utf-8")), a.previous_profile),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
