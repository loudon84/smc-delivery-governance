from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ArtifactRef:
    """Pointer-only artifact identity. GES 6 never copies artifact body."""

    pointer: str
    identity: str
    digest: str
    status: str
    timestamp: str


@dataclass
class Work:
    id: str
    artifacts: list[ArtifactRef] = field(default_factory=list)
    risk: str | None = None
    policy: str | None = None
    ownership: str | None = None
    evidence: list[str] = field(default_factory=list)
    approvals: list[str] = field(default_factory=list)
    release: str | None = None


@dataclass
class Evidence:
    id: str
    pointer: ArtifactRef


@dataclass
class Policy:
    id: str
    rules: dict[str, Any] = field(default_factory=dict)


@dataclass
class Risk:
    id: str
    level: str


@dataclass
class Ownership:
    work_id: str
    owner: str


@dataclass
class Approval:
    id: str
    work_id: str
    actor: str
    verdict: str


@dataclass
class Release:
    id: str
    work_id: str
    commit: str | None = None
    pull_request: str | None = None
    build: str | None = None


BACKPLANE_MODULES = (
    "01 Registry",
    "02 Policy",
    "03 Risk",
    "04 Ownership",
    "05 Evidence",
    "06 Approval",
    "07 Traceability",
    "08 Delivery",
    "09 Release",
    "10 Audit",
)
