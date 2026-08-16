"""`validate` — every finding for the whole workspace, in the `sp-*` vocabulary."""
from __future__ import annotations

import json
import os

from quenching.common.frontmatter import frontmatter_anomalies
from quenching.common.output import exit_for
from quenching.specs.backends import open_backend
from quenching.specs.backends.base import SpecBackend
from quenching.specs.commands.output import Emitter
from quenching.specs.parse import LEGACY_DATED_FILE_RE, PHASES, SPEC_FILE_RE
from quenching.specs.parse.sections import (gate_report, parse_impact_standards, ready_report,
                                            section_state, stray_headings)
from quenching.specs.parse.tasks import _files_bad_annotation
from quenching.specs.schema import (MERGE_ANCHORLESS_STRATEGIES, MERGE_NO_PR_STRATEGIES,
                                    MERGE_STRATEGIES, RECORD_NONE_RE, VERIFICATION_POLICIES,
                                    canonical_headings, load_schema)


def _finding(code: str, severity: str, message: str, **extra) -> dict:
    return {"code": code, "severity": severity, "message": message, **extra}


def validate_spec(backend: SpecBackend, s: dict) -> list[dict]:
    """Every finding for ONE spec file, in the v2 `sp-*` vocabulary.

    The phase-scoped rule is asserted against the schema's per-phase sets — the SAME sets
    `promote` gates on, so the two can never drift into disagreeing about what a phase
    requires.

    ASKED OF THE BACKEND, never of the path — and the derivation is the shared one, so this
    validates the same `frontmatter`/`sections`/`tasks` every other command reads. Against
    GitHub the locator is an issue URL, so `read_text` returned nothing and EVERY spec was
    reported missing every required key: 210 fabricated findings on this repository, from
    documents that were entirely well-formed."""
    where = f"{s['folder']}/{s['file']}"
    info, rerr = backend.read_spec(s["slug"])
    if rerr or info is None:
        # The only refusal reachable here is an ambiguous slug — it came from the listing, so
        # it cannot be unknown — and `cmd_validate` already names it `sp-duplicate-slug`.
        # Deriving from an empty document instead, as `list` does to keep its row, would
        # report a well-formed spec as missing everything: the same fabrication this function
        # exists to stop, just narrowed to the duplicates.
        return []
    text, fm = info["text"], info["frontmatter"]
    sections, tasks = info["sections"], info["tasks"]
    out: list[dict] = []

    # BEFORE the required-key checks, so a parse failure is never presented as a
    # content gap — a value this parser could not represent used to surface as a
    # missing `title`, naming the absence rather than the misread that caused it.
    for a in frontmatter_anomalies(text):
        out.append(_finding("sp-frontmatter-unparsed", "warn",
                            f"{where}: `{a['key']}`: {a['detail']}", spec=s["slug"], path=where,
                            kind=a["kind"], key=a["key"],
                            remedy="quote the value, or write the comment on its own line — "
                                   "see /.knowledge/standards/code/frontmatter-parser.md"))

    schema = load_schema()
    for key in schema.get("frontmatter", {}).get("required", []):
        if not str(fm.get(key, "")).strip():
            out.append(_finding("sp-missing-frontmatter", "error",
                                f"{where}: frontmatter has no `{key}`", spec=s["slug"],
                                path=where, remedy=f"add `{key}:` to the frontmatter"))
    if fm.get("slug") and fm["slug"] != s["slug"]:
        out.append(_finding("sp-slug-mismatch", "error",
                            f"{where}: frontmatter slug `{fm['slug']}` disagrees with the "
                            f"basename `{s['slug']}`", spec=s["slug"], path=where,
                            remedy="make the frontmatter slug match the basename"))
    pol = str(fm.get("verification", "")).strip().lower()
    if pol and pol not in VERIFICATION_POLICIES:
        out.append(_finding("sp-bad-verification", "error",
                            f"{where}: verification `{pol}` is not one of "
                            f"{', '.join(VERIFICATION_POLICIES)}", spec=s["slug"], path=where,
                            remedy=f"set verification to one of {', '.join(VERIFICATION_POLICIES)}"))
    priority = fm.get("priority")
    if isinstance(priority, dict):
        levels = (schema.get("frontmatter", {}).get("records", {}).get("priority", {})
                  .get("complexity", {}).get("levels", []))
        comp = str(priority.get("complexity", "")).strip().lower()
        if comp and levels and comp not in levels:
            out.append(_finding("sp-bad-complexity", "warn",
                                f"{where}: priority.complexity `{comp}` is not one of "
                                f"{', '.join(levels)}", spec=s["slug"], path=where,
                                remedy=f"set priority.complexity to one of {', '.join(levels)}"))

    for h in stray_headings(sections, schema):
        out.append(_finding("sp-stray-heading", "warn",
                            f"{where}: `## {h}` is not one of the fourteen canonical headings",
                            spec=s["slug"], path=where, heading=h,
                            remedy="rename it to a canonical heading or fold it into one"))

    # The phase-scoped rule governs whether a heading must be PRESENT — so `missing` is
    # checked only against the gate of the phase this spec is IN.
    gates = gate_report({"sections": sections}, s["phase"], schema)
    for h in gates["missing"]:
        out.append(_finding("sp-gate-unmet", "warn",
                            f"{where}: `## {h}` is required in {s['phase']}/ and is absent",
                            spec=s["slug"], path=where, heading=h,
                            remedy=f"cq specs section {s['slug']} \"{h}\" --write"))
    # Malformed is NOT phase-scoped. Once a heading exists it must say something, in any
    # phase: it is neither an answer nor a not-yet, and leaving it for the promote to catch
    # means a spec looks fine right up until the gate refuses it.
    for h in canonical_headings(schema):
        if section_state(sections, h) == "empty":
            out.append(_finding("sp-empty-section", "error",
                                f"{where}: `## {h}` is present but empty — neither an answer "
                                f"nor a not-yet", spec=s["slug"], path=where, heading=h,
                                remedy="fill it, or write `- none — <reason>`"))
    # `Handoff` used to be warned on by the ready/ FOLDER. With one folder the same
    # question is asked of the derived ready gate: a spec nobody could build yet is not
    # missing an executor's context, and a spec that is buildable is.
    ready = ready_report({"sections": sections}, schema) if s["phase"] == "plans" else None
    if ready and ready["ok"]:
        for h in ready["warn"]:
            if h == "Overview":
                out.append(_finding("sp-overview-missing", "warn",
                                    f"{where}: `## Overview` is empty in a spec that meets "
                                    f"the ready gate — a reader gets no orientation",
                                    spec=s["slug"], path=where, heading=h,
                                    remedy=f"cq specs section {s['slug']} \"Overview\" --write, "
                                           "written last once the other sections settle"))
            else:
                out.append(_finding("sp-handoff-empty", "warn",
                                    f"{where}: `## {h}` is empty in a spec that meets the ready "
                                    f"gate — an executor gets no context", spec=s["slug"],
                                    path=where, heading=h,
                                    remedy="rewrite it after each committed task"))

    declared = parse_impact_standards(text, schema)
    if declared:
        named = "\n".join(t["text"] for t in tasks)
        for p in declared:
            if p not in named:
                out.append(_finding("sp-impact-uncovered", "warn",
                                    f"{where}: `{p}` is declared under ## Impact but no task "
                                    f"names it", spec=s["slug"], path=where, standard=p,
                                    remedy="add a task that writes it, or drop the declaration"))

    # A `files:` entry carrying a parenthetical that is not the reserved `(new)` is a
    # human comment the parser must not interpret — kept whole it would reach an
    # executor as a path that exists nowhere, which is the exact silence `_split_files`
    # exists to stop. Refuse it at the points that hand paths out and report it here.
    for t in tasks:
        for entry in t["files"]:
            note = _files_bad_annotation(entry)
            if note:
                out.append(_finding("sp-files-annotation", "error",
                                    f"{where}: task {t['id'] or t['index']} declares files "
                                    f"entry {entry!r} with annotation `({note})` — only "
                                    f"`(new)` is reserved", spec=s["slug"], path=where,
                                    task=t["id"] or t["index"], entry=entry,
                                    remedy="remove the comment — `(new)` is the only "
                                           "reserved `files:` annotation"))

    # Judged against the READY gate: a spec is "unrefined" once it could be built, not the
    # moment it is captured. Warning on every fresh capture would train the reader to
    # ignore the code.
    if ready and ready["ok"] and not fm.get("refined"):
        out.append(_finding("sp-unrefined", "warn",
                            f"{where}: ready to build, but nobody has interrogated it",
                            spec=s["slug"], path=where,
                            remedy="run a refinement pass, or build as-is (never gated)"))
    if s["phase"] == "archive" and not fm.get("outcome"):
        out.append(_finding("sp-no-outcome", "warn",
                            f"{where}: archived with no `outcome:` — done and abandoned "
                            f"read alike", spec=s["slug"], path=where,
                            remedy="stamp `outcome: done` or `outcome: abandoned`"))
    merge_finding = merge_record_finding(fm, where, s["slug"])
    if merge_finding:
        out.append(merge_finding)
    return out


