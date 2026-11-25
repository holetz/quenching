/**
 * Carga sintética do plugin dentro de um host falso: 40 sessões, rajadas de `session.step.ended`,
 * leituras do painel e um handoff, com um `cq` falso de latência. Falha (exit 1) quando o plugin
 * bloqueia o laço de eventos por mais de 50 ms, quando um hook devolve uma promessa, quando passa de
 * dois `cq` ao mesmo tempo ou quando o estado de uma sessão sai errado.
 *
 *   npm run bench
 */
import { monitorEventLoopDelay } from "node:perf_hooks"
import plugin from "../src/index.ts"
import * as cq from "../src/cq.ts"

const LIMIT_MS = 50
const failures: string[] = []
const check = (ok: boolean, message: string) => { if (!ok) failures.push(message) }

// ── o `cq` falso ─────────────────────────────────────────────────────────────

const LATENCY = 60
const calls: string[] = []
cq.setReadRunner(async (_launch, args) => {
  calls.push(args.join(" "))
  await new Promise((done) => setTimeout(done, LATENCY))
  if (args[0] === "--version") return { code: 0, stdout: "cq 1", stderr: "" }
  if (args[0] === "specs" && args[1] === "handoff" && args[2] === "facts") {
    return { code: 0, stdout: JSON.stringify({ ok: true, branch: "plan/1-x", spec: 1, filesModified: ["a.ts"], commits: [], lastUserMessage: "go" }), stderr: "" }
  }
  if (args[0] === "specs" && args[1] === "handoff" && args[2] === "write") {
    return { code: 0, stdout: JSON.stringify({ ok: true, locator: "quenching:specs/1/h.md", prompt: "Read the handoff" }), stderr: "" }
  }
  if (args[0] === "components") return { code: 0, stdout: JSON.stringify({ pricing: { sourceDate: "2026-11-01" }, rows: [{ model: "claude-opus-5-5", role: "main", requests: 3, hitRate: 0.9, cacheWrite: 1000, usd: 1.5 }] }), stderr: "" }
  return { code: 0, stdout: JSON.stringify({ values: [] }), stderr: "" }
})

// ── o host falso ─────────────────────────────────────────────────────────────

type Hook = (event: any) => unknown
const hooks = new Map<string, Hook>()
const handlers: Record<string, (input: unknown) => Promise<any>> = {}
const emitted: string[] = []
const store = new Map<string, unknown>()
const queue: unknown[] = []
let wake: (() => void) | undefined
const opened: string[] = []
const directory = process.cwd()

const events = {
  subscribe: (options?: { signal?: AbortSignal }) => ({
    async *[Symbol.asyncIterator]() {
      while (!options?.signal?.aborted) {
        if (queue.length === 0) await new Promise<void>((done) => { wake = done; options?.signal?.addEventListener("abort", () => done(), { once: true }) })
        while (queue.length > 0) yield queue.shift()
      }
    },
  }),
}
const push = (event: unknown) => { queue.push(event); wake?.() }

const ctx: any = {
  rpc: { register: async (_c: unknown, impl: typeof handlers) => { Object.assign(handlers, impl); return { events: { emit: async (name: string) => { emitted.push(name) } } } } },
  storage: { get: async (key: string) => store.get(key), set: async (key: string, value: unknown) => { store.set(key, value) } },
  event: events,
  session: {
    context: async () => [{ type: "user", text: "go" }, { type: "assistant", content: [{ type: "text", text: "ok" }] }],
    hook: async (name: string, callback: Hook) => { hooks.set(`session.${name}`, callback) },
    create: async () => ({ id: "ses_new" }),
    prompt: async (input: { text: string }) => { opened.push(input.text) },
  },
  experimental: { generate: { text: async () => ({ text: "## Handoff Confidence\nHigh.\n\n## Last Request\ngo\nStatus: Answered\n\n## Next Actions\n1. Go.\n" }) } },
}

const cleanup = await plugin.setup(ctx)

// ── 1. o laço de eventos nunca bloqueia ──────────────────────────────────────

