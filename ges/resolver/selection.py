from __future__ import annotations

from ges.catalog.loader import Catalog, Profile
from ges.errors import CAPABILITY_NOT_FOUND, GesError
from ges.resolver.capability_graph import Resolution, resolve_graph


def recommend(catalog: Catalog, profile: Profile) -> list[str]:
    return list(dict.fromkeys(profile.required + profile.optional))


def resolve_selection(
    catalog: Catalog,
    profile: Profile,
    *,
    exclude: list[str] | None = None,
    extra: list[str] | None = None,
) -> Resolution:
    exclude = list(exclude or [])
    extra = list(extra or [])
    unknown = [item for item in exclude + extra if item not in catalog.capabilities]
    if unknown:
        raise GesError(CAPABILITY_NOT_FOUND, f"unknown capability {unknown[0]}", details={"ids": unknown})
    extra = list(extra or [])
    selected = recommend(catalog, profile) + extra
    excluded = [
        item
        for item in dict.fromkeys(profile.excluded + exclude)
        if item not in extra
    ]
    return resolve_graph(
        catalog,
        profile=profile.id,
        selected=selected,
        excluded=excluded,
    )


def project_desired_state(profile: Profile, resolution: Resolution, agents: list[str]) -> dict:
    return {
        "schema": "ges.project.v1",
        "profile": profile.id,
        "agents": agents,
        "engineering_stack": profile.engineering_stack,
        "resolution": {
            "mode": "auto",
            "selected": resolution.closed,
            "excluded": resolution.excluded,
            "optional": profile.optional,
        },
    }