def merge_record_finding(fm: dict, where: str, slug: str) -> dict | None:
    """Whether a `merge:` record still says which commit carries the merge.

    TWO forms are legal and both are read forever: the current `{strategy, subject}`, and
    `{strategy, commit}` on a spec archived before the anchor became the subject. The older
    one is never rewritten — a recorded sha describes a commit that exists, and editing an
    archived spec to "fix" it would be a lie about when the record was made."""
    rec = fm.get("merge")
    if not rec:
        return None
    remedy = ("stamp `merge: {strategy: <one of " + ", ".join(MERGE_STRATEGIES) +
              ">, subject: <the merge commit's subject>}`")
    if not isinstance(rec, dict):
        return _finding("sp-bad-merge", "warn",
                        f"{where}: `merge:` is not a {{strategy, subject}} record",
                        spec=slug, path=where, remedy=remedy)
    strategy = str(rec.get("strategy", "")).strip().lower()
    subject = str(rec.get("subject", "")).strip()
    if strategy not in MERGE_STRATEGIES:
        return _finding("sp-bad-merge", "warn",
                        f"{where}: merge strategy `{strategy or '(unset)'}` is not one of "
                        f"{', '.join(MERGE_STRATEGIES)}", spec=slug, path=where,
                        remedy=remedy)
    if not subject:
        if str(rec.get("commit", "")).strip():
            return None          # the older form, read and left exactly as it was written
        return _finding("sp-bad-merge", "warn",
                        f"{where}: `merge:` names a strategy but nothing to resolve the "
                        f"merge by", spec=slug, path=where, remedy=remedy)
    anchorless = strategy in MERGE_ANCHORLESS_STRATEGIES
    explicit_none = bool(RECORD_NONE_RE.match(subject))
    if anchorless and not explicit_none:
        return _finding("sp-bad-merge", "warn",
                        f"{where}: `{strategy}` creates no merge commit, so `subject:` has "
                        f"nothing to point at", spec=slug, path=where,
                        remedy="write `subject: none — <why>`")
    if not anchorless and explicit_none:
        return _finding("sp-bad-merge", "warn",
                        f"{where}: `{strategy}` creates a merge commit, so `subject:` must "
                        f"name it rather than be an explicit none", spec=slug, path=where,
                        remedy=remedy)
    if str(rec.get("pr", "")).strip() and strategy in MERGE_NO_PR_STRATEGIES:
        return _finding("sp-bad-merge", "warn",
                        f"{where}: `pr:` is set but `{strategy}` has no `gh pr merge` "
                        f"equivalent — the PR route is never offered under it",
                        spec=slug, path=where, remedy="drop `pr:`, or record a strategy "
                        f"`gh pr merge` supports ({', '.join(s for s in MERGE_STRATEGIES if s not in MERGE_NO_PR_STRATEGIES)})")
    return None


