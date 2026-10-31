# From today to the target

The gap between the portal at `main@ba5e2e664` and the `Screen*` cards, read off the running portal at 1440×900 and 390×844, in both themes, over a real store. Line numbers point at `plugins/quenching/assets/portal/`.

| At 1440×900 | Today | Target |
| --- | --- | --- |
| Height above the first card | about 337px | 168px |
| Lanes in view, of seven | 5 | 6, the seventh collapsed |
| Height of a card with a three-line title | about 218px | about 122px |
| Cards in view per lane | 2 | 5 to 6 |

## Defects

Real bugs, independent of any visual decision. Each one reproduces today.

| Id | Defect | Where | Fix |
| --- | --- | --- | --- |
| D1 | **Help never opens.** Two elements have `id="help"`, so `$("#help")` returns the button; the help content is injected into the top bar and the console throws `showModal is not a function` and `close is not a function`. | `index.html:29`, `index.html:68`, `app.js:710`, `app.js:752` | Give the dialog its own id. |
| D2 | **The card's progress bar never renders.** `cardMeta` passes the spec where `progress` expects its `progress` object, so `p.total` is undefined and no card shows tasks. | `app.js:776`, `app.js:778` | `progress(s.progress)`. |
| D3 | **The palette input is cut to about 270px.** It has no `type`, so the width rule misses it, the placeholder is clipped and the focus ring wraps a fragment of the field. | `index.html:63`, `app.css:101` | `type="search"`. |
| D4 | **Underscores turn identifiers into italics.** The inline Markdown rule matches inside words, so `a_b_c` loses its underscores and a path can italicize half a paragraph. | `app.js:1035` | Require a non-word character on both sides of `_`. |
| D5 | **The read-only banner mixes languages.** It prints the server's English reason inside a Portuguese sentence. | `app.js:388` | Map the known reason to a fixed sentence. |
| D6 | **The undated Gantt list is unstyled.** With no dates in a store the whole view becomes browser-default blue links with raw stage keys. | `app.js:1542`, `app.css:509` | Render it as `.table-wrap`, as in `ScreenGantt`. |
| D7 | **Wave titles repeat themselves**, as in “Onda 1 · 1. Onda 1 — …”, and an untitled wave reads “Onda 5 · 5. 3”. | `app.js:1381` | Strip a leading number and wave word from the title. |
| D8 | **A blocked reason has no limit.** One spec fills the viewport in Decidir with a wall of text. | `app.js:1301`, `.why` in `app.css` | Clamp to two lines, with the full text in the spec. |
| D9 | **Sessions on one checkout are indistinguishable.** Every lane reads the same label. | `app.js:1552` | Add the worktree folder and a short session id, as `ScreenSessions` does. |
| D10 | **Controls fail 1.4.11.** Inputs and quiet buttons are outlined in `--line`, 1.42:1. | `app.css:103`, `app.css:106` | `control-line`. |
| D11 | **Disabled primary is only a faded orange**, which reads as a hover state. | `app.css:117` | The neutral disabled style in `bundle.css`. |

## Refinements

Each one has a target card. Work them by slice, below.

