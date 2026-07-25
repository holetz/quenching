# CLAUDE.md — <folder>/

<1-2 lines: what this folder is, and what an agent working HERE needs to know.
Auto-loads only under this folder — nearest-file navigation, not a second root.>

- **Local operations:** <commands / quirks scoped to this folder — omit this bullet if none>.
- **Knowledge for this area:** [<home>](/docs/<home>/index.md) — <one line on what that home holds>.
- **Unfamiliar term?** Resolve it in the glossary: [/docs/knowledge/glossary.md](/docs/knowledge/glossary.md)
  (`grep -i '<term>'`) — omit this bullet if the repo has no glossary.
- **To create / edit knowledge:** use the `claude-quenching` skills (`quenching-docs-add` to add
  one, `quenching-docs-align` to migrate/normalize, `quenching-docs-harness` to keep pointers thin).
- **Boundary:** only <this folder's> concern lives here — <neighbor concern> → <its home>.

<!-- Auto-loaded by Claude Code when working under <folder>/. Keep it a thin pointer
     (nearest-file navigation), never a copy of the knowledge it points to, and never a
     duplicate of the root CLAUDE.md. Installed by the claude-quenching plugin; this file is a
     harness pointer, not an OKF concept. -->

<!-- MOLD (claude-quenching · subfolder harness pointer — do NOT copy this note into the produced file):
     Produces a subfolder CLAUDE.md as a THIN, NEAREST-FILE navigation pointer. Modeled on the
     shipped exemplar assets/docs/standards/CLAUDE.md (18 lines).
     • NO frontmatter, NO `type` — EXEMPT from OKF (okf-spec §strict-7); the validator skips it.
       EVERY link MUST resolve (checked by quenching-docs-harness, not the validator).
     • It auto-loads ONLY when the agent works under this folder: put the LOCAL commands/quirks
       and a pointer to the home that COVERS this area. Never duplicate the root — the root owns
       repo-wide operations and the full home map.
     • CREATION IS EVIDENCE-GATED: propose a new subfolder pointer only where the evidence is concrete —
       either a harness unit clearly scoped to this folder, or a greenfield folder with a local
       operational surface (build/run script, distinct toolchain, README of run-commands) and no
       CLAUDE.md. Never one per directory; data/output/asset folders earn nothing.
       `quenching-docs-align`'s skeleton already ships docs/standards/CLAUDE.md.
     • Size budget: aim ≤ ~20 lines. Structure/links canonical English; prose MAY follow the repo's language. -->
