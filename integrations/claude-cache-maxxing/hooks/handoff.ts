// /cmaxx-handoff: the pure parts. Code extracts the facts that must not be lost (files,
// commits, the last request, the bar's numbers); Haiku writes the judgment sections from
// an abbreviated conversation; a reply with none of the sections falls back to the facts.
// Limits follow auto-handoff (battle-tested): last 120 messages, 2,000 chars each,
// 150,000 in all, tool inputs cut at 300, tool output left out.
import type { SessionMessage } from 'claude-code'

import { handoffSaving, money, tokens } from './logic'

const MAX_MESSAGES = 120
const MAX_MSG_CHARS = 2_000
const MAX_TRANSCRIPT_CHARS = 150_000
const MAX_TOOL_INPUT = 300
const MAX_LAST_MESSAGE = 4_000 // a pasted log must not flood Haiku's prompt or the saved file

// Harness messages that arrive as user rows but are never the user's own words.
const META_PREFIXES = ['Stop hook feedback', '<system-reminder>', '<command-name>', '<local-command', '<task-notification>']
// Whole rows only: "[Image #1] stop, review this" and a message quoting a handoff path are the user's (issue #2).
const META_ROWS = [/^(?:\[Image[^\]]*\]\s*)+$/, /^Read \.claude\/handoffs\/\S+\.md and continue from where we left off\.$/]
// The two sections a new chat can't do without: a reply holding only "Handoff Confidence" is no brief (issue #1).
const REQUIRED_SECTIONS = ['## Last Request from the User', '## Next Steps']
const EDIT_TOOLS = new Set(['Edit', 'Write', 'NotebookEdit'])
const GIT_COMMIT_OUTPUT = /^\[[\w./-]+(?: \(root-commit\))? ([0-9a-f]{7,})\] (.+)$/m
// `git commit -q` prints no "[main abc1234]" line, so its subject comes from -m (quotes may hold & or ;)
const QUIET_COMMIT = /git commit\b((?:[^&;|\n"']|"[^"]*"|'[^']*')*)/

export type Skill = { brief: string; closing: string; nextChat: string }
export type Facts = { filesModified: string[]; commits: string[]; issues: string[]; lastUserMessage?: string }
export type Numbers = { tokens?: number; window?: number; model?: string; bar?: string }

// The three "# " parts of hooks/handoff-skill.md, by name.
export function parseSkill(md: string): Skill {
  md = md.replace(/\r\n/g, '\n') // Git for Windows checks out CRLF (issues #9, #10)
  const part = (name: string) => {
    const m = new RegExp(`^# ${name}[ \\t]*\\n([\\s\\S]*?)(?=^# |(?![\\s\\S]))`, 'm').exec(md)
    if (!m?.[1]?.trim()) throw new Error(`handoff-skill.md has no "# ${name}" part`)
    return m[1].trim()
  }
  return { brief: part('Final brief'), closing: part('Closing line'), nextChat: part('Next-chat instructions') }
}

/** The user's own words, or undefined for a harness signal or a tool-result-only row. */
export function userText(m: SessionMessage): string | undefined {
  if (m.role !== 'user') return undefined
  const raw = m.text.trim()
  return raw && !META_PREFIXES.some(p => raw.startsWith(p)) && !META_ROWS.some(r => r.test(raw)) ? raw : undefined
}

export function extractFacts(messages: readonly SessionMessage[]): Facts {
  const files = new Set<string>()
  const commits: string[] = []
  const issues = new Set<string>()
  let lastUserMessage: string | undefined
  for (const m of messages) {
    const said = userText(m)
    if (said) lastUserMessage = said.length > MAX_LAST_MESSAGE ? `${said.slice(0, MAX_LAST_MESSAGE)} [cut]` : said
    for (const n of `${said ?? (m.role === 'assistant' ? m.text : '')}`.matchAll(/(?<![\w&/])#(\d{2,5})\b/g)) issues.add(`#${n[1]}`)
    for (const t of m.toolUses) {
      const path = t.input.file_path ?? t.input.notebook_path
      if (EDIT_TOOLS.has(t.tool) && typeof path === 'string' && !t.isError) files.add(path)
      if (t.tool !== 'Bash' || typeof t.input.command !== 'string' || t.isError) continue
      // git's own "[main abc1234] subject" line proves a commit landed
      const out = typeof t.text === 'string' ? t.text.match(GIT_COMMIT_OUTPUT) : null
      const quiet = out ? null : t.input.command.match(QUIET_COMMIT)?.[1]
      const msg = quiet && /(?:^|\s)(?:-q|--quiet)\b/.test(quiet) && !/nothing to commit/.test(`${t.text ?? ''}`) ? quiet.match(/-m\s+(["'])(.*?)\1/)?.[2] : undefined
      // from the command alone: `false && git commit -q …` exits 0 with no commit (issue #2)
      const subject = out ? `${out[2]} (${out[1]})` : msg && `${msg} (no git output: unverified)`
      if (subject && !commits.includes(subject)) commits.push(subject)
    }
  }
  return { filesModified: [...files].slice(-20), commits: commits.slice(-10), issues: [...issues].slice(-15), lastUserMessage }
}

// A fence longer than any backtick run in the text: quoted text can't close it and forge a `### user` turn.
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

const list = (items: string[]) => (items.length ? items.map(i => `- ${i}`).join('\n') : 'None.')

export function factsBlock(f: Facts, n: Numbers): string {
  const nums = [
    n.tokens !== undefined && `- **Chat size:** ${n.tokens} tokens${n.window ? ` of a ${n.window} window` : ''}`,
    n.model && `- **Model:** ${n.model}`,
    n.bar && `- **cache-maxxing bar at handoff:** ${n.bar}`,
  ].filter(Boolean)
  const all = `## Handoff Numbers
${nums.length ? nums.join('\n') : 'unknown'}

## Files Modified (from Edit/Write calls)
${list(f.filesModified)}

## Commits This Chat
${list(f.commits)}

## GitHub Issues Mentioned
${f.issues.length ? f.issues.join(', ') : 'None.'}`
  return `${all}\n\n## Last Real User Message (verbatim)\n${f.lastUserMessage ?? 'None found.'}`
}

// Instructions sit in `system`; here the data comes first and one closing line last.
export function briefPrompt(messages: readonly SessionMessage[], f: Facts, n: Numbers, closing: string): string {
  return `# Extracted Facts\n${factsBlock(f, n)}\n\n# Conversation\n${renderTranscript(messages)}\n\n---\n\n${closing}`
}

/** A reply without the last request and the next steps is a fragment, not a brief. */
export const isValidBrief = (text: string) => REQUIRED_SECTIONS.every(h => text.includes(h))

/** Whether the brief's last-request section says it is not (fully) answered. */
export function hasUnansweredLastRequest(text: string): boolean {
  const heading = /##\s*Last Request from the User/i.exec(text)
  if (!heading) return false
  const rest = text.slice(heading.index + heading[0].length)
  const next = /^#{1,6}\s/m.exec(rest)
  const section = next ? rest.slice(0, next.index) : rest
  return /\bStatus[\s*_`]*:[\s*_`"]*(Not (?:yet |fully )?answered|Partially answered|Unanswered)/i.test(section)
}

/** {{#name}}…{{/name}} shows when set, {{^name}}…{{/name}} when not. */
export function renderTemplate(template: string, flags: Record<string, boolean>): string {
  return template
    .replace(/\{\{([#^])(\w+)\}\}([\s\S]*?)\{\{\/\2\}\}/g, (_m, kind: string, name: string, body: string) => ((kind === '#') === Boolean(flags[name]) ? body : ''))
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

export type Ctx = { sessionId: string; transcript: string; skill: Skill }

/** The saved file: instructions for the new chat, Haiku's brief (if usable), then the facts. */
export function assembleBrief(ctx: Ctx, f: Facts, n: Numbers, haiku: string | undefined): string {
  const header = `${renderTemplate(ctx.skill.nextChat, { priority: haiku ? hasUnansweredLastRequest(haiku) : false })}

## Session Handoff Brief

- **Previous chat:** ${ctx.sessionId}
- **Transcript (grep it, never read it whole):** \`${ctx.transcript}\`
- **How this was written:** ${haiku ? 'Haiku wrote the judgment sections from the conversation, abbreviated (long messages cut, tool output left out). They are a model\'s summary of the chat, not the user\'s own words. The facts at the end came from the tool calls, in code.' : 'Haiku did not return a usable brief, so this holds only the facts extracted in code. Grep the transcript for the rest.'}`
  // the user's own last words always: Haiku's section may paraphrase them (issue #1)
  return `${[header, haiku?.trim(), factsBlock(f, n)].filter(Boolean).join('\n\n')}\n`
}

/** Claude Code keeps transcripts under the folder with every non-alphanumeric character as '-', in CLAUDE_CONFIG_DIR or ~/.claude. */
export const transcriptGuess = (cwd: string, id: string, configDir = '~/.claude') => `${configDir.replace(/\/+$/, '')}/projects/${cwd.replace(/[^a-zA-Z0-9]/g, '-')}/${id}.jsonl`

/** .claude/handoffs/2026-11-16-223015-ab754061.md (seconds: two handoffs in one minute don't overwrite) */
export function handoffPath(now: number, sessionId: string): string {
  const d = new Date(now)
  const p = (x: number) => String(x).padStart(2, '0')
  return `.claude/handoffs/${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}-${sessionId.slice(0, 8)}.md`
}

export const seedLine = (path: string) => `Read ${path} and continue from where we left off.`

const family = (model: string) => /opus|sonnet|haiku|fable/.exec(model)?.[0]?.replace(/^./, c => c.toUpperCase()) ?? 'the main model'

/**
 * The line printed in the old chat. Warm cache: only that nothing was resent. Expired cache:
 * also the rough saving, the bar's rebuild minus Haiku's input and output.
 * `problem` says why the brief is facts only.
 */
export function savingsLine(i: {
  path: string
  haiku: { in: number; out: number; usd: number } | null
  main: { model: string; tokens: number; cold: number; isCold: boolean } | null
  problem?: string
}): string {
  const head = `Handoff saved to ${i.path}${i.problem ? ` (facts only: ${i.problem})` : ''}. This command never resent the chat to ${i.main ? family(i.main.model) : 'the main model'}: no cache read, no rebuild.`
  if (!i.main?.isCold) return head
  const saved = handoffSaving(i.main.tokens, i.main.cold, i.haiku) // the bar's 🔴 tip uses the same calculation
  return `${head} You saved approx ${tokens(saved.tokens)} tokens and ${money(saved.usd)}.`
}
