"""The `github` backend — specs as GitHub issues, over the `gh` CLI.

Moved verbatim out of `specs.py`."""
from __future__ import annotations

import json
import os
import re
import sys

from quenching.common.git import _git
from quenching.specs.backends.base import BackendRefusal, SpecBackend
from quenching.specs.backends.hybrid import (GH_BODY_MAX, GH_PART_MAX, hybrid_join,
                                             hybrid_project, hybrid_split, hybrid_title_join,
                                             hybrid_unwrap, hybrid_unwrap_part, hybrid_wrap,
                                             hybrid_wrap_part)
from quenching.specs.config import CONFIG_FILE, find_repo_root, load_config
from quenching.specs.parse import (LEGACY_DATED_FILE_RE, PHASES, SPEC_FILE_RE,
                                   carry_forward_fields, declared_tags, derive_info,
                                   derive_labels, reconcile_label_set, resolve_one,
                                   strip_frontmatter_keys)


# `gh`'s own exit code for "no host is authenticated", distinct from the 1 it uses for an
# API that answered with an error. Telling the two apart is the whole point of shelling out
# to `gh` instead of speaking HTTP: one is fixed by `gh auth login`, the other is not.
GH_NOT_AUTHENTICATED = 4
# OURS, never one of gh's: the binary is not on PATH, so no process ever started.
GH_MISSING = 127


def _gh_run(cwd: str, *argv: str, stdin: str | None = None) -> tuple[int, str, str]:
    """Exit code, stdout AND stderr of one `gh` command.

    A SIBLING of `_git_run`, deliberately not a reuse of it. The two binaries fail
    differently and the difference IS the contract here: `gh` answers "nobody is logged in"
    with its own exit 4 and a body-less stderr, and "GitHub said no" with exit 1 plus an
    `HTTP <code>` line, while the JSON explaining why goes to STDOUT. A runner that
    flattened those to "nonzero" could not tell a human to run `gh auth login` rather than
    to check the repository name.

    A missing binary comes back as `GH_MISSING` rather than as an exception, so the one
    failure a user is most likely to hit is an ordinary return value on the path every
    caller already handles — never a traceback out of a `subprocess` call.

    A cwd that does not exist is an error and NOT a fallback to `"."`, for the same reason
    `_git_run` refuses it: `gh repo view` reads the git remote of wherever it runs, so the
    fallback would resolve some other repository and then write specs into it.

    60s and not git's 30: this is a round trip to api.github.com, not a local object
    lookup, and a paginated listing of a busy repository legitimately takes seconds."""
    import subprocess
    if not os.path.isdir(cwd):
        return 1, "", f"not a directory: {cwd}"
    try:
        out = subprocess.run(["gh", *argv], capture_output=True, text=True, timeout=60,
                             cwd=cwd, input=stdin)
        return out.returncode, out.stdout, out.stderr
    except FileNotFoundError as e:
        return GH_MISSING, "", str(e)
    except (OSError, ValueError, subprocess.SubprocessError) as e:   # noqa: BLE001
        return 1, "", str(e)


def _gh_said(stdout: str, stderr: str) -> str:
    """The one line worth quoting back from a failed `gh` call.

    `gh api` SPLITS A FAILURE ACROSS BOTH STREAMS: stderr carries its own one-liner
    (`gh: Not Found (HTTP 404)`) and stdout carries GitHub's JSON body, whose `message` is
    the half that says why — "API rate limit exceeded for user ID 1" against a bare
    "HTTP 403". Quoting only stderr loses the reason; quoting only stdout loses the status
    code, and loses everything for the failures that never reach the API at all."""
    head = next((ln.strip() for ln in (stderr or "").splitlines() if ln.strip()), "")
    # gh prefixes its own one-liners with `gh: `, and every refusal built from this already
    # says "gh said" — kept, the message reads "gh said: gh: Not Found".
    head = head[4:].strip() if head.startswith("gh: ") else head
    detail = ""
    try:
        obj = json.loads(stdout or "")
        if isinstance(obj, dict) and isinstance(obj.get("message"), str):
            detail = obj["message"].strip()
    except (json.JSONDecodeError, TypeError, ValueError):
        detail = ""
    if detail and detail.lower() not in head.lower():
        return f"{head} — {detail}" if head else detail
    return head or "gh failed without saying why"


