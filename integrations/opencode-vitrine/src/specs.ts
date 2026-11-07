import { spawn, type ChildProcess } from "node:child_process"
import { createInterface } from "node:readline"
import {
  cqBinary, cqJson, cqJsonPartial, forgetBinaries, git, mainRoot, singleFlight, spawnArgs, type Launch,
} from "./cq.js"

/** Uma linha de `cq specs list`, normalizada para a GUI. */
export type SpecRow = {
  id: number
  title: string
  stage: string
  phase: string
  date: string
  checked: number
  blocked: number
  total: number
  work: string
  run: string
}

/** O que a sessão fez com uma spec. `worktree` é o checkout em que ela está; `command` é escrita. */
export type Kind = "worktree" | "command" | "read" | "commit" | "mention"

/** A força da evidência: um fato forte não é rebaixado por um mais fraco. */
const RANK: Record<Kind, number> = { mention: 0, read: 1, command: 2, commit: 3, worktree: 3 }

export type TouchRow = SpecRow & { kind: Kind; at: number }

export type Section = { heading: string; body: string }

/** Uma spec vizinha no grafo de dependências, como o `schedule` a descreve. */
export type Neighbor = {
  id: number
  title: string
  phase: string
  critical: boolean
  slip: number
  start: string
  target: string
}

/** Quem está acima (o que ela espera), abaixo (quem espera por ela) e o ciclo que trava tudo. */
export type Dependencies = { up: Neighbor[]; down: Neighbor[]; cycle: string[] }

export type Detail = {
  id: number
  title: string
  stage: string
  phase: string
  date: string
  priority: string
  priorityHint: string
  complexity: string
  subject: string
  assignee: string
  tags: string[]
  ready: boolean
  missing: string
  checked: number
  blocked: number
  blockedTask: string
  blockedReason: string
  total: number
  run: string
  verifier: string
  pr: string
  prUrl: string
  work: string
  sections: Section[]
  tasks: { id: string; state: string; text: string; blocked: boolean }[]
  deps: Dependencies
}

export type TaskInfo = { text: string; files: string; verify: string; subject: string }

const TTL = 30_000

function normalizeRow(row: any): SpecRow {
  return {
    id: Number(row?.id ?? 0),
    title: String(row?.title ?? ""),
    stage: stageOf(row),
    phase: String(row?.phase ?? ""),
    date: String(row?.date ?? ""),
    checked: Number(row?.tasks?.checked ?? 0),
    blocked: Number(row?.tasks?.blocked ?? 0),
    total: Number(row?.tasks?.total ?? 0),
    work: String(row?.records?.branch?.work ?? ""),
    run: String(row?.records?.run?.state ?? ""),
  }
}

const snapshots = new Map<string, { at: number; rows: SpecRow[] }>()
const listing = singleFlight<SpecRow[]>()

export async function list(cwd: string): Promise<SpecRow[]> {
  const root = (await mainRoot(cwd)) ?? cwd
  const hit = snapshots.get(root)
  if (hit && Date.now() - hit.at < TTL) return hit.rows
  return listing(root, async () => {
    const payload = await cqJson<{ specs?: unknown[] }>(cwd, ["specs", "list", "--phase", "plans"])
    const rows = (payload?.specs ?? []).map(normalizeRow)
    // Uma falha do `cq` não pode apagar o que já se sabia: só publica lista vazia quando nunca houve.
    if (payload || !hit) snapshots.set(root, { at: Date.now(), rows })
    return payload ? rows : (hit?.rows ?? [])
  })
}

export async function search(cwd: string, query: string, limit: number): Promise<SpecRow[]> {
  const rows = await list(cwd)
  const terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean)
  const found = terms.length === 0
    ? rows
    : rows.filter((row) => {
        const haystack = `${row.id} ${row.title} ${row.stage} ${row.work}`.toLowerCase()
        return terms.every((term) => haystack.includes(term))
      })
  // Um id fora de `plans` (arquivada, entregue) ainda abre pelo número.
  if (found.length === 0 && terms.length === 1 && /^\d{3,7}$/.test(terms[0])) {
    const spec = await detail(cwd, Number(terms[0])).catch(() => undefined)
    if (spec?.title) return [rowOf(spec)]
  }
  return found.slice(0, Math.max(1, Math.min(limit, 200)))
}

const catalogues = new Map<string, { at: number; ids: Set<number> }>()
const cataloguing = singleFlight<Set<number>>()

