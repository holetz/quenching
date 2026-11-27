# /quenching-specs create — step 4, resolve a subject, a type, tags and `complexity`: decide, never ask

Resolve the tool per
[align/tool-resolution.md](.agents/quenching/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal), never on prose.

```text
specs_read(verb="config")
```

Read `subjects`, `workItemTypes` and `tagCatalog`. **All three absent or empty → skip only the
metadata lookups** — most repositories declare none of them; still compute `complexity` below.
Where only one or two are declared, resolve only those — this is per-key, never all-or-nothing.

**A declared `subjects`:** read each key's `name`/`description`, judge which one the input best
fits — or fall back to `azurePlacement.defaultSubject` where nothing beats it — and carry the
chosen key to step 5's `--subject`. Keep the one-line reason it was chosen for step 6's screen.

**A declared `workItemTypes`:** read each key's `description` — the same prompt material a
`tagCatalog` value already is — judge which entry the input best fits, or fall back to a declared
`default`, and carry the chosen key to step 5's `--type`. Keep the one-line reason for step 6.

**A declared `tagCatalog`:** read each tag's description — prompt material — and resolve zero or
more that fit the input. A tag outside the declared catalog is never chosen. Carry
whatever was resolved to step 5's `--tags`; the subject's own fixed tags need not be repeated —
`specs_write(verb="create")` folds them in on its own.

**Compute `complexity`** from the classification (step 1), never by interrogating: both the
**sentence path and the plan-source path yield `medium`**, and `low` only where the input explicitly
asks for an unattended pass. The level answers how much a human needs to be part of the process,
never the size or difficulty of the input — the four levels and what each buys are
[spec-driven.md](.agents/quenching/references/specs-develop/spec-driven.md) §The scale, never
transcribed here.

**A capture presumes `medium`**: it puts a human on every question of the definition and then
**recommends** whether the spec needs arguing with, judged against a composed spec rather than a
sentence.

Carry the level to step 5's `--complexity`, and the one-line reason ("a capture, so a human answers
the definition and the close recommends whether it needs arguing with") to step 6.

**Every one of these four is a presumption, not a verdict**, confirmed nowhere before it is written;
step 6 is where the human sees it and corrects it in one answer.
