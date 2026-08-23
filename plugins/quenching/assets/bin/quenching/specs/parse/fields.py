"""The frontmatter writers — one key, one record, the state fields a native surface
stores instead, and the legacy dated-basename fold.

Moved verbatim out of the pre-refactor specs script."""
from __future__ import annotations

import re

from quenching.common.frontmatter import parse_frontmatter
# The pre-date-in-frontmatter basename, read ONLY by the migration fold below — which
# exists precisely to recognise a layout this tool no longer writes. It moved here from
# `parse/spec.py` with the rest of the basename grammar's retirement: this is the one use
# left, and a pattern with one caller belongs beside it.
LEGACY_DATED_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")


def set_frontmatter_key(text: str, key: str, value: str,
                        after: str | None = None) -> str:
    """Set one top-level frontmatter key, preserving every other line as authored.

    Rewriting the block wholesale would reformat a human's `refined: {mode, date}` and
    reorder their keys — a promote is a move, and the outcome stamp is the ONLY content it
    is allowed to write.

    `after` places a key that does not exist yet directly below a named one, instead of at
    the end of the block. It exists for `date`, which the marker fold inserts into documents
    written before the field did: appended, it would land under `verification` and every
    migrated spec would read in a different order from every freshly captured one, for no
    reason a reader could see. An absent `after` key falls back to the end."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return f"---\n{key}: {value}\n---\n\n" + text
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        return text
    for i in range(1, close):
        if lines[i].split(":", 1)[0].strip() == key:
            lines[i] = f"{key}: {value}\n"
            return "".join(lines)
    at = close
    if after:
        for i in range(1, close):
            if lines[i].split(":", 1)[0].strip() == after:
                at = i + 1
                break
    lines.insert(at, f"{key}: {value}\n")
    return "".join(lines)


def strip_frontmatter_keys(text: str, keys: tuple[str, ...]) -> str:
    """`text` with each of `keys`' own frontmatter line removed — the WRITE half of
    `## Design` §Armazenado não é projetado for `tags`/`assignee`/`start`/`target`: the
    native field is the storage, so the document stored alongside it never carries a second,
    unread copy that would go stale the instant a human edited the tracker instead.

    Unlike `hybrid_title_split`, this never refuses. `title` is required and paired with a
    `# <TITLE>` heading it has to reproduce at an exact offset; these four are optional
    scalars/lists with no second copy elsewhere in the document, so dropping the line is the
    whole operation — nothing to reconstruct on the way back, because `read_spec` reassembles
    the VALUES into `info['frontmatter']` directly rather than rebuilding the text."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        return text
    kept = [ln for i, ln in enumerate(lines)
           if not (1 <= i < close and ln.split(":", 1)[0].strip() in keys)]
    return "".join(kept)


def carry_forward_fields(old_fm: dict, new_fm: dict, keys: tuple[str, ...]) -> dict:
    """`keys`, from `new_fm` where THIS WRITE's own text declared one explicitly, and from
    `old_fm` (the pre-write read) where it did not.

    THE BUG THIS FIXES: a key `strip_frontmatter_keys` removes is gone from the document
    once stored, so an ORDINARY write — editing a section, ticking a task — hands
    `write_spec` text that never mentions `tags` at all. Reading that absence as "clear the
    tags" would wipe every stored field on the next unrelated write. Presence in `new_fm` is
    the signal an explicit `cmd_field`/`--subject` write leaves behind — `set_frontmatter_key`
    inserts the line it is asked to set — so presence, not truthiness, is what is asked
    (`tags: []` is a real instruction to clear; the key being ABSENT is silence)."""
    return {k: new_fm[k] if k in new_fm else old_fm.get(k) for k in keys}


def legacy_marker_fold(filename: str, text: str) -> tuple[str, str] | None:
    """`("<slug>.md", the document carrying its own `date:`)` for a spec still stored under
    the dated basename — or None when there is nothing to fold.

    THE PREFIX IS THE ONLY COPY OF THE DATE. A document written before `date:` existed keeps
    its capture date nowhere but that basename, so the fold has to move it into the
    frontmatter in the SAME step that drops it. Dropping first loses the fact; adding first
    and dropping later leaves two copies free to disagree in between. One function, both
    halves, so no caller can perform half of it.

    A document that already declares `date:` keeps its own — only the name was stale. The
    basename's copy is never allowed to win, because a human may have corrected the field and
    nobody ever renames an issue's marker to correct a date."""
    m = LEGACY_DATED_FILE_RE.match(filename)
    if not m:
        return None
    date, slug = m.group(1), m.group(2)
    if str(parse_frontmatter(text).get("date", "")).strip():
        return f"{slug}.md", text
    return f"{slug}.md", set_frontmatter_key(text, "date", date, after="title")


def _render_record(key: str, rec: dict) -> list[str]:
    """A record as frontmatter lines — flow where flow survives a round trip, block where
    it would not. A value carrying a comma cannot go in `{a: b, c: d}`, which
    `parse_frontmatter` splits on commas; a long one wraps in an editor and stops parsing
    as one line. Both are the block form's whole reason to exist."""
    parts = [f"{k}: {v}" for k, v in rec.items()]
    line = f"{key}: {{{', '.join(parts)}}}"
    if len(line) <= 96 and not any("," in str(v) for v in rec.values()):
        return [line + "\n"]
    return [f"{key}:\n"] + [f"  {p}\n" for p in parts]


def set_frontmatter_record(text: str, key: str, rec: dict) -> str:
    """Replace ONE record, its continuation lines included, preserving every other line.

    `set_frontmatter_key` cannot do this: a record already written in block form occupies
    lines the single-line replacement would leave orphaned below the new value, where they
    would parse as a second record's fields."""
    new_lines = _render_record(key, rec)
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "---\n" + "".join(new_lines) + "---\n\n" + text
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        return text
    for i in range(1, close):
        if lines[i][:1] in (" ", "\t") or ":" not in lines[i]:
            continue
        if lines[i].split(":", 1)[0].strip() != key:
            continue
        end = i + 1
        while end < close and lines[end][:1] in (" ", "\t") and lines[end].strip():
            end += 1
        return "".join(lines[:i] + new_lines + lines[end:])
    return "".join(lines[:close] + new_lines + lines[close:])


# The four STATE frontmatter keys — never records, each with a faithful native counterpart
# in at least one backend (`spec-backend.md` §A native value is the same fact).
FIELD_KEYS = ("tags", "assignee", "start", "target")
