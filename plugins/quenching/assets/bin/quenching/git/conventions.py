"""`cq git conventions` — the read-if-present check every command in the `git` pillar runs
once before its first commit: does the target declare its own `docs/standards/git/**`, or do
the plugin's defaults apply? `assets/references/git/conventions.md` §The read-if-present rule
is the contract; this is its one mechanical reading, so five commands stop repeating the same
`ls` and frontmatter peek.

Reports FACTS ONLY — which files exist, and each one's own `authority`. Whether a partial
document covers commits but not merges is a reading a human (or the citing command body) does
over the listed files; this stays a report for the same reason the rest of the `git` pillar
carries no `doctor`."""
from __future__ import annotations

import os

from quenching.common.frontmatter import parse_frontmatter
from quenching.common.io import read_text
from quenching.common.output import emit

STANDARDS_DIR = os.path.join("docs", "standards", "git")


def _declared_docs(cwd: str) -> list[dict]:
    git_dir = os.path.join(cwd, STANDARDS_DIR)
    if not os.path.isdir(git_dir):
        return []
    docs = []
    for name in sorted(os.listdir(git_dir)):
        # `index.md` is the OKF bundle's own reserved layer listing, in every
        # `standards/<subject>/` folder — a convention ABOUT the folder, never one of its docs.
        if not name.endswith(".md") or name == "index.md":
            continue
        rel = f"{STANDARDS_DIR}/{name}"
        fm = parse_frontmatter(read_text(os.path.join(git_dir, name)) or "")
        docs.append({"path": rel, "authority": fm.get("authority")})
    return docs


def cmd_conventions(args) -> int:
    docs = _declared_docs(os.getcwd())
    governs = "target" if docs else "defaults"
    if docs:
        human = "governs: the target's own conventions\n" + "\n".join(
            f"  {d['path']} (authority: {d['authority'] or 'unstated'})" for d in docs)
    else:
        human = "governs: the plugin's defaults — nothing declared under " + STANDARDS_DIR
    emit(args.json, {"ok": True, "governs": governs, "declared": docs}, human)
    return 0
