// Pure-logic tests: every bar state's exact text, cost math, TTL learning.
// These are surface-independent; tests/bar.test.tsx checks the same text on each surface.
import { expect, test } from 'claude-code/testing'

import type { Rec } from '../types'
import { DEFAULTS, HAIKU_ESTIMATE, PRICES_DATE, addStats, clock, costs, decide, emptyStats, fromSessionStart, handoffSaving, haikuUsd, money, newerVersion, priceOf, sendWarning, setFreshStart, setPriceOverride, statsFromTranscript, statsText, isDevCopy, isNewModel, sumStats, tokens, ttlFor, ttlFromUsage, validatePrices } from '../hooks/logic'
import { savingsLine } from '../hooks/handoff'

const MIN = 60_000
const rec = (over: Partial<Rec> = {}): Rec => ({
  at: 0, prefix: 228_000, out: 0, model: 'claude-opus-5-5', read: 228_000, write: 0, ttlMin: 60, miss5: 0, warned: false, window: 1_000_000, ...over,
})

// --- cost math -------------------------------------------------------------

test('costs: Opus 5.5, 228K, 1h cache, worked by hand', async () => {
  const c = costs(rec())!
  expect(Math.abs(c.warm - 0.0456) < 1e-9).toBe(true) // 228K x $0.20/M
  expect(Math.abs(c.cold - 1.824) < 1e-9).toBe(true) // 228K x $4/M x 2
})

test('costs: last reply output is written, not read, on the warm path', async () => {
  // 218K read at $0.20/M + 10K written at $8/M = 0.0436 + 0.08
  expect(Math.abs(costs(rec({ out: 10_000 }))!.warm - 0.1236) < 1e-9).toBe(true)
})

test('costs: 5m cache writes at 1.25x', async () => {
  expect(Math.abs(costs(rec({ ttlMin: 5 }))!.cold - 1.14) < 1e-9).toBe(true) // 228K x $4 x 1.25
})

test('costs: a record from an older version (no `out`) never shows NaN', async () => {
  const old = { ...rec() } as Partial<Rec>
  delete old.out
  expect(decide(old as Rec, 10 * MIN, DEFAULTS).text.includes('NaN')).toBe(false)
})

test('prices: exact version match, platform prefixes, dates, 1m, fast', async () => {
  expect(priceOf('claude-opus-5', 1)!.input).toBe(5)
  expect(priceOf('claude-opus-5-5', 1)!.input).toBe(4)
  expect(priceOf('us.anthropic.claude-opus-5-5', 1)!.input).toBe(4)
  expect(priceOf('claude-opus-5-5[1m]', 1)!.input).toBe(4)
  expect(priceOf('claude-opus-4-5-20251101', 1)!.input).toBe(5)
  expect(priceOf('claude-opus-5-5-fast', 1)!.input).toBe(8)
  expect(priceOf('claude-fable-5-1', 1)!.read).toBe(0.25) // review finding: was $1
  expect(priceOf('claude-opus-5-6', 1)).toBe(null) // unknown newer model is not Opus 5's price
  expect(priceOf('claude-fable-5-3', 1)).toBe(null)
  expect(priceOf('claude-haiku-5-5', 150_000)!.input).toBe(0.5)
  expect(priceOf('gpt-x', 1)).toBe(null)
})

test('formats: clock, tokens, money', async () => {
  expect(clock(47 * MIN + 5_000)).toBe('47:05')
  expect(clock(-1)).toBe('0:00')
  expect(tokens(290_400)).toBe('290K')
  expect(tokens(1_000_000)).toBe('1M')
  expect(tokens(1_500_000)).toBe('1.5M')
  expect(money(0.0456)).toBe('$0.05')
  expect(money(0.004)).toBe('<$0.01')
  expect(money(1.824)).toBe('$1.82')
  expect(money(23.4)).toBe('$23')
})

// --- every bar state, exact text (the contract the docs show) ---------------

