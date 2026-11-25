/** @jsxImportSource @opentui/solid */
import { Plugin } from "@opencode/plugin/tui"
import { createSignal, onCleanup } from "solid-js"
import { Cache, type BandView } from "./rpc.ts"

const REFRESH_MS = 30_000

// The same band as the Desktop pill, in the composer's top slot: one line of text, coloured by tone.
export default Plugin.define({
  id: "quenching-cache",
  setup(ctx) {
    const rpc = ctx.client.rpc(Cache)
    const theme = ctx.theme as unknown as Record<string, unknown>
    const colour = (tone: string): unknown => (tone === "danger" ? theme.error : tone === "warning" ? theme.warning : tone === "success" ? theme.success : theme.textMuted)

    return ctx.ui.slot({
      append: "session.composer.top",
      render: (input) => {
        const sessionID = input.sessionID
        const directory = ctx.location?.directory ?? (ctx.data.session.get(sessionID) as { location?: { directory?: string } } | undefined)?.location?.directory ?? ""
        const [band, setBand] = createSignal<BandView>()
        const refresh = () => {
          if (!directory) return
          void rpc.state({ sessionID, directory }).then((next) => setBand(next as BandView)).catch(() => undefined)
        }
        refresh()
        const tick = setInterval(refresh, REFRESH_MS)
        const off = rpc.events.on("changed", (event) => {
          if ((event.data as { sessionID?: string }).sessionID === sessionID) refresh()
        })
        onCleanup(() => {
          clearInterval(tick)
          off()
        })
        return (
          <>
            {band() && !band()!.hidden ? <text fg={colour(band()!.tone) as never}>{band()!.text}</text> : null}
          </>
        )
      },
    })
  },
})
