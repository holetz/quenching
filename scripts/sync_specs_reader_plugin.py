#!/usr/bin/env python3
"""Generate the payload of `plugins/quenching-specs-reader/` from `plugins/quenching/`.

The reader plugin is one hand-owned command (`commands/read.md`), one hand-owned read-only
entry point (`bin/cq-specs-read`) and its README. Everything it EXECUTES is the `quenching`
package, and that package has exactly one editable source: `plugins/quenching/assets/bin/`.
This script copies only the slice `quenching.specs` imports — `common/` and `specs/` — with
`assets/specs/` (which `quenching/specs/schema.py` finds relative to its own package) and
`assets/portal/` (the read-only portal), and derives `VERSION` and `.claude-plugin/plugin.json` from the source
`VERSION`, so a release never needs to remember the reader.

    --write   rewrite the generated set and delete generated files the source no longer has
    --check   exit 1 and name each drifted path; nothing is written

The generated set is `assets/**`, `VERSION`, `.claude-plugin/plugin.json` and
`.generated-from.json`. Nothing else under the target is read or written.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "plugins/quenching"
TARGET = ROOT / "plugins/quenching-specs-reader"
# `specs` imports only `common` and itself (checked by the lockstep test), so the other pillars
# (design, toolchain, delivery, ...) and the `cq` router stay out: `bin/cq-specs-read` calls
# `quenching.specs.commands.cli` directly and never routes through `cq`.
COPY_DIRS = ("assets/bin/quenching/common", "assets/bin/quenching/specs",
             "assets/specs", "assets/portal")
EXECUTABLE = 0o755
REGULAR = 0o644

DESCRIPTION = (
    "Read-only view of another project's provider-owned quenching specs — one command, "
    "/quenching-specs-reader:read, for a target that must read a specs front without enabling "
    "the full quenching plugin. Generated from plugins/quenching; it never writes the tracker."
)


def _is_build_artefact(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix == ".pyc"


def source_files() -> list[Path]:
    files: list[Path] = []
    for rel in COPY_DIRS:
        files.extend(p for p in sorted((SOURCE / rel).rglob("*"))
                     if p.is_file() and not _is_build_artefact(p))
    return files


def generated_tree() -> dict[str, tuple[bytes, int]]:
    """Every generated path, relative to TARGET, with its bytes and its mode."""
    tree: dict[str, tuple[bytes, int]] = {}
    for path in source_files():
        rel = path.relative_to(SOURCE).as_posix()
        data = path.read_bytes()
        mode = EXECUTABLE if path.stat().st_mode & 0o111 else REGULAR
        tree[rel] = (data, mode)
    version = (SOURCE / "VERSION").read_text(encoding="utf-8").strip()
    source_manifest = json.loads((SOURCE / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    manifest = {
        "name": "quenching-specs-reader",
        "version": version,
        "description": DESCRIPTION,
        "author": source_manifest["author"],
        "license": source_manifest["license"],
        "keywords": ["claude-code", "spec-driven", "backlog", "read-only", "obsidian"],
    }
    tree["VERSION"] = (version.encode() + b"\n", REGULAR)
    tree[".claude-plugin/plugin.json"] = (
        (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode(), REGULAR)
    record = {
        "source": "plugins/quenching",
        "generator": "scripts/sync_specs_reader_plugin.py",
        "copied": list(COPY_DIRS),
    }
    tree[".generated-from.json"] = ((json.dumps(record, indent=2) + "\n").encode(), REGULAR)
    return tree


def existing_generated() -> set[str]:
    found = {p.relative_to(TARGET).as_posix() for p in (TARGET / "assets").rglob("*")
             if p.is_file() and not _is_build_artefact(p)} if (TARGET / "assets").exists() else set()
    for rel in ("VERSION", ".claude-plugin/plugin.json", ".generated-from.json"):
        if (TARGET / rel).is_file():
            found.add(rel)
    return found


def differences(tree: dict[str, tuple[bytes, int]]) -> list[str]:
    drift = []
    for rel, (data, mode) in sorted(tree.items()):
        path = TARGET / rel
        if not path.is_file():
            drift.append(f"missing {rel}")
        elif path.read_bytes() != data:
            drift.append(f"changed {rel}")
        elif bool(path.stat().st_mode & 0o111) != bool(mode & 0o111):
            drift.append(f"mode {rel}")
    drift.extend(f"stale {rel}" for rel in sorted(existing_generated() - tree.keys()))
    return drift


def write(tree: dict[str, tuple[bytes, int]]) -> None:
    for rel in existing_generated() - tree.keys():
        (TARGET / rel).unlink()
    for rel, (data, mode) in tree.items():
        path = TARGET / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file() or path.read_bytes() != data:
            path.write_bytes(data)
        path.chmod(mode)
    for directory in sorted((TARGET / "assets").rglob("*"), reverse=True):
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    tree = generated_tree()
    drift = differences(tree)
    if args.check:
        if drift:
            print("quenching-specs-reader is out of lockstep with plugins/quenching:", file=sys.stderr)
            for line in drift:
                print(f"  {line}", file=sys.stderr)
            print("run: python3 scripts/sync_specs_reader_plugin.py --write", file=sys.stderr)
            return 1
        print(f"quenching-specs-reader in lockstep ({len(tree)} generated files)")
        return 0
    write(tree)
    print(f"quenching-specs-reader regenerated ({len(drift)} paths changed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
