"""Assemble the toolchain applicability result."""
from __future__ import annotations

from quenching.toolchain.probe import probe_toolchain


def inspect_toolchain(root: str) -> tuple[dict | None, dict]:
    """Return the read-only applicability envelope or a refusal payload."""
    applicability = probe_toolchain(root)
    payload = {
        "root": applicability.root,
        "applicability": applicability.as_dict(),
        "inventory": None,
        "findings": [],
        "errors": 0,
        "warnings": 0,
        "ok": True,
    }
    return payload, {}


def doctor(root: str) -> tuple[dict | None, dict, int]:
    """Run the applicability probe; not-applicable is a valid result."""
    return (*inspect_toolchain(root), 0)
