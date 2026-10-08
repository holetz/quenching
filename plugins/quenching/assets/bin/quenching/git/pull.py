"""`cq git pr create` and `cq git pr merge` — the GitHub pull-request writes, with a fixed argv.

The `git-steward` holds no `gh pr create`/`gh pr merge` grant: a pattern on the command text
never fenced `-d`, `-s`, `-r` or an alias. Here every `gh` argv is built in this module. `create`
names `--base` and `--head` explicitly and sends the body on stdin; `merge` reads `gh pr checks`
first and merges only with every check green — a `skipping` check the gate requires is not
green — and the PR's `mergeStateStatus` clean, pinning the head it read with
`--match-head-commit`, always with `--merge` — never `--squash`,
`--rebase`, `--delete-branch`, `--admin` or `--auto`. The Azure route stays in the
`/quenching:git:pr:create` body.

Exit 0 done · 1 findings (`gh` refused, or a check red, pending or absent — `reason` names
which) · 2 refusal (a malformed name or URL)."""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys
import time
from types import SimpleNamespace

from quenching.common.output import FINDINGS, OK, emit, refuse
from quenching.git.audit import _branch_ok
from quenching.specs.commands.fields import cmd_record
from quenching.specs.backends import open_backend
from quenching.specs.commands.output import Emitter, read_one
from quenching.specs.config import find_repo_root

PR_URL = re.compile(r"https://[A-Za-z0-9.-]+/[\w.-]+/[\w.-]+/pull/(\d+)")
GREEN = {"pass", "skipping"}
MERGEABLE = {"CLEAN", "HAS_HOOKS"}
RED = {"fail", "cancel"}
POLL_S = 20
WAIT_MAX_S = 540
GH_TIMEOUT_S = 120


def _gh(*argv: str, stdin: str | None = None) -> tuple[int, str, str]:
    try:
        done = subprocess.run(["gh", *argv], capture_output=True, text=True, input=stdin or "",
                              timeout=GH_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError) as e:
        return 127, "", str(e)
    return done.returncode, done.stdout, done.stderr


def _checks(url: str) -> tuple[str, list[dict], str]:
    """`green`, `red`, `pending`, `none` or `error`, the checks, and gh's message."""
    code, out, err = _gh("pr", "checks", url, "--json", "name,bucket")
    try:
        checks = json.loads(out) if out.strip() else []
    except json.JSONDecodeError:
        checks = None
    if not isinstance(checks, list):
        return "error", [], (err or out).strip()
    if not checks:
        return ("none" if code == 0 or "no checks" in err.lower() else "error"), [], err.strip()
    buckets = {c.get("bucket") for c in checks if isinstance(c, dict)}
    if buckets & RED:
        return "red", checks, err.strip()
    if buckets <= GREEN and all(isinstance(c, dict) for c in checks):
        if "skipping" in buckets:
            skipped = _required_skipped(url, checks)
            if skipped:
                return "skipped", [c for c in checks if c.get("name") in skipped], err.strip()
        return "green", checks, err.strip()
    return "pending", checks, err.strip()


def _required_skipped(url: str, checks: list[dict]) -> set[str]:
    """Names of the `skipping` checks the gate requires; when gh cannot list the required
    checks, every skipping check counts as required."""
    skipping = {c.get("name") for c in checks if c.get("bucket") == "skipping"}
    code, out, err = _gh("pr", "checks", url, "--required", "--json", "name")
    if code == 1 and "no required checks reported" in err.lower():
        return set()
    try:
        required = ({c.get("name") for c in json.loads(out)}
                    if code in (0, 8) and out.strip() else None)
    except (json.JSONDecodeError, AttributeError, TypeError):
        required = None
    return skipping if required is None else skipping & required


def _view(url: str) -> tuple[str, str]:
    """The PR's head sha and `mergeStateStatus`, `("", "")` when gh cannot say."""
    _, out, _ = _gh("pr", "view", url, "--json", "headRefOid,mergeStateStatus")
    try:
        data = json.loads(out)
        return str(data["headRefOid"]), str(data["mergeStateStatus"])
    except (json.JSONDecodeError, KeyError, TypeError):
        return "", ""


def _merge(args) -> int:
    match = PR_URL.fullmatch(args.url or "")
    if not match:
        return refuse({"code": "git-pr-url-invalid",
                       "message": f"not a pull-request URL: {args.url}"}, args.json)
    if not 0 <= args.wait <= WAIT_MAX_S:
        return refuse({"code": "git-pr-wait-invalid",
                       "message": f"--wait must be between 0 and {WAIT_MAX_S} seconds"}, args.json)
    deadline = time.monotonic() + args.wait
    head, _ = _view(args.url)
    while True:
        state, checks, message = _checks(args.url)
        if state != "pending" or time.monotonic() + POLL_S > deadline:
            break
        print(f"checks pending; re-reading in {POLL_S}s", file=sys.stderr, flush=True)
        time.sleep(POLL_S)
    names = sorted(str(c.get("name")) for c in checks if isinstance(c, dict)
                   and (c.get("bucket") not in GREEN or state == "skipped"))
    payload = {"ok": False, "url": args.url, "number": int(match.group(1)), "checks": state,
               "notGreen": names}
    if state != "green":
        payload["reason"] = {"red": "failed", "pending": "pending", "none": "no-checks",
                                    "skipped": "skipped-required"}.get(
            state, "checks-unreadable")
        if message:
            payload["message"] = message
        emit(args.json, payload, f"not merged: {payload['reason']} {' '.join(names)}".rstrip())
        return FINDINGS
    now, merge_state = _view(args.url)
    if not head or now != head or merge_state not in MERGEABLE:
        payload.update(reason="merge-state", message=f"head {head or '?'} -> {now or '?'}, "
                       f"mergeStateStatus {merge_state or 'unreadable'}")
        emit(args.json, payload, f"not merged: {payload['message']}")
        return FINDINGS
    code, out, err = _gh("pr", "merge", args.url, "--merge", f"--match-head-commit={head}")
    if code != 0:
        payload.update(reason="merge-refused", message=(err or out).strip())
        emit(args.json, payload, f"not merged: {payload['message']}")
        return FINDINGS
    payload["ok"] = True
    emit(args.json, payload, f"merged {args.url} (--merge)")
    return OK


