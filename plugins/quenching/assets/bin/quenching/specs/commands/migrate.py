"""`migrate` — the one-way folds to the current layout.

  v1 -> v3   a three-file plan folder (or a v1 backlog task) becomes one spec file
  v2 -> v3   `backlog/` and `ready/` move into `plans/`
  markers    a spec an external tracker still stores under a dated basename

`/.specs/archive/**` is NEVER touched. `_v1_leftovers` sits here, with the fold that clears it,
and is read by `doctor` to name the workspace this command exists to convert."""
from __future__ import annotations

import datetime
import json
import os
import re

from quenching.common.dates import today
from quenching.common.frontmatter import parse_frontmatter
from quenching.common.git import _git
from quenching.common.io import read_text, write_text
from quenching.common.text import slugify
from quenching.specs.backends import open_backend
from quenching.specs.backends.hybrid import (GH_PART_MAX, hybrid_join, hybrid_project,
                                             hybrid_split, hybrid_title_join,
                                             hybrid_title_split)
from quenching.specs.commands.output import Emitter
from quenching.specs.parse import LEGACY_DATED_FILE_RE, SPEC_FILE_RE, titleize
from quenching.specs.parse.derive import _policy
from quenching.specs.parse.fields import legacy_marker_fold, set_frontmatter_key
from quenching.specs.parse.sections import parse_sections, ready_gate
from quenching.specs.parse.spec import LEGACY_PHASES, PHASE_DIRS
from quenching.specs.parse.text import body_after_frontmatter, has_real_content, strip_comments
from quenching.specs.schema import DEFAULT_VERIFICATION, canonical_headings, phase_spec


# Where each v1 artifact's sections land. `## Context` and `## Decisions` merge into the
# single `## Design`; everything else is a rename. The v1 heading is matched
# case-insensitively and its body is carried VERBATIM — a migration must not rewrite prose
# it does not understand.
V1_MAP = {
    "proposal.md": [("Why", "Problem"), ("What Changes", "Proposal"),
                    ("Out of Scope", "Out of Scope"), ("Validation", "Validation"),
                    ("Impact", "Impact")],
    "design.md": [("Context", "Design"), ("Decisions", "Design"),
                  ("Alternatives Considered", "Alternatives Considered"),
                  ("Open Decisions", "Open Decisions"), ("Risks", "Risks")],
}
MIGRATE_NONE = "- none — not recorded in the v1 plan"


def _git_first_commit_date(path: str) -> str | None:
    """The path's first commit date — used only when `.specs.json` has no `created`.

    A birth date is never INVENTED: this walks git history for the real one, and the caller
    falls back to the file's mtime rather than to today."""
    out = _git(os.path.dirname(os.path.abspath(path)),
               "log", "--diff-filter=A", "--follow", "--format=%ad", "--date=short",
               "--", path)
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    return lines[-1] if lines else None


def _birth_date(meta: dict, path: str) -> str:
    created = str(meta.get("created", "") or "")
    if re.match(r"^\d{4}-\d{2}-\d{2}", created):
        return created[:10]
    git = _git_first_commit_date(path)
    if git:
        return git
    try:
        return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()
    except OSError:
        return today()


def _v1_sections(plan_dir: str) -> dict[str, list[str]]:
    """Collect v1 bodies keyed by their V2 heading, in canonical order."""
    collected: dict[str, list[str]] = {}
    for fname, pairs in V1_MAP.items():
        text = read_text(os.path.join(plan_dir, fname))
        if text is None:
            continue
        secs = parse_sections(body_after_frontmatter(text))
        lower = {k.lower(): v for k, v in secs.items()}
        for v1h, v2h in pairs:
            sec = lower.get(v1h.lower())
            if sec and sec["filled"]:
                body = sec["body"].strip()
                # `## Context` and `## Decisions` both land in `## Design`
                collected.setdefault(v2h, []).append(
                    f"### {v1h}\n\n{body}" if v2h == "Design" else body)
    tasks_text = read_text(os.path.join(plan_dir, "tasks.md"))
    if tasks_text is not None:
        body = body_after_frontmatter(tasks_text)
        body = re.sub(r"(?m)^#\s+.*$", "", body, count=1)     # drop the `# Tasks — X` title
        # v1 grouped tasks under `## N.`; v2 nests them under the `## Tasks` section
        body = re.sub(r"(?m)^## ", "### ", body)
        if has_real_content(body):
            collected["Tasks"] = [body.strip()]
    return collected


