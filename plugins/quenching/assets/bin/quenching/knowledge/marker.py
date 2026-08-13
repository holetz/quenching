"""The dirty marker — the only thing this pillar ever writes (a stamp in tempdir).

Moved verbatim out of the pre-refactor OKF validator script. It is its own module for the same
reason it was its own banner there: the trust note turns on this being the one write, and
a reader auditing that claim should find the whole of it in one file.

`PostToolUse` touches it whenever a `/.knowledge/**` file changes, so the `Stop` sweep knows the
bundle moved this session; a completed scan clears it, and a scan the deadline aborted
keeps it for the next turn.
"""
from __future__ import annotations

import hashlib
import os
import pathlib
import tempfile


def _marker_path(project: str) -> str:
    digest = hashlib.sha1(os.path.abspath(project).encode("utf-8")).hexdigest()[:12]
    return os.path.join(tempfile.gettempdir(), f"okf-dirty-{digest}")


def _touch_marker(project: str) -> None:
    try:
        pathlib.Path(_marker_path(project)).touch()
    except OSError:
        pass  # marker is an optimization; never fail the hook over it


def _clear_marker(project: str) -> None:
    try:
        os.remove(_marker_path(project))
    except OSError:
        pass