| Id | Refinement | Target |
| --- | --- | --- |
| R1 | **Fixed shell.** One 48px top bar with everything in it; the shell stays and the content scrolls. Today the bar wraps to two rows at 1440px and the toolbar scrolls away. | `TopBar`, `ScreenBoard` |
| R2 | **Pulse as a strip.** Six counts in 34px instead of 80px, `esperando você` first, each one a link to its filter. | `Pulse` |
| R3 | **Heat rule.** The accent leaves nav, pressed toggles, selected rows, links and rings. | README, The one rule |
| R4 | **One language.** Every stage, status, run and session state in pt-BR; `etapa` everywhere. The store's keys stay in the data. | `Tags`, `Stages` |
| R5 | **Board toolbar in one row.** Selects carry their label inline; quick filters sit beside them; filter chips join the row only when active. | `BoardToolbar` |
| R6 | **Lanes, not boxes.** A stage-coloured rule on top, own scroll, sticky head; `arquivada` collapsed by default. The stripe and the box around each column go. | `Lane` |
| R7 | **Card anatomy.** Id and priority on one line, title clamped at three, then only the signal that card has: progress, verdict, blocked reason or `Aprovar`. Tags show only when they tell cards apart. Open and copy appear on hover and focus, and always on touch. | `SpecCard` |
| R8 | **Ranking as a real table.** Id, stage, priority, tasks and age as columns; arrows appear on hover and on the cursor row. | `RankTable` |
| R9 | **Decide as one queue.** The approval group first, because it is the only one solved here; a summary line instead of a repeated reason; empty groups fold to a line; approval arms in place with `a` and `Enter`. | `DecisionRow`, `ScreenDecide` |
| R10 | **Detail as reading.** Sections are a reading column without panels; contents on the left, tasks and records on the right; actions in one row. The drawer is the same builder. | `SpecHeader`, `ScreenSpecPage`, `ScreenSpecDrawer` |
| R11 | **Epics as programmes.** A meter by wave replaces the ring, finished waves fold to a narrow column, members are one tight line each, and the next step is a strip. | `EpicPanel` |
| R12 | **Gantt.** Arrows into the bar's start, a legend in pt-BR, today in heat. | `GanttChart` |
| R13 | **Sessions.** The waiting question comes first; lanes are one row with their subagents beneath. | `SessionLane` |
| R14 | **Chat.** The log above, the form pinned below, the ceiling and the cost in view. | `ChatPanel` |
| R15 | **Palette.** Group headings instead of a label per row; selection in `surface-3`, not a solid accent bar. | `Palette` |
| R16 | **Feedback without a coloured edge.** Toasts carry an icon and a word; banners carry an icon and a fill. | `Toast`, `Banner` |
| R17 | **Icon set.** Authored inline SVG replaces `◐`, `?`, `×`, `▲` and `▼`. | `Icons` |
| R18 | **Browser surfaces.** Selection, caret, scrollbars, underline offset, focus width and control accent all come from the palette. | `bundle.css`, base |
| R19 | **Phone.** A one-row bottom bar; the board reachable in the first viewport, where today half of it is chrome. | `ScreenMobileBoard`, `ScreenMobileDecide` |

## Contract changes

These touch `docs/standards/architecture/specs-portal.md` and need a human yes before they ship.

| Id | Change | Why it matters |
| --- | --- | --- |
| C1 | UX patterns name “a hero counter” and “state pills”, and the epics view names “a progress ring”. The target replaces them with the pulse cell, the stage mark and the wave meter. | The text must follow. No route or data changes. |
| C2 | `confirm()` at `app.js:1245` gives way to an armed row. | Same write, same route; the gesture changes. |
| C3 | Scroll moves from the window to `main` and `.col-body`. `captureView` and `restoreView` (`app.js:1774`, `app.js:1782`) save `window.scrollY`, so they must save each scroller or a poll will jump. | Without this, “scroll and focus survive a poll” breaks. |
| C4 | `tokens.css` as compiled has no `prefers-color-scheme` block. The `auto` theme needs the dark values a third time in `app.css`, generated from `tokens.json`. | `build.py --check` already counts that copy: 44 KB of the 48 KB budget. |
| C5 | Icons add about 1.0 KB to `app.js`, which stands at 114.9 of 120 KB. | Fits, with little room left. The slices should remove code as they go. |

## Suggested slices

Each slice is one spec and leaves the portal shippable. Portal changes regenerate every distribution and pass `bash scripts/verify_repo.sh`, as the standard says.

1. **Defects:** D1 to D9. No visual change; nothing here waits on a design decision.
2. **Foundations:** generate `app.css` from `tokens.css` and `bundle.css`, with a `--check` in the gate as eclume does. D10, D11, R3, R4, R17, R18.
3. **Shell and board:** R1, R2, R5, R6, R7, C3.
4. **Decide and detail:** R9, R10, C2.
5. **Planning views:** R8, R11, R12, C1.
6. **Live views, overlays and phone:** R13, R14, R15, R16, R19.
