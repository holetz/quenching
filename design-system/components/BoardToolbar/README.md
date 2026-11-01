# BoardToolbar

One row of board controls: group, sort, filters, quick toggles, density, views.

The `épicos` and `features` checkboxes show or hide those cards on the board. The epics view reuses the bar with its own group, sort and quick options, without those checkboxes and `ocultar vazias`; `compacto` there leaves only the head of each epic.

State lives in the URL (`group`, `sort`, `q`, repeated `f=key:value`). Active filters appear as `.fchip` with a remove icon, and `limpar tudo` appears only then. Refinement R5.
