"""`cq git worktree acquire | release | slots` — reusable worktrees, bounded by two limits.

A slot is a registered worktree at `../<repo>-slot-<n>` that outlives its spec. Acquiring one
switches it to the spec's branch and locks it; releasing it detaches it at the remote base and
unlocks it, keeping `.venv` and every other regenerable cache. A fresh worktree costs a scan of
every file an on-access antivirus sees (tens of thousands with a venv); a branch switch rewrites
only what differs.

`git worktree lock` is the mutex: it fails on a tree already locked, so two sessions racing for
the same free slot cannot both win. Only slots count toward `shared.worktreeSlots.max`; any other
worktree is listed and never counted, never taken.
"""
from __future__ import annotations

import contextlib
import datetime
import os
import re
import shutil
import socket
import sys
import time

from quenching.common.config import load_config, namespace
from quenching.common.git import _git_run
from quenching.common.output import FINDINGS, emit, refuse
from quenching.git.audit import SAFE, _branch_ok, _commit, _run
from quenching.git.ignored import _is_link, declared_regenerable, ignored_entries, undeclared
from quenching.git.push import remote_probe

DEFAULTS = {"min": 4, "max": 12, "waitMinutes": 30, "pollSeconds": 30}
REASON_PREFIX = "quenching: "
SEP = " · "


def limits(repo: str) -> dict:
    """`shared.worktreeSlots`, each key falling back to its default when absent or not a
    positive integer; `max` never drops below `min`."""
    raw = namespace(load_config(repo), "shared").get("worktreeSlots")
    raw = raw if isinstance(raw, dict) else {}
    out = {}
    for key, default in DEFAULTS.items():
        value = raw.get(key)
        out[key] = value if isinstance(value, int) and not isinstance(value, bool) \
            and value > 0 else default
    out["max"] = max(out["max"], out["min"])
    return out


def _worktrees(cwd: str) -> list[dict]:
    """Every registered worktree, the primary first, read NUL-separated so a lock reason arrives
    unquoted."""
    code, out, _err = _git_run(cwd, *SAFE, "worktree", "list", "--porcelain", "-z")
    found, cur = [], {}
    for field in (out.split("\0") if code == 0 else []):
        if not field:
            if cur:
                found.append(cur)
            cur = {}
            continue
        key, _, value = field.partition(" ")
        if key == "worktree":
            cur = {"path": value, "branch": None, "detached": False, "locked": None}
        elif key == "branch":
            cur["branch"] = value.removeprefix("refs/heads/")
        elif key == "detached":
            cur["detached"] = True
        elif key == "locked":
            cur["locked"] = value
        elif key == "prunable":
            cur["prunable"] = True
    if cur:
        found.append(cur)
    return found


def _slot_pattern(primary: str) -> re.Pattern:
    return re.compile(re.escape(os.path.basename(os.path.realpath(primary))) + r"-slot-(\d+)$")


def parse_reason(reason: str | None) -> dict | None:
    """`{spec, session, host, date}` of a quenching lock reason, or None for any other lock."""
    if not reason or not reason.startswith(REASON_PREFIX):
        return None
    parts = reason[len(REASON_PREFIX):].split(SEP)
    parts += [""] * (4 - len(parts))
    return dict(zip(("spec", "session", "host", "date"), parts[:4]))


def lock_reason(holder: str, session: str | None) -> str:
    session = session or os.environ.get("OPENCODE_SESSION_ID") \
        or os.environ.get("CLAUDE_SESSION_ID") or "-"
    date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return REASON_PREFIX + SEP.join((holder, session, socket.gethostname(), date))


def survey(cwd: str) -> dict:
    """The slots and the other worktrees, as `slots` reports them."""
    trees = _worktrees(cwd)
    primary = trees[0]["path"] if trees else cwd
    pattern = _slot_pattern(primary)
    parent = os.path.dirname(os.path.realpath(primary))
    slots, others = [], []
    for tree in trees[1:]:
        match = pattern.match(os.path.basename(tree["path"]))
        if match and os.path.dirname(os.path.realpath(tree["path"])) == parent:
            slots.append({**tree, "n": int(match.group(1)),
                          "state": "held" if tree["locked"] is not None else "free",
                          "holder": parse_reason(tree["locked"])})
        else:
            kind = "opencode" if "/opencode/worktree/" in tree["path"] else "legacy"
            others.append({**tree, "kind": kind})
    slots.sort(key=lambda s: s["n"])
    return {"primary": primary, "parent": parent, "slots": slots, "others": others,
            "name": os.path.basename(os.path.realpath(primary))}


