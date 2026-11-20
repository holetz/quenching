// Pure logic for the quenching-cache bar: prices, TTL learning and the bar's rules, top to bottom.
// No $ here, so it is testable on its own and shared by every surface. Derived from cache-maxxing
// by 5m0k3 (MIT); what changed is in ../NOTICE.md.
import type { Rec } from '../types'
import type { Words } from './i18n'
import { LONG_PROMPT, MULTIPLIERS, PRICES } from './prices'

export type Settings = {
  rebuildLimitUsd: number
  warnMinutes: number
  longChatTokens: number
  costStyle: 'dollars' | 'times'
  ttlMinutes: 'auto' | '5' | '60'
}

// The fallback for a session without `cq`: the same numbers as quenching's `shared.cache` block,
// and a long chat at `shared.contextBudgets.main`.
export const DEFAULTS: Settings = {
  rebuildLimitUsd: 0.5,
  warnMinutes: 15,
  longChatTokens: 200_000,
  costStyle: 'dollars',
  ttlMinutes: 'auto',
}

/** Settings from `cq config show --effective --json`: a bad or absent leaf keeps its default. */
export function settingsFromConfig(json: string): Settings {
  let values: { key?: unknown; value?: unknown }[] = []
  try {
    const parsed = JSON.parse(json) as { values?: unknown }
    if (Array.isArray(parsed.values)) values = parsed.values as typeof values
  } catch {
    return DEFAULTS
  }
  const at = (key: string) => values.find(v => v.key === key)?.value
  const num = (v: unknown, d: number) => (typeof v === 'number' && Number.isFinite(v) && v >= 0 ? v : d)
  const ttl = at('shared.cache.ttlMinutes')
  return {
    rebuildLimitUsd: num(at('shared.cache.rebuildLimitUsd'), DEFAULTS.rebuildLimitUsd),
    warnMinutes: num(at('shared.cache.warnMinutes'), DEFAULTS.warnMinutes),
    longChatTokens: num(at('shared.contextBudgets.main'), DEFAULTS.longChatTokens) || DEFAULTS.longChatTokens,
    costStyle: at('shared.cache.costStyle') === 'times' ? 'times' : 'dollars',
    ttlMinutes: ttl === '5' || ttl === '60' ? ttl : 'auto',
  }
}

