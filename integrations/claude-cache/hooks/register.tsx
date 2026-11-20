// quenching-cache: the prompt-cache bar above the prompt, and its one command.
// All decisions live in ./logic.ts and ./handoff.ts; this file only wires events, state, `cq` and
// drawing. Derived from cache-maxxing by 5m0k3 (MIT); what changed is in ../NOTICE.md.
import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Rec } from '../types'
import { assemble, briefPrompt, briefSystem, draftPath, isValidBrief, parseFacts, savedText } from './handoff'
import type { Numbers } from './handoff'
import { WORDS, langOf } from './i18n'
import type { Words } from './i18n'
import { DEFAULTS, costs, decide, fromSessionStart, haikuUsd, sendWarning, setFreshStart, settingsFromConfig, statsText, ttlFor, ttlFromUsage } from './logic'
import type { Settings } from './logic'

const KEEP_MS = 7 * 24 * 60 * 60 * 1000 // saved chats older than this are pruned; an older chat refills on resume
const DAY_MS = 24 * 60 * 60 * 1000
const SEED_MS = 30_000 // a handoff line older than this is stale: a later /clear of your own gets an empty box
const SAME_REPLY_MS = 10 * 60_000 // an estimate this close after an exact record describes the same reply
const FRESH_SAMPLES = 20 // fresh chats' first cache writes kept for the handoff saving
const DEPLOYED_CQ = '.agents/quenching/bin/cq'
const inCwd = (cwd: string, rel: string) => `${cwd.replace(/\/+$/, '')}/${rel}`
const errText = (err: unknown) => (err instanceof Error ? err.message : String(err)).slice(0, 200)

// `shape` declines a record an older version stored in another form (no NaN:NaN).
const last = atom({ plugin: 'quenching-cache', key: 'last' } as const, null, { shape: 'rec-3' })
const tick = atom({ plugin: 'quenching-cache', key: 'tick' } as const, 0)
// Closed with the bar's ✕ for this chat; /quenching-cache brings it back.
const hidden = atom({ plugin: 'quenching-cache', key: 'hidden' } as const, false)

// Module variables survive /clear ($.state does not): the handoff line waiting for the fresh chat,
// and what this checkout declares (its language, its `cq`, its `shared.cache` settings).
let pendingSeed: { line: string; at: number } | undefined
let isNewChat = false // the next main reply is a fresh chat's first: its cache write is a fresh start's size
let settings: Settings = DEFAULTS
let words: Words = WORDS.en
let cq: string | null | undefined // undefined: not looked for yet; null: absent

/** The deployed `cq` of this checkout, else one on PATH, else null. Found once per session. */
async function findCq($: EngineInterface): Promise<string | null> {
  if (cq !== undefined) return cq
  const cwd = await $.session.cwd()
  const deployed = inCwd(cwd, DEPLOYED_CQ)
  if (await $.fs.stat(deployed).catch(() => undefined)) return (cq = deployed)
  const probe = await $.process.run(['cq', '--version'], { cwd, timeoutMs: 10_000 }).catch(() => ({ exitCode: -1 }))
  return (cq = probe.exitCode === 0 ? 'cq' : null)
}

/** `cq <argv>` in this checkout, by fixed argv and no shell; null when there is no `cq`. */
async function runCq($: EngineInterface, argv: string[], timeoutMs = 60_000) {
  const bin = await findCq($)
  if (!bin) return null
  return $.process.run([bin, ...argv], { cwd: await $.session.cwd(), timeoutMs })
    .catch((err: unknown) => ({ exitCode: -1, stdout: '', stderr: errText(err) }))
}

// The language the root harness declares, and the effective `shared.cache` block. Both are read in
// the background: the bar draws from the defaults until they arrive.
async function loadCheckout($: EngineInterface) {
  const cwd = await $.session.cwd()
  const harness = await $.fs.read(inCwd(cwd, 'AGENTS.md')).catch(() => $.fs.read(inCwd(cwd, 'CLAUDE.md'))).catch(() => undefined)
  words = WORDS[langOf(harness === undefined ? undefined : String(harness))]
  const shown = await runCq($, ['config', 'show', '--effective', '--json'], 20_000)
  if (shown && shown.exitCode === 0) settings = settingsFromConfig(shown.stdout)
  await update($, tick, n => n + 1) // redraw with the checkout's words and settings
}

// Clipboard first; if that fails too, a toast shows the line to copy by hand.
async function copyOrSay($: EngineInterface, line: string) {
  const c = await $.ui.copy({ text: line }).catch(() => ({ isCopied: false }))
  $.ui.toast(c.isCopied ? words.handoffCopied(line) : words.handoffSendLine(line))
}

