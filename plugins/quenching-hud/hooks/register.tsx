import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { HudLine } from '../types'
import { basename, formatLine, lineFromStatus, specIdFromBranch } from './hud'

const line = atom({ plugin: 'quenching-hud', key: 'line' } as const, null as HudLine | null)

async function refresh($: EngineInterface) {
  try {
    const cwd = await $.session.cwd()
    const branch = await $.process.run(['git', 'branch', '--show-current'], { cwd })
    const id = branch.exitCode === 0 ? specIdFromBranch(branch.stdout) : null

    if (id === null) {
      await update($, line, () => null)

      return
    }

    const status = await $.process.run(['cq', 'specs', 'status', '--spec', String(id), '--no-fetch', '--json'], { cwd })
    const next = status.exitCode === 0 ? lineFromStatus(id, status.stdout, basename(cwd)) : null
    await update($, line, () => next)
  } catch {
    await update($, line, () => null)
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await refresh($)

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    await refresh($)

    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const current = await read($, line)

    if (current === null) {
      return next(e)
    }

    const { Box, Text } = $.ui.resolve(e)

    return (
      <Box>
        <Text dimColor>{formatLine(current)}</Text>
      </Box>
    )
  })
}
