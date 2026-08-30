"""The static shape-and-gate checks for the proof front.

Each function consumes the frozen inventory model and returns findings without opening a second
interpretation of the target. The checks deliberately grade declarations and structure only; the
suite itself remains outside this pillar's execution boundary.
"""
from __future__ import annotations

from quenching.ops.inventory import build_inventory as build_ops_inventory
from quenching.proof.model import Finding, ProofInventory


def _error(code: str, message: str, *, path: str | None = None,
           layer: str | None = None) -> Finding:
    return Finding(code, "error", message, path, layer)


def check_unlayered(inventory: ProofInventory) -> list[Finding]:
    return [_error("pf-unlayered", "test module is not inside a declared layer",
                    path=item.path)
            for item in inventory.test_modules if item.layer is None]


def check_unmarked(inventory: ProofInventory) -> list[Finding]:
    findings: list[Finding] = []
    registered = set(inventory.gate.markers)
    if inventory.test_modules and not inventory.gate.strict_markers:
        findings.append(_error("pf-unmarked", "pytest strict markers are not enabled",
                               path=inventory.gate.path))
    for item in inventory.test_modules:
        if item.layer and item.marker != item.layer:
            findings.append(_error("pf-unmarked", "derived marker disagrees with its layer",
                                   path=item.path, layer=item.layer))
        if item.marker and item.marker not in registered:
            findings.append(_error("pf-unmarked", f"derived marker `{item.marker}` is not registered",
                                   path=item.path, layer=item.layer))
    return findings


def check_loose_fixture(inventory: ProofInventory) -> list[Finding]:
    locations: dict[str, list[str]] = {}
    for fixture in inventory.fixtures:
        if not fixture.library:
            locations.setdefault(fixture.name, []).append(fixture.path)
    findings: list[Finding] = []
    for name, paths in sorted(locations.items()):
        if len(paths) > 1:
            findings.append(_error("pf-loose-fixture",
                                   f"fixture `{name}` is copied across {len(paths)} test modules",
                                   path=paths[0]))
    return findings


def check_fat_conftest(inventory: ProofInventory) -> list[Finding]:
    findings: list[Finding] = []
    for item in inventory.conftests:
        if not item.library and item.fixture_names:
            findings.append(_error("pf-fat-conftest",
                                   "root conftest defines domain fixtures; move them to fixtures/",
                                   path=item.path))
    return findings


def check_unmeasured_surface(inventory: ProofInventory) -> list[Finding]:
    measured = {item.rstrip("/").split("/")[0] for item in inventory.measured_roots}
    excluded = {item.rstrip("/").split("/")[0] for item in inventory.exclusions}
    return [_error("pf-unmeasured-surface",
                   f"source surface `{surface}` is not in measuredRoots or proofExclusions",
                   path=surface)
            for surface in inventory.source_surfaces
            if surface not in measured and surface not in excluded]


def check_no_floor(inventory: ProofInventory) -> list[Finding]:
    if not inventory.measured_roots:
        return []
    if inventory.gate.coverage_floor is not None or inventory.gate.ratchet_exists:
        return []
    return [_error("pf-no-floor", "measured roots have no coverage floor or ratchet file",
                   path=inventory.gate.ratchet_path)]


def check_stop_first(inventory: ProofInventory) -> list[Finding]:
    return [_error("pf-stop-first", "pytest addopts stops after the first failure",
                   path=inventory.gate.path)
            for option in inventory.gate.addopts if option.startswith("--maxfail")]


def check_empty_layer(inventory: ProofInventory) -> list[Finding]:
    present = {item.layer for item in inventory.test_modules if item.layer}
    return [_error("pf-empty-layer", "required layer has no collected test module",
                   path=item.path, layer=item.name)
            for item in inventory.layers if item.required and item.name not in present]


def check_no_ci(inventory: ProofInventory) -> list[Finding]:
    if any(item.runs_gate for item in inventory.ci):
        return []
    return [_error("pf-no-ci", "no CI definition invokes the proof gate",
                   path=inventory.ci[0].path if inventory.ci else None)]


def check_order_unproven(inventory: ProofInventory) -> list[Finding]:
    if any(item.randomizes_order for item in inventory.ci if item.runs_gate):
        return []
    return [_error("pf-order-unproven",
                   "no proof-gate invocation declares randomized test order",
                   path=inventory.ci[0].path if inventory.ci else None)]


def check_untested_entrypoint(inventory: ProofInventory) -> list[Finding]:
    """Compare test imports with the ops inventory, or stay silent when ops is not configured."""
    operations, err = build_ops_inventory(inventory.repo_root)
    if err:
        if err.get("code") == "op-config-missing":
            return []
        return [_error("pf-untested-entrypoint",
                       f"ops inventory could not be read: {err.get('message', 'unknown error')}")]
    assert operations is not None
    imported = {name for module in inventory.test_modules for name in module.imports}
    findings: list[Finding] = []
    for entry in operations.entry_points:
        if not entry.module:
            continue
        if any(name == entry.module or name.startswith(entry.module + ".") for name in imported):
            continue
        findings.append(_error("pf-untested-entrypoint",
                               f"operations entry point `{entry.module}` is not imported by a test",
                               path=entry.path))
    return findings


def run_checks(inventory: ProofInventory) -> list[Finding]:
    checks = (check_unlayered, check_unmarked, check_loose_fixture, check_fat_conftest,
              check_unmeasured_surface, check_no_floor, check_stop_first, check_empty_layer,
              check_no_ci, check_order_unproven, check_untested_entrypoint)
    findings = [finding for check in checks for finding in check(inventory)]
    return sorted(findings, key=lambda item: (item.code, item.path or "", item.message))
