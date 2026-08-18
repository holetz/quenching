"""The `files` backend — specs as markdown under the specs workspace.

Moved verbatim out of the pre-refactor specs script."""
from __future__ import annotations

import os

from quenching.common.io import write_text
from quenching.specs.backends.base import BackendRefusal, SpecBackend
from quenching.specs.parse import load_spec, spec_files


class FilesBackend(SpecBackend):
    """Specs as markdown files under the specs workspace. The reference implementation:
    when the interface and this backend disagree, this backend is right, because it is the
    one whose behaviour every other backend is asserted against."""

    name = "files"

    def __init__(self, root: str) -> None:
        self.root = root

    def list_specs(self, phase: str | None = None) -> list[dict]:
        return spec_files(self.root, phase)

    def read_spec(self, slug: str) -> tuple[dict | None, dict]:
        return load_spec(self.root, slug)

    def write_spec(self, info: dict, text: str) -> None:
        write_text(info["path"], text)

    def create_spec(self, phase: str, filename: str, text: str) -> str:
        dest_dir = os.path.join(self.root, phase)
        os.makedirs(dest_dir, exist_ok=True)
        path = os.path.join(dest_dir, filename)
        write_text(path, text)
        return path

    def move_spec(self, info: dict, dest_phase: str) -> str:
        """The hop, and the only place that knows whether the destination is taken.

        THE OCCUPIED-DESTINATION GUARD LIVES HERE AND NOT IN `cmd_promote`. The shared verb
        built its destination from the DECLARED root — vacuous under an external backend,
        where that path never exists, and wrong under `files` itself whenever the specs
        worktree is in use, because the declared root is not where this backend writes.
        `self.root` is the resolved one, so the check costs a line exactly where the
        information is correct. `os.rename` is silent over an existing file on POSIX, which
        makes the absence of this line a silent overwrite rather than a visible failure."""
        dest_dir = os.path.join(self.root, dest_phase)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, info["file"])
        if os.path.exists(dest):
            rel = f"{dest_phase}/{info['file']}"
            raise BackendRefusal({
                "code": "sp-dest-exists", "exit": 2, "dest": rel,
                "message": f"{rel} already exists — nothing was moved",
            })
        os.rename(info["path"], dest)
        return dest
