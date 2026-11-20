// Pure logic for the cache-maxxing bar: prices, TTL learning, and the rules in
// docs/RULES.md. No $ here, so it is testable on its own and shared by every surface.
import type { Rec } from '../types'

export type Settings = {
  rebuildLimitUsd: number
  warnMinutes: number
  longChatTokens: number
  costStyle: 'dollars' | 'times'
  memoryMinutes: 'auto' | '5' | '60'
}

export const DEFAULTS: Settings = {
  rebuildLimitUsd: 0.5,
  warnMinutes: 15,
  longChatTokens: 300_000,
  costStyle: 'dollars',
  memoryMinutes: 'auto',
}

// USD per million tokens: [input, cache read], keyed by exact family-version.
// Source: claude-api skill price list (cached 2026-11-03); rows marked * checked on
// 2026-11-17 against platform.claude.com/docs/en/about-claude/pricing (input and cache-hit
// columns match). shortcut: M1 moves this to prices.json with a sourceDate.
const PRICES: Record<string, [input: number, read: number]> = {
  'fable-5-2': [8, 0.2],
  'mythos-5-2': [8, 0.2],
  'fable-5-1': [10, 0.25],
  'mythos-5-1': [10, 0.25],
  'fable-5': [10, 1],
  'mythos-5': [10, 1], // *
  'opus-5-5': [4, 0.2],
  'opus-5': [5, 0.5], // *
  'opus-4-8': [5, 0.5], // *
  'opus-4-7': [5, 0.5], // *
  'opus-4-6': [5, 0.5], // *
  'opus-4-5': [5, 0.5], // *
  'opus-4-1': [15, 1.5], // retired on most platforms; pricing page, 2026-11-17
  'opus-4': [15, 1.5], // retired on most platforms; pricing page, 2026-11-17
  'sonnet-5-5': [2, 0.1],
  'sonnet-5': [2, 0.2], // *
  'sonnet-4-6': [3, 0.3], // *
  'sonnet-4-5': [3, 0.3], // *
  'sonnet-4': [3, 0.3], // retired on most platforms; pricing page, 2026-11-17
  'haiku-5-5': [0.1, 0.01],
  'haiku-4-5': [1, 0.1], // *
}

// Exact version match: 'claude-opus-5-6' is unknown, not Opus 5's price. Accepts
// platform prefixes (anthropic., us.anthropic.), dates, [1m], @versions and -fast.
// The day PRICES was last checked; a downloaded table older than this is refused (/cmaxx-update).
export const PRICES_DATE = '2026-11-17'
export const bundledPrices = () => ({ sourceDate: PRICES_DATE, prices: PRICES })

// Prices /cmaxx-update downloaded (validated), used over the bundled table until a newer release.
let priceOverride: Record<string, [number, number]> | null = null
export function setPriceOverride(p: Record<string, [number, number]> | null) {
  priceOverride = p
}