// /clear is refused while the session is still busy right after the command, so retry a few times
// before falling back. Every refusal reason goes to the debug log.
const CLEAR_RETRY_MS = [0, 500, 1_500, 3_000]
async function clearThenSeed($: EngineInterface, line: string) {
  for (const wait of CLEAR_RETRY_MS) {
    if (wait) await $.clock.sleep(wait)
    try {
      await $.command.run({ command: 'clear' })
      return // the clear SessionStart puts the line in the fresh chat's box
    } catch (err) {
      $.ui.log(`quenching-cache: /clear refused after ${wait} ms: ${String(err)}`, { to: 'debug' })
    }
  }
  pendingSeed = undefined
  await copyOrSay($, line)
}

function isRec(v: unknown): v is Rec {
  const r = v as Rec | null
  return !!r && typeof r.at === 'number' && typeof r.prefix === 'number' && typeof r.ttlMin === 'number' && typeof r.model === 'string'
}

async function save($: EngineInterface, rec: Rec | null, sessionId?: string) {
  await update($, last, () => rec)
  // the store is only a backup: the bar runs from memory even when it can't be written
  const key = `cmx:${sessionId ?? (await $.session.id())}`
  await (rec ? $.store.set(key, rec) : $.store.delete(key)).catch(() => {})
}

// Keeps whichever record is newer: memory, store, or one filled in at session start.
async function adopt($: EngineInterface, candidate: Rec | null, sessionId?: string) {
  const kept = await read($, last)
  const stored = await $.store.get(`cmx:${sessionId ?? (await $.session.id())}`).catch(() => undefined)
  const now = await $.clock.now()
  const pool = [kept, isRec(stored) && now - stored.at <= KEEP_MS ? stored : null, candidate].filter(isRec)
  const [newest, ...rest] = pool.sort((a, b) => b.at - a.at)
  // an estimate dates from the reply's end, an exact record from its request's start: for the same
  // reply the exact one wins
  const exact = rest.find(r => !r.isEstimate)
  const pick = newest?.isEstimate && exact && newest.at - exact.at < SAME_REPLY_MS ? exact : newest ?? null
  if (pick !== kept) await save($, pick, sessionId)
  return pick
}

// At most once a day, in the background: drops bar records older than a week.
async function prune($: EngineInterface) {
  const now = await $.clock.now()
  const at = await $.store.get('prunedAt')
  if (typeof at === 'number' && now - at < DAY_MS) return
  await $.store.set('prunedAt', now)
  for (const k of await $.store.keys()) {
    if (!k.startsWith('cmx:')) continue
    const r = await $.store.get(k)
    if (!isRec(r) || now - r.at > KEEP_MS) await $.store.delete(k)
  }
}

async function toggle($: EngineInterface) {
  const isHidden = !(await read($, hidden))
  await update($, hidden, () => isHidden)
  return { text: isHidden ? words.hidden : words.shown }
}

// /quenching-cache stats: what `cq components session cache --usd` measured, this chat and this project.
async function stats($: EngineInterface) {
  const base = ['components', 'session', 'cache', '--json', '--usd', '--harness', 'claude']
  const usable = (r: { exitCode: number; stdout: string } | null) => (r && r.exitCode !== 2 && r.exitCode !== -1 ? r.stdout : null)
  const project = await runCq($, base)
  if (!project) return { text: words.statsNeedsCq }
  const chat = await runCq($, [...base, '--session', await $.session.id()])
  return { text: statsText(usable(chat), usable(project), words) ?? words.statsNone }
}

