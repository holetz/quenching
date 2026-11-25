import { createSignal } from "solid-js"
import { Command, ComposerPill, Plugin, type ComposerPillRow } from "@opencode/plugin/gui"
import { Quota, type QuotaView } from "./rpc.ts"

// The window asks at most once a minute; the server reuses a reply for `shared.quota.intervalSeconds`.
const REFRESH_MS = 60_000

const LABELS = {
  pt: { detail: "Detalhe", refresh: "Atualizar", hide: "Esconder" },
  en: { detail: "Detail", refresh: "Refresh", hide: "Hide" },
} as const

const ICON = { success: "circle-check", warning: "warning", danger: "circle-exclamation", "": "status" } as const

export default Plugin.define({
  setup(ctx) {
    const [views, setViews] = createSignal<Record<string, QuotaView>>({})
    const watched = new Set<string>()
    const rpc = () => ctx.client.rpc(Quota)
    const keep = (directory: string) => (view: unknown) => setViews((all) => ({ ...all, [directory]: view as QuotaView }))

    const watch = (directory: string) => {
      if (watched.has(directory)) return
      watched.add(directory)
      const tick = () => void rpc().state({ directory }).then(keep(directory)).catch(() => undefined)
      tick()
      setInterval(tick, REFRESH_MS)
      rpc().events.on("changed", tick)
    }

    const detail = (directory: string) => {
      void rpc().state({ directory }).then((view) => {
        const v = view as QuotaView
        keep(directory)(v)
        ctx.toast.show({ title: v.title, description: v.detail, variant: v.tone === "danger" ? "error" : "default" })
      }).catch(() => undefined)
    }
    const refresh = (directory: string) => void rpc().refresh({ directory }).then(keep(directory)).catch(() => undefined)
    const toggle = (directory: string) => void rpc().toggle({ directory }).then(keep(directory)).catch(() => undefined)

    // Beside the cache band (`order: -10`), never in its place.
    ctx.add(ComposerPill, {
      id: "quota",
      order: -5,
      show: (input) => {
        if (input.session.pending) return undefined
        const directory = input.session.directory
        watch(directory)
        const view = views()[directory]
        if (!view || view.hidden) return undefined
        const label = LABELS[view.lang === "pt" ? "pt" : "en"]
        const rows: ComposerPillRow[] = [
          { id: "detail", label: label.detail, icon: "window-analytics", run: () => detail(directory) },
          { id: "refresh", label: label.refresh, icon: "refresh", run: () => refresh(directory) },
          { id: "hide", label: label.hide, icon: "outline-eye-slash", run: () => toggle(directory) },
        ]
        return {
          label: view.text,
          icon: ICON[(view.tone as keyof typeof ICON) in ICON ? (view.tone as keyof typeof ICON) : ""],
          tone: view.tone ? (view.tone as "success" | "warning" | "danger") : undefined,
          title: "quenching-quota",
          rows,
        }
      },
    })

    // `/quenching-quota` shows the detail; `/quenching-quota toggle` hides or shows the band. Never the model.
    ctx.add(Command, () => ({
      id: "quota",
      title: "quenching-quota",
      description: "Cota da assinatura Claude: janela de 5 horas e semanal",
      keywords: "quota cota claude limite 5h semanal weekly usage quenching",
      slash: { name: "quenching-quota", arguments: true as const },
      run: (input?: string) => {
        const session = ctx.sessions.current()
        if (!session) return
        if ((input ?? "").trim() === "toggle") toggle(session.directory)
        else detail(session.directory)
      },
    }))
  },
})
