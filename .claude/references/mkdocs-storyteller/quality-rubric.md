# Quality rubric

Every page is scored **0–5** on ten dimensions before it can be called done. The
score is not decoration — it is the gate. A page below threshold goes back into the
[editorial loop](editorial-loop.md).

## The scale
| Score | Meaning |
| --- | --- |
| **0** | Fail — absent, wrong, or actively misleading |
| **1** | Weak — present but barely acceptable |
| **2** | Good — does its job |
| **3** | Excellent — clearly above average |
| **4** | Reference — other pages should copy it |
| **5** | Iconic — memorable, nothing to add or cut |

## The ten dimensions
| # | Dimension | 0 (fail) | 2 (good) | 4–5 (reference/iconic) |
| --- | --- | --- | --- | --- |
| 1 | **Hook** | opens with a definition/topic | first line states what & why | first line makes you *have* to read on |
| 2 | **Intent clarity** | unclear who/what it's for | one clear purpose | purpose obvious in 3 seconds |
| 3 | **Information architecture** | orphan / wrong section | fits the nav & journey | anchors the whole section |
| 4 | **Scannability** | wall of text | headings, lists, callouts | skim gives 80% in 20 seconds |
| 5 | **Technical density** | vague / hand-wavy | accurate and specific | dense yet effortless to read |
| 6 | **Real examples** | none, or `foo`/`bar` | real, runnable | real + expected output shown |
| 7 | **Visual with function** | decoration or none | each visual informs | the diagram *is* the explanation |
| 8 | **LLM-readability** | facts only in prose/images | stable headings, copyable | TL;DR + contract an agent lifts whole |
| 9 | **Integrity / source** | unsourced/invented claim | claims traceable | source ledger explicit |
| 10 | **Navigation / next step** | dead-ends | ends with a pointer | routes every reader onward |

## Scoring output (per page)
```markdown
### Score — <page>
| Dim | 1 Hook | 2 Intent | 3 IA | 4 Scan | 5 Density | 6 Examples | 7 Visual | 8 LLM | 9 Source | 10 Next | Avg |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| Score | 3 | 4 | 3 | 4 | 3 | 2 | 3 | 4 | 3 | 3 | 3.2 |
- Below threshold: <none | dim + why>
- Fix before done: <bullet list>
```

## The gate (definition of "done")
A page is **done** only when **all** hold:
- **No dimension scores 0.**
- **Critical dimensions ≥ 2:** #9 Integrity/source, #4 Scannability, #10 Navigation.
  A page that invents a fact or dead-ends is never done regardless of its average.
- **Overall average ≥ 2.5.**
- It passes the hard gates in [engagement-checklist.md](engagement-checklist.md)
  (strict build, no orphans, source ledger, visual QA).

Landing pages and section indexes carry the site — hold them to **average ≥ 3.5**.

## Using the score
Report the table per page at delivery (phase 9). If the editorial loop hits its
round limit and a page is still below threshold, **do not silently ship it** — mark
it *below threshold* with the exact failing dimensions and the reason (usually a
**source gap**, not a craft gap).
