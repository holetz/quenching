# RankList

The global order of open specs, one short card per row, so a long list still reads as rows.

Most of the width is the title and its status line: id, priority, title and kind, then subject, tags and complexity, and the blocker, the last run or the summary. A tight block on the right holds stage, target and age over progress, owner and `Aprovar`, which appears only on what waits for the human. Priority, target and owner open the same menus as the card, and `.is-mine` marks the user's rows.

The list follows the hierarchy. The top level holds epics and whatever has no parent; a parent folds, and its parts sit indented below in their own order, numbered `1.1`. A folded parent shows its blocker on the status line. An epic has features, a feature has user stories or tasks, so `.depth-1` and `.depth-2` are enough; tasks are not rows.

Reordering is drag on the row or the arrows beside the number, one commit per move, among siblings only: a parent moves with its parts, and a part does not leave its parent here. With `--read-only`, both go. Arrows appear on hover, focus and the cursor row. On a phone the block wraps under the title. Source: `viewList`. Refinement R8.
