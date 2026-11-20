import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { Composite, CqState, Detail, LedgerEntry, Kind, Member, Neighbor, TouchRow, View } from '../types'
import { createCq } from './cq'
import type { Runner } from './cq'
import { harvest, touch, touchedRows } from './ledger'
import { createSpecs } from './specs'

export const view = atom({ plugin: 'quenching-vitrine', key: 'view' } as const, 'specs' as View)
// Change a tag when the fields it stores change: it declines what an earlier version kept through a reload.
export const ledger = atom({ plugin: 'quenching-vitrine', key: 'ledger' } as const, [] as LedgerEntry[], { shape: 'ledger-1' })
export const rows = atom({ plugin: 'quenching-vitrine', key: 'rows' } as const, [] as TouchRow[], { shape: 'rows-1' })
export const picked = atom({ plugin: 'quenching-vitrine', key: 'picked' } as const, null as number | null)
export const detail = atom({ plugin: 'quenching-vitrine', key: 'detail' } as const, null as Detail | null, { shape: 'detail-1' })
export const tab = atom({ plugin: 'quenching-vitrine', key: 'tab' } as const, 0)
export const cqState = atom({ plugin: 'quenching-vitrine', key: 'cq' } as const, null as CqState | null)
export const busy = atom({ plugin: 'quenching-vitrine', key: 'busy' } as const, '')

// ── services ─────────────────────────────────────────────────────────────────

type Services = { cq: ReturnType<typeof createCq>; specs: ReturnType<typeof createSpecs> }

/** What the cached `cq` runs with; each call swaps in the newest `$`, so a hot reload never leaves a dead one. */
let run: Runner = async () => ({ code: -1, stdout: '', stderr: 'the engine is not ready' })
let held: Services | undefined

/** One `cq` and one specs cache for the mod. */
export function services($: EngineInterface): Services {
  run = async (argv, cwd, timeoutMs) => {
    try {
      const done = await $.process.run(argv, { cwd, timeoutMs })

      return { code: done.exitCode, stdout: done.stdout, stderr: done.stderr }
    } catch (error) {
      return { code: -1, stdout: '', stderr: String(error) }
    }
  }

  if (!held) {
    const cq = createCq((argv, cwd, timeoutMs) => run(argv, cwd, timeoutMs))
    held = { cq, specs: createSpecs(cq) }
  }

  return held
}

// ── actions ──────────────────────────────────────────────────────────────────

/** Re-reads the conversation and merges what it names into the ledger: what a reload lost comes back. */
export async function rebuild($: EngineInterface) {
  const { specs } = services($)
  const cwd = await $.session.cwd()
  const messages = await $.session.messages()
  const found = harvest(messages, await specs.known(cwd))
  const now = await $.clock.now()

  await update($, ledger, entries =>
    found.reduce((all, hit, index) => touch(all, hit.id, hit.kind, now - (found.length - index)), entries),
  )
}

/** Probes `cq`, rebuilds the ledger from the conversation and reads the rows the pane lists. */
export async function refresh($: EngineInterface) {
  const { cq, specs } = services($)
  const cwd = await $.session.cwd()
  await update($, busy, () => 'Reading specs…')

  try {
    specs.forget()
    const probe = await cq.probe(cwd)
    await update($, cqState, () => probe)

    if (!probe.found) {
      await update($, rows, () => [])

      return
    }
    await rebuild($).catch(() => undefined)
    const next = await touchedRows(specs, cwd, await read($, ledger), await $.clock.now())
    await update($, rows, () => next)
  } finally {
    await update($, busy, () => '')
  }
}

/** Opens a spec's detail: the tab goes back to the first and the document loads behind it. */
export async function pick($: EngineInterface, id: number) {
  const { specs } = services($)
  const cwd = await $.session.cwd()
  await update($, picked, () => id)
  await update($, tab, () => 0)
  await update($, detail, () => null)
  await update($, busy, () => 'Reading the spec…')

  try {
    const next = await specs.detail(cwd, id)
    await update($, detail, () => next)
  } finally {
    await update($, busy, () => '')
  }
}