def _migrate_plan(root: str, name: str, dry: bool) -> dict:
    plan_dir = os.path.join(root, name)
    meta_txt = read_text(os.path.join(plan_dir, ".specs.json")) or "{}"
    try:
        meta = json.loads(meta_txt)
    except json.JSONDecodeError:
        meta = {}
    # A v1 folder was normally a bare name, but some carried a `YYYY-MM-DD-` prefix. Left
    # in, that prefix ends up INSIDE the slug and the date is then prepended again, so the
    # fold emits `2026-01-05-2026-01-05-thing.md` with a date buried in its identity key.
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)$", name)
    slug = slugify(m.group(2) if m else name)
    date = m.group(1) if m else _birth_date(meta, os.path.join(plan_dir, ".specs.json"))
    collected = _v1_sections(plan_dir)
    # v1 sorted a plan by whether it had tasks; v3 has one folder, so what that sorting
    # decided is now a derived stage. The gate a v1 plan must still satisfy is the ready
    # set when it carried tasks (it was buildable) and plans/'s own entry gate otherwise.
    dest_phase = "plans"
    gate = (ready_gate()["sections"] if collected.get("Tasks")
            else phase_spec(dest_phase).get("entryGate", []))

    fm = [f"slug: {slug}", f"title: {meta.get('title') or titleize(slug)}",
          f"date: {date}", f"verification: {_policy(meta)}"]
    if isinstance(meta.get("refined"), dict) and meta["refined"].get("mode"):
        r = meta["refined"]
        fm.append(f"refined: {{mode: {r.get('mode')}, date: {r.get('date', date)}}}")

    parts = ["---", *fm, "---", "", f"# {meta.get('title') or titleize(slug)}", ""]
    for h in canonical_headings():
        if h in collected:
            parts += [f"## {h}", "", "\n\n".join(collected[h]), ""]
        elif h in gate:
            # the destination's gate must be satisfiable, and an explicit none that SAYS
            # the v1 plan never recorded it is a fact — not an invented answer
            parts += [f"## {h}", "", MIGRATE_NONE, ""]
    body = "\n".join(parts).rstrip() + "\n"

    strays = sorted(f for f in os.listdir(plan_dir)
                    if f not in (".specs.json", "proposal.md", "design.md", "tasks.md")
                    and os.path.isfile(os.path.join(plan_dir, f)))
    dest = os.path.join(root, dest_phase, f"{slug}.md")
    rec = {"from": f"{name}/", "slug": slug, "to": f"{dest_phase}/{slug}.md",
           "date": date, "dateSource": "created" if meta.get("created") else "git/mtime",
           "sections": sorted(collected), "strays": strays}
    if dry:
        return rec
    os.makedirs(os.path.join(root, dest_phase), exist_ok=True)
    write_text(dest, body)
    for f in (".specs.json", "proposal.md", "design.md", "tasks.md"):
        p = os.path.join(plan_dir, f)
        if os.path.isfile(p):
            os.remove(p)
    if not strays:
        try:
            os.rmdir(plan_dir)
        except OSError:
            rec["kept"] = True
    else:
        rec["kept"] = True          # never delete a folder still holding a human's file
    return rec


