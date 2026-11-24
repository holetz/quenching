/**
 * /quenching-cache handoff on OpenCode, with every host dependency faked.
 *
 *   node --experimental-strip-types integrations/opencode-cache/tests/handoff.check.mjs
 */
import { readFileSync } from "node:fs"
import { runHandoff, toMessages, ownFacts } from "../src/handoff.ts"
import { WORDS } from "../src/core/i18n.ts"

let failed = 0
const ok = (condition, message) => {
  if (!condition) {
    console.error(`FALHOU: ${message}`)
    failed += 1
  }
}
const core = (name) => readFileSync(new URL(`../src/core/${name}`, import.meta.url), "utf8")
const GOOD = "## Handoff Confidence\nHigh.\n\n## Last Request\nship it\nStatus: Answered\n\n## Next Actions\n1. Release.\n"
const context = [
  { type: "user", text: "fix the parser" },
  { type: "assistant", content: [{ type: "text", text: "editing" }, { type: "tool", name: "mcp__opencode__edit", state: { input: { path: "src/a.ts" }, status: "completed" } }] },
  { type: "assistant", content: [{ type: "tool", name: "shell", state: { input: { command: "ls" }, status: "error" } }] },
]

function deps(over = {}) {
  const log = { files: {}, cq: [], opened: [], prompts: [] }
  return {
    log,
    d: {
      sessionID: "ses_abcdef123456", directory: "/work/repo", focus: "parser", words: WORDS.en, now: 1_700_000_000_000,
      context: async () => context,
      generate: async (prompt) => { log.prompts.push(prompt); return GOOD },
      cq: async (args) => {
        log.cq.push(args)
        if (args[0] === "--version") return { code: 0, stdout: "cq 1" }
        return { code: 0, stdout: JSON.stringify({ ok: true, locator: "quenching:specs/9/handoff.md", prompt: "Read the handoff at quenching:specs/9/handoff.md" }) }
      },
      writeFile: async (path, text) => { log.files[path] = text },
      openSession: async (line) => { log.opened.push(line) },
      template: core("handoff-template.md"), preamble: core("handoff-brief.md"),
      numbers: { tokens: 200_000, window: 1_000_000, model: "claude-opus-5-5", bar: "🔴 expired" },
      ...over,
    },
  }
}

// the mapping the shared core reads
const messages = toMessages(context)
ok(messages.length === 3 && messages[1].toolUses[0].tool === "edit" && messages[2].toolUses[0].isError, "rows map to the shared message shape")
ok(JSON.stringify(ownFacts(messages).filesModified) === '["src/a.ts"]', "the plugin's own facts name the edited files")

// the happy path: Haiku's brief + code's facts, stored by cq, and a fresh session sent the line
{
  const { d, log } = deps()
  const r = await runHandoff(d)
  ok(r.ok && r.line.startsWith("Read the handoff"), "ok, with the line that reads the handoff")
  const [path, text] = Object.entries(log.files)[0]
  ok(path.startsWith("/work/repo/.quenching/handoff/draft-1700000000000-ses_abcd"), "the draft lands under .quenching/handoff")
  ok(text.includes("## Last Request") && text.includes("## Facts") && text.includes("src/a.ts"), "the draft is Haiku's brief plus the exact facts")
  const write = log.cq.find((a) => a[1] === "handoff")
  ok(write && write.includes("--from") && write.includes("--focus") && write.includes("parser"), "the draft is stored by `cq specs handoff write`")
  ok(log.opened.length === 1 && log.opened[0] === r.line, "a new session is sent the handoff line")
  ok(/fix the parser/.test(log.prompts[0]) && /^You write a handoff/m.test(log.prompts[0]), "Haiku gets the brief and the conversation")
}

// Haiku fails or answers a fragment: a facts-only handoff that still passes the verb
for (const generate of [async () => { throw new Error("rate limited") }, async () => "just words"]) {
  const { d, log } = deps({ generate })
  const r = await runHandoff(d)
  const text = Object.values(log.files)[0]
  ok(r.ok && /Facts only/.test(r.text), "the fallback is said, not silent")
  ok(/## Last Request/.test(text) && /## Next Actions/.test(text) && /Low: facts only/.test(text), "the fallback still has the required sections")
}

// no cq: nothing is written, nothing is opened
{
  const { d, log } = deps({ cq: async () => null })
  const r = await runHandoff(d)
  ok(!r.ok && r.text === WORDS.en.handoffNeedsCq && Object.keys(log.files).length === 0 && log.opened.length === 0, "no cq: refused before anything is written")
}

// cq refuses the write: the chat is untouched, no new session
{
  const { d, log } = deps({ cq: async (a) => (a[0] === "--version" ? { code: 0, stdout: "" } : { code: 2, stdout: "sp-handoff-incomplete" }) })
  const r = await runHandoff(d)
  ok(!r.ok && log.opened.length === 0 && /refused/.test(r.text), "a refused write opens no session")
}

// an empty conversation is not a handoff
{
  const { d } = deps({ context: async () => [] })
  ok(!(await runHandoff(d)).ok, "no conversation, no handoff")
}

if (failed > 0) process.exit(1)
console.log("handoff: ok")