def gh_refusal(action: str, code: int, stdout: str, stderr: str) -> dict:
    """Every way a `gh` call can fail, as an exit-2 refusal a human can act on.

    THREE OUTCOMES, THREE DIFFERENT REMEDIES, and separating them is the reason this
    backend is a subprocess and not an HTTP client: the binary is missing (install it),
    the binary is there but nobody is logged in (`gh auth login`), or GitHub itself said
    no (read what it said). Collapsing them into "github failed" would leave the first two
    looking like an outage and send a human hunting a network problem that is not there.

    Authentication is recognised by TWO signals, not one. `gh api` exits 4 when no host is
    configured at all, but a configured host holding a revoked or wrong token gets as far
    as the API and comes back as an ordinary exit 1 with `HTTP 401` — the same shape as a
    404, and the wrong remedy for it.

    Always exit 2, always a refusal and never a finding: nothing was read and nothing was
    written, which is a different statement from "the specs have a problem"."""
    if code == GH_MISSING:
        return {
            "code": "sp-gh-missing", "exit": 2, "action": action,
            "message": "backend 'github' needs the `gh` CLI and it is not on PATH — install "
                       "GitHub CLI (https://cli.github.com), then run `gh auth login`; no "
                       "spec was read or written",
        }
    said = _gh_said(stdout, stderr)
    if code == GH_NOT_AUTHENTICATED or "HTTP 401" in (stderr or "") \
            or "gh auth login" in (stderr or ""):
        return {
            "code": "sp-gh-unauthenticated", "exit": 2, "action": action, "gh": said,
            "message": f"`gh` is installed but not authenticated for this repository — run "
                       f"`gh auth login`; gh said: {said}",
        }
    return {
        "code": "sp-gh-api-error", "exit": 2, "action": action, "gh": said, "ghExit": code,
        "message": f"github refused {action} — gh said: {said}",
    }


GH_REMOTE_RE = re.compile(r"github\.com[:/]+([^/\s]+)/([^/\s]+?)(?:\.git)?/?$")


def resolve_github_repo(cwd: str) -> tuple[str, dict]:
    """`owner/name` for the repository this checkout points at, or a refusal.

    ASK `gh` FIRST, because it answers the question the API will actually be called with:
    it resolves the remote gh itself would use, honours the `gh repo set-default` a human
    set for a fork, and surfaces the auth failure at RESOLUTION time rather than three
    calls later in the middle of a write.

    The git remote is the fallback and not the primary for exactly that reason — it is a
    string, not an answer: on a fork, `origin` names the fork rather than the repository
    the issues live in. It is kept because a checkout whose gh-to-git integration fails
    (no git on PATH, a checkout gh cannot attribute) still has a legible answer, and
    refusing there would be refusing over a detail of how gh finds the remote.

    Never guesses a repository it cannot name. A wrong answer here does not fail — it
    silently reads and writes somebody else's issues."""
    code, out, err = _gh_run(cwd, "repo", "view", "--json", "nameWithOwner",
                             "--jq", ".nameWithOwner")
    if code == 0 and out.strip():
        return out.strip(), {}
    # The two failures the remote cannot repair — no binary, nobody logged in — refuse here
    # with their own remedy instead of degrading into "could not resolve the repository".
    if code in (GH_MISSING, GH_NOT_AUTHENTICATED) or "gh auth login" in (err or ""):
        return "", gh_refusal("resolving the repository", code, out, err)
    url = _git(cwd, "remote", "get-url", "origin").strip()
    m = GH_REMOTE_RE.search(url) if url else None
    if m:
        return f"{m.group(1)}/{m.group(2)}", {}
    return "", {
        "code": "sp-gh-repo-unresolved", "exit": 2, "remote": url or None,
        "gh": _gh_said(out, err),
        "message": f"backend 'github' could not tell which repository holds the specs — "
                   f"`gh repo view` failed ({_gh_said(out, err)}) and origin "
                   f"({url or 'absent'}) is not a github.com remote; add one, or pick the "
                   f"repository with `gh repo set-default`",
    }


# Color and one-line description for each `spec:` label — GitHub-only, never in
# schema.json. `label:` there is the name every backend with a native tag concept can use;
# color is a GitHub label's own visual property with no Azure Boards tag equivalent, so it
# stays where the one backend that renders it lives. `_store`'s issue PATCH already creates
# a label missing from the repo (Design item 7 of this spec), with an arbitrary color —
# `_ensure_label_colors` is the one-time follow-up that fixes it.
SPEC_LABEL_META = {
    "spec:ranked":       ("c2e0c6", "priority is recorded — a human ranked this spec"),
    "spec:interrogated": ("bfd4f2", "refined is recorded — a real interrogation happened"),
    "spec:approved":     ("0e8a16", "a human said go"),
    "spec:built":        ("5319e7", "the derived stage — task or Handoff work is under way"),
    "spec:reviewed":     ("fbca04", "a human read the whole branch diff"),
    "spec:merged":       ("1d76db", "the branch merged into the integration branch"),
}


