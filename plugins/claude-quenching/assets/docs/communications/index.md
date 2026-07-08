# `communications/` — directed communication (outbound)

**Announcements to an audience**: outbound messages directed at a business/team/stakeholder
audience — incident, change, deploy, downtime, migration, news, status update. They are
**scannable** (the reader decides in seconds), **dated**, and **archivable**.

**Boundary:** `communications/` = "**messages we send to an audience**" (transient, dated) —
distinct from [documentation/](/docs/documentation/index.md) (how-to), [decisions/](/docs/decisions/index.md)
(why we decided), [standards/](/docs/standards/index.md) (current contract), and
[presentations/](/docs/presentations/index.md) (visual binary). A communication that becomes
a permanent rule **distills into `standards/`**; the message itself stays in
[archive/](archive/index.md) as a record. An issued announcement carries `type: communication`.

## Scannable header (invariant)

Every announcement opens with a **fixed header** of high-signal fields, then a one-sentence
summary + short description. The reader decides **by reading only the header**:
**scope · status · impact · audience · active period · action required · last updated**.

## Structure × content

The skeleton ships the **structure** — the home, one **template per channel**, and the
header form. **Which** communications exist and with what values is this repo's decision.

## Subfolders

* [templates/](templates/index.md) — one **template per channel** (email/chat/wiki/markdown)
* [archive/](archive/index.md) — concrete communications already issued, dated (the repo creates these)

Generating an announcement from a channel template is a job for `quenching-insert` (home
`communications/archive/`).