def cmd_validate(args, root: str, out: Emitter) -> int:
    backend, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    specs = backend.list_specs()
    phase = getattr(args, "phase", None)
    if phase:
        specs = [s for s in specs if s["phase"] == phase]
    findings: list[dict] = []

    seen: dict[str, list[str]] = {}
    for s in specs:
        seen.setdefault(s["slug"], []).append(f"{s['phase']}/{s['file']}")
    for slug, paths in seen.items():
        if len(paths) > 1:
            findings.append(_finding("sp-duplicate-slug", "error",
                                     f"slug `{slug}` resolves to {len(paths)} files: "
                                     f"{', '.join(paths)}", spec=slug,
                                     remedy="rename one — a slug is an identity, and two "
                                            "matches makes every command refuse"))

    for ph in ([phase] if phase else PHASES):
        d = os.path.join(root, ph)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name == "index.md" or name.startswith("."):
                continue
            if os.path.isdir(os.path.join(d, name)):
                # archive/ is DELIBERATELY not migrated — it is historical and read-only, so
                # its v1 `YYYY-MM-DD-<name>/` plan folders are expected, not strays. Flagging
                # them would push a reader to migrate the one tree the design protects.
                if ph == "archive":
                    continue
                findings.append(_finding("sp-stray-dir", "warn",
                                         f"{ph}/{name}/ is a directory — v2 specs are files",
                                         path=f"{ph}/{name}",
                                         remedy="a v1 plan folder? run `cq specs migrate`"))
            elif not SPEC_FILE_RE.match(name):
                dated = LEGACY_DATED_FILE_RE.match(name)
                findings.append(_finding("sp-bad-filename", "error",
                                         f"{ph}/{name} is not `<slug>.md`",
                                         path=f"{ph}/{name}",
                                         remedy="run `cq specs migrate` — the date belongs in "
                                                "`date:` now, not in the basename"
                                         if dated else
                                         "rename it to the one filename pattern all "
                                         "three folders share"))

    target = [s for s in specs if s["slug"] == args.spec] if args.spec else specs
    if args.spec and not target:
        out.emit(args.json, {"ok": False, "code": "sp-unknown-slug", "slug": args.spec,
                             "message": f"no spec with slug '{args.spec}'"},
                 f"error: no spec with slug '{args.spec}'")
        return 1
    for s in target:
        findings.extend(validate_spec(backend, s))

    errors = [f for f in findings if f["severity"] == "error"]
    if args.json:
        print(json.dumps({"ok": not errors, "root": root, "specs": len(specs),
                          "findings": findings}, indent=2, ensure_ascii=False))
    else:
        print(f"specs validate — {root} ({len(errors)} error(s), "
              f"{len(findings) - len(errors)} warning(s))")
        for f in findings:
            print(f"  [{f['severity']:<5}] {f['message']}  ({f['code']})")
            if f.get("remedy"):
                print(f"          remedy: {f['remedy']}")
        if not findings:
            print("  OK — every spec conforms.")
    # Errors fail; warnings are reported. This line read `1 if findings else 0` for as long as the
    # verb existed, which contradicted the `"ok": not errors` two lines above it — a warn-only run
    # printed `"ok": true` and exited 1 — and contradicted `components lint`, `components doctor`
    # and `common.output.exit_for`, all three of which count `severity == "error"` alone. Fifteen
    # warn codes reach here (`sp-unrefined`, `sp-no-outcome`, `sp-impact-uncovered`, the six
    # `sp-bad-merge` arms among them), so any conductor gating on this exit code failed on advice.
    # `exit_for` rather than a fourth copy of the predicate: the rule is one, so its implementation
    # is one.
    return exit_for(findings)
