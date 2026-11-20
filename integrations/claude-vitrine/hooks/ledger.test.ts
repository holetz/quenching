import { expect, test } from 'claude-code/testing'

import { harvest, mentions, mcpHit, ordered, parseCommand, toolHits, touch, touchedRows } from './ledger'
import type { Specs } from './specs'

test('a cq specs command names its spec with the weight of its verb', () => {
  expect(parseCommand('cq specs status --spec 2191 --json').hits).toEqual([{ id: 2191, kind: 'read' }])
  expect(parseCommand('.agents/quenching/bin/cq specs task --check 1.1 --spec 2191').hits).toEqual([])
  expect(parseCommand('cq specs record 2191 approved').hits).toEqual([{ id: 2191, kind: 'command' }])
  expect(parseCommand('cq specs show 1000 && cq specs record 1000 x').hits).toEqual([{ id: 1000, kind: 'command' }])
  expect(parseCommand('ls').hits).toEqual([])
  expect(parseCommand('cq git commit --subject x').commit).toBe(true)
})

test('an explicit mention always counts; a bare id only when loose and known; a date never does', () => {
  const known = new Set([2191])

  expect(mentions('see spec 1985 and #2000', known, false)).toEqual([1985, 2000])
  expect(mentions('what about 2191?', known, true)).toEqual([2191])
  expect(mentions('what about 2191?', known, false)).toEqual([])
  expect(mentions('on 2026-10-11', new Set([2026]), true)).toEqual([])
})

test('an MCP quenching tool names its spec; any other tool names nothing', () => {
  expect(mcpHit('mcp__quenching__specs_status', { spec: 2191 })).toEqual({ id: 2191, kind: 'read' })
  expect(mcpHit('mcp__quenching__specs_record', { spec: '2191' })).toEqual({ id: 2191, kind: 'command' })
  expect(mcpHit('mcp__quenching__specs_next', { epic: 5 })).toEqual({ id: 5, kind: 'read' })
  expect(mcpHit('mcp__other__specs_status', { spec: 1 })).toBe(undefined)
  expect(mcpHit('mcp__quenching__specs_list', {})).toBe(undefined)
  expect(toolHits('Bash', { command: 'cq specs show 777' })).toEqual([{ id: 777, kind: 'read' }])
  expect(toolHits('Read', { file_path: 'cq specs show 777' })).toEqual([])
})

test('the conversation is harvested: the person, the agent and the calls, the heavier fact wins', () => {
  const found = harvest(
    [
      { role: 'user', text: 'look at 2191 and spec 1500', toolUses: [] },
      { role: 'assistant', text: 'Reading 2191 now, also 3000', toolUses: [{ tool: 'Bash', input: { command: 'cq specs record 2191 x' } }] },
      { role: 'assistant', text: '', toolUses: [{ tool: 'mcp__quenching__specs_show', input: { spec: 1500 } }] },
    ],
    new Set([2191]),
  )

  expect(Object.fromEntries(found.map(hit => [hit.id, hit.kind]))).toEqual({ 2191: 'command', 1500: 'read' })
})

test('touching keeps the stronger fact and the newer of equals, and orders by weight then time', () => {
  let ledger = touch([], 1, 'commit', 10)
  ledger = touch(ledger, 1, 'read', 20)
  ledger = touch(ledger, 2, 'read', 30)
  ledger = touch(ledger, 3, 'read', 40)
  ledger = touch(ledger, 2, 'read', 50)

  expect(ledger.find(entry => entry.id === 1)).toEqual({ id: 1, kind: 'commit', at: 10 })
  expect(ordered(ledger).map(entry => entry.id)).toEqual([1, 2, 3])
})

test('the pane rows join the branch and commit evidence and read a spec that left plans', async () => {
  const row = (id: number) => ({ id, title: `T${id}`, stage: 'ready', phase: 'plans', date: '', checked: 0, blocked: 0, total: 0, work: '', run: '', workItemType: '' })
  const specs = {
    branchSpec: async () => 10,
    commitSpec: async () => undefined,
    list: async () => [row(10), row(11)],
    offRow: async (_: string, id: number) => (id === 99 ? { ...row(99), phase: 'archive', stage: 'archived' } : undefined),
  } as unknown as Specs

  const rows = await touchedRows(
    specs,
    '/w',
    [{ id: 11, kind: 'read', at: 5 }, { id: 99, kind: 'command', at: 6 }, { id: 404, kind: 'mention', at: 7 }],
    100,
  )

  expect(rows.map(one => [one.id, one.kind])).toEqual([[10, 'worktree'], [99, 'command'], [11, 'read']])
})
