import { expect, test } from 'claude-code/testing'

import { createCq } from './cq'
import type { Run } from './cq'
import { createSpecs, frontmatter, priorityOf, split, stageOf } from './specs'

type Answers = Record<string, Run | undefined>

/** A fake cq: each answer is keyed by the argv after `cq`, joined with spaces. */
function fake(answers: Answers) {
  const seen: string[] = []
  const cq = createCq(async argv => {
    const key = argv.slice(argv[0] === 'cq' ? 1 : 0).join(' ')
    seen.push(key)

    return answers[key] ?? { code: 2, stdout: '', stderr: 'refused' }
  })

  return { cq, seen, specs: createSpecs(cq) }
}

const ok = (value: unknown): Run => ({ code: 0, stdout: JSON.stringify(value), stderr: '' })

const DOCUMENT = `---
title: T
tags: ["front:plugin", "x"]
assignee: "ana"
workItemType: spec
---

# T

<!-- mold comment -->

## Problem

It hurts.

## Proposal

Do it.
`

test('the document is cut at its level-2 headings and the mold comments are dropped', () => {
  expect(split(DOCUMENT)).toEqual([
    { heading: 'Problem', body: 'It hurts.' },
    { heading: 'Proposal', body: 'Do it.' },
  ])
  expect(split('plain text')).toEqual([{ heading: 'Document', body: 'plain text' }])
  expect(frontmatter(DOCUMENT).assignee).toBe('"ana"')
})

test('the stage comes from the records: archive, a blocked task and review win over the raw stage', () => {
  expect(stageOf({ stage: 'approved', phase: 'archive' })).toBe('archived')
  expect(stageOf({ stage: 'approved', tasks: { blocked: 1 } })).toBe('blocked')
  expect(stageOf({ stage: 'approved', records: { reviewed: { x: 1 } } })).toBe('review')
  expect(stageOf({ stage: 'approved' })).toBe('approved')
  expect(stageOf({ stage: 'nonsense' })).toBe('captured')
})

test('priority is the criticality band, else the 1 to 4 level, else nothing', () => {
  expect(priorityOf({ criticality: 'high' })).toEqual({ label: 'P2', hint: 'P2 · high' })
  expect(priorityOf({ level: 3 })).toEqual({ label: 'P3', hint: 'P3 · level' })
  expect(priorityOf({ complexity: 'low' })).toEqual({ label: '', hint: '' })
})

test('the list reads plans once, keeps rows when a later read fails, and normalises a row', async () => {
  const row = { id: 5, title: 'Five', stage: 'ready', phase: 'plans', date: '2026-11-01', tasks: { checked: 1, blocked: 0, total: 3 } }
  const { specs, seen } = fake({ 'specs list --phase plans --json': ok({ specs: [row] }) })

  const first = await specs.list('/w')
  await specs.list('/w')

  expect(first).toEqual([
    { id: 5, title: 'Five', stage: 'ready', phase: 'plans', date: '2026-11-01', checked: 1, blocked: 0, total: 3, work: '', run: '', workItemType: '' },
  ])
  expect(seen.length).toBe(1)

  specs.forget()
  const dead = fake({})
  expect(await dead.specs.list('/w')).toEqual([])
})

