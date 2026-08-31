"""Stable read-model shapes for the delivery applicability and inventory stages."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Applicability:
    """The signal that decides whether a target has a delivery surface to inspect."""

    root: str
    state: str
    signal: str | None
    provider: str | None = None
    artifacts: tuple[str, ...] = ()
    config_error: dict[str, Any] = field(default_factory=dict, repr=False)

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "signal": self.signal,
            "provider": self.provider,
            "artifacts": list(self.artifacts),
        }


@dataclass(frozen=True)
class Workflow:
    """One provider or provider-equivalent workflow artifact."""

    path: str
    provider: str
    kind: str
    parse: str
    triggers: tuple[str, ...] = ()
    jobs: tuple[str, ...] = ()
    stages: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "provider": self.provider,
            "kind": self.kind,
            "parse": self.parse,
            "triggers": list(self.triggers),
            "jobs": list(self.jobs),
            "stages": list(self.stages),
        }


@dataclass(frozen=True)
class DeliveryInventory:
    """The single workflow read model consumed by later delivery checks."""

    repo_root: str
    applicability: Applicability
    workflows: tuple[Workflow, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "repoRoot": self.repo_root,
            "applicability": self.applicability.as_dict(),
            "workflows": [workflow.as_dict() for workflow in self.workflows],
        }
