"""`cq git audit` — the facts the `verifier` agent checks inside a spec's worktree, read with a
fixed argv so the agent needs no `Bash(git …)` grant at all.

A wildcard grant such as `Bash(git -C * status:*)` admits any git command that merely ends in
`status` — `branch -D`, `clean -fdx`, `-c core.fsmonitor=<cmd>` — and `git log:*` admits
`--output=<file>`. Here the agent names a worktree and refs; every git invocation is built in this
module, refs are resolved to commits before use, and the repository's own config cannot run a
command during the read: the `filter.<x>` drivers it declares are blanked before `status` through
`GIT_CONFIG_COUNT`, which carries a key containing `=` that `-c key=value` would split, and `status`
does not descend into submodules (their own config is not ours to blank); every diff and show
read carries `--no-ext-diff --no-textconv`, so neither `diff.external` nor a `diff.<x>.textconv`
driver runs; `log.showSignature` is forced off so `gpg.program` never runs; and a partial clone's lazy fetch is off
(`GIT_NO_LAZY_FETCH`, and `GIT_ALLOW_PROTOCOL` empty refuses every transport), so a missing blob
or an absent `--sha` never runs `core.sshCommand` or any other transport the config names.
`rewrites` and `reflog` are evidence of what the worker did not erase, not proof against a worker with
`Bash`: `git reflog delete` or `expire` removes the entries and the payload then reads empty with
`complete: true`. The audit, like check 9 of the verifier, catches the widening a worker that follows the
protocol makes by mistake; it is not a sandbox against one who evades it on purpose (a worker with
free `Bash` writes outside any diff anyway). A REPORT only, exit 0 on any facts, and a read that failed is
an entry of the payload's `errors` (`complete: false`), never an empty list; judging them is the verifier's.
An agent, command or skill is read under `.claude/`, under `plugins/<one segment>/`, and under every
plugin root the base or the tip declares (a `.claude-plugin/plugin.json`, a relative `source` of a
`.claude-plugin/marketplace.json`, and the component paths either names), never by an `agents/` at
any depth, so an OKF standard filed under `standards/agents/` is no grant. Nothing here executes the
audited branch's code: the gate is certified by CI before the merge, never by this verb."""
from __future__ import annotations

import json
import os
import posixpath
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
    code, out, err = _git_run(cwd, *SAFE, "diff", "--no-ext-diff", "--no-textconv", "--name-only", "-z", "--no-renames", rng, env=env)
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


LOADED_ROOT = r"^(?:(?:.*/)?\.claude/|(?:.*/)?plugins/[^/]+/)?"   # where Claude Code loads agents, commands and skills from
FRONTMATTER_GRANT = re.compile(LOADED_ROOT + r"(?:(?:agents|commands)/.+\.md|skills/.+/skill\.md)$", re.I)
AGENT = re.compile(LOADED_ROOT + r"agents/.+\.md$", re.I)
MANIFEST = re.compile(r"(?:^|/)\.claude-plugin/(plugin|marketplace)\.json$")
COMPONENT_KEYS = ("agents", "commands", "skills")
SYMLINK = "120000"
SETTINGS = re.compile(r"^\.claude/settings[^/]*\.json$")
SURFACE = re.compile(r"^\.github/workflows/|^\.claude/settings[^/]*\.json$|(^|/)hooks/"
                     r"|(^|/)\.claude-plugin/[^/]+\.json$|(^|/)\.(mcp|lsp)\.json$")
GRANT_KEYS = ("tools", "allowed-tools")
DENY_KEYS = ("disallowedTools",)
DOCS = re.compile(r"^docs/")


def _declared(base: str, value) -> list[str]:
    """The relative paths a manifest field names (a string or a list of strings), joined to `base`
    and normalized; one that leaves the repository is dropped."""
    items = [value] if isinstance(value, str) else value if isinstance(value, list) else []
    out = []
    for item in items:
        if not isinstance(item, str) or not item.strip() or item.startswith("/"):
            continue
        path = posixpath.normpath(posixpath.join(base, item))
        if path != ".." and not path.startswith("../"):
            out.append("" if path == "." else path)
    return out


