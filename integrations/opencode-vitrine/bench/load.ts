/**
 * Carga sintética da vitrine dentro de um host falso: uma sessão de ~400 mil tokens, rajadas de
 * tools e um `cq` falso com latência. Falha (exit 1) quando o plugin bloqueia o laço de eventos
 * por mais de 50 ms, quando um hook espera trabalho, ou quando passa do teto de `cq` simultâneos.
 *
 *   npm run bench
 */
import { monitorEventLoopDelay, performance } from "node:perf_hooks"
import { fileURLToPath } from "node:url"
import { resolve } from "node:path"
import plugin from "../src/index.js"
import * as cq from "../src/cq.js"
import * as specs from "../src/specs.js"

const LIMIT_MS = 50
const failures: string[] = []
const check = (ok: boolean, message: string) => { if (!ok) failures.push(message) }

// ── a sessão sintética ───────────────────────────────────────────────────────

const IDS = Array.from({ length: 400 }, (_, index) => 1500 + index)
const filler = "O agente leu o arquivo, rodou os testes e anotou o resultado da etapa anterior. "

function message(index: number): unknown {
  const id = IDS[index % IDS.length]
  switch (index % 4) {
    case 0:
      return { id: `m${index}`, type: "user", text: `continue a ${id} e veja o que falta ${filler.repeat(4)}` }
    case 1:
      return { id: `m${index}`, type: "assistant", content: [{ type: "text", text: `${filler.repeat(40)} spec ${id} ` }] }
    case 2:
      return {
        id: `m${index}`,
        type: "assistant",
        content: [{ type: "tool", name: "bash", state: { input: { command: `cq specs status ${id} --json && cq specs task ${id} 1.2 --check` } } }],
      }
    default:
      return { id: `m${index}`, type: "assistant", content: [{ type: "text", text: filler.repeat(60) }] }
  }
}

const messages: unknown[] = Array.from({ length: 650 }, (_, index) => message(index))
// Uma saída colada inteira na conversa: um texto único de ~300 KB.
messages.push({ id: "huge", type: "assistant", content: [{ type: "text", text: `${filler.repeat(4_000)} #1777` }] })
const chars = JSON.stringify(messages).length
console.log(`sessão sintética: ${messages.length} mensagens, ${(chars / 1e6).toFixed(2)} M chars (~${Math.round(chars / 4 / 1000)}k tokens)`)

// ── o `cq` falso ─────────────────────────────────────────────────────────────

const LATENCY = 150
const calls = new Map<string, number>()
cq.setReadRunner(async (_launch, args) => {
  const key = args.join(" ")
  calls.set(key, (calls.get(key) ?? 0) + 1)
  await new Promise((done) => setTimeout(done, LATENCY))
  if (args[0] === "specs" && args[1] === "list") {
    const rows = IDS.slice(0, args.includes("--lean") ? IDS.length : 50).map((id) => ({ id, title: `Spec ${id}`, stage: "ready", phase: "plans" }))
    return { code: 0, stdout: JSON.stringify({ specs: rows }), stderr: "" }
  }
  if (args[0] === "specs" && (args[1] === "status" || args[1] === "show")) {
    const id = Number(args[args.indexOf("--spec") + 1])
    return { code: 0, stdout: JSON.stringify({ id, title: `Spec ${id}`, stage: "approved", phase: "archive", tasks: [] }), stderr: "" }
  }
  return { code: 0, stdout: "{}", stderr: "" }
})

// ── o host falso ─────────────────────────────────────────────────────────────

type Hook = (event: any) => unknown
const hooks = new Map<string, Hook>()
const handlers: Record<string, (input: unknown) => Promise<unknown>> = {}
const emitted: string[] = []
const store = new Map<string, unknown>()
const directory = resolve(fileURLToPath(new URL("../../../..", import.meta.url)))
const sessionID = "ses_bench"

const ctx: any = {
  rpc: {
    register: async (_contract: unknown, impl: typeof handlers) => {
      Object.assign(handlers, impl)
      return { events: { emit: async (name: string) => { emitted.push(name) } } }
    },
  },
  storage: {
    get: async (key: string) => store.get(key),
    set: async (key: string, value: unknown) => { store.set(key, value) },
  },
  session: {
    context: async () => messages.slice(),
    get: async () => ({ directory }),
    hook: async (name: string, callback: Hook) => { hooks.set(`session.${name}`, callback) },
  },
  tool: {
    hook: async (name: string, callback: Hook) => { hooks.set(`tool.${name}`, callback) },
    transform: async () => undefined,
  },
}

const cleanup = await plugin.setup(ctx)

// ── 1. os hooks não esperam nada ─────────────────────────────────────────────

let slowestHook = 0
function fire(name: string, event: unknown): void {
  const started = performance.now()
  const result = hooks.get(name)!(event)
  slowestHook = Math.max(slowestHook, performance.now() - started)
  check(!(result instanceof Promise), `${name} devolveu uma promessa: o host esperaria por ela`)
}

const delay = monitorEventLoopDelay({ resolution: 5 })
delay.enable()

