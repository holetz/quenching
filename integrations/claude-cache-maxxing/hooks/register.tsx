// cache-maxxing: draws the cache bar described in docs/RULES.md.
// Vendored from https://github.com/5m0k3/cache-maxxing (MIT, (c) 2026 5m0k3) as quenching-cache-maxxing;
// the quenching changes are listed in ../NOTICE.md.
// All decisions live in ./logic.ts; this file only wires events, state and drawing.
import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Rec } from '../types'
import { assembleBrief, briefPrompt, extractFacts, handoffPath, isValidBrief, parseSkill, savingsLine, seedLine, transcriptGuess } from './handoff'
import type { Numbers } from './handoff'
import { PRICES_DATE, WAITING, isDevCopy, addStats, bundledPrices, costs, decide, fromSessionStart, haikuUsd, handoffSaving, newerVersion, priceOf, readSettings, sendWarning, setFreshStart, setPriceOverride, statsFromTranscript, statsText, sumStats, ttlFor, ttlFromUsage, validatePrices } from './logic'
import type { Stats } from './logic'

const KEEP_MS = 7 * 24 * 60 * 60 * 1000 // saved chats older than this are pruned; an older chat refills on resume
const STATS_KEEP_MS = 90 * 24 * 60 * 60 * 1000 // a chat's /cmaxx-stats counts (your call); then folded into st:retired
const TOMBSTONE_MS = 365 * 24 * 60 * 60 * 1000 // a retired chat's marker, so a resume doesn't read its history again
const DAY_MS = 24 * 60 * 60 * 1000
const MAX_READ = 4 * 1024 * 1024 // $.fs.read refuses bigger files
// prices.json still comes from upstream, which maintains the table; the version is quenching's own,
// because this copy moves in quenching's release lockstep and installs from quenching's marketplace
const REPO_RAW = 'https://raw.githubusercontent.com/5m0k3/cache-maxxing/main'
const MANIFEST_RAW = 'https://raw.githubusercontent.com/holetz/quenching/main/integrations/claude-cache-maxxing/.claude-plugin/plugin.json'
const PLUGIN = 'quenching-cache-maxxing'
const MARKETPLACE = 'quenching'
const SEED_MS = 30_000 // a handoff line older than this is stale: a later /clear of your own gets an empty box
// An error for a reply: its message only, never a cut-off "Error: …" dump
const errText = (err: unknown) => (err instanceof Error ? err.message : String(err)).slice(0, 200)
const SAME_REPLY_MS = 10 * 60_000 // an estimate this close after an exact record describes the same reply
const FRESH_SAMPLES = 20 // fresh chats' first cache writes kept for the handoff saving

// `shape` declines a record an older version stored in another form (no NaN:NaN).
const last = atom({ plugin: 'quenching-cache-maxxing', key: 'last' } as const, null, { shape: 'rec-2' })
const tick = atom({ plugin: 'quenching-cache-maxxing', key: 'tick' } as const, 0)
// Closed with the bar's ✕ for this chat; /cmaxx brings it back.
const hidden = atom({ plugin: 'quenching-cache-maxxing', key: 'hidden' } as const, false)

// Module variables survive /clear ($.state does not): the handoff line waiting for the
// fresh chat, and the transcript path from the latest SessionStart.
let pendingSeed: { line: string; at: number } | undefined
let transcriptPath: string | undefined
let isNewChat = false // the next main reply is a fresh chat's first: its cache write is a fresh start's size
let savedFor: number | undefined // the expired cache a handoff saving was counted for: a second handoff of it saves nothing more

// Clipboard first; if that fails too, a toast shows the line to copy by hand.
async function copyOrSay($: EngineInterface, line: string) {
  const c = await $.ui.copy({ text: line }).catch(() => ({ isCopied: false }))
  $.ui.toast(c.isCopied ? `Handoff line copied. Paste it into a new chat: ${line}` : `Start a new chat and send: ${line}`)
}

