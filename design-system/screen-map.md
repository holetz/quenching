# Screen map

Every surface of the portal, its state against the target and the code that draws it. Status follows the same words the eclume map used.

| Status | Meaning |
| --- | --- |
| **exists** | The target matches what ships. |
| **change** | The surface exists and the target refines it. |
| **new** | The surface does not exist yet. |
| **remove** | The surface goes away. |
| **future** | Agreed direction, not designed yet. |

## Journeys

**Start the day.** Open the portal, read the pulse, go to `Decidir` with `g d`, clear the approvals with `j`, `k` and `a`, then send the writes with `Enviar`.

**Follow an agent.** See a session burning in the nav, open `Sessões`, read the question it asked, answer it in the terminal, and come back to the card moving on the board.

**Unblock a spec.** See the count in `bloqueadas`, follow it to the filtered board, read the reason on the card, open the drawer, copy the command.

**Plan the next wave.** Open `Épicos`, read the health and the next step, reorder in `Ranking`, check the dates in `Gantt`.

**Capture an idea.** Press `Capturar` from anywhere, write a title and a problem, land on the new spec.

## Inventory

| Screen | Route | Status | Card | Source |
| --- | --- | --- | --- | --- |
| Board by stage | `#/board` | change | `ScreenBoard` | `viewBoard`, `column`, `card`, `toolbar` |
| Board by priority, compact | `#/board?group=priority` | change | `ScreenBoardGrouped` | `grouped`, `toolbar` |
| Ranking | `#/list` | change | `ScreenRanking` | `viewList` |
| Decide | `#/human` | change | `ScreenDecide` | `viewHuman`, `triageRow` |
| Decide, empty | `#/human` | change | `ScreenDecideEmpty` | `viewHuman`, `emptyState` |
| Epics | `#/epics` | change | `ScreenEpics` | `viewEpics`, `epicItem`, `nextStep` |
| Gantt | `#/gantt` | change | `ScreenGantt` | `viewGantt` |
| Sessions | `#/sessions` | change | `ScreenSessions` | `viewSessions`, `radar`, `subLane` |
| Chat | `#/chat` | change | `ScreenChat` | `viewChat`, `chatLog` |
| Spec, full page | `#/spec/<id>` | change | `ScreenSpecPage` | `viewDetail`, `specDetail` |
| Spec, drawer | over any view | change | `ScreenSpecDrawer` | `openDrawer`, `specDetail` |
| Search results | `#/search?q=` | change | `ScreenSearch` | `viewSearch` |
| Command palette | `Ctrl K` | change | `ScreenPalette` | `paletteItems`, `renderPalette` |
| Help and shortcuts | `?` | change, broken today (D1) | `ScreenHelp` | `openHelp` |
| Capture | `Capturar` | change | `ScreenCapture` | `captureDialog`, `openDialog` |
| Edit section, register a discovery | from a spec | change | `Dialog` | `sectionDialog`, `discoveryDialog` |
| Notifications | status bar | change | `Events` | `paintEvents` |
| Central server | `cq portal serve` | change | `ScreenCentral` | `paintProjects` |
| Read-only server | `--read-only` | change | `ScreenReadOnly` | `loadConfig` |
| Connection lost | any | change | `ScreenOffline` | `paintConn` |
| First paint | any | change | `ScreenLoading` | `loadingView` |
| Phone: board | any route | change | `ScreenMobileBoard` | responsive rules |
| Phone: decide | any route | change | `ScreenMobileDecide` | responsive rules |

No screen is new or removed: the target refines the portal 2.0 surface as it stands.

## Open questions

Decisions the target took on its own, and that a person may want to reverse.

1. **Ring or meter.** The epic ring gives way to a meter by wave, which shows where the work is rather than only how much. The standard names the ring (C1).
2. **Pills or marks.** Stages become a square and a word, and the tinted chip survives only in a spec's head. Lower noise, less colour per screen.
3. **`arquivada` collapsed by default.** It frees a lane; it also hides a stage until asked.
4. **Interface language.** The portal is hard-coded pt-BR in a project whose artifacts are English. This target keeps pt-BR; strings are not extracted for translation.
5. **The `.mark` gradient.** It stays because it is the only brand element that exists. A flat mark would hold better at favicon size, and the favicon today draws a count, not the mark.
