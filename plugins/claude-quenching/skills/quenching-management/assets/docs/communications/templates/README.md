---
title: communications/templates/ — one template per channel
audience: both
authority: background
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `communications/templates/` — template per channel

One template file **per channel**. All carry the **same logical header**
(scope · status · impact · audience · active period · action · last-updated +
one-sentence summary + short description); each adapts the **form** to the channel.

| Template | Channel | Difference it captures |
| --- | --- | --- |
| [email.md](email.md) | E-mail | key fields in the **subject** (`[SCOPE][IMPACT] title — action DD/MM`); full body |
| [chat.md](chat.md) | Slack / Teams | header in the main message; **edit the original message** on each update (do not reply in thread); pin while open |
| [wiki.md](wiki.md) | Confluence / Notion | header becomes a filterable **properties table** at the top of the page |
| [markdown.md](markdown.md) | neutral | works in any renderer — **the default** when the channel was not specified |

## How to use

- The `<prefix>-announcement` skill reads the template for the **requested channel**
  and fills it in with the gathered values — it does **not** rewrite the template,
  only substitutes the `<placeholders>`.
- **New channel ⇒ new template.** If the repo adopts a channel not listed here
  (e.g.: WhatsApp, status page), add a `<channel>.md` with the same logical header.
  A channel used **without** a template is a smell (the form becomes ad-hoc).
- Do not change the **field names** in the header between channels — only the way
  they are rendered (line, subject, property). That is what keeps the communication
  scannable on any channel.

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
