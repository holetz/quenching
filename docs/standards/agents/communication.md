---
type: standard
title: Agent communication
description: The two language bands an agent writes in — durable artifacts in canonical English so they stay portable and greppable across repos, conversation in the one BCP-47 tag the root harness line declares — and the conduct contract that holds whether or not a language is declared
resource: /docs/**, /.specs/**
tags: [agents, language, communication, harness]
timestamp: 2026-08-29
audience: both
authority: background
source: spec plan/declare-repo-body-language — binds the loose language clause that six standards and shipped references deferred to without any of them defining it
maintainer: quenching
---

# Agent communication

How an agent communicates here, in two halves: the **language** it writes in, which each repo
declares for itself, and the **conduct** it owes whoever is reading, which no repo overrides.

One is a variable, the other a constant — see [Why only one is declared](#why-only-one-is-declared).

## The language

### Declaring it

A repo declares its **conversation** language as **one BCP-47 tag**, on a single line of its
**root** harness file (`CLAUDE.md` / `AGENTS.md`):

```
Language: pt-BR — the contract is /docs/standards/agents/communication.md
```

That line carries **a value and a citation, and nothing else**. It never paraphrases the rule below:
a harness file that restates a standard is precisely the drift `/quenching:components:harness:align` exists to remove,
while a value plus a pointer is not a restatement. It carries **one** value — a second configuration
key on that line is a defect, not a feature.

Three properties earn this form:

- it is **in context at session start**, so reading it costs zero tool calls;
- it works in a repo that has `specs/` and **no `/docs/` bundle** at all;
- it is one line, so there is nothing to keep in sync.

**Only the root harness carries the declaration.** A nested harness file
([../CLAUDE.md](../CLAUDE.md), for instance) loads when that folder is touched, not at session
start, so it would give up the zero-cost property this form was chosen for. A tag found in a nested
harness file is a mistake to report, never a second place to look.

**The value is a tag, not a language name.** `pt-BR`, `en`, `ja` — one spelling each. A name invites
`Português`, `portugues` and `Portuguese` to mean the same thing, and no amount of citation fixes
that.

### What it governs — one band, not both

The prose an agent authors splits into two bands, and **they take different languages**:

| Band | Examples | Language |
| --- | --- | --- |
| **Artifact** | a concept doc's body · a spec's body, `## Handoff` and `## Tasks` included · a commit subject and message · a PR body | **canonical English, always** |
| **Conversation** | an answer to the human · a question a command asks · a report a command prints | **the declared tag** |

The declared tag governs the conversation band only. That band is the one that costs most per day
when it is missed: an agent that reads the tag at session start and still answers, asks and reports
in a language the human did not choose has followed none of this.

**Why the artifact band is English and not the tag.** An artifact outlives the conversation that
produced it and travels further than the team that wrote it. Three properties decide it:

- **It is greppable across repos.** The bundle's whole promise is the same tree in the same place
  in every adopted repository. A `standards/` doc a reader can find by name in one repo and not in
  the next because the prose changed language is a bundle that only looks portable.
- **It is published.** The bundle root is `docs_dir`: every concept doc is a page of the site, read
  by people who never joined the conversation that produced it.
- **It sits beside canonical English structure.** Folder names, slugs, frontmatter keys, `type`
  values and parsed headings are already English by the exclusion below. A body in another language
  wrapped in English metadata is a document that switches language mid-file.

**What this costs, stated plainly.** A team that works in pt-BR now writes its durable docs in a
second language, which is real friction and a real quality risk: a rule written imprecisely in
English is worse than one written precisely in Portuguese. The trade is deliberate — portability
and publication over authoring comfort — and a repo that does not want it declares nothing and is
under no constraint at all (see [What silence means](#what-silence-means)).

Two exclusions, and only two:

1. **The canonical structure.** Folder names, file slugs, frontmatter keys, enum values, the `type`
   vocabulary and the parsed `##` headings stay canonical English, so they stay greppable across
   repos. That rule is not this doc's — it belongs to
   [../naming/command-surface.md](../naming/command-surface.md), and this doc only names it as its
   own boundary.
2. **This plugin's own command surface.** Every body under `plugins/quenching/commands/**` is
   English whatever a target repo declares — which is now the same rule as the artifact band rather
   than an exception to it. **Their output is not.** A question a command asks and a report it
   prints are prose aimed at the human, and they follow the tag. The body in English, the output in
   the language — translating a body is the error this distinction exists to prevent.

### What silence means

**A repo that declares nothing is under no constraint** — in either band. Silence is not a default
of `en` and it is not a finding; a repo that declares no tag is not thereby required to write its
artifacts in English. Adoption is opt-in per repo: nothing becomes retroactively non-conformant, and no
repo that already carries the bundle has to change. Declaring a tag does not retranslate the docs
already written — that is a migration, and a separate piece of work.

Nothing machine-checks any of this. A validator cannot reliably identify the language of a
document, so this rule is applied by convention — as every rule about what prose *says*, rather
than where it sits, must be.

## The conduct

The second half is a **constant**: identical in every repo, not configurable, and never written on
the harness line. It is *stated* here, not declared anywhere.

Three obligations hold in **every** task, whether or not a command is driving and whatever the
declared language:

- **Report what actually happened.** A check that failed is reported failing, with its output. A
  step that was skipped is named as skipped. Work that is done and verified is said plainly,
  without hedging. A green summary over a red run is the one failure mode from which nothing
  downstream can recover.
- **Confirm before the irreversible.** Anything hard to undo or outward-facing is confirmed first,
  unless the human has already authorized it durably. Approval in one context does not extend to
  the next.
- **Ask rather than guess — but only what the answer changes.** A question is owed when different
  readings of the request lead to materially different work. Routine judgment calls are made, not
  escalated.

### This half cites; it never restates

Most of the ground near these three already has an owner, and a second statement of a rule someone
else owns would commit — one layer up — the very defect this doc exists to cure. So the boundary is
drawn explicitly:

| Ground | Owner | This doc |
| --- | --- | --- |
| What one command promises, refuses and routes elsewhere | that command's own body and `description` under `plugins/quenching/commands/**` | never restates it |
| The mechanics of actually asking — how a question is posed, accumulated and applied | `specs-develop/questions.md` §The four shared mechanics (`plugins/quenching/assets/references/specs-develop/questions.md`) | cites it |
| How commands, hooks and agent definitions are classified, authored, budgeted and swept | [../automation/](../automation/index.md) | cites it |

What is left — and what this doc owns — is only what holds in **every** task, command or not. That
is the band none of the three above occupies, and keeping to it is the single failure mode this
half has.

## Why only one is declared

The test is which of the two facts actually varies.

**Conversation language varies between repos**, and only that. That is why it needs one place per
repo to be said — and why the artifact band, which does not vary, is stated here rather than
declared anywhere.

**Conduct does not.** "Report what happened", "confirm before the irreversible" and "ask when the
answer changes the work" are not local preferences; they are the contract. Declaring what does not
vary buys nothing and costs an entire configuration surface: the set of valid profiles, its
evolution, and the end of the *one line, zero tool calls* argument that chose this form in the
first place.

A doc with one variable and one constant is a single definition. Two declared values would be two
configurations sharing a file.
