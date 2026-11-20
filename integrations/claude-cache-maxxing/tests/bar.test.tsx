// End-to-end tests through the real hooks: a reply, a model switch, a compact, an
// older chat, /clear, an app restart. Each draws the bar on every surface and expects
// the SAME text, so a change made for VS Code or the terminal can't silently break desktop.
import { expect, mock, test } from 'claude-code/testing'

import { PRICES_DATE } from '../hooks/logic'

const SURFACES = ['desktop', 'vscode', 'terminal'] as const
const MIN = 60_000
const T0 = 1_800_000_000_000
const HIDDEN = '(engine)' // what Claude Code draws when the plugin shows nothing
const WAITING = '⚪️ cache-maxxing will start after you send a message'
const BAR = { plugin: 'quenching-cache-maxxing', component: 'AbovePrompt', props: { hasSurvey: false, isCollapsed: false, isWorking: false } as never } as const // the kit fills the rest of the band's props

type Body = Extract<Parameters<typeof test>[1], (...args: never[]) => unknown>
type On = Parameters<Body>[1]
type Dollar = Parameters<Body>[0]
type Usage = { read: number; write: number; out?: number; model?: string; ttl?: 5 | 60 } // ttl: the lifetime the write reports

// The engine beneath the plugin (one chat, Opus 5.5, 1M window). Every stand-in is
// registered here, before the test's first call on $, as the kit requires.
function engine(on: On, opts: { store?: Record<string, unknown>; state?: unknown; streamMs?: number; brokenStore?: boolean; now?: number; contextTokens?: number } = {}) {
  const clock = mock.clock(on, { now: opts.now ?? T0 })
  if (opts.brokenStore) for (const k of ['store.get', 'store.set', 'store.delete', 'store.keys'] as const) on(k, () => { throw new Error('store broken') })
  else mock.store(on, opts.store)
  const toasts: string[] = []
  let usage: Usage = { read: 0, write: 0 }
  const steps = { n: 0 } // main-model requests the engine saw
  on('session.id', () => ({ value: 'chat-1' }))
  on('session.model', () => ({ value: 'claude-opus-5-5' }))
  on('session.usage', () => ({ value: { startedAt: T0, context: { window: 1_000_000, ...(opts.contextTokens !== undefined ? { tokens: opts.contextTokens } : {}) } } }) as never)
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('session.end', (_, e) => ({ sessionId: e.sessionId }))
  on('classic.SessionStart', () => ({}))
  on('classic.PostModelSwitch', () => ({}))
  on('classic.PostCompact', () => ({}))
  const commands: string[] = []
  on('command.register', (_, e) => { commands.push((e as { name: string }).name); return { value: { command: 'cmaxx' } } as never })
  on('ui.toast', (_, e) => { toasts.push(JSON.stringify(e)); return { value: undefined } })
  on('ui.render', ($, e) => { const { Text } = $.ui.resolve(e); return <Text>{HIDDEN}</Text> })
  if (opts.state !== undefined) on('state.get', () => ({ value: { value: opts.state, version: 1 } }))
  on('turn.step', async function* () {
    steps.n++
    if (opts.streamMs) await clock.advance(opts.streamMs)
    return {
      turnId: 't', index: 0, answer: '', toolUses: [], stopReason: 'end_turn',
      usage: { input_tokens: 0, output_tokens: usage.out ?? 0, cache_read_input_tokens: usage.read, cache_creation_input_tokens: usage.write, model: usage.model ?? 'claude-opus-5-5',
        ...(usage.ttl ? { ephemeral_5m_input_tokens: usage.ttl === 5 ? usage.write : 0, ephemeral_1h_input_tokens: usage.ttl === 60 ? usage.write : 0 } : {}) },
    }
  })
  return {
    clock,
    toasts,
    commands,
    steps,
    async reply($: Dollar, u: Usage, agentId?: string) {
      usage = u
      const s = $.turn.step({ turnId: 't', index: 0, model: u.model ?? 'claude-opus-5-5', messageCount: 2, ...(agentId ? { agentId } : {}) })
      for await (const _ of s) { /* drain */ }
    },
  }
}

async function bars($: Dollar) {
  const out: (string | null)[] = []
  for (const surface of SURFACES) {
    const ui = await $.ui.mount({ ...BAR, surface })
    out.push((await ui.find({ type: 'Text' }))?.text ?? null)
    await ui.unmount()
  }
  return out
}

async function expectBar($: Dollar, text: string) {
  expect(await bars($)).toEqual(SURFACES.map(() => text))
}

async function start($: Dollar, surface: (typeof SURFACES)[number] = 'desktop') {
  await $.session.start({ cwd: '/', surface, isInteractive: true })
}

test('no reply yet: the waiting line on every surface', async ($, on) => {
  engine(on)
  await start($)
  await expectBar($, WAITING)
})