// /quenching-cache handoff [focus]: Haiku writes the handoff from the chat read locally, on
// quenching's template, and `cq specs handoff write` stores it beside its spec. Never $.model.fork:
// it would resend this chat's prefix, the very rebuild a handoff exists to avoid.
async function handoff($: EngineInterface, focus: string) {
  try {
    if (!(await findCq($))) return { text: words.handoffNeedsCq }
    $.ui.toast(words.handoffWriting)
    const sessionId = await $.session.id()
    const now = await $.clock.now()
    const rec = await read($, last)
    const factsRun = await runCq($, ['specs', 'handoff', 'facts', '--session', sessionId, '--json'])
    const facts = parseFacts(factsRun?.exitCode === 0 ? factsRun.stdout : null)
    const messages = await $.session.messages()
    const nums: Numbers = rec ? { tokens: rec.prefix, window: rec.window, model: rec.model, bar: decide(rec, now, settings, words).text } : {}
    const preamble = String(await $.fs.read(`${$.plugin.root}/hooks/handoff-brief.md`))
    const template = String(await $.fs.read(`${$.plugin.root}/hooks/handoff-template.md`))
    const r = await $.model.complete({
      model: 'haiku',
      system: briefSystem(preamble, template),
      prompt: briefPrompt(messages, facts, nums),
      effort: 'high',
      maxTokens: 64_000,
      timeoutMs: 180_000,
    })
    const usable = r.isAnswered && r.text.trim() && isValidBrief(r.text) ? r.text : undefined
    const problem = usable ? undefined : !r.isAnswered ? `Haiku ${r.reason}` : `Haiku's reply had ${r.text.trim() ? 'none of the required sections' : 'no text'}`
    const draft = inCwd(await $.session.cwd(), draftPath(now, sessionId))
    await $.fs.write(draft, assemble(facts, nums, messages, usable, problem))
    const argv = ['specs', 'handoff', 'write', '--from', draft, '--focus', focus || 'continue this chat', '--push', '--json']
    const wrote = await runCq($, argv, 120_000)
    let stored: { locator?: string; prompt?: string; code?: string; message?: string } = {}
    try {
      stored = JSON.parse(wrote?.stdout ?? '{}') as typeof stored
    } catch { /* reported below */ }
    if (!wrote || wrote.exitCode !== 0 || !stored.locator || !stored.prompt) {
      return { text: words.handoffFailed(`${stored.code ?? `cq exit ${wrote?.exitCode}`}: ${stored.message ?? wrote?.stderr ?? ''}; draft ${draft}`.trim()) }
    }
    const line = stored.prompt
    const c = rec && costs(rec)
    const haiku = r.isAnswered ? { in: r.usage.input_tokens, out: r.usage.output_tokens, usd: haikuUsd(r.usage.input_tokens, r.usage.output_tokens) } : null
    const main = rec && c ? { model: rec.model, tokens: rec.prefix, cold: c.cold, isCold: ['red', 'orange'].includes(decide(rec, now, settings, words).light) } : null
    let text = `${words.handoffSaved(stored.locator)}${problem ? words.handoffFactsOnly(problem) : ''}${savedText(haiku, main)}`
    if ((await $.session.surfaces()).includes('desktop')) {
      // desktop reuses the tab on /clear and its composer refuses a fill: the old chat stays put
      const copied = await $.ui.copy({ text: line }).catch(() => ({ isCopied: false }))
      text += words.handoffContinue(copied.isCopied, line)
      $.ui.toast(text)
      return { text }
    }
    pendingSeed = { line, at: await $.clock.now() } // after Haiku: the call itself may take minutes
    // /clear is refused from inside this hook, so it starts on a timer just after the command
    // returns; the clear SessionStart puts the line in the new chat's box
    $.clock.after(0, () => void clearThenSeed($, line))
    // a notice row kept in this chat's transcript (the model never reads it), so the line is there
    // whenever the user comes back
    const kept = await $.session.append({ message: { type: 'system', content: [{ type: 'text', text }] } }).catch(() => ({ deny: 'error' }))
    return kept.deny ? { text } : {}
  } catch (err) {
    return { text: words.handoffFailed(errText(err)) }
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    // the command and the ticker first: a broken store must never cost the user the bar
    await $.command.register({ name: 'quenching-cache', description: 'Prompt-cache bar: show or hide it, or `handoff [focus]` (Haiku, the expired cache is never resent), or `stats`' })
    // Each second: redraw the bar (it computes from the wall clock, so sleep or a paused timer
    // can't drift it) and pop up once when a big chat's cache expires.
    $.clock.every(1000, () => {
      void (async () => {
        const rec = await read($, last)
        if (!rec) return
        await update($, tick, n => n + 1)
        const v = decide(rec, await $.clock.now(), settings, words)
        if (rec.warned || !v.shouldPopup || (await read($, hidden))) return
        $.ui.toast(v.text) // the pop-up says exactly what the bar says
        await update($, last, r => (r && r.at === rec.at ? { ...r, warned: true } : r))
        const now = await read($, last)
        if (now && now.at === rec.at) await $.store.set(`cmx:${await $.session.id()}`, now).catch(() => {})
      })().catch(() => {})
    })
    void prune($).catch(() => {})
    void loadCheckout($).catch(() => {})
    setFreshStart(await $.store.get('fresh').catch(() => undefined))
    await adopt($, null).catch(() => {}) // bring back this chat's saved record (app restart, reload)
    return next(e)
  })

  // Older chats and chats resumed inside a running app: Claude Code says how long ago the last
  // reply was and how big the chat is, so the bar can show at once.
  on('classic.SessionStart', async ($, e, next) => {
    isNewChat = (e.source === 'startup' || e.source === 'clear') && typeof e.seconds_since_last_response !== 'number'
    if (e.source === 'clear') {
      await save($, null, e.session_id)
      // the fresh chat a handoff opened: put the line in its box; sending stays the user's
      const seed = pendingSeed
      pendingSeed = undefined
      if (seed && (await $.clock.now()) - seed.at < SEED_MS) {
        const line = seed.line
        void $.prompt.fill({ text: line })
          .then(f => (f.isFilled ? undefined : copyOrSay($, line)))
          .catch(() => copyOrSay($, line))
      }
    } else if (typeof e.seconds_since_last_response === 'number' && e.context_tokens) {
      const now = await $.clock.now()
      const prev = await read($, last)
      const candidate = fromSessionStart({
        secondsSince: e.seconds_since_last_response,
        contextTokens: e.context_tokens,
        model: e.model ?? (await $.session.model()),
        window: (await $.session.usage()).context.window || undefined,
      }, now, prev, settings)
      await adopt($, candidate, e.session_id)
    } else {
      await adopt($, null, e.session_id)
    }
    return next(e)
  }).catch(($, e, next) => next(e)) // fail open: never get in Claude Code's way

  on('turn.step', async function* ($, e, next) {
    const startedAt = await $.clock.now() // the cache is refreshed when the request starts
    const r = yield* next(e)
    if (!e.agentId && r.usage) {
      const u = r.usage
      const prev = await read($, last)
      await save($, {
        at: startedAt,
        prefix: u.input_tokens + u.cache_read_input_tokens + u.cache_creation_input_tokens + u.output_tokens,
        out: u.output_tokens,
        model: u.model,
        read: u.cache_read_input_tokens,
        write: u.cache_creation_input_tokens,
        ttlMin: ttlFromUsage(settings.ttlMinutes, u, prev?.ttlMin),
        warned: false,
        window: (await $.session.usage()).context.window || prev?.window,
      })
      if (isNewChat) {
        isNewChat = false
        const had = await $.store.get('fresh').catch(() => undefined)
        const fresh = [...(Array.isArray(had) ? had : []), u.cache_creation_input_tokens].slice(-FRESH_SAMPLES)
        setFreshStart(fresh)
        await $.store.set('fresh', fresh).catch(() => {})
      }
    }
    return r
  })

  // A real model switch drops the cache at once: re-price on the new model now. `resume` only
  // restores the chat's own model, so its cache is untouched.
  on('classic.PostModelSwitch', async ($, e, next) => {
    const prev = await read($, last)
    if (prev && e.source !== 'resume' && e.from_model !== e.to_model) {
      await save($, {
        ...prev,
        model: e.to_model,
        prefix: e.context_tokens || prev.prefix,
        ttlMin: ttlFromUsage(settings.ttlMinutes, {}, prev.ttlMin),
        window: (await $.session.usage()).context.window || prev.window,
        resetBy: 'model',
        warned: false,
      })
    }
    return next(e)
  }).catch(($, e, next) => next(e))

  // /compact replaces the history with a summary: the old cache is useless and the next request
  // writes a much smaller one.
  on('classic.PostCompact', async ($, e, next) => {
    const prev = await read($, last)
    if (prev) {
      const measured = (await $.session.usage()).context.tokens
      // `||`: a 0 from the engine would price the rebuild as free
      const prefix = measured || Math.round(e.compact_summary.length / 4) + 20_000
      await save($, { ...prev, prefix, out: 0, resetBy: 'compact', warned: false })
    }
    return next(e)
  }).catch(($, e, next) => next(e))

  // Warns (never blocks) when you send into a red chat.
  on('prompt.submit', async ($, e, next) => {
    if (e.origin.kind === 'composer' && !e.command && !(await read($, hidden))) {
      const rec = await read($, last)
      if (rec && decide(rec, await $.clock.now(), settings, words).light === 'red') $.ui.toast(sendWarning(rec, words))
    }
    return next(e)
  }).catch(($, e, next) => next(e))

  on('session.end', async ($, e, next) => {
    // the chat is leaving this process: drop the in-memory record so the next chat never shows
    // this one's; the store keeps it
    await update($, last, () => null)
    return next(e)
  })

  on('command.run', { command: 'quenching-cache' }, async ($, e) => {
    const [flow = '', ...rest] = e.args.trim().split(/\s+/)
    if (flow === '' || flow === 'toggle') return toggle($)
    if (flow === 'handoff') return handoff($, rest.join(' '))
    if (flow === 'stats') return stats($)
    return { text: words.help }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (await read($, hidden)) return next(e)
    const rec = await read($, last)
    await read($, tick) // subscribe so the bar redraws every second
    const text = rec ? decide(rec, await $.clock.now(), settings, words).text : words.waiting
    const { Box, Button, Text } = $.ui.resolve(e)
    // nowrap + minWidth 0: VS Code's webview otherwise wraps the ✕ onto its own line
    return (
      <Box key="row" flexDirection="row" flexWrap="nowrap" alignItems="flex-start" gap={1}>
        <Box key="text" flexGrow={1} flexShrink={1} minWidth={0}>
          <Text>{text}</Text>
        </Box>
        <Button key="close" label="✕" plain dimColor onPress={() => update($, hidden, () => true)} />
      </Box>
    )
  })
}
