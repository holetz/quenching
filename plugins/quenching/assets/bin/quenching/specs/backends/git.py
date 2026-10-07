"""The `git` backend — specs as files on a dedicated branch of the code repository's remote.

The branch (`quenching` by default) holds one canonical document per spec and nothing derived:

    specs/<id>.md          an open spec (`plans`)
    specs/archive/<id>.md  an archived spec (`archive`)
    specs/.next-id         the next ID to allocate when no tracker owns identity
    quenching.json         the specs-axis configuration, under the `specs` namespace

Nothing is ever checked out. Reads are `git ls-tree` plus one `git cat-file --batch` over the
remote-tracking ref; writes build a commit with a throwaway index and push it without force, so
the push itself is the compare-and-swap. A rejected push is re-applied on the new tip — the SAME
semantic operation, never a text merge — and a document that changed under the caller refuses
as a stale write instead of being overwritten.

Every store write funnels through `_store`, the name the read-only specs-reader already blocks."""
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
MAX_ATTEMPTS = 5
CACHE_VERSION = 1
GIT_TIMEOUT_S = 120

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


def _cache_path(key: str) -> str:
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    digest = hashlib.sha256(key.encode()).hexdigest()[:32]
    return os.path.join(base, "quenching", "git", f"{digest}.json")


