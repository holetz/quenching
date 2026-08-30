"""Read-only conformance checks for the design front."""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

from quenching.design.build import GENERATED_PATHS, build_drift, compute_build
from quenching.design.model import (
    DesignError,
    color_to_css,
    font_asset_paths,
    font_metadata,
    quenching_extension,
    read_json,
    resolve_token,
    resolve_value,
    token_map,
    validate_source,
)


def inspect_design(root: Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    root = root.resolve()
    design_root = root / ".design"
    token_path = design_root / "tokens.json"
    findings: list[dict[str, str]] = []
    payload: dict[str, Any] = {
        "root": str(root),
        "installed": token_path.is_file(),
        "generated": list(GENERATED_PATHS),
        "webDetector": _web_detector(root),
    }
    if not token_path.is_file():
        findings.append({
            "severity": "error", "code": "design-front-absent", "path": ".design/tokens.json",
            "message": "design front is not installed; run `/quenching:design:align`",
        })
        return payload, findings
    try:
        source = read_json(token_path)
    except DesignError as exc:
        findings.append({
            "severity": "error", "code": "design-source-unreadable", "path": ".design/tokens.json",
            "message": str(exc),
        })
        return payload, findings
    try:
        extension = quenching_extension(source)
        payload.update({
            "schema": source.get("$schema"),
            "tokenCount": len(token_map(source)),
            "designMdVersion": extension.get("designMd", {}).get("version"),
            "productSchema": extension.get("productSchema"),
        })
    except DesignError:
        # `validate_source` below owns the actionable shape finding; status should
        # still return a stable payload when the source is malformed.
        payload.update({"schema": source.get("$schema"), "tokenCount": 0})
    findings.extend(validate_source(source))
    if not findings:
        try:
            result = compute_build(root)
        except DesignError as exc:
            findings.append({
                "severity": "error", "code": "design-build-refusal", "path": ".design/tokens.json",
                "message": str(exc),
            })
        else:
            payload["sources"] = list(result.sources)
            findings.extend(build_drift(result))
    sidecar_path = root / ".impeccable" / "design.json"
    try:
        sidecar = read_json(sidecar_path)
    except DesignError:
        sidecar = None
    if sidecar is not None:
        payload["sidecarSchemaVersion"] = sidecar.get("schemaVersion")
        payload["sidecarComponentCount"] = len(sidecar.get("components", [])) if isinstance(sidecar.get("components"), list) else 0
    findings.extend(_orphan_assets(root))
    findings.extend(_non_web_literals(root, source))
    findings.extend(_font_findings(root, source))
    return payload, sorted(findings, key=lambda item: (item["severity"] != "error", item["path"], item["code"]))


def status_payload(root: Path) -> dict[str, Any]:
    payload, findings = inspect_design(root)
    errors = sum(item["severity"] == "error" for item in findings)
    warnings = len(findings) - errors
    payload.update({
        "ok": errors == 0,
        "errors": errors,
        "warnings": warnings,
        "findings": findings,
    })
    genres = root / ".design" / "genres"
    payload["genres"] = sorted(path.stem for path in genres.glob("*.md")) if genres.is_dir() else []
    return payload


def _orphan_assets(root: Path) -> list[dict[str, str]]:
    assets = root / ".design" / "assets"
    if not assets.is_dir():
        return []
    searchable: list[str] = []
    for base in (root / ".design", root / "docs" / "standards" / "design"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or assets == path.parent or ".design/build" in path.as_posix():
                continue
            try:
                searchable.append(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                continue
    haystack = "\n".join(searchable)
    findings = []
    for asset in sorted(path for path in assets.rglob("*") if path.is_file()):
        if asset.name == ".gitkeep" or asset.name.lower().startswith(("readme", "license", "ofl")):
            continue
        relative = asset.relative_to(root).as_posix()
        design_relative = asset.relative_to(root / ".design").as_posix()
        if relative not in haystack and design_relative not in haystack and asset.name not in haystack:
            findings.append({
                "severity": "warning", "code": "design-asset-orphan", "path": relative,
                "message": "asset is not referenced by tokens, design standards, genres, or media primitives",
            })
    return findings


def _font_findings(root: Path, source: dict[str, Any]) -> list[dict[str, str]]:
    """Check declared font assets without making unannotated legacy fonts invalid."""
    records = token_map(source)
    declarations: dict[str, tuple[Any, dict[str, Any]]] = {}
    try:
        paths_by_token = font_asset_paths(source, root / ".design" / "assets")
    except DesignError as exc:
        return [{"severity": "error", "code": "design-font-metadata",
                 "path": ".design/tokens.json", "message": str(exc)}]
    for token in records.values():
        if token.type != "fontFamily":
            continue
        metadata = font_metadata(token)
        if metadata:
            declarations[token.dotted] = (token, metadata)
    if not declarations:
        return []
    by_family: dict[str, tuple[Any, dict[str, Any]]] = {}
    for token, metadata in declarations.values():
        try:
            value = resolve_value(token.value, records, (token.dotted,))
        except DesignError:
            continue
        names = value if isinstance(value, list) else [value]
        for name in names:
            if isinstance(name, str):
                by_family[name.casefold()] = (token, metadata)
    findings: list[dict[str, str]] = []
    for token in records.values():
        if token.type != "typography":
            continue
        try:
            value = resolve_value(token.value, records, (token.dotted,))
        except DesignError:
            continue
        family = value.get("fontFamily") if isinstance(value, dict) else None
        names = family if isinstance(family, list) else [family]
        for name in names:
            declaration = by_family.get(name.casefold()) if isinstance(name, str) else None
            if not declaration:
                continue
            font_token, metadata = declaration
            if metadata.get("source") == "webfont":
                continue
            paths = font_asset_paths(source, root / ".design" / "assets").get(font_token.dotted, [])
            missing = [path for path in paths if not path.exists()]
            if missing or not paths:
                detail = ", ".join(str(path.relative_to(root)) for path in missing) or "no files or directories"
                findings.append({
                    "severity": "error", "code": "design-font-unresolved",
                    "path": f".design/tokens.json#{token.dotted}",
                    "message": f"font family {name!r} has no resolvable declared asset: {detail}",
                })
    return findings


def _web_detector(root: Path) -> dict[str, Any]:
    """Report optional Impeccable availability without installing or executing it."""
    candidates = []
    resolved = shutil.which("impeccable")
    if resolved:
        candidates.append(Path(resolved))
    candidates.extend([
        root / "node_modules" / ".bin" / "impeccable",
        root / ".impeccable" / "node_modules" / ".bin" / "impeccable",
    ])
    for candidate in candidates:
        if candidate.is_file() and (candidate.is_absolute() or candidate.exists()):
            return {"name": "impeccable", "state": "available", "path": str(candidate)}
    return {
        "name": "impeccable",
        "state": "skipped",
        "reason": "optional detector is not installed; run it only when it already resolves locally",
    }


def _non_web_literals(root: Path, source: dict[str, Any]) -> list[dict[str, str]]:
    """Detect manual color literals in non-web sources; Impeccable owns web drift."""
    literals: dict[str, str] = {}
    try:
        records = token_map(source)
        for token in records.values():
            if token.type != "color":
                continue
            value = color_to_css(resolve_token(token, records))
            if value.startswith("#"):
                literals[value.lower()] = token.dotted
    except DesignError:
        return []
    findings: list[dict[str, str]] = []
    media = root / ".design" / "media"
    if not media.is_dir():
        return findings
    for path in sorted(media.rglob("*")):
        if not path.is_file() or path.suffix.lower() in {".css", ".html", ".htm", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8").lower()
        except (OSError, UnicodeDecodeError):
            continue
        for literal, token_name in literals.items():
            if re.search(rf"(?<![0-9a-f]){re.escape(literal)}(?![0-9a-f])", text):
                findings.append({
                    "severity": "error", "code": "design-nonweb-literal",
                    "path": path.relative_to(root).as_posix(),
                    "message": f"non-web primitive repeats {literal} from {token_name}; import the generated adapter instead",
                })
    return findings
