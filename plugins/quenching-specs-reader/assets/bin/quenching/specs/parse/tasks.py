"""The `## Tasks` grammar — the checkbox line, its indented metadata, and the block
each task owns.

Moved verbatim out of the pre-refactor specs script."""
from __future__ import annotations

import re

from quenching.specs.parse.sections import parse_sections
from quenching.specs.parse.text import HEADING_RE, mask_comments


# `- [ ]` / `- [x]` / `- [!]` — the third is a BLOCKED task, visible and human-legible,
# which is what replaced v1's hidden five-attempt counter in `.specs.json`.
CHECKBOX_RE = re.compile(r"^(\s*)-\s\[( |x|X|!)\]\s+(.*)$")
CHECKBOX_LOOSE_RE = re.compile(r"^\s*-\s*\[.*?\]")   # looks like a checkbox (malformed detection)
TASK_ID_RE = re.compile(r"^(\d+(?:\.\d+)*)\b")
TASK_META_KEYS = ("files", "pattern", "cwd", "verify", "constraint", "subject", "commit")
TASK_META_RE = re.compile(rf"^\s+({'|'.join(TASK_META_KEYS)})\s*:\s*(.+?)\s*$",
                          re.IGNORECASE)
# `constraint:` is INERT by design: the grammar admits it and `next` hands it through, but no
# command reads it. Its only consumer would be an executor sub-agent briefing itself, and the
# decision to dispatch one belongs to another spec — so the field lands first and the decision
# stays untouched. A field nobody reads costs one alternation and moves no turn.
#
# The anchor is written into a one-line grammar and read back, so the only hard requirement
# is that it holds text and stays on its line. `commit:` is both the legacy form of the same
# field — still READ from specs written before the anchor became the subject — AND, since
# `task --commit`, a form written again on purpose: a real git sha, upserted by the CLI once
# the commit that implements the task already exists. `subject:` stays the default `--check`
# writes; `commit:` is opt-in via the new flag. See `task --commit`'s help and `## Design`
# ("Decisão: o anchor task→commit é o sha") for why both anchors coexist for now.
SUBJECT_RE = re.compile(r"^[^\r\n]+$")
# A git object id, short or full — hex only. Loose on purpose (git accepts abbreviations down
# to a repo-dependent minimum well below 7), but tight enough to catch an obvious mistake like
# passing a commit MESSAGE where a sha was meant.
COMMIT_SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
DEFAULT_META_INDENT = "      "
PARALLEL_RE = re.compile(r"^\[P\](?:\s|$)")
BLOCKED_REASON_RE = re.compile(r"—\s*blocked\s*:\s*(.+?)\s*$", re.IGNORECASE)