def _dirty(path: str) -> bool | None:
    code, out, _err = _git_run(path, *SAFE, "status", "--porcelain", "--untracked-files=normal")
    return None if code != 0 else bool(out.strip())


def _fetch_base(cwd: str, remote: str, base: str) -> tuple[str | None, str, dict | None]:
    """`(sha, label, refusal)` of the base to switch from: the fetched remote base, or the local
    one when the remote does not exist."""
    has_remote = remote_probe(cwd, remote)
    if has_remote is None:
        return None, "", {"code": "git-worktree-remote-unreadable",
                          "message": f"git could not read the remote: {remote}"}
    if has_remote:
        code, _out, err = _git_run(cwd, *SAFE, "fetch", "--no-recurse-submodules", "--",
                                   remote, f"refs/heads/{base}")
        if code != 0:
            return None, "", {"code": "git-worktree-fetch-failed",
                              "message": f"git fetch {remote} {base} failed: {err.strip()}"}
        return _commit(cwd, f"refs/remotes/{remote}/{base}"), f"{remote}/{base}", None
    return _commit(cwd, f"refs/heads/{base}"), base, None


def _default_base(cwd: str, remote: str) -> str:
    """The remote's HEAD branch, else `init.defaultBranch`, else `main`."""
    code, out, _err = _git_run(cwd, *SAFE, "symbolic-ref", "--short", f"refs/remotes/{remote}/HEAD")
    if code == 0 and out.strip().startswith(f"{remote}/"):
        return out.strip()[len(remote) + 1:]
    code, out, _err = _git_run(cwd, *SAFE, "config", "init.defaultBranch")
    return out.strip() if code == 0 and out.strip() else "main"


@contextlib.contextmanager
def _creation_lock(cwd: str, timeout: float = 60.0):
    """Serialise slot creation across processes with an `O_EXCL` file in git's common directory;
    a lock older than `timeout` is a crashed taker's and is broken."""
    code, out, _err = _git_run(cwd, *SAFE, "rev-parse", "--path-format=absolute",
                               "--git-common-dir")
    lock = os.path.join(out.strip() if code == 0 else cwd, "quenching-slots.lock")
    start = time.monotonic()
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(lock) > timeout:
                    os.unlink(lock)
                    continue
            except OSError:
                continue
            if time.monotonic() - start > timeout:
                raise TimeoutError(f"slot creation lock held: {lock}")
            time.sleep(0.05)
    try:
        os.close(fd)
        yield
    finally:
        with contextlib.suppress(OSError):
            os.unlink(lock)


def _lock(cwd: str, path: str, reason: str) -> bool:
    return _git_run(cwd, *SAFE, "worktree", "lock", "--reason", reason, "--", path)[0] == 0


def _unlock(cwd: str, path: str) -> None:
    _git_run(cwd, *SAFE, "worktree", "unlock", "--", path)


def _merged_holder(cwd: str, slot: dict, base_sha: str | None) -> bool:
    """A held slot whose branch carries work and is already in the base: its spec is done and
    the slot may go. A branch just cut has no work, and its tip — the base it was cut from — is
    an ancestor of the base too; its reflog, holding only the creation, is what tells them apart.
    No reflog → not provably merged, so the slot is never taken."""
    branch = slot.get("branch")
    tip = _commit(cwd, f"refs/heads/{branch}") if branch else None
    if not (tip and base_sha):
        return False
    code, out, _err = _git_run(cwd, *SAFE, "reflog", "show", "--format=%H", f"refs/heads/{branch}")
    if code != 0 or len(out.split()) < 2:
        return False
    return _run(cwd, "merge-base", "--is-ancestor", tip, base_sha)[0] == 0


