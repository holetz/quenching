---
name: <agent-name>
description: >-
  <3rd person. What the sub-agent does, what input it receives, what it returns
  (condensed result), and WHEN to use it. E.g.: "Performs <scan X> and returns
  only <summary Y>, keeping the main context clean. Use when <the output would
  flood the thread>.">
tools: Read, Grep, Glob          # ALWAYS declare — omitting inherits ALL parent tools
model: haiku                     # audit/scan cheap; opus for heavy reasoning
# disallowedTools: Write, Edit   # alternative denylist (applied before allowlist)
---

You are <role>. Runs in its own context window and returns **only the summary**.

## Inputs
- <what it receives>

## Steps
1. <numbered step>
2. …

## Return format (short)
- <field>: <what goes here>
- …

Do not dump the raw scan into the parent context — only the essentials.
