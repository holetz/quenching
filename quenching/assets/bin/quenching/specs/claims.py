"""A build's reservation of a spec, visible to every machine that shares the `origin`.

The lease is the ref `refs/quenching/claims/<id>` on the remote. Its commit has no parent and a
tree holding one `lease.json`; creating, replacing and deleting it are pushes with
`--force-with-lease`, so the server compares and swaps and two machines can never both win. With
no remote the same ref lives in the local repository and `git update-ref <ref> <new> <old>` is the
compare-and-swap (`scope: local`).

Pure git: nothing here opens the specs backend. Whether a spec is terminal is the caller's answer,
passed in as `terminal`.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import secrets

from quenching.common.config import load_config, namespace
from quenching.common.git import _git_run
from quenching.config.autonomy import coerce as coerce_autonomy

CLAIMS = "refs/quenching/claims/"
REMOTE_CLAIMS = "refs/quenching/remote-claims/"
LEASE_FILE = "lease.json"
SKEW = datetime.timedelta(minutes=2)
# The lease travels to the remote: its commit never carries the user's identity.
IDENTITY = {"GIT_AUTHOR_NAME": "quenching", "GIT_AUTHOR_EMAIL": "quenching@localhost",
            "GIT_COMMITTER_NAME": "quenching", "GIT_COMMITTER_EMAIL": "quenching@localhost"}
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class ClaimError(Exception):
    """git could not answer: a refusal (exit 2), never a lost lease."""


def valid_id(spec_id: str) -> bool:
    return bool(_ID.match(str(spec_id))) and ".." not in str(spec_id)


def now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)


def _stamp(moment: datetime.datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse(stamp: str | None) -> datetime.datetime | None:
    try:
        return datetime.datetime.strptime(str(stamp), "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc)
    except ValueError:
        return None


def claim_minutes(root: str) -> int:
    block = namespace(load_config(root), "shared").get("autonomy")
    return coerce_autonomy(block)[0]["claimMinutes"]


def machine_id(root: str) -> str:
    """The random id of this clone, generated once into its local git config — never a hostname
    or an email, because the holder goes to the remote."""
    code, out, _ = _git_run(root, "config", "--local", "--get", "quenching.machineId")
    if code == 0 and out.strip():
        return out.strip()
    value = secrets.token_hex(8)
    code, _, err = _git_run(root, "config", "--local", "quenching.machineId", value)
    if code != 0:
        raise ClaimError(f"git could not store quenching.machineId: {err.strip()}")
    return value


def session_id(explicit: str | None = None) -> str:
    return explicit or os.environ.get("OPENCODE_SESSION_ID") \
        or os.environ.get("CLAUDE_SESSION_ID") or "-"


def holder_of(machine: str, session: str) -> str:
    return f"{machine}:{session}"


def machine_of(holder: str | None) -> str:
    return str(holder or "").partition(":")[0]


class Store:
    """The claim refs of one repository: on `remote` when it is configured, else local."""

    def __init__(self, root: str, remote: str = "origin"):
        self.root = root
        self.remote = remote
        code, _, _ = _git_run(root, "remote", "get-url", "--", remote)
        if code not in (0, 2):
            raise ClaimError(f"git could not read the remote: {remote}")
        self.scope = "remote" if code == 0 else "local"

    def _git(self, *argv: str) -> str:
        code, out, err = _git_run(self.root, *argv)
        if code != 0:
            raise ClaimError(f"git {argv[0]} failed: {(err or out).strip()}")
        return out

    # — reading —
    def heads(self, spec_id: str | None = None) -> dict[str, str]:
        """`{id: sha}` of the claim refs, one id or all, read from the remote (or locally)."""
        pattern = CLAIMS + (str(spec_id) if spec_id is not None else "*")
        if self.scope == "local":
            out = self._git("for-each-ref", "--format=%(objectname) %(refname)", pattern)
        else:
            out = self._git("ls-remote", "--", self.remote, pattern)
        found = {}
        for line in out.splitlines():
            sha, _, ref = line.strip().partition(" " if self.scope == "local" else "\t")
            if ref.startswith(CLAIMS):
                found[ref[len(CLAIMS):]] = sha
        return found

    def _fetch(self, ids: list[str]) -> None:
        if self.scope == "local" or not ids:
            return
        self._git("fetch", "--quiet", "--no-tags", "--", self.remote,
                  *(f"+{CLAIMS}{i}:{REMOTE_CLAIMS}{i}" for i in ids))

    def lease(self, sha: str) -> dict:
        code, out, _ = _git_run(self.root, "cat-file", "blob", f"{sha}:{LEASE_FILE}")
        if code != 0:
            return {}
        try:
            value = json.loads(out)
        except ValueError:
            return {}
        return value if isinstance(value, dict) else {}

    def read(self, spec_id: str) -> tuple[str | None, dict]:
        sha = self.heads(spec_id).get(str(spec_id))
        if sha is None:
            return None, {}
        self._fetch([str(spec_id)])
        return sha, self.lease(sha)

    def read_all(self) -> dict[str, tuple[str, dict]]:
        heads = self.heads()
        self._fetch(sorted(heads))
        return {i: (sha, self.lease(sha)) for i, sha in heads.items()}

    # — writing —
    def make(self, lease: dict) -> str:
        code, blob, err = _git_run(self.root, "hash-object", "-w", "--stdin",
                                   stdin=json.dumps(lease, indent=2, sort_keys=True) + "\n")
        if code != 0:
            raise ClaimError(f"git hash-object failed: {err.strip()}")
        code, tree, err = _git_run(self.root, "mktree",
                                   stdin=f"100644 blob {blob.strip()}\t{LEASE_FILE}\n")
        if code != 0:
            raise ClaimError(f"git mktree failed: {err.strip()}")
        env = {**os.environ, **IDENTITY}
        code, sha, err = _git_run(self.root, "commit-tree", tree.strip(), "-m",
                                  f"claim {lease.get('spec')} {lease.get('holder')}", env=env)
        if code != 0:
            raise ClaimError(f"git commit-tree failed: {err.strip()}")
        return sha.strip()

    def swap(self, spec_id: str, new: str | None, expected: str | None) -> bool:
        """Compare-and-swap the claim ref: True when it moved, False when another writer got
        there first. `new=None` deletes; `expected=None` demands the ref be absent."""
        ref = CLAIMS + str(spec_id)
        if self.scope == "local":
            if new is None:
                argv = ("update-ref", "-d", ref, *((expected,) if expected else ()))
            else:
                argv = ("update-ref", ref, new, expected or "0" * 40)
            code, out, err = _git_run(self.root, *argv)
        else:
            lease = f"--force-with-lease={ref}:{expected or ''}"
            code, out, err = _git_run(self.root, "push", "--quiet", "--porcelain", lease,
                                      "--", self.remote, f"{new or ''}:{ref}")
        if code == 0:
            return True
        # Refused: the swap lost when the ref no longer holds what was expected (another writer
        # moved it); a ref still at the expected value means git refused for another reason.
        if self.heads(spec_id).get(str(spec_id)) != expected:
            return False
        lines = [line for line in f"{out}\n{err}".splitlines()
                 if line.startswith("!") or "error" in line or "fatal" in line]
        raise ClaimError(f"git could not move {ref}: {' '.join(lines).strip() or err.strip()}")


def view(lease: dict, me: str, at: datetime.datetime, terminal: bool = False) -> dict:
    """The lease as a caller reads it: `live` is unexpired (past the clock skew) on a spec that is
    not terminal; `mine` is the same machine."""
    expires = _parse(lease.get("expires"))
    expired = expires is None or at > expires + SKEW
    return {"spec": lease.get("spec"), "holder": lease.get("holder"),
            "label": lease.get("label"), "stage": lease.get("stage"),
            "acquired": lease.get("acquired"), "renewed": lease.get("renewed"),
            "expires": lease.get("expires"), "expired": expired, "terminal": terminal,
            "mine": bool(me) and machine_of(lease.get("holder")) == machine_of(me),
            "live": not expired and not terminal}


def new_lease(spec_id: str, holder: str, label: str | None, minutes: int,
              at: datetime.datetime, acquired: str | None = None) -> dict:
    lease = {"spec": str(spec_id), "holder": holder, "stage": "execute",
             "acquired": acquired or _stamp(at), "renewed": _stamp(at),
             "expires": _stamp(at + datetime.timedelta(minutes=minutes))}
    if label:
        lease["label"] = label
    return lease


_SNAPSHOTS: dict[tuple[str, str], dict] = {}


def _existing_machine(root: str) -> str:
    """The id of this clone when it has one; a read never generates it."""
    code, out, _ = _git_run(root, "config", "--local", "--get", "quenching.machineId")
    return out.strip() if code == 0 else ""


def snapshot(root: str, remote: str = "origin") -> dict:
    """Every lease, read once per process: `{available, scope, me, at, leases}`.

    One fetch (`--prune`) mirrors `refs/quenching/claims/*` into `refs/quenching/remote-claims/*`
    and the rest is local. A repository that git cannot read answers `available: False` with no
    leases: reading the reservations never fails the caller."""
    key = (os.path.abspath(root), remote)
    if key in _SNAPSHOTS:
        return _SNAPSHOTS[key]
    me = _existing_machine(root)
    snap = {"available": False, "scope": None, "me": me, "at": now(), "leases": {}}
    try:
        store = Store(root, remote)
        if store.scope == "local":
            found = store.read_all()
        else:
            store._git("fetch", "--quiet", "--no-tags", "--prune", "--", remote,
                       f"+{CLAIMS}*:{REMOTE_CLAIMS}*")
            out = store._git("for-each-ref", "--format=%(objectname) %(refname)", REMOTE_CLAIMS)
            found = {}
            for line in out.splitlines():
                sha, _, ref = line.strip().partition(" ")
                if ref.startswith(REMOTE_CLAIMS):
                    found[ref[len(REMOTE_CLAIMS):]] = (sha, store.lease(sha))
        snap.update(available=True, scope=store.scope,
                    leases={i: lease for i, (_, lease) in found.items()})
    except ClaimError:
        pass
    _SNAPSHOTS[key] = snap
    return snap


def reading(snap: dict, spec_id, terminal: bool = False) -> dict | None:
    """What a chooser needs of one spec's lease — `{holder, label, expires, mine, live}` — or
    `None` when the spec holds none (or the snapshot could not be read)."""
    lease = snap["leases"].get(str(spec_id))
    if lease is None:
        return None
    v = view({**lease, "spec": str(spec_id)}, snap["me"], snap["at"], terminal)
    return {k: v[k] for k in ("holder", "label", "expires", "mine", "live")}