/** Notes the specs a tool call named, with the weight of what it did. */
export async function record($: EngineInterface, hits: { id: number; kind: Kind }[]) {
  const now = await $.clock.now()

  await update($, ledger, entries => hits.reduce((all, hit) => touch(all, hit.id, hit.kind, now), entries))
}

/** What the box is told about a whole spec: its stage, its progress and the next task to build. */
export function specNote(spec: Detail): string {
  const next = spec.tasks.find(task => task.state !== 'x' && !task.blocked)

  return [
    `spec ${spec.id} — ${spec.title}`,
    `stage: ${spec.stage} · tasks: ${spec.checked}/${spec.total}${spec.blocked ? ` · blocked: ${spec.blocked}` : ''}`,
    next ? `next: ${next.id} ${next.text}` : '',
  ]
    .filter(Boolean)
    .join('\n')
}

/** What the box is told about one task: its text, the files it may touch and how it is verified. */
export function taskNote(id: number, taskID: string, info: { text: string; files: string; verify: string }): string {
  return `spec ${id} task ${taskID} — ${info.text}\nfiles: ${info.files || '-'}\nverify: ${info.verify || '-'}`
}

/** Why nothing reached the composer, in words the person can act on. */
export function refusalNote(refusal: 'no_composer' | 'dialog' | undefined): string {
  return refusal === 'dialog' ? 'A dialog is open: close it, then attach again.' : 'No prompt box to fill: nothing was attached.'
}

/** Puts a task, or the whole spec, in the composer where the cursor stands; a refusal is a toast. */
export async function attach($: EngineInterface, id: number, taskID?: string) {
  const { specs } = services($)
  const cwd = await $.session.cwd()
  const shown = await read($, detail)
  const text = taskID
    ? taskNote(id, taskID, await specs.task(cwd, id, taskID))
    : specNote(shown?.id === id ? shown : await specs.detail(cwd, id))
  const filled = await $.prompt.fill({ text: `${text}\n`, mode: 'insert' })

  if (!filled.isFilled) {
    $.ui.toast(refusalNote(filled.refusal))
  }
}

export async function back($: EngineInterface) {
  await update($, picked, () => null)
  await update($, detail, () => null)
}

// ── drawing ──────────────────────────────────────────────────────────────────

const EVIDENCE: Record<Kind, string> = {
  worktree: 'worktree',
  commit: 'commit',
  command: 'write',
  mention: 'cited',
  read: 'read',
}

export function ageDays(date: string, now: number): number | null {
  const time = Date.parse(`${date}T00:00:00Z`)

  return date && !Number.isNaN(time) ? Math.max(0, Math.floor((now - time) / 86_400_000)) : null
}

export function ageLabel(date: string, now: number): string {
  const days = ageDays(date, now)

  if (days === null) {
    return date
  }

  if (days === 0) {
    return 'today'
  }

  if (days === 1) {
    return 'yesterday'
  }

  if (days < 30) {
    return `${days} d ago`
  }
  const months = Math.floor(days / 30)

  return `${months} ${months === 1 ? 'month' : 'months'} ago`
}

/** A run that stopped, or a verifier that said no, is worth the eye. */
export function runBad(spec: Pick<Detail, 'run' | 'verifier'>): boolean {
  return spec.run === 'failed' || spec.run === 'blocked' || spec.verifier === 'fail'
}

/** The board signals of the header, as short words. */
export function signals(spec: Detail, now: number): string[] {
  const out = [spec.stage]

  if (spec.priority) {
    out.push(spec.priority)
  }

  if (spec.complexity) {
    out.push(spec.complexity)
  }

  if (spec.date) {
    out.push(ageLabel(spec.date, now))
  }

  if (spec.total > 0) {
    out.push(`${spec.checked}/${spec.total} tasks`)
  }

  if (spec.run) {
    out.push(`run ${spec.run}${spec.verifier ? ` · verifier ${spec.verifier}` : ''}`)
  }

  if (spec.assignee) {
    out.push(spec.assignee)
  }

  return out
}

