import { expect, test } from 'claude-code/testing'

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

const done = (exitCode: number, stdout: string, stderr = '') => ({
  value: { exitCode, stdout, stderr, isStdoutTruncated: false, isStderrTruncated: false },
})
const answer = (value: unknown) => done(0, JSON.stringify(value))

test('an empty session draws the empty state, on every surface', async ($, on) => {
  on('command.register', () => ({ value: { command: 'quenching-vitrine' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('clock.now', () => ({ value: 1000 }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...PANE, surface })

    expect(await ui.find({ type: 'Text', text: /No spec yet/ })).toBeDefined()
    await ui.unmount()
  }
})

test('a cq specs call enters the ledger, and the command lists it from the plans', async ($, on) => {
  on('command.register', () => ({ value: { command: 'quenching-vitrine' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('session.cwd', () => ({ value: '/work' }))
  on('session.messages', () => ({ value: [{ role: 'user', text: 'look at spec 888', toolUses: [] }] }))
  on('clock.now', () => ({ value: 1000 }))
  on('tool.call', () => ({ result: {} }))
  on('process.run', (_, e) => {
    const key = e.argv.join(' ')

    if (key === 'cq --version') {
      return done(0, '7.8.0\n')
    }

    if (key.startsWith('cq specs list --phase plans')) {
      return answer({ specs: [{ id: 777, title: 'Seven', stage: 'ready', phase: 'plans', tasks: { checked: 0, total: 2 } }] })
    }

    if (key.startsWith('cq specs list --lean')) {
      return answer({ specs: [{ id: 777 }, { id: 888 }] })
    }

    return done(2, '', 'refused')
  })

  await $.session.start({ cwd: '/work', surface: 'desktop', isInteractive: true })
  await $.tool.call({ tool: 'Bash', command: 'cq specs show 777 --json' })
  await $.tool.call({ tool: 'Bash', command: 'ls' })
  await $.command.run({
    command: 'quenching-vitrine',
    args: '',
    origin: { kind: 'composer' },
    presentation: { isFullscreen: false, columns: 80 },
  })

  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...PANE, surface })

    expect((await ui.find({ key: 'spec-777' }))?.text).toMatch(/777 · Seven.*ready · 0\/2 · read/)
    // 888 is cited in the conversation but is no plan the cq can read: it is not listed.
    expect(await ui.find({ key: 'spec-888' })).toBe(undefined)
    await ui.unmount()
  }
})

test('a quenching MCP call enters the ledger as well', async ($, on) => {
  on('clock.now', () => ({ value: 1000 }))
  on('tool.call', () => ({ result: {} }))
  on('state.get', (_, e, next) => next(e))
  let written = ''
  on('state.set', (_, e, next) => {
    written = JSON.stringify(e.value)

    return next(e)
  })

  await $.tool.call({ tool: 'mcp__quenching__specs_status', spec: 888 })

  expect(written).toContain('"id":888')
  expect(written).toContain('"kind":"read"')
})
