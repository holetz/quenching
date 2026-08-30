"""Assemble the proof inventory and static findings."""
from __future__ import annotations

from quenching.proof.checks import run_checks
from quenching.proof.inventory import build_inventory


def inspect_proof(root: str) -> tuple[dict | None, dict]:
    """Return one inventory envelope with all findings, or a refusal payload."""
    inventory, err = build_inventory(root)
    if err:
        return None, err
    assert inventory is not None
    findings = [finding.as_dict() for finding in run_checks(inventory)]
    errors = sum(item["severity"] == "error" for item in findings)
    payload = inventory.as_dict()
    payload.update({
        "scanned": len(inventory.test_modules),
        "suiteRun": False,
        "errors": errors,
        "warnings": len(findings) - errors,
        "findings": findings,
        "ok": not findings,
    })
    return payload, {}


def doctor(root: str) -> tuple[dict | None, dict, int]:
    """Run static proof checks; exit 1 means findings and 2 means refusal."""
    payload, err = inspect_proof(root)
    if err:
        return None, err, 2
    assert payload is not None
    return payload, {}, 0 if payload["ok"] else 1