// /clear is refused while the session is still busy right after the command (seen live at
// 23:31: rejected before queueing, while Claude Code started its own background request),
// so retry a few times before falling back. Every refusal reason goes to the debug log.
const CLEAR_RETRY_MS = [0, 500, 1_500, 3_000]
async function clearThenSeed($: EngineInterface, line: string) {
  for (const wait of CLEAR_RETRY_MS) {
    if (wait) await $.clock.sleep(wait)
    try {
      await $.command.run({ command: 'clear' })
      return // the clear SessionStart puts the line in the fresh chat's box
    } catch (err) {
      $.ui.log(`cache-maxxing: /clear refused after ${wait} ms: ${String(err)}`, { to: 'debug' })
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
  // past the keep time it's as good as pruned (prune runs in the background, maybe later)
  const pool = [kept, isRec(stored) && now - stored.at <= KEEP_MS ? stored : null, candidate].filter(isRec)
  const [newest, ...rest] = pool.sort((a, b) => b.at - a.at)
  // an estimate dates from the reply's end, an exact record from its request's start: for the same
  // reply the exact one wins (issue #4). shortcut: a single request over 10 min still loses to its estimate
  const exact = rest.find(r => !r.isEstimate)
  const pick = newest?.isEstimate && exact && newest.at - exact.at < SAME_REPLY_MS ? exact : newest ?? null
  if (pick !== kept) await save($, pick, sessionId)
  return pick
}

// At most once a day, in the background (one store call per key): drops old bar records, folds
// chats untouched for 90 days into st:retired and leaves a marker, drops markers after a year.
async function prune($: EngineInterface) {
  const now = await $.clock.now()
  const last = await $.store.get('prunedAt')
  if (typeof last === 'number' && now - last < DAY_MS) return
  await $.store.set('prunedAt', now)
  for (const k of await $.store.keys()) {
    if (k.startsWith('cmx:')) {
      const r = await $.store.get(k)
      if (!isRec(r) || now - r.at > KEEP_MS) await $.store.delete(k)
    } else if (k.startsWith('st:') && k !== 'st:retired' && k !== 'st:all') {
      const s = (await $.store.get(k)) as (Stats & { at?: number }) | undefined
      if (typeof s?.at !== 'number') await $.store.delete(k)
      else if (s.retired) { if (now - s.at > TOMBSTONE_MS) await $.store.delete(k) }
      else if (now - s.at > STATS_KEEP_MS) {
        const x = addStats(s, {}, now)
        await $.store.set('st:retired', addStats(await $.store.get('st:retired'), { ...x, chats: x.replies > 0 ? 1 : 0 }, now))
        await $.store.set(k, { at: s.at, since: now, isFilled: true, retired: true })
      }
    }
  }
}

// /cmaxx-stats counters, per chat. A turn's counts wait in memory and are written once, at the
// turn's end (or when /cmaxx-stats asks); All chats is summed from these keys when asked.
// shortcut: a crash mid-turn loses that turn's counts; write per step if that ever matters.
const pending = new Map<string, Partial<Stats>>()
let isInteractive = true // claude -p, the SDK and observer sessions aren't counted

async function count($: EngineInterface, d: Partial<Stats>, sessionId?: string) {
  if (!isInteractive) return
  const key = `st:${sessionId ?? (await $.session.id())}`
  pending.set(key, addStats(pending.get(key), d, 0))
}

async function flush($: EngineInterface) {
  const now = await $.clock.now()
  for (const [key, d] of [...pending]) {
    pending.delete(key)
    try {
      const have = await $.store.get(key)
      // no record yet: counted from its first reply, so there's no history to read on a later resume (issue #6)
      await $.store.set(key, { ...addStats(have, d, now), at: now, ...(have ? {} : { isFilled: true }) })
    } catch {
      pending.set(key, addStats(pending.get(key), d, 0)) // a failed write keeps the counts for the next flush
    }
  }
}

// A chat this plugin hasn't counted from its start: read its history from the transcript once
// (4 MiB at most, $.fs.read's limit), adding only what live counting hasn't already. Too big to
// read: counted from now on, and /cmaxx-stats says "since <date>".
async function fillIn($: EngineInterface, sessionId: string, path: string | undefined, ttlMin: number, isFork: boolean) {
  if (!isInteractive || !path) return
  const key = `st:${sessionId}`
  const have = (await $.store.get(key)) as Stats | undefined
  if (have?.isFilled || have?.partialSince) return
  const now = await $.clock.now()
  // a fork's transcript copies its parent's rows: count it from its first reply instead
  if (isFork) return void (await $.store.set(key, { ...addStats(have, {}, now), isFilled: true, at: now }))
  const file = await $.fs.stat(path).catch(() => undefined)
  if (!file) return // nothing on disk yet (a new chat): counted from its first reply
  const isTooBig = (file.size ?? 0) > MAX_READ
  // the transcript holds everything counted live so far, so it replaces those counts
  const chat = isTooBig
    ? { ...addStats(have, {}, now), partialSince: have?.since ?? now }
    : { ...addStats(null, statsFromTranscript(String(await $.fs.read(path)), ttlMin), now), isFilled: true }
  await $.store.set(key, { ...chat, at: now })
}

// Prices /cmaxx-update saved, checked again on load: a bad or stale table is ignored.
async function loadPrices($: EngineInterface) {
  const v = validatePrices(await $.store.get('prices'), PRICES_DATE)
  // only a table newer than the bundled one: a release's corrected prices always win
  setPriceOverride('error' in v || v.sourceDate <= PRICES_DATE ? null : v.prices)
}

export const register: Register = (on, options) => {
  const settings = readSettings(options as Record<string, unknown>)

  on('session.start', async ($, e, next) => {
    isInteractive = e.isInteractive !== false
    savedFor = undefined
    // commands and ticker first: a broken store must never cost the user the bar or the commands
    await $.command.register({ name: 'cmaxx', description: 'Show or hide the cache-maxxing bar' })
    await $.command.register({ name: 'cmaxx-handoff', description: 'Summarize this chat with Haiku (the expired cache is never resent) and start a fresh chat from it' })
    await $.command.register({ name: 'cmaxx-update', description: 'Update cache-maxxing to the latest version, or refresh its model prices (reads its version and price list from GitHub; sends nothing)' })
    await $.command.register({ name: 'cmaxx-stats', description: 'Show what cache-maxxing counted: handoff savings, cold rebuilds, cache hit rate, for this chat and all chats' })
    // Each second: redraw the bar (it computes from the wall clock, so sleep or a
    // paused timer can't drift it) and pop up once when a big chat's cache expires.
    $.clock.every(1000, () => {
      void (async () => {
        const rec = await read($, last)
        if (!rec) return
        await update($, tick, n => n + 1)
        const v = decide(rec, await $.clock.now(), settings)
        if (rec.warned || !v.shouldPopup || (await read($, hidden))) return
        $.ui.toast(v.text) // the pop-up says exactly what the bar says
        // only mark the record we judged: a reply saved meanwhile stays untouched
        await update($, last, r => (r && r.at === rec.at ? { ...r, warned: true } : r))
        const now = await read($, last)
        if (now && now.at === rec.at) await $.store.set(`cmx:${await $.session.id()}`, now).catch(() => {})
      })().catch(() => {})
    })
    void prune($).catch(() => {}) // in the background: never holds up the first prompt
    await loadPrices($).catch(() => {})
    setFreshStart(await $.store.get('fresh').catch(() => undefined))
    await adopt($, null).catch(() => {}) // bring back this chat's saved record (app restart, reload)
    return next(e)
  })

  // Older chats and chats resumed inside a running app: Claude Code says how long
  // ago the last reply was and how big the chat is, so the bar can show at once.
  on('classic.SessionStart', async ($, e, next) => {
    if (e.transcript_path) transcriptPath = e.transcript_path
    isNewChat = (e.source === 'startup' || e.source === 'clear') && typeof e.seconds_since_last_response !== 'number'
    if (e.session_id) await fillIn($, e.session_id, e.transcript_path, ttlFor(settings.memoryMinutes), e.source === 'fork').catch(() => {})
    if (e.source === 'clear') {
      await save($, null, e.session_id)
      // the fresh chat a /cmaxx-handoff opened: put the line in its box; sending stays the user's
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
      const ttlMin = ttlFromUsage(settings.memoryMinutes, u, prev?.ttlMin)
      await save($, {
        at: startedAt,
        prefix: u.input_tokens + u.cache_read_input_tokens + u.cache_creation_input_tokens + u.output_tokens,
        out: u.output_tokens,
        model: u.model,
        read: u.cache_read_input_tokens,
        write: u.cache_creation_input_tokens,
        ttlMin,
        miss5: 0,
        warned: false,
        window: (await $.session.usage()).context.window || prev?.window,
      })
      if (isNewChat) {
        isNewChat = false
        if (isInteractive) {
          const had = await $.store.get('fresh').catch(() => undefined)
          const fresh = [...(Array.isArray(had) ? had : []), u.cache_creation_input_tokens].slice(-FRESH_SAMPLES)
          setFreshStart(fresh)
          await $.store.set('fresh', fresh).catch(() => {})
        }
      }
      // a reply sent after this chat's cache expired or was reset paid for a rebuild: its cache write.
      // Reading under half the last prefix while warm: something reset it with no event (effort, tools, cleared images; issue #5)
      const isRebuild = !!prev && (!!prev.resetBy || startedAt > prev.at + prev.ttlMin * 60_000 || u.cache_read_input_tokens < prev.prefix / 2)
      const p = priceOf(u.model, u.input_tokens + u.cache_read_input_tokens + u.cache_creation_input_tokens)
      const writeUsd = p ? (u.cache_creation_input_tokens * p.input * (ttlMin >= 60 ? 2 : 1.25)) / 1e6 : 0
      await count($, {
        replies: 1, read: u.cache_read_input_tokens, write: u.cache_creation_input_tokens, input: u.input_tokens,
        ...(isRebuild ? { rebuilds: 1, rebuildTokens: u.cache_creation_input_tokens, rebuildUsd: writeUsd } : {}),
      }).catch(() => {})
    }
    return r
  })

  // A real model switch drops the cache at once: re-price on the new model now.
  // `resume` only restores the chat's own model, so its cache is untouched.
  on('classic.PostModelSwitch', async ($, e, next) => {
    const prev = await read($, last)
    if (prev && e.source !== 'resume' && e.from_model !== e.to_model) {
      await save($, {
        ...prev,
        model: e.to_model,
        prefix: e.context_tokens || prev.prefix,
        ttlMin: ttlFromUsage(settings.memoryMinutes, {}, prev.ttlMin),
        window: (await $.session.usage()).context.window || prev.window,
        resetBy: 'model',
        warned: false,
      })
    }
    return next(e)
  }).catch(($, e, next) => next(e)) // fail open: never get in Claude Code's way

  // /compact replaces the history with a summary: the old cache is useless and
  // the next request writes a much smaller one.
  on('classic.PostCompact', async ($, e, next) => {
    const prev = await read($, last)
    if (prev) {
      const measured = (await $.session.usage()).context.tokens
      // estimate when the engine has no figure yet: summary at ~4 chars/token plus the fixed system part
      // `||`: a 0 from the engine would price the rebuild as free (issue #5)
      const prefix = measured || Math.round(e.compact_summary.length / 4) + 20_000
      await save($, { ...prev, prefix, out: 0, resetBy: 'compact', warned: false })
    }
    return next(e)
  }).catch(($, e, next) => next(e)) // fail open: never get in Claude Code's way

  // Warns (never blocks) when you send into a red chat.
  on('prompt.submit', async ($, e, next) => {
    if (e.origin.kind === 'composer' && !e.command && !(await read($, hidden))) {
      const rec = await read($, last)
      if (rec && decide(rec, await $.clock.now(), settings).light === 'red') $.ui.toast(sendWarning(rec))
    }
    return next(e)
  }).catch(($, e, next) => next(e))

  on('session.end', async ($, e, next) => {
    // the chat is leaving this process (clear, resume into another, exit): drop the
    // in-memory record so the next chat never shows this one's; the store keeps it
    await update($, last, () => null)
    await flush($).catch(() => {})
    return next(e)
  })

  // a turn's /cmaxx-stats counts are written once, when it ends
  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    await flush($).catch(() => {})
    return r
  })

  on('command.run', { command: 'cmaxx' }, async $ => {
    const isHidden = !(await read($, hidden))
    await update($, hidden, () => isHidden)
    return { text: isHidden ? 'cache-maxxing bar hidden. Type /cmaxx to show it.' : 'cache-maxxing bar shown.' }
  })

  // /cmaxx-update: the plugin's only network use, and only when you run it. GETs of this
  // repo's own files; nothing is sent. A newer version is installed by Claude Code's own
  // updater where the plugin may run it (the terminal); otherwise the reply says how.
  on('command.run', { command: 'cmaxx-update' }, async $ => {
    const get = async (file: string, url = `${REPO_RAW}/${file}`) => {
      const r = await $.http.fetch(url).catch((err: unknown) => {
        $.ui.log(`cache-maxxing: /cmaxx-update fetch ${file}: ${String(err)}`, { to: 'debug' })
        throw new Error('GitHub not reachable (offline?)') // the raw error went to the debug log
      })
      if (!r.ok) throw new Error(`${file}: HTTP ${r.status}`)
      return JSON.parse(r.text) as unknown
    }
    const lines: string[] = []
    // each step reports on its own: a failed price download never hides a finished update
    try {
      const mine = String((JSON.parse(String(await $.fs.read(`${$.plugin.root}/.claude-plugin/plugin.json`))) as { version?: unknown }).version)
      const latest = String((await get('.claude-plugin/plugin.json', MANIFEST_RAW) as { version?: unknown }).version)
      if (!newerVersion(latest, mine)) lines.push(`cache-maxxing ${mine} is the latest version.`)
      else if (isDevCopy($.plugin.name)) lines.push(`Version ${latest} is out (this is the dev copy, ${mine}: not updated).`)
      else {
        const run = await $.process.run(['claude', 'plugin', 'update', `${PLUGIN}@${MARKETPLACE}`], { timeoutMs: 120_000 }).catch((err: unknown) => ({ exitCode: -1, stdout: '', stderr: String(err) }))
        $.ui.log(`cache-maxxing: plugin update exit ${run.exitCode}: ${run.stderr.slice(0, 300)}`, { to: 'debug' })
        // exit 0 also when nothing changed: Claude Code's marketplace copy is older than GitHub (F73)
        const isStale = run.exitCode === 0 && /already at the latest version/i.test(`${run.stdout} ${run.stderr}`)
        lines.push(isStale
          ? `Version ${latest} is out, but Claude Code's copy of the marketplace is behind (you have ${mine}). In a terminal run \`claude plugin marketplace update ${MARKETPLACE}\`, then /cmaxx-update again.`
          : run.exitCode === 0
          ? `Updated cache-maxxing ${mine} → ${latest}. Run /reload-plugins (or restart the app) to use it.`
          : `Version ${latest} is out (you have ${mine}). To update: in a terminal run \`claude plugin update ${PLUGIN}@${MARKETPLACE}\`, or in the desktop app open + → Plugins → Manage plugins. Then run /reload-plugins. Tip: \`/plugin\` → Marketplaces → ${MARKETPLACE} → Enable auto-update keeps it current.`)
      }
    } catch (err) {
      lines.push(`Couldn't check for a new version: ${errText(err)}.`)
    }
    try {
      const v = validatePrices(await get('prices.json'), PRICES_DATE)
      const before = validatePrices(await $.store.get('prices').catch(() => undefined), PRICES_DATE)
      if ('error' in v) lines.push(`Prices not changed: the downloaded table was refused (${v.error}).`)
      // an older download never replaces newer prices saved earlier (issue #6)
      else if (!('error' in before) && before.sourceDate > v.sourceDate) lines.push(`Prices: up to date (${before.sourceDate}).`)
      else if (v.sourceDate <= PRICES_DATE) {
        // not newer than the prices built into this version: those win, and an older download is dropped
        await $.store.delete('prices').catch(() => {})
        setPriceOverride(null)
        lines.push(`Prices: up to date (${PRICES_DATE}).`)
      } else {
        const known = 'error' in before || before.sourceDate <= PRICES_DATE ? bundledPrices().prices : before.prices
        const added = Object.keys(v.prices).filter(k => !(k in known))
        const changed = added.length > 0 || JSON.stringify(v.prices) !== JSON.stringify(known)
        await $.store.set('prices', v).catch(() => {})
        setPriceOverride(v.prices)
        lines.push(changed ? `Prices updated to ${v.sourceDate}${added.length ? `: new ${added.map(k => `claude-${k}`).join(', ')}` : ''}.` : `Prices: up to date (${v.sourceDate}).`)
      }
    } catch (err) {
      lines.push(`Prices not checked: ${errText(err)}.`)
    }
    const isNothingChecked = lines.every(l => l.startsWith("Couldn't") || l.startsWith('Prices not checked'))
    // no "cache-maxxing:" of our own: Claude Code already names the plugin on its output
    return { text: isNothingChecked ? `${lines.join(' ')} Nothing changed.` : lines.join(' ') }
  })

  on('command.run', { command: 'cmaxx-stats' }, async $ => {
    await flush($).catch(() => {}) // include the turn in progress
    const get = (k: string) => $.store.get(k).catch(() => undefined)
    const now = await $.clock.now()
    const chat = addStats(await get(`st:${await $.session.id()}`), {}, now)
    const keys = (await $.store.keys().catch(() => [] as string[])).filter(k => k.startsWith('st:') && k !== 'st:retired' && k !== 'st:all')
    const all = sumStats(await Promise.all(keys.map(get)), await get('st:retired'), now)
    return { text: statsText(chat, all, settings) }
  })

  // /cmaxx-handoff: Haiku writes the brief from the chat read locally. Never $.model.fork:
  // it would resend this chat's prefix, the very rebuild a handoff exists to avoid.
  on('command.run', { command: 'cmaxx-handoff' }, async $ => {
    try {
      $.ui.toast('cache-maxxing: writing the handoff…')
      const skill = parseSkill(String(await $.fs.read(`${$.plugin.root}/hooks/handoff-skill.md`)))
      const messages = await $.session.messages()
      const sessionId = await $.session.id()
      const now = await $.clock.now()
      const rec = await read($, last)
      const facts = extractFacts(messages)
      const nums: Numbers = rec ? { tokens: rec.prefix, window: rec.window, model: rec.model, bar: decide(rec, now, settings).text } : {}
      const r = await $.model.complete({
        model: 'haiku',
        system: skill.brief,
        prompt: briefPrompt(messages, facts, nums, skill.closing),
        effort: 'high',
        // the API's ceiling, not a budget. shortcut: no output cap yet; set one from a few real briefs
        maxTokens: 64_000,
        timeoutMs: 180_000, // your call: a slow API gets 3 minutes, then the facts-only file
      })
      const usable = r.isAnswered && r.text.trim() && isValidBrief(r.text) ? r.text : undefined
      // why a brief is facts only, with Haiku's token counts: out at the cap means it ran out of room
      const problem = usable ? undefined : !r.isAnswered ? `Haiku ${r.reason}` : `Haiku's reply had ${r.text.trim() ? 'none of the sections' : 'no text'}, in ${r.usage.input_tokens} / out ${r.usage.output_tokens} of 64000 tokens`
      const transcript = transcriptPath ?? transcriptGuess(await $.session.cwd(), sessionId, await $.env.get('CLAUDE_CONFIG_DIR').catch(() => undefined))
      const path = handoffPath(now, sessionId)
      await $.fs.write(path, assembleBrief({ sessionId, transcript, skill }, facts, nums, usable))
      // briefs quote the chat: the folder ignores itself so `git add -A` never picks them up
      const ignore = '.claude/handoffs/.gitignore'
      if (!(await $.fs.stat(ignore).catch(() => undefined))) await $.fs.write(ignore, '*\n').catch(() => {})
      const line = seedLine(path)
      const c = rec && costs(rec)
      const haiku = r.isAnswered ? { in: r.usage.input_tokens, out: r.usage.output_tokens, usd: haikuUsd(r.usage.input_tokens, r.usage.output_tokens) } : null
      const main = rec && c ? { model: rec.model, tokens: rec.prefix, cold: c.cold, isCold: ['red', 'orange'].includes(decide(rec, now, settings).light) } : null
      let text = savingsLine({ path, problem, haiku, main })
      // counted as the notice says it: a saving only when the cache had expired
      // once per expired cache: running it again, or carrying on in the old chat, saves nothing more (issue #3)
      const saved = main?.isCold && rec!.at !== savedFor ? handoffSaving(main.tokens, main.cold, haiku) : null
      if (saved) savedFor = rec!.at
      await count($, { handoffs: 1, ...(saved ? { savedTokens: saved.tokens, savedUsd: saved.usd } : {}) }, sessionId).catch(() => {})
      await flush($).catch(() => {}) // the old chat is about to be cleared: keep its handoff now
      if ((await $.session.surfaces()).includes('desktop')) {
        // desktop reuses the tab on /clear, so the old chat drops out of view, and its own
        // composer refuses a fill (live 00:12, F52): there the old chat stays put
        const c = await $.ui.copy({ text: line }).catch(() => ({ isCopied: false }))
        text += ` To continue, start a new chat and paste${c.isCopied ? ' (auto-copied)' : ''}: ${line}`
        $.ui.toast(text)
        // the desktop app doesn't draw a system notice row (live 00:31, F53): use the command's output
        return { text }
      } else {
        pendingSeed = { line, at: await $.clock.now() } // after Haiku: the call itself may take minutes
        // /clear is refused from inside this hook (measured), so it starts on a timer just
        // after the command returns; the clear SessionStart above puts the line in the new chat's box
        $.clock.after(0, () => void clearThenSeed($, line))
      }
      // a notice row kept in this chat's transcript (the model never reads it), so the line is
      // there whenever the user comes back; command output went unseen after the clear (00:01)
      const kept = await $.session.append({ message: { type: 'system', content: [{ type: 'text', text }] } }).catch(() => ({ deny: 'error' }))
      return kept.deny ? { text } : {}
    } catch (err) {
      return { text: `cache-maxxing: no handoff written (${String(err)}). This chat is untouched.` }
    }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (await read($, hidden)) return next(e)
    const rec = await read($, last)
    await read($, tick) // subscribe so the bar redraws every second
    const text = rec ? decide(rec, await $.clock.now(), settings).text : WAITING
    const { Box, Button, Text } = $.ui.resolve(e)
    // text wraps on the left; ✕ stays pinned top-right however many lines it takes.
    // nowrap + minWidth 0: VS Code's webview otherwise wraps the ✕ onto its own line (P2)
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
