import { singleFlight } from './cq'
import type { Cq } from './cq'

import type { Composite, Composition, Dependencies, Detail, Member, Neighbor, Section, SpecRow, TaskInfo } from '../types'

export type { Composite, Composition, Dependencies, Detail, Member, Neighbor, Section, SpecRow, TaskInfo }

const TTL = 30_000

/** The board's stages, in the order it shows them. */
export const STAGES = ['captured', 'ready', 'approved', 'executing', 'blocked', 'review', 'archived']

/**
 * The stage the board paints: archive, a blocked task and review are not in the document's raw
 * `stage`, they come from the records. Without this the chip colour would lie.
 */
export function stageOf(raw: any): string {
  const phase = String(raw?.phase ?? '')
  const stage = String(raw?.stage ?? '')

  if (phase === 'archive' || stage === 'archive') {
    return 'archived'
  }

  if (Number(raw?.tasks?.blocked ?? 0) > 0) {
    return 'blocked'
  }

  if (raw?.records?.reviewed) {
    return 'review'
  }

  return STAGES.includes(stage) ? stage : 'captured'
}

export function normalizeRow(row: any): SpecRow {
  return {
    id: Number(row?.id ?? 0),
    title: String(row?.title ?? ''),
    stage: stageOf(row),
    phase: String(row?.phase ?? ''),
    date: String(row?.date ?? ''),
    checked: Number(row?.tasks?.checked ?? 0),
    blocked: Number(row?.tasks?.blocked ?? 0),
    total: Number(row?.tasks?.total ?? 0),
    work: String(row?.records?.branch?.work ?? ''),
    run: String(row?.records?.run?.state ?? ''),
    workItemType: String(row?.workItemType ?? ''),
  }
}

/** The whole document cut at the canonical `## <Heading>`. The mold's comments never reach the screen. */
export function split(document: string): Section[] {
  const body = document.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '').replace(/<!--[\s\S]*?-->/g, '')
  const out: Section[] = []
  const heading = /^##[ \t]+(.+?)[ \t]*$/gm
  let match: RegExpExecArray | null
  let last: { heading: string; start: number } | undefined

  while ((match = heading.exec(body)) !== null) {
    if (last) {
      out.push({ heading: last.heading, body: body.slice(last.start, match.index).trim() })
    }
    last = { heading: match[1] ?? '', start: heading.lastIndex }
  }

  if (last) {
    out.push({ heading: last.heading, body: body.slice(last.start).trim() })
  }

  if (out.length === 0 && body.trim()) {
    out.push({ heading: 'Document', body: body.trim() })
  }

  return out
}

/** The document's `---` block as top-level key/value pairs. */
export function frontmatter(document: string): Record<string, string> {
  const block = /^---\r?\n([\s\S]*?)\r?\n---/.exec(document)
  const out: Record<string, string> = {}

  for (const line of (block?.[1] ?? '').split(/\r?\n/)) {
    const field = /^([A-Za-z][\w-]*):[ \t]*(.*)$/.exec(line)

    if (field) {
      out[field[1] ?? ''] = (field[2] ?? '').trim()
    }
  }

  return out
}