class GitHubBackend(SpecBackend):
    """Specs as GitHub issues, reached through `gh api` in a subprocess.

    ONE ISSUE IS ONE SPEC, and the phase is the issue's own state: open is `plans`, closed
    is `archive`. That mapping is not a shortcut — it is the same fact told once. A label
    would be a second declaration of a phase the tracker already knows, and the two would
    diverge the first time somebody closed an issue from the web UI.

    ONE ISSUE BODY IS THE WHOLE DOCUMENT. There are no sub-issues: the retirement and what
    measured it are recorded at HYBRID SERIALISATION above. A document past GitHub's body
    ceiling spills into continuation comments on its own issue, which is the only reason this
    class ever makes a second call for one spec.

    It derives NOTHING. `resolve_one` picks the spec, `derive_info` produces the stages,
    gates, records and tasks, exactly as they are produced for a file on disk; `parse_tasks`
    is the ONLY thing that ever decides a task is checked or blocked. This class turns issues
    into the canonical document and back and does no more than that.

    THE SEVEN FRONTMATTER RECORDS STAY IN THE BODY, none of them a label — every FIELD a
    record carries, that is. Multi-field records (`priority`, `branch`, `merge`, `refined`)
    have no honest single-string label form — encoding `{level, criticality, complexity,
    date}` into a label name would invent a second format only a new parser could read
    back, which is the backend deriving its own encoding exactly where the interface
    forbids it. Keeping them in the body costs the records being invisible in the issue
    list without opening the issue — that gap is what the `spec:` labels below close.

    A `spec:` LABEL PER PRESENT RECORD, PLUS `spec:built` FOR THE DERIVED `executing`
    STAGE, rides inside the same PATCH `_store` already makes — never a second call, never
    read back. This is rendering derived state onto the tracker's own UI, not a second
    encoding of a record's fields: `derive_labels` computes the desired set from `info`
    alone, and `reconcile_label_set` folds it against whatever the issue already carries so
    a human's own label (never under the `spec:` prefix) is untouched. See
    /.docs/standards/architecture/spec-backend.md for the category this is, and why it is not
    the sub-issue projection that was retired.

    The listing is fetched once per process and cached, which is a local cache and NOT a
    store: it is not authoritative, nothing outside this object reads it, and every write
    drops it. It exists because the CLI asks for the listing more than once per command,
    and each ask is a network round trip. Since the listing already carries every body,
    `read_spec` costs NOTHING beyond it for a one-part spec — which is every spec but the
    largest two this repository holds."""

    name = "github"

    def __init__(self, repo: str, cwd: str, types: dict[str, str] | None = None) -> None:
        self.repo = repo
        self.cwd = cwd
        # `workItemTypes.<key>.github`, pre-filtered to the entries this backend can name —
        # never the whole catalogue entry, since `create_spec` needs only the native name.
        self.types = types or {}
        # descriptor, issue number, first chunk, how many parts the marker declares,
        # issue title, and the issue's own labels as of this listing — what the label
        # reconciliation in `_store` diffs against, so it costs no call of its own
        self._rows: list[tuple[dict, int, str, int, str, list[str]]] | None = None
        self._legacy: list[tuple[int, str, str, int, str]] = []
        # `spec:` labels already confirmed correctly colored THIS process — so a repo
        # this tool has been reconciling against for a while pays no repeat GET+PATCH for
        # a label it fixed on an earlier write in the same command.
        self._colors_confirmed: set[str] = set()

    # -- transport ---------------------------------------------------------- #
    def _api(self, action: str, *argv: str, stdin: str | None = None):
        """One `gh api` call, parsed. Raises `BackendRefusal` for every way it can fail."""
        code, out, err = _gh_run(self.cwd, "api", *argv, stdin=stdin)
        if code != 0:
            raise BackendRefusal(gh_refusal(action, code, out, err))
        try:
            return json.loads(out or "null")
        except json.JSONDecodeError as e:
            # Not an API error — gh exited 0 and handed back something unparseable. Named
            # separately so it can never be read as "GitHub said no".
            raise BackendRefusal({
                "code": "sp-gh-bad-response", "exit": 2, "action": action,
                "message": f"`gh api` exited 0 while {action} but its output is not JSON: {e}",
            }) from e

    def _write_api(self, action: str, method: str, path: str, payload: dict):
        """A mutating call, with the payload on STDIN rather than in argv.

        `--input -` and not `-f body=…`: a spec document is kilobytes of markdown with
        newlines, quotes and backticks in it, and every one of those is a way for argv
        quoting to corrupt what lands in the issue.

        THE BODY CEILING IS CHECKED HERE, at the one point every write passes through,
        rather than at each caller — a check per caller is the shape that leaves one out.
        Refusing beats letting GitHub answer 422: in the middle of a migration of dozens of
        specs a 422 is a validation error with no spec's name on it, while this names the
        measured size and the ceiling and emits no call at all.

        IT IS A BACKSTOP AND NO LONGER THE POLICY. Every document write goes through
        `hybrid_split`, which cuts to `GH_PART_MAX` before a payload is ever built, so this
        refusal cannot fire for a spec's own text. It stays because it guards the one point
        every write passes through, and a future caller that builds a body some other way
        must still be unable to hand GitHub something it will answer 422 to."""
        body = payload.get("body")
        if isinstance(body, str) and len(body) > GH_BODY_MAX:
            raise BackendRefusal({
                "code": "sp-gh-body-too-large", "exit": 2, "action": action,
                "size": len(body), "max": GH_BODY_MAX,
                "message": f"the document is {len(body)} characters and a GitHub issue body "
                           f"holds {GH_BODY_MAX} — shorten a section while {action}; nothing "
                           f"was written",
            })
        return self._api(action, "-X", method, path, "--input", "-",
                         stdin=json.dumps(payload))

    # -- the listing, fetched once ------------------------------------------- #
    def _load(self) -> list[tuple[dict, int, str, int, str, list[str]]]:
        if self._rows is not None:
            return self._rows
        # `--slurp` because `--paginate` alone concatenates one JSON array per page, which
        # is not a JSON document. state=all: `archive` is the closed half of the tracker,
        # so a default (open-only) listing would report every archived spec as missing.
        pages = self._api("listing the repository's issues", "--paginate", "--slurp",
                          f"repos/{self.repo}/issues?state=all&per_page=100")
        rows: list[tuple[dict, int, str, int, str, list[str]]] = []
        legacy: list[tuple[int, str, str, int, str]] = []
        for page in (pages or []):
            for issue in (page or []):
                if not isinstance(issue, dict) or "pull_request" in issue:
                    # GitHub models a pull request AS an issue, so `/issues` answers with
                    # both. A PR can never be a spec, and one that happened to carry the
                    # marker would otherwise be listed and then written over.
                    continue
                filename, head, parts = hybrid_unwrap(issue.get("body") or "")
                m = SPEC_FILE_RE.match(filename)
                if not m:
                    # A marker in the pre-fold `YYYY-MM-DD-<slug>.md` form is a SPEC, and it
                    # is kept apart rather than skipped. Skipping is what an ordinary issue
                    # gets, and treating an un-migrated spec that way makes the whole front
                    # vanish silently — `migrate` reads this bucket and nothing else does.
                    if LEGACY_DATED_FILE_RE.match(filename):
                        legacy.append((int(issue.get("number") or 0), filename,
                                       head, parts, str(issue.get("title") or "")))
                    continue
                phase = "archive" if issue.get("state") == "closed" else "plans"
                rows.append(({
                    # The SAME key set `spec_files` returns and nothing more — an extra key
                    # here is a field some command comes to depend on and that the files
                    # backend does not have. `legacy` is False by construction: the v2
                    # folder split never existed here.
                    "phase": phase, "folder": phase, "legacy": False, "file": filename,
                    "path": issue.get("html_url")
                            or f"https://github.com/{self.repo}/issues/{issue.get('number')}",
                    "slug": m.group(1),
                    # For a one-part spec — every spec but the largest — `head` IS the whole
                    # document and this listing has already paid for it. Only a spilled one
                    # costs `read_spec` a second call, and only for the slug it was given.
                }, int(issue.get("number") or 0), head, parts,
                    str(issue.get("title") or ""), self._native_fields(issue),
                    self._issue_labels(issue)))
        self._rows = rows
        self._legacy = legacy
        return rows

    def legacy_rows(self) -> list[tuple[int, str, str, int, str]]:
        """`(number, dated filename, head, parts, issue title)` for every spec still stored
        under the pre-fold basename. `migrate` is the only caller; the read path never sees
        these, because a half-migrated front that half-works is worse than one that says so."""
        self._load()
        return list(self._legacy)

    def _invalidate(self) -> None:
        self._rows = None
        self._legacy = []

    def _issue_number(self, slug: str) -> int:
        return self._issue_parts(slug)[0]

    def _issue_parts(self, slug: str) -> tuple[int, int, list[str]]:
        """`(issue number, how many parts are stored, its current labels)` — all three from
        the listing already in hand, so knowing whether there are stale continuation
        comments to clean up, or which labels a write must reconcile against, costs no
        call of their own.

        The labels come back RAW, `spec:` rendering included — this is the one caller that
        needs them that way, because `reconcile_label_set` diffs against what the issue
        actually carries. Every other reader goes through `declared_tags`."""
        for descriptor, number, _, parts, _title, _native, labels in self._load():
            if descriptor["slug"] == slug:
                return number, parts, labels
        raise BackendRefusal({
            "code": "sp-gh-issue-gone", "exit": 2, "slug": slug,
            "message": f"spec '{slug}' was in the listing and is not there any more — the "
                       f"issue was deleted or transferred while this command ran; nothing "
                       f"was written",
        })

    def _issue_labels(self, issue: dict) -> list[str]:
        """Every label name on `issue`, RAW — the `spec:` rendering included. Only the write
        path wants them this way; readers want `declared_tags` over the result."""
        return [str(lbl.get("name")) for lbl in (issue.get("labels") or [])
                if isinstance(lbl, dict) and lbl.get("name")]

    def _native_fields(self, issue: dict) -> dict:
        """`tags`/`assignee`, reassembled from `labels`/`assignees` — the READ half of
        `## Design` §Armazenado não é projetado. GitHub allows several assignees; the
        canonical field is singular, so only the first is reflected — the same restriction
        the schema already puts on every backend. `start`/`target` have no honest native
        counterpart here (no scheduling fields on an issue) and stay in the document,
        exactly as `date:` already does.

        EVERY `spec:` LABEL IS EXCLUDED. That surface carries two mechanisms — this storage
        and the rendering of derived state `derive_labels` computes — and the reserved prefix
        is what keeps them from reading each other's writes as the spec's own declared
        content. Reassembling one would make the very next write reaffirm a rendered label as
        a tag the document claims."""
        out: dict = {}
        labels = declared_tags(self._issue_labels(issue))
        if labels:
            out["tags"] = labels
        assignees = [a.get("login") for a in (issue.get("assignees") or [])
                    if isinstance(a, dict) and a.get("login")]
        if assignees:
            out["assignee"] = assignees[0]
        return out

    # -- the five primitives -------------------------------------------------- #
    def list_specs(self, phase: str | None = None) -> list[dict]:
        rows = [dict(d) for d, _, _, _, _, _, _ in self._load()
                if phase is None or d["phase"] == phase]
        return sorted(rows, key=lambda r: (PHASES.index(r["phase"]), r["file"]))

    def read_spec(self, slug: str) -> tuple[dict | None, dict]:
        rows = self._load()
        spec, err = resolve_one(self.list_specs(), slug,
                                {d["slug"]: t for d, _, _, _, t, _, _ in rows})
        if err:
            return None, err
        # `spec["slug"]`, never the slug that was ASKED for: a title or approximate match
        # resolved to a different one, and looking the document up by the request would
        # raise right after the resolution succeeded.
        number, head, parts, native_title, native_fields = next(
            (n, d, p, t, f) for descriptor, n, d, p, t, f, _lb in rows
            if descriptor["slug"] == spec["slug"])
        full_text = head if parts <= 1 else self._joined(number, head, parts)
        # The title comes back from the issue's own, which is where the write put it. A
        # document that still carries its own `title:` is returned untouched.
        info = derive_info(spec, hybrid_title_join(full_text, native_title))
        info["frontmatter"].update(native_fields)
        return info, {}

    # `start`/`target` have no native counterpart on an issue (no scheduling fields) and
    # stay in the document, exactly as `date:` already does — only these two are stored.
    GH_STORED_KEYS = ("tags", "assignee")

    def write_spec(self, info: dict, text: str) -> None:
        number, had_parts, current_labels = self._issue_parts(info["slug"])
        # `derive_info` — the SAME shared derivation every read goes through — off the text
        # about to be written, never a second, backend-own way of deciding the stage: this
        # class derives nothing of its own, per its own docstring above. It is also FRESH,
        # which the stored fields need for a second reason: every caller hands `write_spec`
        # the OLD `info` beside the NEW `text`.
        new_info = derive_info(info, text)
        # CARRIED FORWARD where this write's own text is silent — `_store` strips `tags`/
        # `assignee` from the document, so an ordinary write (a section edit, a ticked task)
        # hands text that never mentions them at all; reading that absence as "clear them"
        # would wipe both on the next unrelated write.
        native_fields = carry_forward_fields(info["frontmatter"], new_info["frontmatter"],
                                             self.GH_STORED_KEYS)
        # ONE SURFACE, TWO MECHANISMS, joined here and nowhere else: the spec's own declared
        # tags are STORAGE, the `spec:` set is a RENDERING recomputed on every write. The
        # reserved prefix keeps them disjoint — `reconcile_label_set` replaces the rendered
        # half wholesale and never touches a name outside it, which is exactly what the
        # stored tags are.
        desired = derive_labels(new_info)
        labels = reconcile_label_set(declared_tags(native_fields.get("tags") or []), desired)
        self._store(number, info["slug"], info["file"], text, had_parts, labels,
                    native_fields)
        # AFTER `_store`: a label `_store`'s own PATCH just created does not exist yet
        # before that call, and fixing a nonexistent label's color 404s. Gated on an
        # actual SET change — `set(...)`, not `!=` on the lists — so the no-milestone-
        # change write this backend must cost no round trip for (task 5.2) never reaches
        # this branch at all. GitHub returns a listing's labels alphabetically, never in
        # the schema order `reconcile_label_set` builds `labels` in, so comparing the
        # lists as ORDERED sequences read a same-set reorder as a change every time —
        # measured live against issue #877 on 2026-08-05, before this line read `set(...)`.
        if set(labels) != set(current_labels):
            self._ensure_label_colors(desired)
        self._invalidate()

    def _store(self, number: int, slug: str, filename: str, text: str,
               had_parts: int, labels: list[str] | None = None,
               native_fields: dict | None = None) -> None:
        """The whole write, given an issue number already in hand.

        Split out for `migrate`, which knows every number from its own scan and must not go
        back to the listing between writes: `_invalidate` after each one would make the next
        lookup refetch all eight pages, turning a 73-spec fold into 73 full listings. It is
        the SAME serialisation either way — a migration with a writer of its own would be a
        second implementation that runs exactly once, on the day it matters most.
        `labels`/`assignees`, when given, ride in this SAME PATCH — one call updates title,
        body, the spec's own stored tags and the tracker's `spec:` rendering together, never
        a second round trip. `migrate` omits both: a one-time bulk fold is not the moment to
        reconcile either, and the next ordinary `write_spec` on each folded spec does it for
        free.

        A label GitHub does not already have fails the WHOLE request atomically (measured
        against this repository: `not found`, nothing written), which is the write-refusal
        `## Open Decisions` settles for §3.4: this tool never creates a label to make a
        write of the SPEC'S OWN tags succeed. `_ensure_label_colors` is not an exception to
        that — it grooms the `spec:` set this tool renders and owns, never a name the
        document declared."""
        stripped = strip_frontmatter_keys(text, self.GH_STORED_KEYS)
        stored, title = hybrid_project(slug, stripped)
        chunks = hybrid_split(stored, GH_PART_MAX)
        payload = {"title": title,
                   "body": hybrid_wrap(filename, chunks[0][0], len(chunks))}
        if labels is not None:
            payload["labels"] = labels
        if native_fields is not None and "assignee" in native_fields:
            payload["assignees"] = [native_fields["assignee"]] \
                if native_fields["assignee"] else []
        self._write_api(f"updating issue #{number}", "PATCH",
                        f"repos/{self.repo}/issues/{number}", payload)
        self._sync_parts(number, chunks, had_parts)

    def _ensure_label_colors(self, names: list[str]) -> None:
        """Fix color and description for whichever of `names` are not already confirmed
        correct this process — called only from `write_spec`, and only when a write is
        about to change an issue's labels, so a no-milestone-change write never reaches
        here at all.

        One GET of the repo's own label registry, then a PATCH per label that still
        disagrees — never more than once per label per process, per `_colors_confirmed`."""
        todo = [n for n in names if n in SPEC_LABEL_META and n not in self._colors_confirmed]
        if not todo:
            return
        existing = {l.get("name"): (l.get("color"), l.get("description"))
                   for page in (self._api("listing labels", "--paginate", "--slurp",
                                          f"repos/{self.repo}/labels?per_page=100") or [])
                   for l in (page or [])}
        for name in todo:
            color, desc = SPEC_LABEL_META[name]
            if existing.get(name) != (color, desc):
                self._write_api(f"fixing color for label {name!r}", "PATCH",
                                f"repos/{self.repo}/labels/{name}",
                                {"color": color, "description": desc})
            self._colors_confirmed.add(name)

    def create_spec(self, phase: str, filename: str, text: str) -> str:
        m = SPEC_FILE_RE.match(filename)
        fresh = derive_info({"phase": phase}, text)
        stripped = strip_frontmatter_keys(text, self.GH_STORED_KEYS)
        stored, title = hybrid_project(m.group(1) if m else filename, stripped)
        chunks = hybrid_split(stored, GH_PART_MAX)
        payload = {"title": title,
                  "body": hybrid_wrap(filename, chunks[0][0], len(chunks))}
        # The same union `write_spec` makes, from an empty current set: the spec's declared
        # tags plus whatever the fresh document already renders. A capture form renders
        # nothing (no records, `captured` stage), so this is usually just the tags — but
        # deriving it rather than assuming that keeps the two paths one rule.
        labels = reconcile_label_set(declared_tags(fresh["frontmatter"].get("tags") or []),
                                     derive_labels(fresh))
        if labels:
            payload["labels"] = labels
        if fresh["frontmatter"].get("assignee"):
            payload["assignees"] = [fresh["frontmatter"]["assignee"]]
        issue = self._write_api("creating an issue", "POST", f"repos/{self.repo}/issues",
                                payload)
        number = int((issue or {}).get("number") or 0)
        url = (issue or {}).get("html_url") or f"https://github.com/{self.repo}/issues/{number}"
        # The abstract `workItemType:` key, projected to GitHub's own Issue Type — through
        # `_set_type` (`gh issue edit --type`), NEVER a `type` field on the create payload
        # above. MEASURED live (2026-08-07, holetz/claude-quenching#898): the REST create
        # silently drops an invalid name — `ok: true`, `issueType: null`, no error at all —
        # while `gh issue edit --type` validates against the repository's own types and
        # refuses loudly. A second call rather than free, but only once, and only when a
        # type actually resolves.
        type_key = fresh["frontmatter"].get("workItemType")
        type_name = self.types.get(type_key) if type_key else None
        if type_name:
            self._set_type(number, type_name)
        elif type_key:
            # The entry exists — `resolve_type_key` already gated `--type` at `new` — but
            # names no `github` translation. Never a refusal: an entry may exist for one
            # backend only without breaking the other (§Design), so the create proceeds
            # untyped and only says why.
            print(f"note: workItemType '{type_key}' has no `github` name declared in "
                  f"{CONFIG_FILE} — no type applied to this issue", file=sys.stderr)
        self._sync_parts(number, chunks)
        if phase == "archive":
            # Created open and then closed, because "closed" is not a state an issue can be
            # born in. Two calls for a case `new` never takes — only a migration does.
            self._set_state(number, "closed")
        self._invalidate()
        return url

    def move_spec(self, info: dict, dest_phase: str) -> str:
        number = self._issue_number(info["slug"])
        issue = self._set_state(number, "closed" if dest_phase == "archive" else "open")
        self._invalidate()
        return (issue or {}).get("html_url") \
            or f"https://github.com/{self.repo}/issues/{number}"

    def _set_state(self, number: int, state: str):
        return self._write_api(f"setting issue #{number} to {state}", "PATCH",
                               f"repos/{self.repo}/issues/{number}", {"state": state})

    def _set_type(self, number: int, type_name: str) -> None:
        """`gh issue edit --type`, the one PORCELAIN call this backend makes — never `gh api`.

        The REST `POST .../issues` this backend otherwise uses for everything silently drops
        an invalid `type` field: MEASURED live against `holetz/claude-quenching#898`, a create
        with a nonexistent type name came back `ok: true` with `issueType: null`, no error at
        all. `gh issue edit --type` is the one mechanism proven to validate against the
        repository's own issue types and refuse loudly for the same name — the same shape
        `gh_refusal` already reports for `gh api`, reused here because `gh`'s three failure
        modes (missing binary, unauthenticated, said no) are the same across both."""
        action = f"setting issue #{number}'s type to '{type_name}'"
        code, out, err = _gh_run(self.cwd, "issue", "edit", str(number),
                                 "--repo", self.repo, "--type", type_name)
        if code != 0:
            raise BackendRefusal(gh_refusal(action, code, out, err))

    # -- the continuation comments a spilled document uses --------------------- #
    def _comments(self, number: int) -> list[dict]:
        return self._api(f"listing comments on #{number}",
                         "--paginate", "--slurp",
                         f"repos/{self.repo}/issues/{number}/comments?per_page=100") or []

    def _part_comments(self, number: int) -> list[tuple[int, dict]]:
        """`(index, comment)` for this issue's continuation comments, in part order.

        Ordinary discussion on a spec issue stays possible and is skipped here, the same way
        `_load` skips an issue without the spec marker: a store that assumed every comment was
        its own would eat a human's note the first time somebody left one."""
        found: list[tuple[int, dict]] = []
        for page in self._comments(number):
            for comment in (page if isinstance(page, list) else [page]):
                index, _, _ = hybrid_unwrap_part((comment or {}).get("body") or "")
                if index:
                    found.append((index, comment))
        found.sort(key=lambda row: row[0])
        return found

    def _joined(self, number: int, head: str, parts: int) -> str:
        """The whole document for a spilled spec — one extra call, made only when the marker
        on the body says there is more.

        A part the marker promised and the comments do not hold is a REFUSAL, not a shorter
        document: silently returning the head would hand every downstream command a spec whose
        `## Tasks` simply stops, and the next write would then persist that truncation as the
        new truth."""
        chunks = [(head, False)]      # nothing precedes the head, so its flag is unused
        for _, comment in self._part_comments(number):
            _, chunk, eol = hybrid_unwrap_part(comment.get("body") or "")
            chunks.append((chunk, eol))
        if len(chunks) != parts:
            raise BackendRefusal({
                "code": "sp-gh-parts-missing", "exit": 2, "issue": number,
                "found": len(chunks), "declared": parts,
                "message": f"issue #{number} declares {parts} document parts and "
                           f"{len(chunks)} are present — a continuation comment was deleted; "
                           f"nothing was read and nothing was written",
            })
        return hybrid_join(chunks)

    def _sync_parts(self, number: int, chunks: list[tuple[str, bool]],
                    had_parts: int = 1) -> None:
        """Make the issue's continuation comments match `chunks[1:]` exactly.

        COSTS NOTHING FOR A ONE-PART SPEC THAT WAS ALREADY ONE PART, which is every write this
        repository will make but two: `chunks` is in hand and `had_parts` comes from the listing
        already fetched, so the common case returns before any call is made.

        `had_parts` is why the early return is safe. A document that USED to spill and no longer
        does still has stale comments to delete, and a check that only looked at the new part
        count would leave them there to be joined back on the next read — a truncation that
        would then be persisted as the truth by the write after it.

        A comment the document no longer needs is DELETED, not retired: unlike an issue, a
        comment really can be deleted with an ordinary token, so there is no leftover to skip
        on the next read and no second meaning for a marker to carry."""
        want = chunks[1:]
        if not want and had_parts <= 1:
            return
        existing = self._part_comments(number)
        for position, (chunk, eol) in enumerate(want, start=2):
            body = hybrid_wrap_part(position, len(chunks), chunk, eol)
            if position - 2 < len(existing):
                cid = existing[position - 2][1]["id"]
                self._write_api(f"updating continuation comment {cid} on #{number}", "PATCH",
                                f"repos/{self.repo}/issues/comments/{cid}", {"body": body})
            else:
                self._write_api(f"adding a continuation comment to #{number}", "POST",
                                f"repos/{self.repo}/issues/{number}/comments", {"body": body})
        for _, comment in existing[len(want):]:
            self._api(f"deleting a stale continuation comment on #{number}",
                      "-X", "DELETE", f"repos/{self.repo}/issues/comments/{comment['id']}")


def open_github_backend(root: str) -> tuple[SpecBackend | None, dict]:
    """The `github` backend for this workspace, or the refusal that says why not.

    Resolution happens HERE and not in `GitHubBackend.__init__`, so the cost — one `gh`
    round trip — is paid by the first command that actually needs a spec, on the same
    "on demand" rule `open_backend` applies to the files worktree. It is also what makes
    the missing-binary and not-logged-in refusals arrive at the START of a command instead
    of halfway through a write."""
    cwd = find_repo_root(root)
    repo, err = resolve_github_repo(cwd)
    if err:
        return None, err
    types = {k: v["github"] for k, v in load_config(root)["workItemTypes"].items()
             if v.get("github")}
    return GitHubBackend(repo, cwd, types=types), {}
