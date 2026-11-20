import { expect, test } from 'claude-code/testing'

import type { Detail, TouchRow } from '../types'
import { ageLabel, refusalNote, signals, specNote, tabsOf, taskNote } from './pane'

const PANE = {
  plugin: 'quenching-vitrine',
  component: 'Pane',
  requestId: 'quenching-vitrine',
  props: {
    title: 'Specs',
    isFocused: false,
    bodyColumns: 80,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 20 },
    view: {},
  },
} as const

const SURFACES = ['terminal', 'desktop'] as const

type On = Parameters<Extract<Parameters<typeof test>[1], (...args: any) => any>>[1]

/**
 * Seeds the state the pane draws from. A key is answered with its seed until the plugin writes it; from then
 * on the engine's own state answers, so a press reaches the drawing exactly as in a session.
 */
function memory(on: On) {
  const seeds = new Map<string, unknown>()

  on('state.get', (_, e, next) => (seeds.has(e.key) ? { value: { value: seeds.get(e.key), version: 1 } } : next(e)))
  on('state.set', (_, e, next) => {
    seeds.delete(e.key)

    return next(e)
  })

  return {
    put: (key: string, value: unknown, shape?: string) => seeds.set(key, shape ? { shape, value } : value),
  }
}

const row = (id: number, title: string, kind: TouchRow['kind'] = 'read'): TouchRow => ({
  id, title, stage: 'approved', phase: 'plans', date: '2026-11-19', checked: 1, blocked: 0, total: 3, work: '', run: '', workItemType: '', kind, at: 1,
})

const spec = (extra: Partial<Detail> = {}): Detail => ({
  id: 2191,
  title: 'Port the panel',
  stage: 'blocked',
  phase: 'plans',
  date: '2026-11-19',
  priority: 'P2',
  priorityHint: 'P2 · high',
  complexity: 'medium',
  subject: '',
  assignee: 'ana',
  tags: [],
  ready: true,
  missing: '',
  checked: 1,
  blocked: 1,
  blockedTask: '1.2',
  blockedReason: 'waits for X',
  total: 3,
  run: 'failed',
  verifier: 'fail',
  pr: '',
  prUrl: '',
  work: 'plan/2191-x',
  sections: [{ heading: 'Problem', body: 'It hurts.' }, { heading: 'Proposal', body: 'Do it.' }],
  tasks: [
    { id: '1.1', state: 'x', text: 'one', blocked: false },
    { id: '1.2', state: ' ', text: 'two', blocked: true },
    { id: '1.3', state: ' ', text: 'three', blocked: false },
  ],
  workItemType: 'spec',
  deps: { up: [], down: [], cycle: [] },
  epics: [],
  ...extra,
})

test('the list shows each touched spec with its evidence, and picking one reads it', async ($, on) => {
  const state = memory(on)
  on('session.cwd', () => ({ value: '/w' }))
  on('clock.now', () => ({ value: Date.parse('2026-11-20T00:00:00Z') }))
  on('process.run', (_, e) => {
    const key = e.argv.join(' ')
    const answer = (value: unknown) => ({
      value: { exitCode: 0, stdout: JSON.stringify(value), stderr: '', isStdoutTruncated: false, isStderrTruncated: false },
    })

    if (key.startsWith('cq specs status')) {
      return answer({ title: 'Port the panel', stage: 'approved', tasks: { checked: 1, total: 3 } })
    }

    return answer({ nodes: [], tasks: [], sections: [] })
  })
  state.put('rows', [row(2191, 'Port the panel', 'command'), row(7, 'Other')], 'rows-1')

  for (const surface of SURFACES) {
    state.put('picked', null)
    const ui = await $.ui.mount({ ...PANE, surface })

    expect((await ui.find({ key: 'spec-2191' }))?.text).toMatch(/2191 · Port the panel.*approved · 1\/3 · write/)
    expect((await ui.find({ key: 'spec-7' }))?.text).toMatch(/7 · Other.*read/)

    await ui.press({ key: 'spec-2191' })
    await ui.redraw()
    expect(await ui.find({ key: 'back' })).toBeDefined()
    await ui.unmount()
  }
})

