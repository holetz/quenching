// /quenching-cache handoff for OpenCode: the same handoff as the Claude Code plugin, through the
// same shared core. Everything the host owns (the conversation, Haiku, the new session, `cq`) comes
// in as a dependency, so the whole flow runs under plain Node in the checks.
import type { Words } from './core/i18n.ts'
import { assemble, briefPrompt, briefSystem, draftPath, isValidBrief, parseFacts } from './core/handoff.ts'
import type { Facts, Numbers } from './core/handoff.ts'
import type { SessionMessage } from './core/message.ts'

export type HandoffResult = { ok: boolean; text: string; line: string }

export type HandoffDeps = {
  sessionID: string
  directory: string
  focus: string
  words: Words
  now: number
  /** The conversation as OpenCode keeps it (`ctx.session.context`). */
  context(): Promise<unknown[]>
  /** One Haiku call, with no session, history or tools (`ctx.experimental.generate.text`). */
  generate(prompt: string): Promise<string>
  /** `cq <args>` by fixed argv; the exit code and stdout. `null` when there is no `cq` at all. */
  cq(args: string[]): Promise<{ code: number; stdout: string } | null>
  writeFile(path: string, text: string): Promise<void>
  /** A new session in this directory that is sent `line` (`ctx.session.create` + `ctx.session.prompt`). */
  openSession(line: string): Promise<void>
  template: string
  preamble: string
  numbers: Numbers
}

const EDIT_TOOLS = new Set(['edit', 'write', 'patch', 'multiedit'])
const bare = (name: unknown) => String(name ?? '').split('__').pop()!.toLowerCase()

/** OpenCode's rows in the shape the shared core reads. */
export function toMessages(context: unknown[]): SessionMessage[] {
  const out: SessionMessage[] = []
  for (const raw of context) {
    const m = raw as { type?: string; text?: string; content?: unknown[] }
    if (m?.type === 'user') {
      if (typeof m.text === 'string' && m.text.trim()) out.push({ role: 'user', text: m.text, toolUses: [] })
    } else if (m?.type === 'assistant' && Array.isArray(m.content)) {
      const blocks = m.content as { type?: string; text?: string; name?: string; state?: { input?: unknown; status?: string } }[]
      out.push({
        role: 'assistant',
        text: blocks.filter(b => b?.type === 'text' && typeof b.text === 'string').map(b => b.text).join('\n'),
        toolUses: blocks.filter(b => b?.type === 'tool').map(b => ({ tool: bare(b.name), input: b.state?.input ?? {}, isError: b.state?.status === 'error' })),
      })
    }
  }
  return out
}

/** The rung under `cq specs handoff facts`: files the chat edited and the user's last words. */
export function ownFacts(messages: readonly SessionMessage[]): Facts {
  const files: string[] = []
  for (const m of messages) {
    for (const t of m.toolUses) {
      if (!EDIT_TOOLS.has(t.tool)) continue
      const input = (t.input ?? {}) as Record<string, unknown>
      const path = input.path ?? input.filePath ?? input.file_path
      if (typeof path === 'string' && path && !files.includes(path)) files.push(path)
    }
  }
  return { branch: null, spec: null, filesModified: files, commits: [] }
}


export async function runHandoff(d: HandoffDeps): Promise<HandoffResult> {
  const fail = (why: string): HandoffResult => ({ ok: false, text: d.words.handoffFailed(why), line: '' })
  const probe = await d.cq(['--version']).catch(() => null)
  if (!probe) return { ok: false, text: d.words.handoffNeedsCq, line: '' }

  const messages = toMessages(await d.context().catch(() => []))
  if (messages.length === 0) return fail('no conversation to read')
  // The facts are `cq`'s, from the OpenCode database; the plugin's own extraction is the rung under it.
  const asked = await d.cq(['specs', 'handoff', 'facts', '--session', d.sessionID, '--json']).catch(() => null)
  const said = asked && asked.code === 0 ? parseFacts(asked.stdout) : null
  // the transcript `cq` names is a database row, not a file anyone can grep
  const facts: Facts = said ? { ...said, transcript: undefined } : ownFacts(messages)

  let brief: string | undefined
  let problem: string | undefined
  try {
    const text = await d.generate(`${briefSystem(d.preamble, d.template)}\n\n${briefPrompt(messages, facts, d.numbers)}`)
    if (isValidBrief(text)) brief = text
    else problem = 'the reply lacked the required sections'
  } catch (err) {
    problem = (err instanceof Error ? err.message : String(err)).slice(0, 200)
  }

  const draft = draftPath(d.now, d.sessionID)
  await d.writeFile(`${d.directory.replace(/\/+$/, '')}/${draft}`, assemble(facts, d.numbers, messages, brief, problem))
  const written = await d.cq(['specs', 'handoff', 'write', '--from', draft, '--focus', d.focus, '--json'])
  if (!written || written.code !== 0) return fail(`cq specs handoff write refused: ${written?.stdout.slice(0, 200) ?? 'no output'}`)
  let parsed: { locator?: string; prompt?: string }
  try {
    parsed = JSON.parse(written.stdout) as { locator?: string; prompt?: string }
  } catch {
    return fail('cq printed no JSON')
  }
  const line = parsed.prompt ?? ''
  if (!line) return fail('cq printed no handoff line')
  await d.openSession(line).catch(() => undefined)
  const text = `${d.words.handoffSaved(parsed.locator ?? draft)}${problem ? d.words.handoffFactsOnly(problem) : ''}`
  return { ok: true, text, line }
}

