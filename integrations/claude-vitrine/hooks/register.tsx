import { atom, read } from 'claude-code'
import type { Register } from 'claude-code'

import type { View } from '../types'

const PANE = 'quenching-vitrine'
const TITLE = 'Specs'

const view = atom({ plugin: 'quenching-vitrine', key: 'view' } as const, 'specs' as View)

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

    return { text: 'Specs pane opened.' }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const current = await read($, view)

    return (
      <Box flexDirection="column">
        <Text dimColor>No specs yet ({current}).</Text>
      </Box>
    )
  })
}
