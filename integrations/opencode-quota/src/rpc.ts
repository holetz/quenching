import { Rpc } from "@opencode/plugin/rpc"

const view = {
  type: "object",
  properties: {
    text: { type: "string" },
    tone: { type: "string" },
    hidden: { type: "boolean" },
    title: { type: "string" },
    detail: { type: "string" },
    lang: { type: "string" },
  },
  required: ["text", "tone", "hidden", "title", "detail", "lang"],
  additionalProperties: false,
} as const

const ref = {
  type: "object",
  properties: { directory: { type: "string" } },
  required: ["directory"],
  additionalProperties: false,
} as const

/** What a window draws: the band, its tone, whether the person hid it, the detail, and the language its labels speak. */
export type QuotaView = { text: string; tone: string; hidden: boolean; title: string; detail: string; lang: string }

/** The contract between the plugin's server and its windows; it never carries the token. */
export const Quota = Rpc.define({
  id: "quenching-quota",
  methods: {
    state: { input: ref, output: view },
    refresh: { input: ref, output: view },
    toggle: { input: ref, output: view },
  },
  // After a toggle every open window redraws, so the band hides or shows everywhere at once.
  events: { changed: { schema: { type: "object", properties: {}, additionalProperties: false } } },
})
