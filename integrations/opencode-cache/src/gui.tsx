import { createSignal } from "solid-js"
import { Command, ComposerPill, Plugin, type ComposerPillRow } from "@opencode/plugin/gui"
import { Cache, type BandView, type Reply } from "./rpc.ts"

const REFRESH_MS = 30_000

const ICON = { green: "circle-check", yellow: "warning", orange: "warning", red: "circle-exclamation", none: "status" } as const
type Light = keyof typeof ICON

export default Plugin.define({
  setup(ctx) {
    // One band per session, filled by the server and refreshed on its `changed` events and a slow tick.
    const [bands, setBands] = createSignal<Record<string, BandView>>({})
    const asked = new Set<string>()
    const rpc = () => ctx.client.rpc(Cache)

    const refresh = (sessionID: string, directory: string) => {
      void rpc().state({ sessionID, directory }).then((band) => {
        setBands((all) => ({ ...all, [sessionID]: band as BandView }))
      }).catch(() => undefined)
    }

    const watch = (sessionID: string, directory: string) => {
      if (asked.has(sessionID)) return
      asked.add(sessionID)
      refresh(sessionID, directory)
      setInterval(() => refresh(sessionID, directory), REFRESH_MS)
      rpc().events.on("changed", (event) => {
        if ((event as unknown as { sessionID: string }).sessionID === sessionID) refresh(sessionID, directory)
      })
    }

    // The expiry toast: once per reply, from the server's timer or from sending on a gone cache.
    rpc().events.on("expired", (event) => {
      const { text } = event as unknown as { sessionID: string; text: string }
      ctx.toast.show({ title: "quenching-cache", description: text, variant: "default" })
    })

    const say = (reply: Reply, title: string) =>
      ctx.toast.show({ title, description: reply.text, variant: reply.ok ? "success" : "error" })

    const act = {
      handoff: (sessionID: string, directory: string, focus = "") => {
        ctx.toast.show({ title: "quenching-cache", description: "handoff…" })
        void rpc().handoff({ sessionID, directory, focus }).then((r) => say(r as Reply, "handoff")).catch((cause) => say({ ok: false, text: String(cause), line: "" }, "handoff"))
      },
      stats: (sessionID: string, directory: string) => {
        void rpc().stats({ sessionID, directory }).then((r) => say(r as Reply, "stats")).catch((cause) => say({ ok: false, text: String(cause), line: "" }, "stats"))
      },
      toggle: (sessionID: string, directory: string) => {
        void rpc().toggle({ sessionID, directory }).then((band) => {
          setBands((all) => ({ ...all, [sessionID]: band as BandView }))
        }).catch(() => undefined)
      },
    }

    ctx.add(ComposerPill, {
      id: "cache",
      order: -10,
      show: (input) => {
        const sessionID = input.session.id
        const directory = input.session.directory
        if (input.session.pending) return undefined
        watch(sessionID, directory)
        const band = bands()[sessionID]
        if (!band || band.hidden) return undefined
        const rows: ComposerPillRow[] = [
          { id: "handoff", label: "Handoff", icon: "new-session", run: () => act.handoff(sessionID, directory) },
          { id: "stats", label: "Stats", icon: "window-analytics", run: () => act.stats(sessionID, directory) },
          { id: "hide", label: "Hide", icon: "outline-eye-slash", run: () => act.toggle(sessionID, directory) },
        ]
        return {
          label: band.text,
          icon: ICON[(band.light as Light) in ICON ? (band.light as Light) : "none"],
          tone: band.tone ? (band.tone as "success" | "warning" | "danger") : undefined,
          title: "quenching-cache",
          rows,
        }
      },
    })

    // `/quenching-cache`, `/quenching-cache handoff [focus]`, `/quenching-cache stats`: the Claude Code plugin's command.
    ctx.add(Command, () => ({
      id: "cache",
      title: "quenching-cache",
      description: "Esconder ou mostrar a faixa do cache; handoff e stats",
      keywords: "cache handoff stats quenching prompt cache",
      slash: { name: "quenching-cache", arguments: true as const },
      run: (input?: string) => {
        const session = ctx.sessions.current()
        if (!session) return
        const [verb = "", ...rest] = (input ?? "").trim().split(/\s+/)
        if (verb === "handoff") act.handoff(session.id, session.directory, rest.join(" "))
        else if (verb === "stats") act.stats(session.id, session.directory)
        else act.toggle(session.id, session.directory)
      },
    }))
  },
})
