import { expect, test } from 'claude-code/testing'

import type { ConfigKey, ConfigSchema } from '../types'
import { describe, encode, isReadOnly, parseSchema, restoreLayer, sectionsOf, shown, sourceOf, targetLayer } from './config'

const key = (extra: Partial<ConfigKey> & Pick<ConfigKey, 'key' | 'type'>): ConfigKey => ({
  default: null,
  category: 'build',
  scope: 'either',
  reader: 'cq specs',
  editable: true,
  copy: { en: { title: `Title of ${extra.key}`, summary: `Summary of ${extra.key}` }, 'pt-BR': { title: 't', summary: 's' } },
  ...extra,
})

const SCHEMA: ConfigSchema = {
  categories: [
    { id: 'build', title: { en: 'Build', 'pt-BR': 'Construir' } },
    { id: 'empty', title: { en: 'Empty', 'pt-BR': 'Vazio' } },
    { id: 'git', title: { en: 'Git', 'pt-BR': 'Git' } },
  ],
  keys: [
    key({ key: 'specs.mode', type: 'enum', choices: ['a', 'b'], default: 'a' }),
    key({ key: 'specs.limit', type: 'integer', default: 3 }),
    key({ key: 'git.name', type: 'string', category: 'git', scope: 'project' }),
    key({ key: 'shared.hooks', type: 'object', category: 'git', editable: false }),
  ],
  values: { 'specs.limit': { value: 5, source: 'local' }, 'git.name': { value: 'x', source: 'repository' } },
  layerPaths: { project: '/p/.agents/quenching.json', local: '/p/.agents/quenching.local.json' },
}

test('the keys are grouped by category, empty categories are left out', () => {
  expect(sectionsOf(SCHEMA).map(section => [section.title, section.keys.map(one => one.key)])).toEqual([
    ['Build', ['specs.mode', 'specs.limit']],
    ['Git', ['git.name', 'shared.hooks']],
  ])
})

test('a field becomes the JSON the cq validates', () => {
  expect(encode({ type: 'integer' }, ' 7 ')).toBe('7')
  expect(encode({ type: 'string' }, 'hi "there"')).toBe('"hi \\"there\\""')
  expect(encode({ type: 'paths' }, 'a, b ,,c')).toBe('["a","b","c"]')
  expect(encode({ type: 'strings' }, '')).toBe('[]')
  expect(shown(['a', 'b'])).toBe('a, b')
  expect(shown({ a: 1 })).toBe('{"a":1}')
  expect(shown(null)).toBe('')
})

test('a project key always writes to the project; restore removes from the layer that gave the value', () => {
  expect(targetLayer({ scope: 'project' }, 'local')).toBe('project')
  expect(targetLayer({ scope: 'machine' }, 'local')).toBe('local')
  expect(restoreLayer('local')).toBe('local')
  expect(restoreLayer('repository')).toBe('project')
  expect(restoreLayer('default')).toBe(undefined)
  expect(restoreLayer('user')).toBe(undefined)
  expect(sourceOf(SCHEMA, SCHEMA.keys[1]!)).toBe('local')
  expect(sourceOf(SCHEMA, SCHEMA.keys[0]!)).toBe('default')
  expect(isReadOnly(SCHEMA.keys[3]!)).toBe(true)
})

test('the schema is read from the cq text, and anything else is nothing', () => {
  expect(parseSchema(JSON.stringify(SCHEMA))?.keys.length).toBe(4)
  expect(parseSchema('nope')).toBe(undefined)
  expect(parseSchema('{"keys":[]}')).toBe(undefined)
  expect(describe(SCHEMA.keys[0]!)).toBe(
    'Summary of specs.mode\nDefault: a\nRead by: cq specs\nScope: either: the project wins; local fills what it leaves out\nspecs.mode',
  )
})

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

type On = Parameters<Extract<Parameters<typeof test>[1], (...args: any) => any>>[1]

/** A key is answered with its seed until the plugin writes it; then the engine's own state answers. */
function memory(on: On) {
  const seeds = new Map<string, unknown>()

  on('state.get', (_, e, next) => (seeds.has(e.key) ? { value: { value: seeds.get(e.key), version: 1 } } : next(e)))
  on('state.set', (_, e, next) => {
    seeds.delete(e.key)

    return next(e)
  })

  return { put: (key: string, value: unknown, shape?: string) => seeds.set(key, shape ? { shape, value } : value) }
}

const done = (exitCode: number, stdout: string, stderr = '') => ({
  value: { exitCode, stdout, stderr, isStdoutTruncated: false, isStderrTruncated: false },
})