test('after a reply: green with the countdown, identical on desktop, vscode, terminal', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 45_000, write: 5_000 })
  await w.clock.advance(10 * MIN)
  await expectBar($, '🟢 50 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('countdown starts at the request, not the end of a 3-minute reply', async ($, on) => {
  const w = engine(on, { streamMs: 3 * MIN })
  await start($)
  await w.reply($, { read: 50_000, write: 0 })
  await expectBar($, '🟢 57 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('subagent steps do not move the clock', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 50_000, write: 0 })
  await w.clock.advance(30 * MIN)
  await w.reply($, { read: 900_000, write: 0 }, 'agent-7')
  await expectBar($, '🟢 30 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('ticks to yellow, then red, with exactly one pop-up', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 228_000, write: 0 })
  await w.clock.advance(57 * MIN)
  await expectBar($, '🟡 3:00 min left · next message ≈ $0.05, later ≈ $1.82 (40× more) · 228K / 1M · ⏳ Reply soon or try /cmaxx-handoff')
  await w.clock.advance(15 * MIN)
  await expectBar($, '🔴 cache expired · next message ≈ $1.82 (40× more) · 228K / 1M · 🔄 Try /cmaxx-handoff to save 170K tokens | $1.71')
  await w.clock.advance(5 * MIN)
  // the pop-up says exactly what the bar says
  expect(w.toasts.filter(t => t.includes('🔴 cache expired · next message ≈ $1.82 (40× more) · 228K / 1M · 🔄 Try /cmaxx-handoff to save 170K tokens | $1.71')).length).toBe(1)
})

test('model switch re-prices at once; a resume "switch" does not', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 228_000, write: 0 })
  const sw = { requested_model: null, context_tokens: 228_000, prompt_cache_warm: true, cache_ttl: '1h', estimated_cache_write_usd: 1, pricing: 'catalog' }
  await $.classic.PostModelSwitch({ ...sw, from_model: 'claude-sonnet-5-5', to_model: 'claude-opus-5-5', source: 'resume' } as never)
  expect((await bars($))[0]?.startsWith('🟢')).toBe(true)
  await $.classic.PostModelSwitch({ ...sw, from_model: 'claude-opus-5-5', to_model: 'claude-sonnet-5-5', source: 'command' } as never)
  await expectBar($, '🔴 cache reset (model changed) · next message ≈ $0.91 (40× more) · 228K / 1M · 🔄 Try /cmaxx-handoff to save 170K tokens | $0.85')
})

// Seen live 2026-11-16: /model switches then /compact left the next reply's countdown at 5:00.
test('after model switches and a compact, the next reply counts down from a full hour', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 228_000, write: 0 })
  const sw = { requested_model: 'haiku', context_tokens: 228_000, prompt_cache_warm: true, cache_ttl: '5m', estimated_cache_write_usd: 1, pricing: 'catalog', source: 'command' }
  await $.classic.PostModelSwitch({ ...sw, from_model: 'claude-opus-5-5', to_model: 'claude-haiku-5-5' } as never)
  await $.classic.PostModelSwitch({ ...sw, from_model: 'claude-haiku-5-5', to_model: 'claude-opus-5-5' } as never)
  await $.classic.PostCompact({ trigger: 'manual', compact_summary: 'x'.repeat(40_000) } as never)
  await w.clock.advance(20 * MIN)
  await $.classic.SessionStart({ source: 'compact', session_id: 'chat-1', seconds_since_last_response: 1200, context_tokens: 30_000, prompt_cache_likely_expired: true, model: 'claude-opus-5-5' } as never)
  await w.reply($, { read: 0, write: 30_000 })
  await expectBar($, '🟢 60 min left · next message ≈ <$0.01 · 30K / 1M · ✅ Keep going')
})

test('compact resets the cache at once', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 228_000, write: 0 })
  await $.classic.PostCompact({ trigger: 'manual', compact_summary: 'x'.repeat(40_000) } as never)
  await expectBar($, '🟠 cache reset (chat compacted) · next message ≈ $0.24 (40× more) · 30K / 1M · Small chat, fine to keep going')
})

test('older chat: filled in on resume, no reply needed', async ($, on) => {
  engine(on)
  await start($)
  await $.classic.SessionStart({ source: 'resume', session_id: 'chat-1', seconds_since_last_response: 7200, context_tokens: 290_000, prompt_cache_likely_expired: true, model: 'claude-opus-5-5' } as never)
  await expectBar($, '🔴 cache expired · next message ≈ $2.32 (40× more) · 290K / 1M · 🔄 Try /cmaxx-handoff to save 232K tokens | $2.21')
})

test('/clear goes back to the waiting line', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 50_000, write: 0 })
  await $.session.end({ reason: 'clear', sessionId: 'chat-1', resume: {} } as never)
  await expectBar($, WAITING)
})

test('app restart: the saved record brings the bar back before any reply', async ($, on) => {
  const saved = { at: T0 - 10 * MIN, prefix: 50_000, out: 0, model: 'claude-opus-5-5', read: 50_000, write: 0, ttlMin: 60, miss5: 0, warned: false, window: 1_000_000 }
  engine(on, { store: { 'cmx:chat-1': saved } })
  await start($)
  await expectBar($, '🟢 50 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('a malformed record from an older version is ignored, never NaN', async ($, on) => {
  engine(on, { store: { 'cmx:chat-1': { at: 'x' } }, state: { at: 1, prefix: 5 } })
  await start($)
  const out = await bars($)
  expect(out.some(t => t?.includes('NaN'))).toBe(false)
})

test('the close button hides the bar on every surface; /cmaxx brings it back', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 50_000, write: 0 })
  const ui = await $.ui.mount({ ...BAR, surface: 'desktop' })
  await ui.press({ key: 'close' })
  await ui.unmount()
  await expectBar($, HIDDEN)
  await $.command.run({ command: 'cmaxx', args: '' } as never)
  expect((await bars($))[0]?.startsWith('🟢')).toBe(true)
})

// VS Code's own case: its ✕ is pressed inside the extension's webview, a different
// drawing from desktop's, so press it there too.
test('vscode: the ✕ sits beside the text, and pressing it hides the bar everywhere', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 50_000, write: 0 })
  const ui = await $.ui.mount({ ...BAR, surface: 'vscode' })
  expect((await ui.find({ type: 'Button', key: 'close' }))?.text).toBe('✕')
  await ui.press({ key: 'close' })
  await ui.unmount()
  await expectBar($, HIDDEN)
  await $.command.run({ command: 'cmaxx', args: '' } as never)
  expect((await bars($)).every(t => t?.startsWith('🟢'))).toBe(true)
})

