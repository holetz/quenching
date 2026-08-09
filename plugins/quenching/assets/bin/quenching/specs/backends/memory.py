"""The `memory` backend — specs in a dict, the other side of the equivalence check.

Moved verbatim out of `specs.py`."""
from __future__ import annotations

from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.backends.base import SpecBackend
from quenching.specs.parse import PHASES, SPEC_FILE_RE, derive_info, resolve_one


class MemoryBackend(SpecBackend):
    """Specs in a dict. No disk, no network, no repository to stage.

    This exists to be the OTHER side of the selftest's equality: the canonical case list runs
    against `files` and against this, and the two must agree. A backend that shares nothing
    with the filesystem but the interface is the only honest way to prove the interface is
    what the CLI depends on — if a command reaches around it to a path, this backend is where
    that shows up, immediately and without a fixture.

    It is deliberately NOT a cache and never reachable from the config: nothing a human can
    declare selects it, because a store that forgets on exit must never be somewhere real
    work can land."""

    name = "memory"

    def __init__(self) -> None:
        # slug -> (phase, filename, document). The filename is stored rather than rebuilt
        # from the slug so that this backend can hand back exactly what it was given, the
        # way a filesystem does. It no longer carries the capture date: that moved into the
        # document's `date:`, which every backend reads through the one derivation — the
        # divergence the equality check caught here was a backend RECOMPUTING the date, and
        # the fix was to stop having a second place able to compute it at all.
        self.docs: dict[str, tuple[str, str, str]] = {}

    def _descriptor(self, slug: str) -> dict:
        # The SAME key set `spec_files` returns, and nothing more. An extra key here would
        # be a field some command could come to depend on and that the files backend would
        # then not have.
        phase, filename, _ = self.docs[slug]
        m = SPEC_FILE_RE.match(filename)
        return {"phase": phase, "folder": phase, "legacy": False, "file": filename,
                "path": f"memory://{phase}/{filename}",
                "slug": m.group(1) if m else slug}

    def list_specs(self, phase: str | None = None) -> list[dict]:
        rows = [self._descriptor(s) for s in self.docs
                if phase is None or self.docs[s][0] == phase]
        return sorted(rows, key=lambda r: (PHASES.index(r["phase"]), r["file"]))

    def read_spec(self, slug: str) -> tuple[dict | None, dict]:
        spec, err = resolve_one(self.list_specs(), slug, lambda: {
            k: str(parse_frontmatter(d[2]).get("title", "")) for k, d in self.docs.items()})
        if err:
            return None, err
        return derive_info(spec, self.docs[spec["slug"]][2]), {}

    def write_spec(self, info: dict, text: str) -> None:
        phase, filename, _ = self.docs[info["slug"]]
        self.docs[info["slug"]] = (phase, filename, text)

    def create_spec(self, phase: str, filename: str, text: str) -> str:
        m = SPEC_FILE_RE.match(filename)
        slug = m.group(1) if m else filename
        self.docs[slug] = (phase, filename, text)
        return f"memory://{phase}/{filename}"

    def move_spec(self, info: dict, dest_phase: str) -> str:
        _, filename, text = self.docs[info["slug"]]
        self.docs[info["slug"]] = (dest_phase, filename, text)
        return f"memory://{dest_phase}/{filename}"
