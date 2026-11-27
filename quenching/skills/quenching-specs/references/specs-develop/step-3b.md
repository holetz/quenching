### 3b. Load what THIS pass needs — and nothing more
Now that the pass is known, and in **one call** — §The batching contract's second row, both
commands together, every stage at once:

```text
components_read(verb="read", path=".agents/quenching/references/specs-develop/questions.md", sections=["§Compose", "§Approval"])   # + "§Refine" where refine runs,
                                                    # + "§Who answers", + "§Gathering the evidence"
specs_read(verb="section", spec=<id>, headings=<every heading this pass reads or writes>)   # the union, once
```

| Stage | Spec sections it reads or writes |
| --- | --- |
| discoveries | `## Discoveries` |
| compose | `## Problem` `## Design`, plus every heading `ready.missing`/`ready.malformed` named in step 2, plus `## Impact` `## Tasks` where step 3d runs |
| refine | `## Problem` `## Proposal` `## Design` `## Alternatives Considered` `## Risks` `## Impact` `## Tasks` |
| approval | `## Proposal` `## Impact` `## Risks` — and it writes nothing into the body |

Ask for the **union**, in one call. A heading that is absent comes back as `(## X is absent)` with
exit 1 — a result, not a refusal, and it is the same gap map `ready` already reported.

**Compose and refine also read `/docs/`** (Doctrine): the `/docs/standards/` this spec's
`## Impact` declares — the declared files, never the folders they sit in — and
`/docs/glossary.md`. Either **may** delegate that reading to a read-only sub-agent under
§Gathering the evidence, which returns one compact table. It is an option, not a step: for a
two-file spec, keep the reading.
**Done when:** every stage's section and the union of spec sections are in hand, in one call, and
nothing else was opened.
