# Output contracts

**Mandatory intermediate outputs.** The skill may not edit a page until these six
contracts exist for the job. They are the plan of record — produce them in order,
show them, and only then write. Keep each terse (a filled template, not an essay).

Where to write them: for a small job, inline in the working message; for a large
one, a scratch file (e.g. `docs/_studio/plan.md`, deleted before delivery, or a
scratchpad path). Never ship the contracts as site pages.

---

## 1. Diagnosis
```markdown
### Diagnosis
- Sources found:      <files/dirs; who each is for>
- Target audience:    <primary readers + technical maturity>
- Current site state: <greenfield | existing nav shape | toolchain>
- Main problems:      <orphans · duplication · weak titles · walls · dumps>
- Truth/source risks: <claims with no obvious source; stats to verify>
- Visual opportunities: <where a flow/table/map would unlock a wall>
```

## 2. Reader journeys
Define at least these three, end to end:
```markdown
### Reader journeys
- 5-min evaluator:    landing → ? → ? → verdict (no full read needed)
- Working implementer: quickstart → guide → reference → troubleshooting
- Agent / LLM:        entry → matching heading → copy contract/example
```
Each journey must reach its goal with no dead-end or forced backtracking.

## 3. Information architecture proposal
```markdown
### IA proposal
- New nav tree:       <intent-based sections & pages>
- Source → dest map:  <source.md → dest.md (+ split/merge)>
- Page intents:       <one intent per destination page>
- Out of scope:       <what is dropped and why>
- Becomes reference:  <which sources → reference pages>
- Becomes guide:      <which sources → how-to pages>
- Becomes concept:    <which sources → explanation pages>
```

## 4. Visual plan
```markdown
### Visual plan
- Cards:      <where "choose your path" applies>
- Tabs:       <where a concept has platform/profile/scenario variants>
- Mermaid:    <which flows/architectures/maps>
- Tables:     <which comparisons/params/decisions>
- Hero:       <landing(s) only>
- Badges:     <which pages get an info bar>
- Screenshots/assets: <need + strategy — proposed, see visual-language.md>
- NO visual:  <pages/sections that must stay plain text>
```

## 5. LLM-readability plan
```markdown
### LLM-readability plan
- TL;DR for agents:  <which pages carry a contract block>
- Input/output contracts: <which pages state them explicitly>
- Stable headings:   <headings that must not be renamed>
- Key anchors:       <#anchors agents will deep-link>
- Glossary/concept map: <exists? which terms defined once>
- Copyable examples: <which real commands/snippets>
```

## 6. Execution plan
```markdown
### Execution plan
- Files to edit:     <path → change>
- MkDocs extensions needed: <attr_list, md_in_html, tabbed, emoji, mermaid, …>
- Risk per change:   <low | med | high — and why>
- Validation:        <strict build + visual QA + rubric threshold>
```

---

## Rule
If any contract can't be filled because the sources are silent, write
**`source gap: <what's missing>`** instead of guessing, and carry it into the
[source ledger](source-ledger.md). A missing input is a documented gap, never an
invention.