// VS Code's webview wrapped the ✕ below the text (seen 2026-11-16). The kit can't measure
// layout, so pin the props that keep it top-right.
test('vscode: the ✕ row never wraps and the text column can shrink', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 50_000, write: 0 })
  const ui = await $.ui.mount({ ...BAR, surface: 'vscode' })
  expect((await ui.find({ type: 'Box', key: 'row' }))?.props).toMatchObject({ flexDirection: 'row', flexWrap: 'nowrap' })
  expect((await ui.find({ type: 'Box', key: 'text' }))?.props).toMatchObject({ flexShrink: 1, minWidth: 0 })
  await ui.unmount()
})

test('a closed bar also stops the pop-up', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 228_000, write: 0 })
  const ui = await $.ui.mount({ ...BAR, surface: 'desktop' })
  await ui.press({ key: 'close' })
  await ui.unmount()
  await w.clock.advance(80 * MIN)
  expect(w.toasts.length).toBe(0)
})

// --- /cmaxx-handoff -------------------------------------------------------------
// Everything outside the plugin is a stand-in: the chat, Haiku, the disk, /clear, the box.
const BRIEF = '## Handoff Confidence\nHigh: all there.\n\n## Last Request from the User\nship it\nStatus: Answered\n\n## Next Steps\n1. Release.'

function handoffEngine(on: On, opts: { reply?: string | null; clearRefusals?: number; fillRefused?: boolean; noticeRefused?: boolean; surface?: (typeof SURFACES)[number] } = {}) {
  const w = engine(on)
  const calls = { model: [] as { model: string; system?: unknown; prompt: unknown; effort?: string; maxTokens?: number }[], writes: [] as { path: string; text: string }[], clears: 0, fills: [] as string[], copies: [] as string[], notices: [] as string[] }
  // the kit has no disk: the skill file's three parts, with real section names
  on('fs.read', (_, e) => {
    if (!String((e as { path: string }).path).endsWith('/hooks/handoff-skill.md')) throw new Error('unexpected read')
    return { value: '# Final brief\nRole.\n\n## Handoff Confidence\nx\n\n## What Was Tried and Why It Failed\nx\n\n# Closing line\nWrite it now.\n\n# Next-chat instructions\n## Instructions\nGo.' }
  })
  on('session.messages', () => ({ value: [
    { role: 'user', text: 'ship it', toolUses: [] },
    { role: 'assistant', text: 'done', toolUses: [{ tool_use_id: 'a', tool: 'Edit', input: { file_path: 'hooks/register.tsx' }, text: 'ok' }] },
  ] }))
  on('session.cwd', () => ({ value: '/Users/x/proj' }))
  on('session.surfaces', () => ({ value: [opts.surface ?? 'terminal'] }) as never)
  on('session.append', (_, e, next) => {
    const m = (e as unknown as { message: { type: string; content: { text: string }[] } }).message
    if (opts.noticeRefused) return { deny: 'no' } as never
    if (m.type === 'system') calls.notices.push(m.content[0]!.text)
    return next(e)
  })
  on('ui.log', () => ({ value: undefined }))
  on('model.complete', (_, e) => {
    calls.model.push(e as never)
    return { value: opts.reply === null
      ? { isAnswered: false, reason: 'api-error', text: '' }
      : { isAnswered: true, text: opts.reply ?? BRIEF, usage: { input_tokens: 40_000, output_tokens: 1_500, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 } } } as never
  })
  on('fs.write', (_, e) => { calls.writes.push(e as never); return { value: undefined } })
  on('command.run', { command: 'clear' }, () => { calls.clears++; if (calls.clears <= (opts.clearRefusals ?? 0)) throw new Error("busy"); return { text: '' } })
  on('prompt.fill', (_, e) => { calls.fills.push((e as { text: string }).text); return { isFilled: !opts.fillRefused } as never })
  on('ui.copy', (_, e) => { calls.copies.push((e as { text: string }).text); return { value: { isCopied: true } } })
  return { ...w, calls }
}

async function handoff($: Dollar) {
  return $.command.run({ command: 'cmaxx-handoff', args: '' } as never)
}

test('handoff: Haiku writes it from the chat read locally; the main model never runs', async ($, on) => {
  const h = handoffEngine(on)
  await start($, 'terminal')
  const r = await handoff($)
  expect(h.steps.n).toBe(0)
  expect(h.calls.model.length).toBe(1)
  expect(h.calls.model[0]).toMatchObject({ model: 'haiku', effort: 'high', maxTokens: 64_000 }) // no cap yet: the API's ceiling
  expect(h.calls.model[0]).toMatchObject({ timeoutMs: 180_000 }) // your call: 3 minutes, then facts only
  expect(String(h.calls.model[0]!.system)).toContain('## What Was Tried and Why It Failed') // the real skill file
  expect(String(h.calls.model[0]!.prompt)).toContain('# Extracted Facts')
  expect(h.calls.writes.length).toBe(2) // the brief, then the folder's .gitignore
  expect(h.calls.writes[0]!.path).toMatch(/\/\.claude\/handoffs\/\d{4}-\d\d-\d\d-\d{6}-chat-1\.md$/)
  expect(h.calls.writes[0]!.text).toContain('## Handoff Confidence')
  expect(h.calls.writes[0]!.text).toContain('- hooks/register.tsx')
  // the line is a notice kept in the old chat, not command output that goes unseen after the clear
  expect(r.text).toBe(undefined)
  expect(h.calls.notices.length).toBe(1)
  expect(h.calls.notices[0]).toMatch(/^Handoff saved to \.claude\/handoffs\/.+\. This command never resent the chat to the main model: no cache read, no rebuild\.$/)
})

