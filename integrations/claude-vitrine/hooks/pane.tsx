import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { Composite, ConfigKey, ConfigLayer, ConfigSchema, CqState, Detail, LedgerEntry, Kind, Member, Neighbor, TouchRow, View } from '../types'
import { SOURCE_LABEL, describe, encode, isReadOnly, parseSchema, restoreLayer, sectionsOf, shown, sourceOf, targetLayer } from './config'
import { createCq, DEPLOYED_CQ, withLauncher } from './cq'
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
export const config = atom({ plugin: 'quenching-vitrine', key: 'config' } as const, null as ConfigSchema | null, { shape: 'config-1' })
export const configError = atom({ plugin: 'quenching-vitrine', key: 'configError' } as const, '')
export const layer = atom({ plugin: 'quenching-vitrine', key: 'layer' } as const, 'project' as ConfigLayer)
export const drafts = atom({ plugin: 'quenching-vitrine', key: 'drafts' } as const, {} as Record<string, string>, { shape: 'drafts-1' })

// ── services ─────────────────────────────────────────────────────────────────

type Services = { cq: ReturnType<typeof createCq>; specs: ReturnType<typeof createSpecs> }

/** What the cached `cq` runs with; each call swaps in the newest `$`, so a hot reload never leaves a dead one. */
let run: Runner = async () => ({ code: -1, stdout: '', stderr: 'the engine is not ready' })
let held: Services | undefined
/** The newest `$.fs.stat`, swapped like `run`. */
let stat: (path: string) => Promise<{ kind: string } | undefined> = async () => undefined

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

  stat = path => $.fs.stat(path).catch(() => undefined)

  if (!held) {
    const locate = async (cwd: string) => {
      const top = await run(['git', 'rev-parse', '--show-toplevel'], cwd, 10_000)

      if (top.code !== 0 || !top.stdout.trim()) {
        return undefined
      }
      const path = `${top.stdout.trim()}/${DEPLOYED_CQ}`
      return (await stat(path))?.kind === 'file' ? path : undefined
    }
    const cq = createCq(withLauncher((argv, cwd, timeoutMs) => run(argv, cwd, timeoutMs), locate))
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

/** Switches between the Specs view and the Configuração view; the configuration is read when it opens. */
export async function show($: EngineInterface, next: View) {
  await update($, view, () => next)

  if (next === 'config') {
    await loadConfig($)
  }
}

/** Reads every key with its effective value and the layer that gave it; a failure is shown, never thrown. */
export async function loadConfig($: EngineInterface) {
  const { cq } = services($)
  const cwd = await $.session.cwd()
  await update($, busy, () => 'Reading the configuration…')

  try {
    const read = await cq.configSchema(cwd)
    const schema = read.ok ? parseSchema(read.json) : undefined

    await update($, configError, () => (schema ? '' : read.error || 'cq printed a configuration this pane cannot read.'))

    if (schema) {
      await update($, config, () => schema)
      await update($, drafts, () => ({}))
    }
  } finally {
    await update($, busy, () => '')
  }
}

/** Writes a key through `cq config set|unset` and reads the schema back; a refusal is a toast with the cq's reason. */
export async function writeConfig($: EngineInterface, entry: ConfigKey, value: string | null, into?: ConfigLayer) {
  const { cq } = services($)
  const cwd = await $.session.cwd()
  const target = into ?? targetLayer(entry, await read($, layer))
  const result = await cq.configWrite(cwd, entry.key, target, value)

  if (!result.ok) {
    $.ui.toast(`Not saved: ${result.message || 'cq refused the value'}`)

    return
  }
  $.ui.toast(`${entry.key} → ${target === 'local' ? 'Local' : 'Project'}`)
  await loadConfig($)
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

/** The Configuração view: every key by category with its layer badge, a Write to selector and Restore default. */
export function drawConfig(
  $: EngineInterface,
  els: Elements,
  state: { schema: ConfigSchema | null; error: string; layer: ConfigLayer; drafts: Record<string, string>; working: string },
) {
  const { Box, Button, Input, Select, Text } = els
  const { schema } = state

  const control = (entry: ConfigKey, schema: ConfigSchema) => {
    const current = schema.values[entry.key]?.value
    const restorable = restoreLayer(sourceOf(schema, entry))
    const restore = restorable && (
      <Button key={`restore-${entry.key}`} label="Restore default" onPress={() => writeConfig($, entry, null, restorable)} />
    )

    if (isReadOnly(entry)) {
      return (
        <Text dimColor>{`read-only here: edit ${schema.layerPaths.project}${shown(current) ? ` · now ${shown(current)}` : ''}`}</Text>
      )
    }

    if (entry.type === 'boolean') {
      return (
        <Box flexDirection="row" gap={1}>
          <Button
            key={`cfg-${entry.key}`}
            label={current === true ? 'On' : 'Off'}
            onPress={() => writeConfig($, entry, JSON.stringify(current !== true))}
          />
          {restore}
        </Box>
      )
    }

    if (entry.type === 'enum') {
      return (
        <Box flexDirection="row" gap={1}>
          <Select
            key={`cfg-${entry.key}`}
            options={(entry.choices ?? []).map(choice => ({ value: choice, label: choice }))}
            value={typeof current === 'string' ? current : undefined}
            onSelect={choice => writeConfig($, entry, JSON.stringify(choice))}
          />
          {restore}
        </Box>
      )
    }

    return (
      <Box flexDirection="row" gap={1}>
        <Input
          key={`cfg-${entry.key}`}
          value={state.drafts[entry.key] ?? shown(current)}
          placeholder={shown(entry.default) || 'Enter saves'}
          onInput={text => update($, drafts, all => ({ ...all, [entry.key]: text }))}
          onSubmit={text => writeConfig($, entry, encode(entry, text))}
        />
        {restore}
      </Box>
    )
  }

  return (
    <Box flexDirection="column" gap={1}>
      <Box flexDirection="row" gap={2}>
        <Button key="reload" label="Reload" onPress={() => loadConfig($)} />
        <Select
          key="layer"
          label="Write to"
          options={[
            { value: 'project', label: 'Project' },
            { value: 'local', label: 'Local' },
          ]}
          value={state.layer}
          onSelect={choice => update($, layer, () => (choice === 'local' ? 'local' : 'project'))}
        />
      </Box>
      <Text dimColor>Project is .agents/quenching.json, the team contract; Local is .agents/quenching.local.json, this machine only.</Text>
      {state.working !== '' && <Text dimColor>{state.working}</Text>}
      {state.error !== '' && <Text color="red">{state.error}</Text>}
      {schema === null && state.error === '' && state.working === '' && <Text dimColor>The configuration is not read yet.</Text>}
      {schema &&
        sectionsOf(schema).map(section => (
          <Box key={`section-${section.id}`} flexDirection="column" gap={1}>
            <Text bold>{section.title}</Text>
            {section.keys.map(entry => (
              <Box key={`row-${entry.key}`} flexDirection="column">
                <Text>
                  {entry.copy.en.title}
                  <Text dimColor>{` [${SOURCE_LABEL[sourceOf(schema, entry)] ?? sourceOf(schema, entry)}]${entry.scope === 'project' && state.layer === 'local' ? ' project key: always written to the project' : ''}`}</Text>
                </Text>
                <Text dimColor>{describe(entry)}</Text>
                {control(entry, schema)}
              </Box>
            ))}
          </Box>
        ))}
    </Box>
  )
}

const taskMark = (task: Detail['tasks'][number]) => (task.state === 'x' ? '[x]' : task.blocked ? '[!]' : '[ ]')

async function drawSpecs($: EngineInterface, els: Elements) {
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

/** The pane: the two views side by side in one bar, then the one chosen. */
export async function drawPane($: EngineInterface, e: Parameters<EngineInterface['ui']['resolve']>[0]) {
  const els = $.ui.resolve(e)
  const { Box, Button } = els
  const current = await read($, view)
  const body =
    current === 'config'
      ? drawConfig($, els, {
          schema: await read($, config),
          error: await read($, configError),
          layer: await read($, layer),
          drafts: await read($, drafts),
          working: await read($, busy),
        })
      : await drawSpecs($, els)

  return (
    <Box flexDirection="column" gap={1}>
      <Box flexDirection="row" gap={1}>
        <Button key="view-specs" label="Specs" variant={current === 'specs' ? 'primary' : undefined} onPress={() => show($, 'specs')} />
        <Button key="view-config" label="Configuração" variant={current === 'config' ? 'primary' : undefined} onPress={() => show($, 'config')} />
      </Box>
      {body}
    </Box>
  )
}
