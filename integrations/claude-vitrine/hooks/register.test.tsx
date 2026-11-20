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

test('the command opens the pane and the pane draws, on every surface', async ($, on) => {
  on('command.register', () => ({ value: { command: 'quenching-vitrine' } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...PANE, surface })

    expect(await ui.find({ type: 'Text', text: /No specs yet/ })).toBeDefined()
    await ui.unmount()
  }
})
