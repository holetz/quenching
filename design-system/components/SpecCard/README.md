# SpecCard

The board's unit: one spec, its signal and nothing it does not need.

Order: id, priority, age; the title, clamped at three lines; then only what this card has (progress and verdict, a blocked reason, or `Aprovar`); then owner and subject. Show a tag only when it tells cards apart in the current view; a tag on most of them belongs in the toolbar. Show `.stage` on the card only when grouping by something else. The title's stretched link opens the drawer, and quick actions appear on hover, focus and `.is-cursor`, always on touch. Compact density drops the reason and the footer. Source: `card`, `cardMeta`. Refinement R7, defect D2.
