"""The specs pillar's argument declarations, its subcommand map, and its entry point.

`build_parser` declares every argument, `DISPATCH` maps a subcommand name to the function that
answers it, and `main` is the pillar's whole entry: the UTF-8 reconfiguration, the writer lock,
the invocation's `Emitter`, and the single place a `BackendRefusal` becomes an exit code.
`cq specs …` mounts on these three.

Every dispatched verb takes `(args, root, out)`. The third is the invocation's output layer,
carrying the resolution receipt: an object with this call's lifetime, handed down rather than a
module global reached for.

`selftest` is NOT here. `cmd_selftest` is a test and migrates to `tests/`; whether the verb
survives is task 6.3's to decide, and re-adding it is one subparser and one `DISPATCH` row."""
from __future__ import annotations

import argparse
import sys

from quenching.common.version import VERSION
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.commands.create import cmd_new
from quenching.specs.commands.doctor import cmd_config, cmd_doctor
from quenching.specs.commands.fields import cmd_field, cmd_record, cmd_verification
from quenching.specs.commands.find import cmd_find
from quenching.specs.commands.granular import cmd_section, cmd_show
from quenching.specs.commands.migrate import cmd_migrate
from quenching.specs.commands.next import cmd_next
from quenching.specs.commands.output import Emitter
from quenching.specs.commands.parallel import cmd_parallel
from quenching.specs.commands.promote import cmd_promote
from quenching.specs.commands.read import cmd_export, cmd_list, cmd_status
from quenching.specs.commands.release import cmd_release
from quenching.specs.commands.task import cmd_discover, cmd_task
from quenching.specs.commands.validate import cmd_validate
from quenching.specs.config import find_specs_root
from quenching.specs.parse import PHASES
from quenching.specs.schema import DEFAULT_VERIFICATION, OUTCOMES, VERIFICATION_POLICIES
from quenching.specs.worktree import writer_lock


