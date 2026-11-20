import { expect, test } from 'claude-code/testing'

import { createCq, limiter, singleFlight } from './cq'
import type { Run, Runner } from './cq'

const ok = (stdout: string): Run => ({ code: 0, stdout, stderr: '' })
const settle = async () => {
  for (let turn = 0; turn < 5; turn += 1) {
    await Promise.resolve()
  }
}

test('a read appends --json and parses the payload', async () => {
  const seen: string[][] = []
  const cq = createCq(async argv => {
    seen.push(argv)

    return ok('{"id":7}')
  })

  expect(await cq.json('/w', ['specs', 'status', '--spec', '7'])).toEqual({ id: 7 })
  expect(seen).toEqual([['cq', 'specs', 'status', '--spec', '7', '--json']])
})

test('exit 1 and output that is not JSON read as nothing; exit 1 still hands a partial payload over', async () => {
  const cq = createCq(async argv => (argv.includes('a') ? { code: 1, stdout: '{"cycle":["1"]}', stderr: '' } : ok('nope')))

  expect(await cq.json('/w', ['a'])).toBe(undefined)
  expect(await cq.jsonPartial('/w', ['a'])).toEqual({ cycle: ['1'] })
  expect(await cq.json('/w', ['b'])).toBe(undefined)
})

test('a missing cq is a state, not a crash', async () => {
  const cq = createCq(async () => ({ code: -1, stdout: '', stderr: 'spawn cq ENOENT' }))

  expect(await cq.probe('/w')).toEqual({ found: false, version: '', detail: 'spawn cq ENOENT' })
  expect(await cq.json('/w', ['specs', 'list'])).toBe(undefined)
  expect((await cq.configSchema('/w')).ok).toBe(false)
})

test('the version is read from cq --version', async () => {
  const cq = createCq(async () => ok('7.8.0\n'))

  expect(await cq.probe('/w')).toEqual({ found: true, version: '7.8.0', detail: '' })
})

test('the limiter holds the cap and the queue drains in order', async () => {
  const run = limiter(2)
  let active = 0
  let peak = 0
  const order: number[] = []
  const task = (n: number) => async () => {
    active += 1
    peak = Math.max(peak, active)
    await settle()
    active -= 1
    order.push(n)
  }

  await Promise.all([1, 2, 3, 4, 5].map(n => run(task(n))))

  expect(peak).toBe(2)
  expect(order).toEqual([1, 2, 3, 4, 5])
})

test('the same read in flight is one process', async () => {
  let spawned = 0
  const runner: Runner = async () => {
    spawned += 1
    await settle()

    return ok('{}')
  }
  const cq = createCq(runner)

  await Promise.all([cq.json('/w', ['specs', 'list']), cq.json('/w', ['specs', 'list'])])
  await cq.json('/w', ['specs', 'list'])

  expect(spawned).toBe(2)
  expect(cq.stats.peak).toBe(1)
})

test('single flight lets the next ask start once the first settled', async () => {
  const once = singleFlight<number>()
  let n = 0

  expect(await once('k', async () => ++n)).toBe(1)
  expect(await once('k', async () => ++n)).toBe(2)
})

test('config writes go through cq config set|unset with the layer and report a refusal', async () => {
  const seen: string[][] = []
  const cq = createCq(async argv => {
    seen.push(argv)

    return argv.includes('bad')
      ? { code: 2, stdout: '{"message":"not a key","remedy":"see schema"}', stderr: '' }
      : ok('{"ok":true}')
  })

  expect(await cq.configWrite('/w', 'a.b', 'local', '3')).toEqual({ ok: true, message: '' })
  expect(await cq.configWrite('/w', 'a.b', 'project', null)).toEqual({ ok: true, message: '' })
  expect(await cq.configWrite('/w', 'bad', 'project', '1')).toEqual({ ok: false, message: 'not a key — see schema' })
  expect(seen[0]).toEqual(['cq', 'config', 'set', 'a.b', '3', '--layer', 'local', '--json'])
  expect(seen[1]).toEqual(['cq', 'config', 'unset', 'a.b', '--layer', 'project', '--json'])
})

test('git reads go through the same cap and return trimmed stdout, or nothing on a refusal', async () => {
  const cq = createCq(async argv => (argv[1] === 'rev-parse' ? ok('abc123\n') : { code: 128, stdout: '', stderr: 'no' }))

  expect(await cq.git('/w', ['rev-parse', 'HEAD'])).toBe('abc123')
  expect(await cq.git('/w', ['branch'])).toBe(undefined)
})
