"""The persistent specs worktree the `files` backend writes into, and the lock that
serialises the invocations that write there.

Moved verbatim out of `specs.py`."""
from __future__ import annotations

import datetime
import json
import os

from quenching.common.git import _git, _git_run
from quenching.common.io import read_text
from quenching.common.version import VERSION
from quenching.specs.config import DEFAULT_BACKEND, DEFAULT_SPECS_BRANCH, load_config
from quenching.specs.parse.spec import PHASE_DIRS


SPECS_WORKTREE_DIR = ".claude/worktrees"


def worktree_dir_ignored(cwd: str, rel: str = SPECS_WORKTREE_DIR) -> bool:
    """Whether git ignores the path the `files` backend puts its specs worktree at.

    `git check-ignore` prints the path when it is ignored and nothing when it is not, so the
    existing `_git` — which swallows the exit code — answers this without a second helper. A
    path that does not exist yet answers the same way, which is exactly what the guard needs:
    the question is asked BEFORE `git worktree add`, never after.

    Resolved against the repo top level, not against `cwd`: this tool's `cwd` is the specs
    workspace, and `.claude/worktrees/` relative to `<repo>/.specs/` is a different path that
    would answer the wrong question. No git and no repo answer `False` — a tree git cannot
    speak for is one where nothing can promise the worktree stays out of `git status`."""
    top = _git(cwd, "rev-parse", "--show-toplevel").strip()
    if not top:
        return False
    return bool(_git(top, "check-ignore", os.path.join(top, rel, "")).strip())


def worktree_guard(ignored: bool, rel: str = SPECS_WORKTREE_DIR) -> dict:
    """The refusal that stops the `files` backend sabotaging itself, or `{}` to proceed.

    Pure policy over the one fact `worktree_dir_ignored` establishes, kept separate from it so
    the decision is assertable without a repository to stage.

    Exit 2 rather than a warning, and rather than writing the line itself: `.gitignore` belongs
    to the target repo, and a tool that edits it uninvited to unblock its own feature is making
    the human's decision for them. Naming the one line to add is the whole remedy."""
    if ignored:
        return {}
    return {
        "code": "sp-worktree-unignored", "exit": 2, "path": rel,
        "message": f"git does not ignore '{rel}/' — add it to .gitignore before the files "
                   f"backend creates its specs worktree there; an untracked worktree breaks "
                   f"the clean-tree gate /specs:execute requires before its first task",
    }