test('with no rows the pane says how a spec gets here; with no cq it says cq is missing', async ($, on) => {
  const state = memory(on)
  on('clock.now', () => ({ value: 0 }))
  state.put('rows', [], 'rows-1')
  state.put('busy', '')
  state.put('picked', null)

  for (const surface of SURFACES) {
    state.put('cq', null)
    const ui = await $.ui.mount({ ...PANE, surface })
    expect(await ui.find({ type: 'Text', text: /No spec yet/ })).toBeDefined()
    await ui.unmount()

    state.put('cq', { found: false, version: '', detail: 'spawn cq ENOENT' })
    const missing = await $.ui.mount({ ...PANE, surface })
    expect(await missing.find({ type: 'Text', text: /cq was not found/ })).toBeDefined()
    expect(await missing.find({ type: 'Text', text: /ENOENT/ })).toBeDefined()
    await missing.unmount()
  }
})

test('the detail draws the signals, the block reason, the tasks and one tab at a time', async ($, on) => {
  const state = memory(on)
  on('clock.now', () => ({ value: Date.parse('2026-11-20T00:00:00Z') }))
  state.put('picked', 2191)
  state.put('detail', spec(), 'detail-1')

  for (const surface of SURFACES) {
    state.put('tab', 0)
    const ui = await $.ui.mount({ ...PANE, surface })

    expect((await ui.find({ type: 'Text', text: /stage|blocked · P2/ }))?.text).toBe(
      'blocked · P2 · medium · yesterday · 1/3 tasks · run failed · verifier fail · ana',
    )
    expect(await ui.find({ type: 'Text', text: /blocked 1.2: waits for X/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /\[!\] 1.2 two/ })).toBeDefined()

    await ui.press({ key: 'tab-1' })
    await ui.redraw()
    expect((await ui.find({ type: 'Markdown' }))?.text).toBe('It hurts.')
    await ui.press({ key: 'tab-2' })
    await ui.redraw()
    expect((await ui.find({ type: 'Markdown' }))?.text).toBe('Do it.')
    expect(await ui.find({ type: 'Text', text: /\[!\] 1.2 two/ })).toBe(undefined)
    await ui.unmount()
  }
})

test('the tab list is Overview, the sections, then Dependências; ages and signals read plainly', () => {
  expect(tabsOf(spec())).toEqual(['Overview', 'Problem', 'Proposal', 'Dependências'])
  const now = Date.parse('2026-11-20T00:00:00Z')

  expect(ageLabel('2026-11-20', now)).toBe('today')
  expect(ageLabel('2026-11-10', now)).toBe('10 d ago')
  expect(ageLabel('2026-08-01', now)).toBe('3 months ago')
  expect(ageLabel('junk', now)).toBe('junk')
  expect(signals(spec({ run: '', verifier: '', assignee: '', priority: '', complexity: '' }), now)).toEqual(['blocked', 'yesterday', '1/3 tasks'])
})

test('the Dependências tab draws the edges both ways, the epic block and the member block, and a press opens the neighbour', async ($, on) => {
  const state = memory(on)
  on('clock.now', () => ({ value: Date.parse('2026-11-20T00:00:00Z') }))
  on('session.cwd', () => ({ value: '/w' }))
  on('process.run', () => ({
    value: { exitCode: 2, stdout: '', stderr: 'refused', isStdoutTruncated: false, isStderrTruncated: false },
  }))
  const neighbor = (id: number, extra = {}) => ({ id, title: `T${id}`, phase: 'plans', critical: false, slip: 0, start: '', target: '', ...extra })
  const full = spec({
      deps: { up: [neighbor(9, { phase: 'archive', critical: true, slip: 2, start: '2026-11-01', target: '2026-11-09' })], down: [neighbor(11)], cycle: ['2191', '9', '2191'] },
      epics: [{ epic: 1, title: 'Epic', label: 'S1', group: 2 }],
      composition: {
        progress: { done: 1, total: 2, blocked: 1, ready: 0 },
        groups: [],
        items: [{ label: 'S1', spec: 12, title: 'Member', group: 1, status: 'done', stage: 'archived', after: ['S0'], waitingOn: [] }],
      },
    })

  for (const surface of SURFACES) {
    state.put('picked', 2191)
    state.put('detail', full, 'detail-1')
    state.put('tab', 3)
    const ui = await $.ui.mount({ ...PANE, surface })

    expect((await ui.find({ key: 'dep-up-9' }))?.text).toBe('9 · T9 archived · critical path · +2d · 2026-11-01 → 2026-11-09')
    expect((await ui.find({ key: 'dep-down-11' }))?.text).toBe('11 · T11 ')
    expect((await ui.find({ key: 'epic-1' }))?.text).toBe('S1 1 · Epic wave 2')
    expect((await ui.find({ key: 'member-12' }))?.text).toBe('✓ S1 12 · Member archived · waits for S0')
    expect(await ui.find({ type: 'Text', text: /1\/2 done · 1 blocked/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /cycle: 2191 → 9 → 2191/ })).toBeDefined()

    await ui.press({ key: 'dep-down-11' })
    await ui.redraw()
    expect(await ui.find({ key: 'back' })).toBeDefined()
    await ui.unmount()
  }
})

