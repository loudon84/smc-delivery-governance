from __future__ import annotations

from pathlib import Path

from ges.catalog.loader import Capability, Catalog, SourcePin
from ges.errors import SPEC_KIT_MANAGED_CONFLICT, SPEC_KIT_RECONCILE_CONFLICT, GesError
from ges.reconciler.hashes import artifact_index
from ges.reconciler.state import read_receipt
from ges.resolver.capability_graph import Resolution
from ges.source_adapters.base import ProjectedFile, Projection
from ges.source_adapters.speckit_render import command_rel, render_selected

WRAPPER = """---
name: {name}
description: Spec Kit {capability} capability composed by GES 6.
---

# {name}

Use the pinned Spec Kit command at `{managed}`.

- source repo: {repo}
- source commit: {sha}
- source path: {source_path}
"""


class SpecKitAdapter:
    source_id = "spec-kit"

    def project(
        self,
        catalog: Catalog,
        pin: SourcePin,
        capabilities: list[Capability],
        repo: Path,
        resolution: Resolution,
    ) -> Projection:
        projection = Projection()
        owned = artifact_index(read_receipt(repo) or {})
        for item in render_selected(pin, capabilities):
            if (repo / item.relpath).is_file() and item.relpath not in owned:
                current = (repo / item.relpath).read_bytes()
                if current != item.content:
                    raise GesError(
                        SPEC_KIT_MANAGED_CONFLICT,
                        f"managed Spec Kit path {item.relpath} exists without GES receipt ownership",
                    )
            projection.add(item)
        for cap in capabilities:
            if cap.projection_type != "speckit-capability" or not cap.skill_name:
                continue
            command = cap.id.split(".", 1)[1]
            managed = command_rel(command)
            rel = f".agents/skills/{cap.skill_name}/SKILL.md"
            content = WRAPPER.format(
                name=cap.skill_name,
                capability=cap.id,
                managed=managed,
                repo=pin.repo,
                sha=pin.commit_sha,
                source_path=cap.source_path,
            ).encode("utf-8")
            if (repo / rel).is_file() and rel not in owned:
                if (repo / rel).read_bytes() != content:
                    raise GesError(
                        SPEC_KIT_RECONCILE_CONFLICT,
                        f"Spec Kit wrapper {rel} exists without GES receipt ownership",
                    )
            projection.add(
                ProjectedFile(
                    relpath=rel,
                    content=content,
                    capability=cap.id,
                    source=pin.id,
                    source_sha=pin.commit_sha,
                    kind="skill",
                    ownership_type="FILE",
                )
            )
        return projection
