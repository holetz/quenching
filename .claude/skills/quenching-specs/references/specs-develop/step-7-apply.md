### 7. Apply, verify, and record what the pass earned
- **Apply the explicit-none rule on every write.** A section with nothing in it is
  `- none — <reason>`, a present-but-empty heading is malformed, and an absent heading before its
  own gate is legal —
  [spec-driven.md](.agents/quenching/references/specs-develop/spec-driven.md)
  §The gates.

**The batching contract for this step:**

| Where | The bounded read(s) |
| --- | --- |
| step 7 | the entire application — the section write, every `specs_write(verb="discover")` line, every `specs_write(verb="record")`, `specs_write(verb="verification")`, `specs_read(verb="validate")` (plus `specs_read(verb="parallel")` where `## Tasks` moved), and the closing `specs_read(verb="status")` that verifies where the pass landed |

On the git store every write of step 7 lands in the clone's local pending commit: the remote and
the card see the pass at the next sync point (`git_external(verb="push")`, `git_external(verb="pr_create")`, `specs_external(verb="push")`), and `specs_read(verb="status")` lists the spec as pending until then.

A call splits only where the next command's **input** depends on the previous one's output. The
`approved` stamp is the one such split: it waits for step 7's verification to prove `ready` rather
than asserting it off the drafts.

**Every write of this step is ONE call** — the batching note above: the section write,
the `## Discoveries` lines, the records, `verification`, `validate`, and the closing `status`.

Write the narrated sections with ONE `specs_write(verb="section_write", spec=<id>, sections=[…])` — it creates
each heading in canonical position on first write, so creating and revising
are the same call. An emptied section becomes an explicit `- none — <reason>`, never a deleted
heading. The surface group and the `## Impact` sub-heading that declares it land in this same
single write as the rest; there is no surface-specific write, call or record.

**Every body goes in that one call:**

```text
specs_write(verb="section_write", spec=<id>, sections=[
  {"heading": "<Heading>", "body": "<the drafted section, verbatim>"},
  {"heading": "<Other Heading>", "body": "<the other drafted section, verbatim>"}])
```

A repeat or a heading outside the canonical thirteen refuses (exit 2) **without writing any of
them**. `heading` and `body` instead of `sections` is the singular form. The N splices land as ONE
write.

Every follow-up the plan parked is written in this same edit — `specs_write(verb="discover", spec=<id>,
text="<finding>")`, one call per line — and never mid-stage, which
[questions.md](.agents/quenching/references/specs-develop/questions.md) §The four shared
mechanics forbids. The call creates `## Discoveries` when the heading is absent, and a filled
`## Discoveries` moves no derived stage.

**Ask the epic's authorization before the execute, never at the verify.** When a task's `files:` touches the
surface of the verifier's checks 9 and 10 (a hook, settings, a workflow, a grant, the gate) and the spec belongs to an
epic, the human answers once whether the epic's `## Design` authorizes it (a sub-agent returns `needs-human:`), and the
dated bullet naming the spec id or the path is written to that `## Design` before `execute`.

Then the frontmatter records this command owns — read
[questions.md](.agents/quenching/references/specs-develop/questions.md) §Recording the
pass for which stage earns which, and
[spec-driven.md](.agents/quenching/references/specs-develop/spec-driven.md) §Frontmatter
for the write-once semantics, in one call. Each is stamped through `specs_write(verb="record")`:

| Record | When | Call |
| --- | --- | --- |
| `refined: {mode, date}` | compose or refine ran; `mode` is the deepest reached | `specs_write(verb="record", spec=<id>, name="refined", fields={"mode": "<compose\|refine>", "date": "<today>"})` |
| `verification` | compose settled the policy | `specs_write(verb="verification", spec=<id>, policy=<per-task\|per-section\|end-of-plan>)` |
| `tags` | the pass changed the spec's scope, or the capture presumed wrong | `specs_write(verb="tags", spec=<id>, value=<whole list>)` |
| `complexity` (in `priority`) | the pass outgrew its size and the human approved the new level, or the close's recommendation was taken (step 8) | `specs_write(verb="record", spec=<id>, name="priority", fields={"complexity": "<level>", "date": "<today>"})` |

`approved` is **not** stamped here — it waits for the verification below to prove `ready`, and is
stamped in step 8.

`specs_write(verb="tags")` **replaces** the whole list, never appends — reissue the subject's own fixed tags
together with whatever this pass adds, or the fixed ones are lost.

The title is the sole short description every ranked listing prints (`specs_read(verb="next")`); keep it descriptive when the spec's scope changes.

`verification` is a plain frontmatter key with a verb of its own. Omit the value to read what is in
force; absent means the default, and the default is never stamped to make it explicit.

`complexity` is a field of `priority`, and the record merges — `level` and `criticality` survive
a re-stamp that touches only the size.

Then, in the same call, **verify where the pass landed**: `specs_read(verb="validate", spec=<id>)` and
`specs_read(verb="status", spec=<id>)`. **When this pass touched `## Tasks`, run `specs_read(verb="parallel", spec=<id>)`
here too** — exit 1 names the `[P]` group whose `files:` sets are not disjoint, and
definition time is the only moment that is cheap to fix. Report what each says; a `[P]` nobody
proved is a promise execution will refuse.
**Done when:** the pass's one edit is written, the records it earned are stamped, and validate,
`status` — plus `parallel`, where `## Tasks` moved — have run in that same call.
