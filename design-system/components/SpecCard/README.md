# SpecCard

The board's unit: one spec, its signal and nothing it does not need.

Age fades with recency, in `ink` and weight, never in `accent`: `.fresh-1` for today and yesterday, `.fresh-2` up to 3 days, `.fresh-3` up to 7 days, and past that the plain `muted` of low importance.

A captured card offers `Mover para a fila` as a neutral `.small` button, because it is a choice and nothing is waiting. In the queue, `Aprovar` appears only once the spec is developed; it stays `button.heat`, because then it waits for the human.

The priority and the owner open a menu, and the target opens a date field; the same controls appear on the ranking and in the spec detail. A read-only server shows them as text. A target shows working days up to 10, then weeks; 3 working days or fewer is a filled `.soon`, and overdue is `.late`. An owner is a `.av` badge, whose hue only tells people apart; a card without one offers `Atribuir` in any lane. `.is-mine` rings the cards of the person identified by the git email. `data-tip` is the balloon for exact values.

Order: id, priority, age; the title, clamped at three lines; then only what this card has (progress and verdict, a blocked reason, or `Aprovar`); then owner and subject. Show a tag only when it tells cards apart in the current view; a tag on most of them belongs in the toolbar. Show `.stage` on the card only when grouping by something else. The title's stretched link opens the drawer, and quick actions appear on hover, focus and `.is-cursor`, always on touch. Compact density drops the reason and the footer. Source: `card`, `cardMeta`. Refinement R7, defect D2.

An epic or feature card names its kind with a `.tag` beside the owner and carries `data-kind`; a user story has no tag. The progress counts direct parts: features on an epic, user stories or tasks on a feature, tasks on a user story.