def _plugin_components(root: str, manifest) -> list[tuple[str, str]]:
    """`(kind, prefix)` for one plugin root: its default `agents/`, `commands/`, `skills/` and every
    component path its manifest entry declares (a `.md` path is one file, anything else a folder)."""
    prefix = f"{root}/" if root else ""
    found = [(kind, prefix + kind + "/") for kind in COMPONENT_KEYS]
    if isinstance(manifest, dict):
        for kind in COMPONENT_KEYS:
            for path in _declared(root, manifest.get(kind)):
                found.append((kind, path if path.lower().endswith(".md") else (f"{path}/" if path else "")))
    return found


def _plugin_roots(cwd: str, revs: tuple[str, ...], env: dict[str, str],
                  errors: list[dict]) -> list[tuple[str, str]]:
    """Every `(kind, prefix)` a plugin of the base or the tip loads agents, commands and skills from,
    whatever the path's shape: a folder holding `.claude-plugin/plugin.json` is a root even when its
    JSON does not parse (only the declared component paths are lost then), and so is every relative
    `source` of a `.claude-plugin/marketplace.json` (under `metadata.pluginRoot` when set). A tree
    that cannot be listed is an `errors` entry: the roots are unknown, never empty."""
    found: list[tuple[str, str]] = []
    for rev in revs:
        code, out, err = _git_run(cwd, *SAFE, "ls-tree", "-r", "--name-only", "-z", rev, env=env)
        if code != 0:
            errors.append(_error(("ls-tree", rev), code, err))
            continue
        for path in out.split("\0"):
            m = MANIFEST.search(path)
            if not m:
                continue
            here = posixpath.dirname(posixpath.dirname(path))
            code, text, _e = _git_run(cwd, *SAFE, "show", "--no-textconv", f"{rev}:{path}", env=env)
            try:
                data = json.loads(text) if code == 0 else None
            except ValueError:
                data = None
            if m.group(1) == "plugin":
                found += _plugin_components(here, data)
                continue
            if not isinstance(data, dict) or not isinstance(data.get("plugins"), list):
                continue
            meta = data.get("metadata")
            prefix = (_declared(here, meta.get("pluginRoot")) if isinstance(meta, dict) else []) or [here]
            for entry in data["plugins"]:
                source = entry.get("source") if isinstance(entry, dict) else None
                for root in _declared(prefix[0], source) if isinstance(source, str) else []:
                    found += _plugin_components(root, entry)
    return found


def _component(path: str, roots: list[tuple[str, str]]) -> tuple[bool, bool]:
    """`(grant-bearing frontmatter, agent)` for a path under one of `roots`: an agent or command
    `.md`, or a skill's `SKILL.md`, case-insensitively."""
    low, frontmatter, agent = path.lower(), False, False
    for kind, prefix in roots:
        pre = prefix.lower()
        if pre.endswith(".md"):
            hit = low == pre
        elif not low.startswith(pre):
            continue
        elif kind == "skills":
            rel = low[len(pre):]
            hit = rel == "skill.md" or rel.endswith("/skill.md")
        else:
            hit = low.endswith(".md")
        frontmatter = frontmatter or hit
        agent = agent or (hit and kind == "agents")
    return frontmatter, agent


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


KNOWN_KEYS = GRANT_KEYS + DENY_KEYS
INERT_KEYS = ("name", "description", "argument-hint")   # grant, deny and change nothing: never `unknown`
TOP_KEY = re.compile(r"^([A-Za-z_-]+):(?:\s+(.*))?$")
LIST_ITEM = re.compile(r"^\s*-\s+")