test('a spec with no edge and no epic says so, above and below', async ($, on) => {
  const state = memory(on)
  on('clock.now', () => ({ value: 0 }))
  state.put('picked', 2191)
  state.put('detail', spec(), 'detail-1')

  for (const surface of SURFACES) {
    state.put('tab', 3)
    const ui = await $.ui.mount({ ...PANE, surface })

    expect(await ui.find({ type: 'Text', text: /nothing above/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /nothing below/ })).toBeDefined()
    await ui.unmount()
  }
})

test('a task and the whole spec go to the composer; a refusal is a toast', async ($, on) => {
  const state = memory(on)
  on('clock.now', () => ({ value: 0 }))
  on('session.cwd', () => ({ value: '/w' }))
  on('process.run', (_, e) => {
    const key = e.argv.join(' ')
    const out = key.startsWith('cq specs show --spec 2191 --task 1.3')
      ? JSON.stringify({ tasks: [{ text: 'three', files: ['a.ts', 'b.ts'], verify: 'make test', subject: '' }] })
      : '{}'

    return { value: { exitCode: 0, stdout: out, stderr: '', isStdoutTruncated: false, isStderrTruncated: false } }
  })
  const filled: string[] = []
  const toasts: string[] = []
  let refusal: 'dialog' | undefined
  on('prompt.fill', (_, e) => {
    filled.push(`${e.mode}:${e.text}`)

    return refusal ? { isFilled: false, refusal, text: '', cursor: 0 } : { isFilled: true, text: e.text, cursor: 0 }
  })
  on('ui.toast', (_, e) => {
    toasts.push(e.text)

    return { value: undefined }
  })

  for (const surface of SURFACES) {
    state.put('picked', 2191)
    state.put('detail', spec(), 'detail-1')
    state.put('tab', 0)
    const ui = await $.ui.mount({ ...PANE, surface })

    await ui.press({ key: 'attach-1.3' })
    await ui.press({ key: 'attach-spec' })
    refusal = 'dialog'
    await ui.press({ key: 'attach-spec' })
    refusal = undefined
    await ui.unmount()
  }

  expect(filled[0]).toBe('insert:spec 2191 task 1.3 — three\nfiles: a.ts, b.ts\nverify: make test\n')
  expect(filled[1]).toBe('insert:spec 2191 — Port the panel\nstage: blocked · tasks: 1/3 · blocked: 1\nnext: 1.3 three\n')
  expect(toasts.length).toBe(2)
})

test('a refusal reads as an instruction', () => {
  expect(refusalNote('dialog')).toMatch(/dialog is open/)
  expect(refusalNote('no_composer')).toMatch(/No prompt box/)
  expect(refusalNote(undefined)).toMatch(/No prompt box/)
})

test('the notes carry the spec and the task as the OpenCode attach did', () => {
  expect(specNote(spec({ blocked: 0, tasks: [] }))).toBe('spec 2191 — Port the panel\nstage: blocked · tasks: 1/3')
  expect(taskNote(7, '1.1', { text: 'x', files: '', verify: '' })).toBe('spec 7 task 1.1 — x\nfiles: -\nverify: -')
})