def _take(cwd: str, view: dict, cap: int, reason: str, base_sha: str,
          freed: list) -> tuple[dict | None, bool]:
    """Lock one slot for the caller: a free clean one, else a new one under the cap, else a held
    one whose branch is merged and whose tree is clean (released first). `(slot, created)`."""
    for slot in view["slots"]:
        if slot["state"] == "free" and _lock(cwd, slot["path"], reason):
            if _dirty(slot["path"]) is False:
                return slot, False
            _unlock(cwd, slot["path"])
    with _creation_lock(cwd):
        # Counted again under the lock: two takers that both saw room must not both cut.
        current = survey(cwd)["slots"]
        if len(current) < cap:
            used = {s["n"] for s in current}
            n = next(i for i in range(1, cap + 2) if i not in used
                     and not os.path.lexists(os.path.join(view["parent"],
                                                          f"{view['name']}-slot-{i}")))
            path = os.path.join(view["parent"], f"{view['name']}-slot-{n}")
            code, _out, _err = _git_run(cwd, *SAFE, "worktree", "add", "--detach", "--lock",
                                        "--reason", reason, "--", path, base_sha)
            if code == 0:
                return {"path": path, "n": n, "branch": None}, True
    for slot in view["slots"]:
        if slot["state"] == "held" and slot["holder"] and _merged_holder(cwd, slot, base_sha) \
                and _dirty(slot["path"]) is False:
            # Re-lock under the caller's reason only after the merged holder's lock is gone; a
            # second session racing here loses at `lock`, never both win.
            _unlock(cwd, slot["path"])
            if _lock(cwd, slot["path"], reason):
                freed.append({"path": slot["path"], "branch": slot["branch"],
                              "spec": slot["holder"].get("spec")})
                return slot, False
    return None, False


def _holders(view: dict) -> list[dict]:
    return [{"slot": s["n"], "path": s["path"], "branch": s["branch"],
             **(s["holder"] or {"lock": s["locked"]}),
             "release": f"cq git worktree release --path {s['path']}"}
            for s in view["slots"] if s["state"] == "held"]