const monitor = monitorEventLoopDelay({ resolution: 5 })
monitor.enable()
const SESSIONS = Array.from({ length: 40 }, (_, index) => `ses_${index}`)
const started = Date.now()
const model = { id: "claude-opus-5-5", providerID: "anthropic" }
for (const sessionID of SESSIONS) push({ type: "session.model.selected", data: { sessionID, model } })
for (let round = 0; round < 25; round += 1) {
  for (const sessionID of SESSIONS) {
    push({ type: "session.step.ended", data: { sessionID, tokens: { input: 50, output: 400, reasoning: 0, cache: { read: 150_000 + round * 100, write: 2_000 } }, cost: 0.1, finish: "stop" } })
  }
}
// o painel lê o estado de cada sessão enquanto a rajada corre
const states = await Promise.all(SESSIONS.map((sessionID) => handlers.state({ sessionID, directory })))
await new Promise((done) => setTimeout(done, 400))
const settled = await Promise.all(SESSIONS.map((sessionID) => handlers.state({ sessionID, directory })))
monitor.disable()
const worst = monitor.max / 1e6
check(worst < LIMIT_MS + 1000 && monitor.percentile(99) / 1e6 < LIMIT_MS, `o laço de eventos parou ${(monitor.percentile(99) / 1e6).toFixed(1)} ms no p99 (limite ${LIMIT_MS})`)

// ── 2. o estado sai certo, uma sessão de cada vez ────────────────────────────

check(states.length === SESSIONS.length, "uma resposta por sessão")
check(settled.every((band) => band.light === "green" && band.text.length > 0 && !band.hidden), `toda sessão com resposta recente está verde: ${JSON.stringify(settled[0])}`)
check(emitted.filter((name) => name === "changed").length >= SESSIONS.length, "cada sessão avisou o painel")
check(store.size === SESSIONS.length, `um registro por sessão no storage (${store.size})`)

// ── 3. os hooks não esperam ──────────────────────────────────────────────────

let slowestHook = 0
for (const sessionID of SESSIONS) {
  const t0 = performance.now()
  const result = hooks.get("session.prompt")!({ sessionID, prompt: { text: "hi" } })
  slowestHook = Math.max(slowestHook, performance.now() - t0)
  check(!(result instanceof Promise), "o hook de prompt devolveu uma promessa: o host esperaria por ela")
}
check(slowestHook < LIMIT_MS, `um hook demorou ${slowestHook.toFixed(1)} ms (limite ${LIMIT_MS})`)

// ── 4. stats e handoff, sob o teto de `cq` ───────────────────────────────────

const stats = await handlers.stats({ sessionID: SESSIONS[0], directory })
check(stats.ok && /claude-opus-5-5/.test(stats.text), "stats mostra as linhas do cq")
const handoff = await handlers.handoff({ sessionID: SESSIONS[0], directory, focus: "bench" })
check(handoff.ok && handoff.line === "Read the handoff" && opened[0] === "Read the handoff", `o handoff gravou e abriu a sessão nova: ${JSON.stringify(handoff)}`)
check(cq.cqStats.peak <= cq.CQ_CONCURRENCY, `${cq.cqStats.peak} cq ao mesmo tempo (teto ${cq.CQ_CONCURRENCY})`)
check(calls.filter((c) => c.startsWith("config show")).length <= 2, "as configurações do checkout são lidas uma vez, não por sessão")

// ── 5. o fim ─────────────────────────────────────────────────────────────────

if (typeof cleanup === "function") await cleanup()
console.log(`bench: ${SESSIONS.length} sessões × 25 passos em ${Date.now() - started} ms; p99 do laço ${(monitor.percentile(99) / 1e6).toFixed(1)} ms; pico de cq ${cq.cqStats.peak}; ${calls.length} chamadas ao cq`)
if (failures.length > 0) {
  for (const failure of failures) console.error(`FALHOU: ${failure}`)
  process.exit(1)
}
console.log("bench: ok")
process.exit(0)
