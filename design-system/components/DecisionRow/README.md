# DecisionRow

One decision per row, with the action at the end of the line.

The first line is id and title; the second is the spec's summary or, for a blocked spec, its reason in `bad`, clamped at two lines (D8). `Aprovar` arms the row (`.is-armed`) instead of opening `confirm()`: the line states what will be written, `Confirmar aprovação` is the view's primary, `Esc` disarms. Source: `triageRow`. Refinement R9, contract C2.
