import { Plugin } from "@opencode/plugin"
import { Vitrine } from "./rpc.js"
import * as specs from "./specs.js"
import * as quench from "./quenching.js"

export default Plugin.define({
  id: "quenching-vitrine",
  async setup(ctx) {
    const counters = { tools: 0, last: "" }
    const directories = new Map<string, string>()
    const harvested = new Map<string, number>()
    const hydrated = new Set<string>()

    const rpc = await ctx.rpc.register(Vitrine, {
      stats: async () => ({ ...counters }),
      touched: async (input) => {
        const { sessionID, directory } = input as { sessionID: string; directory: string }
        await harvestSession(sessionID, directory)
        const ledger = specs.ledger(sessionID)
        await absorbStorage(sessionID, ledger)
        const rows = await specs.touched(directory, ledger)
        remember(sessionID, ledger)
        return rows
      },
      search: async (input) => {
        const { directory, query, limit } = input as { directory: string; query: string; limit: number }
        return specs.search(directory, query, limit)
      },
      detail: async (input) => {
        const { directory, id } = input as { directory: string; id: number }
        return specs.detail(directory, id)
      },
      task: async (input) => {
        const { directory, id, task } = input as { directory: string; id: number; task: string }
        return specs.task(directory, id, task)
      },
      board: async (input) => {
        const { directory } = input as { directory: string }
        return specs.board(directory)
      },
      quenching: async (input) => {
        const { directory } = input as { directory: string }
        return quench.health(directory)
      },
      upgrade: async (input) => {
        const { directory } = input as { directory: string }
        const result = await quench.upgrade(directory)
        if (result.ok) specs.forget()
        return result
      },
    })

    async function absorbStorage(sessionID: string, ledger: specs.Ledger): Promise<void> {
      const stored = await ctx.storage.get(`specs.${sessionID}`).catch(() => undefined) as
        | Record<string, { kind?: specs.Kind; at?: number }>
        | undefined
      if (!stored) return
      const entries: [number, { kind: specs.Kind; at: number }][] = []
      for (const [id, value] of Object.entries(stored)) {
        if (value && typeof value === "object") {
          entries.push([Number(id), {
            kind: (value.kind ?? "read") as specs.Kind,
            at: Number(value.at ?? Date.now()),
          }])
        }
      }
      specs.absorb(ledger, entries)
    }

    async function ledgerFor(sessionID: string): Promise<specs.Ledger> {
      const ledger = specs.ledger(sessionID)
      if (!hydrated.has(sessionID)) {
        hydrated.add(sessionID)
        await absorbStorage(sessionID, ledger)
      }
      return ledger
    }

    function remember(sessionID: string, ledger: specs.Ledger): void {
      void ctx.storage.set(`specs.${sessionID}`, Object.fromEntries(ledger)).catch(() => undefined)
    }

    async function record(sessionID: string, hits: { id: number; kind: specs.Kind }[]): Promise<void> {
      if (hits.length === 0) return
      const ledger = await ledgerFor(sessionID)
      for (const hit of hits) specs.touch(ledger, hit.id, hit.kind)
      remember(sessionID, ledger)
      await rpc.events.emit("changed", { sessionID })
    }

    /** A conversa da sessão é a fonte da verdade: o painel varre ao abrir, sem depender de hook. */
    async function harvestSession(sessionID: string, directory: string): Promise<void> {
      const at = harvested.get(sessionID) ?? 0
      if (Date.now() - at < 5_000) return
      harvested.set(sessionID, Date.now())
      const messages = await ctx.session.context({ sessionID }).catch(() => undefined)
      if (!messages || messages.length === 0) return
      const found = specs.harvest(messages, await specs.known(directory))
      if (found.hits.length === 0) return
      const ledger = specs.ledger(sessionID)
      for (const hit of found.hits) specs.touch(ledger, hit.id, hit.kind)
      remember(sessionID, ledger)
    }

    async function directoryOf(sessionID: string): Promise<string | undefined> {
      const known = directories.get(sessionID)
      if (known) return known
      const session = await ctx.session.get({ sessionID }).catch(() => undefined)
      const directory = (session as { directory?: string } | undefined)?.directory
      if (directory) directories.set(sessionID, directory)
      return directory
    }

    // Hook: cada tool executada por qualquer sessão atualiza o painel ao vivo.
    await ctx.tool.hook("execute.after", async (event) => {
      counters.tools += 1
      counters.last = event.tool
      await rpc.events.emit("updated", { ...counters })
      if (!specs.isShell(event.tool) || event.status !== "completed") return
      const command = specs.commandOf(event.input)
      if (!command || !/\bcq\s+git\s+commit\b/.test(command)) return
      const directory = await directoryOf(event.sessionID)
      if (!directory) return
      const id = await specs.commitSpec(directory)
      if (id) await record(event.sessionID, [{ id, kind: "commit" }])
    })

    // Hook: o ledger nasce do comando `cq` já no instante em que ele roda.
    await ctx.tool.hook("execute.before", async (event) => {
      if (!specs.isShell(event.tool)) return
      const command = specs.commandOf(event.input)
      if (!command) return
      const parsed = specs.parse(command)
      await record(event.sessionID, parsed.hits)
    })

    // Hook: o que o humano escreve na sessão também é evidência.
    await ctx.session.hook("prompt", async (event) => {
      const text = event.prompt?.text
      if (!text) return
      // Fora do caminho do envio: o painel atualiza quando a varredura termina.
      void (async () => {
        const directory = await directoryOf(event.sessionID)
        if (!directory) return
        const ids = specs.mentions(text, await specs.known(directory))
        await record(event.sessionID, ids.map((id) => ({ id, kind: "mention" as const })))
      })().catch(() => undefined)
    })

    // Tool: o agente passa a poder chamar `vitrine_saudacao`.
    await ctx.tool.transform((editor) => {
      editor.add({
        name: "vitrine_saudacao",
        description: "Saudação de demonstração do plugin quenching-vitrine, com o total de tools executadas.",
        input: { type: "object", properties: { nome: { type: "string" } }, required: ["nome"] },
        execute: async (input) => ({
          content: `Olá, ${(input as { nome: string }).nome}! ${counters.tools} tools rodaram desde que o plugin subiu.`,
        }),
      })
    })
  },
})