def _block(text: str | None) -> tuple[dict[str, list[str]], bool, tuple[str, ...]] | None:
    """The leading frontmatter block as `{key: [its lines]}`, whether every line was recognized,
    and the block's raw lines (an unrecognized line is in no key, so only these show it changed);
    `None` when there is no block. A leading BOM is dropped and lines split on `\\n` only, as the
    Claude Code reads them (`str.splitlines` also breaks on FF/VT/U+2028, hiding a grant behind a
    fake comment line). A top-level `key:` opens a key, the indented and
    `- item` lines after it belong to it, blank and `#` lines are skipped. Any other top-level line
    (a quoted key, a line with no `key:`), a repeated key, or a known key whose value is inline AND
    continued on the next line is not recognized: the audit computes only what it reads whole."""
    if text is None:
        return None
    lines = [ln.removesuffix("\r") for ln in text.removeprefix("\ufeff").split("\n")]
    if not lines or lines[0].strip() != "---":
        return None
    keys: dict[str, list[str]] = {}
    ok, cur, raw = True, None, []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        raw.append(line)
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = TOP_KEY.match(line)
        if m:
            cur = m.group(1)
            if cur in keys:
                ok = False
            keys[cur] = [line]
        elif cur is not None and (line[:1] in (" ", "\t") or LIST_ITEM.match(line)):
            keys[cur].append(line)
        else:
            ok = False
    for body in filter(None, map(keys.get, KNOWN_KEYS)):
        inline = (TOP_KEY.match(body[0]).group(2) or "").strip()
        if body[1:] and (inline or not all(LIST_ITEM.match(ln) for ln in body[1:])):
            ok = False
    return keys, ok, tuple(raw)


def _entries(keys: dict[str, list[str]], wanted: tuple[str, ...]) -> set[str] | None:
    """The entries of `wanted` in a recognized block, inline or as a block list; `None` when none
    of `wanted` appears."""
    found: set[str] | None = None
    for key in wanted:
        if key not in keys:
            continue
        found = found or set()
        head, *items = keys[key]
        value = (TOP_KEY.match(head).group(2) or "").strip()
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1]
        found.update(_split_entries(value))
        for item in items:
            found.update(_split_entries(LIST_ITEM.sub("", item)))
    return found


def _grant_entries(text: str | None, parsed: tuple | None, agent: bool) -> set[str]:
    """What `tools:` / `allowed-tools:` grant. An agent whose frontmatter has no `tools:` holds
    every tool, read as `*`; an absent file grants nothing."""
    if text is None:
        return set()
    found = _entries(parsed[0], GRANT_KEYS) if parsed else None
    if found is None:
        return {"*"} if agent else set()
    return found


def _unknown_keys(old: dict[str, list[str]], new: dict[str, list[str]]) -> list[str]:
    """Every key outside the known and the inert ones that the branch adds, removes or changes."""
    return sorted(k for k in set(old) | set(new)
                  if k not in KNOWN_KEYS + INERT_KEYS and old.get(k) != new.get(k))


def _deny_entries(path: str, text: str | None, key: str = "deny") -> set[str]:
    """The rules of a file: `permissions.<key>` (`deny` or `ask`) of a settings JSON,
    `disallowedTools` of a frontmatter (deny only). Raises ValueError on a settings file that is
    not a JSON object, whose `permissions` is not an object or whose `<key>` is not a list."""
    if text is None:
        return set()
    if SETTINGS.search(path):
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("not a JSON object")
        permissions = data.get("permissions", {})
        if not isinstance(permissions, dict):
            raise ValueError("permissions is not an object")
        rules = permissions.get(key, [])
        if not isinstance(rules, list):
            raise ValueError(f"permissions.{key} is not a list")
        return {str(e) for e in rules}
    if key != "deny":
        return set()
    parsed = _block(text)
    return (_entries(parsed[0], DENY_KEYS) if parsed else None) or set()


