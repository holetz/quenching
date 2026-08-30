"""Read a coverage result and maintain the proof front's monotonic floor.

This module consumes evidence produced by a target-owned gate. It never invokes pytest or any
other target command. JSON coverage is preferred; a binary `.coverage` database is converted by
coverage's library API when that optional dependency is present, which keeps conversion inside
the read boundary and out of the target's process.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from quenching.proof.config import load_proof_config


FLOOR_VERSION = 1


def _coverage_candidates(config: dict) -> list[Path]:
    root = Path(config["repoRoot"])
    proof_root = Path(config["proofRoot"])
    return [
        root / "coverage.json",
        root / "coverage" / "coverage.json",
        proof_root / "coverage.json",
        root / ".coverage.json",
        root / ".coverage",
    ]


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("coverage artifact must contain a JSON object")
    return value


def _convert_binary(path: Path) -> dict[str, Any]:
    """Convert `.coverage` through coverage's API without launching a target process."""
    try:
        from coverage import Coverage
    except ImportError as exc:
        raise ValueError("binary .coverage requires the coverage package") from exc
    with tempfile.TemporaryDirectory(prefix="quenching-proof-") as directory:
        output = Path(directory) / "coverage.json"
        coverage = Coverage(data_file=str(path))
        coverage.load()
        coverage.json_report(outfile=str(output))
        return _read_json(output)


def read_coverage(config: dict, artifact: str | None = None) -> tuple[dict | None, dict]:
    """Read one existing coverage artifact, returning a refusal when none is usable."""
    candidates = [Path(artifact)] if artifact else _coverage_candidates(config)
    path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if path is None:
        return None, {
            "code": "pf-coverage-missing",
            "exit": 2,
            "message": "no coverage artifact found; run the target's gate before `ratchet`",
            "searched": [str(candidate) for candidate in candidates],
        }
    try:
        payload = (_convert_binary(path) if path.name == ".coverage" else _read_json(path))
    except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
        return None, {
            "code": "pf-coverage-invalid",
            "exit": 2,
            "path": str(path),
            "message": f"coverage artifact cannot be read: {exc}",
        }
    return {"path": str(path), "payload": payload}, {}


def _normalise(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def _percent(summary: dict[str, Any]) -> float | None:
    value = summary.get("percent_covered")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    covered = summary.get("covered_lines")
    statements = summary.get("num_statements")
    if isinstance(covered, (int, float)) and isinstance(statements, (int, float)) and statements:
        return float(covered) * 100 / float(statements)
    return None


def measured_percentages(payload: dict[str, Any], roots: list[dict]) -> tuple[dict[str, float], dict]:
    """Extract one percentage per configured source root from coverage.py JSON."""
    files = payload.get("files")
    totals = payload.get("totals")
    if not isinstance(files, dict) or not isinstance(totals, dict):
        return {}, {"code": "pf-coverage-invalid", "exit": 2,
                    "message": "coverage artifact lacks `files` and `totals`"}

    result: dict[str, float] = {}
    for root in roots:
        declared = root["relative"]
        prefix = declared.rstrip("/") + "/"
        matching = [summary for name, summary in files.items()
                    if isinstance(name, str) and _normalise(name).startswith(prefix)
                    and isinstance(summary, dict)]
        if matching:
            covered = sum(float(item.get("covered_lines", 0)) for item in matching)
            statements = sum(float(item.get("num_statements", 0)) for item in matching)
            if statements:
                result[declared] = covered * 100 / statements
                continue
        total = _percent(totals) if len(roots) == 1 else None
        if total is not None:
            result[declared] = total
    if not result:
        return {}, {"code": "pf-coverage-no-measured-root", "exit": 2,
                    "message": "coverage artifact contains no configured measured root"}
    return result, {}


def _read_floor(path: Path) -> tuple[dict[str, float], dict]:
    if not path.is_file():
        return {}, {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, {"code": "pf-floor-invalid", "exit": 2,
                    "path": str(path), "message": f"ratchet file cannot be read: {exc}"}
    floors = payload.get("floors") if isinstance(payload, dict) else None
    if not isinstance(floors, dict):
        return {}, {"code": "pf-floor-invalid", "exit": 2, "path": str(path),
                    "message": "ratchet file must contain a `floors` object"}
    result = {str(key): float(value) for key, value in floors.items()
              if isinstance(key, str) and isinstance(value, (int, float))
              and not isinstance(value, bool)}
    return result, {}


def _floor_payload(floors: dict[str, float]) -> dict[str, Any]:
    return {"version": FLOOR_VERSION, "floors": {
        key: round(value, 6) for key, value in sorted(floors.items())
    }}


def evaluate(config: dict, *, mode: str, artifact: str | None = None) -> tuple[dict, int]:
    """Evaluate or raise floors; `1` means a run was understood but the gate failed."""
    coverage, err = read_coverage(config, artifact)
    if err:
        return {"ok": False, **err}, 2
    assert coverage is not None
    percentages, err = measured_percentages(coverage["payload"], config["measuredRoots"])
    if err:
        return {"ok": False, **err}, 2
    floor_path = Path(config["ratchetPath"])
    floors, err = _read_floor(floor_path)
    if err:
        return {"ok": False, **err}, 2

    findings: list[dict[str, Any]] = []
    next_floors = dict(floors)
    for root, achieved in sorted(percentages.items()):
        current = floors.get(root)
        if current is None:
            findings.append({"code": "pf-no-floor", "severity": "error",
                             "root": root, "message": f"no floor recorded for `{root}`"})
            if mode == "raise":
                next_floors[root] = achieved
        elif achieved < current:
            findings.append({"code": "pf-floor-regressed", "severity": "error",
                             "root": root, "floor": current, "achieved": achieved,
                             "message": f"coverage for `{root}` fell from {current:.2f}% "
                                        f"to {achieved:.2f}%"})
        elif mode == "raise" and achieved > current:
            next_floors[root] = achieved

    if mode == "raise" and not any(item["code"] == "pf-floor-regressed" for item in findings):
        floor_path.parent.mkdir(parents=True, exist_ok=True)
        floor_path.write_text(json.dumps(_floor_payload(next_floors), indent=2) + "\n",
                              encoding="utf-8")

    return {
        "ok": not findings,
        "mode": mode,
        "coverage": coverage["path"],
        "ratchetPath": str(floor_path),
        "achieved": {key: round(value, 6) for key, value in percentages.items()},
        "floors": _floor_payload(next_floors)["floors"],
        "findings": findings,
    }, 1 if findings else 0
