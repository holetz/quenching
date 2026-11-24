import { Plugin } from "@opencode/plugin"
import { readFile } from "node:fs/promises"
import { join } from "node:path"
import { Cache, type BandView } from "./rpc.ts"
import { cqJson, cqRun } from "./cq.ts"
import { DEFAULTS, hostPrice, priceOf, settingsFromConfig, statsText } from "./core/logic.ts"
import type { HostCost, PriceSource, Settings } from "./core/logic.ts"
import { WORDS, langOf } from "./core/i18n.ts"
import type { Words } from "./core/i18n.ts"
import type { Rec } from "./core/types.ts"
import { runHandoff } from "./handoff.ts"
import { fileURLToPath } from "node:url"
import { mkdir, writeFile } from "node:fs/promises"
import { dirname } from "node:path"
import { applyStep, clearReset, expiresIn, explicitCache, normModel, reset, view } from "./track.ts"
import type { ModelRef } from "./track.ts"

type Session = { rec: Rec | null; hidden: boolean; model?: ModelRef }
type Checkout = { settings: Settings; words: Words; at: number }

const KEEP = "quenching-cache"
const HAIKU = { id: "claude-haiku-5-5", providerID: "anthropic" }
const CHECKOUT_TTL_MS = 5 * 60_000

export default Plugin.define({
  id: "quenching-cache",
  async setup(ctx) {
    const sessions = new Map<string, Session>()
    const directories = new Map<string, string>()
    const checkouts = new Map<string, Checkout>()
    const timers = new Map<string, ReturnType<typeof setTimeout>>()
    const hostCosts = new Map<string, HostCost[]>()
    const stop = new AbortController()

    const rpc = await ctx.rpc.register(Cache, {
      state: async (input) => {
        const { sessionID, directory } = input as { sessionID: string; directory: string }
        directories.set(sessionID, directory)
        return await bandOf(sessionID, directory)
      },
      toggle: async (input) => {
        const { sessionID, directory } = input as { sessionID: string; directory: string }
        const session = await sessionOf(sessionID)
        session.hidden = !session.hidden
        remember(sessionID, session)
        return await bandOf(sessionID, directory)
      },
      stats: async (input) => {
        const { sessionID, directory } = input as { sessionID: string; directory: string }
        const { words } = await checkoutOf(directory)
        const base = ["components", "session", "cache", "--harness", "opencode", "--usd"]
        const [chat, project] = await Promise.all([
          cqJson<unknown>(directory, [...base, "--session", sessionID]),
          cqJson<unknown>(directory, [...base, "--directory", directory]),
        ])
        const text = statsText(chat ? JSON.stringify(chat) : null, project ? JSON.stringify(project) : null, words)
        return { ok: text !== null, text: text ?? words.statsNone, line: "" }
      },
      handoff: async (input) => {
        const { sessionID, directory, focus } = input as { sessionID: string; directory: string; focus: string }
        const { words } = await checkoutOf(directory)
        const session = await sessionOf(sessionID)
        const core = (name: string) => readFile(fileURLToPath(new URL(`./core/${name}`, import.meta.url)), "utf8")
        const band = await bandOf(sessionID, directory)
        return runHandoff({
          sessionID, directory, focus, words, now: Date.now(),
          context: () => ctx.session.context({ sessionID }) as unknown as Promise<unknown[]>,
          generate: async (prompt) => (await ctx.experimental.generate.text({ prompt, model: HAIKU as never })).text,
          cq: async (args) => {
            const run = await cqRun(directory, args, 120_000).catch(() => undefined)
            return run && run.code !== -1 ? { code: run.code, stdout: run.stdout } : null
          },
          writeFile: async (path, text) => { await mkdir(dirname(path), { recursive: true }); await writeFile(path, text, "utf8") },
          openSession: async (line) => {
            const created = await ctx.session.create({ location: { directory } as never })
            await ctx.session.prompt({ sessionID: (created as { id: string }).id as never, text: line })
          },
          template: await core("handoff-template.md"),
          preamble: await core("handoff-brief.md"),
          numbers: { tokens: session.rec?.prefix, window: session.rec?.window, model: session.rec?.model, bar: band.text },
        })
      },
    })

    function remember(sessionID: string, session: Session): void {
      void ctx.storage.set(`${KEEP}.${sessionID}`, { rec: session.rec, hidden: session.hidden, model: session.model ?? null } as never).catch(() => undefined)
    }

    async function sessionOf(sessionID: string): Promise<Session> {
      const known = sessions.get(sessionID)
      if (known) return known
      const stored = (await ctx.storage.get(`${KEEP}.${sessionID}`).catch(() => undefined)) as
        | { rec?: Rec | null; hidden?: boolean; model?: ModelRef | null }
        | undefined
      const session: Session = { rec: stored?.rec ?? null, hidden: stored?.hidden === true, model: stored?.model ?? undefined }
      sessions.set(sessionID, session)
      return session
    }

    /** The checkout's words and `shared.cache` settings, read once in a while, never awaited by a hook. */
    async function checkoutOf(directory: string): Promise<Checkout> {
      const hit = checkouts.get(directory)
      if (hit && Date.now() - hit.at < CHECKOUT_TTL_MS) return hit
      const fallback: Checkout = hit ?? { settings: DEFAULTS, words: WORDS.en, at: Date.now() }
      const fresh = await (async () => {
        const harness = await readFile(join(directory, "AGENTS.md"), "utf8").catch(() => readFile(join(directory, "CLAUDE.md"), "utf8")).catch(() => undefined)
        const shown = await cqRun(directory, ["config", "show", "--effective", "--json"], 20_000).catch(() => undefined)
        return {
          settings: shown && shown.code === 0 ? settingsFromConfig(shown.stdout) : fallback.settings,
          words: WORDS[langOf(harness)],
          at: Date.now(),
        }
      })()
      checkouts.set(directory, fresh)
      return fresh
    }

    function priceFor(session: Session): PriceSource {
      const rows = session.model ? hostCosts.get(`${session.model.providerID}/${session.model.id}`) : undefined
      const host = hostPrice(rows)
      return (model, prefix) => priceOf(normModel(model), prefix) ?? host(model, prefix)
    }

    async function bandOf(sessionID: string, directory: string): Promise<BandView> {
      const session = await sessionOf(sessionID)
      const { settings, words } = await checkoutOf(directory)
      const v = view(session.rec, Date.now(), settings, words, priceFor(session), !explicitCache(session.model))
      return { light: v.light, text: v.text, tone: v.tone ?? "", hidden: session.hidden, implicit: v.implicit, shouldPopup: v.shouldPopup }
    }

    function announce(sessionID: string): void {
      void Promise.resolve(rpc.events.emit("changed", { sessionID })).catch(() => undefined)
    }

    /** One timer per session, at the instant its cache runs out; the toast fires once per reply. */
    function arm(sessionID: string): void {
      const old = timers.get(sessionID)
      if (old) clearTimeout(old)
      timers.delete(sessionID)
      const session = sessions.get(sessionID)
      const left = expiresIn(session?.rec ?? null, Date.now())
      if (!session || left === null || !explicitCache(session.model)) return
      const timer = setTimeout(() => {
        timers.delete(sessionID)
        announce(sessionID)
        const directory = directories.get(sessionID)
        if (!directory || session.rec?.warned) return
        void bandOf(sessionID, directory).then((band) => {
          if (!band.shouldPopup || session.hidden || !session.rec) return
          session.rec = { ...session.rec, warned: true }
          remember(sessionID, session)
          void Promise.resolve(rpc.events.emit("expired", { sessionID, text: band.text })).catch(() => undefined)
        }).catch(() => undefined)
      }, Math.min(left + 250, 2 ** 31 - 1))
      timer.unref?.()
      timers.set(sessionID, timer)
    }

    /** Fora do caminho do serviço: o evento devolve na hora, o trabalho segue em segundo plano. */
    function detach(work: () => Promise<unknown>): void {
      void Promise.resolve().then(work).catch(() => undefined)
    }

    async function learnCost(model: ModelRef): Promise<void> {
      const key = `${model.providerID}/${model.id}`
      if (hostCosts.has(key)) return
      hostCosts.set(key, [])
      const lookup = (ctx as unknown as { model?: { get?: (ref: ModelRef) => Promise<unknown> } }).model?.get
      const info = (await lookup?.call((ctx as unknown as { model: object }).model, model).catch(() => undefined)) as
        | { cost?: { input?: number; cache?: { read?: number; write?: number }; tier?: { size?: number } }[] }
        | undefined
      const rows = (info?.cost ?? []).map((c) => ({ input: c.input ?? NaN, cacheRead: c.cache?.read ?? NaN, cacheWrite: c.cache?.write, above: c.tier?.size }))
      hostCosts.set(key, rows)
    }

    async function onEvent(event: { type: string; data: Record<string, unknown> }): Promise<void> {
      const sessionID = String(event.data.sessionID ?? "")
      if (!sessionID) return
      const session = await sessionOf(sessionID)
      if (event.type === "session.model.selected") {
        const next = event.data.model as ModelRef
        const changedModel = session.model && (session.model.id !== next.id || session.model.providerID !== next.providerID)
        session.model = { id: next.id, providerID: next.providerID }
        if (changedModel && session.rec) session.rec = reset(session.rec, "model")
        detach(() => learnCost(next))
      } else if (event.type === "session.compaction.ended") {
        if (session.rec) session.rec = reset(session.rec, "compact")
      } else if (event.type === "session.step.ended") {
        const directory = directories.get(sessionID) ?? ""
        const settings = directory ? (await checkoutOf(directory)).settings : DEFAULTS
        const tokens = event.data.tokens as { input: number; output: number; cache: { read: number; write: number } }
        const model = session.model?.id ?? session.rec?.model ?? ""
        session.rec = applyStep(session.rec ? clearReset(session.rec) : null, { tokens, native: event.data.native, at: Date.now(), model, window: session.rec?.window }, settings)
      } else return
      remember(sessionID, session)
      arm(sessionID)
      announce(sessionID)
    }

    // The loop never blocks the service: a failed subscription ends quietly and the band stays at its last state.
    detach(async () => {
      const types = ["session.step.ended", "session.compaction.ended", "session.model.selected"] as const
      for await (const event of ctx.event.subscribe({ types: [...types], signal: stop.signal })) {
        const next = event as unknown as { type: string; data: Record<string, unknown> }
        detach(() => onEvent(next))
      }
    })

    // A prompt sent on a chat whose cache is gone is the moment to say so; the window shows the toast.
    await ctx.session.hook("prompt", (event) => {
      const sessionID = event.sessionID as string
      const directory = directories.get(sessionID)
      if (!directory) return
      detach(async () => {
        const band = await bandOf(sessionID, directory)
        const session = sessions.get(sessionID)
        if (!session?.rec || session.hidden || !band.shouldPopup) return
        session.rec = { ...session.rec, warned: true }
        remember(sessionID, session)
        await rpc.events.emit("expired", { sessionID, text: band.text })
      })
    })

    return () => {
      stop.abort()
      for (const timer of timers.values()) clearTimeout(timer)
      timers.clear()
    }
  },
})
