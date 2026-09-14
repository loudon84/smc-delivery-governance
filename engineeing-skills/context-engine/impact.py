"""Build an impact manifest from the dependency graph."""
from __future__ import annotations

from typing import Any

from coe_common import IMPACT_SCHEMA, sha256_json
from graph import reverse_closure
from registry import Registry


def impact_manifest(
    registry: Registry,
    graph: dict[str, Any],
    changed_modules: list[str],
    *,
    contract_changes: bool = False,
    architecture_boundary: bool = False,
) -> dict[str, Any]:
    affected_modules: set[str] = set(changed_modules)
    for module in changed_modules:
        affected_modules.update(reverse_closure(graph, module))
    applications = [r.rec_id for r in registry.records if r.kind == "application" and any(m in r.uses or m in r.allowed_dependencies for m in affected_modules)]
    components = [r.rec_id for r in registry.components() if r.host_module in affected_modules]
    contracts = sorted({c for r in registry.records if r.rec_id in affected_modules for c in r.contracts})
    reviews = []
    if architecture_boundary:
        reviews.append("ARCHITECTURE")
    if contract_changes or len(affected_modules) > 1:
        reviews.append("INTEGRATION")
    if affected_modules:
        reviews.append("MODULE")
    coverage = graph.get("coverage") or "COMPLETE"
    payload = {
        "schema": IMPACT_SCHEMA,
        "impact_id": sha256_json({"modules": sorted(affected_modules), "graph": graph.get("digest")})[7:23],
        "graph_digest": graph.get("digest"),
        "coverage": coverage,
        "affected": {
            "modules": sorted(affected_modules),
            "components": sorted(components),
            "applications": sorted(applications),
            "contracts": contracts,
            "reviews": sorted(set(reviews)),
            "verifications": ["integration"] if "INTEGRATION" in reviews else ["module"],
        },
        "incomplete_reasons": list(graph.get("incomplete_reasons") or []),
    }
    return payload