test('handoff: it clears to a fresh chat and puts the line in its box, unsent', async ($, on) => {
  const h = handoffEngine(on)
  await start($, 'terminal')
  await handoff($)
  await h.clock.advance(1) // /clear starts on a timer once the command has returned
  await w8()
  expect(h.calls.copies).toEqual([])
  expect(h.calls.clears).toBe(1)
  await $.classic.SessionStart({ source: 'clear', session_id: 'chat-2', model: 'claude-opus-5-5' } as never)
  await w8()
  expect(h.calls.fills.length).toBe(1)
  expect(h.calls.fills[0]).toMatch(/^Read \.claude\/handoffs\/.+-chat-1\.md and continue from where we left off\.$/)
  await expectBar($, WAITING)
})

// Seen live at 23:31 in VS Code: /clear refused right after the command, the session still busy.
test('handoff: /clear refused at first is retried, and the fresh chat still opens', async ($, on) => {
  const h = handoffEngine(on, { clearRefusals: 2 })
  await start($, 'terminal')
  await handoff($)
  await settle(h)
  expect(h.calls.clears).toBe(3)
  expect(h.calls.copies).toEqual([])
  await $.classic.SessionStart({ source: 'clear', session_id: 'chat-2', model: 'claude-opus-5-5' } as never)
  await w8()
  expect(h.calls.fills.length).toBe(1)
})

test('handoff: /clear refused every time → the line goes to the clipboard and nothing is cleared', async ($, on) => {
  const h = handoffEngine(on, { clearRefusals: 99 })
  await start($, 'terminal')
  await handoff($)
  await settle(h)
  expect(h.calls.clears).toBe(4)
  expect(h.calls.copies.length).toBe(1)
  expect(h.calls.fills.length).toBe(0)
})

// runs out the clear retries (0, 0.5, 1.5, 3 s) on the test clock
async function settle(h: { clock: { advance: (ms: number) => Promise<unknown> } }) {
  for (const ms of [1, 500, 1_500, 3_000, 1]) {
    await h.clock.advance(ms)
    await w8()
  }
}

test('handoff: Haiku fails → a facts-only file is still written', async ($, on) => {
  const h = handoffEngine(on, { reply: null })
  await start($, 'terminal')
  const r = await handoff($)
  expect(h.calls.writes[0]!.text).toContain('Haiku did not return a usable brief')
  expect(h.calls.writes[0]!.text).toContain('## Last Real User Message (verbatim)\nship it')
  expect(h.calls.notices[0]).toContain('facts only')
})

test('handoff: a reply with no sections is not used as a brief', async ($, on) => {
  const h = handoffEngine(on, { reply: 'Sure! Here is a summary of the chat.' })
  await start($, 'terminal')
  const r = await handoff($)
  expect(h.calls.writes[0]!.text.includes('Sure!')).toBe(false)
  // the reason, with Haiku's counts: out at the cap would mean it ran out of room
  expect(h.calls.notices[0]).toContain("(facts only: Haiku's reply had none of the sections, in 40000 / out 1500 of 64000 tokens)")
  expect(h.calls.notices[0]).toContain('This command never resent the chat to the main model: no cache read, no rebuild.') // no reply yet, so no bar record
})

// lets fire-and-forget promises (fill, copy) settle
// the kit runs on a real event loop: let queued work settle
const w8 = () => new Promise(r => (globalThis as unknown as { setTimeout: (f: (v: unknown) => void, ms: number) => void }).setTimeout(r, 20))

test('handoff: the box refuses the line → it goes to the clipboard', async ($, on) => {
  const h = handoffEngine(on, { fillRefused: true })
  await start($, 'terminal')
  await handoff($)
  await h.clock.advance(1)
  await w8()
  await $.classic.SessionStart({ source: 'clear', session_id: 'chat-2', model: 'claude-opus-5-5' } as never)
  await w8()
  expect(h.calls.fills.length).toBe(1)
  expect(h.calls.copies).toEqual(h.calls.fills)
})

test('handoff: on an expired cache the old chat sees the approx saving, net of Haiku', async ($, on) => {
  const h = handoffEngine(on)
  await start($, 'terminal')
  await h.reply($, { read: 228_000, write: 0 })
  await h.clock.advance(70 * MIN)
  const r = await handoff($)
  // rebuild 228K on Opus 1h = $1.824; Haiku 40K in + 1.5K out = $0.00475; tokens 228,000 - 41,500
  expect(h.calls.notices[0]!.endsWith('You saved approx 174K tokens and $1.72.')).toBe(true)
})

test('handoff: a refused notice falls back to the command output, so the line is never lost', async ($, on) => {
  const h = handoffEngine(on, { noticeRefused: true })
  await start($, 'terminal')
  const r = await handoff($)
  expect(r.text).toMatch(/^Handoff saved to /)
})

// Seen live at 00:12 on desktop: /clear reused the tab (old chat out of view) and the box stayed empty (F52).
test('handoff on desktop: no /clear; the command output and a pop-up carry the line, copied', async ($, on) => {
  const h = handoffEngine(on, { surface: 'desktop' })
  await start($, 'desktop')
  const r = await handoff($)
  await settle(h)
  expect(h.calls.clears).toBe(0)
  expect(h.calls.fills.length).toBe(0)
  expect(h.calls.copies.length).toBe(1)
  expect(h.calls.copies[0]).toMatch(/^Read \.claude\/handoffs\/.+-chat-1\.md and continue from where we left off\.$/)
  expect(h.calls.notices).toEqual([]) // the desktop app doesn't draw a notice row (F53)
  expect(r.text).toMatch(/To continue, start a new chat and paste \(auto-copied\): Read \.claude\/handoffs\/.+-chat-1\.md and continue from where we left off\.$/)
})

