import type { LedgerEntry, Kind } from '../types'
import type { SpecRow, Specs } from './specs'

/** The weight of the evidence: a strong fact is never demoted by a weaker one. */
const RANK: Record<Kind, number> = { mention: 0, read: 1, command: 2, commit: 3, worktree: 3 }

export const rank = (kind: Kind) => RANK[kind]

/** `cq specs <verb>` verbs that write; every other verb reads. */
const WRITE = new Set([
  'record', 'task', 'start', 'target', 'assignee', 'tags', 'title', 'promote', 'discover', 'new', 'link',
  'epic', 'scrub', 'push', 'artifact', 'sync', 'migrate', 'release',
])

/** MCP tools of the `quenching` server that only read; any other `specs_*` tool writes. */
const READ_TOOLS = new Set(['list', 'status', 'show', 'section', 'next', 'epic_progress'])

/** The specs a `cq` command names, each with the weight of the verb that named it. */
export function parseCommand(command: string): { hits: { id: number; kind: Kind }[]; commit: boolean } {
  const hits = new Map<number, Kind>()
  const pattern = /\bcq\b[^\n;&|]*?\bspecs\s+([a-z][a-z-]*)([^\n;&|]*)/g
  let match: RegExpExecArray | null

  while ((match = pattern.exec(command)) !== null) {
    const kind: Kind = WRITE.has(match[1] ?? '') ? 'command' : 'read'
    const id = /^\s+(?:--spec\s+)?(\d{3,})\b/.exec(match[2] ?? '')

    if (!id) {
      continue
    }
    const value = Number(id[1])

    // The same id under two verbs of one command keeps the heavier weight.
    if (kind === 'command' || !hits.has(value)) {
      hits.set(value, kind)
    }
  }

  return { hits: [...hits].map(([id, kind]) => ({ id, kind })), commit: /\bcq\s+git\s+commit\b/.test(command) }
}

/**
 * A spec id in any text: `#1985` and `spec 1985` always; a bare id (`1985`) only when `loose`, in what the person
 * wrote, where the intent is, and only when it is a known spec. `2026-10-11` is not an id.
 */
export function mentions(text: string, known: Set<number>, loose = true): number[] {
  const found = new Set<number>()
  const explicit = /\bspecs?\b[^0-9\n]{0,16}(\d{3,7})(?![\dA-Za-z\-/])|#(\d{3,7})(?![\dA-Za-z\-/])/gi
  let match: RegExpExecArray | null

  while ((match = explicit.exec(text)) !== null) {
    const id = Number(match[1] ?? match[2])

    if (id) {
      found.add(id)
    }
  }

  if (!loose) {
    return [...found]
  }

  for (const bare of text.matchAll(/(?<!\d)(\d{3,7})(?![\dA-Za-z\-/])/g)) {
    const id = Number(bare[1])

    if (known.has(id)) {
      found.add(id)
    }
  }

  return [...found]
}

/** The spec a `mcp__quenching__specs_*` call names, with the weight of the tool, or nothing for any other tool. */
export function mcpHit(tool: string, input: Record<string, unknown>): { id: number; kind: Kind } | undefined {
  const name = /^mcp__quenching__specs_([a-z_]+)$/.exec(tool)?.[1]

  if (!name) {
    return undefined
  }
  const id = Number(input.spec ?? input.epic)

  return Number.isInteger(id) && id > 0 ? { id, kind: READ_TOOLS.has(name) ? 'read' : 'command' } : undefined
}

/** What a tool call tells the ledger: the specs a Bash `cq` command or a quenching MCP tool names. */
export function toolHits(tool: string, input: Record<string, unknown>): { id: number; kind: Kind }[] {
  if (tool === 'Bash') {
    return typeof input.command === 'string' ? parseCommand(input.command).hits : []
  }
  const hit = mcpHit(tool, input)

  return hit ? [hit] : []
}

type Message = {
  role: 'user' | 'assistant'
  text: string
  toolUses: { tool: string; input: Record<string, unknown> }[]
}

/** The specs a conversation has already touched: the person's words, the agent's words and the calls it made. */
export function harvest(messages: readonly Message[], known: Set<number>): { id: number; kind: Kind }[] {
  const hits = new Map<number, Kind>()
  const add = (id: number, kind: Kind) => {
    const previous = hits.get(id)

    if (previous === undefined || RANK[kind] >= RANK[previous]) {
      hits.set(id, kind)
    }
  }

  for (const message of messages) {
    // A bare id counts in what the person wrote; in the agent's text it is noise.
    for (const id of mentions(message.text ?? '', known, message.role === 'user')) {
      add(id, 'mention')
    }

    for (const use of message.toolUses ?? []) {
      for (const hit of toolHits(use.tool, use.input ?? {})) {
        add(hit.id, hit.kind)
      }

      if (use.tool === 'Bash' && typeof use.input?.command === 'string') {
        for (const id of mentions(use.input.command, known, false)) {
          add(id, 'mention')
        }
      }
    }
  }

  return [...hits].map(([id, kind]) => ({ id, kind }))
}

/** The ledger with `id` seen as `kind` at `at`: a fact stronger than this one is kept, and the newer of equals wins. */
export function touch(entries: readonly LedgerEntry[], id: number, kind: Kind, at: number): LedgerEntry[] {
  const previous = entries.find(entry => entry.id === id)

  if (previous && (RANK[previous.kind] > RANK[kind] || (RANK[previous.kind] === RANK[kind] && previous.at >= at))) {
    return [...entries]
  }

  return [...entries.filter(entry => entry.id !== id), { id, kind, at }].slice(-400)
}

/** The ledger ordered for the pane: the strongest evidence first, the most recent first within a weight. */
export function ordered(entries: readonly LedgerEntry[]): LedgerEntry[] {
  return [...entries].sort((a, b) => RANK[b.kind] - RANK[a.kind] || b.at - a.at)
}

/** A ledger row shown in the pane: the spec's list row and the evidence that put it there. */
export type TouchRow = SpecRow & { kind: Kind; at: number }

/** Specs outside `plans` read per pane opening; a long session cites hundreds, each costing three `cq` reads. */
export const OFF_LIST_READS = 12

/**
 * The ledger as pane rows. The session's own branch and commit join first, as the strongest evidence; a spec
 * that left `plans` (delivered, archived) still shows while the session is on it, read through its detail.
 */
export async function touchedRows(specs: Specs, cwd: string, entries: readonly LedgerEntry[], now: number): Promise<TouchRow[]> {
  let ledger = [...entries]
  const [branch, commit] = await Promise.all([specs.branchSpec(cwd), specs.commitSpec(cwd)])

  if (branch) {
    ledger = touch(ledger, branch, 'worktree', now)
  }

  if (commit) {
    ledger = touch(ledger, commit, 'commit', now)
  }
  const byId = new Map((await specs.list(cwd)).map(row => [row.id, row]))
  const out: TouchRow[] = []
  let reads = 0

  for (const entry of ordered(ledger)) {
    let row = byId.get(entry.id)

    if (!row && reads < OFF_LIST_READS) {
      reads += 1
      row = await specs.offRow(cwd, entry.id)
    }

    if (row) {
      out.push({ ...row, kind: entry.kind, at: entry.at })
    }
  }

  return out
}