def _split_files(val: str) -> list[str]:
    """Comma-split that respects parentheses: a comma inside `(…)` belongs to the same
    entry, so a comment like `a.md (descartável, revertido ao fim)` reads as ONE path
    instead of two invented ones the executor could not tell from real paths. Depth is
    tracked, never counted: an unbalanced `(` simply keeps the rest of the line one
    entry. Stdlib-only."""
    out: list[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(val):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == "," and depth == 0:
            piece = val[start:i].strip()
            if piece:
                out.append(piece)
            start = i + 1
    piece = val[start:].strip()
    if piece:
        out.append(piece)
    return out


FILES_ANNOTATION_RE = re.compile(r"\s*\(([^()]*)\)\s*$")


def _files_bad_annotation(entry: str) -> str | None:
    """The single reserved `files:` annotation is `(new)` — a path about to be created,
    which `_norm_file` strips for comparisons. Any OTHER trailing parenthetical is a
    human comment; kept inside the entry, the executor receives a path that exists
    nowhere with the same confidence as a real one — the silent failure this rule
    closes. Return the annotation text so the caller can refuse the entry."""
    m = FILES_ANNOTATION_RE.search(entry)
    if not m:
        return None
    note = m.group(1)
    return None if note == "new" else note


def parse_tasks(text: str) -> list[dict]:
    """Every checkbox under `## Tasks`, in order: index, explicit id, state, text, line
    number, the `[P]` marker, the optional indented metadata (`files`/`pattern`/`verify`),
    and — for a blocked task — the reason written right in the line.

    `state` is `" "` (open), `"x"` (done) or `"!"` (blocked). The blocked marker is
    deliberately IN THE FILE rather than in sidecar state: it is what a human reads when
    they come to unblock it, and v1's hidden attempt counter was read by nobody."""
    sections = parse_sections(mask_comments(text))
    if "Tasks" not in sections:
        return []
    base = sections["Tasks"]["lineno"] + 1
    lines = sections["Tasks"]["lines"]
    out = []
    idx = 0
    section = 0
    for i, line in enumerate(lines):
        hm = HEADING_RE.match(line)
        if hm and len(hm.group(1)) == 3:
            section += 1          # a `### N.` heading starts a new task section
            continue
        m = CHECKBOX_RE.match(line)
        if not m:
            continue
        idx += 1
        state = m.group(2).lower()
        body = m.group(3).strip()
        idm = TASK_ID_RE.match(body)
        rest = body[idm.end():].lstrip() if idm else body
        parallel = bool(PARALLEL_RE.match(rest))
        blocked = BLOCKED_REASON_RE.search(body)
        files: list[str] = []
        pattern = cwd = verify = subject = commit = None
        subject_off = commit_off = last_meta_off = None
        meta_indent = None
        block_end = i + 1
        for off, cont in enumerate(lines[i + 1:], start=i + 1):
            # the task's block ends at a blank line, a non-indented line, or another
            # checkbox; anything else indented is scanned, so a wrapped prose line between
            # the checkbox and its `verify:` does not hide it.
            if not cont.strip() or cont[:1] not in (" ", "\t") or CHECKBOX_RE.match(cont):
                break
            block_end = off + 1
            mm = TASK_META_RE.match(cont)
            if not mm:
                continue
            key, val = mm.group(1).lower(), mm.group(2).strip()
            if meta_indent is None:
                meta_indent = cont[:len(cont) - len(cont.lstrip())]
            last_meta_off = off
            if key == "files":
                files = _split_files(val)
            elif key == "pattern":
                pattern = val
            elif key == "cwd":
                cwd = val
            elif key == "subject":
                subject, subject_off = val, off
            elif key == "commit":
                commit, commit_off = val, off
            elif key == "verify":
                verify = val
            # `constraint:` is admitted by the grammar and read by nothing — the inert field.
            # This arm is why the dispatch is exhaustive rather than an `else: verify = val`:
            # under the open form, a `constraint:` line following `verify:` overwrote it, and
            # the loop would have run that prose as the task's shell command.
        out.append({
            "index": idx,
            "id": idm.group(1) if idm else None,
            "state": state,
            "checked": state == "x",
            "blocked": state == "!",
            "reason": blocked.group(1) if blocked else None,
            "text": body,
            "lineno": base + i,
            "section": section,
            "parallel": parallel,
            "files": files,
            "pattern": pattern,
            "cwd": cwd,
            "verify": verify,
            "subject": subject,
            "commit": commit,
            # ONE PAST the task's own last line — checkbox plus every indented metadata
            # line under it, exactly the span `block_end` already tracked to find the
            # metadata. Exists so a caller can slice `lines[lineno:blockEndLineno]` and get
            # the task's literal source text, verbatim, with nothing re-rendered. The
            # `github` backend is the first reader: a task's raw block IS what a sub-issue
            # stores, so `checked`/`blocked` round-trip by re-parsing the same text through
            # THIS function again on read, rather than the backend inventing its own
            # encoding of state.
            "blockEndLineno": base + block_end,
            # where the anchor line is, and where one would go — so `task` upserts it
            # mechanically instead of the caller doing string surgery on the file. Both
            # forms are tracked because both are read AND, as of `task --commit`, both can be
            # written: `subject:` by `--check --subject`, `commit:` by `--check --commit` once
            # the real sha exists. A spec written before either form applied to it carries
            # only whichever one it has, and `--uncheck` must still be able to drop it.
            "subjectLineno": (base + subject_off) if subject_off is not None else None,
            "commitLineno": (base + commit_off) if commit_off is not None else None,
            # After the last metadata line when there is one; otherwise after the WHOLE
            # block, not under the checkbox's first physical line. A task with no `files:`
            # or `verify:` whose text wraps was being cut in half by its own `subject:`.
            "metaInsertAt": base + ((last_meta_off + 1) if last_meta_off is not None
                                    else block_end),
            "metaIndent": meta_indent or DEFAULT_META_INDENT,
        })
    return out


def task_progress(tasks: list[dict]) -> tuple[int, int, int]:
    """(checked, blocked, total)."""
    return (sum(1 for t in tasks if t["checked"]),
            sum(1 for t in tasks if t["blocked"]),
            len(tasks))