// VS Code clears and fills like the terminal; its notice row is kept but not drawn (F70, F71).
test('handoff in VS Code: clears to a fresh chat with the line in its box, unsent', async ($, on) => {
  const h = handoffEngine(on, { surface: 'vscode' })
  await start($, 'vscode')
  const r = await handoff($)
  await h.clock.advance(1)
  await w8()
  expect(r.text).toBe(undefined)
  expect(h.calls.clears).toBe(1)
  await $.classic.SessionStart({ source: 'clear', session_id: 'chat-2', model: 'claude-opus-5-5' } as never)
  await w8()
  expect(h.calls.copies).toEqual([])
  expect(h.calls.fills[0]).toMatch(/^Read \.claude\/handoffs\/.+-chat-1\.md and continue from where we left off\.$/)
})

// Only the terminal clears: the line goes in the fresh chat's box, the notice stays in the old chat.
test('handoff in the terminal: clears to a fresh chat, line in its box, notice kept in the old chat', async ($, on) => {
  const h = handoffEngine(on, { surface: 'terminal' })
  await start($, 'terminal')
  const r = await handoff($)
  await h.clock.advance(1)
  await w8()
  expect(r.text).toBe(undefined)
  expect(h.calls.notices.length).toBe(1)
  expect(h.calls.clears).toBe(1)
  await $.classic.SessionStart({ source: 'clear', session_id: 'chat-2', model: 'claude-opus-5-5' } as never)
  await w8()
  expect(h.calls.copies).toEqual([])
  expect(h.calls.fills[0]).toMatch(/^Read \.claude\/handoffs\/.+-chat-1\.md and continue from where we left off\.$/)
})

// Sending into an expired big chat warns once and never blocks (RULES); checked on the terminal.
test('send warning in the terminal: a red chat warns, the message still goes through unchanged', async ($, on) => {
  const w = engine(on)
  on('prompt.submit', (_, e) => ({ text: (e as { text: string }).text }) as never)
  await start($, 'terminal')
  await $.classic.SessionStart({ source: 'resume', session_id: 'chat-1', seconds_since_last_response: 7200, context_tokens: 290_000, prompt_cache_likely_expired: true, model: 'claude-opus-5-5' } as never)
  const r = await $.prompt.submit({ text: 'carry on', wait: false, origin: { kind: 'composer' } } as never)
  expect((r as { text: string; drop?: unknown }).text).toBe('carry on')
  expect((r as { drop?: unknown }).drop).toBe(undefined)
  expect(w.toasts.filter(t => t.includes('Heads-up: ')).length).toBe(1)
  // the engine's own turns (claude -p) never warn
  await $.prompt.submit({ text: 'x', wait: false, origin: { kind: 'sdk' } } as never)
  expect(w.toasts.filter(t => t.includes('Heads-up: ')).length).toBe(1)
})

// --- review fixes (2026-11-17) ----------------------------------------------------
test('a broken store never costs the commands, the bar or the pop-up', async ($, on) => {
  const w = engine(on, { brokenStore: true })
  await start($)
  expect(w.commands).toEqual(['cmaxx', 'cmaxx-handoff', 'cmaxx-update', 'cmaxx-stats'])
  await w.reply($, { read: 290_000, write: 0 })
  await w.clock.advance(MIN)
  await expectBar($, '🟢 59 min left · next message ≈ $0.06 · 290K / 1M · ✅ Keep going')
  await w.clock.advance(61 * MIN)
  expect(w.toasts.filter(t => t.includes('🔴 cache expired')).length).toBe(1)
})

test('weeks away: an 8-day-old record is pruned (7-day rule), and a resume still fills the bar', async ($, on) => {
  const old = { at: T0 - 8 * 24 * 60 * MIN, prefix: 50_000, out: 0, model: 'claude-opus-5-5', read: 50_000, write: 0, ttlMin: 60, miss5: 0, warned: false, window: 1_000_000 }
  engine(on, { store: { 'cmx:chat-1': old } })
  await start($)
  await expectBar($, WAITING) // pruned: kept, it would show its expired record
  await $.classic.SessionStart({ source: 'resume', session_id: 'chat-1', seconds_since_last_response: 30 * 24 * 3600, context_tokens: 290_000, prompt_cache_likely_expired: true, model: 'claude-opus-5-5' } as never)
  await expectBar($, '🔴 cache expired · next message ≈ $2.32 (40× more) · 290K / 1M · 🔄 Try /cmaxx-handoff to save 232K tokens | $2.21')
})

test('clock set back: a record from the "future" still gives a valid bar', async ($, on) => {
  const saved = { at: T0 + 10 * MIN, prefix: 50_000, out: 0, model: 'claude-opus-5-5', read: 50_000, write: 0, ttlMin: 60, miss5: 0, warned: false, window: 1_000_000 }
  engine(on, { store: { 'cmx:chat-1': saved } })
  await start($)
  const out = await bars($)
  expect(out.some(t => !t || /NaN|-\d/.test(t))).toBe(false)
})

test('handoff: the folder gets a .gitignore once, so briefs never reach git', async ($, on) => {
  const h = handoffEngine(on)
  let exists = false
  on('fs.stat', (_, e) => { if (exists && String((e as { path: string }).path).endsWith('.gitignore')) return { value: { kind: 'file' } } as never; throw new Error('missing') })
  await start($, 'vscode')
  await handoff($)
  expect(h.calls.writes[1]!.path.endsWith('/.claude/handoffs/.gitignore')).toBe(true)
  expect(h.calls.writes[1]!.text).toBe('*\n')
  exists = true
  await handoff($)
  expect(h.calls.writes.filter(w => w.path.endsWith('.gitignore')).length).toBe(1)
})

test('handoff: a /clear more than 30 s later (your own) gets an empty box, not the old line', async ($, on) => {
  const h = handoffEngine(on)
  await start($, 'vscode')
  await handoff($)
  await h.clock.advance(1) // the clear is queued, but its fresh chat never opens (you sent a message first)
  await w8()
  expect(h.calls.clears).toBe(1)
  await h.clock.advance(31_000)
  await w8()
  await $.classic.SessionStart({ source: 'clear', session_id: 'chat-2', model: 'claude-opus-5-5' } as never)
  await w8()
  expect(h.calls.fills).toEqual([])
})