class _Quiet(Emitter):
    """Collects what `cmd_record` would print, so the verb emits ONE document."""

    def __init__(self) -> None:
        self.seen: dict = {}

    def emit(self, as_json: bool, obj: dict, human: str) -> None:
        self.seen = obj


def _stamp(spec: str, number: int, url: str) -> dict:
    """Merge the `pr` record through the same function `cq specs record` runs."""
    quiet = _Quiet()
    ns = SimpleNamespace(spec=spec, name="pr", json=True, set=[
        f"number={number}", f"url={url}", f"date={datetime.date.today().isoformat()}"])
    try:
        code = cmd_record(ns, find_repo_root(os.getcwd()), quiet)
    except Exception as e:  # the PR exists already: a stamp that blew up is reported, not raised
        return {"ok": False, "message": str(e)}
    if code != 0:
        return {"ok": False, "message": quiet.seen.get("message", f"record exited {code}")}
    return {"ok": True, "value": quiet.seen.get("value")}


def _spec_vs_head(spec: str, head: str) -> dict | None:
    """Refuse BEFORE any PR exists: the spec must exist and own `head`.

    The spec owns the branch its `branch.work` record names; before that record exists, the
    branch name must carry the spec's id (`plan/<id>-<slug>`). `None` means the pair is fine."""
    quiet = _Quiet()
    backend, err = open_backend(find_repo_root(os.getcwd()))
    info, err2 = (None, err) if err else read_one(backend, spec, quiet)
    if err2 or not info:
        return {"code": "git-pr-spec-unknown",
                "message": f"--spec {spec} does not resolve: "
                           f"{(err2 or {}).get('message', 'no such spec')}"}
    work = ((info.get("frontmatter") or {}).get("branch") or {}).get("work")
    sid = str(info["id"])
    if work:
        owned = work == head
    else:
        owned = re.match(rf"(?:.+/)?{re.escape(sid)}-", head) is not None
    if not owned:
        return {"code": "git-pr-spec-head-mismatch",
                "message": f"spec {sid} does not own branch {head}"
                           + (f" (its branch record is {work})" if work else "")}
    return None


def _record(args) -> int:
    """`pr record`: the Azure route stamps the `pr` record through the same function."""
    number, url = args.number, args.url
    if number < 1 or not url.startswith("https://") or "/_apis/" in url:
        return refuse({"code": "git-pr-record-invalid",
                       "message": "--number must be positive and --url the PR's https webUrl "
                                  "(never an /_apis/ URL)"}, args.json)
    bad = _spec_vs_head(args.spec, args.head)
    if bad:
        return refuse(bad, args.json)
    stamp = _stamp(args.spec, number, url)
    payload = {"ok": stamp["ok"], "number": number, "url": url, "head": args.head, "pr": stamp}
    if not stamp["ok"]:
        payload.update(reason="stamp-failed", message=stamp["message"])
    emit(args.json, payload, f"pr record stamped: #{number} {url}" if stamp["ok"]
         else f"`pr` record not stamped: {stamp['message']}")
    return OK if stamp["ok"] else FINDINGS


def _create(args) -> int:
    cwd = os.getcwd()
    for label, value in (("base", args.base), ("head", args.head)):
        if value.startswith("-") or not _branch_ok(cwd, value):
            return refuse({"code": "git-pr-ref-invalid",
                           "message": f"{label} is not a branch name: {value}"}, args.json)
    if not args.title.strip():
        return refuse({"code": "git-pr-title-blank", "message": "--title may not be blank"},
                      args.json)
    if args.spec:
        bad = _spec_vs_head(args.spec, args.head)
        if bad:
            return refuse(bad, args.json)
    code, out, err = _gh("pr", "create", f"--base={args.base}", f"--head={args.head}",
                         f"--title={args.title}", "--body-file=-", stdin=args.body)
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    url = next((line for line in reversed(lines) if PR_URL.fullmatch(line)), None)
    if code != 0 or url is None:
        emit(args.json, {"ok": False, "reason": "create-refused",
                         "message": (err or out).strip()}, f"PR not created: {(err or out).strip()}")
        return FINDINGS
    number = int(PR_URL.fullmatch(url).group(1))
    payload = {"ok": True, "url": url, "number": number, "base": args.base, "head": args.head}
    if args.spec:
        payload["pr"] = stamp = _stamp(args.spec, number, url)
        if not stamp["ok"]:
            payload.update(ok=False, reason="stamp-failed", message=stamp["message"])
            emit(args.json, payload, f"PR #{number}: {url} opened; `pr` record not stamped: "
                                     f"{stamp['message']}")
            return FINDINGS
    emit(args.json, payload, f"PR #{number}: {url}")
    return OK


def cmd_pr(args) -> int:
    if args.action == "record":
        return _record(args)
    return _merge(args) if args.action == "merge" else _create(args)