/** The tabs of a spec: Overview, each section of the document, then Dependências. */
export function tabsOf(spec: Detail): string[] {
  return ['Overview', ...spec.sections.map(section => section.heading), 'Dependências']
}

/** What the board shows beside a neighbour: archived, on the critical path, slipping, and its window. */
export function depMeta(node: Neighbor): string {
  const bits: string[] = []

  if (node.phase === 'archive') {
    bits.push('archived')
  }

  if (node.critical) {
    bits.push('critical path')
  }

  if (node.slip > 0) {
    bits.push(`+${node.slip}d`)
  }

  if (node.start || node.target) {
    bits.push(`${node.start || '?'} → ${node.target || '?'}`)
  }

  return bits.join(' · ')
}

const MEMBER_MARK: Record<string, string> = { done: '✓', dropped: '×', 'in-progress': '▸', waiting: '!' }

/** What the epic knows of a member: its spec stage and what it waits for inside the epic. */
export function memberMeta(member: Member): string {
  const bits: string[] = []

  if (member.stage) {
    bits.push(member.stage)
  }

  if (member.after.length > 0) {
    bits.push(`waits for ${member.after.join(', ')}`)
  }

  return bits.join(' · ')
}

type Elements = ReturnType<EngineInterface['ui']['resolve']>

/** The Dependências tab: where the spec is a member, what the epic is made of, and the edges both ways. */
export function drawDependencies($: EngineInterface, els: Elements, spec: Detail) {
  const { Box, Button, Text } = els
  const edges = spec.deps.up.length > 0 || spec.deps.down.length > 0
  const group = (label: string, group: string, nodes: Neighbor[], empty: string) => (
    <Box flexDirection="column">
      <Text bold>{label}</Text>
      {nodes.length === 0 && <Text dimColor>{empty}</Text>}
      {nodes.map(node => (
        <Button key={`dep-${group}-${node.id}`} plain onPress={() => pick($, node.id)}>
          {`${node.id} · ${node.title} `}
          <Text dimColor>{depMeta(node)}</Text>
        </Button>
      ))}
    </Box>
  )

  return (
    <Box flexDirection="column" gap={1}>
      {spec.epics.length > 0 && (
        <Box flexDirection="column">
          <Text bold>Part of</Text>
          {spec.epics.map((epic: Composite) => (
            <Button key={`epic-${epic.epic}`} plain onPress={() => pick($, epic.epic)}>
              {`${epic.label || '·'} ${epic.epic} · ${epic.title} `}
              <Text dimColor>{epic.group > 0 ? `wave ${epic.group}` : ''}</Text>
            </Button>
          ))}
        </Box>
      )}
      {spec.composition && (
        <Box flexDirection="column">
          <Text bold>
            {`Specs of this epic · ${spec.composition.progress.done}/${spec.composition.progress.total} done${
              spec.composition.progress.blocked > 0 ? ` · ${spec.composition.progress.blocked} blocked` : ''
            }`}
          </Text>
          {spec.composition.items.map(member => (
            <Button key={`member-${member.spec}`} plain onPress={() => pick($, member.spec)}>
              {`${MEMBER_MARK[member.status] ?? '·'} ${member.label} ${member.spec} · ${member.title} `}
              <Text dimColor>{memberMeta(member)}</Text>
            </Button>
          ))}
        </Box>
      )}
      {spec.deps.cycle.length > 0 && (
        <Text color="red">{`cycle: ${spec.deps.cycle.join(' → ')} — nothing is scheduled while it exists`}</Text>
      )}
      {/* With no edge, and a composition or membership above, the two lists have nothing to say. */}
      {(edges || (!spec.composition && spec.epics.length === 0)) && (
        <Box flexDirection="column" gap={1}>
          {group('Above — this spec waits for', 'up', spec.deps.up, 'nothing above: no dependency declared')}
          {group('Below — waiting for this spec', 'down', spec.deps.down, 'nothing below: no spec declares it depends on this one')}
        </Box>
      )}
    </Box>
  )
}

const taskMark = (task: Detail['tasks'][number]) => (task.state === 'x' ? '[x]' : task.blocked ? '[!]' : '[ ]')