test('green, keep going', async () => {
  expect(decide(rec({ prefix: 50_000 }), 10 * MIN, DEFAULTS).text).toBe('🟢 50 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('green, long chat', async () => {
  expect(decide(rec({ prefix: 320_000 }), 10 * MIN, DEFAULTS).text).toBe('🟢 50 min left · next message ≈ $0.06 · 320K / 1M · 🔄 Try /cmaxx-handoff or a new chat')
})

test('yellow on 1h cache; 15:00 left is yellow, 15:01 is green', async () => {
  expect(decide(rec(), 57 * MIN, DEFAULTS).text).toBe('🟡 3:00 min left · next message ≈ $0.05, later ≈ $1.82 (40× more) · 228K / 1M · ⏳ Reply soon or try /cmaxx-handoff')
  expect(decide(rec(), 45 * MIN, DEFAULTS).light).toBe('yellow')
  expect(decide(rec(), 45 * MIN - 1_000, DEFAULTS).light).toBe('green')
})

test('green shows whole minutes, rounded up; yellow keeps the seconds', async () => {
  expect(decide(rec({ prefix: 50_000 }), 60 * MIN - (47 * MIN + 12_000), DEFAULTS).text.startsWith('🟢 48 min left ·')).toBe(true) // 47:12 left
  expect(decide(rec({ prefix: 50_000 }), 0, DEFAULTS).text.startsWith('🟢 60 min left ·')).toBe(true) // not "1:00:00"
  expect(decide(rec({ prefix: 50_000 }), 45 * MIN - 1_000, DEFAULTS).text.startsWith('🟢 16 min left ·')).toBe(true) // 15:01: last green
  expect(decide(rec({ prefix: 50_000 }), 47 * MIN + 30_000, DEFAULTS).text.startsWith('🟡 12:30 min left ·')).toBe(true)
  // 5m cache, last second: "1 min", never "0 min"
  expect(decide(rec({ prefix: 50_000, ttlMin: 5 }), 5 * MIN - 1_000, DEFAULTS).text.startsWith('🟢 1 min left ·')).toBe(true)
})

test('5m cache never shows yellow', async () => {
  const five = rec({ ttlMin: 5 })
  expect(decide(five, 1 * MIN, DEFAULTS).light).toBe('green')
  expect(decide(five, 4.9 * MIN, DEFAULTS).light).toBe('green')
  expect(decide(five, 6 * MIN, DEFAULTS).light).toBe('red')
})

test('red, expired big chat: popup once', async () => {
  const v = decide(rec(), 72 * MIN, DEFAULTS)
  expect(v.text).toBe('🔴 cache expired · next message ≈ $1.82 (40× more) · 228K / 1M · 🔄 Try /cmaxx-handoff to save 170K tokens | $1.71')
  expect(v.shouldPopup).toBe(true)
  expect(decide(rec({ warned: true }), 72 * MIN, DEFAULTS).shouldPopup).toBe(false)
})

test('orange, expired small chat: no popup', async () => {
  const v = decide(rec({ prefix: 20_000 }), 72 * MIN, DEFAULTS)
  expect(v.text).toBe('🟠 cache expired · next message ≈ $0.16 (40× more) · 20K / 1M · Small chat, fine to keep going')
  expect(v.shouldPopup).toBe(false)
})

test('model switch: reset at once on the new model, no popup', async () => {
  const v = decide(rec({ model: 'claude-sonnet-5-5', resetBy: 'model' }), 20 * MIN, DEFAULTS)
  expect(v.text).toBe('🔴 cache reset (model changed) · next message ≈ $0.91 (40× more) · 228K / 1M · 🔄 Try /cmaxx-handoff to save 170K tokens | $0.85')
  expect(v.shouldPopup).toBe(false)
})

test('compact: reset, usually small and orange', async () => {
  expect(decide(rec({ prefix: 30_000, resetBy: 'compact' }), 1 * MIN, DEFAULTS).text).toBe(
    '🟠 cache reset (chat compacted) · next message ≈ $0.24 (40× more) · 30K / 1M · Small chat, fine to keep going',
  )
})

test('times style hides dollars', async () => {
  expect(decide(rec(), 72 * MIN, { ...DEFAULTS, costStyle: 'times' }).text).toBe('🔴 cache expired · next message: 40× more · 228K / 1M · 🔄 Try /cmaxx-handoff to save 170K tokens')
  expect(decide(rec({ prefix: 50_000 }), 10 * MIN, { ...DEFAULTS, costStyle: 'times' }).text).toBe('🟢 50 min left · next message: normal cost · 50K / 1M · ✅ Keep going')
})

test('unknown model or window: no dollars, no context field', async () => {
  expect(decide(rec({ model: 'some-new-model' }), 72 * MIN, DEFAULTS).text.includes('$')).toBe(false)
  expect(decide(rec({ prefix: 50_000, window: undefined }), 10 * MIN, DEFAULTS).text).toBe('🟢 50 min left · next message ≈ $0.01 · ✅ Keep going')
})

test('send warning names the real cause', async () => {
  expect(sendWarning(rec({ resetBy: 'model' })).includes('the model changed')).toBe(true)
  expect(sendWarning(rec({ resetBy: 'compact' })).includes('compacted')).toBe(true)
  expect(sendWarning(rec()).includes('expired')).toBe(true)
})

// --- TTL ---------------------------------------------------------------------
// Auto is always 1h: the main chat never wrote a 5m cache in any measured session (FACTS F37).

test('TTL: auto starts at 1h; the setting forces 5 or 60', async () => {
  expect(ttlFor('auto')).toBe(60)
  expect(ttlFor('5')).toBe(5)
  expect(ttlFor('60')).toBe(60)
})

test('TTL auto follows the reply\'s cache write: 5m on an API key or usage credits (issue #4)', async () => {
  expect(ttlFromUsage('auto', { ephemeral_1h_input_tokens: 900, ephemeral_5m_input_tokens: 0 })).toBe(60)
  expect(ttlFromUsage('auto', { ephemeral_1h_input_tokens: 0, ephemeral_5m_input_tokens: 900 })).toBe(5)
  expect(ttlFromUsage('auto', {}, 5)).toBe(5) // nothing written: the chat's last known lifetime
  expect(ttlFromUsage('auto', {})).toBe(60)
  expect(ttlFromUsage('60', { ephemeral_5m_input_tokens: 900 })).toBe(60) // a forced setting wins
  expect(fromSessionStart({ secondsSince: 60, contextTokens: 50_000, model: 'claude-opus-5-5' }, 0, rec({ ttlMin: 5 }), DEFAULTS).ttlMin).toBe(5)
})

// --- older chats -------------------------------------------------------------

test('older chat filled in from session start: expired 2h ago, red', async () => {
  const now = 10 * 60 * MIN
  const r = fromSessionStart({ secondsSince: 7200, contextTokens: 290_000, model: 'claude-opus-5-5', window: 1_000_000 }, now, null, DEFAULTS)
  expect(r.isEstimate).toBe(true)
  expect(decide(r, now, DEFAULTS).text).toBe('🔴 cache expired · next message ≈ $2.32 (40× more) · 290K / 1M · 🔄 Try /cmaxx-handoff to save 232K tokens | $2.21')
})

test('older chat still warm (20 min ago): green with the right time', async () => {
  const now = 10 * 60 * MIN
  const r = fromSessionStart({ secondsSince: 1200, contextTokens: 50_000, model: 'claude-opus-5-5', window: 1_000_000 }, now, null, DEFAULTS)
  expect(decide(r, now, DEFAULTS).text).toBe('🟢 40 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('older chat: "likely expired" after 10 min no longer shrinks the TTL to 5m', async () => {
  const r = fromSessionStart({ secondsSince: 600, contextTokens: 50_000, model: 'claude-opus-5-5' }, 0, null, DEFAULTS)
  expect(r.ttlMin).toBe(60)
})

test('sleep: countdown is wall-clock based', async () => {
  expect(decide(rec(), 10 * MIN, DEFAULTS).text.startsWith('🟢 50 min left')).toBe(true)
  expect(decide(rec(), 180 * MIN, DEFAULTS).text.startsWith('🔴 cache expired')).toBe(true)
})

test('rounding edges: no "1000K", no "$10.00", no "(1× more)"', () => {
  expect(tokens(999_499)).toBe('999K')
  expect(tokens(999_500)).toBe('1M')
  expect(money(9.994)).toBe('$9.99')
  expect(money(9.996)).toBe('$10')
  expect(money(0.004)).toBe('<$0.01')
  // a chat that is almost all the last reply: rebuilding costs about the same as a warm message
  const tiny = rec({ prefix: 2_000, out: 2_000, read: 0 })
  const c = costs(tiny)!
  expect(Math.round(c.cold / c.warm)).toBeLessThan(2)
  const text = decide({ ...tiny, at: -2 * 60 * MIN }, 0, DEFAULTS).text
  expect(text.includes('× more')).toBe(false)
  expect(decide({ ...tiny, at: -2 * 60 * MIN }, 0, { ...DEFAULTS, costStyle: 'times' }).text).toContain('next message: normal cost')
})

test('the 🔴 tip and the handoff notice use one calculation: same figures when Haiku uses the estimate', () => {
  const r = rec()
  const bar = decide(r, 72 * MIN, DEFAULTS).text
  const haiku = { ...HAIKU_ESTIMATE, usd: haikuUsd(HAIKU_ESTIMATE.in, HAIKU_ESTIMATE.out) }
  const notice = savingsLine({ path: 'x.md', haiku, main: { model: r.model, tokens: r.prefix, cold: costs(r)!.cold, isCold: true } })
  expect(bar.endsWith('to save 170K tokens | $1.71')).toBe(true)
  expect(notice.endsWith('You saved approx 170K tokens and $1.71.')).toBe(true)
  expect(Math.round(haiku.usd * 1e6)).toBe(6_500) // $0.0065: 40K in at $0.10/M + 5K out at $0.50/M
})

test('stats: counts add up, junk counts as empty, the table puts this chat and all chats side by side', () => {
  const now = Date.UTC(2026, 10, 17)
  expect(addStats({ replies: 'x' }, { replies: 1 }, now).replies).toBe(1)
  const chat = addStats(addStats(undefined, { replies: 1, read: 90, write: 10 }, now), { rebuilds: 1, rebuildTokens: 228_000, rebuildUsd: 1.82, handoffs: 1, savedTokens: 183_000, savedUsd: 1.8175 }, now)
  const all = { ...addStats(chat, { replies: 4, read: 100 }, now), chats: 3 }
  expect(statsText(chat, all, DEFAULTS)).toBe([
    'cache-maxxing stats',
    '',
    '| | This chat | All chats |',
    '|---|---|---|',
    '| Saved by handoffs | $1.82 | $1.82 |',
    '| Tokens saved | 183K | 183K |',
    '| Cache hit rate | 90% | 95% |',
    '| Handoffs | 1 | 1 |',
    '| Cold rebuilds paid | 1 (228K tokens, $1.82) | 1 (228K tokens, $1.82) |',
    '| Replies | 1 | 5 |',
    '| Chats | – | 3 |',
  ].join('\n'))
  // zero dollars read "$0.00", not "<$0.01"; a chat too big to read says since when it was counted
  const empty = statsText({ ...emptyStats(now), partialSince: now }, emptyStats(now), DEFAULTS)
  expect(empty).toContain('| Saved by handoffs | $0.00 | $0.00 |')
  expect(empty).toContain('| | This chat (since 2026-11-17) | All chats |')
  // times style: no dollar rows or amounts
  const t = statsText(emptyStats(now), emptyStats(now), { ...DEFAULTS, costStyle: 'times' })
  expect(t.includes('$')).toBe(false)
  expect(t).toContain('| Cache hit rate | – | – |')
})

// --- 0.4.0: transcript fill-in, /cmaxx-update ----------------------------------------
const row = (o: object) => JSON.stringify(o)
const asst = (id: string, at: string, read: number, write: number, extra: object = {}) =>
  row({ type: 'assistant', timestamp: at, message: { id, model: 'claude-opus-5-5', usage: { input_tokens: 2, cache_read_input_tokens: read, cache_creation_input_tokens: write, output_tokens: 10 } }, ...extra })

test('transcript: requests counted once, rebuilds after the cache time, handoffs only from notice rows', () => {
  const jsonl = [
    asst('a1', '2026-11-17T10:00:00Z', 0, 50_000),
    asst('a1', '2026-11-17T10:00:01Z', 0, 50_000), // same request, second content block
    asst('s1', '2026-11-17T10:05:00Z', 9_000, 0, { isSidechain: true }), // subagent
    asst('a2', '2026-11-17T10:30:00Z', 50_000, 0),
    asst('a3', '2026-11-17T12:00:00Z', 0, 228_000), // 90 min later: a rebuild
    row({ type: 'system', subtype: 'informational', content: 'Handoff saved to .claude/handoffs/x.md. This command never resent the chat to Opus: no cache read, no rebuild. You saved approx 183K tokens and $1.82.' }),
    row({ type: 'system', subtype: 'local_command', content: '<local-command-stdout>ponytail+cache-maxxing: Handoff saved to .claude/handoffs/y.md. This command never resent the chat to Opus: no cache read, no rebuild.</local-command-stdout>' }),
    row({ type: 'user', message: { role: 'user', content: 'it said: Handoff saved to z.md. You saved approx 999K tokens and $9.99.' } }), // a quote, not a notice
    row({ type: 'queue-operation', content: 'Handoff saved to q.md. You saved approx 999K tokens and $9.99.' }), // a queued prompt, not a notice
    'not json',
  ].join('\n')
  expect(statsFromTranscript(jsonl, 60)).toEqual({
    replies: 3, read: 50_000, write: 278_000, input: 6,
    rebuilds: 1, rebuildTokens: 228_000, rebuildUsd: 1.824,
    handoffs: 2, savedTokens: 183_000, savedUsd: 1.82,
  })
})

test('versions compare as numbers', () => {
  expect(newerVersion('0.10.0', '0.9.3')).toBe(true)
  expect(newerVersion('0.4.0', '0.4.0')).toBe(false)
  expect(newerVersion('0.3.9', '0.4.0')).toBe(false)
  expect(newerVersion('1.0', '0.9.9')).toBe(true)
  expect(newerVersion('x', '0.1.0')).toBe(false)
  expect(newerVersion('0.4.1+build.1', '0.4.0')).toBe(true) // issue #6
  expect(newerVersion('0.5.0-rc.1', '0.4.0')).toBe(true)
  expect(newerVersion('0.4.0', '0.4.0+build.2')).toBe(false)
})

test('transcript: a "<$0.01" saving keeps its tokens; the Haiku tier counts uncached input (issue #6)', () => {
  const note = row({ type: 'system', content: 'Handoff saved to x.md. This command never resent the chat to Haiku: no cache read, no rebuild. You saved approx 12K tokens and <$0.01.' })
  expect(statsFromTranscript(note, 60)).toMatchObject({ handoffs: 1, savedTokens: 12_000, savedUsd: 0 })
  // 98K cached + 3K uncached = 101K: the 5x tier
  const h = (id: string, at: string) => row({ type: 'assistant', timestamp: at, message: { id, model: 'claude-haiku-5-5', usage: { input_tokens: 3_000, cache_read_input_tokens: 0, cache_creation_input_tokens: 98_000, output_tokens: 1 } } })
  const s = statsFromTranscript([h('a', '2026-11-17T10:00:00Z'), h('b', '2026-11-17T12:00:00Z')].join('\n'), 60)
  expect(Math.abs(s.rebuildUsd! - (98_000 * 0.1 * 5 * 2) / 1e6) < 1e-9).toBe(true)
})

test('handoff saving: the fresh chat\'s size is learned from the user\'s own first replies (issue #3)', () => {
  // 228K expired on Opus 5.5, Haiku 45K: the default 13K start
  expect(handoffSaving(228_000, 1.824, { in: 40_000, out: 5_000, usd: 0 }).tokens).toBe(170_000)
  setFreshStart([42_000, 40_000, 44_000]) // median 42K + 4K brief read
  expect(handoffSaving(228_000, 1.824, { in: 40_000, out: 5_000, usd: 0 }).tokens).toBe(137_000)
  setFreshStart([90_000, 'x', -1]) // under 3 good samples: back to the default
  expect(handoffSaving(228_000, 1.824, { in: 40_000, out: 5_000, usd: 0 }).tokens).toBe(170_000)
  setFreshStart(undefined)
})

test('a downloaded price table is refused unless it is sane and not older than the bundled one', () => {
  const ok = { sourceDate: PRICES_DATE, prices: { 'opus-6': [5, 0.5] } }
  expect(validatePrices(ok, PRICES_DATE)).toEqual(ok)
  for (const bad of [
    null, 'x', { prices: ok.prices }, { sourceDate: '2026-1-1', prices: ok.prices },
    { sourceDate: '2026-01-01', prices: ok.prices }, // older than bundled
    { sourceDate: PRICES_DATE, prices: {} },
    { sourceDate: PRICES_DATE, prices: { 'Opus 6': [5, 0.5] } },
    { sourceDate: PRICES_DATE, prices: { 'opus-6': [-5, 0.5] } },
    { sourceDate: PRICES_DATE, prices: { 'opus-6': [5, 6] } }, // read above input
    { sourceDate: PRICES_DATE, prices: { 'opus-6': [500, 0.5] } },
    { sourceDate: PRICES_DATE, prices: { 'opus-6': ['5', 0.5] } },
    { sourceDate: PRICES_DATE, prices: Object.fromEntries(Array.from({ length: 201 }, (_, i) => [`m-${i}`, [1, 0.1]])) },
  ]) expect('error' in validatePrices(bad, PRICES_DATE)).toBe(true)
})

test('an unknown model nudges to /cmaxx-update until a downloaded price covers it', () => {
  const r = rec({ model: 'claude-opus-6', prefix: 50_000 })
  expect(decide(r, 10 * MIN, DEFAULTS).text).toBe('🟢 50 min left · next message: normal cost · 50K / 1M · ✅ Keep going · new model? try /cmaxx-update')
  setPriceOverride({ 'opus-6': [5, 0.5] })
  try {
    expect(decide(r, 10 * MIN, DEFAULTS).text).toBe('🟢 50 min left · next message ≈ $0.03 · 50K / 1M · ✅ Keep going')
    expect(priceOf('claude-opus-5-5', 1)).toEqual({ input: 4, read: 0.2 }) // bundled prices still apply to the rest
  } finally {
    setPriceOverride(null)
  }
})

// --- final-review fixes ------------------------------------------------------------
test('the dev copy is told apart by its -dev suffix, which dev-sync.sh\'s rename cannot flip', () => {
  expect(isDevCopy('cache-maxxing-dev')).toBe(true)
  expect(isDevCopy('cache-maxxing')).toBe(false)
  expect(isDevCopy('some-other-plugin')).toBe(false) // an equality check against one name would say true
})

test('"new model?" only for a model newer than every priced one of its family', () => {
  expect(isNewModel('claude-opus-6')).toBe(true)
  expect(isNewModel('claude-sonnet-6-1-20270101')).toBe(true)
  expect(isNewModel('claude-newfamily-1')).toBe(true)
  expect(isNewModel('claude-sonnet-3-5')).toBe(false) // old, unpriced
  expect(isNewModel('claude-3-7-sonnet-20250219')).toBe(false) // old-style id
  expect(priceOf('claude-opus-4-1-20250805', 1)).toEqual({ input: 15, read: 1.5 }) // older models now priced
  expect(priceOf('claude-sonnet-4-20250514', 1)).toEqual({ input: 3, read: 0.3 })
  expect(decide(rec({ model: 'claude-sonnet-3-5' }), 10 * MIN, DEFAULTS).text.includes('new model?')).toBe(false)
})

test('a tip with nothing to save falls back to the plain suggestion', () => {
  // a 30K chat under a $0.01 limit: 30K - 45K Haiku - 13K start is below zero
  const v = decide(rec({ prefix: 30_000, read: 30_000 }), 72 * MIN, { ...DEFAULTS, rebuildLimitUsd: 0.01 })
  expect(v.light).toBe('red')
  expect(v.text.endsWith('🔄 Try /cmaxx-handoff or a new chat')).toBe(true)
})

test('All chats: every chat summed with the retired ones; a chat with no reply or already retired is not counted again', () => {
  const now = 0
  const a = { ...emptyStats(now), replies: 3, read: 10 }
  const empty = emptyStats(now)
  const back = { ...emptyStats(now), replies: 1, retired: true } // resumed after retiring
  const all = sumStats([a, empty, back], { ...emptyStats(now), replies: 5, chats: 2 }, now)
  expect(all.replies).toBe(9)
  expect(all.chats).toBe(3)
})
