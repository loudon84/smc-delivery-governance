from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from ges.catalog.loader import Capability, Catalog, SourcePin
from ges.resolver.capability_graph import Resolution


@dataclass
class ProjectedFile:
    relpath: str
    content: bytes
    capability: str | None
    source: str | None
    source_sha: str | None
    kind: str
    managed: bool = True


@dataclass
class Projection:
    files: dict[str, ProjectedFile] = field(default_factory=dict)

    def add(self, item: ProjectedFile) -> None:
        self.files[item.relpath] = item

    def contents(self) -> dict[str, bytes]:
        return {key: value.content for key, value in self.files.items()}


class SourceAdapter(Protocol):
    source_id: str

    def project(
        self,
        catalog: Catalog,
        pin: SourcePin,
        capabilities: list[Capability],
        repo: Path,
        resolution: Resolution,
    ) -> Projection:
        ...
