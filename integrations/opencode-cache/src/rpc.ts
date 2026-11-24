import { Rpc } from "@opencode/plugin/rpc"

const view = {
  type: "object",
  properties: {
    light: { type: "string" },
    text: { type: "string" },
    tone: { type: "string" },
    hidden: { type: "boolean" },
    implicit: { type: "boolean" },
    shouldPopup: { type: "boolean" },
  },
  required: ["light", "text", "tone", "hidden", "implicit", "shouldPopup"],
  additionalProperties: false,
} as const

const ref = {
  type: "object",
  properties: { sessionID: { type: "string" }, directory: { type: "string" } },
  required: ["sessionID", "directory"],
  additionalProperties: false,
} as const

const message = {
  type: "object",
  properties: { ok: { type: "boolean" }, text: { type: "string" }, line: { type: "string" } },
  required: ["ok", "text", "line"],
  additionalProperties: false,
} as const

const changed = {
  type: "object",
  properties: { sessionID: { type: "string" } },
  required: ["sessionID"],
  additionalProperties: false,
} as const

const expired = {
  type: "object",
  properties: { sessionID: { type: "string" }, text: { type: "string" } },
  required: ["sessionID", "text"],
  additionalProperties: false,
} as const

export type BandView = { light: string; text: string; tone: string; hidden: boolean; implicit: boolean; shouldPopup: boolean }
export type Reply = { ok: boolean; text: string; line: string }

/** The contract between the plugin's server and the Desktop window. */
export const Cache = Rpc.define({
  id: "quenching-cache",
  methods: {
    state: { input: ref, output: view },
    toggle: { input: ref, output: view },
    stats: { input: ref, output: message },
    handoff: {
      input: {
        type: "object",
        properties: { sessionID: { type: "string" }, directory: { type: "string" }, focus: { type: "string" } },
        required: ["sessionID", "directory", "focus"],
        additionalProperties: false,
      },
      output: message,
    },
  },
  events: { changed: { schema: changed }, expired: { schema: expired } },
})