def build_parser() -> tuple[argparse.ArgumentParser, argparse._SubParsersAction]:
    p = argparse.ArgumentParser(prog="cq specs",
                                description="deterministic trail for the specs front")
    p.add_argument("--root", help="the `/.specs/` workspace directory (default: nearest `/.specs/` upward)")
    p.add_argument("--version", action="store_true", help="print the version and exit")
    sub = p.add_subparsers(dest="cmd")

    def add_json(sp):
        sp.add_argument("--json", action="store_true", help="machine-readable output")
        return sp

    sp = add_json(sub.add_parser("new", help="capture a spec into plans/"))
    sp.add_argument("name")
    sp.add_argument("--title")
    sp.add_argument("--verification", choices=list(VERIFICATION_POLICIES),
                    help=f"when the suite runs (default: {DEFAULT_VERIFICATION})")
    sp.add_argument("--subject",
                    help="a key from `azurePlacement.subjects` — applies its parent (where "
                         "the backend has one) and its fixed tags; omit to fall back to "
                         "`defaultSubject`")
    sp.add_argument("--type",
                    help="a key from `workItemTypes` — recorded as `workItemType:` in the "
                         "new spec's frontmatter; omit to resolve one later, at build time")
    sp.add_argument("--summary",
                    help="ONE line — the summary line the ranked table prints; written the "
                         "same as `cq specs summary`")
    sp.add_argument("--tags",
                    help="a comma-separated list — REPLACES the whole list, same as "
                         "`cq specs tags`; the subject's fixed tags are folded in "
                         "automatically and need not be repeated")
    # No `choices=`: argparse would refuse a bad value with a usage message on stderr and no
    # JSON, the same reason `verification`'s `policy` argument below has none. The refusal
    # carries `sp-bad-complexity` and the declared levels like every other refusal here.
    sp.add_argument("--complexity",
                    help="one of low/medium/high/xhigh — written into the new spec's "
                         "`priority.complexity` record")

    sp = add_json(sub.add_parser("list", help="every spec, by folder and derived stage"))
    sp.add_argument("--phase", choices=list(PHASES),
                    help="cut the listing to one phase (default: every phase)")

    sp = add_json(sub.add_parser("status", help="one spec's sections, stage, tasks, gates"))
    sp.add_argument("--spec", required=True)

    sp = add_json(sub.add_parser("show", help="granular read: ONE task, the map by default, "
                                              "the document only with --full (section "
                                              "bodies are `section`'s)"))
    sp.add_argument("--spec", required=True)
    sp.add_argument("--task", action="append", metavar="ID",
                    help="one task's line and metadata, by id or index; repeatable")
    sp.add_argument("--full", action="store_true",
                    help="the WHOLE document — never the default, because every caller "
                         "that did not need it pays for it in context on every later turn")

    sp = add_json(sub.add_parser("section", help="read or write N sections in ONE call"))
    sp.add_argument("spec")
    sp.add_argument("heading", nargs="?",
                    help="one canonical heading, or several comma-separated; returned in "
                         "the order asked. Omit when --moment resolves the list instead")
    sp.add_argument("--moment", choices=["decision", "build", "close"],
                    help="read every canonical section declared this moment, in canonical "
                         "order, instead of an enumerated heading list")
    sp.add_argument("--write", action="store_true",
                    help="replace one or more headings from stdin, creating each in "
                         "canonical position. Several: open the stream on `## <Heading>` "
                         "lines, one per body, and the set must match what was declared "
                         "here; a stream carrying no heading is one raw body under the one "
                         "heading declared")
    sp.add_argument("--scope", choices=["global", "current"],
                    help="narrow ## Handoff to one block — the evergreen global one, or that "
                         "one plus the ### N. matching the next actionable task's section. "
                         "Reading, it composes with the other headings asked for (--moment "
                         "build included), which come back whole; writing, it replaces just "
                         "that block, leaves every other untouched, and takes ## Handoff alone")
    sp.add_argument("--fold", metavar="STRAY",
                    help="close an sp-stray-heading: demote `## <STRAY>` to `### <STRAY>` so "
                         "it folds into the canonical section that precedes it, text "
                         "preserved. The ONE path that admits a heading outside the fourteen "
                         "— every other way of naming one still exits 2 — and it takes no "
                         "heading, --moment, --write or --scope beside it")

    sp = add_json(sub.add_parser("verification",
                                 help="read or set ONE spec's verification policy"))
    sp.add_argument("spec")
    # No `choices=`: argparse would refuse a bad value with a usage message on stderr and
    # exit 2 with no JSON, and every caller of this tool is told to branch on the exit code
    # AND the `--json` payload. The check lives in the command, where the refusal carries
    # `sp-bad-verification` and the declared set like every other refusal here.
    sp.add_argument("policy", nargs="?",
                    help="omit to read; one of " + ", ".join(VERIFICATION_POLICIES))

    for field, value_help in (
        ("tags", "omit to read; a comma-separated list to SET (replaces, never appends)"),
        ("assignee", "omit to read; a name or identity to set"),
        ("start", "omit to read; YYYY-MM-DD to set"),
        ("target", "omit to read; YYYY-MM-DD to set"),
        ("summary", "omit to read; ONE line to set — the one-line summary the ranked table prints"),
    ):
        sp = add_json(sub.add_parser(field, help=f"read or set ONE spec's `{field}` — "
                                                 f"stored, never projected"))
        sp.add_argument("spec")
        sp.add_argument("value", nargs="?", help=value_help)
        sp.set_defaults(field=field)

    sp = add_json(sub.add_parser("record", help="read or merge ONE frontmatter record"))
    sp.add_argument("spec")
    sp.add_argument("name", help="one of the declared records")
    sp.add_argument("--set", action="append", metavar="FIELD=VALUE",
                    help="merge one field; repeatable. Fields not named survive, so a "
                         "re-stamp never drops what an earlier pass wrote")

    sp = add_json(sub.add_parser("promote", help="the gated close-out: plans/ → archive/"))
    sp.add_argument("spec")
    sp.add_argument("--to", choices=list(PHASES), help="force the destination phase")
    sp.add_argument("--outcome", choices=list(OUTCOMES),
                    help="archive hop only (default: done)")
    sp.add_argument("--force", action="store_true",
                    help="archive as done despite open tasks")
    sp.add_argument("--dry-run", action="store_true", dest="dry_run")

    sp = add_json(sub.add_parser("task", help="flip or block a checkbox"))
    sp.add_argument("--spec", required=True)
    sp.add_argument("--check")
    sp.add_argument("--uncheck")
    sp.add_argument("--block", help="mark TASK blocked (requires --reason)")
    sp.add_argument("--reason", help="why the task is blocked — written into the line")
    sp.add_argument("--subject", help="the subject of the commit that implements the task, "
                                      "recorded as a `subject:` metadata line "
                                      "(goes with --check)")
    sp.add_argument("--commit", help="the sha of the commit that implements the task, "
                                     "recorded as a `commit:` metadata line — call it AFTER "
                                     "the commit exists (goes with --check; additive to "
                                     "--subject, not a replacement for it)")

    sp = add_json(sub.add_parser("next", help="THE single next action, or --front for the "
                                              "ranked candidate list"))
    sp.add_argument("--spec", help="one spec's next action")
    sp.add_argument("--table", action="store_true",
                    help="with --front: the ranked table `spec-driven.md` §The spec table "
                         "declares, instead of one line per spec. Refuses with --json")
    sp.add_argument("--columns",
                    help="with --table: a comma-separated subset to print. Columns are "
                         "omitted, never reordered (default: all)")
    sp.add_argument("--order", choices=["rank", "priority"], default="rank",
                    help="with --front: `rank` is the four-factor ordering (executing, "
                         "closest to done, priority, age); `priority` is the human's "
                         "ranking alone")
    sp.add_argument("--front", action="store_true",
                    help="rank every active spec: executing, closest to done, priority, age")

    sp = add_json(sub.add_parser("parallel", help="prove a [P] group's files: are disjoint"))
    sp.add_argument("--spec", required=True)

    sp = add_json(sub.add_parser("find", help="resolve a branch, a commit, or a PR back to "
                                              "the spec that owns it"))
    sp.add_argument("--branch", help="an exact `branch.work` value")
    sp.add_argument("--commit", help="a commit sha, resolved to its subject and matched "
                                     "against each task's recorded `subject:`")
    sp.add_argument("--pr", help="a PR number or URL, matched against `pr`/`merge.pr`")

    sp = add_json(sub.add_parser("discover", help="append a line to ## Discoveries"))
    sp.add_argument("spec")
    sp.add_argument("text")

    sp = add_json(sub.add_parser("validate", help="the canonical set, the gates, the sp-* codes"))
    sp.add_argument("--spec", help="one slug (default: every spec)")
    sp.add_argument("--phase", choices=list(PHASES),
                    help="cut the sweep to one phase (default: every phase)")
    sp.add_argument("--by-code", action="store_true", dest="by_code",
                    help="one line per (code, severity) with the count and the specs, "
                         "instead of one line per finding")

    add_json(sub.add_parser("config", help="the workspace's declared parameters, as data"))

    sp = add_json(sub.add_parser("release", help="bump the plugin's seven version-carrying "
                                                  "artifacts and tag the commit — the plugin's "
                                                  "own repository only"))
    sp.add_argument("version", help="the new version, X.Y.Z")

    add_json(sub.add_parser("doctor", help="workspace shape; remedies declared"))

    sp = add_json(sub.add_parser("migrate", help="one-way fold to the current layout "
                                                 "(v1 → v3, and backlog/ + ready/ → plans/)"))
    sp.add_argument("--dry-run", action="store_true", dest="dry_run")

    sp = add_json(sub.add_parser("export", help="dump the canonical markdown to disk — "
                                                "write-only, nothing reads it back"))
    grp = sp.add_mutually_exclusive_group(required=True)
    grp.add_argument("--spec", help="one slug")
    grp.add_argument("--all", action="store_true", help="every spec")
    sp.add_argument("--out", default="specs-export",
                    help="destination directory (default: ./specs-export)")

    return p, sub


