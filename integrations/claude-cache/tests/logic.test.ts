// Pure-logic tests: every bar state's exact text, cost math, TTL learning.
// These are surface-independent; tests/bar.test.tsx checks the same text on each surface.
import { expect, test } from 'claude-code/testing'

import type { Rec } from '../types'
import { DEFAULTS, HAIKU_ESTIMATE, clock, costs, decide, fromSessionStart, handoffSaving, haikuUsd, money, priceOf, sendWarning, setFreshStart, settingsFromConfig, statsText, tokens, ttlFor, ttlFromUsage } from '../hooks/logic'
import { savedText } from '../hooks/handoff'
import { WORDS, langOf } from '../hooks/i18n'

const W = WORDS.en
const P = WORDS.pt

const MIN = 60_000
const rec = (over: Partial<Rec> = {}): Rec => ({
  at: 0, prefix: 228_000, out: 0, model: 'claude-opus-5-5', read: 228_000, write: 0, ttlMin: 60, warned: false, window: 1_000_000, ...over,
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
  expect(decide(old as Rec, 10 * MIN, DEFAULTS, W).text.includes('NaN')).toBe(false)
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
  expect(decide(rec({ prefix: 50_000 }), 10 * MIN, DEFAULTS, W).text).toBe('🟢 50 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('green, long chat', async () => {
  expect(decide(rec({ prefix: 320_000 }), 10 * MIN, DEFAULTS, W).text).toBe('🟢 50 min left · next message ≈ $0.06 · 320K / 1M · 🔄 Try /quenching-cache handoff or a new chat')
})

test('yellow on 1h cache; 15:00 left is yellow, 15:01 is green', async () => {
  expect(decide(rec(), 57 * MIN, DEFAULTS, W).text).toBe('🟡 3:00 min left · next message ≈ $0.05, later ≈ $1.82 (40× more) · 228K / 1M · ⏳ Reply soon or try /quenching-cache handoff')
  expect(decide(rec(), 45 * MIN, DEFAULTS, W).light).toBe('yellow')
  expect(decide(rec(), 45 * MIN - 1_000, DEFAULTS, W).light).toBe('green')
})

test('green shows whole minutes, rounded up; yellow keeps the seconds', async () => {
  expect(decide(rec({ prefix: 50_000 }), 60 * MIN - (47 * MIN + 12_000), DEFAULTS, W).text.startsWith('🟢 48 min left ·')).toBe(true) // 47:12 left
  expect(decide(rec({ prefix: 50_000 }), 0, DEFAULTS, W).text.startsWith('🟢 60 min left ·')).toBe(true) // not "1:00:00"
  expect(decide(rec({ prefix: 50_000 }), 45 * MIN - 1_000, DEFAULTS, W).text.startsWith('🟢 16 min left ·')).toBe(true) // 15:01: last green
  expect(decide(rec({ prefix: 50_000 }), 47 * MIN + 30_000, DEFAULTS, W).text.startsWith('🟡 12:30 min left ·')).toBe(true)
  // 5m cache, last second: "1 min", never "0 min"
  expect(decide(rec({ prefix: 50_000, ttlMin: 5 }), 5 * MIN - 1_000, DEFAULTS, W).text.startsWith('🟢 1 min left ·')).toBe(true)
})

test('5m cache never shows yellow', async () => {
  const five = rec({ ttlMin: 5 })
  expect(decide(five, 1 * MIN, DEFAULTS, W).light).toBe('green')
  expect(decide(five, 4.9 * MIN, DEFAULTS, W).light).toBe('green')
  expect(decide(five, 6 * MIN, DEFAULTS, W).light).toBe('red')
})

test('red, expired big chat: popup once', async () => {
  const v = decide(rec(), 72 * MIN, DEFAULTS, W)
  expect(v.text).toBe('🔴 cache expired · next message ≈ $1.82 (40× more) · 228K / 1M · 🔄 Try /quenching-cache handoff to save 170K tokens | $1.71')
  expect(v.shouldPopup).toBe(true)
  expect(decide(rec({ warned: true }), 72 * MIN, DEFAULTS, W).shouldPopup).toBe(false)
})

test('orange, expired small chat: no popup', async () => {
  const v = decide(rec({ prefix: 20_000 }), 72 * MIN, DEFAULTS, W)
  expect(v.text).toBe('🟠 cache expired · next message ≈ $0.16 (40× more) · 20K / 1M · Small chat, fine to keep going')
  expect(v.shouldPopup).toBe(false)
})

test('model switch: reset at once on the new model, no popup', async () => {
  const v = decide(rec({ model: 'claude-sonnet-5-5', resetBy: 'model' }), 20 * MIN, DEFAULTS, W)
  expect(v.text).toBe('🔴 cache reset (model changed) · next message ≈ $0.91 (40× more) · 228K / 1M · 🔄 Try /quenching-cache handoff to save 170K tokens | $0.85')
  expect(v.shouldPopup).toBe(false)
})

test('compact: reset, usually small and orange', async () => {
  expect(decide(rec({ prefix: 30_000, resetBy: 'compact' }), 1 * MIN, DEFAULTS, W).text).toBe(
    '🟠 cache reset (chat compacted) · next message ≈ $0.24 (40× more) · 30K / 1M · Small chat, fine to keep going',
  )
})

test('times style hides dollars', async () => {
  expect(decide(rec(), 72 * MIN, { ...DEFAULTS, costStyle: 'times' }, W).text).toBe('🔴 cache expired · next message: 40× more · 228K / 1M · 🔄 Try /quenching-cache handoff to save 170K tokens')
  expect(decide(rec({ prefix: 50_000 }), 10 * MIN, { ...DEFAULTS, costStyle: 'times' }, W).text).toBe('🟢 50 min left · next message: normal cost · 50K / 1M · ✅ Keep going')
})

test('unknown model or window: no dollars, no context field', async () => {
  expect(decide(rec({ model: 'some-new-model' }), 72 * MIN, DEFAULTS, W).text.includes('$')).toBe(false)
  expect(decide(rec({ prefix: 50_000, window: undefined }), 10 * MIN, DEFAULTS, W).text).toBe('🟢 50 min left · next message ≈ $0.01 · ✅ Keep going')
})

test('send warning names the real cause', async () => {
  expect(sendWarning(rec({ resetBy: 'model' }), W).includes('the model changed')).toBe(true)
  expect(sendWarning(rec({ resetBy: 'compact' }), W).includes('compacted')).toBe(true)
  expect(sendWarning(rec(), W).includes('expired')).toBe(true)
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
  expect(decide(r, now, DEFAULTS, W).text).toBe('🔴 cache expired · next message ≈ $2.32 (40× more) · 290K / 1M · 🔄 Try /quenching-cache handoff to save 232K tokens | $2.21')
})

test('older chat still warm (20 min ago): green with the right time', async () => {
  const now = 10 * 60 * MIN
  const r = fromSessionStart({ secondsSince: 1200, contextTokens: 50_000, model: 'claude-opus-5-5', window: 1_000_000 }, now, null, DEFAULTS)
  expect(decide(r, now, DEFAULTS, W).text).toBe('🟢 40 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('older chat: "likely expired" after 10 min no longer shrinks the TTL to 5m', async () => {
  const r = fromSessionStart({ secondsSince: 600, contextTokens: 50_000, model: 'claude-opus-5-5' }, 0, null, DEFAULTS)
  expect(r.ttlMin).toBe(60)
})

test('sleep: countdown is wall-clock based', async () => {
  expect(decide(rec(), 10 * MIN, DEFAULTS, W).text.startsWith('🟢 50 min left')).toBe(true)
  expect(decide(rec(), 180 * MIN, DEFAULTS, W).text.startsWith('🔴 cache expired')).toBe(true)
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
  const text = decide({ ...tiny, at: -2 * 60 * MIN }, 0, DEFAULTS, W).text
  expect(text.includes('× more')).toBe(false)
  expect(decide({ ...tiny, at: -2 * 60 * MIN }, 0, { ...DEFAULTS, costStyle: 'times' }, W).text).toContain('next message: normal cost')
})

test('the 🔴 tip and the handoff notice use one calculation: same figures when Haiku uses the estimate', () => {
  const r = rec()
  const bar = decide(r, 72 * MIN, DEFAULTS, W).text
  const haiku = { ...HAIKU_ESTIMATE, usd: haikuUsd(HAIKU_ESTIMATE.in, HAIKU_ESTIMATE.out) }
  const notice = savedText(haiku, { model: r.model, tokens: r.prefix, cold: costs(r)!.cold, isCold: true })
  expect(bar.endsWith('to save 170K tokens | $1.71')).toBe(true)
  expect(notice).toBe(' ≈ 170K tokens · $1.71 (Opus).')
  expect(savedText(haiku, { model: r.model, tokens: r.prefix, cold: 1, isCold: false })).toBe('')
  expect(Math.round(haiku.usd * 1e6)).toBe(6_500) // $0.0065: 40K in at $0.10/M + 5K out at $0.50/M
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

test('a tip with nothing to save falls back to the plain suggestion', () => {
  // a 30K chat under a $0.01 limit: 30K - 45K Haiku - 13K start is below zero
  const v = decide(rec({ prefix: 30_000, read: 30_000 }), 72 * MIN, { ...DEFAULTS, rebuildLimitUsd: 0.01 }, W)
  expect(v.light).toBe('red')
  expect(v.text.endsWith('🔄 Try /quenching-cache handoff or a new chat')).toBe(true)
})


// --- quenching: settings from cq, the declared language, stats from cq ----------------------

test('settings come from cq config show --effective; a bad leaf keeps its default', () => {
  const shown = JSON.stringify({ values: [
    { key: 'shared.cache.rebuildLimitUsd', value: 2 }, { key: 'shared.cache.warnMinutes', value: 'x' },
    { key: 'shared.cache.ttlMinutes', value: '5' }, { key: 'shared.cache.costStyle', value: 'times' },
    { key: 'shared.contextBudgets.main', value: 150000 },
  ] })
  expect(settingsFromConfig(shown)).toEqual({ rebuildLimitUsd: 2, warnMinutes: 15, longChatTokens: 150_000, costStyle: 'times', ttlMinutes: '5' })
  expect(settingsFromConfig('not json')).toEqual(DEFAULTS)
  expect(DEFAULTS.longChatTokens).toBe(200_000) // shared.contextBudgets.main's default
})

test('the long-chat line is the main context budget', () => {
  expect(decide(rec({ prefix: 210_000 }), 10 * MIN, DEFAULTS, W).text.endsWith(`🔄 Try /quenching-cache handoff or a new chat`)).toBe(true)
  expect(decide(rec({ prefix: 210_000 }), 10 * MIN, { ...DEFAULTS, longChatTokens: 300_000 }, W).text.endsWith('✅ Keep going')).toBe(true)
})

test('the bar speaks the language the root harness declares', () => {
  expect(langOf('# x\n\nLanguage: pt-BR — the contract is /docs/standards/agents/communication.md\n')).toBe('pt')
  expect(langOf('Language: en')).toBe('en')
  expect(langOf(undefined)).toBe('en')
  expect(decide(rec(), 72 * MIN, DEFAULTS, P).text).toBe('🔴 cache expirado · próxima mensagem ≈ $1.82 (40× mais) · 228K / 1M · 🔄 Use /quenching-cache handoff e economize 170K tokens | $1.71')
  expect(decide(rec({ prefix: 50_000 }), 10 * MIN, DEFAULTS, P).text).toBe('🟢 50 min restantes · próxima mensagem ≈ $0.01 · 50K / 1M · ✅ Pode seguir')
})

test('stats: this chat and this project from cq components session cache --usd', () => {
  const row = (o: object) => ({ model: 'claude-opus-5-5', role: 'main', requests: 10, hitRate: 0.98, cacheWrite: 150_000, usd: 1.5, ...o })
  const project = JSON.stringify({ pricing: { sourceDate: '2026-11-17' }, rows: [row({}), row({ model: 'claude-haiku-5-5', role: 'subagent', usd: 0.2 })] })
  const chat = JSON.stringify({ pricing: { sourceDate: '2026-11-17' }, rows: [row({ requests: 3, usd: null })] })
  expect(statsText(chat, project, W)).toBe([
    'quenching-cache stats (list prices of 2026-11-17; an estimate, not a bill)',
    '',
    '| | Model | Requests | Cache hit | Cache writes | ≈ USD |',
    '|---|---|---|---|---|---|',
    '| This chat | claude-opus-5-5 | 3 | 98% | 150K | – |',
    '| This project | claude-opus-5-5 | 10 | 98% | 150K | $1.50 |',
    '| This project | claude-haiku-5-5 (subagent) | 10 | 98% | 150K | $0.20 |',
    '| This project | **total** | | | | $1.70 |',
  ].join('\n'))
  expect(statsText(null, '{"ok":false}', W)).toBe(null)
})
