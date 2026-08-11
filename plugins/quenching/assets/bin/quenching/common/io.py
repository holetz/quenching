"""Reading and writing a whole document — the atomic replace every writer goes
through, and the read that treats an unreadable file as absence.

Moved verbatim out of the pre-refactor specs script."""
from __future__ import annotations

import os
import pathlib


def read_text(path: str) -> str | None:
    try:
        return pathlib.Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def write_text(path: str, text: str) -> None:
    """Replace a file's whole content ATOMICALLY — a reader never sees half a spec.

    Write-then-rename rather than `Path.write_text`, which truncates first: a reader landing in
    the window between the truncate and the write gets an empty or torn document. That window
    is why this is here rather than left alone — `SpecsLock` serialises WRITERS ONLY, and the
    argument for letting readers run unlocked is exactly that a write is never observable
    half-done. `os.replace` is atomic on POSIX and on Windows.

    The temp file is created in the SAME directory, so the rename never crosses a filesystem,
    and carries the pid, so two writers cannot collide on the temp name even where no lock
    covers them (a workspace still in the code tree has no worktree and takes no lock)."""
    p = pathlib.Path(path)
    tmp = p.with_name(f".{p.name}.tmp-{os.getpid()}")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, p)
    finally:
        try:
            tmp.unlink()      # a no-op after a successful replace; cleanup after a failure
        except OSError:
            pass
