"""The `git` backend — specs as files on a dedicated branch of the code repository's remote.

The branch (`quenching` by default) holds one canonical document per spec and nothing derived:

    specs/<id>.md          an open spec (`plans`)
    specs/archive/<id>.md  an archived spec (`archive`)
    specs/.next-id         the next ID to allocate when no tracker owns identity
    quenching.json         the specs-axis configuration, under the `specs` namespace

Nothing is ever checked out. Reads are `git ls-tree` plus one `git cat-file --batch` over the
remote-tracking ref, with the clone's unsent writes laid over it. A write builds ONE local pending
commit (`refs/quenching/pending/<branch>`, shared by every worktree of the clone, never pushed)
with a throwaway index and moves that ref by compare-and-swap (`update-ref <new> <old>`); the
remote sees it only at a sync. A lost compare-and-swap re-applies the SAME semantic operation,
never a text merge, and a document that changed under the caller refuses as a stale write
instead of being overwritten.

Every mutation of the pending ref and of the branch funnels through `_store`, the name the
read-only specs-reader already blocks."""
from __future__ import annotations

import hashlib
import json
import os
import random
import shutil
import subprocess
import tempfile
import time

from quenching.common.config import find_repo_root
from quenching.common.leak import guard_store_write, patterns, scan_text, store_refusal
from quenching.specs.backends.base import BackendRefusal, SpecBackend
from quenching.specs.parse import PHASES, derive_info, derive_labels, resolve_one


STORE_BRANCH = "quenching"
DEFAULT_REMOTE = "origin"
SPECS_DIR = "specs"
PHASE_DIRS = {"plans": "specs", "archive": "specs/archive"}
COUNTER_PATH = "specs/.next-id"
CONFIG_PATH = "quenching.json"
LOCATOR_PREFIX = "quenching:"
COMMIT_PREFIX = "[skip ci] specs:"
FETCH_TTL_S = 30
TIP_MEMO_S = 1.0   # one read pass resolves the tip once; a longer-lived process re-reads it
MAX_ATTEMPTS = 5
CACHE_VERSION = 1
GIT_TIMEOUT_S = 120
NO_FETCH_ENV = "QUENCHING_SPECS_NO_FETCH"
PENDING_PREFIX = "refs/quenching/pending/"

# A push the remote turned down because someone else moved the branch first — the one failure
# that is retried. Anything else (auth, network, a protected branch) refuses at once.
_REJECTED_MARKERS = ("[rejected]", "non-fast-forward", "fetch first", "stale info",
                     "cannot lock ref", "failed to update ref", "is at ")


def _refusal(code: str, message: str, **extra) -> BackendRefusal:
    return BackendRefusal({"code": code, "exit": 2, "message": message, **extra})


def stale_write_refusal(spec_id: int, expected: str, actual: str | None) -> BackendRefusal:
    """The document changed on the branch after the caller read it."""
    return _refusal(
        "sp-git-stale-write",
        f"spec {spec_id} changed on branch '{STORE_BRANCH}' after it was read — expected blob "
        f"{expected[:12]}, found {(actual or 'none')[:12]}; re-read the spec and reapply the "
        "change instead of merging two documents automatically",
        id=spec_id, expectedBlob=expected, actualBlob=actual,
        remedy="re-read the spec and reapply the change")


def conflict_refusal(conflicts: list[dict]) -> BackendRefusal:
    """The same spec changed locally and on the remote since the pending writes were based."""
    named = "; ".join(f"spec {c['id']}: local blob {(c['localBlob'] or 'none')[:12]}, remote blob "
                      f"{(c['remoteBlob'] or 'none')[:12]}" for c in conflicts)
    return _refusal(
        "sp-git-stale-write",
        f"unsent local writes conflict with branch '{STORE_BRANCH}' — {named}; recover the local "
        "text with `git cat-file -p <local blob>`, then discard it with `cq specs push --drop <id>` "
        "and reapply the change on the remote document",
        conflicts=conflicts, ids=[c["id"] for c in conflicts],
        remedy="recover the local text, then `cq specs push --drop <id>`")


def _spec_id(path: str) -> int | None:
    """The spec a store path belongs to: `specs/<id>.md` and `specs/archive/<id>.md` are one."""
    for phase_dir in PHASE_DIRS.values():
        rest = path[len(phase_dir) + 1:] if path.startswith(phase_dir + "/") else ""
        if rest.endswith(".md") and rest[:-3].isdigit() and "/" not in rest:
            return int(rest[:-3])
    return None


def _spec_paths(spec_id: int) -> tuple[str, ...]:
    return tuple(f"{phase_dir}/{spec_id}.md" for phase_dir in PHASE_DIRS.values())


class _Blob(str):
    """A change value that is already an object in the store: written by sha, never re-hashed."""


def _cache_path(key: str) -> str:
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    digest = hashlib.sha256(key.encode()).hexdigest()[:32]
    return os.path.join(base, "quenching", "git", f"{digest}.json")


_UNSET = object()


