"""`stale-doc` — the one check that asks git a question, and the two calls that ask it.

Moved verbatim out of `assets/hooks/okf-validate.py`; only `parse_frontmatter`'s call
shape changed, from the `(fm, has_block, well_formed)` tuple to the bare dict
`quenching.common.frontmatter` returns.

STALENESS (CLI only — advisory, never blocking)
- **`stale-doc`** the doc's `timestamp` predates the last commit touching the code its
  `resource` globs name (`git log -1 --format=%cI`, explicit `:(glob)` pathspec magic).
  It is **advisory and part of no verify gate**: unlike the integrity codes, a
  stale-looking doc may be perfectly correct, because code moves under a rule that did
  not change. It runs in CLI mode only — never `PostToolUse`, never `Stop` — since it
  shells out once per doc, and a tree that is not a git checkout skips it silently.

The two subprocess calls are this pillar's own and NOT `quenching.common.git._git`: `_git`
falls back to `cwd="."` for a directory that does not exist, where these must answer
"no git facts" for that path, and `_is_git_checkout` reads the exit code and the stdout
together. Left as they were rather than folded into the shared helper.
"""
from __future__ import annotations

import os
import subprocess

from quenching.common.frontmatter import parse_frontmatter
from quenching.knowledge.resource import (_is_bundle_aggregate, _project_root,
                                          _rel_to_project, parse_resource)
from quenching.knowledge.schema import GIT_TIMEOUT_S, ISO_DATE, RESOLVABLE_KINDS, _nonempty

_GIT_CHECKOUT: dict[str, bool] = {}


def _is_git_checkout(project_root: str) -> bool:
    """Whether `project_root` sits inside a git work tree. Cached per process, so a
    whole-tree sweep asks once per bundle rather than once per doc — a repo that is
    not a checkout would otherwise pay one failed subprocess per concept doc."""
    key = os.path.abspath(project_root)
    if key not in _GIT_CHECKOUT:
        try:
            proc = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                                  cwd=key, capture_output=True, text=True,
                                  timeout=GIT_TIMEOUT_S)
            _GIT_CHECKOUT[key] = proc.returncode == 0 and proc.stdout.strip() == "true"
        except (OSError, subprocess.SubprocessError):
            _GIT_CHECKOUT[key] = False
    return _GIT_CHECKOUT[key]


def _git_last_commit_date(entries: list[str], project_root: str) -> str | None:
    """Newest committer date (`YYYY-MM-DD`) across the entry globs, or None when
    the answer cannot be trusted — not a git checkout, git absent, no commit
    touching the scope, or the call timed out.

    Pathspecs carry explicit **`:(glob)`** magic. Git's default wildmatch lets a
    single `*` cross a slash, so a naive `src/*` silently widens to everything
    under `src/` and reports a perfectly current doc as stale; `:(glob)` gives the
    same segment-wise semantics `_glob_contains` implements for `resource-self`,
    so one glob means one thing across the whole checker. The fixture's
    `shallow.md` pins this: it is silent under `:(glob)` and a false positive
    without it.
    """
    try:
        proc = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--"] + [f":(glob){e}" for e in entries],
            cwd=project_root, capture_output=True, text=True, timeout=GIT_TIMEOUT_S,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()[:10] or None


def check_stale(text: str, bundle_root: str) -> list[tuple[str, str, str]]:
    """`stale-doc` — the doc's `timestamp` predates the last commit touching the
    code its `resource` governs.

    **Advisory, and never must-fix.** Unlike the integrity codes, a stale-looking
    doc may be perfectly correct: code moves under a rule that did not change.
    Conflating the two would make the must-fix set unusable, since every mature
    bundle carries some legitimately stale-looking doc.

    Bundle-aggregate entries are excluded on the same mechanism as `resource-self`:
    a scope containing the whole bundle contains the doc, so it is touched whenever
    the doc itself is, and would report fresh forever.
    """
    fm = parse_frontmatter(text)
    if not _nonempty(fm, "resource") or not _nonempty(fm, "timestamp"):
        return []
    stamped = str(fm["timestamp"]).strip()[:10]
    if not ISO_DATE.match(stamped):
        return []          # a non-ISO timestamp is `missing-timestamp`'s business, not ours
    project_root = _project_root(bundle_root)
    if not _is_git_checkout(project_root):
        return []          # no history to compare against — skip silently, never report
    bundle_rel = _rel_to_project(bundle_root, project_root)
    entries = [e for e, kind in parse_resource(fm["resource"])
               if kind in RESOLVABLE_KINDS and not _is_bundle_aggregate(e, kind, bundle_rel)]
    if not entries:
        return []
    last = _git_last_commit_date(entries, project_root)
    if last and last > stamped:
        return [("WARN", "stale-doc",
                 f"`timestamp` {stamped} predates the last commit touching its `resource` "
                 f"({last}) — the doc may no longer describe what it governs")]
    return []