// --- /cmaxx-stats (0.3.0) --------------------------------------------------------
async function stats($: Dollar) {
  return String((await $.command.run({ command: 'cmaxx-stats', args: '' } as never)).text)
}

test('stats: replies, a cold rebuild after expiry, and all chats adding up', async ($, on) => {
  const retired = { since: T0 - 60 * 24 * 60 * MIN, replies: 5, read: 0, write: 0, input: 0, rebuilds: 0, rebuildTokens: 0, rebuildUsd: 0, handoffs: 0, savedTokens: 0, savedUsd: 0, haikuUsd: 0, chats: 1 }
  const w = engine(on, { store: { 'st:retired': retired } }) // chats pruned earlier
  await start($)
  await w.reply($, { read: 0, write: 228_000 }) // first reply: no earlier record, so not a rebuild
  await w.clock.advance(70 * MIN)
  await w.reply($, { read: 0, write: 228_000 }) // after the hour: a rebuild, priced as the 1h write
  await w.clock.advance(5 * MIN)
  await w.reply($, { read: 228_000, write: 0 }) // warm: not a rebuild
  const t = await stats($)
  expect(t).toContain('| Cold rebuilds paid | 1 (228K tokens, $1.82) | 1 (228K tokens, $1.82) |')
  expect(t).toContain('| Replies | 3 | 8 |')
  expect(t).toContain('| Chats | – | 2 |')
  expect(t).toContain('| Cache hit rate | 33% | 33% |')
})

test('stats: a handoff on an expired chat counts the notice\'s saving and Haiku\'s cost', async ($, on) => {
  const h = handoffEngine(on)
  await start($, 'vscode')
  await h.reply($, { read: 228_000, write: 0 })
  await h.clock.advance(70 * MIN)
  await handoff($)
  const t = await stats($)
  expect(t).toContain('| Handoffs | 1 | 1 |')
  // Haiku in the stand-in used 40,000 in / 1,500 out, and the fresh chat's start is 13K:
  // 228K - 41.5K - 13K = 173.5K; $1.824 - $0.00475 - $0.104 = $1.715
  expect(t).toContain('| Tokens saved | 174K | 174K |')
  expect(t).toContain('| Saved by handoffs | $1.72 | $1.72 |')
  expect(h.calls.notices[0]).toContain('You saved approx 174K tokens and $1.72.')
})

test('stats: a broken store still answers /cmaxx-stats, with zeros', async ($, on) => {
  engine(on, { brokenStore: true })
  await start($)
  expect(await stats($)).toContain('| Replies | 0 | 0 |')
})

// --- 0.4.0: stats fill-in, /cmaxx-update -----------------------------------------------
const TRANSCRIPT = [
  JSON.stringify({ type: 'assistant', timestamp: '2026-11-17T10:00:00Z', message: { id: 'a1', model: 'claude-opus-5-5', usage: { input_tokens: 0, cache_read_input_tokens: 0, cache_creation_input_tokens: 228_000, output_tokens: 0 } } }),
  JSON.stringify({ type: 'assistant', timestamp: '2026-11-17T12:00:00Z', message: { id: 'a2', model: 'claude-opus-5-5', usage: { input_tokens: 0, cache_read_input_tokens: 0, cache_creation_input_tokens: 228_000, output_tokens: 0 } } }),
].join('\n')

function onDisk(on: On, size: number) {
  const reads = { n: 0 }
  on('fs.stat', () => ({ value: { kind: 'file', size } }) as never)
  on('fs.read', () => { reads.n++; return { value: TRANSCRIPT } as never })
  return reads
}
const resume = ($: Dollar) => $.classic.SessionStart({ source: 'resume', session_id: 'chat-1', transcript_path: '/t/chat-1.jsonl', model: 'claude-opus-5-5' } as never)

test('stats fill-in: an older chat\'s history is read once from its transcript, then counted live', async ($, on) => {
  const w = engine(on)
  const reads = onDisk(on, 1_000)
  await start($)
  await resume($)
  await resume($) // already filled: not read again
  expect(reads.n).toBe(1)
  expect(await stats($)).toContain('| Cold rebuilds paid | 1 (228K tokens, $1.82) | 1 (228K tokens, $1.82) |')
  await w.reply($, { read: 228_000, write: 0 })
  const t = await stats($)
  expect(t).toContain('| Replies | 3 | 3 |')
  expect(t).toContain('| Chats | – | 1 |')
})

test('stats fill-in: a transcript over 4 MiB is not read; the column says since when it was counted', async ($, on) => {
  const w = engine(on)
  const reads = onDisk(on, 5 * 1024 * 1024)
  await start($)
  await resume($)
  await w.reply($, { read: 228_000, write: 0 })
  expect(reads.n).toBe(0)
  const t = await stats($)
  expect(t).toContain('| | This chat (since 2027-01-15) | All chats |')
  expect(t).toContain('| Replies | 1 | 1 |')
})

