import { expect, test } from 'claude-code/testing'

import { basename, formatLine, lineFromStatus, specIdFromBranch } from './hud'

test('a plan branch yields its spec id', () => {
  expect(specIdFromBranch('plan/1521-plugin-quenching-hud-minimo')).toBe(1521)
  expect(specIdFromBranch('plan/7-x\n')).toBe(7)
})

test('a branch outside plan/<id>- yields no id, so no argv is built', () => {
  expect(specIdFromBranch('main')).toBe(null)
  expect(specIdFromBranch('')).toBe(null)
  expect(specIdFromBranch('plan/12;rm -rf')).toBe(null)
  expect(specIdFromBranch('feature/plan/12-x')).toBe(null)
})

test('the line carries id, stage, checked/total and the worktree', () => {
  const line = lineFromStatus(1521, JSON.stringify({ stage: 'approved', tasks: { checked: 3, total: 7 } }), 'wt')

  expect(line).toEqual({ id: 1521, stage: 'approved', checked: 3, total: 7, worktree: 'wt' })
  expect(formatLine(line!)).toBe('spec 1521 · approved · 3/7 · wt')
})

test('output that is not a status payload yields no line', () => {
  expect(lineFromStatus(1, 'not json', 'wt')).toBe(null)
  expect(lineFromStatus(1, JSON.stringify({ stage: 'x' }), 'wt')).toBe(null)
})

test('the worktree is the last path segment', () => {
  expect(basename('/home/u/repo-1521/')).toBe('repo-1521')
})
