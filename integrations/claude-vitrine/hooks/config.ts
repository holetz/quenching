import type { ConfigKey, ConfigLayer, ConfigSchema } from '../types'

/** The layer badge words, by the `source` `cq config schema --values` reports for a value. */
export const SOURCE_LABEL: Record<string, string> = {
  default: 'Default',
  user: 'User',
  repository: 'Project',
  branch: 'Branch',
  local: 'Local',
}

/** The schema `cq config schema --values --json` printed, or nothing when it is not one. */
export function parseSchema(json: string): ConfigSchema | undefined {
  try {
    const value = JSON.parse(json) as Partial<ConfigSchema>

    return Array.isArray(value.categories) && Array.isArray(value.keys) && value.values && typeof value.values === 'object'
      ? (value as ConfigSchema)
      : undefined
  } catch {
    return undefined
  }
}

/** A value as a field shows it. */
export function shown(value: unknown): string {
  if (value === null || value === undefined) {
    return ''
  }

  if (Array.isArray(value)) {
    return value.join(', ')
  }

  if (typeof value === 'object') {
    return JSON.stringify(value)
  }

  return String(value)
}

/** A field's text as the JSON `cq config set` validates. */
export function encode(entry: Pick<ConfigKey, 'type'>, text: string): string {
  const raw = text.trim()

  if (entry.type === 'paths' || entry.type === 'strings') {
    return JSON.stringify(raw ? raw.split(',').map(item => item.trim()).filter(Boolean) : [])
  }

  if (entry.type === 'integer' || entry.type === 'number') {
    return raw
  }

  return JSON.stringify(raw)
}

/** The keys grouped by task category, in the registry's order; a category with no key is left out. */
export function sectionsOf(schema: ConfigSchema): { id: string; title: string; keys: ConfigKey[] }[] {
  return schema.categories
    .map(category => ({
      id: category.id,
      title: category.title.en,
      keys: schema.keys.filter(entry => entry.category === category.id),
    }))
    .filter(section => section.keys.length > 0)
}

export const sourceOf = (schema: ConfigSchema, entry: ConfigKey): string => schema.values[entry.key]?.source ?? 'default'

/** The layer a write goes to: a project key always goes to the project, whatever the selector says. */
export function targetLayer(entry: Pick<ConfigKey, 'scope'>, layer: ConfigLayer): ConfigLayer {
  return entry.scope === 'project' ? 'project' : layer
}

/** Restore default removes the value from the layer that gave it; a default or user value has nothing to remove. */
export function restoreLayer(source: string): ConfigLayer | undefined {
  return source === 'local' ? 'local' : source === 'repository' ? 'project' : undefined
}

/** A structured catalogue (hooks, subjects) is read-only here: it is edited in the file. */
export const isReadOnly = (entry: Pick<ConfigKey, 'editable'>) => !entry.editable

const SCOPE: Record<ConfigKey['scope'], string> = {
  project: 'project: the team contract; the local layer does not count',
  machine: 'machine: the local value wins over the project',
  either: 'either: the project wins; local fills what it leaves out',
}

/** What a key's row says on hover: the summary, the default, who reads it and which layers count. */
export function describe(entry: ConfigKey): string {
  return [
    entry.copy.en.summary,
    `Default: ${shown(entry.default) || 'none'}`,
    `Read by: ${entry.reader}`,
    `Scope: ${SCOPE[entry.scope]}`,
    entry.key,
  ].join('\n')
}
