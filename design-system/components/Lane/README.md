# Lane

A column of the board: rule, name, count, its own scroll.

The rule takes the stage colour through `[data-stage]`; a grouping other than stage has no rule colour. A lane scrolls by itself with its head fixed. `.is-collapsed` turns it into a 40px strip with `aria-expanded="false"`, and `arquivada` starts that way. An empty lane says `nada aqui`, or disappears with `ocultar vazias`. Refinement R6.
