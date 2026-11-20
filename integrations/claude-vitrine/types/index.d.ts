export type View = 'specs' | 'config'

/** What the session did with a spec: the checkout it is in, a commit, a write, a read or a mention. */
export type Kind = 'worktree' | 'command' | 'read' | 'commit' | 'mention'

export type LedgerEntry = { id: number; kind: Kind; at: number }

/** What the pane learned about `cq` in the session's directory: found with its version, or not. */
export type CqState = { found: boolean; version: string; detail: string }

/** One line of `cq specs list`, normalised for the pane. */
export type SpecRow = {
  id: number
  title: string
  stage: string
  phase: string
  date: string
  checked: number
  blocked: number
  total: number
  work: string
  run: string
  workItemType: string
}

export type Section = { heading: string; body: string }

/** A neighbouring spec in the dependency graph, as `schedule` describes it. */
export type Neighbor = {
  id: number
  title: string
  phase: string
  critical: boolean
  slip: number
  start: string
  target: string
}

/** Who sits above (what the spec waits for), below (who waits for it) and the cycle that stalls everything. */
export type Dependencies = { up: Neighbor[]; down: Neighbor[]; cycle: string[] }

/** A spec an epic is made of, as the epic's document declares it. */
export type Member = {
  label: string
  spec: number
  title: string
  group: number
  status: string
  stage: string
  after: string[]
  waitingOn: string[]
}

/** An epic's composition: how much has shipped, the declared groups, and the members in document order. */
export type Composition = {
  progress: { done: number; total: number; blocked: number; ready: number }
  groups: { group: number; title: string; done: number; blocked: number; total: number }[]
  items: Member[]
}

/** Where a spec is a member: the composite that names it, its title and the label it gave the member. */
export type Composite = { epic: number; title: string; label: string; group: number }

export type Detail = {
  id: number
  title: string
  stage: string
  phase: string
  date: string
  priority: string
  priorityHint: string
  complexity: string
  subject: string
  assignee: string
  tags: string[]
  ready: boolean
  missing: string
  checked: number
  blocked: number
  blockedTask: string
  blockedReason: string
  total: number
  run: string
  verifier: string
  pr: string
  prUrl: string
  work: string
  sections: Section[]
  tasks: { id: string; state: string; text: string; blocked: boolean }[]
  workItemType: string
  deps: Dependencies
  composition?: Composition
  epics: Composite[]
}

export type TaskInfo = { text: string; files: string; verify: string; subject: string }

/** A ledger row shown in the pane: the spec's list row and the evidence that put it there. */
export type TouchRow = SpecRow & { kind: Kind; at: number }

export type ConfigLayer = 'project' | 'local'

/** One key of the registry, as `cq config schema --json` prints it. */
export type ConfigKey = {
  key: string
  type: 'string' | 'integer' | 'number' | 'boolean' | 'enum' | 'paths' | 'strings' | 'prose' | 'object'
  default: unknown
  category: string
  scope: 'project' | 'machine' | 'either'
  reader: string
  editable: boolean
  choices?: string[]
  minimum?: number
  maximum?: number
  copy: Record<'en' | 'pt-BR', { title: string; summary: string }>
}

export type ConfigSchema = {
  categories: { id: string; title: Record<'en' | 'pt-BR', string> }[]
  keys: ConfigKey[]
  values: Record<string, { value: unknown; source: string }>
  layerPaths: Record<ConfigLayer, string>
}

declare module 'claude-code' {
  interface PluginState {
    'quenching-vitrine': {
      view: View
      ledger: Shaped<LedgerEntry[]>
      rows: Shaped<TouchRow[]>
      picked: number | null
      detail: Shaped<Detail | null>
      tab: number
      cq: CqState | null
      busy: string
      config: Shaped<ConfigSchema | null>
      configError: string
      layer: ConfigLayer
      drafts: Shaped<Record<string, string>>
    }
  }
}
