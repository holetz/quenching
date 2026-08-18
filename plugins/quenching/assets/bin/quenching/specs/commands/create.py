"""`new` — capture a spec into `plans/` in ONE call: frontmatter, `summary`, `tags`,
`priority.complexity` and N sections, all spliced into the body IN MEMORY before the single
`backend.create_spec`."""
from __future__ import annotations

import json
import sys

from quenching.common.dates import today
from quenching.common.text import slugify
from quenching.specs.backends import open_backend
from quenching.specs.commands.fields import record_field_value_error
from quenching.specs.commands.output import Emitter, display_locator
from quenching.specs.config import (azure_workitemtype_retirement, load_config,
                                    resolve_subject, resolve_type_key)
from quenching.specs.parse import derive_info, titleize
from quenching.specs.parse.edit import split_section_stream, upsert_section
from quenching.specs.parse.fields import set_frontmatter_key, set_frontmatter_record
from quenching.specs.parse.spec import SLUG_RE
from quenching.specs.schema import (DEFAULT_VERIFICATION, canonical_headings, capture_form,
                                    load_schema, section_guidance)


def _tags_repr(tags: list[str]) -> str:
    return "[" + ", ".join(json.dumps(t, ensure_ascii=False) for t in tags) + "]"


def cmd_new(args, root: str, out: Emitter) -> int:
    """Scaffold `plans/<slug>.md`, carrying whatever the capture supplies — `## Problem`
    alone by default, or every flag and section a caller hands in.

    THE DATE IS STAMPED HERE AND NEVER AGAIN, now into the frontmatter's `date:` rather than
    into the basename. `promote` moves the file without renaming it, so the basename — the
    bare slug — is the spec's identity for its whole lifecycle, and the date is a fact the
    document carries instead of a fact its name encodes.

    EVERY REFUSAL IS SETTLED BEFORE THE ONE `create_spec`, exactly as `cmd_section`'s stream
    write already does: `--complexity` is validated and the stdin stream is decomposed and
    checked before a single byte of the document is assembled, so a rejected capture leaves
    no orphaned issue behind on a backend like `github` that has no local undo.

    `sp-write-set-mismatch` does not apply here: unlike `section --write`, `new` declares no
    heading set on the command line — the stream IS the declaration, so a stream that never
    opens on a canonical heading has no single implied heading to fall back on and refuses
    instead."""
    slug = slugify(args.name)
    if not SLUG_RE.match(slug):
        out.emit(args.json, {"ok": False, "code": "sp-bad-slug", "slug": args.name,
                             "message": f"'{args.name}' does not reduce to a kebab-case slug"},
                 f"error: '{args.name}' does not reduce to a kebab-case slug")
        return 2
    backend, err = open_backend(root)
    if err:
        return out.emit_err(args.json, err)
    # Asked of the backend, not of the filesystem: a slug already taken in GitHub must
    # refuse here exactly as one already taken on disk does.
    matches = [s for s in backend.list_specs() if s["slug"] == slug]
    if matches:
        m = matches[0]
        out.emit(args.json,
                 {"ok": False, "code": "sp-slug-exists", "slug": slug,
                  "existing": f"{m['folder']}/{m['file']}",
                  "message": f"slug '{slug}' already exists at {m['folder']}/{m['file']}"},
                 f"refused: slug '{slug}' already exists at {m['folder']}/{m['file']}")
        return 2
    cfg = load_config(root)
    subject, serr = resolve_subject(cfg, args.subject)
    if serr:
        return out.emit_err(args.json, serr)
    type_key, terr = resolve_type_key(cfg, args.type)
    if terr:
        return out.emit_err(args.json, terr)
    if cfg["backend"] == "azure-boards":
        retirement = azure_workitemtype_retirement(cfg, type_key)
        if retirement and retirement["severity"] == "error":
            return out.emit_err(args.json, retirement)
        if retirement:
            print(f"note: {retirement['message']}", file=sys.stderr)

    schema = load_schema()

    # `--complexity` — validated against the SAME per-field rule `cq specs record` enforces,
    # so a bad level refuses with `sp-bad-complexity` before anything is written.
    complexity_record = None
    if args.complexity:
        rspec = schema.get("frontmatter", {}).get("records", {}).get("priority", {})
        rerr = record_field_value_error(rspec, "complexity", args.complexity)
        if rerr:
            out.emit(args.json,
                     {"ok": False, "code": "sp-bad-complexity", "given": args.complexity,
                      "levels": rspec.get("complexity", {}).get("levels", []),
                      "message": rerr}, f"refused: {rerr}")
            return 2
        complexity_record = {"complexity": args.complexity}

    # The stdin stream — read once, decomposed and checked before the document exists at all.
    content = sys.stdin.read() if not sys.stdin.isatty() else ""
    blocks: list[tuple[str | None, str]] = []
    if content.strip():
        blocks = split_section_stream(content, canonical_headings(schema))
        if not blocks:
            msg = ("stdin does not open on a canonical `## <Heading>` line — the stream IS "
                   "the declaration for `cq specs new`, with no single implied heading to "
                   "fall back on the way `section --write` falls back on the one it was given")
            out.emit(args.json,
                     {"ok": False, "code": "sp-stray-heading", "source": "stream",
                      "canonical": canonical_headings(schema), "message": msg},
                     f"error: {msg}")
            return 2
        unresolved = [i for i, (h, _) in enumerate(blocks, 1) if h is None]
        if unresolved:
            out.emit(args.json,
                     {"ok": False, "code": "sp-stray-heading", "source": "stream",
                      "unresolvedBlocks": unresolved, "canonical": canonical_headings(schema),
                      "message": "the stream carries a `## ` heading that is not one of the "
                                 "fourteen canonical ones, at block(s) "
                                 f"{', '.join(str(i) for i in unresolved)}"},
                     f"error: non-canonical `## ` heading at stream block(s) "
                     f"{', '.join(str(i) for i in unresolved)}")
            return 2
        carried = [h for h, _ in blocks]
        if len(set(carried)) != len(carried):
            out.emit(args.json,
                     {"ok": False, "code": "sp-write-duplicate-heading", "stream": carried,
                      "message": "the stream carries the same heading twice — which body "
                                 "wins is not derivable"},
                     "error: the stream carries the same heading twice")
            return 2

    policy = args.verification or DEFAULT_VERIFICATION
    title = args.title or titleize(slug)
    name = f"{slug}.md"
    body = (capture_form(schema=schema)
            .replace("<SLUG>", slug)
            .replace("<TITLE>", title)
            .replace("<DATE>", today())
            .replace("<VERIFICATION>", policy))
    # The subject's fixed tags go into the CANONICAL DOCUMENT, never applied to the tracker
    # directly: `tags:` is a recognised frontmatter key, so `create_spec` reads them off this
    # text through the same path every other stored field takes — never a second,
    # backend-specific write path of this command's own. `--tags` REPLACES the whole list,
    # exactly as `cq specs tags` does, so the subject's fixed tags are folded into it here
    # rather than lost.
    tags: list[str] = []
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if subject and subject.get("tags"):
        tags = tags + [t for t in subject["tags"] if t not in tags]
    if tags:
        close = body.index("\n---\n")
        body = body[:close] + f"\ntags: {_tags_repr(tags)}" + body[close:]
    # The abstract catalogue key, never the backend's native name — `create_spec` reads it
    # off `fresh["frontmatter"]` and projects the native name at write time (§Design).
    if type_key:
        close = body.index("\n---\n")
        body = body[:close] + f"\nworkItemType: {type_key}" + body[close:]
    if args.summary:
        body = set_frontmatter_key(body, "summary", args.summary.strip())
    if complexity_record:
        body = set_frontmatter_record(body, "priority", complexity_record)
    if blocks:
        # Re-derived between splices, exactly as `cmd_section`'s own stream write does: each
        # section's write invalidates the next one's line offsets.
        cur = derive_info({"phase": "plans"}, body)
        for heading, section_body in blocks:
            block = (f"## {heading}\n\n{section_body.strip()}\n"
                     if section_body.strip() else section_guidance(heading))
            body, _ = upsert_section(cur, heading, block)
            cur = derive_info({"phase": "plans"}, body)
    # The parent, by contrast, has no canonical-document counterpart to carry it in — it is
    # `azure-boards`-only, applied through the SAME `self.parent_id` the backend already
    # reaffirms on every write (§2.4); a resolved subject here simply overrides the
    # `defaultSubject` `open_azure_backend` applied when the backend was opened.
    if subject and subject.get("parent") and hasattr(backend, "parent_id"):
        backend.parent_id = subject["parent"]
    path = backend.create_spec("plans", name, body)
    out.emit(args.json,
             {"ok": True, "slug": slug, "title": title, "verification": policy,
              "workItemType": type_key,
              "phase": "plans", "folder": "plans", "file": name, "stage": "captured",
              "path": display_locator(path, root)},
             f"created plans/{name}  (slug: {slug} · verification: {policy})\n"
             f"next: write ## Problem, then `cq specs section {slug} Proposal --write`")
    return 0
