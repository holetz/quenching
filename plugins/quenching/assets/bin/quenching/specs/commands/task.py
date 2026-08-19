"""The executor's two verbs — `task` and `discover`.

`task` flips a checkbox MECHANICALLY and records the anchor of the commit that implements it;
`discover` appends one line to `## Discoveries`. Both are written during a build, and both exist
so nothing does string surgery on a spec from the caller's side."""
from __future__ import annotations

from quenching.specs.backends import open_backend
from quenching.specs.commands.output import Emitter, read_one
from quenching.specs.parse.edit import upsert_section
from quenching.specs.parse.tasks import (BLOCKED_REASON_RE, CHECKBOX_RE, COMMIT_SHA_RE,
                                         SUBJECT_RE)


def _find_task(tasks: list[dict], ident: str) -> dict | None:
    for t in tasks:
        if t["id"] == ident or str(t["index"]) == ident:
            return t
    return None


def cmd_task(args, root: str, out: Emitter) -> int:
    """Flip a checkbox MECHANICALLY — never by string surgery on the caller's side.

    `--block` writes the reason into the line itself. That visibility is the whole point:
    v1 kept an attempt counter in `.specs.json` that nobody read, and a task went quiet
    after five failures with no trace of why.

    `--check` may carry `--subject`, `--commit`, both, or neither. `--commit <sha>` is
    called AFTER the commit implementing the task already exists — the CLI records the sha
    it is given, it never resolves or invents one — and is additive: `--subject` keeps
    working exactly as before for any caller that has not moved to the sha anchor. Whichever
    write actually lands the anchor (`backend.write_spec`, below) is where a failure — a
    `gh api` call included — is reported, never swallowed."""
    backend, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    info, err = read_one(backend, args.spec, out)
    if err:
        return out.emit_err(args.json, err)
    ident = args.check or args.uncheck or args.block
    if not ident:
        out.emit(args.json, {"ok": False, "code": "sp-no-action",
                             "message": "pass --check, --uncheck or --block"},
                 "error: pass --check, --uncheck or --block")
        return 1
    # The subject names WHICH COMMIT IMPLEMENTS THIS TASK, so it is meaningful only on the
    # transition that says the task is done. On --uncheck any recorded anchor is dropped
    # rather than left behind pointing at work the checkbox no longer claims.
    if args.subject and not args.check:
        out.emit(args.json, {"ok": False, "code": "sp-subject-without-check",
                             "message": "--subject records the commit that implements a task, "
                                        "so it goes with --check"},
                 "error: --subject goes with --check")
        return 1
    if args.subject is not None and not SUBJECT_RE.match(args.subject.strip()):
        out.emit(args.json, {"ok": False, "code": "sp-bad-subject", "subject": args.subject,
                             "message": "a commit subject must be one non-empty line"},
                 "error: a commit subject must be one non-empty line")
        return 1
    # --commit is the sha form of the SAME anchor, meant to be called AFTER the commit that
    # implements the task already exists — the CLI never invents or looks up a sha, it only
    # records the one the caller already has. Same rule as --subject: meaningful only on the
    # transition that says the task is done, so it goes with --check too. It is additive,
    # not a replacement: a caller may still pass --subject alone, exactly as before.
    if args.commit and not args.check:
        out.emit(args.json, {"ok": False, "code": "sp-commit-without-check",
                             "message": "--commit records the sha of the commit that implements "
                                        "a task, so it goes with --check"},
                 "error: --commit goes with --check")
        return 1
    if args.commit is not None and not COMMIT_SHA_RE.match(args.commit.strip()):
        out.emit(args.json, {"ok": False, "code": "sp-bad-commit-sha", "commit": args.commit,
                             "message": "--commit takes a git sha (hex, 7-40 characters), not "
                                        "free text"},
                 "error: --commit takes a git sha (hex, 7-40 characters), not free text")
        return 1
    if args.block and not args.reason:
        out.emit(args.json, {"ok": False, "code": "sp-no-reason",
                             "message": "--block requires --reason"},
                 "error: --block requires --reason (a blocked task without a reason is the "
                 "hidden state this replaced)")
        return 1
    t = _find_task(info["tasks"], ident)
    if not t:
        out.emit(args.json, {"ok": False, "code": "sp-unknown-task", "task": ident,
                             "message": f"no task '{ident}' in {info['slug']}"},
                 f"error: no task '{ident}' in {info['slug']}")
        return 1

    lines = info["text"].splitlines(keepends=True)
    line = lines[t["lineno"]]
    m = CHECKBOX_RE.match(line.rstrip("\n"))
    if not m:
        out.emit(args.json, {"ok": False, "code": "sp-line-drift", "task": ident,
                             "lineno": t["lineno"],
                             "message": "the parsed line is not a checkbox — the file changed"},
                 "error: the parsed line is not a checkbox — re-read the spec")
        return 1
    mark = {"check": "x", "uncheck": " ", "block": "!"}[
        "check" if args.check else "uncheck" if args.uncheck else "block"]
    body = m.group(3).rstrip()
    body = BLOCKED_REASON_RE.sub("", body).rstrip()      # drop any stale blocked suffix
    if args.block:
        body = f"{body} — blocked: {args.reason.strip()}"
    lines[t["lineno"]] = f"{m.group(1)}- [{mark}] {body}\n"

    # Upsert the `subject:`/`commit:` metadata lines — replace one that is already there,
    # otherwise append it after the task's last metadata line (or right under the
    # checkbox). The two anchors are independent: passing one never disturbs an existing
    # line for the other, and both may be written in the same call while a spec transitions
    # from the subject anchor to the sha one. New lines are inserted together in ONE slice
    # so inserting one never shifts the position computed for the other.
    subject = None
    commit = None
    new_entries: list[str] = []
    if args.subject:
        subject = args.subject.strip()
        entry = f"{t['metaIndent']}subject: {subject}\n"
        if t["subjectLineno"] is not None:
            lines[t["subjectLineno"]] = entry
        else:
            new_entries.append(entry)
    if args.commit:
        commit = args.commit.strip()
        entry = f"{t['metaIndent']}commit: {commit}\n"
        if t["commitLineno"] is not None:
            lines[t["commitLineno"]] = entry
        else:
            new_entries.append(entry)
    if new_entries:
        lines[t["metaInsertAt"]:t["metaInsertAt"]] = new_entries
    if not args.subject and not args.commit and args.uncheck:
        # Drop whichever anchor the line carries — `subject:`, `commit:` written by
        # `--commit`, or the legacy `commit:` on a spec written before either form applied
        # to it. Highest offset first, so deleting one cannot shift the index of the other.
        for off in sorted((o for o in (t["subjectLineno"], t["commitLineno"])
                           if o is not None), reverse=True):
            del lines[off]
    # THE FAILURE-REPORTING CONTRACT: this call is the one that can fail out from under a
    # tick that already looks applied to `lines`. The backend either persists the document or
    # raises. `GitHubBackend` pushes the same edited task block into the task's own
    # `GitHubBackend` pushes the same edited document into the issue body (`write_spec`) and
    # raises `BackendRefusal` — never swallowed
    # — the instant `gh api` fails, e.g. on a network error. `main()` is the one place that
    # exception becomes an exit code and an `ok: false` JSON body; nothing here catches it
    # and nothing here prints a success message before this line returns.
    backend.write_spec(info, "".join(lines))

    verb = "checked" if args.check else "unchecked" if args.uncheck else "blocked"
    anchor_lines = ((f"\n  subject: {subject}" if subject else "") +
                    (f"\n  commit: {commit}" if commit else ""))
    out.emit(args.json,
             {"ok": True, "slug": info["slug"], "task": ident, "action": verb,
              "state": mark, "text": body, "subject": subject, "commit": commit,
              "reason": args.reason if args.block else None},
             f"task {ident} {verb}: {body}" + anchor_lines)
    return 0


def cmd_discover(args, root: str, out: Emitter) -> int:
    """Append one line to `## Discoveries`, creating the section when absent.

    Captured INDISCRIMINATELY during execution — whether a discovery is worth acting on is
    triage's judgment, not the executor's, and the cost of asking mid-build is a human
    interrupted for something that may not matter."""
    backend, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    info, err = read_one(backend, args.spec, out)
    if err:
        return out.emit_err(args.json, err)
    entry = f"- {args.text.strip()}"
    sec = info["sections"].get("Discoveries")
    if sec and sec["filled"]:
        block = f"## Discoveries\n{sec['body'].rstrip()}\n{entry}\n"
    else:
        block = f"## Discoveries\n\n{entry}\n"
    new_text, _ = upsert_section(info, "Discoveries", block)
    backend.write_spec(info, new_text)
    out.emit(args.json,
             {"ok": True, "slug": info["slug"], "entry": args.text.strip()},
             f"recorded in ## Discoveries: {args.text.strip()}")
    return 0