// 'claude-opus-5-5-20260401' → opus-5-5. Exact version match: 'claude-opus-5-6' is unknown, not
// Opus 5's price. Accepts platform prefixes, dates, [1m], @versions and -fast.
function modelKey(model: string): string | null {
  const m = /claude-([a-z]+)-(\d+)(?:-(\d{1,2}))?(?=$|-\d{8}|\[|@|-v\d|-fast|:)/.exec(model.toLowerCase())
  if (!m) return null
  return m[3] ? `${m[1]}-${m[2]}-${m[3]}` : `${m[1]}-${m[2]}`
}

export function priceOf(model: string, prefix: number): { input: number; read: number } | null {
  const key = modelKey(model)
  const p = key ? PRICES[key] : undefined
  if (!key || !p) return null
  const long = LONG_PROMPT[key]
  const tier = long && prefix > long.above ? long.multiplier : 1
  const fast = model.toLowerCase().includes('-fast') ? MULTIPLIERS.fast : 1
  return { input: p[0] * tier * fast, read: p[1] * tier * fast }
}

// warm: the cached part is read; the last reply's output (and your new message) is written.
// cold: everything is written. A write costs MULTIPLIERS.write5m or write1h × input.
export function costs(rec: Rec): { warm: number; cold: number } | null {
  const p = priceOf(rec.model, rec.prefix)
  if (!p) return null
  const write = p.input * (rec.ttlMin >= 60 ? MULTIPLIERS.write1h : MULTIPLIERS.write5m)
  const out = Number.isFinite(rec.out) ? Math.min(rec.out, rec.prefix) : 0
  return { warm: ((rec.prefix - out) * p.read + out * write) / 1e6, cold: (rec.prefix * write) / 1e6 }
}

// The cache lifetime before any reply says otherwise: a subscription's main chat writes the 1h cache.
export function ttlFor(setting: Settings['ttlMinutes']): number {
  return setting === 'auto' ? 60 : Number(setting)
}

// `auto`: the lifetime the reply's cache write actually used. A reply that wrote nothing keeps the
// chat's previous lifetime.
export function ttlFromUsage(setting: Settings['ttlMinutes'], u: { ephemeral_1h_input_tokens?: number; ephemeral_5m_input_tokens?: number }, prev?: number): number {
  if (setting !== 'auto') return Number(setting)
  if ((u.ephemeral_1h_input_tokens ?? 0) > 0) return 60
  if ((u.ephemeral_5m_input_tokens ?? 0) > 0) return 5
  return prev ?? 60
}

// Haiku 5.5's cost for a handoff.
export function haikuUsd(inTok: number, outTok: number): number {
  const p = priceOf('claude-haiku-5-5', inTok)!
  return (inTok * p.input + outTok * p.input * MULTIPLIERS.output) / 1e6
}

// What a handoff costs before it runs: the conversation sent to Haiku is capped at 150,000 chars
// (~37.5K tokens) plus facts and instructions; briefs run about 4-5K tokens.
export const HAIKU_ESTIMATE = { in: 40_000, out: 5_000 }

// The fresh chat's own first cache write plus reading the brief, learned from the user's last 20
// fresh chats (median); until 3 are seen, a measured 13K.
export const FRESH_START_TOKENS = 13_000
const BRIEF_TOKENS = 4_000
let freshStart = FRESH_START_TOKENS
export function setFreshStart(firstWrites: unknown) {
  const xs = Array.isArray(firstWrites) ? firstWrites.filter((x): x is number => typeof x === 'number' && x >= 0).sort((a, b) => a - b) : []
  freshStart = xs.length >= 3 ? xs[Math.floor(xs.length / 2)]! + BRIEF_TOKENS : FRESH_START_TOKENS
}

// The rebuild a handoff avoids, minus what Haiku read, wrote and cost, and the fresh chat's start.
export function handoffSaving(prefix: number, cold: number, haiku: { in: number; out: number; usd: number } | null) {
  const startUsd = prefix > 0 ? (cold * freshStart) / prefix : 0
  return {
    tokens: Math.max(0, prefix - (haiku ? haiku.in + haiku.out : 0) - freshStart),
    usd: Math.max(0, cold - (haiku?.usd ?? 0) - startUsd),
  }
}

export type Light = 'green' | 'yellow' | 'orange' | 'red'
export type Verdict = { light: Light; text: string; shouldPopup: boolean }

export function money(usd: number): string {
  if (usd < 0.01) return '<$0.01'
  const cents = Math.round(usd * 100) / 100
  return `$${cents < 10 ? cents.toFixed(2) : cents.toFixed(0)}`
}

// 290K, 1M, 1.5M, 850
export function tokens(n: number): string {
  if (n >= 999_500) return `${Number((n / 1e6).toFixed(1))}M`
  if (n >= 1e3) return `${Math.round(n / 1e3)}K`
  return String(n)
}

// 47:05, or 1:02:05 past an hour
export function clock(ms: number): string {
  const t = Math.max(0, Math.floor(ms / 1000))
  const h = Math.floor(t / 3600)
  const m = Math.floor((t % 3600) / 60)
  const sec = String(t % 60).padStart(2, '0')
  return h > 0 ? `${h}:${String(m).padStart(2, '0')}:${sec}` : `${m}:${sec}`
}

// The rules, top to bottom; first match wins. The light says the state, so the text is only:
// time, next-message cost, context, recommendation.
export function decide(rec: Rec, now: number, s: Settings, w: Words): Verdict {
  const left = rec.at + rec.ttlMin * 60_000 - now
  const c = costs(rec)
  const r = c && c.warm > 0 ? Math.round(c.cold / c.warm) : null
  const ratio = r && r >= 2 ? r : null
  const dollars = s.costStyle === 'dollars' && c !== null
  const more = ratio ? w.more(ratio) : ''
  const ctx = rec.window ? ` · ${tokens(rec.prefix)} / ${tokens(rec.window)}` : ''
  const nextWarm = dollars ? w.next(money(c.warm)) : w.nextNormal
  const nextCold = dollars ? `${w.next(money(c.cold))}${more}` : ratio ? w.nextTimes(ratio) : r ? w.nextNormal : w.nextMuch
  // no price known: fall back to size (≈ $0.50 of an Opus 5.5 rebuild)
  const isBigRebuild = c ? c.cold >= s.rebuildLimitUsd : rec.prefix >= 60_000

  if (left <= 0 || rec.resetBy) {
    const head = `${rec.resetBy ? w.reset[rec.resetBy] : w.expired} · ${nextCold}${ctx}`
    const save = handoffSaving(rec.prefix, c?.cold ?? 0, { ...HAIKU_ESTIMATE, usd: haikuUsd(HAIKU_ESTIMATE.in, HAIKU_ESTIMATE.out) })
    const suggest = save.tokens > 0 && save.usd > 0 ? w.save(tokens(save.tokens), dollars ? money(save.usd) : null) : w.suggestNew
    return isBigRebuild
      ? { light: 'red', text: `🔴 ${head} · ${suggest}`, shouldPopup: !rec.warned && !rec.resetBy }
      : { light: 'orange', text: `🟠 ${head} · ${w.smallChat}`, shouldPopup: false }
  }
  // yellow only on the 1h cache: a 5m window is too short for a useful warning
  if (rec.ttlMin >= 60 && left <= s.warnMinutes * 60_000) {
    const later = dollars ? `${w.later(money(c.cold))}${more}` : ratio ? w.laterTimes(ratio) : r ? w.laterNormal : w.laterMuch
    return { light: 'yellow', text: `🟡 ${w.minLeft(clock(left))} · ${nextWarm}${later}${ctx} · ${w.replySoon}`, shouldPopup: false }
  }
  const head = `🟢 ${w.minLeft(String(Math.ceil(left / 60_000)))} · ${nextWarm}${ctx}`
  if (rec.prefix >= s.longChatTokens) return { light: 'green', text: `${head} · ${w.suggestNew}`, shouldPopup: false }
  return { light: 'green', text: `${head} · ${w.keepGoing}`, shouldPopup: false }
}

export function sendWarning(rec: Rec, w: Words): string {
  return w.sendWarning(rec.resetBy ?? 'expired')
}

// Fills in a record for a chat this plugin never saw reply (older chats), from what Claude Code
// says at session start. Nothing is learned from it (read/write 0).
export function fromSessionStart(
  i: { secondsSince: number; contextTokens: number; model: string; window?: number },
  now: number, prev: Rec | null, s: Settings,
): Rec {
  const ttlMin = ttlFromUsage(s.ttlMinutes, {}, prev?.ttlMin)
  return {
    at: now - i.secondsSince * 1000, prefix: i.contextTokens, out: 0, model: i.model, read: 0, write: 0,
    ttlMin, warned: false, window: i.window ?? prev?.window, isEstimate: true,
  }
}

// /quenching-cache stats: the table from `cq components session cache --json --usd`, main and
// subagent rows of each scope side by side. Tokens never sum across models; dollars do.
type CacheRow = { model?: unknown; role?: unknown; requests?: unknown; hitRate?: unknown; cacheWrite?: unknown; usd?: unknown }
export function statsText(chat: string | null, project: string | null, w: Words): string | null {
  const rows = (json: string | null): CacheRow[] => {
    try {
      const v = json ? (JSON.parse(json) as { rows?: unknown }).rows : null
      return Array.isArray(v) ? (v as CacheRow[]) : []
    } catch {
      return []
    }
  }
  const date = (json: string | null) => {
    try {
      return json ? String((JSON.parse(json) as { pricing?: { sourceDate?: unknown } }).pricing?.sourceDate ?? '') : ''
    } catch {
      return ''
    }
  }
  const scopes: [string, CacheRow[]][] = [[w.statsThisChat, rows(chat)], [w.statsProject, rows(project)]]
  if (scopes.every(([, r]) => r.length === 0)) return null
  const pct = (v: unknown) => (typeof v === 'number' ? `${Math.round(v * 100)}%` : '–')
  const usd = (v: unknown) => (typeof v === 'number' ? money(v) : '–')
  const lines = [w.statsTitle(date(project) || date(chat)), '', w.statsHeader, '|---|---|---|---|---|---|']
  for (const [label, rs] of scopes) {
    for (const r of rs) {
      const role = r.role === 'subagent' ? ' (subagent)' : ''
      lines.push(`| ${label} | ${String(r.model)}${role} | ${String(r.requests)} | ${pct(r.hitRate)} | ${tokens(Number(r.cacheWrite) || 0)} | ${usd(r.usd)} |`)
    }
    const total = rs.reduce((t, r) => t + (typeof r.usd === 'number' ? r.usd : 0), 0)
    if (rs.length > 1) lines.push(`| ${label} | **total** | | | | ${money(total)} |`)
  }
  return lines.join('\n')
}
