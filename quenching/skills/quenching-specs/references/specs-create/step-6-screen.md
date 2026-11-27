# /quenching-specs create — step 6, the one screen: capture, correction and direction

Resolve the tool per
[align/tool-resolution.md](.agents/quenching/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal), never on prose.

```text
components_read(verb="read", path=".agents/quenching/references/specs-develop/report-mold.md", sections=["§The report mold"], rules_only=true)
```

Emit §The report mold's fixed header (report shape:
[report-mold.md](.agents/quenching/references/specs-develop/report-mold.md)
§The report mold), then one body block showing what was written and what was
presumed and why — the shape differs by path:

| Path | What the body block shows |
| --- | --- |
| sentence | the descriptive title and drafted `## Problem` text **in full**, exactly what a human wants to check about the capture. Plus subject, type, tags and `complexity`, each with its one-line reason |
| plan source | subject, type, tags and `complexity` (each reasoned), and the **list** of sections filled with the task count. **Never the bodies** — the plan is large and the human just wrote it |

Then the next-step block — `/quenching-specs develop <id>` as the forward candidate — and **one**
decision sheet ([questions.md](.agents/quenching/references/specs-develop/questions.md) §The four shared mechanics §1), immediately after. Two options, labelled in the declared language:

A. **Develop now (recommended)** — narrate, then invoke `quenching-specs develop <id>` through
   the **Skill** tool, with no sentence declared. Whether that pass asks anything is the
   `complexity` shown on this sheet: `high` and `xhigh` ask, `low` and `medium` answer from
   evidence and park the rest in `## Open Decisions`; correcting it in the reply is how the human
   chooses to be asked or not.
B. **Stop here** — nothing more is invoked; the report above is the whole of this run.

**The correction is free text in the reply**, invited explicitly by the sheet ("…or correct any
presumption in your reply before continuing"). A correction is
applied with the deterministic verb that owns the field — `specs_write(verb="tags", spec=<id>, value=<whole list>)`
(fixed tags included, or they are lost), `specs_write(verb="record", spec=<id>, name="priority",
fields={"complexity": "<level>", "date": "<today>"})`, `specs_write(verb="section_write", spec=<id>, heading="<Heading>", body=<body>)` — **and only
then** honour whichever of the two options the same reply also names. A reply that names
no direction falls to B.
