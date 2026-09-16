from __future__ import annotations

from pathlib import Path

from ges.catalog.loader import Capability, Catalog, SourcePin
from ges.errors import SPEC_KIT_RECONCILE_CONFLICT, GesError
from ges.resolver.capability_graph import Resolution
from ges.source_adapters.base import ProjectedFile, Projection
from ges.source_adapters.cache import resolve_path

WRAPPER = """---
name: {name}
description: Spec Kit {capability} capability composed by GES 6.
---

# {name}

Use the project's Spec Kit `{command}` command. GES composed this skill
from pinned spec-kit `{sha}` and does not reinitialize `.specify/`.
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
        existing = (repo / ".specify").exists()
        if not existing:
            self._materialize_runtime(pin, capabilities, projection)
        for cap in capabilities:
            if cap.projection_type != "speckit-capability" or not cap.skill_name:
                continue
            command = cap.id.split(".", 1)[1]
            content = WRAPPER.format(
                name=cap.skill_name,
                capability=cap.id,
                command=command,
                sha=pin.commit_sha,
            ).encode("utf-8")
            rel = f".agents/skills/{cap.skill_name}/SKILL.md"
            projection.add(
                ProjectedFile(
                    relpath=rel,
                    content=content,
                    capability=cap.id,
                    source=pin.id,
                    source_sha=pin.commit_sha,
                    kind="skill",
                )
            )
            source_file = resolve_path(pin, cap.source_path)
            managed = f".specify/.ges/commands/{source_file.name}"
            if existing and (repo / managed).is_file():
                current = (repo / managed).read_bytes()
                desired = source_file.read_bytes()
                if current != desired:
                    raise GesError(
                        SPEC_KIT_RECONCILE_CONFLICT,
                        f"managed Spec Kit path {managed} diverged from pinned source",
                    )
            projection.add(
                ProjectedFile(
                    relpath=managed,
                    content=source_file.read_bytes(),
                    capability=cap.id,
                    source=pin.id,
                    source_sha=pin.commit_sha,
                    kind="specify",
                )
            )
        return projection

    def _materialize_runtime(
        self,
        pin: SourcePin,
        capabilities: list[Capability],
        projection: Projection,
    ) -> None:
        runtime_root = resolve_path(pin, ".specify")
        if runtime_root.is_dir():
            for path in runtime_root.rglob("*"):
                if path.is_file():
                    rel = ".specify/" + path.relative_to(runtime_root).as_posix()
                    projection.add(
                        ProjectedFile(
                            relpath=rel,
                            content=path.read_bytes(),
                            capability=None,
                            source=pin.id,
                            source_sha=pin.commit_sha,
                            kind="specify-runtime",
                        )
                    )
        for cap in capabilities:
            for runtime_path in cap.runtime_paths:
                if runtime_path == ".specify":
                    continue
                src = resolve_path(pin, runtime_path)
                dest = f".specify/.ges/runtime/{Path(runtime_path).name}"
                projection.add(
                    ProjectedFile(
                        relpath=dest,
                        content=src.read_bytes(),
                        capability=cap.id,
                        source=pin.id,
                        source_sha=pin.commit_sha,
                        kind="specify-runtime",
                    )
                )