/**
 * Os ids que a sessão pode citar soltos, sem `#` nem a palavra "spec", em todas as fases.
 * `--lean` evita o custo de ler os documentos só para montar este conjunto. Uma falha também
 * fica em cache (vazia, pelo mesmo prazo): sem isso cada hook repetia um `cq` que falha.
 */
export async function known(cwd: string): Promise<Set<number>> {
  const root = (await mainRoot(cwd)) ?? cwd
  const hit = catalogues.get(root)
  if (hit && Date.now() - hit.at < 120_000) return hit.ids
  return cataloguing(root, async () => {
    const payload = await cqJson<{ specs?: { id?: number }[] }>(cwd, ["specs", "list", "--lean"])
    const ids = new Set((payload?.specs ?? []).map((row) => Number(row?.id ?? 0)).filter(Boolean))
    const value = ids.size > 0 ? ids : (hit?.ids ?? ids)
    catalogues.set(root, { at: Date.now(), ids: value })
    return value
  })
}

const details = new Map<string, { at: number; value: Detail }>()
const detailing = singleFlight<Detail>()

/** Depois de um deploy, o que foi lido com o `cq` antigo não serve mais. */
export function forget(): void {
  details.clear()
  catalogues.clear()
  snapshots.clear()
  graphs.clear()
  homes.clear()
  offRows.clear()
  forgetBinaries()
}

/** O documento inteiro, cortado nos `## <Heading>` canônicos. Comentários do molde não vão para a tela. */
export function split(document: string): Section[] {
  const body = document
    .replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, "")
    .replace(/<!--[\s\S]*?-->/g, "")
  const out: Section[] = []
  const heading = /^##[ \t]+(.+?)[ \t]*$/gm
  let match: RegExpExecArray | null
  let last: { heading: string; start: number } | undefined
  while ((match = heading.exec(body)) !== null) {
    if (last) out.push({ heading: last.heading, body: body.slice(last.start, match.index).trim() })
    last = { heading: match[1], start: heading.lastIndex }
  }
  if (last) out.push({ heading: last.heading, body: body.slice(last.start).trim() })
  if (out.length === 0 && body.trim()) out.push({ heading: "Documento", body: body.trim() })
  return out
}

/** As etapas do board, na ordem em que ele as mostra. */
export const STAGES = ["captured", "ready", "approved", "executing", "blocked", "review", "archived"]

/**
 * A etapa que o board pinta: arquivo, bloqueio por task e revisão não estão no `stage`
 * cru do documento, saem dos registros. Sem isso a cor do chip mentiria.
 */
export function stageOf(raw: any): string {
  const phase = String(raw?.phase ?? "")
  const stage = String(raw?.stage ?? "")
  if (phase === "archive" || stage === "archive") return "archived"
  if (Number(raw?.tasks?.blocked ?? 0) > 0) return "blocked"
  if (raw?.records?.reviewed) return "review"
  return STAGES.includes(stage) ? stage : "captured"
}

/** O bloco `---` do documento, como pares chave/valor de primeiro nível. */
export function frontmatter(document: string): Record<string, string> {
  const block = /^---\r?\n([\s\S]*?)\r?\n---/.exec(document)
  const out: Record<string, string> = {}
  for (const line of (block?.[1] ?? "").split(/\r?\n/)) {
    const field = /^([A-Za-z][\w-]*):[ \t]*(.*)$/.exec(line)
    if (field) out[field[1]] = field[2].trim()
  }
  return out
}

