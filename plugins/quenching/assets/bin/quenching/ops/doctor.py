"""Assemble the ops checks and expose the three-step doctor contract."""
from __future__ import annotations

from quenching.ops.checks import run_checks
from quenching.ops.inventory import build_inventory


def inspect_ops(root: str) -> tuple[dict | None, dict]:
    """Return the inventory envelope with its findings, or a refusal payload."""
    inventory, err = build_inventory(root)
    if err:
        return None, err
    assert inventory is not None
    findings = [finding.as_dict() for finding in run_checks(inventory)]
    errors = sum(finding["severity"] == "error" for finding in findings)
    payload = inventory.as_dict()
    payload.update({
        "scanned": len(inventory.entry_points),
        "errors": errors,
        "warnings": len(findings) - errors,
        "findings": findings,
        "ok": not findings,
    })
    return payload, {}


def doctor(root: str) -> tuple[dict | None, dict, int]:
    """Run the full read-only doctor and return ``(payload, refusal, exit_code)``.

    Unlike the generic report helper, this contract treats warnings as findings too: the ops
    probe is the align's gate, so a non-empty report must return 1 even while a later policy may
    downgrade a heuristic's severity for display.
    """
    payload, err = inspect_ops(root)
    if err:
        return None, err, 2
    assert payload is not None
    return payload, {}, 0 if not payload["findings"] else 1
