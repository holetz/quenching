"""The spec backend interface, and the refusal an external backend carries to the CLI.

Moved verbatim out of the pre-refactor specs script. `BackendRefusal` travels with the interface rather than with
`github`, where it used to sit: both external backends raise it, and neither may import the
other."""
from __future__ import annotations


class SpecBackend:
    """Where a repo's specs actually live. One implementation per target; every command
    above talks to this and never to a path.

    THE INTERFACE IS THE DOCUMENT, NOT THE VERBS. `status`, `show`, `section`, `task`,
    `discover`, `promote` and `validate` are shared code layered on the five primitives
    below — they are not methods each backend reimplements. That is what makes "every
    backend behaves identically" provable by construction rather than by hoping three
    parsers agree: the canonical markdown document is the contract, the derivation of
    stages, gates, records and tasks happens once, and a backend's only job is to produce
    that document and to store it again.

    A backend is therefore free to serialise natively — `## Tasks` as sub-issues, sections
    as fields — provided it reassembles the canonical document on read. The hybrid
    serialisation lives inside each external implementation, exactly where it belongs, and
    it can never drift the JSON the CLI prints.

    Granular reading is unaffected by this split, because the cost it addresses is the
    agent's context and not I/O: `section` hands back the headings asked for whether or not
    the backend had to fetch the whole document to find them."""

    name = "abstract"

    def list_specs(self, phase: str | None = None) -> list[dict]:
        """Every spec descriptor, oldest first within each phase."""
        raise NotImplementedError

    def read_spec(self, spec_id: str | int) -> tuple[dict | None, dict]:
        """`(info, err)` — the canonical document plus everything derived from it, or a
        ready-to-emit refusal. Never raises for an unknown ID."""
        raise NotImplementedError

    def write_spec(self, info: dict, text: str) -> None:
        """Replace one spec's whole document with `text`."""
        raise NotImplementedError

    def create_spec(self, phase: str, text: str) -> str:
        """Store a new spec and return the locator a report can show a human."""
        raise NotImplementedError

    def move_spec(self, info: dict, dest_phase: str) -> str:
        """The one lifecycle hop — `plans/` to `archive/` — returning the new locator."""
        raise NotImplementedError

    # There is no `reconcile_labels` hook here, and the absence is deliberate. One existed
    # briefly — a no-op on the base class, meant for an external backend to override — and
    # nothing ever called it or overrode it, because the reconciliation belongs INSIDE
    # `write_spec`: it has to ride the store call's own request to satisfy the "costs zero
    # calls beyond the write already being made" condition
    # (/.knowledge/standards/architecture/spec-backend.md §Rendering derived state). A hook that
    # every implementer must fold into `write_spec` anyway is a sixth primitive that does
    # nothing, and this interface stays five.


class BackendRefusal(Exception):
    """An external backend's call that failed, carried to the CLI boundary as a
    ready-to-emit refusal. Shared by `github` and `azure-boards`.

    THREE OF THE FIVE PRIMITIVES RETURN A LOCATOR AND NOT `(value, err)` — `write_spec`,
    `create_spec` and `move_spec` were shaped around a backend that cannot fail halfway.
    A network target can, and the contract is "never a traceback", so the failure travels
    as an exception carrying the refusal already built and is converted exactly once, in
    `main`. Widening the interface instead would make every backend and every command pay,
    in every signature, for a failure mode only the external backends have."""

    def __init__(self, err: dict) -> None:
        super().__init__(err.get("message", "the backend failed"))
        self.err = err
