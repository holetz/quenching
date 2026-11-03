import { Rpc } from "@opencode/plugin/rpc"

const counters = {
  type: "object",
  properties: { tools: { type: "number" }, last: { type: "string" } },
  required: ["tools", "last"],
  additionalProperties: false,
} as const

const row = {
  type: "object",
  properties: {
    id: { type: "number" },
    title: { type: "string" },
    stage: { type: "string" },
    phase: { type: "string" },
    date: { type: "string" },
    checked: { type: "number" },
    blocked: { type: "number" },
    total: { type: "number" },
    work: { type: "string" },
    run: { type: "string" },
  },
  required: ["id", "title", "stage", "phase", "date", "checked", "blocked", "total", "work", "run"],
  additionalProperties: false,
} as const

const touch = {
  type: "object",
  properties: { ...row.properties, kind: { type: "string" }, at: { type: "number" } },
  required: [...row.required, "kind", "at"],
  additionalProperties: false,
} as const

const section = {
  type: "object",
  properties: { heading: { type: "string" }, body: { type: "string" } },
  required: ["heading", "body"],
  additionalProperties: false,
} as const

const task = {
  type: "object",
  properties: {
    id: { type: "string" },
    state: { type: "string" },
    text: { type: "string" },
    blocked: { type: "boolean" },
  },
  required: ["id", "state", "text", "blocked"],
  additionalProperties: false,
} as const

const detail = {
  type: "object",
  properties: {
    id: { type: "number" },
    title: { type: "string" },
    stage: { type: "string" },
    phase: { type: "string" },
    date: { type: "string" },
    priority: { type: "string" },
    priorityHint: { type: "string" },
    complexity: { type: "string" },
    subject: { type: "string" },
    assignee: { type: "string" },
    tags: { type: "array", items: { type: "string" } },
    ready: { type: "boolean" },
    missing: { type: "string" },
    checked: { type: "number" },
    blocked: { type: "number" },
    blockedTask: { type: "string" },
    blockedReason: { type: "string" },
    total: { type: "number" },
    run: { type: "string" },
    verifier: { type: "string" },
    pr: { type: "string" },
    prUrl: { type: "string" },
    work: { type: "string" },
    sections: { type: "array", items: section },
    tasks: { type: "array", items: task },
  },
  required: [
    "id", "title", "stage", "phase", "date", "priority", "priorityHint", "complexity",
    "subject", "assignee", "tags", "ready", "missing", "checked", "blocked", "blockedTask",
    "blockedReason", "total", "run", "verifier", "pr", "prUrl", "work", "sections", "tasks",
  ],
  additionalProperties: false,
} as const

const taskInfo = {
  type: "object",
  properties: {
    text: { type: "string" },
    files: { type: "string" },
    verify: { type: "string" },
    subject: { type: "string" },
  },
  required: ["text", "files", "verify", "subject"],
  additionalProperties: false,
} as const

const board = {
  type: "object",
  properties: { url: { type: "string" } },
  required: ["url"],
  additionalProperties: false,
} as const

const quenchingHealth = {
  type: "object",
  properties: {
    installed: { type: "boolean" },
    version: { type: "string" },
    available: { type: "string" },
    outdated: { type: "boolean" },
    missing: { type: "boolean" },
    root: { type: "string" },
    error: { type: "string" },
  },
  required: ["installed", "version", "available", "outdated", "missing", "root", "error"],
  additionalProperties: false,
} as const

const quenchingUpdate = {
  type: "object",
  properties: {
    ok: { type: "boolean" },
    version: { type: "string" },
    available: { type: "string" },
    output: { type: "string" },
  },
  required: ["ok", "version", "available", "output"],
  additionalProperties: false,
} as const

const changed = {
  type: "object",
  properties: { sessionID: { type: "string" } },
  required: ["sessionID"],
  additionalProperties: false,
} as const

export type Counters = { tools: number; last: string }
export type Row = {
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
}
export type Touch = Row & { kind: string; at: number }
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
  sections: { heading: string; body: string }[]
  tasks: { id: string; state: string; text: string; blocked: boolean }[]
}
export type TaskInfo = { text: string; files: string; verify: string; subject: string }
export type Quenching = {
  installed: boolean
  version: string
  available: string
  outdated: boolean
  missing: boolean
  root: string
  error: string
}
export type QuenchingUpdate = { ok: boolean; version: string; available: string; output: string }

const empty = { type: "object", properties: {}, additionalProperties: false } as const

/** Contrato entre o servidor do plugin e a janela do Desktop. */
export const Vitrine = Rpc.define({
  id: "quenching-vitrine",
  methods: {
    stats: { input: empty, output: counters },
    touched: {
      input: {
        type: "object",
        properties: { sessionID: { type: "string" }, directory: { type: "string" } },
        required: ["sessionID", "directory"],
        additionalProperties: false,
      },
      output: { type: "array", items: touch },
    },
    search: {
      input: {
        type: "object",
        properties: {
          directory: { type: "string" },
          query: { type: "string" },
          limit: { type: "number" },
        },
        required: ["directory", "query", "limit"],
        additionalProperties: false,
      },
      output: { type: "array", items: row },
    },
    detail: {
      input: {
        type: "object",
        properties: { directory: { type: "string" }, id: { type: "number" } },
        required: ["directory", "id"],
        additionalProperties: false,
      },
      output: detail,
    },
    task: {
      input: {
        type: "object",
        properties: { directory: { type: "string" }, id: { type: "number" }, task: { type: "string" } },
        required: ["directory", "id", "task"],
        additionalProperties: false,
      },
      output: taskInfo,
    },
    board: {
      input: {
        type: "object",
        properties: { directory: { type: "string" } },
        required: ["directory"],
        additionalProperties: false,
      },
      output: board,
    },
    quenching: {
      input: {
        type: "object",
        properties: { directory: { type: "string" } },
        required: ["directory"],
        additionalProperties: false,
      },
      output: quenchingHealth,
    },
    upgrade: {
      input: {
        type: "object",
        properties: { directory: { type: "string" } },
        required: ["directory"],
        additionalProperties: false,
      },
      output: quenchingUpdate,
    },
  },
  events: { updated: { schema: counters }, changed: { schema: changed } },
})