export async function drawPane($: EngineInterface, e: Parameters<EngineInterface['ui']['resolve']>[0]) {
  const els = $.ui.resolve(e)
  const { Box, Button, Markdown, Text } = els
  const cq = await read($, cqState)
  const list = await read($, rows)
  const id = await read($, picked)
  const spec = await read($, detail)
  const index = await read($, tab)
  const working = await read($, busy)
  const now = await $.clock.now()

  if (cq !== null && !cq.found) {
    return (
      <Box flexDirection="column" gap={1}>
        <Text bold>cq was not found</Text>
        <Text dimColor>{cq.detail || 'Run cq --version in this directory.'}</Text>
        <Text dimColor>Install quenching in the project (cq deploy), or put cq on PATH, then reopen the pane.</Text>
        <Button key="refresh" label="Check again" onPress={() => refresh($)} />
      </Box>
    )
  }

  if (id === null) {
    return (
      <Box flexDirection="column" gap={1}>
        <Box flexDirection="row" gap={2}>
          <Text bold>Specs of this session</Text>
          <Button key="refresh" label="Refresh" onPress={() => refresh($)} />
        </Box>
        {working !== '' && <Text dimColor>{working}</Text>}
        {working === '' && list.length === 0 && (
          <Text dimColor>No spec yet: cite one, run a cq specs command, or work on a plan/ branch.</Text>
        )}
        {list.map(row => (
          <Button key={`spec-${row.id}`} plain onPress={() => pick($, row.id)}>
            {`${row.id} · ${row.title} `}
            <Text dimColor>
              {`${row.stage} · ${row.total > 0 ? `${row.checked}/${row.total} · ` : ''}${EVIDENCE[row.kind]}`}
            </Text>
          </Button>
        ))}
      </Box>
    )
  }

  if (spec === null) {
    return (
      <Box flexDirection="column" gap={1}>
        <Button key="back" label="Back" onPress={() => back($)} />
        <Text dimColor>{working || `Spec ${id} could not be read.`}</Text>
      </Box>
    )
  }
  const tabs = tabsOf(spec)
  const at = Math.min(index, tabs.length - 1)
  const section = at > 0 && at < tabs.length - 1 ? spec.sections[at - 1] : undefined

  return (
    <Box flexDirection="column" gap={1}>
      <Box flexDirection="row" gap={2}>
        <Button key="back" label="Back" onPress={() => back($)} />
        <Text bold>{`${spec.id} · ${spec.title}`}</Text>
        <Button key="attach-spec" label="Attach spec" onPress={() => attach($, spec.id)} />
      </Box>
      <Text color={runBad(spec) ? 'red' : undefined} dimColor={!runBad(spec)}>
        {signals(spec, now).join(' · ')}
      </Text>
      {spec.blocked > 0 && (
        <Text color="red">{`blocked ${spec.blockedTask}: ${spec.blockedReason || 'no reason recorded'}`}</Text>
      )}
      <Box flexDirection="row" flexWrap="wrap" gap={1}>
        {tabs.map((label, position) => (
          <Button
            key={`tab-${position}`}
            plain={position !== at ? true : undefined}
            variant={position === at ? 'primary' : undefined}
            label={label}
            onPress={() => update($, tab, () => position)}
          />
        ))}
      </Box>
      {at === 0 && (
        <Box flexDirection="column">
          {spec.tasks.length === 0 && <Text dimColor>No tasks yet.</Text>}
          {spec.tasks.map(task => (
            <Box key={`row-${task.id}`} flexDirection="row" gap={1}>
              <Text>{`${taskMark(task)} ${task.id} ${task.text}`}</Text>
              <Button key={`attach-${task.id}`} label="Attach" onPress={() => attach($, spec.id, task.id)} />
            </Box>
          ))}
        </Box>
      )}
      {section && <Markdown key={`section-${spec.id}-${at}`} text={section.body || '_Empty._'} />}
      {at === tabs.length - 1 && drawDependencies($, els, spec)}
    </Box>
  )
}