test('the detail joins status, show, the full document and the dependency graph, both ways', async () => {
  const graph = {
    nodes: [
      { id: '10', title: 'Ten', phase: 'plans', dependsOn: ['9'], critical: true, slipDays: 2, start: '2026-11-01', target: '2026-11-09' },
      { id: '9', title: 'Nine', phase: 'archive', dependsOn: [] },
      { id: '11', title: 'Eleven', phase: 'plans', dependsOn: ['10'] },
      { id: '1', title: 'Epic', phase: 'plans', dependsOn: [] },
    ],
    cycle: [],
    composites: { '10': [{ epic: '1', label: 'S1', group: 2 }, { epic: '404', label: 'x' }] },
  }
  const status = {
    title: 'Ten',
    stage: 'approved',
    phase: 'plans',
    date: '2026-11-02',
    records: { priority: { criticality: 'medium', complexity: 'high' }, run: { state: 'failed', verifier: 'fail' }, pr: { number: 3, url: 'https://x/3' }, branch: { work: 'plan/10-ten' } },
    ready: { ok: false, missing: ['Risks'] },
    tasks: { checked: 1, blocked: 1, total: 3, blockedTasks: [{ id: '1.2', text: '1.2 do — blocked: waits for X' }] },
    composition: { progress: { done: 1, total: 2, blocked: 0, ready: 1 }, groups: [], items: [{ label: 'S1', spec: 10, title: 'Ten', group: 1, status: 'done', stage: 'archived', after: [], waitingOn: [] }] },
  }
  const { specs } = fake({
    'specs schedule --all --json': ok(graph),
    'specs status --spec 10 --json': ok(status),
    'specs show --spec 10 --json': ok({ tasks: [{ id: '1.1', state: 'x', text: 'one' }, { id: '1.2', state: ' ', text: 'two' }] }),
    'specs show --spec 10 --full --json': ok({ document: DOCUMENT }),
  })

  const detail = await specs.detail('/w', 10)

  expect(detail.priority).toBe('P3')
  expect(detail.complexity).toBe('high')
  expect(detail.blockedReason).toBe('waits for X')
  expect(detail.run).toBe('failed')
  expect(detail.verifier).toBe('fail')
  expect(detail.assignee).toBe('ana')
  expect(detail.tags).toEqual(['front:plugin', 'x'])
  expect(detail.sections.map(one => one.heading)).toEqual(['Problem', 'Proposal'])
  expect(detail.tasks.map(one => [one.id, one.blocked])).toEqual([['1.1', false], ['1.2', true]])
  expect(detail.deps.up.map(one => one.id)).toEqual([9])
  expect(detail.deps.up[0]?.phase).toBe('archive')
  expect(detail.deps.down.map(one => one.id)).toEqual([11])
  expect(detail.epics).toEqual([{ epic: 1, title: 'Epic', label: 'S1', group: 2 }])
  expect(detail.composition?.items[0]?.label).toBe('S1')
})

test('a cycle exits 1 with its payload and still reaches the detail; an old cq falls back to the open graph', async () => {
  const cyc = { code: 1, stdout: JSON.stringify({ nodes: [{ id: '2', title: 'Two', dependsOn: ['3'] }], cycle: ['2', '3', '2'] }), stderr: '' }
  const one = fake({ 'specs schedule --all --json': cyc, 'specs status --spec 2 --json': ok({ title: 'Two' }) })

  expect((await one.specs.detail('/w', 2)).deps.cycle).toEqual(['2', '3', '2'])

  const old = fake({
    'specs schedule --json': ok({ nodes: [{ id: '2', title: 'Two', dependsOn: [] }, { id: '4', title: 'Four', dependsOn: ['2'] }] }),
    'specs status --spec 2 --json': ok({ title: 'Two' }),
  })

  expect((await old.specs.detail('/w', 2)).deps.down.map(node => node.id)).toEqual([4])
})

test('a task read keeps the real files and drops the empty marker', async () => {
  const { specs } = fake({
    'specs show --spec 7 --task 1.1 --json': ok({ tasks: [{ text: 'x', files: ['a.ts', '[]', ' '], verify: 'v', subject: 's' }] }),
  })

  expect(await specs.task('/w', 7, '1.1')).toEqual({ text: 'x', files: 'a.ts', verify: 'v', subject: 's' })
})

test('the branch and the commit name their spec, and the commit answer is cached by sha', async () => {
  let finds = 0
  const cq = createCq(async argv => {
    const key = argv.join(' ')

    if (key === 'git branch --show-current') {
      return { code: 0, stdout: 'plan/12-x\n', stderr: '' }
    }

    if (key === 'git rev-parse HEAD') {
      return { code: 0, stdout: 'abc\n', stderr: '' }
    }
    finds += 1

    return ok({ id: 12 })
  })
  const specs = createSpecs(cq)

  expect(await specs.branchSpec('/w')).toBe(12)
  expect(await specs.commitSpec('/w')).toBe(12)
  expect(await specs.commitSpec('/w')).toBe(12)
  expect(finds).toBe(2)
})
