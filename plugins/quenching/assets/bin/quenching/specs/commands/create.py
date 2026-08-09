"""`new` — scaffold one spec into `plans/`."""
from __future__ import annotations

import json
import sys

from quenching.common.dates import today
from quenching.common.text import slugify
from quenching.specs.backends import open_backend
from quenching.specs.commands.output import display_locator, emit, emit_err
from quenching.specs.config import (azure_workitemtype_retirement, load_config,
                                    resolve_subject, resolve_type_key)
from quenching.specs.parse import titleize
from quenching.specs.parse.spec import SLUG_RE
from quenching.specs.schema import DEFAULT_VERIFICATION, capture_form


def cmd_new(args, root: str) -> int:
    """Scaffold `plans/<slug>.md` carrying `## Problem` and nothing else.

    THE DATE IS STAMPED HERE AND NEVER AGAIN, now into the frontmatter's `date:` rather than
    into the basename. `promote` moves the file without renaming it, so the basename — the
    bare slug — is the spec's identity for its whole lifecycle, and the date is a fact the
    document carries instead of a fact its name encodes."""
    slug = slugify(args.name)
    if not SLUG_RE.match(slug):
        emit(args.json, {"ok": False, "code": "sp-bad-slug", "slug": args.name,
                         "message": f"'{args.name}' does not reduce to a kebab-case slug"},
             f"error: '{args.name}' does not reduce to a kebab-case slug")
        return 2
    backend, err = open_backend(root)
    if err:
        return emit_err(args.json, err)
    # Asked of the backend, not of the filesystem: a slug already taken in GitHub must
    # refuse here exactly as one already taken on disk does.
    matches = [s for s in backend.list_specs() if s["slug"] == slug]
    if matches:
        m = matches[0]
        emit(args.json, {"ok": False, "code": "sp-slug-exists", "slug": slug,
                         "existing": f"{m['folder']}/{m['file']}",
                         "message": f"slug '{slug}' already exists at {m['folder']}/{m['file']}"},
             f"refused: slug '{slug}' already exists at {m['folder']}/{m['file']}")
        return 2
    cfg = load_config(root)
    subject, serr = resolve_subject(cfg, args.subject)
    if serr:
        return emit_err(args.json, serr)
    type_key, terr = resolve_type_key(cfg, args.type)
    if terr:
        return emit_err(args.json, terr)
    if cfg["backend"] == "azure-boards":
        retirement = azure_workitemtype_retirement(cfg, type_key)
        if retirement and retirement["severity"] == "error":
            return emit_err(args.json, retirement)
        if retirement:
            print(f"note: {retirement['message']}", file=sys.stderr)
    policy = args.verification or DEFAULT_VERIFICATION
    title = args.title or titleize(slug)
    name = f"{slug}.md"
    body = (capture_form()
            .replace("<SLUG>", slug)
            .replace("<TITLE>", title)
            .replace("<DATE>", today())
            .replace("<VERIFICATION>", policy))
    # The subject's fixed tags go into the CANONICAL DOCUMENT, never applied to the tracker
    # directly: `tags:` is a recognised frontmatter key, so `create_spec` reads them off this
    # text through the same path every other stored field takes — never a second,
    # backend-specific write path of this command's own.
    if subject and subject.get("tags"):
        tags_repr = "[" + ", ".join(json.dumps(t, ensure_ascii=False)
                                    for t in subject["tags"]) + "]"
        close = body.index("\n---\n")
        body = body[:close] + f"\ntags: {tags_repr}" + body[close:]
    # The abstract catalogue key, never the backend's native name — `create_spec` reads it
    # off `fresh["frontmatter"]` and projects the native name at write time (§Design).
    if type_key:
        close = body.index("\n---\n")
        body = body[:close] + f"\nworkItemType: {type_key}" + body[close:]
    # The parent, by contrast, has no canonical-document counterpart to carry it in — it is
    # `azure-boards`-only, applied through the SAME `self.parent_id` the backend already
    # reaffirms on every write (§2.4); a resolved subject here simply overrides the
    # `defaultSubject` `open_azure_backend` applied when the backend was opened.
    if subject and subject.get("parent") and hasattr(backend, "parent_id"):
        backend.parent_id = subject["parent"]
    path = backend.create_spec("plans", name, body)
    emit(args.json,
         {"ok": True, "slug": slug, "title": title, "verification": policy,
          "workItemType": type_key,
          "phase": "plans", "folder": "plans", "file": name, "stage": "captured",
          "path": display_locator(path, root)},
         f"created plans/{name}  (slug: {slug} · verification: {policy})\n"
         f"next: write ## Problem, then `specs.py section {slug} Proposal --write`")
    return 0
