import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { LedgerEntry, View } from '../types'
import { createCq } from './cq'
import type { Run } from './cq'
import { harvest, toolHits, touch, touchedRows } from './ledger'
import { createSpecs } from './specs'

const PANE = 'quenching-vitrine'
const TITLE = 'Specs'

const view = atom({ plugin: 'quenching-vitrine', key: 'view' } as const, 'specs' as View)
// Change the tag when an entry's fields change: it declines what an earlier version stored.
const ledger = atom({ plugin: 'quenching-vitrine', key: 'ledger' } as const, [] as LedgerEntry[], { shape: 'ledger-1' })

/** A `$.process.run` that never throws: a missing `cq` is an exit code and a message. */
function runnerOf($: EngineInterface) {
  return async (argv: string[], cwd: string, timeoutMs: number): Promise<Run> => {
    try {
      const run = await $.process.run(argv, { cwd, timeoutMs })

      return { code: run.exitCode, stdout: run.stdout, stderr: run.stderr }
    } catch (error) {
      return { code: -1, stdout: '', stderr: String(error) }
    }
  }
}

/** Re-reads the conversation and merges what it names into the ledger: what a reload lost comes back. */
async function rebuild($: EngineInterface, specs: ReturnType<typeof createSpecs>, cwd: string) {
  const messages = await $.session.messages()
  const found = harvest(messages, await specs.known(cwd))
  const now = await $.clock.now()

  await update($, ledger, entries =>
    found.reduce((all, hit, index) => touch(all, hit.id, hit.kind, now - (found.length - index)), entries),
  )
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'quenching-vitrine',
      description: 'Open the quenching Specs pane: the specs this session touched, their dependencies and the configuration',
    })

    return next(e)
  })

  on('command.run', { command: 'quenching-vitrine' }, async $ => {
    const cwd = await $.session.cwd()
    const cq = createCq(runnerOf($))
    const specs = createSpecs(cq)

    try {
      await rebuild($, specs, cwd)
      await touchedRows(specs, cwd, await read($, ledger), await $.clock.now())
    } catch {
      // The pane opens either way: an unreadable conversation leaves the ledger as it was.
    }
    await $.ui.open({ id: PANE, title: TITLE })

    return { text: 'Specs pane opened.' }
  })

  on('tool.call', async ($, e, next) => {
    const { tool, ...input } = e as unknown as { tool: string } & Record<string, unknown>
    const hits = toolHits(tool, input)

    if (hits.length > 0) {
      const now = await $.clock.now()
      await update($, ledger, entries => hits.reduce((all, hit) => touch(all, hit.id, hit.kind, now), entries))
    }

    return next(e)
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const current = await read($, view)
    const entries = await read($, ledger)

    return (
      <Box flexDirection="column">
        <Text dimColor>
          No specs yet ({current}, {entries.length}).
        </Text>
      </Box>
    )
  })
}