def acquire(args) -> int:
    """Lock a slot, switch it to `--branch`, link the shared paths and run `worktreeSetup`."""
    from quenching.git.worktree import _link, _link_lines, _setup, _stamp_branch
    from quenching.git.pull import _spec_vs_head

    cwd = os.getcwd()
    missing = [f"--{k}" for k in ("branch", "base") if not getattr(args, k)]
    if missing:
        return refuse({"code": "git-worktree-acquire-args",
                       "message": f"`worktree acquire` needs {', '.join(missing)}"}, args.json)
    for label, value in (("branch", args.branch), ("base", args.base), ("remote", args.remote)):
        if not value or value.startswith("-") or not _branch_ok(cwd, value):
            return refuse({"code": "git-worktree-ref-invalid",
                           "message": f"{label} is not a usable name: {value}"}, args.json)
    if args.spec:
        bad = _spec_vs_head(args.spec, args.branch, by_name=False)
        if bad:
            return refuse({**bad, "code": bad["code"].replace("git-pr-", "git-worktree-")},
                          args.json)
    view = survey(cwd)
    for tree in view["slots"] + view["others"]:
        if tree.get("branch") == args.branch:
            mine = tree in view["slots"]
            payload = {"ok": mine, "path": tree["path"], "branch": args.branch, "reused": True,
                       "message": f"{args.branch} is already checked out at {tree['path']}"}
            if not mine:
                return refuse({**payload, "code": "git-worktree-branch-held"}, args.json)
            emit(args.json, payload, f"slot: {tree['path']} (already holds {args.branch})")
            return 0
    base_sha, start, refusal = _fetch_base(cwd, args.remote, args.base)
    if refusal or base_sha is None:
        return refuse(refusal or {"code": "git-worktree-ref-invalid",
                                  "message": f"the base does not resolve: {args.base}"}, args.json)
    cap = limits(view["primary"])
    reason = lock_reason(str(args.spec or args.branch), getattr(args, "session", None))
    wait = getattr(args, "wait", False)
    deadline = time.monotonic() + 60 * (getattr(args, "timeout_minutes", None)
                                        or cap["waitMinutes"])
    freed: list = []
    announced = False
    while True:
        slot, created = _take(cwd, view, cap["max"], reason, base_sha, freed)
        if slot or not wait or time.monotonic() >= deadline:
            break
        if not announced:
            print(f"slot limit reached ({cap['max']}): waiting for a slot — every "
                  f"{cap['pollSeconds']}s, up to {cap['waitMinutes']} min", file=sys.stderr,
                  flush=True)
            announced = True
        time.sleep(cap["pollSeconds"])
        view = survey(cwd)
    if slot is None:
        code = "git-worktree-slots-timeout" if wait else "git-worktree-slots-full"
        holders = _holders(survey(cwd))
        return refuse({"code": code, "max": cap["max"], "holders": holders,
                       "needsHuman": wait,
                       "message": f"all {cap['max']} slots are held"
                                  + ("; the wait timed out" if wait else "")
                                  + " — tell the human the limit was reached; a stale lock is "
                                    "released with the command each holder names"}, args.json)
    path = slot["path"]
    if _commit(cwd, f"refs/heads/{args.branch}") is not None:
        switch = ("switch", args.branch)
    else:
        switch = ("switch", "--no-track", "-c", args.branch, base_sha)
    code, _out, err = _git_run(path, *SAFE, *switch)
    if code != 0:
        _git_run(path, *SAFE, "switch", "--detach", base_sha)
        _unlock(cwd, path)
        return refuse({"code": "git-worktree-switch-failed", "path": path,
                       "message": f"git switch failed in {path}: {err.strip()}"}, args.json)
    results, link_refusal = _link(path)
    stamp = _stamp_branch(args.spec, args.base, args.branch) if args.spec else None
    setup = None if link_refusal or args.no_setup else _setup(path)
    payload = {"ok": link_refusal is None and (stamp is None or stamp["ok"])
                     and (setup is None or setup["ok"]),
               "path": path, "slot": slot["n"], "created": created, "reused": not created,
               "branch": args.branch, "base": args.base, "start": start, "startSha": base_sha,
               "lock": reason, "freed": freed, "paths": results or [],
               "linkRefusal": link_refusal, "setup": setup}
    if stamp:
        payload["branchRecord"] = stamp
    human = [f"slot {slot['n']}: {path} ({'new' if created else 'reused'})",
             f"branch: {args.branch} from {start} ({base_sha[:12]})"]
    human += [f"freed: {f['path']} (merged {f['branch']})" for f in freed]
    human += _link_lines(results or [])
    if link_refusal:
        human.append(f"link refused: {link_refusal.get('message')}")
    if stamp:
        human.append(f"`branch` record stamped for spec {args.spec}" if stamp["ok"]
                     else f"`branch` record not stamped: {stamp['message']}")
    if setup:
        human.append(f"setup ran: {setup['command']}" if setup["ok"]
                     else f"setup failed (exit {setup['exit']}): {setup['command']}")
    emit(args.json, payload, "\n".join(human))
    return 0 if payload["ok"] else FINDINGS