DISPATCH: dict = {
    "new": cmd_new,
    "list": cmd_list,
    "status": cmd_status,
    "show": cmd_show,
    "section": cmd_section,
    "verification": cmd_verification,
    "tags": cmd_field,
    "assignee": cmd_field,
    "start": cmd_field,
    "target": cmd_field,
    "summary": cmd_field,
    "record": cmd_record,
    "promote": cmd_promote,
    "task": cmd_task,
    "next": cmd_next,
    "parallel": cmd_parallel,
    "find": cmd_find,
    "discover": cmd_discover,
    "validate": cmd_validate,
    "config": cmd_config,
    "release": cmd_release,
    "doctor": cmd_doctor,
    "migrate": cmd_migrate,
    "export": cmd_export,
}


def _force_utf8_output() -> None:
    """Spec files are prose — em-dashes, arrows, accented words — and a Windows console
    defaults to cp1252, where printing one raises UnicodeEncodeError AFTER the write
    already landed. That turns a successful `task --check` into a traceback and a nonzero
    exit, which the exit-code contract (0 ok / 1 findings / 2 refusal) reads as a finding.
    Encode output as UTF-8 and never let a glyph decide the exit code."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def main(argv: list[str]) -> int:
    _force_utf8_output()
    if "--version" in argv:
        print(f"specs {VERSION}")
        return 0
    parser, _ = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_help()
        return 1
    if not hasattr(args, "json"):
        args.json = False
    root = find_specs_root(args.root)
    # One command, one resolution — held by the emitter's lifetime. It is built here, handed to
    # the verb, and dropped when the call returns, so a process that dispatches more than once
    # cannot let one command's receipt ride out on the next one's payload.
    out = Emitter()
    # The lock is taken HERE and not inside the backend, because the unit it protects is the
    # whole command: every writing subcommand reads a document, edits it and writes it back,
    # and a lock that only spanned the write would let two of them read the same text and each
    # store its own edit over the other's. `finally` and not `atexit`: the lock must be gone by
    # the time the process reports its exit code, so whatever runs next sees a free worktree.
    lock, err = writer_lock(args, root)
    if err:
        return out.emit_err(args.json, err)
    try:
        return DISPATCH[args.cmd](args, root, out)
    except BackendRefusal as e:
        # THE ONE PLACE A TRANSPORT FAILURE BECOMES AN EXIT CODE. An external backend can
        # fail in the middle of a primitive that has no error channel, and the contract is
        # a legible refusal and never a traceback — so the failure is raised where it
        # happens, carrying the message already built, and converted exactly once here.
        return out.emit_err(args.json, e.err)
    finally:
        if lock is not None:
            lock.release()