function inlineList(value: string | undefined): string[] {
  if (!value) return []
  return value
    .replace(/^\[|\]$/g, "")
    .split(",")
    .map((item) => item.trim().replace(/^["']|["']$/g, ""))
    .filter(Boolean)
}

const BANDS = ["critical", "high", "medium", "low"]
const BAND_LABEL = ["crítica", "alta", "média", "baixa"]

/** O `P1..P4` do board: `criticality` quando existe, senão o `level` de 1 a 4. */
export function priorityOf(record: any): { label: string; hint: string } {
  const band = BANDS.indexOf(String(record?.criticality ?? "").toLowerCase())
  if (band >= 0) return { label: `P${band + 1}`, hint: `P${band + 1} · ${BAND_LABEL[band]}` }
  const level = Number(record?.level)
  if (Number.isInteger(level) && level >= 1 && level <= 4) return { label: `P${level}`, hint: `P${level} · nível` }
  return { label: "", hint: "" }
}

type ScheduleNode = {
  id?: string
  title?: string
  phase?: string
  dependsOn?: string[]
  critical?: boolean
  slipDays?: number
  start?: string | null
  target?: string | null
}

type Schedule = { nodes?: ScheduleNode[]; cycle?: string[] }

type Graph = { at: number; nodes: Map<string, ScheduleNode>; cycle: string[] }

const graphs = new Map<string, Graph>()
const graphing = singleFlight<Graph>()

/**
 * O grafo de dependências inteiro numa leitura só. `--all` inclui as specs sem aresta e as
 * arquivadas: quem está ABAIXO de uma spec é o nó que a nomeia, e um dependente arquivado fica
 * fora da seleção padrão do `schedule`. Um `cq` anterior ao `--all` recusa o pedido; aí vale o
 * grafo aberto, menor, e o painel mostra o que ele tem em vez de mentir que não há aresta.
 * Um ciclo sai do `cq` com exit 1 e ainda assim traz o payload: é ele que o painel precisa.
 */
async function dependencyGraph(cwd: string): Promise<Graph> {
  const root = (await mainRoot(cwd)) ?? cwd
  const hit = graphs.get(root)
  if (hit && Date.now() - hit.at < TTL) return hit
  return graphing(root, async () => {
    const payload = await cqJsonPartial<Schedule>(cwd, ["specs", "schedule", "--all"])
      ?? await cqJson<Schedule>(cwd, ["specs", "schedule"])
    const nodes = new Map<string, ScheduleNode>()
    for (const node of payload?.nodes ?? []) {
      if (node?.id !== undefined) nodes.set(String(node.id), node)
    }
    const value: Graph = { at: Date.now(), nodes, cycle: (payload?.cycle ?? []).map(String) }
    // Uma falha do `cq` não pode apagar o grafo que já se sabia.
    if (payload || !hit) graphs.set(root, value)
    return payload ? value : (hit ?? value)
  })
}

function neighborOf(node: ScheduleNode): Neighbor {
  return {
    id: Number(node.id ?? 0),
    title: String(node.title ?? ""),
    phase: String(node.phase ?? ""),
    critical: Boolean(node.critical),
    slip: Number(node.slipDays ?? 0),
    start: String(node.start ?? ""),
    target: String(node.target ?? ""),
  }
}

/** As arestas que tocam `id`, nas duas direções: as declaradas por ela e as que a nomeiam. */
function neighbors(graph: Graph, id: number): Dependencies {
  const key = String(id)
  const up = (graph.nodes.get(key)?.dependsOn ?? [])
    .map((dep) => graph.nodes.get(dep))
    .filter((node): node is ScheduleNode => Boolean(node))
    .map(neighborOf)
  const down = [...graph.nodes.values()]
    .filter((node) => String(node.id) !== key && (node.dependsOn ?? []).includes(key))
    .map(neighborOf)
    .sort((a, b) => a.id - b.id)
  return { up, down, cycle: graph.cycle }
}

export async function detail(cwd: string, id: number): Promise<Detail> {
  const root = (await mainRoot(cwd)) ?? cwd
  const key = `${root}:${id}`
  const hit = details.get(key)
  if (hit && Date.now() - hit.at < TTL) return hit.value
  return detailing(key, () => readDetail(cwd, id, key))
}

async function readDetail(cwd: string, id: number, key: string): Promise<Detail> {
  const [status, show, full, graph] = await Promise.all([
    cqJson<any>(cwd, ["specs", "status", "--spec", String(id)]),
    cqJson<any>(cwd, ["specs", "show", "--spec", String(id)]),
    cqJson<any>(cwd, ["specs", "show", "--spec", String(id), "--full"]),
    dependencyGraph(cwd),
  ])
  const blocked = new Set<string>(
    (status?.tasks?.blockedTasks ?? []).map((task: any) => String(task?.id ?? task?.task ?? "")),
  )
  const sections: Section[] = full?.document
    ? split(String(full.document))
    : (show?.sections ?? []).map((section: any) => ({ heading: String(section?.heading ?? ""), body: "" }))
  const fm = full?.document ? frontmatter(String(full.document)) : {}
  const priority = priorityOf(status?.records?.priority)
  const blockedTask = (status?.tasks?.blockedTasks ?? [])[0] as any
  const blockedText = String(blockedTask?.text ?? "")
  const reason = blockedText.split(/—\s*blocked:\s*/i)[1] ?? blockedText
  const value: Detail = {
    id,
    title: String(status?.title ?? show?.title ?? ""),
    stage: stageOf(status ?? show),
    phase: String(status?.phase ?? show?.phase ?? ""),
    date: String(status?.date ?? ""),
    priority: priority.label,
    priorityHint: priority.hint,
    complexity: String(status?.records?.priority?.complexity ?? ""),
    subject: fm.subject ? fm.subject.replace(/^["']|["']$/g, "") : "",
    assignee: fm.assignee ? fm.assignee.replace(/^["']|["']$/g, "") : "",
    tags: inlineList(fm.tags),
    ready: Boolean(status?.ready?.ok ?? false),
    missing: (status?.ready?.missing ?? []).join(", "),
    checked: Number(status?.tasks?.checked ?? 0),
    blocked: Number(status?.tasks?.blocked ?? 0),
    blockedTask: String(blockedTask?.id ?? ""),
    blockedReason: reason.trim(),
    total: Number(status?.tasks?.total ?? 0),
    run: String(status?.records?.run?.state ?? ""),
    verifier: String(status?.records?.run?.verifier ?? ""),
    pr: String(status?.records?.pr?.number ?? status?.records?.pr?.url ?? ""),
    prUrl: String(status?.records?.pr?.url ?? ""),
    work: String(status?.records?.branch?.work ?? ""),
    sections,
    tasks: (show?.tasks ?? []).map((task: any) => ({
      id: String(task?.id ?? ""),
      state: String(task?.state ?? ""),
      text: String(task?.text ?? ""),
      blocked: blocked.has(String(task?.id ?? "")),
    })),
    deps: neighbors(graph, id),
  }
  details.set(key, { at: Date.now(), value })
  return value
}

export async function task(cwd: string, id: number, taskID: string): Promise<TaskInfo> {
  const payload = await cqJson<any>(cwd, ["specs", "show", "--spec", String(id), "--task", taskID])
  const found = payload?.tasks?.[0]
  return {
    text: String(found?.text ?? ""),
    files: (found?.files ?? [])
      .filter((file: unknown) => typeof file === "string" && file.trim() !== "" && file !== "[]")
      .map(String)
      .join(", "),
    verify: String(found?.verify ?? ""),
    subject: String(found?.subject ?? ""),
  }
}

const WRITE = new Set([
  "record", "task", "start", "target", "assignee", "tags", "title", "promote",
  "discover", "new", "link", "epic", "scrub", "push", "artifact", "sync",
  "migrate", "release",
])

/** As specs que um comando `cq` nomeia, cada uma com o peso do verbo que a nomeou. */
export function parse(command: string): { hits: { id: number; kind: Kind }[]; commit: boolean } {
  const hits = new Map<number, Kind>()
  const pattern = /\bcq\b[^\n;&|]*?\bspecs\s+([a-z][a-z-]*)([^\n;&|]*)/g
  let match: RegExpExecArray | null
  while ((match = pattern.exec(command)) !== null) {
    const kind: Kind = WRITE.has(match[1]) ? "command" : "read"
    const id = /^\s+(?:--spec\s+)?(\d{3,})\b/.exec(match[2])
    if (!id) continue
    const value = Number(id[1])
    // O mesmo id em dois verbos do mesmo comando fica com o peso maior.
    if (kind === "command" || !hits.has(value)) hits.set(value, kind)
  }
  return { hits: [...hits].map(([id, kind]) => ({ id, kind })), commit: /\bcq\s+git\s+commit\b/.test(command) }
}

export type Ledger = Map<number, { kind: Kind; at: number }>

const ledgers = new Map<string, Ledger>()

/**
 * O ledger de uma sessão vive no módulo, não na instância do plugin: o host carrega o
 * plugin mais de uma vez por requisição e o painel precisa ver o que o hook gravou.
 */
export function ledger(sessionID: string): Ledger {
  let value = ledgers.get(sessionID)
  if (!value) {
    value = new Map()
    ledgers.set(sessionID, value)
  }
  return value
}

/** Absorve o que outra instância gravou sem rebaixar a evidência que já está aqui. */
export function absorb(target: Ledger, entries: Iterable<[number, { kind: Kind; at: number }]>): void {
  for (const [id, value] of entries) {
    const previous = target.get(id)
    const wins = !previous
      || RANK[value.kind] > RANK[previous.kind]
      || (RANK[value.kind] === RANK[previous.kind] && value.at > previous.at)
    if (wins) target.set(id, { kind: value.kind, at: value.at })
  }
}

export function touch(ledger: Ledger, id: number, kind: Kind): void {
  // Um fato mais forte não é rebaixado por uma leitura posterior.
  const previous = ledger.get(id)
  if (!previous || RANK[kind] >= RANK[previous.kind]) ledger.set(id, { kind, at: Date.now() })
}

/**
 * Um id de spec em qualquer texto: `#1985`, `spec 1985` sempre; um id solto (`1985`)
 * só quando `loose` — no texto do humano, onde a intenção está. `2026-10-11` não é id.
 */
export function mentions(text: string, known: Set<number>, loose = true): number[] {
  const found = new Set<number>()
  const explicit = /\bspecs?\b[^0-9\n]{0,16}(\d{3,7})(?![\dA-Za-z\-/])|#(\d{3,7})(?![\dA-Za-z\-/])/gi
  let match: RegExpExecArray | null
  while ((match = explicit.exec(text)) !== null) {
    const id = Number(match[1] ?? match[2])
    if (id) found.add(id)
  }
  if (!loose) return [...found]
  for (const bare of text.matchAll(/(?<!\d)(\d{3,7})(?![\dA-Za-z\-/])/g)) {
    const id = Number(bare[1])
    if (known.has(id)) found.add(id)
  }
  return [...found]
}

export function isShell(tool: string): boolean {
  const name = tool.toLowerCase()
  return name === "bash" || name === "shell" || name.endsWith(".bash") || name.endsWith(".shell")
}

export function commandOf(input: unknown): string | undefined {
  if (!input || typeof input !== "object") return undefined
  const value = input as { command?: unknown; cmd?: unknown; script?: unknown }
  const command = value.command ?? value.cmd ?? value.script
  return typeof command === "string" ? command : undefined
}

type Part = { type?: string; text?: string; name?: string; input?: unknown; state?: { input?: unknown } }
type ChatMessage = { role?: string; type?: string; text?: string; content?: unknown }

/**
 * Varre o que a sessão já conversou: texto do humano, do agente e comandos executados.
 * Aceita as duas formas — a do contexto do modelo (`role`/`content`) e a da sessão
 * (`type: "user"` com `text`, `type: "assistant"` com `content`, `tool` com `state.input`).
 */
export function harvest(messages: readonly unknown[], known: Set<number>): { hits: { id: number; kind: Kind }[] } {
  const hits = new Map<number, Kind>()
  for (const message of messages) {
    for (const _ of scanMessage(message, known, hits)) { /* síncrono: percorre tudo */ }
  }
  return { hits: [...hits].map(([id, kind]) => ({ id, kind })) }
}

/** Janela de texto varrida de uma vez; a sobreposição cobre um id cortado na borda. */
const WINDOW = 32 * 1024
const OVERLAP = 48

function addHit(hits: Map<number, Kind>, id: number, kind: Kind): void {
  const previous = hits.get(id)
  if (previous === undefined || RANK[kind] >= RANK[previous]) hits.set(id, kind)
}

function* scanText(text: string, known: Set<number>, loose: boolean, hits: Map<number, Kind>): Generator<void> {
  if (text.length <= WINDOW) {
    for (const id of mentions(text, known, loose)) addHit(hits, id, "mention")
    return
  }
  for (let start = 0; start < text.length; start += WINDOW) {
    const slice = text.slice(Math.max(0, start - OVERLAP), start + WINDOW)
    for (const id of mentions(slice, known, loose)) addHit(hits, id, "mention")
    yield
  }
}

/** Varre uma mensagem; cede (`yield`) entre janelas de texto longo para quem fatia o trabalho. */
function* scanMessage(raw: unknown, known: Set<number>, hits: Map<number, Kind>): Generator<void> {
  const message = raw as ChatMessage
  if (!message || typeof message !== "object") return
  // O id solto vale no que o humano escreveu; no texto do agente ele é ruído.
  const loose = message.role === "user" || message.type === "user"
  if (typeof message.text === "string") yield* scanText(message.text, known, loose, hits)
  if (!Array.isArray(message.content)) return
  for (const part of message.content as Part[]) {
    if (!part || typeof part !== "object") continue
    if (part.type === "text" && typeof part.text === "string") {
      yield* scanText(part.text, known, loose, hits)
      continue
    }
    const name = part.name
    if (!name || (part.type !== "tool-call" && part.type !== "tool")) continue
    if (!isShell(name)) continue
    const command = commandOf(part.input ?? part.state?.input)
    if (!command) continue
    for (const hit of parse(command).hits) addHit(hits, hit.id, hit.kind)
    yield* scanText(command, known, false, hits)
  }
}

/** Devolve o laço de eventos ao host antes de continuar. */
export function yieldToHost(): Promise<void> {
  return new Promise((done) => setImmediate(done))
}

/**
 * A mesma varredura de `harvest`, fatiada: a cada `budget` ms de CPU ela cede o laço de eventos
 * ao serviço do OpenCode, que é quem roda o plugin. Uma conversa de 400 mil tokens não pode
 * segurar a thread principal de uma vez.
 */
export async function harvestSliced(
  messages: readonly unknown[],
  known: Set<number>,
  budget = 8,
): Promise<{ hits: { id: number; kind: Kind }[] }> {
  const hits = new Map<number, Kind>()
  let started = performance.now()
  for (const message of messages) {
    for (const _ of scanMessage(message, known, hits)) {
      if (performance.now() - started >= budget) {
        await yieldToHost()
        started = performance.now()
      }
    }
    if (performance.now() - started >= budget) {
      await yieldToHost()
      started = performance.now()
    }
  }
  return { hits: [...hits].map(([id, kind]) => ({ id, kind })) }
}

/** A identidade de uma mensagem para o cursor: o `id` quando a forma tem, senão nada. */
export function messageKey(message: unknown): string | undefined {
  const id = (message as { id?: unknown } | null)?.id
  return typeof id === "string" || typeof id === "number" ? String(id) : undefined
}

export type Cursor = { count: number; last?: string }

/**
 * Onde a varredura anterior parou. Retoma depois da última mensagem já vista quando ela ainda
 * está no mesmo lugar; se a conversa encolheu ou foi reescrita (compactação), recomeça do zero.
 */
export function resumeAt(messages: readonly unknown[], cursor: Cursor | undefined): number {
  if (!cursor || cursor.count === 0) return 0
  if (cursor.count > messages.length) return 0
  if (cursor.last !== undefined && messageKey(messages[cursor.count - 1]) !== cursor.last) return 0
  // A última mensagem vista pode ter crescido (streaming): ela é varrida de novo.
  return cursor.count - 1
}

export function cursorOf(messages: readonly unknown[]): Cursor {
  return { count: messages.length, last: messages.length > 0 ? messageKey(messages[messages.length - 1]) : undefined }
}

const homes = new Map<string, { at: number; id?: number }>()
const homing = singleFlight<number | undefined>()

async function home(cwd: string): Promise<number | undefined> {
  const hit = homes.get(cwd)
  if (hit && Date.now() - hit.at < TTL) return hit.id
  return homing(cwd, async () => {
    const branch = await git(cwd, ["rev-parse", "--abbrev-ref", "HEAD"])
    const id = branch && branch !== "HEAD"
      ? (await cqJson<{ id?: number }>(cwd, ["specs", "find", "--branch", branch]))?.id
      : undefined
    homes.set(cwd, { at: Date.now(), id })
    return id
  })
}

function rowOf(spec: Detail): SpecRow {
  return {
    id: spec.id,
    title: spec.title,
    stage: spec.stage,
    phase: spec.phase,
    date: "",
    checked: spec.checked,
    blocked: spec.blocked,
    total: spec.total,
    work: spec.work,
    run: spec.run,
  }
}

const offRows = new Map<string, { at: number; row?: SpecRow }>()

async function offList(cwd: string, id: number): Promise<SpecRow | undefined> {
  const root = (await mainRoot(cwd)) ?? cwd
  const key = `${root}:${id}`
  const hit = offRows.get(key)
  if (hit && Date.now() - hit.at < 300_000) return hit.row
  const spec = await detail(cwd, id).catch(() => undefined)
  const row = spec?.title ? rowOf(spec) : undefined
  offRows.set(key, { at: Date.now(), row })
  return row
}

export async function touched(cwd: string, ledger: Ledger): Promise<TouchRow[]> {
  const homeID = await home(cwd)
  if (homeID) touch(ledger, homeID, "worktree")
  const rows = await list(cwd)
  const byId = new Map(rows.map((row) => [row.id, row]))
  const out: TouchRow[] = []
  // Os mais fortes e mais recentes primeiro: o teto de leituras fora de `plans` corta o fim da fila.
  const ordered = [...ledger].sort(([, a], [, b]) => RANK[b.kind] - RANK[a.kind] || b.at - a.at)
  let reads = 0
  for (const [id, evidence] of ordered) {
    let row = byId.get(id)
    // Uma spec concluída sai de `plans`; o painel ainda a mostra enquanto a sessão estiver nela.
    // Ela quase não muda, então a linha fica 5 min em cache: cada `detail` são três `cq`.
    if (!row) {
      const cached = offCached(await mainRoot(cwd) ?? cwd, id)
      if (cached.hit) row = cached.row
      else if (reads < OFF_LIST_READS) {
        reads += 1
        row = await offList(cwd, id)
      }
    }
    if (row) out.push({ ...row, kind: evidence.kind, at: evidence.at })
  }
  return out.sort((a, b) => RANK[b.kind] - RANK[a.kind] || b.at - a.at)
}

/**
 * Specs fora de `plans` lidas por abertura do painel. Uma sessão longa cita centenas de ids;
 * sem teto cada abertura subia três `cq` por id. As que ficam de fora entram nas aberturas seguintes.
 */
export const OFF_LIST_READS = 12

function offCached(root: string, id: number): { hit: boolean; row?: SpecRow } {
  const hit = offRows.get(`${root}:${id}`)
  return hit && Date.now() - hit.at < 300_000 ? { hit: true, row: hit.row } : { hit: false }
}

const commits = new Map<string, number | undefined>()

/** A spec de um commit não muda: a resposta fica em cache pelo SHA. */
export async function commitSpec(cwd: string): Promise<number | undefined> {
  const sha = await git(cwd, ["rev-parse", "HEAD"])
  if (!sha) return undefined
  const key = `${(await mainRoot(cwd)) ?? cwd}:${sha}`
  if (commits.has(key)) return commits.get(key)
  const payload = await cqJson<{ id?: number }>(cwd, ["specs", "find", "--commit", sha])
  // Só uma resposta conta: um `cq` que falhou não fica gravado como "sem spec".
  if (payload) {
    if (commits.size > 500) commits.clear()
    commits.set(key, payload.id)
  }
  return payload?.id
}

type Portal = { child: ChildProcess; url: Promise<string> }
let portal: Portal | undefined

function launch(cwd: string, cq: Launch, args: string[]): Portal {
  const call = spawnArgs(cq, args)
  const child = spawn(call.command, call.args, { cwd, stdio: ["ignore", "pipe", "inherit"], windowsHide: true, ...call.options })
  const url = new Promise<string>((resolveURL, reject) => {
    let text = ""
    createInterface({ input: child.stdout! }).on("line", (line) => {
      text += line
      try {
        const parsed = JSON.parse(text) as { url?: string }
        if (parsed.url) resolveURL(parsed.url)
        else reject(new Error(text))
      } catch {
        // objeto ainda incompleto
      }
    })
    child.once("error", reject)
    child.once("exit", () => reject(new Error("o portal encerrou antes de publicar a URL")))
  })
  const reset = () => { if (portal?.child === child) portal = undefined }
  child.once("exit", reset)
  child.once("error", reset)
  process.once("exit", () => child.kill())
  return { child, url }
}

function stop(): void {
  if (!portal) return
  const current = portal
  portal = undefined
  current.child.kill()
}

async function start(cwd: string): Promise<string> {
  const { launch: cq } = await cqBinary(cwd)
  // Sem `--read-only`: o board abre com escrita habilitada (o backend ainda pode recusar).
  const central = launch(cwd, cq, ["portal", "serve", "--json"])
  portal = central
  try {
    return await central.url
  } catch {
    if (portal?.child === central.child) portal = undefined
    const single = launch(cwd, cq, ["specs", "serve", "--json"])
    portal = single
    return single.url
  }
}

/**
 * A URL do board no navegador, sempre com o `nonce` que o `cq` imprimiu. O nonce vale uma
 * vez e vira cookie; como o navegador do sistema pode abrir sem cookie, cada clique sobe
 * um portal novo em vez de reaproveitar uma URL já gasta — era isso que devolvia
 * `sp-portal-token` a partir do segundo clique.
 */
export async function board(cwd: string): Promise<{ url: string }> {
  stop()
  return { url: await start(cwd) }
}