function inlineList(value: string | undefined): string[] {
  if (!value) {
    return []
  }

  return value
    .replace(/^\[|\]$/g, '')
    .split(',')
    .map(item => item.trim().replace(/^["']|["']$/g, ''))
    .filter(Boolean)
}

const unquote = (value: string | undefined) => (value ? value.replace(/^["']|["']$/g, '') : '')

const BANDS = ['critical', 'high', 'medium', 'low']

/** The board's `P1..P4`: `criticality` when present, else the 1 to 4 `level`. */
export function priorityOf(record: any): { label: string; hint: string } {
  const band = BANDS.indexOf(String(record?.criticality ?? '').toLowerCase())

  if (band >= 0) {
    return { label: `P${band + 1}`, hint: `P${band + 1} · ${BANDS[band]}` }
  }
  const level = Number(record?.level)

  if (Number.isInteger(level) && level >= 1 && level <= 4) {
    return { label: `P${level}`, hint: `P${level} · level` }
  }

  return { label: '', hint: '' }
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

type CompositeRef = { epic?: string; label?: string; group?: number }

type Schedule = {
  nodes?: ScheduleNode[]
  cycle?: string[]
  composites?: Record<string, CompositeRef[]>
}

type Graph = {
  at: number
  nodes: Map<string, ScheduleNode>
  cycle: string[]
  composites: Map<string, CompositeRef[]>
}

function neighborOf(node: ScheduleNode): Neighbor {
  return {
    id: Number(node.id ?? 0),
    title: String(node.title ?? ''),
    phase: String(node.phase ?? ''),
    critical: Boolean(node.critical),
    slip: Number(node.slipDays ?? 0),
    start: String(node.start ?? ''),
    target: String(node.target ?? ''),
  }
}

/**
 * The composites that name `id`, titled from the graph, with the label the composite gave the member.
 * An id the graph does not know is dropped: a broken reference is a `validate` finding, not a row.
 */
function membershipOf(graph: Graph, id: number): Composite[] {
  return (graph.composites.get(String(id)) ?? [])
    .map(ref => ({
      epic: Number(ref.epic ?? 0),
      title: String(graph.nodes.get(String(ref.epic ?? ''))?.title ?? ''),
      label: String(ref.label ?? ''),
      group: Number(ref.group ?? 0),
    }))
    .filter(ref => ref.epic > 0 && graph.nodes.has(String(ref.epic)))
}

/** The edges that touch `id`, both ways: the ones it declares and the ones that name it. */
function neighbors(graph: Graph, id: number): Dependencies {
  const key = String(id)
  const up = (graph.nodes.get(key)?.dependsOn ?? [])
    .map(dep => graph.nodes.get(dep))
    .filter((node): node is ScheduleNode => Boolean(node))
    .map(neighborOf)
  const down = [...graph.nodes.values()]
    .filter(node => String(node.id) !== key && (node.dependsOn ?? []).includes(key))
    .map(neighborOf)
    .sort((a, b) => a.id - b.id)

  return { up, down, cycle: graph.cycle }
}

/** The composition `status` already carries for an epic; absent for a spec that is not one. */
function compositionOf(raw: any): Composition | undefined {
  if (!raw || !Array.isArray(raw.items)) {
    return undefined
  }
  const count = (value: unknown) => Number(value ?? 0)
  const labels = (value: unknown) => (Array.isArray(value) ? value.map(String) : [])

  return {
    progress: {
      done: count(raw.progress?.done),
      total: count(raw.progress?.total),
      blocked: count(raw.progress?.blocked),
      ready: count(raw.progress?.ready),
    },
    groups: (raw.groups ?? []).map((group: any) => ({
      group: count(group?.group),
      title: String(group?.title ?? ''),
      done: count(group?.done),
      blocked: count(group?.blocked),
      total: count(group?.total),
    })),
    items: raw.items.map((item: any) => ({
      label: String(item?.label ?? ''),
      spec: Number(item?.spec ?? 0),
      title: String(item?.title ?? ''),
      group: count(item?.group),
      status: String(item?.status ?? ''),
      stage: String(item?.stage ?? ''),
      after: labels(item?.after),
      waitingOn: labels(item?.waitingOn),
    })),
  }
}

export type Specs = {
  list: (cwd: string) => Promise<SpecRow[]>
  /** Every spec id in every phase, for loose mentions in the conversation. */
  known: (cwd: string) => Promise<Set<number>>
  detail: (cwd: string, id: number) => Promise<Detail>
  task: (cwd: string, id: number, taskID: string) => Promise<TaskInfo>
  /** The spec of the session's branch, or `undefined`. */
  branchSpec: (cwd: string) => Promise<number | undefined>
  /** The spec of the session's commit, or `undefined`. */
  commitSpec: (cwd: string) => Promise<number | undefined>
  /** A spec outside `plans` (archived, delivered) as a list row, read through its detail. */
  offRow: (cwd: string, id: number) => Promise<SpecRow | undefined>
  forget: () => void
}

/** The specs reads over a `cq`, each cached for a short while and shared while in flight. */
export function createSpecs(cq: Cq): Specs {
  const snapshots = new Map<string, { at: number; rows: SpecRow[] }>()
  const listing = singleFlight<SpecRow[]>()
  const catalogues = new Map<string, { at: number; ids: Set<number> }>()
  const cataloguing = singleFlight<Set<number>>()
  const details = new Map<string, { at: number; value: Detail }>()
  const detailing = singleFlight<Detail>()
  const graphs = new Map<string, Graph>()
  const graphing = singleFlight<Graph>()
  const commits = new Map<string, number | undefined>()

  const list: Specs['list'] = async cwd => {
    const hit = snapshots.get(cwd)

    if (hit && Date.now() - hit.at < TTL) {
      return hit.rows
    }

    return listing(cwd, async () => {
      const payload = await cq.json<{ specs?: unknown[] }>(cwd, ['specs', 'list', '--phase', 'plans'])
      const rows = (payload?.specs ?? []).map(normalizeRow)

      // A cq failure must not erase what was known: an empty list is published only when there never was one.
      if (payload || !hit) {
        snapshots.set(cwd, { at: Date.now(), rows })
      }

      return payload ? rows : (hit?.rows ?? [])
    })
  }

  const known: Specs['known'] = async cwd => {
    const hit = catalogues.get(cwd)

    if (hit && Date.now() - hit.at < 120_000) {
      return hit.ids
    }

    return cataloguing(cwd, async () => {
      const payload = await cq.json<{ specs?: { id?: number }[] }>(cwd, ['specs', 'list', '--lean'])
      const ids = new Set((payload?.specs ?? []).map(row => Number(row?.id ?? 0)).filter(Boolean))
      const value = ids.size > 0 ? ids : (hit?.ids ?? ids)
      catalogues.set(cwd, { at: Date.now(), ids: value })

      return value
    })
  }

  /**
   * The whole dependency graph in one read. `--all` includes specs with no edge and archived ones: who sits
   * BELOW a spec is the node that names it, and an archived dependent is outside the default selection.
   * A `cq` older than `--all` refuses it, so the open graph answers instead; a cycle exits 1 with its payload.
   */
  const dependencyGraph = async (cwd: string): Promise<Graph> => {
    const hit = graphs.get(cwd)

    if (hit && Date.now() - hit.at < TTL) {
      return hit
    }

    return graphing(cwd, async () => {
      const payload =
        (await cq.jsonPartial<Schedule>(cwd, ['specs', 'schedule', '--all'])) ??
        (await cq.json<Schedule>(cwd, ['specs', 'schedule']))
      const nodes = new Map<string, ScheduleNode>()

      for (const node of payload?.nodes ?? []) {
        if (node?.id !== undefined) {
          nodes.set(String(node.id), node)
        }
      }
      const composites = new Map<string, CompositeRef[]>()

      for (const [member, refs] of Object.entries(payload?.composites ?? {})) {
        if (Array.isArray(refs)) {
          composites.set(String(member), refs)
        }
      }
      const value: Graph = { at: Date.now(), nodes, cycle: (payload?.cycle ?? []).map(String), composites }

      if (payload || !hit) {
        graphs.set(cwd, value)
      }

      return payload ? value : (hit ?? value)
    })
  }

  const readDetail = async (cwd: string, id: number, key: string): Promise<Detail> => {
    const [status, show, full, graph] = await Promise.all([
      cq.json<any>(cwd, ['specs', 'status', '--spec', String(id)]),
      cq.json<any>(cwd, ['specs', 'show', '--spec', String(id)]),
      cq.json<any>(cwd, ['specs', 'show', '--spec', String(id), '--full']),
      dependencyGraph(cwd),
    ])
    const blocked = new Set<string>((status?.tasks?.blockedTasks ?? []).map((one: any) => String(one?.id ?? one?.task ?? '')))
    const sections: Section[] = full?.document
      ? split(String(full.document))
      : (show?.sections ?? []).map((section: any) => ({ heading: String(section?.heading ?? ''), body: '' }))
    const fm = full?.document ? frontmatter(String(full.document)) : {}
    const priority = priorityOf(status?.records?.priority)
    const composition = compositionOf(status?.composition)
    const blockedTask = (status?.tasks?.blockedTasks ?? [])[0] as any
    const blockedText = String(blockedTask?.text ?? '')
    const reason = blockedText.split(/—\s*blocked:\s*/i)[1] ?? blockedText
    const value: Detail = {
      id,
      title: String(status?.title ?? show?.title ?? ''),
      stage: stageOf(status ?? show),
      phase: String(status?.phase ?? show?.phase ?? ''),
      date: String(status?.date ?? ''),
      priority: priority.label,
      priorityHint: priority.hint,
      complexity: String(status?.records?.priority?.complexity ?? ''),
      subject: unquote(fm.subject),
      assignee: unquote(fm.assignee),
      tags: inlineList(fm.tags),
      ready: Boolean(status?.ready?.ok ?? false),
      missing: (status?.ready?.missing ?? []).join(', '),
      checked: Number(status?.tasks?.checked ?? 0),
      blocked: Number(status?.tasks?.blocked ?? 0),
      blockedTask: String(blockedTask?.id ?? ''),
      blockedReason: reason.trim(),
      total: Number(status?.tasks?.total ?? 0),
      run: String(status?.records?.run?.state ?? ''),
      verifier: String(status?.records?.run?.verifier ?? ''),
      pr: String(status?.records?.pr?.number ?? status?.records?.pr?.url ?? ''),
      prUrl: String(status?.records?.pr?.url ?? ''),
      work: String(status?.records?.branch?.work ?? ''),
      sections,
      tasks: (show?.tasks ?? []).map((one: any) => ({
        id: String(one?.id ?? ''),
        state: String(one?.state ?? ''),
        text: String(one?.text ?? ''),
        blocked: blocked.has(String(one?.id ?? '')),
      })),
      workItemType: unquote(fm.workItemType),
      deps: neighbors(graph, id),
      epics: membershipOf(graph, id),
      ...(composition ? { composition } : {}),
    }
    details.set(key, { at: Date.now(), value })

    return value
  }

  const detail: Specs['detail'] = async (cwd, id) => {
    const key = `${cwd}:${id}`
    const hit = details.get(key)

    if (hit && Date.now() - hit.at < TTL) {
      return hit.value
    }

    return detailing(key, () => readDetail(cwd, id, key))
  }

  return {
    list,
    known,
    detail,
    task: async (cwd, id, taskID) => {
      const payload = await cq.json<any>(cwd, ['specs', 'show', '--spec', String(id), '--task', taskID])
      const found = payload?.tasks?.[0]

      return {
        text: String(found?.text ?? ''),
        files: (found?.files ?? [])
          .filter((file: unknown) => typeof file === 'string' && file.trim() !== '' && file !== '[]')
          .map(String)
          .join(', '),
        verify: String(found?.verify ?? ''),
        subject: String(found?.subject ?? ''),
      }
    },
    branchSpec: async cwd => {
      const branch = await cq.git(cwd, ['branch', '--show-current'])

      return branch ? (await cq.json<{ id?: number }>(cwd, ['specs', 'find', '--branch', branch]))?.id : undefined
    },
    commitSpec: async cwd => {
      const sha = await cq.git(cwd, ['rev-parse', 'HEAD'])

      if (!sha) {
        return undefined
      }
      const key = `${cwd}:${sha}`

      if (commits.has(key)) {
        return commits.get(key)
      }
      const payload = await cq.json<{ id?: number }>(cwd, ['specs', 'find', '--commit', sha])

      // Only an answer counts: a failed cq is never recorded as "no spec".
      if (payload) {
        commits.set(key, payload.id)
      }

      return payload?.id
    },
    offRow: async (cwd, id) => {
      const spec = await detail(cwd, id).catch(() => undefined)

      return spec?.title ? rowOf(spec) : undefined
    },
    forget: () => {
      snapshots.clear()
      catalogues.clear()
      details.clear()
      graphs.clear()
      commits.clear()
    },
  }
}

export function rowOf(spec: Detail): SpecRow {
  return {
    id: spec.id,
    title: spec.title,
    stage: spec.stage,
    phase: spec.phase,
    date: spec.date,
    checked: spec.checked,
    blocked: spec.blocked,
    total: spec.total,
    work: spec.work,
    run: spec.run,
    workItemType: spec.workItemType,
  }
}
