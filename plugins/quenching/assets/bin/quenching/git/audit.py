"""`cq git audit` — the facts the `verifier` agent checks inside a spec's worktree, read with a
fixed argv so the agent needs no `Bash(git …)` grant at all.

A wildcard grant such as `Bash(git -C * status:*)` admits any git command that merely ends in
`status` — `branch -D`, `clean -fdx`, `-c core.fsmonitor=<cmd>` — and `git log:*` admits
`--output=<file>`. Here the agent names a worktree and refs; every git invocation is built in this
module, refs are resolved to commits before use, and the repository's own config cannot run a
command during the read: the `filter.<x>` drivers it declares are blanked before `status` through
`GIT_CONFIG_COUNT`, which carries a key containing `=` that `-c key=value` would split, and `status`
does not descend into submodules (their own config is not ours to blank); `log.showSignature` is
forced off so `gpg.program` never runs; and a partial clone's lazy fetch is off
(`GIT_NO_LAZY_FETCH`, and `GIT_ALLOW_PROTOCOL` empty refuses every transport), so a missing blob
or an absent `--sha` never runs `core.sshCommand` or any other transport the config names. A
REPORT only, exit 0 on any facts, and a read that failed is
an entry of the payload's `errors` (`complete: false`), never an empty list; judging them is the verifier's. Nothing here executes the
audited branch's code: the gate is certified by CI before the merge, never by this verb."""
from __future__ import annotations

import os
import re
from quenching.common.git import _git_run
from quenching.common.output import emit, refuse

FILTER_KEY = re.compile(r"^filter\.(.+)\.(clean|smudge|process)$", re.S)
SAFE = ("--no-optional-locks", "-c", "core.fsmonitor=false", "-c", "core.hooksPath=/dev/null",
        "-c", "log.showSignature=false")
NO_FETCH = {"GIT_NO_LAZY_FETCH": "1", "GIT_ALLOW_PROTOCOL": ""}


def _run(cwd: str, *argv: str, env: dict[str, str] | None = None) -> tuple[int, str]:
    """One read. With no `env` the lazy fetch is still off: a caller that forgot to pass the inert
    environment (`cq git worktree`, `push`, through `_commit`) never reaches a transport."""
    code, out, _err = _git_run(cwd, *SAFE, *argv, env=env or {**os.environ, **NO_FETCH})
    return code, out


def _lines(cwd: str, *argv: str, env: dict[str, str] | None = None,
           errors: list[dict] | None = None) -> list[str]:
    """The non-empty stdout lines of one read. A read that FAILS (non-zero exit, a timeout, no git)
    is not an empty list: it is appended to `errors` as `{read, code, message}` so the payload says
    the fact is unknown. Without `errors` the caller opted out of that and gets `[]`."""
    code, out, err = _git_run(cwd, *SAFE, *argv, env=env)
    if code != 0:
        if errors is not None:
            errors.append(_error(argv, code, err))
        return []
    return [line for line in out.splitlines() if line]


def _error(argv: tuple[str, ...], code: int, err: str) -> dict:
    lines = [line for line in (err or "").strip().splitlines() if line.strip()]
    return {"read": " ".join(argv[:2]), "code": code, "message": lines[0] if lines else ""}


def _reflog(cwd: str, ref: str, env: dict[str, str] | None = None,
            errors: list[dict] | None = None) -> list[str]:
    """The reflog entries of `ref` that MOVED it, newest first. The check judges movement, not
    message: an entry whose sha equals the next older entry's moved nothing and is dropped whatever
    it says (`git merge --abort` logs `reset: moving to HEAD`); every other entry stays, and one
    with an empty message (`git update-ref` without `-m`) reads `(no reflog message) <old>..<new>`,
    so a rewrite made silently is still seen. The oldest entry is the ref's creation and stays."""
    entries = [(line.split(" ", 1) + [""])[:2]
               for line in _lines(cwd, "reflog", "show", "--format=%H %gs", ref, env=env, errors=errors)]
    if not entries and errors is not None:   # a live ref always has its creation entry: none means expired or never logged
        errors.append(_error(("reflog", "show", ref), 0, "reflog empty or expired: the ref's history is unknown, not clean"))
    kept = []
    for i, (sha, subject) in enumerate(entries):
        older = entries[i + 1][0] if i + 1 < len(entries) else None
        if older == sha:
            continue
        kept.append(subject or f"(no reflog message) {(older or '')[:12]}..{sha[:12]}")
    return kept


def _rewrites(cwd: str, ref: str, env: dict[str, str] | None = None,
              errors: list[dict] | None = None) -> list[str]:
    """The reflog moves of `ref` that are not fast-forwards: the older sha is not an ancestor of the
    newer one. The verdict is the graph's, so a rewrite made with no message or a forged one
    (`update-ref -m "commit: tidy"`) is still listed. The oldest entry is the creation and has no
    older sha, so it is never one. Each item reads `<subject or (no reflog message)> <old>..<new>`."""
    entries = [(line.split(" ", 1) + [""])[:2]
               for line in _lines(cwd, "reflog", "show", "--format=%H %gs", ref, env=env)]
    found = []
    for i, (sha, subject) in enumerate(entries[:-1]):
        older = entries[i + 1][0]
        if older == sha:
            continue
        code, _out, err = _git_run(cwd, *SAFE, "merge-base", "--is-ancestor", older, sha, env=env)
        if code > 1:
            if errors is not None:
                errors.append(_error(("merge-base", "--is-ancestor"), code, err))
            continue
        if code == 1:
            found.append(f"{subject or '(no reflog message)'} {older[:12]}..{sha[:12]}")
    return found


