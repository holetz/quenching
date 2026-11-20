import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { CqState, Detail, LedgerEntry, Kind, TouchRow, View } from '../types'
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

const taskMark = (task: Detail['tasks'][number]) => (task.state === 'x' ? '[x]' : task.blocked ? '[!]' : '[ ]')

export async function drawPane($: EngineInterface, e: Parameters<EngineInterface['ui']['resolve']>[0]) {
  const { Box, Button, Markdown, Text } = $.ui.resolve(e)
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
            <Text key={`task-${task.id}`}>{`${taskMark(task)} ${task.id} ${task.text}`}</Text>
          ))}
        </Box>
      )}
      {section && <Markdown key={`section-${spec.id}-${at}`} text={section.body || '_Empty._'} />}
      {at === tabs.length - 1 && <Text dimColor>No dependencies read yet.</Text>}
    </Box>
  )
}