function updateEngine(on: On, o: { latest?: string; prices?: unknown; processExit?: number; processOut?: string; offline?: boolean; pricesFail?: boolean; store?: Record<string, unknown> } = {}) {
  const w = engine(on, { store: o.store })
  const calls = { argv: [] as string[][], urls: [] as string[] }
  on('fs.read', (_, e) => {
    if (String((e as { path: string }).path).endsWith('/.claude-plugin/plugin.json')) return { value: JSON.stringify({ name: 'quenching-cache-maxxing', version: '0.4.0' }) } as never
    throw new Error('unexpected read')
  })
  on('http.fetch', (_, e) => {
    const url = (e as { url: string }).url
    calls.urls.push(url)
    if (o.offline || (o.pricesFail && url.endsWith('prices.json'))) throw new Error('ENOTFOUND')
    const body = url.endsWith('plugin.json') ? { version: o.latest ?? '0.4.0' } : (o.prices ?? { sourceDate: '2026-12-02', prices: { 'opus-5-5': [4, 0.2], 'opus-6': [5, 0.5] } })
    return { value: { status: 200, ok: true, headers: {}, text: JSON.stringify(body) } } as never
  })
  on('process.run', (_, e) => {
    calls.argv.push([...(e as { argv: string[] }).argv])
    if (o.processExit === undefined) throw new Error('not available on this surface')
    return { value: { exitCode: o.processExit, stdout: o.processOut ?? '', stderr: '' } } as never
  })
  on('ui.log', () => ({ value: undefined }))
  return { ...w, calls }
}
const runUpdate = async ($: Dollar) => String((await $.command.run({ command: 'cmaxx-update', args: '' } as never)).text)

test('update, same version: only this repo\'s files are read, and a new model is priced at once', async ($, on) => {
  const u = updateEngine(on)
  await start($)
  const t = await runUpdate($)
  expect(t).toBe('cache-maxxing 0.4.0 is the latest version. Prices updated to 2026-12-02: new claude-opus-6.')
  expect(u.calls.argv).toEqual([])
  expect(u.calls.urls).toEqual(['https://raw.githubusercontent.com/holetz/quenching/main/integrations/claude-cache-maxxing/.claude-plugin/plugin.json', 'https://raw.githubusercontent.com/5m0k3/cache-maxxing/main/prices.json'])
  await u.reply($, { read: 50_000, write: 0, model: 'claude-opus-6' })
  await expectBar($, '🟢 60 min left · next message ≈ $0.03 · 50K / 1M · ✅ Keep going')
  expect(await runUpdate($)).toContain('Prices: up to date (2026-12-02).')
})

test('update, newer version: Claude Code\'s updater runs where it may; elsewhere the reply says how', async ($, on) => {
  const u = updateEngine(on, { latest: '0.5.0', processExit: 0 })
  await start($)
  expect(await runUpdate($)).toContain('Updated cache-maxxing 0.4.0 → 0.5.0. Run /reload-plugins')
  expect(u.calls.argv).toEqual([['claude', 'plugin', 'update', 'quenching-cache-maxxing@quenching']])
})

test('update, newer version but the updater is refused: manual steps, and prices still refreshed', async ($, on) => {
  updateEngine(on, { latest: '0.5.0' })
  await start($)
  const t = await runUpdate($)
  expect(t).toContain('Version 0.5.0 is out (you have 0.4.0). To update:')
  expect(t).toContain('Enable auto-update')
  expect(t).toContain('Prices updated to 2026-12-02')
})

test('update: offline or a bad table changes nothing', async ($, on) => {
  updateEngine(on, { offline: true })
  await start($)
  expect(await runUpdate($)).toBe("Couldn't check for a new version: GitHub not reachable (offline?). Prices not checked: GitHub not reachable (offline?). Nothing changed.")
})

test('update: a refused price table leaves the prices as they were', async ($, on) => {
  const u = updateEngine(on, { prices: { sourceDate: '2026-12-02', prices: { 'opus-5-5': [4, 9] } } })
  await start($)
  expect(await runUpdate($)).toContain('Prices not changed: the downloaded table was refused (bad price for opus-5-5).')
  await u.reply($, { read: 50_000, write: 0 })
  await expectBar($, '🟢 60 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('prices saved by an earlier /cmaxx-update are used after a restart', async ($, on) => {
  const w = engine(on, { store: { prices: { sourceDate: '2026-12-02', prices: { 'opus-6': [5, 0.5] } } } })
  await start($)
  await w.reply($, { read: 50_000, write: 0, model: 'claude-opus-6' })
  await expectBar($, '🟢 60 min left · next message ≈ $0.03 · 50K / 1M · ✅ Keep going')
})

// --- final-review fixes ------------------------------------------------------------
test('a session that never gets a reply is not a chat; a non-interactive one is never counted', async ($, on) => {
  const w = engine(on)
  on('fs.stat', () => { throw new Error('ENOENT') }) // a new chat: no transcript yet
  await start($)
  await $.classic.SessionStart({ source: 'startup', session_id: 'chat-1', transcript_path: '/t/chat-1.jsonl', model: 'claude-opus-5-5' } as never)
  expect(await stats($)).toContain('| Chats | – | 0 |')
  await w.reply($, { read: 0, write: 50_000 })
  expect(await stats($)).toContain('| Chats | – | 1 |')
})

test('claude -p and other non-interactive sessions are not counted', async ($, on) => {
  const w = engine(on)
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: false })
  await w.reply($, { read: 0, write: 50_000 })
  expect(await stats($)).toContain('| Replies | 0 | 0 |')
})

test('a fork does not read its transcript (the parent\'s rows): counted from its first reply', async ($, on) => {
  const w = engine(on)
  const reads = onDisk(on, 1_000)
  await start($)
  await $.classic.SessionStart({ source: 'fork', session_id: 'chat-1', transcript_path: '/t/chat-1.jsonl', model: 'claude-opus-5-5' } as never)
  await w.reply($, { read: 228_000, write: 0 })
  expect(reads.n).toBe(0)
  expect(await stats($)).toContain('| Replies | 1 | 1 |')
})

test('after 90 days a chat is retired into the totals; resumed, it is not read or counted again', async ($, on) => {
  const old = { since: T0 - 100 * 24 * 60 * MIN, at: T0 - 100 * 24 * 60 * MIN, replies: 2, read: 0, write: 0, input: 0, rebuilds: 0, rebuildTokens: 0, rebuildUsd: 0, handoffs: 0, savedTokens: 0, savedUsd: 0, isFilled: true }
  engine(on, { store: { 'st:chat-1': old } })
  const reads = onDisk(on, 1_000)
  await start($)
  await w8() // prune runs in the background
  await resume($)
  expect(reads.n).toBe(0)
  const t = await stats($)
  expect(t).toContain('| Replies | 0 | 2 |')
  expect(t).toContain('| Chats | – | 1 |')
})

