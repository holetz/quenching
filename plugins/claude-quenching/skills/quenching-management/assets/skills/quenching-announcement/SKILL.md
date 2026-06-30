---
name: quenching-announcement
description: >-
  Drafts DIRECTED/outbound communication to an audience — incident, change,
  deploy, outage/maintenance, migration, update, or status-update announcement —
  reading the template for the requested CHANNEL (email, Slack/Teams,
  Confluence/Notion, markdown) from communications/templates/ and filling it in.
  Use when the user asks to "communicate", "notify", "announce", "draft an
  announcement", "write a message to the team/area", "open an incident alert",
  "inform about a change/deploy/outage/migration", or mentions "X broke",
  "down", "scheduled maintenance", "update the announcement". Generates
  scannable messages with a fixed header (scope · status · impact · audience ·
  validity · action · last-updated) + summary + description.
when_to_use: >-
  draft/update a directed announcement to an audience, adapted to the delivery
  channel, from the per-channel templates versioned in communications/.
allowed-tools: Read, Grep, Glob, Edit, Write
---

# Directed announcement — per-channel generator

> Skill-template of the `quenching-management` method. Generic and portable:
> **does not embed** scopes, audiences, or status values from any repo — reads
> the channel template from `<docs>/communications/templates/` and fills it with
> what the user provides. Fix the real path of `communications/` in the repo
> where it is installed.

## What this skill is (and is not)

It is **one** generic skill that **reads per-channel templates** and fills them
in — not one skill per topic (incident/deploy/migration are **values of
status/scope**, not distinct skills). The channel defines the **form**; the topic
defines the **values**.

## Procedure

1. **Gather the header fields** (ask the user only for what is missing):
   **scope** · **status** (`open`/`in-progress`/`resolved`/`monitoring`/
   `informational`) · **impact** (`high`/`medium`/`low`) · **audience** ·
   **validity** · **action required** (`yes — what` / `no`) · **what happened /
   why it matters** (description). If this is an **update** to an already-open
   announcement, change only `status` + `last-updated`.
2. **Choose the channel and read the right template** from
   `communications/templates/`: `email.md` · `chat.md` (Slack/Teams) ·
   `wiki.md` (Confluence/Notion) · `markdown.md` (**default** if the channel was
   not specified). Read **only** the template for the requested channel
   (progressive disclosure — do not load all).
3. **Fill in the `<placeholders>`** of the template; do **not** rewrite the
   structure or rename the header fields. The reader decides **by reading only
   the header** whether to continue — keep it intact and scannable.
4. **Respect the channel difference** (noted in each template footer): subject
   line in email; edit-the-original-message + pin in chat; property table +
   update history in wiki.
5. **Validate:** reading only the header, can the reader decide if it is
   relevant? Is `Action required` clear? Is each description block ≤ 2 sentences?
   No jargon in the `Summary`?
6. **Archive** the issued announcement in `communications/archive/` as
   `YYYY-MM-DD-<scope>-<slug>.md` (dated record, `authority: background`).

## New channel

If the repo adopts a channel without a template (e.g., status page, WhatsApp),
**create** `communications/templates/<channel>.md` with the **same logical header**,
adapting only the form. A channel used without a template = the form becomes ad-hoc
(smell of dim 2).

## Boundary

An announcement is **not** a guide (`guides/`), an ADR (`decisions/`), or a
contract (`standards/`). If the message has become a permanent rule, **distill it
to `standards/`** and keep the announcement in `archive/` only as history. The
taxonomy of the home lives in `references/docs-taxonomy.md` of the method.