/** A cq that serves the schema and records every config write; `bad` is refused with a reason. */
function cq(on: On) {
  const writes: string[] = []

  on('process.run', (_, e) => {
    const key = e.argv.join(' ')

    if (key.startsWith('cq config schema')) {
      return done(0, JSON.stringify(SCHEMA))
    }

    if (key.startsWith('cq config set') || key.startsWith('cq config unset')) {
      writes.push(key)

      return key.includes('9999') ? done(2, '{"message":"above the maximum","remedy":"use 10"}') : done(0, '{"ok":true}')
    }

    return done(2, '', 'refused')
  })

  return writes
}

function setup(on: On) {
  const state = memory(on)
  const writes = cq(on)
  const toasts: string[] = []
  on('clock.now', () => ({ value: 0 }))
  on('session.cwd', () => ({ value: '/w' }))
  on('ui.toast', (_, e) => {
    toasts.push(e.text)

    return { value: undefined }
  })

  return { state, writes, toasts }
}

test('the Configuração view groups keys by category with the layer badge, and read-only catalogues name the file', async ($, on) => {
  const { state } = setup(on)

  for (const surface of SURFACES) {
    state.put('view', 'config')
    state.put('config', SCHEMA, 'config-1')
    const ui = await $.ui.mount({ ...PANE, surface })

    expect(await ui.find({ type: 'Text', text: /^Build$/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /^Git$/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /^Empty$/ })).toBe(undefined)
    expect((await ui.find({ key: 'row-specs.limit' }))?.text).toContain('Title of specs.limit [Local]')
    expect((await ui.find({ key: 'row-git.name' }))?.text).toContain('[Project]')
    expect((await ui.find({ key: 'row-specs.mode' }))?.text).toContain('[Default]')
    expect((await ui.find({ key: 'row-shared.hooks' }))?.text).toContain('read-only here: edit /p/.agents/quenching.json')
    expect(await ui.find({ key: 'cfg-shared.hooks' })).toBe(undefined)
    await ui.unmount()
  }
})

test('a value is written through cq config set on the chosen layer, and read back', async ($, on) => {
  const { state, writes, toasts } = setup(on)

  for (const surface of SURFACES) {
    writes.length = 0
    state.put('view', 'config')
    state.put('config', SCHEMA, 'config-1')
    state.put('layer', 'project')
    const ui = await $.ui.mount({ ...PANE, surface })

    await ui.input({ key: 'cfg-specs.limit', text: '9', kind: 'submit' })
    await ui.select({ key: 'layer', value: 'local' })
    await ui.input({ key: 'cfg-specs.limit', text: '8', kind: 'submit' })
    await ui.select({ key: 'cfg-specs.mode', value: 'b' })
    await ui.unmount()

    expect(writes).toEqual([
      'cq config set specs.limit 9 --layer project --json',
      'cq config set specs.limit 8 --layer local --json',
      'cq config set specs.mode "b" --layer local --json',
    ])
  }
  expect(toasts[0]).toBe('specs.limit → Project')
})

test('a project key goes to the project even with Local selected; restore unsets the layer that gave the value', async ($, on) => {
  const { state, writes } = setup(on)
  state.put('view', 'config')
  state.put('config', SCHEMA, 'config-1')
  state.put('layer', 'local')

  for (const surface of SURFACES) {
    writes.length = 0
    const ui = await $.ui.mount({ ...PANE, surface })

    await ui.input({ key: 'cfg-git.name', text: 'y', kind: 'submit' })
    await ui.press({ key: 'restore-specs.limit' })
    await ui.press({ key: 'restore-git.name' })
    expect(await ui.find({ key: 'restore-specs.mode' })).toBe(undefined)
    await ui.unmount()

    expect(writes).toEqual([
      'cq config set git.name "y" --layer project --json',
      'cq config unset specs.limit --layer local --json',
      'cq config unset git.name --layer project --json',
    ])
    state.put('view', 'config')
    state.put('config', SCHEMA, 'config-1')
    state.put('layer', 'local')
  }
})

test('a value the cq refuses is a toast with its reason, never a silent write', async ($, on) => {
  const { state, toasts } = setup(on)
  state.put('view', 'config')
  state.put('config', SCHEMA, 'config-1')

  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  await ui.input({ key: 'cfg-specs.limit', text: '9999', kind: 'submit' })
  await ui.unmount()

  expect(toasts).toEqual(['Not saved: above the maximum — use 10'])
})