class GitBackend(SpecBackend):
    """Specs on a git branch, written by plumbing and read from the remote-tracking ref.

    `mirror_dir` selects the read-only mode: objects and refs live in a bare repository there,
    fetched from the target's remote URL, so a reader never writes into the target's `.git`."""

    name = "git"

    def __init__(self, repo_root: str, remote: str = DEFAULT_REMOTE,
                 branch: str = STORE_BRANCH, mirror_dir: str | None = None,
                 remote_url: str | None = None, card=_UNSET) -> None:
        self.repo_root = os.path.abspath(repo_root)
        self.remote = remote
        self.branch = branch
        self.mirror_dir = os.path.abspath(mirror_dir) if mirror_dir else None
        self.read_only = self.mirror_dir is not None
        self.remote_url = remote_url
        self.tracking_ref = f"refs/remotes/{remote}/{branch}"
        self.pending_ref = f"{PENDING_PREFIX}{branch}"
        self._fetched_at: float | None = None
        self._snapshots: dict[str, dict[str, str]] = {}
        self._blob_text: dict[str, str] = {}
        cache_key = f"{self.mirror_dir or self.repo_root}\0{remote}\0{branch}"
        self._cache_file = _cache_path(cache_key)
        # The card client: `_UNSET` resolves it from the configuration on first use, `None`
        # means "no card", and a client object is used as given (tests, migration).
        self._card_client = card
        self.last_sync: dict | None = None

    # -- the card -------------------------------------------------------------- #
    def card(self):
        """The configured card client, or None when this repository keeps no card."""
        if self._card_client is _UNSET:
            if self.read_only:
                self._card_client = None
            else:
                from quenching.specs import cards          # deferred: cards imports the trackers
                self._card_client = cards.resolve_card_client(self.repo_root)
        return self._card_client

    def read_card(self, number: int) -> dict:
        """`{title, body, closed}` of an existing tracker item, for `new --card <n>`."""
        client = self.card()
        if client is None:
            raise _refusal("sp-card-none", "no card provider is configured, so there is no "
                           "issue or work item to adopt; set `card` in the branch config")
        return client.read(int(number))

    def _card_transitions(self, pairs: list[tuple[dict, dict]]) -> None:
        """One request per spec whose lifecycle facts changed — after the spec is written, so
        a tracker failure is raised loudly and never undoes the document."""
        from quenching.specs import cards
        client = self.card()
        if client is None:
            return
        failure = None
        for old, new in pairs:
            if cards.lifecycle_key(old) == cards.lifecycle_key(new):
                continue
            try:
                client.update(int(new["id"]), cards.card_state(new))
            except BackendRefusal as exc:
                failure = failure or cards.card_refusal(new["id"], "updated", exc.err)
        if failure:
            raise failure

    # -- transport ------------------------------------------------------------ #
    def _base(self) -> list[str]:
        if self.mirror_dir:
            return ["git", "--git-dir", self.mirror_dir]
        return ["git", "-C", self.repo_root]

    def _git(self, *argv: str, stdin: bytes | None = None,
             env: dict | None = None) -> tuple[int, bytes, str]:
        try:
            run = subprocess.run([*self._base(), *argv], input=stdin, capture_output=True,
                                 timeout=GIT_TIMEOUT_S, env=env)
        except (OSError, subprocess.SubprocessError) as exc:
            return 127, b"", str(exc)
        return run.returncode, run.stdout, run.stderr.decode("utf-8", "replace")

    def _git_ok(self, action: str, *argv: str, stdin: bytes | None = None,
                env: dict | None = None) -> bytes:
        code, out, err = self._git(*argv, stdin=stdin, env=env)
        if code != 0:
            raise _refusal("sp-git-failed", f"git failed while {action}: {err.strip() or code}",
                           action=action)
        return out

    def _fetch_source(self) -> str:
        if not self.mirror_dir:
            return self.remote
        if not self.remote_url:
            run = subprocess.run(["git", "-C", self.repo_root, "remote", "get-url", self.remote],
                                 capture_output=True, text=True, timeout=GIT_TIMEOUT_S)
            self.remote_url = run.stdout.strip() if run.returncode == 0 else ""
            if not self.remote_url:
                raise _refusal("sp-git-no-remote",
                               f"remote '{self.remote}' has no URL in {self.repo_root}")
        if not os.path.isdir(self.mirror_dir):
            os.makedirs(os.path.dirname(self.mirror_dir) or ".", exist_ok=True)
            subprocess.run(["git", "init", "--quiet", "--bare", self.mirror_dir],
                           capture_output=True, timeout=GIT_TIMEOUT_S, check=False)
        return self.remote_url

    def _fetch(self) -> str | None:
        """One fetch of the store branch into the tracking ref; the tip, or None when the
        remote has no store branch yet."""
        source = self._fetch_source()
        code, _, err = self._git("fetch", "--quiet", "--no-tags", "--no-write-fetch-head",
                                 source, f"+refs/heads/{self.branch}:{self.tracking_ref}")
        self._fetched_at = time.monotonic()
        if code != 0:
            if "couldn't find remote ref" in err:
                self._git("update-ref", "-d", self.tracking_ref)
                self._touch_cache()
                return None
            raise _refusal("sp-git-fetch-failed",
                           f"could not fetch branch '{self.branch}' from '{self.remote}': "
                           f"{err.strip() or code}", remote=self.remote)
        self._touch_cache()
        return self._local_tip()

    def _local_tip(self) -> str | None:
        code, out, _ = self._git("rev-parse", "--verify", "--quiet",
                                 f"{self.tracking_ref}^{{commit}}")
        return (out.decode().strip() or None) if code == 0 else None

    def has_local_ref(self) -> bool:
        return self._local_tip() is not None or self._pending() is not None

    def _pending(self) -> str | None:
        """The clone's pending commit, or None; a read-only mirror never has one."""
        if self.read_only:
            return None
        code, out, _ = self._git("rev-parse", "--verify", "--quiet",
                                 f"{self.pending_ref}^{{commit}}")
        return (out.decode().strip() or None) if code == 0 else None

    def _parent(self, commit: str) -> str | None:
        code, out, _ = self._git("rev-parse", "--verify", "--quiet", f"{commit}^1")
        return (out.decode().strip() or None) if code == 0 else None

    def _ops(self, commit: str | None) -> list[str]:
        """The operations a pending commit accumulated, from its message."""
        if commit is None:
            return []
        body = self._git_ok("reading the pending message", "show", "-s", "--format=%B",
                            commit).decode("utf-8", "replace").strip()
        body = body[len(COMMIT_PREFIX):] if body.startswith(COMMIT_PREFIX) else body
        return [op.strip() for op in body.split(";") if op.strip()]

    def _cache_fresh(self) -> bool:
        try:
            with open(self._cache_file, encoding="utf-8") as handle:
                value = json.load(handle)
        except (OSError, ValueError):
            return False
        return (isinstance(value, dict) and value.get("version") == CACHE_VERSION
                and isinstance(value.get("fetchedAt"), (int, float))
                and time.time() - value["fetchedAt"] <= FETCH_TTL_S)

    def _touch_cache(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._cache_file), exist_ok=True)
            with open(self._cache_file, "w", encoding="utf-8") as handle:
                json.dump({"version": CACHE_VERSION, "fetchedAt": time.time()}, handle)
        except OSError:
            pass

    def _fetched_fresh(self) -> bool:
        return self._fetched_at is not None and time.monotonic() - self._fetched_at <= FETCH_TTL_S

    def _tip(self) -> str | None:
        """The tip a read sees: no fetch while this process fetched or wrote within the TTL or
        the cache is fresh, and none at all under `QUENCHING_SPECS_NO_FETCH` (the local ref as it
        stands). The tip is memoized for `TIP_MEMO_S` only, so one read pass resolves it once and
        a long-lived process (the portal) still sees a commit made outside it; any write clears
        the memo so the next read sees the new tip."""
        return self._heads()[0]

    def _heads(self) -> tuple[str | None, str | None]:
        """`(tip, pending)` under the same memo window as `_tip`."""
        memo = getattr(self, "_tip_memo", None)
        if memo is not None and time.monotonic() - memo[0] <= TIP_MEMO_S:
            return memo[1], memo[2]
        if self._fetched_fresh() or os.environ.get(NO_FETCH_ENV, "") not in ("", "0") \
                or self._cache_fresh():
            tip = self._local_tip()
        else:
            tip = self._fetch()
        pending = self._pending()
        self._tip_memo = (time.monotonic(), tip, pending)
        return tip, pending

    # -- the read model -------------------------------------------------------- #
    def _snapshot(self, tip: str | None) -> "_Tree":
        """Everything under `specs/` at `tip`: one `ls-tree`, texts loaded on demand."""
        if tip is None:
            return _Tree(self, {})
        if tip not in self._snapshots:
            listing = self._git_ok("listing the store tree", "ls-tree", "-r", "-z",
                                   "--full-tree", tip, "--", SPECS_DIR)
            blobs: dict[str, str] = {}
            for record in listing.split(b"\0"):
                if not record:
                    continue
                meta, path = record.split(b"\t", 1)
                _, kind, blob = meta.split(b" ")
                if kind == b"blob":
                    blobs[path.decode("utf-8")] = blob.decode()
            self._snapshots[tip] = blobs
        return _Tree(self, self._snapshots[tip])

    def _view(self) -> "_Tree":
        """What a read sees: the remote tip with the clone's pending writes laid over it. The
        replay is computed in memory and never moves the pending ref — reads never write."""
        tip, pending = self._heads()
        if pending is None:
            return self._snapshot(tip)
        return _Tree(self, self._replay(pending, tip)["view"])

    def _replay(self, pending: str, tip: str | None, drop: tuple = ()) -> dict:
        """The pending commit replayed onto `tip`, judged per spec ID.

        Returns `view` (the `specs/` listing a read sees), `changes` (path -> `_Blob` or None,
        relative to `tip`), `conflicts` (specs changed on both sides to different results; the
        view keeps the local document) and `remote` (spec IDs the remote changed since the
        pending base). `specs/.next-id` takes the larger value; `drop` discards those specs'
        local writes."""
        base = self._parent(pending)
        before = self._snapshot(base).blobs
        local = self._snapshot(pending).blobs
        remote = self._snapshot(tip).blobs
        view = dict(remote)
        changes: dict[str, str | None] = {}
        conflicts: list[dict] = []
        remote_ids = {_spec_id(p) for p in set(before) | set(remote)
                      if before.get(p) != remote.get(p)} - {None}
        touched = {p for p in set(before) | set(local) if before.get(p) != local.get(p)}
        for spec_id in sorted({_spec_id(p) for p in touched} - {None} - set(drop)):
            paths = _spec_paths(spec_id)
            if spec_id in remote_ids and any(local.get(p) != remote.get(p) for p in paths):
                conflicts.append({"id": spec_id,
                                  "localBlob": next((local[p] for p in paths if p in local), None),
                                  "remoteBlob": next((remote[p] for p in paths if p in remote),
                                                     None)})
            for path in paths:
                if local.get(path) != remote.get(path):
                    changes[path] = _Blob(local[path]) if path in local else None
        if COUNTER_PATH in touched and COUNTER_PATH in local:
            mine, theirs = local[COUNTER_PATH], remote.get(COUNTER_PATH)
            texts = self._texts([b for b in (mine, theirs) if b])

            def value(blob):
                text = texts.get(blob, "").strip() if blob else ""
                return int(text) if text.isdigit() else 0
            if value(mine) > value(theirs):
                changes[COUNTER_PATH] = _Blob(mine)
        for path, blob in changes.items():
            if blob is None:
                view.pop(path, None)
            else:
                view[path] = str(blob)
        return {"view": view, "changes": changes, "conflicts": conflicts, "remote": remote_ids}

    def _texts(self, blobs: list[str]) -> dict[str, str]:
        """`blob -> text` through one `cat-file --batch` for whatever is not cached yet.
        Blobs are immutable, so the cache never needs invalidating."""
        missing = list(dict.fromkeys(b for b in blobs if b not in self._blob_text))
        if missing:
            out = self._git_ok("reading the store blobs", "cat-file", "--batch",
                               stdin="".join(f"{blob}\n" for blob in missing).encode())
            pos = 0
            for blob in missing:
                newline = out.index(b"\n", pos)
                size = int(out[pos:newline].split(b" ")[2])
                self._blob_text[blob] = out[newline + 1:newline + 1 + size].decode("utf-8")
                pos = newline + 1 + size + 1
        return {blob: self._blob_text[blob] for blob in blobs}

    @staticmethod
    def _path(phase: str, spec_id: int) -> str:
        return f"{PHASE_DIRS[phase]}/{spec_id}.md"

    @staticmethod
    def _index(snapshot: "_Tree") -> dict[int, tuple[str, str]]:
        """`id -> (phase, path)`; an open copy wins over an archived one of the same ID."""
        found: dict[int, tuple[str, str]] = {}
        for phase in ("archive", "plans"):
            prefix = PHASE_DIRS[phase] + "/"
            for path in snapshot:
                rest = path[len(prefix):] if path.startswith(prefix) else ""
                if "/" in rest or not rest.endswith(".md") or not rest[:-3].isdigit():
                    continue
                found[int(rest[:-3])] = (phase, path)
        return found

    @staticmethod
    def _descriptor(spec_id: int, phase: str, path: str) -> dict:
        return {"id": spec_id, "phase": phase, "folder": phase, "legacy": False,
                "path": LOCATOR_PREFIX + path}

    # -- the five primitives --------------------------------------------------- #
    def list_specs(self, phase: str | None = None, lean: bool = False) -> list[dict]:
        snapshot = self._view()
        if lean:
            snapshot.preload()
        rows = []
        for spec_id, (spec_phase, path) in self._index(snapshot).items():
            if phase is not None and spec_phase != phase:
                continue
            row = self._descriptor(spec_id, spec_phase, path)
            if lean:
                info = derive_info(row, snapshot[path][1])
                row.update({"title": info["frontmatter"].get("title", ""),
                            "state": "closed" if spec_phase == "archive" else "open",
                            "records": derive_labels(info),
                            "epic": info["frontmatter"].get("epic"),
                            "workItemType": info["frontmatter"].get("workItemType")})
            rows.append(row)
        return sorted(rows, key=lambda r: (PHASES.index(r["phase"]), r["id"]))

    def read_spec(self, spec_id: str | int) -> tuple[dict | None, dict]:
        snapshot = self._view()
        # A second read in one process means a sweep (list --json, validate): load every text in
        # one batch instead of one `cat-file` per spec.
        self._reads = getattr(self, "_reads", 0) + 1
        if self._reads == 2:
            snapshot.preload()
        spec, err = resolve_one(self.list_specs(), spec_id)
        if err:
            return None, err
        blob, text = snapshot[spec["path"][len(LOCATOR_PREFIX):]]
        info = derive_info(spec, text)
        info["_git_blob"] = blob
        return info, {}

    def read_specs(self, spec_ids: list) -> dict[str, dict | None]:
        """N reads from ONE snapshot: one index, one batched blob load, no per-spec listing."""
        snapshot = self._view()
        index = self._index(snapshot)
        wanted = {str(s): index.get(int(s)) if str(s).isdigit() else None for s in spec_ids}
        snapshot._backend._texts([snapshot.blobs[p[1]] for p in wanted.values() if p])
        out: dict[str, dict | None] = {}
        for key, hit in wanted.items():
            if hit is None:
                out[key] = None
                continue
            blob, text = snapshot[hit[1]]
            info = derive_info(self._descriptor(int(key), hit[0], hit[1]), text)
            info["_git_blob"] = blob
            out[key] = info
        return out

    def write_spec(self, info: dict, text: str) -> None:
        self.write_specs([(info, text)])

    def write_specs(self, items: list[tuple[dict, str]]) -> None:
        """Replace N documents in ONE commit — the batch a triage writes its priorities with.

        Each item is checked against the blob its `info` was read at, on every attempt: a
        document that changed under the caller refuses the whole batch."""
        items = [(info, guard_store_write(text, self.repo_root, info.get("text"), BackendRefusal))
                 for info, text in items]

        def apply(snapshot):
            index = self._index(snapshot)
            changes: dict[str, str | None] = {}
            for info, text in items:
                spec_id = int(info["id"])
                if spec_id not in index:
                    raise _refusal("sp-unknown-id", f"no spec with id '{spec_id}' on branch "
                                   f"'{self.branch}'", id=spec_id)
                path = index[spec_id][1]
                blob, current = snapshot[path]
                expected = info.get("_git_blob")
                if expected and blob != expected:
                    raise stale_write_refusal(spec_id, expected, blob)
                if current != text:
                    changes[path] = text
            return changes, None

        ids = " ".join(str(int(info["id"])) for info, _ in items)
        blobs = self._store(apply, f"write {ids}", sync=False)
        for info, _ in items:
            for path, blob in blobs.items():
                if path.endswith(f"/{int(info['id'])}.md"):
                    info["_git_blob"] = blob

    def create_spec(self, phase: str, text: str, spec_id: int | str | None = None,
                    card: int | None = None) -> str:
        """Store a new spec.

        With a card provider and no explicit ID, the card is created FIRST (one request) and
        its native number becomes the spec's ID. `card=<n>` adopts an existing tracker item
        instead: the document is written under that number, then the item is rewritten to the
        thin card. `spec_id` alone is the hook for an ID the caller already owns; with none of
        them the branch counter allocates one under the same compare-and-swap."""
        from quenching.specs import cards
        text = guard_store_write(text, self.repo_root, None, BackendRefusal)
        client = self.card()
        fresh = derive_info({"phase": phase}, text)
        adopting = card is not None
        created_card = False
        if adopting:
            if client is None:
                raise _refusal("sp-card-none", "--card needs a card provider; none is configured")
            spec_id = int(card)
        elif spec_id is None and client is not None:
            self._guard_identity()  # before the card: a refused identity must leave no orphan
            try:
                spec_id = client.create(cards.card_state(fresh))
            except BackendRefusal as exc:
                exc.err["message"] += " — the card is created first, so no spec was written"
                raise
            created_card = True
        locator = self._create(phase, text, spec_id, orphan_card=created_card)
        if adopting:
            adopted = derive_info({"id": int(spec_id), "phase": phase}, text)
            try:
                client.update(int(spec_id), cards.card_state(adopted))
            except BackendRefusal as exc:
                raise cards.card_refusal(spec_id, "rewritten as a thin card", exc.err)
        return locator

    def _create(self, phase: str, text: str, spec_id: int | str | None,
                orphan_card: bool = False) -> str:
        allocated: dict[str, int] = {}

        def apply(snapshot):
            ids = set(self._index(snapshot))
            highest = max(ids, default=0)
            try:
                counter = int(snapshot.get(COUNTER_PATH, ("", ""))[1].strip())
            except ValueError:
                counter = highest + 1
            if spec_id is None:
                new_id = max(counter, highest + 1)
            else:
                new_id = int(spec_id)
                if new_id in ids:
                    extra = (f"; the card #{new_id} was already created and is now an orphan "
                             "to close by hand" if orphan_card else "")
                    raise _refusal("sp-git-id-taken", f"spec {new_id} already exists on branch "
                                   f"'{self.branch}'; nothing was written{extra}", id=new_id)
            allocated["id"] = new_id
            return {self._path(phase, new_id): text,
                    COUNTER_PATH: f"{max(counter, new_id + 1)}\n"}, None

        self._store(apply, lambda: f"create {allocated['id']}")
        return LOCATOR_PREFIX + self._path(phase, allocated["id"])

    def import_specs(self, items: list[tuple[int, str, str]],
                     config: dict | None = None) -> list[str]:
        """Write N documents under THEIR OWN IDs in ONE commit — the migration batch.

        `items` is `[(id, phase, text)]`. A document already on the branch with the same text
        and phase is left alone, so a re-run is a no-op; one that differs refuses the whole
        batch, because a migration must never overwrite what the branch already holds.
        `config`, when given, is the `specs` namespace written to the branch's
        `quenching.json` in the SAME commit. Returns the paths written."""
        items = [(spec_id, phase, guard_store_write(text, self.repo_root, None, BackendRefusal))
                 for spec_id, phase, text in items]

        def apply(snapshot):
            index = self._index(snapshot)
            changes: dict[str, str | None] = {}
            conflicts = []
            for spec_id, phase, text in items:
                dest = self._path(phase, spec_id)
                if spec_id in index:
                    held = index[spec_id][1]
                    if held == dest and snapshot[held][1] == text:
                        continue
                    conflicts.append(spec_id)
                    continue
                changes[dest] = text
            if conflicts:
                raise _refusal("sp-git-id-taken", "the branch already holds different "
                               f"documents for spec(s) {', '.join(map(str, conflicts))}; "
                               "nothing was written", ids=conflicts)
            if config is not None:
                rendered = json.dumps({"specs": config}, indent=2, ensure_ascii=False) + "\n"
                if self._config_text(snapshot) != rendered:
                    changes[CONFIG_PATH] = rendered
            if any(path != CONFIG_PATH for path in changes):
                try:
                    counter = int(snapshot.get(COUNTER_PATH, ("", ""))[1].strip())
                except ValueError:
                    counter = 0
                top = max([int(i) for i, _, _ in items] + list(index) + [0])
                changes[COUNTER_PATH] = f"{max(counter, top + 1)}\n"
            return changes, None

        written = self._store(apply, f"import {len(items)} specs")
        return sorted(path for path in written if path not in (COUNTER_PATH, CONFIG_PATH))

    def move_spec(self, info: dict, dest_phase: str) -> str:
        spec_id = int(info["id"])
        dest = self._path(dest_phase, spec_id)

        def apply(snapshot):
            index = self._index(snapshot)
            if spec_id not in index:
                raise _refusal("sp-unknown-id", f"no spec with id '{spec_id}' on branch "
                               f"'{self.branch}'", id=spec_id)
            path = index[spec_id][1]
            if path == dest:
                return {}, None
            return {path: None, dest: snapshot[path][1]}, None

        verb = "archive" if dest_phase == "archive" else "restore"
        self._store(apply, f"{verb} {spec_id}")
        return LOCATOR_PREFIX + dest

    # -- configuration on the branch ------------------------------------------ #
    def read_config(self) -> dict:
        """The `specs` namespace of the branch's `quenching.json`, or {} when absent."""
        tip = self._tip()
        if tip is None:
            return {}
        code, out, _ = self._git("cat-file", "blob", f"{tip}:{CONFIG_PATH}")
        if code != 0:
            return {}
        try:
            value = json.loads(out.decode("utf-8"))
        except ValueError:
            return {}
        specs = value.get("specs") if isinstance(value, dict) else None
        return specs if isinstance(specs, dict) else {}

    def _config_text(self, _snapshot=None) -> str | None:
        """The raw `quenching.json` at the current tracking tip, or None."""
        tip = self._local_tip()
        if tip is None:
            return None
        code, out, _ = self._git("cat-file", "blob", f"{tip}:{CONFIG_PATH}")
        return out.decode("utf-8") if code == 0 else None

    def write_config(self, specs_namespace: dict) -> None:
        """Replace the branch's `quenching.json` with `{"specs": specs_namespace}`."""
        text = json.dumps({"specs": specs_namespace}, indent=2, ensure_ascii=False) + "\n"
        self._store(lambda snapshot: ({CONFIG_PATH: text}, None), "configure")

    # -- the one write path ---------------------------------------------------- #
    def _store(self, apply, message, sync: bool = True, drop: tuple = (),
               collapse: bool = False) -> dict[str, str]:
        """The one write path: `sync=False` moves only the local pending ref, `sync=True`
        sends the store to the remote."""
        self._tip_memo = None
        try:
            if not sync:
                return self._store_local(apply, message)
            return self._store_sync(apply, message, drop, collapse)
        finally:
            self._tip_memo = None

    def _store_local(self, apply, message) -> dict[str, str]:
        """Apply `apply(view) -> (changes, _)` and replace the pending commit by a local
        compare-and-swap; nothing reaches the remote.

        The pending commit's parent is the remote tip it is based on: a write after a fetch
        persists the replay onto the new tip, unless a spec conflicts — then the pending commit
        keeps its base, so the sync can still name the conflict, and a write to a spec the
        remote changed meanwhile refuses."""
        if self.read_only:
            raise _refusal("sp-git-read-only", f"the store mirror at {self.mirror_dir} is "
                           "read-only; nothing was written")
        self._guard_identity()
        for attempt in range(MAX_ATTEMPTS):
            if attempt:
                time.sleep(random.uniform(0, 0.01 * 2 ** attempt))
                self._tip_memo = None
            tip, pending = self._heads()
            replay = self._replay(pending, tip) if pending else \
                {"view": self._snapshot(tip).blobs, "changes": {}, "conflicts": [], "remote": set()}
            changes, _ = apply(_Tree(self, replay["view"]))
            if not changes:
                return {}
            if replay["conflicts"]:
                stale = ({_spec_id(p) for p in changes} & replay["remote"]) \
                    - {c["id"] for c in replay["conflicts"]}
                if stale:
                    raise conflict_refusal(replay["conflicts"])
                base, parent, changes = pending, self._parent(pending), changes
            else:
                base, parent, changes = tip, tip, {**replay["changes"], **changes}
            subject = message() if callable(message) else message
            ops = self._ops(pending)
            ops += [subject] if subject not in ops else []
            commit, blobs = self._commit(base, changes, f"{COMMIT_PREFIX} {'; '.join(ops)}",
                                         [parent] if parent else [])
            code, _, _ = self._git("update-ref", "-m", "quenching: pending write",
                                   self.pending_ref, commit, pending or "")
            if code == 0:
                return blobs
        raise _refusal("sp-git-cas-exhausted",
                       f"the pending ref '{self.pending_ref}' kept moving — {MAX_ATTEMPTS} local "
                       "writes lost the compare-and-swap; nothing was written",
                       attempts=MAX_ATTEMPTS)

    def _store_sync(self, apply, message, drop: tuple = (),
                    collapse: bool = False) -> dict[str, str]:
        """Send the store: replay the pending commit onto the remote tip T, run `apply` (the
        sync operation, or None for a bare push) on that view, and push ONE parentless commit
        with `--force-with-lease=<branch>:<T>`, so the branch always holds a single commit.

        Every attempt re-reads the pending ref; a stale lease fetches and retries up to
        `MAX_ATTEMPTS`; a remote that refuses the rewrite receives the same tree as a
        fast-forward child of T (`history: appended`). A spec changed on both sides refuses
        with both blobs and keeps the pending ref. Returns `path -> blob` for every text
        `apply` wrote; `self.last_sync` describes the push."""
        if self.read_only:
            raise _refusal("sp-git-read-only", f"the store mirror at {self.mirror_dir} is "
                           "read-only; nothing was written")
        self._guard_identity()
        self.last_sync = None
        tip = self._tip()
        for attempt in range(MAX_ATTEMPTS):
            if attempt:
                # Full jitter, doubling: writers that collided once must not collide again.
                time.sleep(random.uniform(0, 0.1 * 2 ** attempt))
                tip = self._fetch()
            pending = self._pending()
            replay = self._replay(pending, tip, drop) if pending else \
                {"view": self._snapshot(tip).blobs, "changes": {}, "conflicts": []}
            if replay["conflicts"]:
                raise conflict_refusal(replay["conflicts"])
            changes = apply(_Tree(self, replay["view"]))[0] if apply else {}
            changes = {**replay["changes"], **changes}
            if not changes and not (collapse and tip and self._parent(tip)):
                if pending:
                    self._close(pending, tip)
                return {}
            subject = message() if callable(message) else message
            ops = self._ops(pending) + [f"drop {spec_id}" for spec_id in drop]
            ops += [subject] if subject and subject not in ops else []
            text = f"{COMMIT_PREFIX} {'; '.join(ops) or 'push'}"
            commit, blobs = self._commit(tip, changes, text, [])
            lease = f"--force-with-lease=refs/heads/{self.branch}:{tip or ''}"
            code, said = self._push(lease, commit)
            history = "collapsed"
            if code != 0 and "[remote rejected]" in said:
                # No right to rewrite (no force push, a protected branch): append the same tree.
                tree = self._git_ok("reading the sync tree", "rev-parse",
                                    f"{commit}^{{tree}}").decode().strip()
                commit = self._git_ok("creating the commit", "commit-tree", tree,
                                      *(["-p", tip] if tip else []), "-m", text).decode().strip()
                code, said = self._push(None, commit)
                history = "appended"
            if code == 0:
                self._close(pending, commit)
                self.last_sync = {"commit": commit, "previous": tip, "history": history,
                                  "attempts": attempt + 1}
                self._sync_cards(tip, commit)
                return blobs
            if "[remote rejected]" in said or \
                    not any(marker in said for marker in _REJECTED_MARKERS):
                raise _refusal("sp-git-push-failed",
                               f"pushing branch '{self.branch}' to '{self.remote}' failed: "
                               f"{said.strip() or code}; nothing was written",
                               remote=self.remote)
        raise _refusal("sp-git-cas-exhausted",
                       f"branch '{self.branch}' kept moving — {MAX_ATTEMPTS} attempts were "
                       "rejected; nothing was written", attempts=MAX_ATTEMPTS)

    def _push(self, lease: str | None, commit: str) -> tuple[int, str]:
        code, out, err = self._git("push", "--quiet", "--porcelain", "--no-verify",
                                   *([lease] if lease else []), self.remote,
                                   f"{commit}:refs/heads/{self.branch}")
        return code, out.decode("utf-8", "replace") + err

    def _close(self, sent: str | None, pushed: str | None) -> None:
        """Move the tracking ref to `pushed` and retire the pending commit that was `sent`, by
        compare-and-swap: a write that replaced it during the sync is replayed onto `pushed`
        instead of being dropped."""
        if pushed and pushed != self._local_tip():
            self._git("update-ref", self.tracking_ref, pushed)
            self._fetched_at = time.monotonic()
            self._touch_cache()
        if sent is None:
            return
        for _ in range(MAX_ATTEMPTS):
            code, _, _ = self._git("update-ref", "-d", self.pending_ref, sent)
            if code == 0:
                return
            current = self._pending()
            if current is None:
                return
            mine, theirs = self._snapshot(sent).blobs, self._snapshot(current).blobs
            late = {p: (_Blob(theirs[p]) if p in theirs else None)
                    for p in set(mine) | set(theirs) if mine.get(p) != theirs.get(p)}
            ops = [op for op in self._ops(current) if op not in self._ops(sent)]
            commit, _ = self._commit(pushed, late, f"{COMMIT_PREFIX} {'; '.join(ops) or 'write'}",
                                     [pushed] if pushed else [])
            code, _, _ = self._git("update-ref", "-m", "quenching: pending write",
                                   self.pending_ref, commit, current)
            if code == 0:
                return
            sent = current

    def _sync_cards(self, before: str | None, after: str) -> None:
        """One card request per spec whose lifecycle facts changed between the two tips; a
        spec the sync created already has its card."""
        if self.card() is None:
            return
        old, new = self._snapshot(before), self._snapshot(after)
        changed = {_spec_id(p) for p in set(old.blobs) | set(new.blobs)
                   if old.blobs.get(p) != new.blobs.get(p)} - {None}
        old_index, new_index = self._index(old), self._index(new)
        pairs = []
        for spec_id in sorted(changed):
            if spec_id not in old_index or spec_id not in new_index:
                continue
            (old_phase, old_path), (new_phase, new_path) = old_index[spec_id], new_index[spec_id]
            pairs.append((derive_info(self._descriptor(spec_id, old_phase, old_path),
                                      old[old_path][1]),
                          derive_info(self._descriptor(spec_id, new_phase, new_path),
                                      new[new_path][1])))
        self._card_transitions(pairs)

    def push(self, drop: tuple = ()) -> dict:
        """`cq specs push`: send every pending write of the clone, collapsing the branch to one
        commit even when nothing is pending; `drop` discards those specs' local writes first."""
        self._store(None, "", drop=tuple(int(d) for d in drop), collapse=True)
        return self.last_sync or {"commit": None, "history": "unchanged"}

    def pending_state(self) -> dict | None:
        """The unsent local writes, without reading the remote: `{specs, since, commit}`."""
        pending = self._pending()
        if pending is None:
            return None
        base = self._parent(pending)
        before, local = self._snapshot(base).blobs, self._snapshot(pending).blobs
        specs = sorted({_spec_id(p) for p in set(before) | set(local)
                        if before.get(p) != local.get(p)} - {None})
        oldest = self._git_ok("reading the pending date", "show", "-s", "--format=%cI",
                              pending).decode().strip()
        return {"specs": specs, "since": oldest, "commit": pending}

    def _guard_identity(self) -> None:
        """The author and committer emails `commit-tree` will sign with, judged like the text:
        `_store` pushes with `--no-verify`, so no hook ever sees them."""
        for var in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
            code, out, _ = self._git("var", var)
            email = out.decode("utf-8", "replace").partition("<")[2].partition(">")[0]
            findings = scan_text(f"git var {var}", email, patterns(require_denylist=False)) \
                if code == 0 else []
            if findings:
                raise BackendRefusal(store_refusal(findings))

    def _commit(self, base: str | None, changes: dict[str, str | None], message: str,
                parents: list[str]) -> tuple[str, dict[str, str]]:
        """Build one commit with `base`'s tree plus `changes`, on `parents`, with a throwaway
        index: no checkout, no worktree. A `_Blob` change is staged by sha; `blobs` reports
        only the texts hashed here."""
        scratch = tempfile.mkdtemp(prefix="quenching-store-")
        try:
            env = {**os.environ, "GIT_INDEX_FILE": os.path.join(scratch, "index")}
            if base:
                self._git_ok("reading the base tree", "read-tree", base, env=env)
            else:
                self._git_ok("starting an empty tree", "read-tree", "--empty", env=env)
            writes = [(path, text) for path, text in changes.items()
                      if text is not None and not isinstance(text, _Blob)]
            stored = {path: str(blob) for path, blob in changes.items() if isinstance(blob, _Blob)}
            removes = [path for path, text in changes.items() if text is None]
            blobs: dict[str, str] = {}
            if writes:
                files = []
                for n, (_, text) in enumerate(writes):
                    name = os.path.join(scratch, f"blob{n}")
                    with open(name, "wb") as handle:
                        handle.write(text.encode("utf-8"))
                    files.append(name)
                out = self._git_ok("hashing the documents", "hash-object", "-w", "--no-filters",
                                   "--stdin-paths", stdin="".join(f + "\n" for f in files).encode())
                shas = out.decode().split()
                blobs = {path: sha for (path, _), sha in zip(writes, shas)}
            entries = {**stored, **blobs}
            if entries:
                info = "".join(f"100644 {sha}\t{path}\n" for path, sha in entries.items())
                self._git_ok("staging the documents", "update-index", "--add", "--index-info",
                             stdin=info.encode("utf-8"), env=env)
            if removes:
                self._git_ok("removing the moved document", "update-index", "--force-remove",
                             "--", *removes, env=env)
            tree = self._git_ok("writing the tree", "write-tree", env=env).decode().strip()
            commit = self._git_ok("creating the commit", "commit-tree", tree,
                                  *[arg for p in parents for arg in ("-p", p)],
                                  "-m", message).decode().strip()
            return commit, blobs
        finally:
            shutil.rmtree(scratch, ignore_errors=True)


