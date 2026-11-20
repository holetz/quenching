import type { Register } from 'claude-code'

import { toolHits } from './ledger'
import { drawPane, record, refresh } from './pane'

const PANE = 'quenching-vitrine'
const TITLE = 'Specs'

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'quenching-vitrine',
      description: 'Open the quenching Specs pane: the specs this session touched, their dependencies and the configuration',
    })

    return next(e)
  })

  on('command.run', { command: 'quenching-vitrine' }, async $ => {
    await $.ui.open({ id: PANE, title: TITLE })
    // The pane is already up: the rows arrive when the reads settle, and the state redraws it.
    await refresh($).catch(() => undefined)

    return { text: 'Specs pane opened.' }
  })

  on('tool.call', async ($, e, next) => {
    const { tool, ...input } = e as unknown as { tool: string } & Record<string, unknown>
    const hits = toolHits(tool, input)

    if (hits.length > 0) {
      await record($, hits)
    }

    return next(e)
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'Pane', requestId: PANE }, ($, e) => drawPane($, e))
}
