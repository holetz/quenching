#!/usr/bin/env python3
"""Validate the shipped controls catalog offline; never assess a target repository."""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re

DATA = Path(__file__).resolve().parents[1] / "plugins/quenching/assets/opensource"
OWNERS = {"opensource", "security", "delivery", "toolchain", "knowledge", "proof", "git"}
SOURCE_IDS = {"osps", "scorecard", "github-community", "reuse", "contributor-covenant",
              "dco", "keep-a-changelog", "semver", "cff", "github-funding"}
# The released inventory is immutable; a new baseline needs an explicit schema migration.
REQUIREMENT_COUNTS = {
    "AC": [1, 1, 2, 2], "BR": [4, 2, 2, 1, 1, 1, 2],
    "DO": [1, 1, 2, 1, 1, 1, 1], "GV": [2, 1, 2, 1],
    "LE": [1, 2, 2], "QA": [2, 2, 1, 2, 2, 3, 1],
    "SA": [1, 1, 2], "VM": [1, 1, 1, 2, 3, 2],
}


def duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=duplicate_keys)


def text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def strings(value: object) -> bool:
    return isinstance(value, list) and all(text(item) for item in value)


def day(value: object) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def levels(value: object, supplemental: bool = False) -> bool:
    return (isinstance(value, list) and
            (bool(value) or supplemental) and
            all(type(item) is int and item in {1, 2, 3} for item in value) and
            value == sorted(set(value)))