class GitBackend(SpecBackend):
    """Specs on a git branch, written by plumbing and read from the remote-tracking ref.

    `mirror_dir` selects the read-only mode: objects and refs live in a bare repository there,
    fetched from the target's remote URL, so a reader never writes into the target's `.git`."""

    name = "git"

    def __init__(self, repo_root: str, remote: str = DEFAULT_REMOTE,
                 branch: str = STORE_BRANCH, mirror_dir: str | None = None,
                 remote_url: str | None = None) -> None:
        self.repo_root = os.path.abspath(repo_root)
        self.remote = remote
        self.branch = branch
        self.mirror_dir = os.path.abspath(mirror_dir) if mirror_dir else None
        self.read_only = self.mirror_dir is not None
        self.remote_url = remote_url
        self.tracking_ref = f"refs/remotes/{remote}/{branch}"
        self._fetched = False
        self._snapshots: dict[str, dict[str, str]] = {}
        self._blob_text: dict[str, str] = {}
        cache_key = f"{self.mirror_dir or self.repo_root}\0{remote}\0{branch}"
        self._cache_file = _cache_path(cache_key)

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
        self._fetched = True
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

    def _tip(self) -> str | None:
        """The tip a read sees: at most one fetch per process, none while the cache is fresh."""
        if self._fetched or self._cache_fresh():
            return self._local_tip()
        return self._fetch()

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
        snapshot = self._snapshot(self._tip())
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
                            "records": derive_labels(info)})
            rows.append(row)
        return sorted(rows, key=lambda r: (PHASES.index(r["phase"]), r["id"]))

    def read_spec(self, spec_id: str | int) -> tuple[dict | None, dict]:
        snapshot = self._snapshot(self._tip())
        spec, err = resolve_one(self.list_specs(), spec_id)
        if err:
            return None, err
        blob, text = snapshot[spec["path"][len(LOCATOR_PREFIX):]]
        info = derive_info(spec, text)
        info["_git_blob"] = blob
        return info, {}

    def read_specs(self, spec_ids: list) -> dict[str, dict | None]:
        """N reads from ONE snapshot: one index, one batched blob load, no per-spec listing."""
        snapshot = self._snapshot(self._tip())
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
        blobs = self._store(apply, f"write {ids}")
        for info, _ in items:
            for path, blob in blobs.items():
                if path.endswith(f"/{int(info['id'])}.md"):
                    info["_git_blob"] = blob

    def create_spec(self, phase: str, text: str, spec_id: int | str | None = None) -> str:
        """Store a new spec. `spec_id` is the hook for an ID a tracker card already owns;
        without it the branch counter allocates one under the same compare-and-swap."""
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
                    raise _refusal("sp-git-id-taken", f"spec {new_id} already exists on branch "
                                   f"'{self.branch}'; nothing was written", id=new_id)
            allocated["id"] = new_id
            return {self._path(phase, new_id): text,
                    COUNTER_PATH: f"{max(counter, new_id + 1)}\n"}, None

        self._store(apply, lambda: f"create {allocated['id']}")
        return LOCATOR_PREFIX + self._path(phase, allocated["id"])

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

    def write_config(self, specs_namespace: dict) -> None:
        """Replace the branch's `quenching.json` with `{"specs": specs_namespace}`."""
        text = json.dumps({"specs": specs_namespace}, indent=2, ensure_ascii=False) + "\n"
        self._store(lambda snapshot: ({CONFIG_PATH: text}, None), "configure")

    # -- the one write path ---------------------------------------------------- #
    def _store(self, apply, message) -> dict[str, str]:
        """Apply `apply(snapshot) -> (changes, _)` on the tip, commit, push without force.

        A rejected push fetches and re-runs `apply` on the new tip, up to `MAX_ATTEMPTS`
        times; `apply` raising a refusal (a stale document, a taken ID) ends the loop.
        Returns `path -> blob` for every file written."""
        if self.read_only:
            raise _refusal("sp-git-read-only", f"the store mirror at {self.mirror_dir} is "
                           "read-only; nothing was written")
        tip = self._tip()
        for attempt in range(MAX_ATTEMPTS):
            if attempt:
                # Full jitter, doubling: writers that collided once must not collide again.
                time.sleep(random.uniform(0, 0.1 * 2 ** attempt))
                tip = self._fetch()
            snapshot = self._snapshot(tip)
            # An absent branch (`tip is None`) reads as an empty tree: the store bootstraps as
            # an orphan commit on its first write.
            changes, _ = apply(snapshot)
            if not changes:
                return {}
            subject = message() if callable(message) else message
            commit, blobs = self._commit(tip, changes, f"{COMMIT_PREFIX} {subject}")
            code, out, err = self._git("push", "--quiet", "--porcelain", "--no-verify",
                                       self.remote, f"{commit}:refs/heads/{self.branch}")
            said = out.decode("utf-8", "replace") + err
            if code == 0:
                self._git("update-ref", self.tracking_ref, commit)
                self._fetched = True
                self._touch_cache()
                return blobs
            if not any(marker in said for marker in _REJECTED_MARKERS):
                raise _refusal("sp-git-push-failed",
                               f"pushing branch '{self.branch}' to '{self.remote}' failed: "
                               f"{said.strip() or code}; nothing was written",
                               remote=self.remote)
        raise _refusal("sp-git-cas-exhausted",
                       f"branch '{self.branch}' kept moving — {MAX_ATTEMPTS} attempts were "
                       "rejected as non-fast-forward; nothing was written",
                       attempts=MAX_ATTEMPTS)

    def _commit(self, tip: str | None, changes: dict[str, str | None],
                message: str) -> tuple[str, dict[str, str]]:
        """Build one commit on `tip` with a throwaway index: no checkout, no worktree."""
        scratch = tempfile.mkdtemp(prefix="quenching-store-")
        try:
            env = {**os.environ, "GIT_INDEX_FILE": os.path.join(scratch, "index")}
            if tip:
                self._git_ok("reading the tip tree", "read-tree", tip, env=env)
            else:
                self._git_ok("starting an empty tree", "read-tree", "--empty", env=env)
            writes = [(path, text) for path, text in changes.items() if text is not None]
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
                info = "".join(f"100644 {blobs[path]}\t{path}\n" for path, _ in writes)
                self._git_ok("staging the documents", "update-index", "--add", "--index-info",
                             stdin=info.encode("utf-8"), env=env)
            if removes:
                self._git_ok("removing the moved document", "update-index", "--force-remove",
                             "--", *removes, env=env)
            tree = self._git_ok("writing the tree", "write-tree", env=env).decode().strip()
            parents = ["-p", tip] if tip else []
            commit = self._git_ok("creating the commit", "commit-tree", tree, *parents,
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
