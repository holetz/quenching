"""The specs pillar's output layer — the resolution receipt, and the two doors that carry it.

Moved verbatim out of `specs.py`'s `# output` block. `common/output.py` owns the exit-code
contract and the two renderings; what stays here is the half that is the PILLAR's and not every
pillar's — how a slug was reached, and a locator printed the way a report should print it. The
receipt rides out through the `prefix` parameter `common.output.emit` takes for exactly this.
"""
from __future__ import annotations

import os

from quenching.common.output import emit as _emit
from quenching.specs.backends.base import SpecBackend


def display_locator(locator: str, root: str) -> str:
    """A backend's locator as a report should print it.

    `path` is the ONE field the backends are allowed to differ on — a filesystem path for
    `files`, an issue URL for `github` — and only one of the two is a path. Making a URL
    relative to the workspace produces a string that is neither, and that no reader can
    follow: `../../../https:/github.com/o/r/issues/2`. A remote locator is already the
    address a human would open, so it is printed exactly as the backend gave it."""
    if "://" in locator:
        return locator
    return os.path.relpath(locator, os.path.dirname(root)).replace(os.sep, "/")


# How THIS command reached its spec, or None where it resolved no slug of its own. Written by
# `read_one` and read by `emit`, so the receipt rides out on every payload by construction — a
# verb added tomorrow announces an approximate match without its author knowing the rule exists.
# The alternative, writing the two keys into each verb's payload by hand, is the shape
# /.docs/standards/architecture/shared-mold-keys.md measured and rejected: a rule that depends on
# the author remembering is a rule the next author forgets, and the count of verbs owing it moved
# three times while this was being specified.
_RESOLUTION: dict | None = None


def read_one(backend: SpecBackend, slug: str) -> tuple[dict | None, dict]:
    """Resolve the slug a human typed, and record HOW it was reached.

    The single entry every verb takes into resolution — which is what makes the receipt a
    property of the layer rather than an obligation on each verb. Only the human's own
    argument comes through here: a loop already walking a listing resolves slugs it just read
    itself, and a receipt for those would be a receipt for nothing.

    `resolve_one` stays pure over the listing. That purity is what makes "every backend
    resolves the same way and gets the same refusals" a property instead of a claim, and a
    side effect down there would spend it to buy what this layer already gives."""
    global _RESOLUTION
    info, err = backend.read_spec(slug)
    if err:
        return None, err
    _RESOLUTION = {"resolvedBy": info.get("resolvedBy"),
                   "resolvedFrom": info.get("resolvedFrom")}
    return info, {}


def announced(obj: dict) -> dict:
    """`obj` carrying the receipt, where this command resolved a slug at all.

    Both keys, always — `resolvedBy: null` on the exact path — so a caller reads
    `payload["resolvedBy"]` without testing for presence first. A verb that resolves no spec
    (`config`, `doctor`, `validate`) gets neither: a null answer to a question nobody asked is
    noise, not information."""
    return {**obj, **_RESOLUTION} if _RESOLUTION else obj


def receipt_line() -> str:
    """The same receipt for a human reader — empty unless the slug was reached inexactly.

    A receipt only the `--json` reader gets is half a receipt: the human running the verb by
    hand is exactly the one who mistyped the slug."""
    if not _RESOLUTION or _RESOLUTION["resolvedBy"] is None:
        return ""
    return (f"resolved by {_RESOLUTION['resolvedBy']}, "
            f"from {_RESOLUTION['resolvedFrom']!r}\n")


def emit(as_json: bool, obj: dict, human: str) -> None:
    _emit(as_json, announced(obj), human, receipt_line())


def emit_err(as_json: bool, err: dict) -> int:
    emit(as_json, {"ok": False, **{k: v for k, v in err.items() if k != "exit"}},
         f"error: {err['message']}")
    return err.get("exit", 1)


def reset_resolution() -> None:
    """One command, one resolution — called by `main` before it dispatches.

    `main` no longer shares a module with the global, so the `global` statement that reset it
    lives here, next to the one that writes it. The global itself is unchanged and is still
    task 3.5's to remove."""
    global _RESOLUTION
    _RESOLUTION = None