def fields(value: object, keys: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == keys


def check(catalog: object, snapshot: object) -> list[str]:
    errors: list[str] = []

    def error(code: str, detail: object) -> None:
        errors.append(f"osc-{code}: {detail}")

    if not fields(snapshot, {"schema_version", "version", "released_on", "inspected_on",
                             "tag", "sources", "controls"}):
        return ["osc-snapshot: invalid snapshot fields"]
    if (type(snapshot["schema_version"]) is not int or snapshot["schema_version"] != 1 or
            snapshot["version"] != "2026.08.28" or snapshot["released_on"] != "2026-08-28" or
            snapshot["tag"] != "v2026.08.28" or not day(snapshot["inspected_on"])):
        error("snapshot", "unsupported version or invalid release metadata")
    sources = snapshot["sources"]
    if not isinstance(sources, dict) or set(sources) != set(REQUIREMENT_COUNTS):
        error("snapshot", "expected all eight source families")
    else:
        for family, source in sources.items():
            if (not fields(source, {"url", "sha256"}) or
                    source.get("url") != f"https://raw.githubusercontent.com/ossf/security-baseline/v2026.08.28/baseline/OSPS-{family}.yaml" or
                    not isinstance(source.get("sha256"), str) or
                    not re.fullmatch(r"[0-9a-f]{64}", source["sha256"])):
                error("snapshot", f"invalid source provenance: {family}")
    expected = {}
    if not isinstance(snapshot["controls"], list):
        error("snapshot", "controls must be a list")
    else:
        for control in snapshot["controls"]:
            if not fields(control, {"id", "family", "requirements"}) or not text(control.get("id")):
                error("snapshot", "invalid control fields")
                continue
            cid = control["id"]
            if cid in expected:
                error("snapshot", f"duplicate control: {cid}")
            expected[cid] = control
            if not isinstance(control["requirements"], list):
                error("snapshot", f"requirements must be a list: {cid}")
                continue
            for requirement in control["requirements"]:
                if (not fields(requirement, {"id", "levels", "state"}) or
                        not text(requirement.get("id")) or not levels(requirement.get("levels"))):
                    error("snapshot", f"invalid requirement: {cid}")
                    continue
                state = "retired" if requirement["id"] == "OSPS-BR-01.02" else "active"
                if requirement["state"] != state:
                    error("snapshot", f"incorrect requirement state: {requirement['id']}")
        inventory = {f"OSPS-{family}-{n:02d}": count
                     for family, counts in REQUIREMENT_COUNTS.items()
                     for n, count in enumerate(counts, 1)}
        if set(expected) != set(inventory):
            error("snapshot", "control inventory differs from the pinned release")
        for cid, count in inventory.items():
            if cid not in expected or not isinstance(expected[cid]["requirements"], list):
                continue
            control = expected[cid]
            ids = [r.get("id") for r in control["requirements"] if isinstance(r, dict)]
            if control["family"] != cid.split("-")[1] or ids != [f"{cid}.{n:02d}" for n in range(1, count + 1)]:
                error("snapshot", f"requirement inventory differs: {cid}")
    if errors:
        return errors

    if not fields(catalog, {"schema_version", "baseline", "owners", "sources", "controls"}):
        return ["osc-schema: invalid catalog fields"]
    if type(catalog["schema_version"]) is not int or catalog["schema_version"] != 1:
        error("schema", "unsupported schema_version")
    if catalog["baseline"] != {"version": snapshot["version"], "released_on": snapshot["released_on"],
                               "snapshot": "baseline-2026.08.28.json"}:
        error("baseline", "catalog and pinned snapshot metadata differ")
    if (not strings(catalog["owners"]) or set(catalog["owners"]) != OWNERS or
            len(catalog["owners"]) != len(OWNERS)):
        error("owner", "owner vocabulary differs from the seven declared fronts and pillars")
    references = catalog["sources"]
    if not isinstance(references, dict) or set(references) != SOURCE_IDS:
        return errors + ["osc-source: expected all authoritative reference sources"]
    coverage = {}
    for sid, source in references.items():
        keys = {"url", "version", "inspected_on"} | ({"items"} if sid != "osps" else set())
        if (not fields(source, keys) or not text(source.get("url")) or
                not source["url"].startswith("https://") or not text(source.get("version")) or
                not day(source.get("inspected_on"))):
            error("source", f"invalid metadata: {sid}")
            continue
        if sid == "osps":
            if source["version"] != snapshot["version"]:
                error("baseline", "OSPS source version differs")
        elif not strings(source.get("items")) or not source["items"] or len(source["items"]) != len(set(source["items"])):
            error("source", f"invalid item inventory: {sid}")
        else:
            coverage.update({(sid, item): 0 for item in source["items"]})
    if not isinstance(catalog["controls"], list) or not catalog["controls"]:
        return errors + ["osc-schema: controls must be a nonempty list"]
    seen, osps_seen = set(), set()
    for control in catalog["controls"]:
        if not isinstance(control, dict):
            error("schema", "control must be an object")
            continue
        cid = control.get("id")
        if not text(cid) or not re.fullmatch(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+", cid):
            error("id", f"invalid control ID: {cid}")
            continue
        if cid in seen:
            error("duplicate", cid)
        seen.add(cid)
        osps = control.get("framework") == "osps"
        keys = {"id", "framework", "title", "owner", "optional", "references", "requirements",
                "measurable_without_provider"} | ({"family"} if osps else set())
        if not fields(control, keys):
            error("schema", f"invalid control fields: {cid}")
        if not isinstance(control.get("owner"), str) or control["owner"] not in OWNERS:
            error("owner", f"exactly one valid scalar owner required: {cid}")
        if (not text(control.get("title")) or not isinstance(control.get("framework"), str) or
                control["framework"] not in {"osps", "supplemental"}):
            error("schema", f"invalid title or framework: {cid}")
        if type(control.get("optional")) is not bool or control["optional"] == osps:
            error("optional", f"OSPS is baseline; supplements are optional: {cid}")
        pinned = expected.get(cid)
        if osps:
            osps_seen.add(cid)
            if pinned is None or control.get("family") != pinned["family"]:
                error("coverage", f"unknown OSPS control or family: {cid}")
        elif cid.startswith("OSPS-"):
            error("coverage", f"OSPS ID cannot be supplemental: {cid}")
        if not isinstance(control.get("references"), list):
            error("reference", f"references must be a list: {cid}")
        else:
            for ref in control["references"]:
                if (not fields(ref, {"source", "item", "relation"}) or
                        not text(ref.get("source")) or not text(ref.get("item")) or
                        ref.get("relation") != "related" or (ref["source"], ref["item"]) not in coverage):
                    error("reference", f"unresolved or overstated reference: {cid}")
                else:
                    coverage[(ref["source"], ref["item"])] += 1
            if not osps and not control["references"]:
                error("reference", f"supplement needs an authoritative source: {cid}")
        requirements = control.get("requirements")
        if not isinstance(requirements, list) or not requirements:
            error("requirement", f"requirements must be a nonempty list: {cid}")
            continue
        identities, actual, active_provider = set(), [], False
        for requirement in requirements:
            if not fields(requirement, {"id", "levels", "state", "provider_required", "evidence"}):
                error("requirement", f"invalid requirement fields: {cid}")
                continue
            rid = requirement["id"]
            if not text(rid) or not re.fullmatch(re.escape(cid) + r"\.\d{2}", rid):
                error("requirement", f"invalid requirement ID: {cid}")
                continue
            if rid in identities:
                error("duplicate", rid)
            identities.add(rid)
            if not levels(requirement["levels"], supplemental=not osps) or (not osps and requirement["levels"]):
                error("levels", rid)
            if (not isinstance(requirement["state"], str) or requirement["state"] not in {"active", "retired"} or
                    (not osps and requirement["state"] != "active")):
                error("state", rid)
            actual.append({key: requirement[key] for key in ("id", "levels", "state")})
            evidence = requirement["evidence"]
            if (not fields(evidence, {"paths", "provider", "assessment", "human_required"}) or
                    not strings(evidence.get("paths")) or not strings(evidence.get("provider")) or
                    not text(evidence.get("assessment")) or type(evidence.get("human_required")) is not bool):
                error("evidence", rid)
                continue
            if any(Path(path).is_absolute() or ".." in Path(path).parts for path in evidence["paths"]):
                error("evidence", f"paths must be repository-relative: {rid}")
            if type(requirement["provider_required"]) is not bool or requirement["provider_required"] != bool(evidence["provider"]):
                error("provider", f"provider flag and evidence disagree: {rid}")
            if requirement["state"] == "active":
                active_provider |= bool(evidence["provider"])
                if not evidence["paths"] and not evidence["provider"]:
                    error("evidence", f"active requirement has no evidence route: {rid}")
            elif evidence["paths"] or evidence["provider"] or evidence["human_required"]:
                error("state", f"retired requirement must not request assessment: {rid}")
        if osps and pinned is not None and actual != pinned["requirements"]:
            error("coverage", f"requirement IDs, states or applicability differ: {cid}")
        if type(control.get("measurable_without_provider")) is not bool or control["measurable_without_provider"] != (not active_provider):
            error("provider", f"control measurement flag disagrees with active requirements: {cid}")
    if osps_seen != set(expected):
        error("coverage", f"OSPS controls differ: missing={sorted(set(expected) - osps_seen)}, extra={sorted(osps_seen - set(expected))}")
    for (sid, item), count in sorted(coverage.items()):
        if count != 1:
            error("reference", f"{sid}:{item} needs one catalog route, found {count}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DATA / "controls.json")
    parser.add_argument("--baseline", type=Path, default=DATA / "baseline-2026.08.28.json")
    args = parser.parse_args()
    try:
        catalog, snapshot = load(args.catalog), load(args.baseline)
    except (OSError, ValueError) as exc:
        print(f"osc-json: {exc}")
        return 1
    errors = check(catalog, snapshot)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"opensource-controls: OK ({len(catalog['controls'])} controls; 41 OSPS; 64 active, 1 retired requirements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
