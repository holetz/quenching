"""A spec's identity — the phases, the basename grammar, the files listing, and the
one resolution every backend shares.

Moved verbatim out of the pre-refactor specs script."""
from __future__ import annotations

import os
import re


PHASES = ("plans", "archive")

# v2 folders. READ so an unmigrated workspace keeps working and `migrate` can fold it;
# NEVER written — `new` and `promote` only ever target a folder in PHASES. Reading them
# is not politeness: `list` globs the phase folders, so a workspace this tool refused to
# see would read as EMPTY rather than as out of date, and a skill would conclude there is
# no work when there is.
LEGACY_PHASES = ("backlog", "ready")
PHASE_ALIASES = {"backlog": "plans", "ready": "plans"}
# scan order — a spec's canonical folder before the legacy ones it may still sit in
PHASE_DIRS = ("plans", "backlog", "ready", "archive")


def canonical_phase(folder: str) -> str:
    """The schema phase a folder maps to. `plans` for both v2 definition folders, so
    stage rules, gates and `next` branch on ONE phase and never on where the file
    happens to sit mid-migration."""
    return PHASE_ALIASES.get(folder, folder)


# THE BASENAME IS THE SLUG, and nothing else. It used to carry a `YYYY-MM-DD-` prefix, so the
# identity key and the capture date lived in one string — which meant a store with no filenames
# had to invent one to hold a date, and the `github` marker did exactly that. The date is a
# frontmatter field now (`date:`), in EVERY backend, because no external store carries an honest
# copy of it: an issue's `created_at` is when the issue was made, and a migration makes them all
# on the same day. The citable identity is the bare slug, which is already the only thing a human
# ever typed and the only thing `--spec` ever took.
#
# THE LOOKAHEAD IS LOAD-BEARING. `[a-z0-9]` matches digits, so without it the old
# `2026-07-25-<slug>.md` matches this pattern *whole* and the date is swallowed INTO the
# identity key — measured against this repository's 72 specs, every one of them came back
# slugged `2026-07-25-decide-agents-md-harness-default` with an empty date, and nothing
# reported a thing. Refusing the dated shape turns that silent corruption into the
# `sp-bad-filename` finding it always was. A slug may still begin with digits (`2026-roadmap`);
# only the full date prefix is rejected.
SPEC_FILE_RE = re.compile(r"^(?!\d{4}-\d{2}-\d{2}-)([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
# The pre-date-in-frontmatter basename, read ONLY by the migration folds — which exist precisely
# to recognise a layout this tool no longer writes. Nothing else may match on it: a file still
# named this way is a `sp-bad-filename` finding, not a second supported form.
LEGACY_DATED_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def titleize(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.replace("_", "-").split("-") if w)


def spec_files(root: str, phase: str | None = None) -> list[dict]:
    """Every conformant spec file across the phase folders, oldest first within each.

    Each row carries BOTH `folder` (where the file actually is, so every message names a
    real path) and `phase` (what it means, so a v2 file in `backlog/` derives exactly like
    a v3 file in `plans/`). Passing `phase` filters on the canonical phase, so
    `phase="plans"` sweeps up the legacy folders too.

    A file whose name does not match `<slug>.md` is NOT returned — it is a finding for
    `validate`/`doctor` to report, not something to silently half-support.

    The rows are in BASENAME order, which is slug order. It used to be date order, for free,
    because the date led the basename; ordering by date now would mean opening every file to
    read its frontmatter, and the one caller that ranks by date — `_next_front` — already
    reads each document and sorts on `info["date"]` itself."""
    out: list[dict] = []
    for folder in PHASE_DIRS:
        ph = canonical_phase(folder)
        if phase and ph != phase:
            continue
        d = os.path.join(root, folder)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            m = SPEC_FILE_RE.match(name)
            if not m:
                continue
            out.append({
                "phase": ph,
                "folder": folder,
                "legacy": folder in LEGACY_PHASES,
                "file": name,
                "path": os.path.join(d, name),
                "slug": m.group(1),
            })
    return out


def resolve_one(specs: list[dict], spec_id: str | int) -> tuple[dict | None, dict]:
    """Pick one spec descriptor out of a listing by its provider-native ID."""
    spec = next((s for s in specs if str(s["id"]) == str(spec_id)), None)
    if spec is not None:
        return spec, {}
    return None, {"code": "sp-unknown-id", "exit": 1, "id": spec_id,
                  "message": f"no spec with id '{spec_id}'"}
