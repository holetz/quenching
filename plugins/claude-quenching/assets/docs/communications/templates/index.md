# `communications/templates/` — one template per channel

One template file **per channel**. All carry the **same logical header** (scope · status ·
impact · audience · active period · action · last-updated + one-sentence summary + short
description); each adapts the **form** to the channel. Each template carries
`type: communication-template`.

| Template | Channel | Difference it captures |
| --- | --- | --- |
| [email.md](email.md) | E-mail | key fields in the **subject** (`[SCOPE][IMPACT] title — action DD/MM`); full body |
| [chat.md](chat.md) | Slack / Teams | header in the main message; **edit the original** on each update; pin while open |
| [wiki.md](wiki.md) | Confluence / Notion | header becomes a filterable **properties table** |
| [markdown.md](markdown.md) | neutral | works in any renderer — **the default** when the channel was not specified |

## How to use

- `quenching-insert` reads the template for the **requested channel**, fills the `<placeholders>`
  with the gathered values, and writes the issued announcement into
  [../archive/](../archive/index.md) (`type: communication`, dated filename).
- **New channel ⇒ new template.** Add `<channel>.md` with the same logical header. A channel
  used **without** a template is a smell.
- Do not change the header **field names** between channels — only how they are rendered
  (line, subject, property). That is what keeps the announcement scannable everywhere.