class _Tree:
    """`path -> (blob, text)` at one tip. Texts load lazily, or in one batch on `preload`, so
    a write re-applied on a new tip reads only the documents it touches."""

    def __init__(self, backend: GitBackend, blobs: dict[str, str]) -> None:
        self._backend = backend
        self.blobs = blobs

    def __iter__(self):
        return iter(self.blobs)

    def __contains__(self, path: str) -> bool:
        return path in self.blobs

    def __getitem__(self, path: str) -> tuple[str, str]:
        blob = self.blobs[path]
        return blob, self._backend._texts([blob])[blob]

    def get(self, path: str, default=None):
        return self[path] if path in self.blobs else default

    def preload(self) -> None:
        self._backend._texts(list(self.blobs.values()))


_STORES: dict[tuple[str, str], GitBackend] = {}


def open_git_backend(root: str, mirror_dir: str | None = None) -> tuple[SpecBackend | None, dict]:
    """The `git` store for this repository — one instance per repository and process, so the
    config loader and the commands share the one fetch."""
    repo = find_repo_root(root)
    key = (os.path.abspath(repo), mirror_dir or "")
    if key in _STORES:
        return _STORES[key], {}
    run = subprocess.run(["git", "-C", repo, "remote", "get-url", DEFAULT_REMOTE],
                         capture_output=True, text=True, timeout=GIT_TIMEOUT_S, check=False) \
        if os.path.isdir(repo) else None
    if run is None or run.returncode != 0 or not run.stdout.strip():
        return None, {"code": "sp-git-no-remote", "exit": 2,
                      "message": f"the git store needs a '{DEFAULT_REMOTE}' remote in {repo}; "
                                 "no spec was read or written"}
    backend = GitBackend(repo, mirror_dir=mirror_dir, remote_url=run.stdout.strip())
    _STORES[key] = backend
    return backend, {}


def branch_config(root: str) -> dict:
    """The branch's specs-axis configuration for the config loader; {} when unreadable."""
    backend, err = open_git_backend(root)
    if err or backend is None:
        return {}
    try:
        return backend.read_config()                       # type: ignore[union-attr]
    except BackendRefusal:
        return {}
