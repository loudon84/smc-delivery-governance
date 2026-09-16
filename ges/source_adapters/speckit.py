from __future__ import annotations

from pathlib import Path

from ges.catalog.loader import Capability, Catalog, SourcePin
from ges.errors import SPEC_KIT_RECONCILE_CONFLICT, GesError
from ges.reconciler.hashes import artifact_index
from ges.reconciler.state import read_receipt
from ges.resolver.capability_graph import Resolution
from ges.source_adapters.base import ProjectedFile, Projection
from ges.source_adapters.cache import resolve_path

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
        existing = (repo / ".specify").exists()
        if not existing:
            self._materialize_runtime(pin, capabilities, projection)
        owned = artifact_index(read_receipt(repo) or {})
        for cap in capabilities:
            if cap.projection_type != "speckit-capability" or not cap.skill_name:
                continue
            command = cap.id.split(".", 1)[1]
            source_file = resolve_path(pin, cap.source_path)
            managed = f".specify/.ges/commands/{command}.md"
            if (repo / managed).is_file() and managed not in owned:
                raise GesError(
                    SPEC_KIT_RECONCILE_CONFLICT,
                    f"managed Spec Kit path {managed} exists without GES receipt ownership",
                )
            projection.add(
                ProjectedFile(
                    relpath=managed,
                    content=source_file.read_bytes(),
                    capability=cap.id,
                    source=pin.id,
                    source_sha=pin.commit_sha,
                    kind="specify",
                    ownership_type="FILE",
                )
            )
            content = WRAPPER.format(
                name=cap.skill_name,
                capability=cap.id,
                managed=managed,
                repo=pin.repo,
                sha=pin.commit_sha,
                source_path=cap.source_path,
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
                    ownership_type="FILE",
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
                            ownership_type="FILE",
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
                        ownership_type="FILE",
                    )
                )