def release(args) -> int:
    """Detach a clean slot at the remote base and unlock it; `branch -d` its branch when merged.

    A dirty tree, or ignored content no `shared.regenerablePaths` entry covers, keeps the slot
    held (exit 1): nothing of one spec may leak into the next, and nothing is committed or
    discarded to free it."""
    cwd = os.getcwd()
    view = survey(cwd)
    want = os.path.realpath(args.path) if args.path else None
    match = [s for s in view["slots"]
             if (want and os.path.realpath(s["path"]) == want)
             or (not want and args.branch and s["branch"] == args.branch)]
    if not match:
        return refuse({"code": "git-worktree-release-not-a-slot",
                       "message": f"not a slot of this repository: {args.path or args.branch}"
                                  " — a worktree that is not a slot is removed with `retire`"},
                      args.json)
    slot = match[0]
    path, branch = slot["path"], slot["branch"]
    base = args.base or _default_base(cwd, args.remote)
    if not _branch_ok(cwd, base) or not _branch_ok(cwd, args.remote):
        return refuse({"code": "git-worktree-ref-invalid",
                       "message": f"base or remote is not a usable name: {base}"}, args.json)
    dirty = _dirty(path)
    if dirty is None:
        return refuse({"code": "git-worktree-release-status-failed",
                       "message": f"git status failed in {path}"}, args.json)
    payload = {"ok": False, "path": path, "slot": slot["n"], "branch": branch,
               "released": False, "branchDeleted": False, "archived": None}
    if dirty:
        payload["message"] = f"{path} has uncommitted changes; the slot stays held"
        emit(args.json, payload, payload["message"])
        return FINDINGS
    ignored = ignored_entries(path)
    if ignored is None:
        return refuse({"code": "git-worktree-release-status-failed",
                       "message": f"git status failed in {path}"}, args.json)
    rules = declared_regenerable(load_config(view["primary"]))
    left = [e for e in undeclared(path, ignored, rules)
            if not e.replace(os.sep, "/").startswith(".quenching/codex")]
    if left:
        payload.update(ignored=left, message=f"{path} holds ignored files no "
                       f"shared.regenerablePaths entry covers: {', '.join(left)}; the slot stays held")
        emit(args.json, payload, payload["message"])
        return FINDINGS
    base_sha, start, refusal = _fetch_base(cwd, args.remote, base)
    if refusal or base_sha is None:
        return refuse(refusal or {"code": "git-worktree-ref-invalid",
                                  "message": f"the base does not resolve: {base}"}, args.json)
    source = os.path.join(path, ".quenching", "codex")
    if os.path.isdir(source) and not _is_link(source):
        archived = os.path.join(view["primary"], ".quenching", "codex", "retired",
                                f"{os.path.basename(path)}-{(branch or 'detached').replace('/', '-')}")
        suffix, target = 2, archived
        while os.path.lexists(target):
            target, suffix = f"{archived}-{suffix}", suffix + 1
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.move(source, target)
        payload["archived"] = target
    code, _out, err = _git_run(path, *SAFE, "switch", "--detach", base_sha)
    if code != 0:
        payload["message"] = f"git switch --detach failed in {path}: {err.strip()}"
        emit(args.json, payload, payload["message"])
        return FINDINGS
    _unlock(cwd, path)
    payload.update(ok=True, released=True, base=start)
    tip = _commit(cwd, f"refs/heads/{branch}") if branch else None
    if tip and _run(cwd, "merge-base", "--is-ancestor", tip, base_sha)[0] == 0:
        payload["branchDeleted"] = _git_run(cwd, *SAFE, "branch", "-d", "--", branch)[0] == 0
    emit(args.json, payload, f"released slot {slot['n']}: {path} detached at {start}"
         + (f"; branch {branch} deleted" if payload["branchDeleted"] else
            (f"; branch {branch} kept (not merged)" if branch else "")))
    return 0


def slots(args) -> int:
    """List the slots, who holds each, and the worktrees that are not slots (never counted)."""
    view = survey(os.getcwd())
    cap = limits(view["primary"])
    held = [s for s in view["slots"] if s["state"] == "held"]
    payload = {"ok": True, **cap, "count": len(view["slots"]), "held": len(held),
               "free": len(view["slots"]) - len(held),
               "slots": [{"slot": s["n"], "path": s["path"], "state": s["state"],
                          "branch": s["branch"], "holder": s["holder"], "lock": s["locked"]}
                         for s in view["slots"]],
               "others": [{"path": o["path"], "branch": o["branch"], "kind": o["kind"]}
                          for o in view["others"]]}
    human = [f"slots: {payload['count']} of {cap['max']} ({len(held)} held, "
             f"{payload['free']} free; floor {cap['min']})"]
    for s in view["slots"]:
        who = s["holder"] or {}
        human.append(f"  slot {s['n']:<3} {s['state']:<5} {s['branch'] or '(detached)'}"
                     + (f"  — {who.get('spec')} · {who.get('session')} · {who.get('date')}"
                        if who else ""))
    for o in view["others"]:
        human.append(f"  {o['kind']:<9} {o['path']}  {o['branch'] or '(detached)'}  (not counted)")
    emit(args.json, payload, "\n".join(human))
    return 0
