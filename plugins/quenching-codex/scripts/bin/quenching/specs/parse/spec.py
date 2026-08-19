"""A spec's identity — the phases, the basename grammar, the files listing, and the
one resolution every backend shares.

Moved verbatim out of the pre-refactor specs script."""
from __future__ import annotations

import difflib
import os
import re
import unicodedata


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


# How close a slug or title has to be before it resolves at all. Tuned to accept a TYPO —
# `evaluate-spec-creation-flo` scores 0.98 against its slug — while refusing a merely adjacent
# spec: `0.62` matched `decide-plan-quick-skill` against `decide-sp-unrefined-severity` on this
# repository's own listing, which is not a near miss, it is a different spec.
#
# A COPIED FRAGMENT DOES NOT RESOLVE, and that is a property of the metric rather than of this
# number. `SequenceMatcher.ratio()` is 2·M/(len(a)+len(b)), so a fragment's score is capped at
# 2·len(fragment)/(len(fragment)+len(title)) no matter how perfectly it appears inside the
# title: `fluxo de criação de specs` scores 0.5618 against the 62-character title it was copied
# out of, and nothing shorter than ~60% of a title can clear 0.75 at all. Lowering the number
# would not buy the fragment rung — it would only start matching adjacent specs, which is the
# failure this threshold exists to prevent. Resolving a fragment needs a containment metric on
# the title rung, which is a different design and is left to its own spec.
FUZZY_MATCH_THRESHOLD = 0.75


def _norm(text: str) -> str:
    """Case, accents and runs of whitespace folded away — the form both sides of a title
    comparison are reduced to, so `Criação` and `criacao ` are the same string."""
    folded = unicodedata.normalize("NFD", " ".join((text or "").split()).lower())
    return "".join(c for c in folded if not unicodedata.combining(c))


def resolve_one(specs: list[dict], slug: str,
                titles: dict | None = None) -> tuple[dict | None, dict]:
    """Pick one spec descriptor out of a listing, by slug and then by title.

    Pure over the listing, so every backend resolves the same way and gets the same refusals
    — an ambiguous slug is exit 2 whether the duplicates are two files or two issues. THE
    TOLERANCE LIVES HERE AND NOWHERE ELSE, for that same reason.

    Four rungs, tried in order and stopping at the first that answers:

      1. the exact slug          the only path that costs anything today
      2. the exact title         normalised for case, accents and whitespace
      3. the closest slug OR title above the threshold, if exactly ONE clears it
      4. nothing                 `sp-unknown-slug`, exit 1

    TWO MATCHES IS STILL A REFUSAL at every rung — never a guess, and the refusal names the
    candidates so the human picks. A rung-3 answer is announced: the descriptor comes back
    carrying `resolvedBy: "approximate"` and what it matched, because a command that silently
    acted on a spec the human did not name is worse than one that asked.

    `titles` is `{slug: title}`, or a callable returning one. It is consulted ONLY after the
    exact slug misses, so the common path never pays to build it. External backends provide
    their title index directly, without a local file walk."""
    matches = [s for s in specs if s["slug"] == slug]
    if len(matches) > 1:
        return None, _ambiguous(slug, matches, "slug")
    if matches:
        return matches[0], {}

    index = (titles() if callable(titles) else titles) or {}
    want = _norm(slug)

    exact = [s for s in specs if _norm(index.get(s["slug"], "")) == want]
    if len(exact) > 1:
        return None, _ambiguous(slug, exact, "title")
    if exact:
        return dict(exact[0], resolvedBy="title",
                    resolvedFrom=index.get(exact[0]["slug"], "")), {}

    scored = []
    for s in specs:
        ratio = max(
            difflib.SequenceMatcher(None, want, _norm(s["slug"])).ratio(),
            difflib.SequenceMatcher(None, want, _norm(index.get(s["slug"], ""))).ratio()
            if index.get(s["slug"]) else 0.0)
        if ratio >= FUZZY_MATCH_THRESHOLD:
            scored.append((ratio, s))
    if len(scored) > 1:
        best = max(r for r, _ in scored)
        tied = [s for r, s in scored if r == best]
        # A single clear winner among several that merely cleared the bar still resolves;
        # what refuses is a genuine tie, where picking either one would be a coin flip.
        if len(tied) > 1:
            return None, _ambiguous(slug, tied, "approximate")
        return dict(tied[0], resolvedBy="approximate",
                    resolvedFrom=index.get(tied[0]["slug"], "") or tied[0]["slug"]), {}
    if scored:
        s = scored[0][1]
        return dict(s, resolvedBy="approximate",
                    resolvedFrom=index.get(s["slug"], "") or s["slug"]), {}

    return None, {"code": "sp-unknown-slug", "exit": 1, "slug": slug,
                  "message": f"no spec with slug '{slug}'"}


def _ambiguous(slug: str, matches: list[dict], rung: str) -> dict:
    """The one refusal every rung of `resolve_one` shares — exit 2, with the candidates
    named. `rung` says WHICH comparison tied, because "two specs share a slug" and "your
    fragment is close to two titles" are fixed by different things."""
    where = [f"{m['phase']}/{m['file']}" for m in matches]
    return {
        "code": "sp-ambiguous-slug", "exit": 2, "slug": slug, "matchedOn": rung,
        "matches": where,
        "message": f"'{slug}' matches {len(matches)} specs by {rung} — {', '.join(where)}",
    }
