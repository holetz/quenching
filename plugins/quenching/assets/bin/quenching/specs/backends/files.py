"""The `files` backend — specs as markdown under the specs workspace.

Moved verbatim out of the pre-refactor specs script."""
from __future__ import annotations

import os

from quenching.common.io import write_text
from quenching.specs.backends.base import SpecBackend
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
        dest_dir = os.path.join(self.root, dest_phase)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, info["file"])
        os.rename(info["path"], dest)
        return dest
