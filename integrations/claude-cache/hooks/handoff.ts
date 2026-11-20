// /quenching-cache handoff: the pure parts. `cq specs handoff facts` extracts the facts that must
// not be lost; Haiku writes the judgement sections on quenching's handoff template from an
// abbreviated conversation; a reply without the required sections falls back to the facts.
// Derived from cache-maxxing by 5m0k3 (MIT): last 120 messages, 2,000 chars each, 150,000 in all,
// tool inputs cut at 300, tool output left out.
import type { SessionMessage } from 'claude-code'

import { handoffSaving, money, tokens } from './logic'

const MAX_MESSAGES = 120
const MAX_MSG_CHARS = 2_000
const MAX_TRANSCRIPT_CHARS = 150_000
const MAX_TOOL_INPUT = 300

const META_PREFIXES = ['Stop hook feedback', '<system-reminder>', '<command-name>', '<local-command', '<task-notification>']
const META_ROWS = [/^(?:\[Image[^\]]*\]\s*)+$/]
// The sections `cq specs handoff write` refuses a handoff without.
export const REQUIRED_SECTIONS = ['## Last Request', '## Next Actions']

export type Facts = { branch?: string | null; spec?: number | string | null; filesModified: string[]; commits: string[]; lastUserMessage?: string | null; transcript?: string }
export type Numbers = { tokens?: number; window?: number; model?: string; bar?: string }

/** The facts `cq specs handoff facts --json` printed; empty lists when it printed nothing usable. */
export function parseFacts(json: string | null): Facts {
  try {
    const f = json ? (JSON.parse(json) as Record<string, unknown>) : {}
    const strs = (v: unknown) => (Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : [])
    return {
      branch: typeof f.branch === 'string' ? f.branch : null,
      spec: typeof f.spec === 'number' || typeof f.spec === 'string' ? f.spec : null,
      filesModified: strs(f.filesModified),
      commits: strs(f.commits),
      lastUserMessage: typeof f.lastUserMessage === 'string' ? f.lastUserMessage : null,
      transcript: typeof f.transcript === 'string' ? f.transcript : undefined,
    }
  } catch {
    return { filesModified: [], commits: [] }
  }
}

/** The user's own words, or undefined for a harness signal or a tool-result-only row. */
export function userText(m: SessionMessage): string | undefined {
  if (m.role !== 'user') return undefined
  const raw = m.text.trim()
  return raw && !META_PREFIXES.some(p => raw.startsWith(p)) && !META_ROWS.some(r => r.test(raw)) ? raw : undefined
}

// A fence longer than any backtick run in the text: quoted text can't close it and forge a turn.
export function fenced(text: string): string {
  const fence = '`'.repeat(Math.max(3, ...[...text.matchAll(/`+/g)].map(m => m[0].length + 1)))
  return `${fence}\n${text}\n${fence}`
}

/** The conversation as Haiku reads it; harness rows are labelled so they aren't taken for the user. */
export function renderTranscript(messages: readonly SessionMessage[]): string {
  const lines = messages.slice(-MAX_MESSAGES).map(m => {
    const role = m.role === 'user' && m.text.trim() && !userText(m) ? 'system signal (not the user)' : m.role
    const text = m.text.length > MAX_MSG_CHARS ? `${m.text.slice(0, MAX_MSG_CHARS)} [truncated]` : m.text
    const tools = m.toolUses.map(t => `  [tool ${t.tool}${t.isError ? ' ERROR' : ''}] ${JSON.stringify(t.input).slice(0, MAX_TOOL_INPUT)}`)
    return [`### ${role}`, text && fenced(text), ...tools].filter(Boolean).join('\n')
  })
  const joined = lines.join('\n\n')
  return joined.length > MAX_TRANSCRIPT_CHARS ? joined.slice(-MAX_TRANSCRIPT_CHARS) : joined
}

/** The last real user message: the facts' when `cq` read the transcript, else the session's own. */
export function lastRequest(f: Facts, messages: readonly SessionMessage[]): string | null {
  if (f.lastUserMessage) return f.lastUserMessage
  for (let i = messages.length - 1; i >= 0; i--) {
    const said = userText(messages[i]!)
    if (said) return said
  }
  return null
}

const list = (items: string[]) => (items.length ? items.map(i => `- ${i}`).join('\n') : 'None.')

/** The closing `## Facts` section: exact, from code, never from a model. */
export function factsSection(f: Facts, n: Numbers): string {
  return [
    '## Facts',
    '',
    `- **Branch:** ${f.branch ?? 'unknown'}`,
    `- **Spec:** ${f.spec ?? 'none'}`,
    n.tokens !== undefined ? `- **Chat size:** ${n.tokens} tokens${n.window ? ` of a ${n.window} window` : ''}` : null,
    n.model ? `- **Model:** ${n.model}` : null,
    n.bar ? `- **quenching-cache bar at handoff:** ${n.bar}` : null,
    f.transcript ? `- **Transcript (grep it, never read it whole):** \`${f.transcript}\`` : null,
    '',
    '### Files modified',
    list(f.filesModified),
    '',
    '### Commits',
    list(f.commits),
  ].filter(l => l !== null).join('\n')
}

/** Haiku's system prompt: the plugin's reading rules, then quenching's template. */
export function briefSystem(preamble: string, template: string): string {
  return `${preamble.trim()}\n\n${template.replace(/^<!--[\s\S]*?-->\n/, '').trim()}`
}

export function briefPrompt(messages: readonly SessionMessage[], f: Facts, n: Numbers): string {
  return `# Facts\n${factsSection({ ...f, lastUserMessage: undefined }, n)}\n\n## Last user message (verbatim)\n${lastRequest(f, messages) ?? 'None found.'}\n\n# Conversation\n${renderTranscript(messages)}\n\n---\n\nWrite the handoff now.`
}

/** A reply without the last request and the next actions is a fragment, not a handoff. */
export const isValidBrief = (text: string) => {
  const heads = text.split('\n').map(l => l.trim())
  return REQUIRED_SECTIONS.every(h => heads.some(l => l.startsWith(h)))
}

/** The stored file: Haiku's handoff when usable, else a facts-only one that still passes the verb. */
export function assemble(f: Facts, n: Numbers, messages: readonly SessionMessage[], haiku: string | undefined, problem: string | undefined): string {
  const body = haiku?.trim() ?? [
    '## Handoff Confidence',
    `Low: facts only — ${problem ?? 'no brief'}. Grep the transcript for the rest.`,
    '',
    '## Last Request',
    lastRequest(f, messages) ?? 'None found.',
    'Status: Not answered',
    '',
    '## Next Actions',
    '1. Read the facts below, then grep the transcript for what they do not say.',
  ].join('\n')
  return `${body}\n\n${factsSection(f, n)}\n`
}

const family = (model: string) => /opus|sonnet|haiku|fable/.exec(model)?.[0]?.replace(/^./, c => c.toUpperCase()) ?? 'the main model'

/** What a handoff on an expired cache saved, net of Haiku: the bar's 🔴 tip uses the same sum. */
export function savedText(haiku: { in: number; out: number; usd: number } | null, main: { model: string; tokens: number; cold: number; isCold: boolean } | null): string {
  if (!main?.isCold) return ''
  const s = handoffSaving(main.tokens, main.cold, haiku)
  return ` ≈ ${tokens(s.tokens)} tokens · ${money(s.usd)} (${family(main.model)}).`
}

export const draftPath = (now: number, sessionId: string) => `.quenching/handoff/draft-${now}-${sessionId.slice(0, 8)}.md`
