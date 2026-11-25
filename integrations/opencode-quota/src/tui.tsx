/** @jsxImportSource @opentui/solid */
import { Plugin } from "@opencode/plugin/tui"
import { createSignal, onCleanup } from "solid-js"
import { Quota, type QuotaView } from "./rpc.ts"

const REFRESH_MS = 60_000

// The same band as the Desktop pill, in the prompt footer's status slot (the cache band sits in
// `session.composer.top`), plus `/quenching-quota` for the detail.
export default Plugin.define({
  id: "quenching-quota",
  setup(ctx) {
    const rpc = ctx.client.rpc(Quota)
    const theme = ctx.theme as unknown as Record<string, unknown>
    const colour = (tone: string): unknown => (tone === "danger" ? theme.error : tone === "warning" ? theme.warning : tone === "success" ? theme.success : theme.textMuted)
    const directory = () => ctx.location?.directory ?? process.cwd()

    ctx.keymap.layer(() => ({
      commands: [{
        id: "quenching-quota",
        title: "quenching-quota",
        description: "Cota da assinatura Claude: janela de 5 horas e semanal",
        palette: true,
        slash: { name: "quenching-quota", arguments: true },
        run: (input?: string) => {
          const ask = (input ?? "").trim() === "toggle" ? rpc.toggle({ directory: directory() }) : rpc.state({ directory: directory() })
          void ask.then((view) => {
            const v = view as QuotaView
            ctx.ui.toast.show({ title: v.title, message: v.detail, variant: v.tone === "danger" ? "error" : v.tone === "warning" ? "warning" : "info" })
          }).catch(() => undefined)
        },
      }],
    }))

    return ctx.ui.slot({
      append: "prompt.footer.status",
      render: () => {
        const [view, setView] = createSignal<QuotaView>()
        const refresh = () => void rpc.state({ directory: directory() }).then((next) => setView(next as QuotaView)).catch(() => undefined)
        refresh()
        const tick = setInterval(refresh, REFRESH_MS)
        const off = rpc.events.on("changed", refresh)
        onCleanup(() => {
          clearInterval(tick)
          off()
        })
        return <>{view() && !view()!.hidden ? <text fg={colour(view()!.tone) as never}>{view()!.text}</text> : null}</>
      },
    })
  },
})