test('update: a failed price download never hides a finished update', async ($, on) => {
  updateEngine(on, { latest: '0.5.0', processExit: 0, pricesFail: true })
  await start($)
  const t = await runUpdate($)
  expect(t).toContain('Updated cache-maxxing 0.4.0 → 0.5.0. Run /reload-plugins')
  expect(t).toContain('Prices not checked: GitHub not reachable (offline?).')
  expect(t.includes('Nothing changed')).toBe(false)
})

test('a downloaded table dated like the built-in one never overrides it', async ($, on) => {
  const same = { sourceDate: PRICES_DATE, prices: { 'opus-5-5': [9, 0.9] } }
  const u = updateEngine(on, { store: { prices: same }, prices: same })
  await start($)
  await u.reply($, { read: 50_000, write: 0 })
  await expectBar($, '🟢 60 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going') // bundled $4/$0.20, not $9
  expect(await runUpdate($)).toContain(`Prices: up to date (${PRICES_DATE}).`)
})

// --- 0.4.x: GitHub issues #3, #4, #5, #6 -----------------------------------------------
test('API key or usage credits: a reply that wrote the 5m cache counts down 5 minutes (issue #4)', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 0, write: 50_000, ttl: 5 })
  await expectBar($, '🟢 5 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
  await w.clock.advance(2 * MIN)
  await w.reply($, { read: 50_000, write: 0 }) // wrote nothing: keeps the 5 minutes
  await w.clock.advance(6 * MIN)
  await expectBar($, '🟠 cache expired · next message ≈ $0.25 (25× more) · 50K / 1M · Small chat, fine to keep going')
})

test('resume: the exact record beats the session-start estimate of the same reply (issue #4)', async ($, on) => {
  const w = engine(on, { streamMs: 3 * MIN })
  await start($)
  await w.reply($, { read: 45_000, write: 5_000 }) // started at T0, ended 3 min later
  await $.classic.SessionStart({ source: 'resume', session_id: 'chat-1', seconds_since_last_response: 0, context_tokens: 50_000, model: 'claude-opus-5-5' } as never)
  await expectBar($, '🟢 57 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('the 🔴 saving uses the size of your own fresh chats, learned from their first replies (issue #3)', async ($, on) => {
  const w = engine(on, { store: { fresh: [40_000, 44_000] } })
  on('fs.stat', () => { throw new Error('ENOENT') })
  await start($)
  await $.classic.SessionStart({ source: 'startup', session_id: 'chat-1', transcript_path: '/t/chat-1.jsonl', model: 'claude-opus-5-5' } as never)
  await w.reply($, { read: 0, write: 42_000 })
  await w.reply($, { read: 42_000, write: 186_000 })
  await w.clock.advance(70 * MIN)
  // 228K - 45K Haiku estimate - (42K median of 40K, 44K and this chat's 42K + 4K brief) = 137K; two samples would fall back to 13K: 170K
  expect((await bars($))[0]).toContain('🔄 Try /cmaxx-handoff to save 137K tokens')
})

test('stats: a second handoff of the same expired chat counts no second saving (issue #3)', async ($, on) => {
  const h = handoffEngine(on)
  await start($, 'vscode')
  await h.reply($, { read: 228_000, write: 0 })
  await h.clock.advance(70 * MIN)
  await handoff($)
  await handoff($)
  const t = await stats($)
  expect(t).toContain('| Handoffs | 2 | 2 |')
  expect(t).toContain('| Tokens saved | 174K | 174K |')
})

test('compact: a 0 from the engine is not a free rebuild (issue #5)', async ($, on) => {
  const w = engine(on, { contextTokens: 0 })
  await start($)
  await w.reply($, { read: 228_000, write: 0 })
  await $.classic.PostCompact({ trigger: 'manual', compact_summary: 'x'.repeat(40_000) } as never)
  await expectBar($, '🟠 cache reset (chat compacted) · next message ≈ $0.24 (40× more) · 30K / 1M · Small chat, fine to keep going')
})

test('stats: a warm reply that read under half the chat paid for a rebuild with no event (issue #5)', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 228_000, write: 0 })
  await w.clock.advance(5 * MIN)
  await w.reply($, { read: 0, write: 228_000 }) // effort or tools changed, old images cleared: the cache was dropped
  expect(await stats($)).toContain('| Cold rebuilds paid | 1 (228K tokens, $1.82) |')
})

test('update: an older download never replaces newer prices saved earlier (issue #6)', async ($, on) => {
  const newer = { sourceDate: '2026-12-05', prices: { 'opus-5-5': [4, 0.2], 'opus-6': [8, 0.8] } } // the download says [5, 0.5]
  const u = updateEngine(on, { store: { prices: newer } }) // the download is dated 2026-12-02
  await start($)
  expect(await runUpdate($)).toContain('Prices: up to date (2026-12-05).')
  await u.reply($, { read: 50_000, write: 0, model: 'claude-opus-6' })
  await expectBar($, '🟢 60 min left · next message ≈ $0.04 · 50K / 1M · ✅ Keep going')
})

test('update: when Claude Code says it is already at the latest, the reply never claims "Updated" (F73)', async ($, on) => {
  updateEngine(on, { latest: '0.5.0', processExit: 0, processOut: '✔ cache-maxxing is already at the latest version (0.4.0).' })
  await start($)
  const t = await runUpdate($)
  expect(t.includes('Updated')).toBe(false)
  expect(t).toContain('claude plugin marketplace update quenching')
})