def _migrate_task(root: str, path: str, dry: bool) -> dict:
    text = read_text(path) or ""
    fm = parse_frontmatter(text)
    slug = slugify(os.path.splitext(os.path.basename(path))[0])
    stamp = str(fm.get("timestamp", ""))
    date = stamp[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", stamp) else _birth_date({}, path)
    body = strip_comments(body_after_frontmatter(text)).strip()
    body = re.sub(r"(?m)^#\s+.*$", "", body, count=1).strip()
    problem = fm.get("description") or body or titleize(slug)
    extra = [f"{k}: {fm[k]}" for k in ("priority", "tags", "complexity") if fm.get(k)]
    if extra:
        problem += f"\n\n_(v1 backlog task — {' · '.join(extra)})_"
    if body and fm.get("description") and body not in problem:
        problem += f"\n\n{body}"
    out = ["---", f"slug: {slug}", f"title: {fm.get('title') or titleize(slug)}",
           f"date: {date}", f"verification: {DEFAULT_VERIFICATION}", "---", "",
           f"# {fm.get('title') or titleize(slug)}", "", "## Problem", "", problem, ""]
    dest = os.path.join(root, "plans", f"{slug}.md")
    rec = {"from": f"backlog/{os.path.basename(path)}", "slug": slug,
           "to": f"plans/{slug}.md", "date": date, "kind": "task"}
    if dry:
        return rec
    os.makedirs(os.path.join(root, "plans"), exist_ok=True)
    write_text(dest, "\n".join(out).rstrip() + "\n")
    os.remove(path)
    return rec


def _v2_leftovers(root: str) -> list[dict]:
    """Every spec file still sitting in a v2 folder, in scan order.

    It used to be a pure FILE MOVE — v2 and v3 spec files were the same format and only the
    folder had changed, so the file was never opened, never reformatted and never renamed.
    That stopped being true when the capture date left the basename: a v2 file is named
    `YYYY-MM-DD-<slug>.md` and carries no `date:`, which is a format difference and not a
    location one. So BOTH names are collected here, and `_migrate_v2_file` moves the already
    conformant one untouched and rewrites the dated one."""
    out = []
    for folder in LEGACY_PHASES:
        d = os.path.join(root, folder)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not os.path.isfile(os.path.join(d, name)):
                continue
            if SPEC_FILE_RE.match(name) or LEGACY_DATED_FILE_RE.match(name):
                out.append({"folder": folder, "file": name,
                            "path": os.path.join(d, name)})
    return out


def _migrate_v2_file(root: str, item: dict, dry: bool) -> dict:
    """Move one v2 spec file into `plans/`, renaming it only if it still carries a date.

    A file already named `<slug>.md` is moved and NOT opened — the lossless case the v2 fold
    was written for, and the one that still works on a file this tool could not parse. A
    `YYYY-MM-DD-<slug>.md` one is the format change: the date is the only copy of a fact the
    basename is about to stop holding, so it is written into the frontmatter as `date:`
    BEFORE the rename, and never dropped on the floor."""
    dest_dir = os.path.join(root, "plans")
    legacy = LEGACY_DATED_FILE_RE.match(item["file"])
    slug = legacy.group(2) if legacy else SPEC_FILE_RE.match(item["file"]).group(1)
    name = f"{slug}.md" if legacy else item["file"]
    rec = {"from": f"{item['folder']}/{item['file']}", "slug": slug,
           "to": f"plans/{name}", "kind": "v2-file"}
    if legacy:
        rec["date"] = legacy.group(1)
    if dry:
        return rec
    os.makedirs(dest_dir, exist_ok=True)
    if legacy:
        text = read_text(item["path"]) or ""
        # Only when it has none of its own: a v2 file that somebody already gave a `date:`
        # has a human's answer in it, and the basename is the derived copy, not the source.
        if not str(parse_frontmatter(text).get("date", "")).strip():
            write_text(item["path"], set_frontmatter_key(text, "date", legacy.group(1)))
    os.rename(item["path"], os.path.join(dest_dir, name))
    return rec


def _migrate_markers(backend, dry: bool) -> list[dict]:
    """Fold every spec an external backend still stores under a dated basename.

    ONE WRITE PER SPEC, and the document that goes out has already been proved: the fold is
    `legacy_marker_fold` — the same pure function `selftest` exercises — and the write is
    `write_spec`, the same path every other command uses. Nothing here has a serialisation of
    its own, because a migration with its own writer is a second implementation that only
    ever runs once, on the day it matters most.

    `--dry-run` performs the WHOLE fold offline and compares byte for byte, so the answer to
    "will this lose anything" is measured against the real corpus rather than argued."""
    out: list[dict] = []
    for number, filename, head, parts, _title in backend.legacy_rows():
        text = head if parts <= 1 else backend._joined(number, head, parts)
        folded = legacy_marker_fold(filename, text)
        if folded is None:
            continue
        name, new_text = folded
        slug = SPEC_FILE_RE.match(name).group(1)
        # What the store WILL hold, and what a read WILL rebuild from it — run here, before
        # anything is sent, so a document that would not survive is reported and skipped
        # rather than written and lost.
        body, native = hybrid_project(slug, new_text)
        chunks = hybrid_split(body, GH_PART_MAX)
        rebuilt = hybrid_title_join(hybrid_join(
            [(chunks[0][0].replace("\r\n", "\n"), False)]
            + [(c.replace("\r\n", "\n"), eol) for c, eol in chunks[1:]]), native)
        rec = {"issue": number, "from": filename, "to": name, "slug": slug,
               "date": str(parse_frontmatter(new_text).get("date", "")),
               "parts": len(chunks), "projectedTitle": hybrid_title_split(new_text) is not None,
               "roundTrip": rebuilt == new_text}
        if not rec["roundTrip"]:
            rec["skipped"] = "the document would not come back byte for byte"
            out.append(rec)
            continue
        if not dry:
            # The number came from this scan, so no lookup and no re-listing between writes.
            backend._store(number, slug, name, new_text, parts)
        out.append(rec)
    return out


def cmd_migrate(args, root: str, out: Emitter) -> int:
    """One-way, to the CURRENT layout. `/.specs/archive/**` is NEVER touched — it is
    historical and read-only, and churning it would break every link into it for no gain.

    Two folds, either of which may apply:
      v1 -> v3   a three-file plan folder (or a v1 backlog task) becomes one spec file
      v2 -> v3   `backlog/` and `ready/` move into `plans/`, basenames unchanged

    The v2 fold moves files and nothing else: same format, same name, only the folder
    changed. Refuses (exit 2) when neither fold applies, so a second run cannot quietly
    re-migrate an already-converted workspace."""
    plans = _v1_leftovers(root)
    tasks = []
    bdir = os.path.join(root, "backlog")
    if os.path.isdir(bdir):
        for name in sorted(os.listdir(bdir)):
            p = os.path.join(bdir, name)
            # A conformant spec file in `backlog/` — under EITHER name — is the v2 fold's,
            # not the v1 task fold's. Matching only the current name would hand every dated
            # v2 file to the task fold, which rewrites it into a `## Problem` stub.
            if (name == "index.md" or not os.path.isfile(p)
                    or SPEC_FILE_RE.match(name) or LEGACY_DATED_FILE_RE.match(name)):
                continue
            if str(parse_frontmatter(read_text(p) or "").get("type", "")) == "task":
                tasks.append(p)
    v2 = _v2_leftovers(root)

    # The external fold: specs an issue tracker still holds under the dated basename. It is
    # asked of the backend, not of the filesystem, and it is the only fold that can apply to a
    # repo with no `/.specs/` folder at all.
    markers: list[dict] = []
    backend, berr = open_backend(root)
    if not berr and backend is not None and hasattr(backend, "legacy_rows"):
        markers = _migrate_markers(backend, args.dry_run)
        if markers:
            broken = [r for r in markers if not r["roundTrip"]]
            out.emit(args.json,
                     {"ok": not broken, "root": root, "dryRun": bool(args.dry_run),
                      "kind": "markers", "count": len(markers),
                      "projected": sum(1 for r in markers if r["projectedTitle"]),
                      "spilled": sum(1 for r in markers if r["parts"] > 1),
                      "skipped": broken, "specs": markers},
                     f"{'would fold' if args.dry_run else 'folded'} {len(markers)} spec(s) out of "
                     f"the dated basename" + (f" — {len(broken)} SKIPPED, see --json" if broken
                                              else ", all byte-for-byte"))
            return 1 if broken else 0

    if not plans and not tasks and not v2:
        out.emit(args.json, {"ok": False, "code": "sp-nothing-to-migrate", "root": root,
                             "message": "no v1 plan folders, no v1 backlog tasks, no specs in "
                                        "backlog/ or ready/ and no dated markers — this workspace "
                                        "is already current"},
                 "refused: nothing to migrate — this workspace is already current")
        return 2

    # A name collision is the one way this could destroy work, so it is checked for the
    # WHOLE set before a single file moves — a partial migration is worse than none.
    dest_dir = os.path.join(root, "plans")
    clashes = []
    seen: dict[str, str] = {}
    for it in v2:
        if os.path.exists(os.path.join(dest_dir, it["file"])):
            clashes.append(f"{it['folder']}/{it['file']} — plans/{it['file']} already exists")
        if it["file"] in seen:
            clashes.append(f"{it['folder']}/{it['file']} — same basename as "
                           f"{seen[it['file']]}/{it['file']}")
        seen[it["file"]] = it["folder"]
    if clashes:
        out.emit(args.json,
                 {"ok": False, "code": "sp-migrate-collision", "root": root,
                  "collisions": clashes,
                  "message": f"{len(clashes)} destination collision(s) — nothing moved"},
                 f"refused: {len(clashes)} destination collision(s) — nothing moved\n" +
                 "\n".join(f"  {c}" for c in clashes))
        return 2

    migrated = [_migrate_plan(root, n, args.dry_run) for n in plans]
    migrated += [_migrate_task(root, p, args.dry_run) for p in tasks]
    migrated += [_migrate_v2_file(root, it, args.dry_run) for it in v2]

    # An emptied v2 folder is removed; one still holding anything (a customized index.md,
    # a human's stray note) is KEPT and named, never deleted on a guess.
    kept_dirs = []
    if not args.dry_run:
        for folder in LEGACY_PHASES:
            d = os.path.join(root, folder)
            if not os.path.isdir(d):
                continue
            try:
                os.rmdir(d)
            except OSError:
                kept_dirs.append(f"{folder}/ ({', '.join(sorted(os.listdir(d))[:4])})")

    obj = {"ok": True, "dryRun": bool(args.dry_run), "root": root,
           "migrated": migrated,
           "archiveUntouched": True,
           "keptFolders": kept_dirs,
           "kept": [m["from"] for m in migrated if m.get("kept")]}
    if args.json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    else:
        verb = "would migrate" if args.dry_run else "migrated"
        print(f"{verb} {len(migrated)} item(s) — `/.specs/archive/**` untouched")
        for m in migrated:
            src = m.get("dateSource")
            print(f"  {m['from']:<40} → {m['to']}" +
                  (f"   (date from {src})" if src else ""))
            if m.get("strays"):
                print(f"      kept, still holds: {', '.join(m['strays'])}")
        for k in kept_dirs:
            print(f"  kept (not empty): {k}")
    return 0


def _v1_leftovers(root: str) -> list[str]:
    """A v1 plan folder is a directory at the specs root holding proposal/tasks/.specs.json.

    Detecting it matters more than it looks: v2 `list` globs the three phase folders, so an
    unmigrated v1 workspace reads as EMPTY rather than as wrong-format, and a skill would
    conclude there is no work when there is."""
    out = []
    if not os.path.isdir(root):
        return out
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if not os.path.isdir(d) or name in PHASE_DIRS or name.startswith("."):
            continue
        if any(os.path.isfile(os.path.join(d, f))
               for f in (".specs.json", "proposal.md", "tasks.md")):
            out.append(name)
    return out