// ── 2. rajada: 50 tools por minuto, comprimidas em 2 s, com o painel aberto ──

const burst: Promise<unknown>[] = []
for (let index = 0; index < 100; index += 1) {
  const id = IDS[index % IDS.length]
  const command = index % 3 === 0 ? `cq specs task ${id} 2.1 --check` : index % 3 === 1 ? "ls -la" : `cq git commit -m "${id}"`
  const event = { tool: "bash", sessionID, agent: "build", messageID: `m${index}`, id: `c${index}`, input: { command } }
  fire("tool.execute.before", event)
  fire("tool.execute.after", { ...event, status: "completed", result: {} })
  if (index % 10 === 0) fire("session.prompt", { sessionID, prompt: { text: `olha a ${id} e a #${id + 1}` } })
  if (index % 25 === 0) burst.push(handlers.touched({ sessionID, directory }))
  await new Promise((done) => setTimeout(done, 20))
}
await Promise.all(burst)

// ── 3. varredura incremental: a sessão cresce e o painel reabre ──────────────

for (let index = 0; index < 8; index += 1) messages.push(message(650 + index))
messages.push({ id: "tail", type: "user", text: "fecha a 1899 por favor" })
await new Promise((done) => setTimeout(done, 5_100))
const rows = (await handlers.touched({ sessionID, directory })) as { id: number }[]
const ledger = specs.ledger(sessionID)
check(rows.length > 0, `o painel devolveu ${rows.length} linhas`)
check(ledger.has(1899), "a mensagem nova (1899) não entrou no ledger: o cursor pulou o fim")
check(ledger.has(1777), "o id no fim do texto de 300 KB (1777) não entrou: a janela cortou o texto")

delay.disable()
await new Promise((done) => setTimeout(done, 1_200))
await (cleanup as (() => unknown) | undefined)?.()

// ── 4. a varredura fatiada concorda com a síncrona ───────────────────────────

const known = new Set(IDS)
const whole = specs.harvest(messages, known).hits.map((hit) => `${hit.id}:${hit.kind}`).sort()
const sliced = (await specs.harvestSliced(messages, known)).hits.map((hit) => `${hit.id}:${hit.kind}`).sort()
check(JSON.stringify(whole) === JSON.stringify(sliced), "harvestSliced e harvest discordam")

const syncStarted = performance.now()
specs.harvest(messages, known)
const syncCost = performance.now() - syncStarted

// ── 5. cursor ────────────────────────────────────────────────────────────────

const cursor = specs.cursorOf(messages)
check(specs.resumeAt(messages, cursor) === messages.length - 1, "o cursor não retoma na última mensagem vista")
check(specs.resumeAt(messages.slice(0, 10), cursor) === 0, "uma conversa que encolheu não recomeça do zero")
const rewritten = messages.slice()
rewritten[cursor.count - 1] = { id: "outra" }
check(specs.resumeAt(rewritten, cursor) === 0, "uma conversa reescrita não recomeça do zero")

// ── o veredito ───────────────────────────────────────────────────────────────

const maxDelay = delay.max / 1e6
const lean = calls.get("specs list --lean --json") ?? 0
console.log(`laço de eventos: máx ${maxDelay.toFixed(1)} ms bloqueado, p99 ${(delay.percentile(99) / 1e6).toFixed(1)} ms`)
console.log(`hook mais lento: ${slowestHook.toFixed(2)} ms`)
console.log(`varredura síncrona da sessão inteira (referência, o que o plugin antigo fazia): ${syncCost.toFixed(1)} ms`)
console.log([...calls].sort((a, b) => b[1] - a[1]).slice(0, 6).map(([k, v]) => `  ${v}x ${k}`).join("\n"))
console.log(`cq: ${cq.cqStats.spawned} processos, pico de ${cq.cqStats.peak} simultâneos; \`specs list --lean\` ${lean}x`)
console.log(`avisos: ${emitted.filter((name) => name === "changed").length} changed, ${emitted.filter((name) => name === "updated").length} updated`)

// A resolução do monitor (5 ms) e o ruído de GC entram no máximo; o teto é o da spec.
check(maxDelay <= LIMIT_MS, `o laço de eventos ficou ${maxDelay.toFixed(1)} ms bloqueado (> ${LIMIT_MS} ms)`)
check(slowestHook < 5, `um hook levou ${slowestHook.toFixed(2)} ms no caminho da tool`)
check(cq.cqStats.peak <= cq.CQ_CONCURRENCY, `pico de ${cq.cqStats.peak} cq simultâneos (> ${cq.CQ_CONCURRENCY})`)
check(cq.cqStats.spawned <= 150, `${cq.cqStats.spawned} processos cq numa rajada: o teto de leituras fora de plans não segurou`)
check(lean <= 2, `\`specs list --lean\` rodou ${lean}x: a promessa em voo não foi compartilhada`)
check(emitted.filter((name) => name === "changed").length <= 12, "o painel recebeu um aviso por comando, sem coalescer")

if (failures.length > 0) {
  for (const failure of failures) console.error(`FALHOU: ${failure}`)
  process.exit(1)
}
console.log("ok")
process.exit(0)
