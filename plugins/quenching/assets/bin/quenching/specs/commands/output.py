"""The specs pillar's output layer — the resolution receipt, and the two doors that carry it.

`common/output.py` owns the exit-code contract and the two renderings; what stays here is the
half that is the PILLAR's and not every pillar's — how a slug was reached, and a locator printed
the way a report should print it. The receipt rides out through the `prefix` parameter
`common.output.emit` takes for exactly this.

The doors are methods on `Emitter` rather than module functions: the receipt is one invocation's
answer, and an invocation is what the object is scoped to.
"""
from __future__ import annotations

from quenching.common.output import emit as _emit
from quenching.specs.backends.base import SpecBackend
from quenching.specs.config import load_config


def front_fields(root: str) -> dict:
    """`{"backend": …, "root": …}` — the two fields a workspace-wide payload opens with.

    ONE HELPER FOR TEN EMIT SITES, because the field was wrong at all ten in the same way and
    a fix applied ten times is a fix nine of which can rot. External backends have no local
    document root, so `root` is always `null` and the backend name says which remote owns the
    canonical document.

    THE KEY IS NOT RENAMED. `root` stays `root`: the swept consumers read it as a locator to
    show, never to compose a path from, so correcting the value is additive while renaming the
    key would break every installed target for nothing.

    `null` rather than the empty string, and rather than the declared path: an empty string
    makes every consumer invent its own vacuity test, and the declared path is the lie itself.
    `None` is the one value nobody can mistake for a directory."""
    cfg = load_config(root)
    return {"backend": cfg["backend"], "root": None}


def display_locator(locator: str, root: str) -> str:
    """A backend's locator as a report should print it.

    `path` is the backend locator a human can follow. External backends return an issue or work
    item URL, so it is printed exactly as the backend gave it; no local path is composed here."""
    return locator


class Emitter:
    """The two doors of ONE invocation, carrying that invocation's resolution receipt.

    Every verb is handed one of these and emits through it, so the receipt rides out on every
    payload BY CONSTRUCTION — a verb added tomorrow announces an approximate match without its
    author knowing the rule exists, because the emitter arrives in the signature and there is no
    other way to answer. The alternative, writing the two keys into each verb's payload by hand,
    is the shape /.knowledge/standards/architecture/shared-mold-keys.md measured and rejected: a rule
    that depends on the author remembering is a rule the next author forgets, and the count of
    verbs owing it moved three times while this was being specified.

    ONE COMMAND, ONE RESOLUTION — held by lifetime rather than by discipline. The receipt used
    to live in a module global that `main` had to blank before dispatching, so a process that
    dispatches twice would carry one command's receipt onto the next one's payload the moment
    anyone forgot the reset. This object is built in `main` and dropped when the call returns,
    which is the same guarantee with nothing left to remember."""

    def __init__(self) -> None:
        # How THIS command reached its spec, or None where it resolved no slug of its own.
        self.resolution: dict | None = None

    def resolved(self, info: dict) -> None:
        """Record HOW this invocation reached its spec. `read_one` is the only caller."""
        self.resolution = {"resolvedBy": info.get("resolvedBy"),
                           "resolvedFrom": info.get("resolvedFrom")}

    def announced(self, obj: dict) -> dict:
        """`obj` carrying the receipt, where this command resolved a slug at all.

        Both keys, always — `resolvedBy: null` on the exact path — so a caller reads
        `payload["resolvedBy"]` without testing for presence first. A verb that resolves no
        spec (`config`, `doctor`, `validate`) gets neither: a null answer to a question nobody
        asked is noise, not information."""
        return {**obj, **self.resolution} if self.resolution else obj

    def receipt_line(self) -> str:
        """The same receipt for a human reader — empty unless the slug was reached inexactly.

        A receipt only the `--json` reader gets is half a receipt: the human running the verb
        by hand is exactly the one who mistyped the slug."""
        if not self.resolution or self.resolution["resolvedBy"] is None:
            return ""
        return (f"resolved by {self.resolution['resolvedBy']}, "
                f"from {self.resolution['resolvedFrom']!r}\n")

    def emit(self, as_json: bool, obj: dict, human: str) -> None:
        _emit(as_json, self.announced(obj), human, self.receipt_line())

    def emit_err(self, as_json: bool, err: dict) -> int:
        self.emit(as_json, {"ok": False, **{k: v for k, v in err.items() if k != "exit"}},
                  f"error: {err['message']}")
        return err.get("exit", 1)


def read_one(backend: SpecBackend, slug: str, out: Emitter) -> tuple[dict | None, dict]:
    """Resolve the slug a human typed, recording HOW it was reached on the emitter.

    The single entry every verb takes into resolution — which is what makes the receipt a
    property of the layer rather than an obligation on each verb. Only the human's own
    argument comes through here: a loop already walking a listing resolves slugs it just read
    itself, and a receipt for those would be a receipt for nothing.

    `resolve_one` stays pure over the listing. That purity is what makes "every backend
    resolves the same way and gets the same refusals" a property instead of a claim, and a
    side effect down there would spend it to buy what this layer already gives."""
    info, err = backend.read_spec(slug)
    if err:
        return None, err
    out.resolved(info)
    return info, {}