# --------------------------------------------------------------------------- #
# the persistent specs worktree — where the `files` backend puts the specs branch
# --------------------------------------------------------------------------- #
def _repo_main_worktree(start: str) -> str:
    """The MAIN checkout of the repository `start` belongs to, or `""` when git cannot say.

    The main checkout and NOT `--show-toplevel`, because the specs worktree is ONE per
    repository and is reused: asked from inside a plan worktree, `--show-toplevel` answers with
    that plan worktree, so the backend would try to grow a second specs worktree per branch
    under development — each one wanting the same branch, which git refuses outright. Every
    linked worktree agrees on `--git-common-dir`, so it is the one answer that makes "created
    on demand and reused" true from anywhere in the repo.

    `start` may not exist yet (the default specs root is `<cwd>/specs` whether or not it is
    there), so the question is asked from the nearest ancestor that does."""
    d = os.path.abspath(start)
    while not os.path.isdir(d):
        parent = os.path.dirname(d)
        if parent == d:
            return ""
        d = parent
    common = _git(d, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()
    # `--path-format` landed in git 2.31; on an older one the flag itself fails, and the main
    # checkout is still the right answer for every repo that has no linked worktree.
    top = os.path.dirname(common) if common else _git(d, "rev-parse", "--show-toplevel").strip()
    return top if top and os.path.isdir(top) else ""


def specs_worktree_path(top: str, branch: str) -> str:
    """Where the specs branch is checked out — one fixed, derivable path per branch.

    Derived rather than recorded: a path this tool can recompute from the branch name needs no
    state file, and a second process finds the SAME worktree instead of creating a rival one.
    `/` becomes `-` so a namespaced branch (`quenching/specs`) stays one directory deep and can
    never nest inside another worktree's path."""
    return os.path.join(top, SPECS_WORKTREE_DIR, branch.replace("/", "-").strip("-") or "specs")


def _create_empty_branch(top: str, branch: str) -> tuple[int, str]:
    """Point `branch` at a commit whose tree is EMPTY, for a git too old for `--orphan`.

    `git worktree add --orphan` (git 2.42) leaves the branch unborn, which is emptier still and
    is what this prefers. Below that version the same intent costs three plumbing calls and
    lands one root commit holding nothing — the specs branch still shares no history and no
    file with the code branches, which is the property the whole design rests on.

    `mktree` over empty input is the empty tree without depending on `/dev/null` or on a
    hardcoded hash, which differs between a sha1 and a sha256 repository."""
    code, tree, err = _git_run(top, "mktree", stdin="")
    if code != 0:
        return code, err
    code, commit, err = _git_run(top, "commit-tree", tree.strip(),
                                 "-m", f"quenching: initialise the {branch} branch", stdin="")
    if code != 0:
        return code, err
    code, _, err = _git_run(top, "branch", branch, commit.strip())
    return code, err


def specs_worktree(top: str, branch: str) -> tuple[str, dict]:
    """The checkout of the specs branch the `files` backend reads and writes — reused when it
    is already there, created on demand when it is not. Returns `(path, err)`.

    PERSISTENT, not per-command: the branch is checked out once and left in place, so the cost
    of the whole design is one `git worktree add` in a repository's life and one `os.path.isdir`
    per command afterwards. A worktree created and removed around every call would pay a
    checkout per `status`.

    THE GUARD RUNS BEFORE ANYTHING IS CREATED, and only on the creation path. An unignored
    worktree is untracked content in the working tree, which breaks the clean-tree gate
    `/specs:execute` demands before its first task — the backend would sabotage the command
    that drives it. That damage is done by the `git worktree add`, so that is what the guard
    stands in front of; the reuse path creates nothing and pays no subprocess for it.

    The branch is created EMPTY when it does not exist. Not branched off the current HEAD: a
    specs branch sharing history with the code is the very thing the backend exists to undo,
    and one that starts with the whole repository in it would put every code file one merge
    away from the specs."""
    path = specs_worktree_path(top, branch)
    if os.path.isdir(path):
        # The reuse test is `--show-toplevel`, NOT `--is-inside-work-tree`: this path sits
        # inside the repository by construction, so "are you in a work tree" answers `true` for
        # any ordinary directory left there and the backend would happily write specs into a
        # folder that belongs to the code branch. Only a real linked worktree answers with its
        # OWN path as the top level.
        if os.path.realpath(_git(path, "rev-parse", "--show-toplevel").strip() or os.sep) \
                == os.path.realpath(path):
            return path, {}
        return path, {
            "code": "sp-worktree-unusable", "exit": 2, "path": path, "branch": branch,
            "message": f"'{path}' exists but git does not know it as a worktree — the files "
                       f"backend will not write specs into a directory it cannot attribute to "
                       f"the '{branch}' branch; move it aside or `git worktree repair`",
        }

    refusal = worktree_guard(worktree_dir_ignored(top))
    if refusal:
        return path, refusal

    os.makedirs(os.path.dirname(path), exist_ok=True)
    exists, _, _ = _git_run(top, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}")
    if exists == 0:
        code, _, err = _git_run(top, "worktree", "add", path, branch)
    else:
        code, _, err = _git_run(top, "worktree", "add", "--orphan", "-b", branch, path)
        if code != 0 and not os.path.isdir(path):
            # Either `--orphan` is not understood (git < 2.42) or the add failed outright. The
            # `isdir` test is what tells the two apart without parsing git's prose: a refused
            # flag creates nothing, so retrying the long way is safe; anything that got as far
            # as making the directory is reported instead of being retried on top of itself.
            code, err = _create_empty_branch(top, branch)
            if code == 0:
                code, _, err = _git_run(top, "worktree", "add", path, branch)
    if code != 0 or not os.path.isdir(path):
        return path, {
            "code": "sp-worktree-failed", "exit": 2, "path": path, "branch": branch,
            "git": err.strip(),
            "message": f"could not check out the specs branch '{branch}' at '{path}' — git "
                       f"said: {err.strip() or 'nothing'}",
        }
    return path, {}


def _inside_worktree_dir(path: str, rel: str = SPECS_WORKTREE_DIR) -> bool:
    """Whether `path` already sits under a worktree directory, so nothing nests another one
    inside it. Compared segment by segment rather than as a substring — a repository legitimately
    named `.claude/worktrees-archive` is not a worktree."""
    parts = os.path.abspath(path).split(os.sep)
    want = rel.split("/")
    return any(parts[i:i + len(want)] == want for i in range(len(parts)))


def _holds_phase_folder(root: str) -> bool:
    return any(os.path.isdir(os.path.join(root, p)) for p in PHASE_DIRS)


def resolve_files_root(root: str, cfg: dict) -> tuple[str, dict]:
    """Which directory the `files` backend actually operates on: the workspace as declared, or
    the persistent worktree of the specs branch. Returns `(root, err)`.

    Three shapes answer WITHOUT git, and they answer first — which is what keeps the resolution
    free for everything that is not a migrated repository, and what lets the backend be
    exercised over a bare temp directory with no repository at all:

      already inside a worktree   nothing nests a worktree in a worktree; the specs branch is
                                  already the tree underfoot.
      the workspace is populated  a `/.specs/` holding phase folders in the code tree is the
                                  PRE-MIGRATION store and stays authoritative until a human
                                  moves it. Switching silently would make every repository that
                                  upgrades this tool look like it had lost every spec it has —
                                  the loudest regression this change could ship, and the one
                                  this repository would have taken on the very next `list`.
                                  Moving those files is deliberate work (`## Out of Scope`),
                                  so the presence of the old store is the honest signal that it
                                  has not happened yet.
      no repository               there is no branch to check out, so there is nowhere else the
                                  specs could be.

    Otherwise the specs live on the specs branch, and the worktree is created on demand. The
    workspace keeps its own basename inside it, so `SPECS_ROOT=<x>/design` resolves to
    `<worktree>/design` and the layout is the same on both sides of the migration.

    Memoised per declared root: the answer costs subprocesses, and it is asked twice per
    writing command — once by `writer_lock`, once by `open_backend`. The cache is what makes
    the lock and the backend point at the SAME worktree by construction rather than by two
    resolutions agreeing."""
    if root in _FILES_ROOT_CACHE:
        return _FILES_ROOT_CACHE[root]
    out = _resolve_files_root(root, cfg)
    _FILES_ROOT_CACHE[root] = out
    return out


_FILES_ROOT_CACHE: dict[str, tuple[str, dict]] = {}


def _resolve_files_root(root: str, cfg: dict) -> tuple[str, dict]:
    if _inside_worktree_dir(root) or _holds_phase_folder(root):
        return root, {}
    top = _repo_main_worktree(root)
    if not top:
        return root, {}
    path, err = specs_worktree(top, cfg.get("specsBranch") or DEFAULT_SPECS_BRANCH)
    if err:
        return root, err
    return os.path.join(path, os.path.basename(os.path.normpath(root)) or ".specs"), {}


def files_specs_worktree(root: str, cfg: dict) -> tuple[str | None, dict]:
    """The specs worktree the `files` backend resolved to, or `None` when it did not use one.

    `None` is not a failure — it is the pre-migration workspace still sitting in the code tree,
    which is a legal and currently common state. Anything that guards the worktree has to be
    able to tell the two apart without triggering a second resolution."""
    target, err = resolve_files_root(root, cfg)
    if err:
        return None, err
    if os.path.abspath(target) == os.path.abspath(root):
        return None, {}
    return os.path.dirname(os.path.abspath(target)), {}


# --------------------------------------------------------------------------- #
# the specs worktree lock — one writer at a time, per worktree
# --------------------------------------------------------------------------- #
LOCK_SUFFIX = ".lock"
LOCK_WAIT_SECONDS = 10.0
LOCK_POLL_SECONDS = 0.05


def specs_lock_path(worktree: str) -> str:
    """`<…>/.claude/worktrees/<name>.lock` — BESIDE the worktree, never inside it.

    Inside, the lock would be untracked content in the one tree whose whole job is to hold a
    clean, committable set of specs, and every `git status` run there would report the tool's
    own bookkeeping. Beside, it is already covered by the `.claude/worktrees/` ignore rule that
    `worktree_guard` refuses to run without — so the lock costs no new ignore line, and cannot
    dirty the code tree either."""
    return os.path.normpath(worktree) + LOCK_SUFFIX


def _lock_holder(path: str) -> dict:
    """Who the lock file says is holding it. An unreadable or unparseable lock comes back as an
    empty record rather than as an error: the file existing is the lock, and its contents are
    only ever used to describe the holder to a human or to prove it is gone."""
    try:
        obj = json.loads(read_text(path) or "")
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        return {}


def _holder_is_gone(info: dict) -> bool:
    """True ONLY when this process can prove the recorded holder no longer exists.

    AGE IS NEVER THE REASON. "The lock is old, so I will take it" is the tempting rule and the
    wrong one: a `promote` on a slow filesystem and a crashed process look identical through a
    timestamp, and the fast case for guessing wrong is two writers in the same document. Age
    appears in the refusal message as information for the human and never as a decision.

    Proof, and the three things that make it unavailable:

      another host      a pid is meaningless off the machine that issued it, and a specs
                        worktree on a network share can legitimately be held from elsewhere.
      not POSIX         `os.kill(pid, 0)` is a liveness probe on POSIX and NOT on Windows,
                        where `os.kill` terminates the target whatever signal it is handed.
                        A probe that kills the process it asks about is not a probe.
      pid alive, or not ours  `ProcessLookupError` is the only answer that proves absence.
                        `PermissionError` means it is running under another user, which is
                        alive. Pid reuse can only make a dead holder look ALIVE, which errs
                        toward refusing — the safe direction."""
    import socket
    if os.name != "posix":
        return False
    if str(info.get("host") or "") != socket.gethostname():
        return False
    try:
        pid = int(info.get("pid") or 0)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except (OSError, OverflowError):
        return False
    return False


class SpecsLock:
    """Serialises the `specs.py` invocations that WRITE into one specs worktree.

    THE SCOPE IS THE WHOLE COMMAND, not the write syscall. Every writing command is a
    read-modify-write — `task --check` reads the document, flips one character, writes the
    whole file back — so a lock held only around the write would still let two processes read
    the same document and each store its own edit over the other's. Nothing would look corrupt
    and one tick would simply be gone, which is the worse failure: it leaves no trace.

    ONE LOCK PER WORKTREE, because the worktree is the resource. Two agents ticking tasks on
    DIFFERENT specs do contend under this, and that is right rather than unfortunate: they
    share one checkout of one branch, and the next thing that touches it commits everything in
    it. Contention costs milliseconds — the work under the lock is one parse and one rename.

    `O_CREAT | O_EXCL` is the primitive, not `fcntl` and not `msvcrt.locking`: exclusive create
    is one syscall with the same meaning on POSIX and on Windows, and this tool ships to both
    (`_force_utf8_output` is here for the same reason). The cost is a file left behind when a
    process dies, which is what `_holder_is_gone` answers; the gain is a lock with no platform
    branch inside it.

    READERS TAKE NO LOCK. `list`, `status`, `show`, `next`, `validate` and `doctor` are the
    commands a skill calls most, several of them per turn, and putting them in a queue behind a
    writer would make the lock the front's throughput limit. What makes that safe is not luck:
    `write_text` replaces a document by rename, so a reader sees the old text or the new one and
    never a half-written file."""

    def __init__(self, path: str, label: str = "") -> None:
        self.path = path
        self.label = label
        self.held = False

    def acquire(self, wait: float = LOCK_WAIT_SECONDS) -> dict:
        """`{}` once held, or a ready-to-emit refusal naming the holder. Never raises, never
        waits forever: a bounded wait absorbs the normal case, where the process ahead is
        finishing a rename, and anything beyond it is reported to whoever can act on it."""
        import socket
        import time
        deadline = time.monotonic() + max(0.0, wait)
        record = json.dumps({"pid": os.getpid(), "host": socket.gethostname(),
                             "command": self.label, "since": _now_iso(),
                             "tool": f"specs.py {VERSION}"}, ensure_ascii=False)
        while True:
            try:
                os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            except FileExistsError:
                pass
            except OSError as e:
                return {"code": "sp-lock-unwritable", "exit": 2, "path": self.path,
                        "message": f"could not create the specs worktree lock at "
                                   f"'{self.path}': {e}"}
            else:
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    fh.write(record)
                self.held = True
                return {}

            holder = _lock_holder(self.path)
            if _holder_is_gone(holder):
                try:
                    os.remove(self.path)      # PROVEN dead — not merely old
                except OSError:
                    pass                      # someone else got there first, or we may not
            else:
                time.sleep(LOCK_POLL_SECONDS)
            if time.monotonic() >= deadline:
                return self._refusal(holder, wait)

    def _refusal(self, holder: dict, waited: float) -> dict:
        who = (f"pid {holder.get('pid')} on {holder.get('host')}"
               if holder.get("pid") else "an unidentified process")
        what = f" running `{holder['command']}`" if holder.get("command") else ""
        since = f" since {holder['since']}" if holder.get("since") else ""
        return {
            "code": "sp-specs-locked", "exit": 2, "path": self.path, "holder": holder,
            "waited": round(waited, 2),
            "message": f"the specs worktree is locked by {who}{what}{since} — waited "
                       f"{waited:g}s and gave up; nothing was written. If that process is gone, "
                       f"delete '{self.path}'",
        }

    def release(self) -> None:
        """Drop the lock. Idempotent and silent about a file already gone — a release that
        raised would turn a successful write into a nonzero exit in the `finally` that runs
        after it."""
        if not self.held:
            return
        self.held = False
        try:
            os.remove(self.path)
        except OSError:
            pass

    def __enter__(self) -> "SpecsLock":
        return self

    def __exit__(self, *exc) -> None:
        self.release()


def _now_iso() -> str:
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def command_writes(args) -> bool:
    """Whether THIS invocation will modify a spec — the scope the lock is taken for.

    Per invocation and not per subcommand: `section` without `--write` and `promote --dry-run`
    read and report, and queueing them behind a writer would put the lock in front of the two
    reads a skill makes most.

    `migrate` is deliberately absent. It rewrites the DECLARED workspace's own folder layout —
    the pre-migration `/.specs/` in the code tree — and never touches the specs worktree, so the
    worktree's lock would guard nothing it writes. `release` is absent for the same reason: it
    writes the plugin's own version-carrying artifacts, never a spec."""
    cmd = getattr(args, "cmd", "")
    if cmd in ("new", "task", "discover"):
        return True
    if cmd == "section":
        return bool(getattr(args, "write", False))
    if cmd == "record":
        return bool(getattr(args, "set", None))
    if cmd == "verification":
        return bool(getattr(args, "policy", None))
    if cmd == "promote":
        return not bool(getattr(args, "dry_run", False))
    return False


def writer_lock(args, root: str) -> tuple[SpecsLock | None, dict]:
    """The lock this invocation must hold before it runs, or `(None, {})` when it needs none.

    Three ways to need none, each a fact about where the specs are rather than a policy:

      the command only reads    see `command_writes`.
      an external backend       GitHub and Azure Boards serialise on their own server; a local
                                file could not make a remote write atomic and would only add a
                                second thing to get stuck.
      no specs worktree         a pre-migration workspace in the code tree has nowhere to put a
                                lock that git ignores, and an untracked file there is exactly
                                the breakage `worktree_guard` exists to prevent. It is left
                                unserialised knowingly — that workspace is the state this
                                backend exists to end, and adding a second untracked artifact
                                to it would buy safety for a layout on its way out at the price
                                of the clean-tree gate `/specs:execute` runs under."""
    if not command_writes(args):
        return None, {}
    cfg = load_config(root)
    if cfg["backend"] != DEFAULT_BACKEND:
        return None, {}
    worktree, err = files_specs_worktree(root, cfg)
    if err:
        return None, err
    if worktree is None:
        return None, {}
    lock = SpecsLock(specs_lock_path(worktree), label=_invocation_label(args))
    return lock, lock.acquire()


def _invocation_label(args) -> str:
    """A short, honest name for what is holding the lock — the subcommand and the spec it is
    writing. Read by a human staring at a refusal, so it names the spec rather than echoing the
    whole argv, which would carry `--json` and other noise into the message."""
    spec = getattr(args, "spec", None) or getattr(args, "title", None) or ""
    return f"{getattr(args, 'cmd', '?')} {spec}".strip()
