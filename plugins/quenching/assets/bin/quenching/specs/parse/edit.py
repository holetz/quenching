"""The section engine — resolving a requested heading name, and splicing one section's
block back into a document in canonical position.

Moved verbatim out of the pre-refactor specs script."""
from __future__ import annotations

from quenching.specs.parse.handoff import (current_handoff_section, parse_handoff,
                                           task_section_title)
from quenching.specs.parse.tasks import parse_tasks
from quenching.specs.parse.text import body_after_frontmatter
from quenching.specs.schema import canonical_headings, section_guidance


def _canonical_index(heading: str, schema: dict | None = None) -> int:
    canon = canonical_headings(schema)
    return canon.index(heading) if heading in canon else len(canon)


def resolve_heading_name(name: str, candidates: list[str]) -> str | None:
    """One requested name onto the candidate that answers it, or None.

    **`§X` and `## X` are the same request, and a UNIQUE prefix resolves** — the two forms
    `SECTION_CASES` pins, which the components pillar carries verbatim. The command bodies already cite
    sections as `§Handoff`, so a reader that refused over the marker would be unusable from the
    very prose it serves. An ambiguous prefix resolves to nothing: a guess between two headings is
    worse than the refusal that names them.

    It takes the candidate list as an argument for one reason — so the canonical cases exercise
    THIS function over the fixture's headings, rather than a second copy of the rule written
    inside the selftest. A rule proved against a private re-implementation is not proved."""
    want = " ".join(name.strip().lstrip("#§").strip().split()).lower()
    if not want:
        return None
    for c in candidates:
        if c.lower() == want:
            return c
    hits = [c for c in candidates if c.lower().startswith(want)]
    return hits[0] if len(hits) == 1 else None


def _match_heading(heading: str) -> str | None:
    """Case-insensitive lookup onto the canonical spelling. Headings are a parsed contract,
    so the FILE always carries canonical English — but a human typing `cq specs section x
    validation` should not get a stray section for their trouble."""
    return resolve_heading_name(heading, canonical_headings())


def upsert_section(info: dict, heading: str, block: str) -> tuple[str, str]:
    """Replace a section's block, or create it in CANONICAL POSITION when absent.

    Position is derived from the schema's declared order, not from where the writer
    happened to be: a spec whose `## Tasks` was written before its `## Proposal` still
    reads in contract order, so a human and the parser see the same document."""
    text = info["text"]
    lines = text.splitlines(keepends=True)
    # sections were parsed from the body, so their line numbers need the frontmatter back
    fm_offset = len(lines) - len(body_after_frontmatter(text).splitlines(keepends=True))
    if heading in info["sections"]:
        sec = info["sections"][heading]
        start = sec["lineno"] + fm_offset
        end = start + 1 + len(sec["lines"])
        return "".join(lines[:start]) + block + "".join(lines[end:]), "replaced"
    idx = _canonical_index(heading)
    following = [sec["lineno"] + fm_offset for h, sec in info["sections"].items()
                 if _canonical_index(h) > idx]
    if following:
        at = min(following)
        return "".join(lines[:at]) + block + "\n" + "".join(lines[at:]), "created"
    return text.rstrip() + "\n\n" + block, "created"


def write_handoff_block(info: dict, scope: str, body: str) -> tuple[str, str]:
    """Replace ONE piece of `## Handoff` — `scope="global"` for the evergreen block, or
    `scope="current"` for the `### N.` block matching the next actionable task's section
    — and leave every OTHER block exactly as it stood. That is the whole of "closing": a
    section's block is simply never targeted again once its tasks are done, the same way
    a merged branch needs no explicit "done" flag.

    Reuses `upsert_section` for the actual splice rather than re-deriving its frontmatter
    offset math — this function's only job is to compute `## Handoff`'s new FULL body
    with one block swapped, then hand that whole block to the existing writer."""
    body_text = body_after_frontmatter(info["text"])
    parsed = parse_handoff(body_text)
    new_body = body.strip("\n")

    if scope == "global":
        global_text, blocks = new_body, parsed["blocks"]
    else:
        tasks = parse_tasks(body_text)
        n = current_handoff_section(tasks)
        if n is None:
            return info["text"], "no-op"
        global_text = parsed["global"].strip("\n")
        title = next((b["title"] for b in parsed["blocks"] if b["section"] == n),
                     None) or task_section_title(body_text, n) or str(n)
        blocks = [dict(b, body=new_body) if b["section"] == n else b
                 for b in parsed["blocks"]]
        if not any(b["section"] == n for b in parsed["blocks"]):
            blocks = blocks + [{"section": n, "title": title, "body": new_body}]

    parts = [global_text] if global_text else []
    parts += [f"### {b['title']}\n\n{b['body'].strip(chr(10))}" for b in blocks]
    section_text = "\n\n".join(p for p in parts if p.strip())
    block = f"## Handoff\n\n{section_text}\n" if section_text else section_guidance("Handoff")
    return upsert_section(info, "Handoff", block)
