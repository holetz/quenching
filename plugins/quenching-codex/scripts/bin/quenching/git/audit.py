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

import json
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


def _paths(cwd: str, rng: str, env: dict[str, str], errors: list[dict]) -> list[str]:
    """The paths a range changes, read with `-z` so a non-ASCII path arrives raw, never quoted."""
    code, out, err = _git_run(cwd, *SAFE, "diff", "--name-only", "-z", "--no-renames", rng, env=env)
    if code != 0:
        errors.append(_error(("diff", "--name-only"), code, err))
        return []
    return [p for p in out.split("\0") if p]


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


FRONTMATTER_GRANT = re.compile(r"(^|/)(agents/[^/]+|commands/.+)\.md$|(^|/)skills/.+/SKILL\.md$")
AGENT = re.compile(r"(^|/)agents/[^/]+\.md$")
SETTINGS = re.compile(r"^\.agents/settings[^/]*\.json$")
SURFACE = re.compile(r"^\.github/workflows/|^\.agents/settings[^/]*\.json$|(^|/)hooks/")
GRANT_KEYS = ("tools", "allowed-tools")
DENY_KEYS = ("disallowedTools",)


def _split_entries(value: str) -> list[str]:
    """Comma-separated entries, a comma inside parentheses never separating."""
    out, depth, cur = [], 0, ""
    for ch in value:
        depth += (ch == "(") - (ch == ")")
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    out.append(cur.strip())
    return [e.strip("'\"") for e in out if e]


def _frontmatter(text: str, keys: tuple[str, ...]) -> set[str] | None:
    """The entries of `keys` in a leading frontmatter block, inline or as a block list; `None` when
    there is no frontmatter or none of `keys` appears in it."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    found: set[str] | None = None
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", lines[i])
        if m and m.group(1) in keys:
            found = found or set()
            value = m.group(2).strip()
            if value.startswith("[") and value.endswith("]"):
                value = value[1:-1]
            found.update(_split_entries(value))
            while i + 1 < len(lines) and re.match(r"^\s+-\s+|^-\s+", lines[i + 1]):
                i += 1
                found.update(_split_entries(re.sub(r"^\s*-\s+", "", lines[i])))
        i += 1
    return found


def _grant_entries(text: str | None, agent: bool) -> set[str]:
    """What `tools:` / `allowed-tools:` grant. An agent whose frontmatter has no `tools:` holds
    every tool, read as `*`; an absent file grants nothing."""
    if text is None:
        return set()
    found = _frontmatter(text, GRANT_KEYS)
    if found is None:
        return {"*"} if agent else set()
    return found


def _deny_entries(path: str, text: str | None) -> set[str]:
    """The deny rules of a file: `permissions.deny` of a settings JSON, `disallowedTools` of a
    frontmatter. Raises ValueError on a settings file that is not a JSON object."""
    if text is None:
        return set()
    if SETTINGS.search(path):
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("not a JSON object")
        deny = (data.get("permissions") or {}).get("deny") or []
        return {str(e) for e in deny}
    return _frontmatter(text, DENY_KEYS) or set()


def _grants(cwd: str, base: str, tip: str, changed: list[str], env: dict[str, str],
            errors: list[dict]) -> list[dict]:
    """Every entry the branch ADDS to the grant surface against its merge-base with `base`:
    `tools:`/`allowed-tools:` of an agent, command or skill (an agent with no `tools:` is `*`), a
    deny rule removed (`kind: deny`), and the added lines of a hook or CI workflow. Narrowing and
    unchanged never appear."""
    code, out, err = _git_run(cwd, *SAFE, "merge-base", base, tip, env=env)
    if code != 0 or not out.strip():
        errors.append(_error(("merge-base", base), code, err or "no common ancestor"))
        return []
    fork = out.strip()

    def show(rev: str, path: str) -> str | None:
        code, text, _e = _git_run(cwd, *SAFE, "show", f"{rev}:{path}", env=env)
        return text if code == 0 else None

    found = []
    for path in changed:
        frontmatter, surface = FRONTMATTER_GRANT.search(path), SURFACE.search(path)
        if not (frontmatter or surface):
            continue
        new = show(tip, path)
        if new is None:
            continue          # deleted at the tip: nothing was added
        old = show(fork, path)
        if frontmatter:
            agent = bool(AGENT.search(path))
            added = sorted(_grant_entries(new, agent) - _grant_entries(old, agent))
            if added:
                found.append({"path": path, "kind": "tools", "added": added})
        if frontmatter or SETTINGS.search(path):
            try:
                removed = sorted(_deny_entries(path, old) - _deny_entries(path, new))
            except ValueError as exc:
                errors.append(_error(("show", path), 0, f"settings unreadable: {exc}"))
                removed = []
            if removed:
                found.append({"path": path, "kind": "deny", "added": removed})
        if surface:
            code, out, err = _git_run(cwd, *SAFE, "diff", "-U0", "--no-renames", f"{base}...{tip}",
                                      "--", path, env=env)
            if code != 0:
                errors.append(_error(("diff", "-U0"), code, err))
                continue
            added = [ln[1:].strip() for ln in out.splitlines()
                     if ln.startswith("+") and not ln.startswith("+++") and ln[1:].strip()]
            if added:
                found.append({"path": path, "kind": "surface", "added": added})
    return found


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
        "status": _lines(worktree, "status", "--porcelain", "--untracked-files=normal",
                         "--ignore-submodules=all", env=env, errors=errors),
        "stash": _lines(worktree, "stash", "list", env=env, errors=errors),
        "commits": _lines(worktree, "log", "--oneline", f"{base}..{tip}", env=env, errors=errors),
        "changed": _paths(worktree, f"{base}...{tip}", env, errors),
        "ancestry": ancestry,
        "grants": [],
        "reflog": {"branch": _reflog(worktree, f"refs/heads/{args.branch}", env, errors),
                   "head": _reflog(worktree, "HEAD", env, errors)},
        "rewrites": {"branch": _rewrites(worktree, f"refs/heads/{args.branch}", env, errors),
                     "head": _rewrites(worktree, "HEAD", env, errors)},
    }
    payload["grants"] = _grants(worktree, base, tip, payload["changed"], env, errors)
    payload["errors"] = errors
    payload["complete"] = not errors

    lines = [f"worktree: {worktree}", f"branch: {args.branch} ({tip[:12]}) over {args.base}",
             f"commits: {len(payload['commits'])}", f"changed: {len(payload['changed'])} path(s)",
             f"status: {len(payload['status'])} entries", f"stash: {len(payload['stash'])} entries",
             f"grants added: {sum(len(g['added']) for g in payload['grants'])}"]
    lines += [f"ERROR {e['read']} (exit {e['code']}): {e['message']}" for e in errors]
    lines += [f"ancestor {s}: {'yes' if ok else 'NO'}" for s, ok in payload["ancestry"].items()]
    emit(args.json, payload, "\n".join(lines))
    return 0
