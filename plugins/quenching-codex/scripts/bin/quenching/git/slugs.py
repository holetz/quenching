"""`cq git slugs <branch>` — the `quenching-slugs:` line a branch's own description carries,
read plain and rewritten by read-merge-write. Absorbs the `python3 -c` block that used to sit
copy-pasted inside `assets/references/git/isolation.md` §Marking the branch with the specs it
built: `quenching-specs-execute` writes here after every task's commit, `quenching-specs-conclude`'s
auto-discover reads here to resolve which spec(s) built a branch with no `--spec` given.

`git config branch.<name>.description` is the same slot `git branch --edit-description` opens
an editor on — any other line a human wrote there is preserved untouched above and below the
one this owns."""
from __future__ import annotations

import re

from quenching.common.git import _git, _git_run
from quenching.common.output import emit, refuse

LINE_RE = re.compile(r"quenching-slugs: (.*)")


def _read_slugs(cwd: str, branch: str) -> tuple[list[str], list[str], int | None]:
    """The description's lines, the sorted slugs the marking line already carries, and that
    line's index — `None` when the branch has no marking of its own yet."""
    out = _git(cwd, "config", f"branch.{branch}.description")
    lines = out.splitlines() if out else []
    slugs: list[str] = []
    idx = None
    for i, line in enumerate(lines):
        m = LINE_RE.match(line)
        if m:
            slugs = sorted({s.strip() for s in m.group(1).split(",") if s.strip()})
            idx = i
    return lines, slugs, idx


def cmd_slugs(args) -> int:
    cwd = "."
    lines, slugs, idx = _read_slugs(cwd, args.branch)
    if not args.add:
        emit(args.json, {"ok": True, "branch": args.branch, "slugs": slugs},
             ",".join(slugs) if slugs else "(no marking)")
        return 0

    merged = sorted(set(slugs) | {args.add})
    newline = "quenching-slugs: " + ",".join(merged)
    if idx is not None:
        lines[idx] = newline
    else:
        lines.append(newline)
    code, _out, err = _git_run(cwd, "config", f"branch.{args.branch}.description",
                               "\n".join(lines))
    if code != 0:
        return refuse({"code": "git-slugs-write-failed", "branch": args.branch,
                       "message": err.strip() or "git config exited nonzero"}, args.json)
    emit(args.json, {"ok": True, "branch": args.branch, "slugs": merged}, ",".join(merged))
    return 0