def _registered(cwd: str, path: str) -> bool:
    code, out = _run(cwd, "worktree", "list", "--porcelain")
    if code != 0:
        return False
    want = os.path.realpath(path)
    return any(os.path.realpath(line[len("worktree "):]) == want
               for line in out.splitlines() if line.startswith("worktree "))


def _commit(cwd: str, ref: str, env: dict[str, str] | None = None) -> str | None:
    if not ref or ref.startswith("-"):
        return None
    code, out = _run(cwd, "rev-parse", "--verify", "--quiet", "--end-of-options", f"{ref}^{{commit}}",
                     env=env)
    return out.strip() if code == 0 and out.strip() else None


def _branch_ok(cwd: str, branch: str) -> bool:
    if branch.startswith("-"):
        return False
    return _run(cwd, "check-ref-format", "--branch", branch)[0] == 0


def _inert_env(cwd: str, errors: list[dict] | None = None) -> dict[str, str]:
    """The environment every read of this verb runs under: the lazy fetch off, and every
    `filter.<x>` driver the repository config declares blanked as a `GIT_CONFIG_COUNT` pair, so the
    status cannot run one against the branch's `.gitattributes` whatever `<x>` contains.
    `required` is cleared too: a required filter with no command would die instead of being
    skipped. The pairs are appended after any the caller already passes."""
    env = {**os.environ, **NO_FETCH}
    code, out = _run(cwd, "config", "-z", "--name-only", "--get-regexp",
                     r"^filter\..*\.(clean|smudge|process)$", env=env)   # 1: no such key, a fact
    if code not in (0, 1) and errors is not None:   # the filter list is unknown, not empty
        errors.append(_error(("config", "--get-regexp"), code, "filter config unreadable: the drivers could not be blanked"))
    try:
        n = int(env.get("GIT_CONFIG_COUNT", "0"))
    except ValueError:
        n = 0
    for key in out.split("\0") if code == 0 else []:
        m = FILTER_KEY.match(key)
        if m:
            for k, v in ((key, ""), (f"filter.{m.group(1)}.required", "false")):
                env[f"GIT_CONFIG_KEY_{n}"], env[f"GIT_CONFIG_VALUE_{n}"] = k, v
                n += 1
    env["GIT_CONFIG_COUNT"] = str(n)
    return env


def cmd_audit(args) -> int:
    cwd = os.getcwd()
    worktree = os.path.realpath(args.worktree)
    if not _registered(cwd, worktree):
        return refuse({"code": "audit-worktree-unregistered",
                       "message": f"not a worktree this repository registers: {args.worktree}"},
                      args.json)
    if not _branch_ok(worktree, args.branch):
        return refuse({"code": "audit-ref-invalid", "message": f"not a branch name: {args.branch}"},
                      args.json)
    errors: list[dict] = []
    env = _inert_env(worktree, errors)
    resolved = {}
    for label, ref in [("base", args.base), ("branch", f"refs/heads/{args.branch}"),
                       *(("sha", s) for s in args.sha)]:
        sha = _commit(worktree, ref, env)
        if sha is None:
            return refuse({"code": "audit-ref-invalid",
                           "message": f"{label} does not resolve to a commit: {ref}"}, args.json)
        resolved[ref] = sha
    base, tip = resolved[args.base], resolved[f"refs/heads/{args.branch}"]

    ancestry = {}
    for sha in args.sha:
        code, _out, err = _git_run(worktree, *SAFE, "merge-base", "--is-ancestor", resolved[sha], tip,
                                   env=env)
        if code > 1:                      # 1 is the answer "no"; anything above it is git failing
            errors.append(_error(("merge-base", "--is-ancestor"), code, err))
        ancestry[sha] = code == 0
    payload = {
        "ok": True,
        "worktree": worktree,
        "base": {"ref": args.base, "sha": base},
        "branch": {"ref": args.branch, "sha": tip},
        "status": _lines(worktree, "status", "--porcelain", "--ignore-submodules=all", env=env,
                         errors=errors),
        "stash": _lines(worktree, "stash", "list", env=env, errors=errors),
        "commits": _lines(worktree, "log", "--oneline", f"{base}..{tip}", env=env, errors=errors),
        "changed": _lines(worktree, "diff", "--name-only", "--no-renames", f"{base}...{tip}", env=env, errors=errors),
        "ancestry": ancestry,
        "reflog": {"branch": _reflog(worktree, f"refs/heads/{args.branch}", env, errors),
                   "head": _reflog(worktree, "HEAD", env, errors)},
        "rewrites": {"branch": _rewrites(worktree, f"refs/heads/{args.branch}", env, errors),
                     "head": _rewrites(worktree, "HEAD", env, errors)},
    }
    payload["errors"] = errors
    payload["complete"] = not errors

    lines = [f"worktree: {worktree}", f"branch: {args.branch} ({tip[:12]}) over {args.base}",
             f"commits: {len(payload['commits'])}", f"changed: {len(payload['changed'])} path(s)",
             f"status: {len(payload['status'])} entries", f"stash: {len(payload['stash'])} entries"]
    lines += [f"ERROR {e['read']} (exit {e['code']}): {e['message']}" for e in errors]
    lines += [f"ancestor {s}: {'yes' if ok else 'NO'}" for s, ok in payload["ancestry"].items()]
    emit(args.json, payload, "\n".join(lines))
    return 0