def _grants(cwd: str, base: str, tip: str, changed: list[str], env: dict[str, str],
            errors: list[dict]) -> list[dict]:
    """Every entry the branch ADDS to the grant surface against its merge-base with `base`:
    `tools:`/`allowed-tools:` of an agent, command or skill (an agent with no `tools:` is `*`), a
    deny rule removed (`kind: deny`), and the added lines of a hook, a CI workflow, a
    `.claude-plugin/*.json` manifest or a `.mcp.json`/`.lsp.json` server config. The agents, commands
    and skills are the ones under `LOADED_ROOT` or a root `_plugin_roots` derives. What it does not
    understand fails closed as `kind: unknown`: any other frontmatter key added, removed or changed
    (its name), a changed block it cannot read whole (`(unparsed frontmatter)`), and a sensitive
    file deleted (`(deleted)`), and every symlink the branch adds or repoints, at any path
    (`(symlink)`), its target never read. Narrowing and unchanged never appear."""
    code, out, err = _git_run(cwd, *SAFE, "merge-base", base, tip, env=env)
    if code != 0 or not out.strip():
        errors.append(_error(("merge-base", base), code, err or "no common ancestor"))
        return []
    fork = out.strip()
    code, out, err = _git_run(cwd, *SAFE, "diff", "--no-ext-diff", "--no-textconv", "--raw", "-z",
                              "--no-renames", f"{fork}..{tip}", env=env)
    if code != 0:
        errors.append(_error(("diff", "--raw"), code, err))
    fields = out.split("\0") if code == 0 else []
    symlinks = {fields[i + 1] for i in range(0, len(fields) - 1, 2)
                if fields[i].split(" ")[1:2] == [SYMLINK]}

    def show(rev: str, path: str) -> str | None:
        code, text, _e = _git_run(cwd, *SAFE, "show", "--no-textconv", f"{rev}:{path}", env=env)
        return text if code == 0 else None

    roots = _plugin_roots(cwd, (fork, tip), env, errors)
    found = []
    for path in changed:
        if path in symlinks:   # its target is never read: a link into the tree or a directory fails closed
            found.append({"path": path, "kind": "unknown", "added": ["(symlink)"]})
            continue
        by_root, agent_by_root = _component(path, roots)
        frontmatter = (FRONTMATTER_GRANT.search(path) or by_root) and not DOCS.match(path)
        surface = SURFACE.search(path)
        if not (frontmatter or surface):
            continue
        new = show(tip, path)
        if new is None:
            found.append({"path": path, "kind": "unknown", "added": ["(deleted)"]})
            continue
        old = show(fork, path)
        unparsed = False
        if frontmatter:
            agent = bool(AGENT.search(path)) or agent_by_root
            old_fm, new_fm = _block(old), _block(new)
            (old_keys, old_ok, old_raw), (new_keys, new_ok, new_raw) = (
                old_fm or ({}, True, ()), new_fm or ({}, True, ()))
            if old_raw != new_raw and not (old_ok and new_ok):
                unparsed = True
                found.append({"path": path, "kind": "unknown", "added": ["(unparsed frontmatter)"]})
            else:
                old_grants = _grant_entries(old, old_fm, agent)
                added = [] if "*" in old_grants else sorted(_grant_entries(new, new_fm, agent) - old_grants)
                if added:
                    found.append({"path": path, "kind": "tools", "added": added})
                unknown = _unknown_keys(old_keys, new_keys)
                if unknown:
                    found.append({"path": path, "kind": "unknown", "added": unknown})
        if (frontmatter and not unparsed) or SETTINGS.search(path):
            for kind in ("deny", "ask"):
                try:
                    removed = sorted(_deny_entries(path, old, kind) - _deny_entries(path, new, kind))
                except ValueError as exc:
                    errors.append(_error(("show", path), 0, f"settings unreadable: {exc}"))
                    removed = []
                if removed:
                    found.append({"path": path, "kind": kind, "added": removed})
        if surface:
            code, out, err = _git_run(cwd, *SAFE, "diff", "--no-ext-diff", "--no-textconv", "-U0",
                                      "--no-renames", f"{base}...{tip}", "--", path, env=env)
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