// 'claude-opus-5-5-20260401' → family opus, version 5.5; old-style ids ('claude-3-7-sonnet') don't parse.
function parseModel(model: string): { key: string; family: string; v: [number, number] } | null {
  const m = /claude-([a-z]+)-(\d+)(?:-(\d{1,2}))?(?=$|-\d{8}|\[|@|-v\d|-fast|:)/.exec(model.toLowerCase())
  if (!m) return null
  return { key: m[3] ? `${m[1]}-${m[2]}-${m[3]}` : `${m[1]}-${m[2]}`, family: m[1]!, v: [Number(m[2]), Number(m[3] ?? 0)] }
}

// True for a model newer than every priced one of its family (or a family not priced at all):
// the moment /cmaxx-update helps. An old unpriced model (Sonnet 3.7) is not "new".
export function isNewModel(model: string): boolean {
  const m = parseModel(model)
  if (!m) return false
  const known = Object.keys({ ...PRICES, ...priceOverride }).map(k => parseModel(`claude-${k}`)).filter(k => k?.family === m.family)
  return known.every(k => m.v[0] > k!.v[0] || (m.v[0] === k!.v[0] && m.v[1] > k!.v[1]))
}

export function priceOf(model: string, prefix: number): { input: number; read: number } | null {
  const id = model.toLowerCase()
  const parsed = parseModel(id)
  if (!parsed) return null
  const key = parsed.key
  const p = priceOverride?.[key] ?? PRICES[key]
  if (!p) return null
  const tier = key === 'haiku-5-5' && prefix > 100_000 ? 5 : 1 // Haiku 5.5 bills prompts over 100K at 5x
  const fast = id.includes('-fast') ? 2 : 1 // fast-mode deployments cost 2x
  return { input: p[0] * tier * fast, read: p[1] * tier * fast }
}

// warm: the cached part is read; the last reply's output (and your new message) is
// written. cold: everything is written. Writes cost 1.25x (5m) or 2x (1h) of input.
export function costs(rec: Rec): { warm: number; cold: number } | null {
  const p = priceOf(rec.model, rec.prefix)
  if (!p) return null
  const write = p.input * (rec.ttlMin >= 60 ? 2 : 1.25)
  // a record from an older version may lack `out`: treat it as 0, never NaN
  const out = Number.isFinite(rec.out) ? Math.min(rec.out, rec.prefix) : 0
  return { warm: ((rec.prefix - out) * p.read + out * write) / 1e6, cold: (rec.prefix * write) / 1e6 }
}

// The cache lifetime before any reply says otherwise. A subscription's main chat writes the 1h
// cache (F37, F74), so `auto` starts at 1h; ttlFromUsage corrects it from each reply.
export function ttlFor(setting: Settings['memoryMinutes']): number {
  return setting === 'auto' ? 60 : Number(setting)
}

// `auto`: the lifetime the reply's cache write actually used (issue #4: API keys, cloud providers and
// usage credits write 5m). A reply that wrote nothing keeps the chat's previous lifetime.
export function ttlFromUsage(setting: Settings['memoryMinutes'], u: { ephemeral_1h_input_tokens?: number; ephemeral_5m_input_tokens?: number }, prev?: number): number {
  if (setting !== 'auto') return Number(setting)
  if ((u.ephemeral_1h_input_tokens ?? 0) > 0) return 60
  if ((u.ephemeral_5m_input_tokens ?? 0) > 0) return 5
  return prev ?? 60
}

// Haiku 5.5's cost for a handoff; output is 5x its input rate in both bands (FACTS F48b).
export function haikuUsd(inTok: number, outTok: number): number {
  const p = priceOf('claude-haiku-5-5', inTok)!
  return (inTok * p.input + outTok * p.input * 5) / 1e6
}

// What a handoff costs before it runs. Estimate: the chat sent to Haiku is capped at 150,000
// chars (~37.5K tokens) plus facts and instructions; briefs ran 13.8-15.6K chars (F46, F47).
// Four real handoffs used 12K-46K in+out, so this is the top: the bar never promises more than the notice reports.
export const HAIKU_ESTIMATE = { in: 40_000, out: 5_000 }

// The one saving calculation, for the bar (Haiku estimated) and the handoff's notice (Haiku measured):
// the rebuild the handoff avoids, minus what Haiku read, wrote and cost.
// The fresh chat's own first cache write plus reading the brief (~4K tokens: briefs ran 13.8-15.6K chars),
// priced at the main model's write rate. Learned from the user's own last 20 fresh chats (median): MCP tools
// and a big CLAUDE.md can make it ~42K (issue #3). Until 3 are seen: 9.3K, your median over 890 chats (F47b).
export const FRESH_START_TOKENS = 13_000
const BRIEF_TOKENS = 4_000
let freshStart = FRESH_START_TOKENS
export function setFreshStart(firstWrites: unknown) {
  const xs = Array.isArray(firstWrites) ? firstWrites.filter((x): x is number => typeof x === 'number' && x >= 0).sort((a, b) => a - b) : []
  freshStart = xs.length >= 3 ? xs[Math.floor(xs.length / 2)]! + BRIEF_TOKENS : FRESH_START_TOKENS
}

export function handoffSaving(prefix: number, cold: number, haiku: { in: number; out: number; usd: number } | null) {
  const startUsd = prefix > 0 ? (cold * freshStart) / prefix : 0 // cold is the whole prefix at the write rate
  return {
    tokens: Math.max(0, prefix - (haiku ? haiku.in + haiku.out : 0) - freshStart),
    usd: Math.max(0, cold - (haiku?.usd ?? 0) - startUsd),
  }
}

export type Light = 'green' | 'yellow' | 'orange' | 'red'
export type Verdict = { light: Light; text: string; shouldPopup: boolean }

// Cents. The ratio comes from exact amounts, so it can differ slightly from the
// rounded ones shown ($0.05 × 40 ≠ $1.82 is expected; you chose cents anyway).
export function money(usd: number): string {
  if (usd < 0.01) return '<$0.01'
  const cents = Math.round(usd * 100) / 100 // round first: $9.996 shows "$10", like every amount from $10 up
  return `$${cents < 10 ? cents.toFixed(2) : cents.toFixed(0)}`
}

// What the bar suggests instead of commanding (built in 0.2.0)
export const HANDOFF = '/cmaxx-handoff'
const SUGGEST_NEW = `🔄 Try ${HANDOFF} or a new chat`
const RESET_LABEL = { model: 'cache reset (model changed)', compact: 'cache reset (chat compacted)' } as const

// 290K, 1M, 1.5M, 850: short token counts for the context field
export function tokens(n: number): string {
  if (n >= 999_500) return `${Number((n / 1e6).toFixed(1))}M` // 999,500 would round to "1000K"
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

// The rules of docs/RULES.md, top to bottom; first match wins. The light says
// the state, so the text is only: time, next-message cost, context, recommendation.
export function decide(rec: Rec, now: number, s: Settings): Verdict {
  const v = decideBase(rec, now, s)
  // no price for this model (likely a new one): the moment /cmaxx-update helps
  return costs(rec) || !isNewModel(rec.model) ? v : { ...v, text: `${v.text} · new model? try /cmaxx-update` }
}

function decideBase(rec: Rec, now: number, s: Settings): Verdict {
  const left = rec.at + rec.ttlMin * 60_000 - now
  const c = costs(rec)
  const r = c && c.warm > 0 ? Math.round(c.cold / c.warm) : null
  const ratio = r && r >= 2 ? r : null // "(1× more)" says nothing: leave it out
  const dollars = s.costStyle === 'dollars' && c !== null
  const more = ratio ? ` (${ratio}× more)` : ''
  const ctx = rec.window ? ` · ${tokens(rec.prefix)} / ${tokens(rec.window)}` : ''
  const nextWarm = dollars ? `next message ≈ ${money(c.warm)}` : 'next message: normal cost'
  const nextCold = dollars ? `next message ≈ ${money(c.cold)}${more}` : `next message: ${ratio ? `${ratio}× more` : r ? 'normal cost' : 'much more'}`
  // no price known: fall back to size (≈ $0.50 of Opus 5.5 rebuild)
  const isBigRebuild = c ? c.cold >= s.rebuildLimitUsd : rec.prefix >= 60_000

  if (left <= 0 || rec.resetBy) {
    const head = `${rec.resetBy ? RESET_LABEL[rec.resetBy] : 'cache expired'} · ${nextCold}${ctx}`
    const save = handoffSaving(rec.prefix, c?.cold ?? 0, { ...HAIKU_ESTIMATE, usd: haikuUsd(HAIKU_ESTIMATE.in, HAIKU_ESTIMATE.out) })
    // nothing to show as saved (a rebuild barely above the limit): the plain suggestion
    const suggest = save.tokens > 0 && save.usd > 0 ? `🔄 Try ${HANDOFF} to save ${tokens(save.tokens)} tokens${dollars ? ` | ${money(save.usd)}` : ''}` : SUGGEST_NEW
    return isBigRebuild
      ? { light: 'red', text: `🔴 ${head} · ${suggest}`, shouldPopup: !rec.warned && !rec.resetBy }
      : { light: 'orange', text: `🟠 ${head} · Small chat, fine to keep going`, shouldPopup: false }
  }
  // yellow only on the 1h cache: a 5m window is too short for a useful warning
  if (rec.ttlMin >= 60 && left <= s.warnMinutes * 60_000) {
    const later = dollars ? `, later ≈ ${money(c.cold)}${more}` : `, later ${ratio ? `${ratio}× more` : r ? 'normal cost' : 'much more'}`
    return { light: 'yellow', text: `🟡 ${clock(left)} min left · ${nextWarm}${later}${ctx} · ⏳ Reply soon or try ${HANDOFF}`, shouldPopup: false }
  }
  // whole minutes, rounded up (your call: seconds ticking distract): never "0 min", and the last green is "16 min" before 🟡 15:00
  const head = `🟢 ${Math.ceil(left / 60_000)} min left · ${nextWarm}${ctx}`
  if (rec.prefix >= s.longChatTokens) {
    return { light: 'green', text: `${head} · ${SUGGEST_NEW}`, shouldPopup: false }
  }
  return { light: 'green', text: `${head} · ✅ Keep going`, shouldPopup: false }
}

// Shown before this chat's first reply, when there is nothing to measure yet.
export const WAITING = '⚪️ cache-maxxing will start after you send a message'

// The heads-up when you send into a red chat; the cause decides the wording.
export function sendWarning(rec: Rec): string {
  const why = rec.resetBy === 'model' ? 'the model changed' : rec.resetBy === 'compact' ? 'the chat was compacted' : "this chat's cache had expired"
  return `Heads-up: ${why}, so this message rebuilds the cache. See the bar for the cost.`
}

// Fills in a record for a chat this plugin never saw reply (older chats), from
// what Claude Code says at session start. Nothing is learned from it (read/write 0).
export function fromSessionStart(
  i: { secondsSince: number; contextTokens: number; model: string; window?: number },
  now: number, prev: Rec | null, s: Settings,
): Rec {
  const ttlMin = ttlFromUsage(s.memoryMinutes, {}, prev?.ttlMin) // nothing new written: the chat's last known lifetime
  return {
    at: now - i.secondsSince * 1000, prefix: i.contextTokens, out: 0, model: i.model, read: 0, write: 0,
    ttlMin, miss5: 0, warned: false, window: i.window ?? prev?.window, isEstimate: true,
  }
}

export function readSettings(o: Record<string, unknown>): Settings {
  const num = (v: unknown, d: number) => (typeof v === 'number' && v > 0 ? v : typeof v === 'string' && Number(v) > 0 ? Number(v) : d)
  return {
    rebuildLimitUsd: num(o.rebuildLimitUsd, DEFAULTS.rebuildLimitUsd),
    warnMinutes: num(o.warnMinutes, DEFAULTS.warnMinutes),
    longChatTokens: num(o.longChatTokens, DEFAULTS.longChatTokens),
    costStyle: o.costStyle === 'times' ? 'times' : 'dollars',
    memoryMinutes: o.memoryMinutes === '5' || o.memoryMinutes === '60' ? o.memoryMinutes : 'auto',
  }
}

// /cmaxx-stats: counters per chat (`st:<chat id>`) and for all chats (`st:all`). Counts only, never chat text.
export type Stats = {
  since: number // ms epoch of the first count
  replies: number
  read: number // cache read tokens
  write: number // cache write tokens
  input: number // uncached input tokens
  rebuilds: number // replies sent after the cache expired or was reset
  rebuildTokens: number
  rebuildUsd: number
  handoffs: number
  savedTokens: number // the handoff notice's own figures, counted only when the cache had expired
  savedUsd: number
  chats?: number // all chats only
  isFilled?: boolean // this chat's history was read from its transcript (or never needs reading)
  partialSince?: number // transcript too big to read: counted from this time only
  retired?: boolean // pruned after 90 days: its counts live on in st:retired, it counts as a chat there
}

const COUNTS = ['replies', 'read', 'write', 'input', 'rebuilds', 'rebuildTokens', 'rebuildUsd', 'handoffs', 'savedTokens', 'savedUsd', 'chats'] as const

export const emptyStats = (now: number): Stats => ({ since: now, replies: 0, read: 0, write: 0, input: 0, rebuilds: 0, rebuildTokens: 0, rebuildUsd: 0, handoffs: 0, savedTokens: 0, savedUsd: 0 })

// Adds `d` to `s`; an unreadable stored value counts as empty, never NaN.
export function addStats(s: unknown, d: Partial<Stats>, now: number): Stats {
  const base = { ...emptyStats(now), ...(s && typeof s === 'object' ? (s as Partial<Stats>) : {}) }
  const out: Stats = { ...base }
  for (const k of COUNTS) {
    const v = d[k]
    if (typeof v !== 'number') continue
    const cur = Number(base[k] ?? 0)
    out[k] = (Number.isFinite(cur) ? cur : 0) + v
  }
  if (!Number.isFinite(out.since)) out.since = now
  return out
}

// The /cmaxx-stats reply: this chat and all chats side by side.
export function statsText(chat: Stats, all: Stats, s: Settings): string {
  const date = (ms: number) => new Date(ms).toISOString().slice(0, 10)
  const usd = (n: number) => (n > 0 ? money(n) : '$0.00')
  const hit = (x: Stats) => {
    const total = x.read + x.write + x.input
    return total ? `${Math.round((x.read / total) * 100)}%` : '–'
  }
  const dollars = s.costStyle === 'dollars'
  const rebuilds = (x: Stats) => `${x.rebuilds}${x.rebuilds ? ` (${tokens(x.rebuildTokens)} tokens${dollars ? `, ${usd(x.rebuildUsd)}` : ''})` : ''}`
  const rows: [string, (x: Stats) => string, boolean?][] = [
    ['Saved by handoffs', x => usd(x.savedUsd), dollars],
    ['Tokens saved', x => tokens(x.savedTokens)],
    ['Cache hit rate', hit],
    ['Handoffs', x => String(x.handoffs)],
    ['Cold rebuilds paid', rebuilds],
    ['Replies', x => String(x.replies)],
  ]
  const lines = rows.filter(([, , show]) => show !== false).map(([name, f]) => `| ${name} | ${f(chat)} | ${f(all)} |`)
  return [
    'cache-maxxing stats',
    '',
    `| | This chat${chat.partialSince ? ` (since ${date(chat.partialSince)})` : ''} | All chats |`,
    '|---|---|---|',
    ...lines,
    `| Chats | – | ${all.chats ?? 0} |`,
  ].join('\n')
}

// "183K" / "1.2M" / "850" back to a number (the handoff notice's rounded figures).
const untokens = (t: string) => Number.parseFloat(t) * (t.endsWith('M') ? 1e6 : t.endsWith('K') ? 1e3 : 1)

// A chat's history from its transcript (JSONL), for chats this plugin never counted live.
// Each request is written once per content block: counted once per message id. A rebuild is a
// request more than the cache time after the one before (a model switch or /compact also resets the
// cache, but a transcript doesn't show it, so those rebuilds are counted only live). Handoffs come from this plugin's notice
// rows (a system row, or the command's output row), never from text that merely quotes one.
export function statsFromTranscript(jsonl: string, ttlMin: number): Partial<Stats> {
  const out = { replies: 0, read: 0, write: 0, input: 0, rebuilds: 0, rebuildTokens: 0, rebuildUsd: 0, handoffs: 0, savedTokens: 0, savedUsd: 0 }
  const seen = new Set<string>()
  let prevAt = 0
  for (const line of jsonl.split('\n')) {
    if (!line.includes('"usage"') && !line.includes('Handoff saved to')) continue
    let d: { type?: string; isSidechain?: boolean; timestamp?: string; content?: unknown; message?: { id?: string; model?: string; usage?: Record<string, number> } }
    try { d = JSON.parse(line) } catch { continue }
    if (d.type === 'system' && typeof d.content === 'string' && /^(?:<local-command-stdout>)?(?:[\w+.-]+: )?Handoff saved to /.test(d.content)) {
      out.handoffs++
      // "and <$0.01" too: its tokens still count, its dollars as 0
      const m = /You saved approx (\d+(?:\.\d+)?[KM]?) tokens and (<?)\$(\d+(?:\.\d+)?)/.exec(d.content)
      if (m) { out.savedTokens += untokens(m[1]!); out.savedUsd += m[2] ? 0 : Number(m[3]) }
      continue
    }
    const u = d.message?.usage
    if (d.type !== 'assistant' || d.isSidechain || !u || !d.message?.model || d.message.model.startsWith('<')) continue
    const id = d.message.id ?? `${d.timestamp}`
    if (seen.has(id)) continue
    seen.add(id)
    const at = Date.parse(d.timestamp ?? '')
    const read = u.cache_read_input_tokens ?? 0, write = u.cache_creation_input_tokens ?? 0
    out.replies++
    out.read += read
    out.write += write
    out.input += u.input_tokens ?? 0
    if (prevAt && Number.isFinite(at) && at - prevAt > ttlMin * 60_000) {
      const p = priceOf(d.message.model, read + write + (u.input_tokens ?? 0)) // Haiku's tier is by the whole prompt
      out.rebuilds++
      out.rebuildTokens += write
      out.rebuildUsd += p ? (write * p.input * (ttlMin >= 60 ? 2 : 1.25)) / 1e6 : 0
    }
    if (Number.isFinite(at)) prevAt = at
  }
  return out
}

// All chats, worked out when asked: every chat's own counts plus the pruned ones' (st:retired).
// Chats = chats with a reply, plus the retired ones (a resumed retired chat isn't counted twice).
export function sumStats(chats: unknown[], retired: unknown, now: number): Stats {
  let all = addStats(retired, {}, now)
  for (const c of chats) {
    const x = addStats(c, {}, now)
    all = addStats(all, { ...x, chats: x.replies > 0 && !(c as Stats).retired ? 1 : 0 }, now)
    if (x.since < all.since) all.since = x.since
  }
  return all
}

// The dev copy (built by scripts/dev-sync.sh as cache-maxxing-dev) never updates the real install.
// endsWith: dev-sync.sh renames every quoted 'cache-maxxing', so an equality check would flip.
export const isDevCopy = (name: string) => name.endsWith('-dev')

// /cmaxx-update: "0.10.0" is newer than "0.9.3". A pre-release or build tag ("0.4.1-rc.1", "+build.1")
// is compared by its numbers only.
export function newerVersion(a: string, b: string): boolean {
  const nums = (v: string) => v.split(/[-+]/)[0]!.split('.').map(Number)
  const pa = nums(a), pb = nums(b)
  for (let i = 0; i < 3; i++) {
    const x = pa[i] ?? 0, y = pb[i] ?? 0
    if (!Number.isFinite(x) || !Number.isFinite(y)) return false
    if (x !== y) return x > y
  }
  return false
}

// A downloaded prices.json, checked before it can change any figure: shape, sane amounts,
// at most 200 models, and never older than the bundled table.
export function validatePrices(json: unknown, bundledDate: string): { sourceDate: string; prices: Record<string, [number, number]> } | { error: string } {
  const j = json as { sourceDate?: unknown; prices?: unknown } | null
  if (!j || typeof j !== 'object' || typeof j.sourceDate !== 'string' || !/^\d{4}-\d\d-\d\d$/.test(j.sourceDate)) return { error: 'no valid sourceDate' }
  if (j.sourceDate < bundledDate) return { error: `older than the bundled prices (${j.sourceDate} < ${bundledDate})` }
  if (!j.prices || typeof j.prices !== 'object' || Array.isArray(j.prices)) return { error: 'no prices table' }
  const entries = Object.entries(j.prices as Record<string, unknown>)
  if (!entries.length || entries.length > 200) return { error: `${entries.length} models (1 to 200 expected)` }
  const prices: Record<string, [number, number]> = {}
  for (const [k, v] of entries) {
    if (!/^[a-z]+-\d+(?:-\d{1,2})?$/.test(k)) return { error: `bad model key ${JSON.stringify(k).slice(0, 40)}` }
    if (!Array.isArray(v) || v.length !== 2) return { error: `bad entry for ${k}` }
    const [input, read] = v as [unknown, unknown]
    if (typeof input !== 'number' || typeof read !== 'number' || !(input > 0 && input <= 100) || !(read > 0 && read <= input)) return { error: `bad price for ${k}` }
    prices[k] = [input, read]
  }
  return { sourceDate: j.sourceDate, prices }
}
