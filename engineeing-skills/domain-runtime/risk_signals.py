"""Shared structured risk runtime for PRD / Plan / Review.

Structured facts are the primary SOT. Negation-aware text hints only detect
contradictions or fill conservative fallback when structured facts are missing.
"""
from __future__ import annotations

import json
import re
from typing import Any

RISK_KEYS = (
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

CAPABILITY_KEYS = (
    "existing_owner",
    "existing_capability",
    "bounded_writes",
    "deterministic_verification",
)

# Affirmative phrase patterns keyed by risk. Negation wrappers flip AFFIRMATIVE -> NEGATED.
AFFIRMATIVE_PATTERNS: dict[str, tuple[str, ...]] = {
    "new_owner": (r"\bnew\s+(service|store|client|protocol|owner)\b", r"\bintroduce\s+new\s+owner\b"),
    "public_contract": (r"\bpublic\s+(api|contract)\b", r"\bprotocol\s+change\b"),
    "security_boundary": (r"\b(auth|authentication|authorization)\s+boundary\b", r"\b(trust|security)\s+boundary\b"),
    "schema_migration": (r"\bschema\s+migration\b", r"\bdata\s+migration\b"),
    "protocol_change": (r"\bprotocol\s+change\b", r"\bbreaking\s+protocol\b"),
    "external_dependency": (r"\bnew\s+external\s+dependency\b", r"\badd\s+external\s+dependency\b"),
    "lifecycle_change": (r"\blifecycle\s+change\b", r"\bdeployment\s+lifecycle\b"),
    "cross_domain_ownership": (r"\bcross[- ]domain\s+ownership\b",),
    "live_acceptance": (r"\b\bLIVE\b", r"\bFAULT[_ ]?INJECTION\b", r"\bEXTERNAL\b"),
}

NEGATION = re.compile(
    r"\b(no|none|not|without|never|unchanged|not\s+required|is\s+not\s+required|does\s+not)\b",
    re.I,
)
AMBIGUOUS = re.compile(r"\b(tbd|unknown|maybe|possibly|unclear|undecided)\b", re.I)


def classify_text_hint(text: str, risk: str) -> str:
    """Return AFFIRMATIVE | NEGATED | AMBIGUOUS | ABSENT for one risk key."""
    patterns = AFFIRMATIVE_PATTERNS.get(risk, ())
    hits: list[tuple[int, int, str]] = []
    for pat in patterns:
        for m in re.finditer(pat, text, re.I):
            hits.append((m.start(), m.end(), m.group(0)))
    if not hits:
        return "ABSENT"
    for start, end, _ in hits:
        window = text[max(0, start - 48) : min(len(text), end + 48)]
        if AMBIGUOUS.search(window):
            return "AMBIGUOUS"
        if NEGATION.search(window):
            return "NEGATED"
    return "AFFIRMATIVE"


def parse_routing_facts(section_text: str) -> dict[str, Any] | None:
    raw = section_text.strip()
    if raw.startswith("```"):
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    return value if isinstance(value, dict) else None


def extract_risk_snapshot(text: str) -> dict[str, Any] | None:
    """Read Plan Risk Facts Snapshot JSON if present."""
    m = re.search(
        r"Risk Facts Snapshot:\s*`?(\{.*?\})`?",
        text,
        re.S,
    )
    if not m:
        # also accept fenced block under Governance Profile
        m2 = re.search(
            r"##\s+Governance Profile\s*\n.*?Risk Facts Snapshot:\s*\n```json\s*(\{.*?\})\s*```",
            text,
            re.S | re.I,
        )
        if not m2:
            return None
        blob = m2.group(1)
    else:
        blob = m.group(1)
    try:
        value = json.loads(blob)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def structured_high_risk(facts: dict[str, Any] | None) -> tuple[bool, list[str]]:
    if facts is None:
        return True, ["RISK_FACTS_MISSING"]
    reasons: list[str] = []
    complete = True
    for key in RISK_KEYS:
        if key not in facts:
            complete = False
            reasons.append(f"RISK_FACTS_MISSING:{key}")
            continue
        if facts.get(key) is True:
            reasons.append(key)
        elif facts.get(key) is not False:
            complete = False
            reasons.append(f"RISK_FACTS_INVALID:{key}")
    if not complete and not any(facts.get(k) is True for k in RISK_KEYS):
        return True, reasons or ["RISK_FACTS_INVALID"]
    return bool(reasons and any(facts.get(k) is True for k in RISK_KEYS)), [r for r in reasons if not r.startswith("RISK_FACTS_")]


def contradiction_errors(facts: dict[str, Any] | None, text: str) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    if facts is None:
        return [{"code": "RISK_FACTS_MISSING", "detail": "structured facts unavailable"}]
    for key in RISK_KEYS:
        hint = classify_text_hint(text, key)
        structured = facts.get(key)
        if structured is False and hint == "AFFIRMATIVE":
            errors.append({"code": "RISK_FACT_CONTRADICTION", "detail": key})
        if hint == "AMBIGUOUS":
            errors.append({"code": "RISK_TEXT_AMBIGUOUS", "detail": key})
    return errors


def resolve_risk(text: str, facts: dict[str, Any] | None) -> dict[str, Any]:
    # @lat: [[acceptance-hardening#Structured Risk Runtime]]
    """Canonical resolver used by PRD / Plan / Review adapters."""
    errors: list[dict[str, str]] = []
    if facts is None:
        # Conservative fallback: ambiguous or affirmative text => high risk; negated-only is not high.
        text_hits = []
        for key in RISK_KEYS:
            hint = classify_text_hint(text, key)
            if hint == "AFFIRMATIVE":
                text_hits.append(key)
            elif hint == "AMBIGUOUS":
                errors.append({"code": "RISK_TEXT_AMBIGUOUS", "detail": key})
        high = bool(text_hits) or bool(errors) or True  # missing structured => fail closed high
        return {
            "schema": "smc.ges.risk-resolve.v1",
            "high_risk": True,
            "reasons": ["RISK_FACTS_MISSING"] + text_hits,
            "errors": [{"code": "RISK_FACTS_MISSING", "detail": "structured facts unavailable"}] + errors,
            "mode": "legacy_fallback",
        }

    high, reasons = structured_high_risk(facts)
    errors.extend(contradiction_errors(facts, text))
    if errors:
        high = True
        reasons = reasons + [e["code"] + ":" + e["detail"] for e in errors]
    return {
        "schema": "smc.ges.risk-resolve.v1",
        "high_risk": high,
        "reasons": reasons,
        "errors": errors,
        "mode": "structured",
        "facts": {k: facts.get(k) for k in RISK_KEYS},
    }


def acceptance_structure_clearance(text: str, facts: dict[str, Any] | None) -> tuple[bool, list[str]]:
    # @lat: [[acceptance-hardening#LEAN First Review Clearance]]
    """Deterministic LEAN first-review clearance for acceptance-governed plans."""
    reasons: list[str] = []
    if facts is None:
        return False, ["RISK_FACTS_MISSING"]
    high, high_reasons = structured_high_risk(facts)
    if high:
        return False, high_reasons
    if any(facts.get(k) is not True for k in CAPABILITY_KEYS):
        return False, ["CAPABILITY_FACTS_INCOMPLETE"]
    # No LIVE/FAULT/EXTERNAL modes in verification tables
    if re.search(r"\|\s*(LIVE|FAULT_INJECTION|EXTERNAL)\s*\|", text, re.I):
        return False, ["LIVE_OR_EXTERNAL_PRESENT"]
    if "Acceptance Claim Ledger" not in text and "acceptance_contract: smc.acceptance.v1" in text:
        # acceptance declared but ledger missing => not clear
        if "## Acceptance Claim Ledger" not in text:
            return False, ["ACCEPTANCE_STRUCTURE_INCOMPLETE"]
    return True, reasons


def snapshot_json(facts: dict[str, Any]) -> str:
    payload = {k: facts.get(k) for k in (*CAPABILITY_KEYS, *RISK_KEYS)}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
