// End-to-end tests through the real hooks: a reply, a model switch, a compact, an
// older chat, /clear, an app restart. Each draws the bar on every surface and expects
// the SAME text, so a change made for VS Code or the terminal can't silently break desktop.
import { expect, mock, test } from 'claude-code/testing'

const SURFACES = ['desktop', 'vscode', 'terminal'] as const
const MIN = 60_000
const T0 = 1_800_000_000_000
const HIDDEN = '(engine)' // what Claude Code draws when the plugin shows nothing
const WAITING = '⚪️ quenching-cache starts after you send a message'
const BAR = { plugin: 'quenching-cache', component: 'AbovePrompt', props: { hasSurvey: false, isCollapsed: false, isWorking: false } as never } as const // the kit fills the rest of the band's props

// The plugin redraws once per second, so `clock.advance` costs one redraw per simulated second and a
// long advance is thousands of them: its real run time follows machine load, and the kit's 5 s test
// timeout is hit on a busy host. Tests that only read the bar after a long wait start from a saved
// record of the right age instead; the ones about what a tick does advance only the minutes that matter.
const saved = (age: number, over: Record<string, unknown> = {}) => ({ at: T0 - age, prefix: 228_000, out: 0, model: 'claude-opus-5-5', read: 228_000, write: 0, ttlMin: 60, warned: false, window: 1_000_000, ...over })

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
  on('command.register', (_, e) => { commands.push((e as { name: string }).name); return { value: { command: 'quenching-cache' } } as never })
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

test('countdown starts at the request, not the end of a 1-minute reply', async ($, on) => {
  const w = engine(on, { streamMs: MIN })
  await start($)
  await w.reply($, { read: 50_000, write: 0 })
  await expectBar($, '🟢 59 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('subagent steps do not move the clock', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 50_000, write: 0 })
  await w.clock.advance(5 * MIN)
  await w.reply($, { read: 900_000, write: 0 }, 'agent-7')
  await expectBar($, '🟢 55 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('ticks to yellow, then red, with exactly one pop-up', async ($, on) => {
  const w = engine(on, { store: { 'cmx:chat-1': saved(57 * MIN) } })
  await start($)
  await expectBar($, '🟡 3:00 min left · next message ≈ $0.05, later ≈ $1.82 (40× more) · 228K / 1M · ⏳ Reply soon or try /quenching-cache handoff')
  await w.clock.advance(4 * MIN)
  await expectBar($, '🔴 cache expired · next message ≈ $1.82 (40× more) · 228K / 1M · 🔄 Try /quenching-cache handoff to save 170K tokens | $1.71')
  await w.clock.advance(5 * MIN)
  // the pop-up says exactly what the bar says
  expect(w.toasts.filter(t => t.includes('🔴 cache expired · next message ≈ $1.82 (40× more) · 228K / 1M · 🔄 Try /quenching-cache handoff to save 170K tokens | $1.71')).length).toBe(1)
})

test('model switch re-prices at once; a resume "switch" does not', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 228_000, write: 0 })
  const sw = { requested_model: null, context_tokens: 228_000, prompt_cache_warm: true, cache_ttl: '1h', estimated_cache_write_usd: 1, pricing: 'catalog' }
  await $.classic.PostModelSwitch({ ...sw, from_model: 'claude-sonnet-5-5', to_model: 'claude-opus-5-5', source: 'resume' } as never)
  expect((await bars($))[0]?.startsWith('🟢')).toBe(true)
  await $.classic.PostModelSwitch({ ...sw, from_model: 'claude-opus-5-5', to_model: 'claude-sonnet-5-5', source: 'command' } as never)
  await expectBar($, '🔴 cache reset (model changed) · next message ≈ $0.91 (40× more) · 228K / 1M · 🔄 Try /quenching-cache handoff to save 170K tokens | $0.85')
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
  await w.clock.advance(2 * MIN)
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
  await expectBar($, '🔴 cache expired · next message ≈ $2.32 (40× more) · 290K / 1M · 🔄 Try /quenching-cache handoff to save 232K tokens | $2.21')
})

test('/clear goes back to the waiting line', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 50_000, write: 0 })
  await $.session.end({ reason: 'clear', sessionId: 'chat-1', resume: {} } as never)
  await expectBar($, WAITING)
})

test('app restart: the saved record brings the bar back before any reply', async ($, on) => {
  const saved = { at: T0 - 10 * MIN, prefix: 50_000, out: 0, model: 'claude-opus-5-5', read: 50_000, write: 0, ttlMin: 60, warned: false, window: 1_000_000 }
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

test('the close button hides the bar on every surface; /quenching-cache brings it back', async ($, on) => {
  const w = engine(on)
  await start($)
  await w.reply($, { read: 50_000, write: 0 })
  const ui = await $.ui.mount({ ...BAR, surface: 'desktop' })
  await ui.press({ key: 'close' })
  await ui.unmount()
  await expectBar($, HIDDEN)
  await $.command.run({ command: 'quenching-cache', args: '' } as never)
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
  await $.command.run({ command: 'quenching-cache', args: '' } as never)
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
  const w = engine(on, { store: { 'cmx:chat-1': saved(55 * MIN) } })
  await start($)
  const ui = await $.ui.mount({ ...BAR, surface: 'desktop' })
  await ui.press({ key: 'close' })
  await ui.unmount()
  await w.clock.advance(10 * MIN)
  expect(w.toasts.length).toBe(0)
})


// --- /quenching-cache handoff ---------------------------------------------------------
// Everything outside the plugin is a stand-in: the chat, Haiku, the disk, `cq`, /clear, the box.
const BRIEF = '## Handoff Confidence\nHigh: all there.\n\n## Last Request\nship it\nStatus: Answered\n\n## Next Actions\n1. Release.'
const LINE = 'Read the handoff at quenching:specs/artifacts/7/handoff-2027-01-15-continue-this-chat.md before acting: `.agents/quenching/bin/cq specs artifact read --spec 7 --name handoff-2027-01-15-continue-this-chat.md`. It belongs to spec 7; continue with `/quenching-specs execute 7`.'
const FACTS = { ok: true, branch: 'plan/7-x', spec: 7, filesModified: ['hooks/register.tsx'], commits: ['abc1234 Fix the bar'], lastUserMessage: 'ship it', transcript: '/t/chat-1.jsonl' }
const WROTE = { ok: true, spec: 7, name: 'handoff-2027-01-15-continue-this-chat.md', locator: 'quenching:specs/artifacts/7/handoff-2027-01-15-continue-this-chat.md', sent: true, local: false, prompt: LINE, block: '## Handoff' }

type CqOpts = { noCq?: boolean; writeExit?: number; config?: object; cache?: { chat?: object; project?: object }; harness?: string }
// `cq` as a fixed argv: the deployed binary is found by fs.stat, every call answered by its verb.
function cqEngine(on: On, o: CqOpts = {}) {
  const argv: string[][] = []
  on('session.cwd', () => ({ value: '/Users/x/proj' }))
  on('fs.stat', (_, e) => {
    if (!o.noCq && String((e as { path: string }).path).endsWith('.agents/quenching/bin/cq')) return { value: { kind: 'file' } } as never
    throw new Error('ENOENT')
  })
  on('process.run', (_, e) => {
    const a = [...(e as { argv: string[] }).argv]
    argv.push(a)
    const out = (code: number, body: object) => ({ value: { exitCode: code, stdout: JSON.stringify(body), stderr: '' } }) as never
    if (o.noCq) return { value: { exitCode: 127, stdout: '', stderr: 'not found' } } as never
    const verb = a.slice(1, 4).join(' ')
    if (verb === 'config show --effective') return o.config ? out(0, o.config) : out(2, { ok: false })
    if (verb === 'specs handoff facts') return out(0, FACTS)
    if (verb === 'specs handoff write') return out(o.writeExit ?? 0, (o.writeExit ?? 0) === 0 ? WROTE : { ok: false, code: 'sp-handoff-incomplete', message: 'the handoff lacks ## Next Actions' })
    if (verb === 'components session cache') return a.includes('--session') ? (o.cache?.chat ? out(0, o.cache.chat) : out(2, { ok: false })) : (o.cache?.project ? out(0, o.cache.project) : out(2, { ok: false, code: 'se-no-usage' }))
    throw new Error(`unexpected cq ${a.join(' ')}`)
  })
  return argv
}

function handoffEngine(on: On, opts: { store?: Record<string, unknown>; reply?: string | null; clearRefusals?: number; fillRefused?: boolean; noticeRefused?: boolean; surface?: (typeof SURFACES)[number] } & CqOpts = {}) {
  const w = engine(on, opts.store ? { store: opts.store } : {})
  const argv = cqEngine(on, opts)
  const calls = { argv, model: [] as { model: string; system?: unknown; prompt: unknown; effort?: string; maxTokens?: number; timeoutMs?: number }[], writes: [] as { path: string; text: string }[], clears: 0, fills: [] as string[], copies: [] as string[], notices: [] as string[] }
  on('fs.read', (_, e) => {
    const path = String((e as { path: string }).path)
    if (path.endsWith('/hooks/handoff-brief.md')) return { value: 'Rules for Haiku.' }
    if (path.endsWith('/hooks/handoff-template.md')) return { value: '<!-- generated -->\n# Handoff template\n\n## Last Request\n## Next Actions\n' }
    if (path.endsWith('/AGENTS.md') && opts.harness) return { value: opts.harness }
    throw new Error('ENOENT')
  })
  on('session.messages', () => ({ value: [
    { role: 'user', text: 'ship it', toolUses: [] },
    { role: 'assistant', text: 'done', toolUses: [{ tool_use_id: 'a', tool: 'Edit', input: { file_path: 'hooks/register.tsx' }, text: 'ok' }] },
  ] }))
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
  on('command.run', { command: 'clear' }, () => { calls.clears++; if (calls.clears <= (opts.clearRefusals ?? 0)) throw new Error('busy'); return { text: '' } })
  on('prompt.fill', (_, e) => { calls.fills.push((e as { text: string }).text); return { isFilled: !opts.fillRefused } as never })
  on('ui.copy', (_, e) => { calls.copies.push((e as { text: string }).text); return { value: { isCopied: true } } })
  return { ...w, calls }
}

const run = ($: Dollar, args: string) => $.command.run({ command: 'quenching-cache', args } as never)
const handoff = ($: Dollar, focus = '') => run($, `handoff ${focus}`.trim())
// lets fire-and-forget promises (fill, copy) settle on the kit's real event loop
const w8 = () => new Promise(r => (globalThis as unknown as { setTimeout: (f: (v: unknown) => void, ms: number) => void }).setTimeout(r, 20))
// runs out the clear retries (0, 0.5, 1.5, 3 s) on the test clock
async function settle(h: { clock: { advance: (ms: number) => Promise<unknown> } }) {
  for (const ms of [1, 500, 1_500, 3_000, 1]) {
    await h.clock.advance(ms)
    await w8()
  }
}

test('handoff: Haiku writes it on quenching\'s template from facts cq read; the main model never runs', async ($, on) => {
  const h = handoffEngine(on)
  await start($, 'terminal')
  const r = await handoff($, 'ship the release')
  expect(h.steps.n).toBe(0)
  expect(h.calls.model.length).toBe(1)
  expect(h.calls.model[0]).toMatchObject({ model: 'haiku', effort: 'high', maxTokens: 64_000, timeoutMs: 180_000 })
  expect(String(h.calls.model[0]!.system)).toBe('Rules for Haiku.\n\n# Handoff template\n\n## Last Request\n## Next Actions')
  expect(String(h.calls.model[0]!.prompt)).toContain('- **Spec:** 7')
  const cq = '/Users/x/proj/.agents/quenching/bin/cq'
  expect(h.calls.argv).toContainEqual([cq, 'specs', 'handoff', 'facts', '--session', 'chat-1', '--json'])
  const draft = h.calls.writes[0]!
  expect(draft.path).toMatch(/^\/Users\/x\/proj\/\.quenching\/handoff\/draft-\d+-chat-1\.md$/)
  expect(draft.text.startsWith(BRIEF)).toBe(true)
  expect(draft.text).toContain('### Commits\n- abc1234 Fix the bar')
  expect(h.calls.argv).toContainEqual([cq, 'specs', 'handoff', 'write', '--from', draft.path, '--focus', 'ship the release', '--push', '--json'])
  // the line is a notice kept in the old chat, not command output that goes unseen after the clear
  expect(r.text).toBe(undefined)
  expect(h.calls.notices).toEqual([`Handoff saved to ${WROTE.locator}. This command never resent the chat to the main model: no cache read, no rebuild.`])
})

test('handoff: it clears to a fresh chat and puts cq\'s prompt in its box, unsent', async ($, on) => {
  const h = handoffEngine(on)
  await start($, 'terminal')
  await handoff($)
  await h.clock.advance(1)
  await w8()
  expect(h.calls.clears).toBe(1)
  await $.classic.SessionStart({ source: 'clear', session_id: 'chat-2', model: 'claude-opus-5-5' } as never)
  await w8()
  expect(h.calls.fills).toEqual([LINE])
  await expectBar($, WAITING)
})

test('handoff: /clear refused at first is retried; refused every time, the line goes to the clipboard', async ($, on) => {
  const h = handoffEngine(on, { clearRefusals: 99 })
  await start($, 'terminal')
  await handoff($)
  await settle(h)
  expect(h.calls.clears).toBe(4)
  expect(h.calls.copies).toEqual([LINE])
  expect(h.calls.fills.length).toBe(0)
})

test('handoff: Haiku fails → a facts-only handoff that still passes the verb is stored', async ($, on) => {
  const h = handoffEngine(on, { reply: null })
  await start($, 'terminal')
  await handoff($)
  expect(h.calls.writes[0]!.text).toContain('Low: facts only — Haiku api-error.')
  expect(h.calls.writes[0]!.text).toContain('## Last Request\nship it')
  expect(h.calls.writes[0]!.text).toContain('## Next Actions')
  expect(h.calls.notices[0]).toContain('Facts only: Haiku api-error.')
})

test('handoff: a reply without the required sections is not used as a brief', async ($, on) => {
  const h = handoffEngine(on, { reply: 'Sure! Here is a summary.' })
  await start($, 'terminal')
  await handoff($)
  expect(h.calls.writes[0]!.text.includes('Sure!')).toBe(false)
  expect(h.calls.notices[0]).toContain("Facts only: Haiku's reply had none of the required sections.")
})

test('handoff: a refused write is reported with its code, and nothing is cleared', async ($, on) => {
  const h = handoffEngine(on, { writeExit: 2 })
  await start($, 'terminal')
  const r = await handoff($)
  await settle(h)
  expect(String(r.text)).toContain('no handoff written (sp-handoff-incomplete: the handoff lacks ## Next Actions; draft /Users/x/proj/.quenching/handoff/')
  expect(h.calls.clears).toBe(0)
})

test('handoff without cq: refused before Haiku runs, the chat untouched', async ($, on) => {
  const h = handoffEngine(on, { noCq: true })
  await start($, 'terminal')
  const r = await handoff($)
  expect(String(r.text)).toContain('`cq` was not found')
  expect(h.calls.model.length).toBe(0)
  expect(h.calls.writes.length).toBe(0)
})

test('handoff: on an expired cache the old chat sees the approx saving, net of Haiku', async ($, on) => {
  const h = handoffEngine(on, { store: { 'cmx:chat-1': saved(70 * MIN) } })
  await start($, 'terminal')
  await handoff($)
  // rebuild 228K on Opus 1h = $1.824; Haiku 40K in + 1.5K out = $0.00475; tokens 228,000 - 41,500 - 13,000
  expect(h.calls.notices[0]!.endsWith(' ≈ 174K tokens · $1.72 (Opus).')).toBe(true)
})

test('handoff: a refused notice falls back to the command output, so the line is never lost', async ($, on) => {
  handoffEngine(on, { noticeRefused: true })
  await start($, 'terminal')
  const r = await handoff($)
  expect(String(r.text)).toMatch(/^Handoff saved to /)
})

test('handoff on desktop: no /clear; the command output and a pop-up carry the line, copied', async ($, on) => {
  const h = handoffEngine(on, { surface: 'desktop' })
  await start($, 'desktop')
  const r = await handoff($)
  await settle(h)
  expect(h.calls.clears).toBe(0)
  expect(h.calls.copies).toEqual([LINE])
  expect(h.calls.notices).toEqual([])
  expect(String(r.text).endsWith(`To continue, start a new chat and paste (auto-copied): ${LINE}`)).toBe(true)
})

test('handoff: a /clear more than 30 s later (your own) gets an empty box, not the old line', async ($, on) => {
  const h = handoffEngine(on)
  await start($, 'vscode')
  await handoff($)
  await h.clock.advance(1)
  await w8()
  await h.clock.advance(31_000)
  await w8()
  await $.classic.SessionStart({ source: 'clear', session_id: 'chat-2', model: 'claude-opus-5-5' } as never)
  await w8()
  expect(h.calls.fills).toEqual([])
})

// --- the checkout's own values: shared.cache, the declared language, stats -------------------------

test('the checkout\'s shared.cache block and main budget reach the bar', async ($, on) => {
  const w = engine(on)
  cqEngine(on, { config: { values: [{ key: 'shared.cache.costStyle', value: 'times' }, { key: 'shared.contextBudgets.main', value: 40_000 }] } })
  await start($)
  await w8()
  await w.reply($, { read: 50_000, write: 0 })
  await expectBar($, '🟢 60 min left · next message: normal cost · 50K / 1M · 🔄 Try /quenching-cache handoff or a new chat')
})

test('a pt-BR root harness speaks Portuguese', async ($, on) => {
  const w = engine(on)
  cqEngine(on)
  on('fs.read', (_, e) => (String((e as { path: string }).path).endsWith('/AGENTS.md') ? { value: 'Language: pt-BR — the contract is x' } : (() => { throw new Error('ENOENT') })()))
  await start($)
  await w8()
  await expectBar($, '⚪️ o quenching-cache começa depois da sua primeira mensagem')
  await w.reply($, { read: 50_000, write: 0 })
  await expectBar($, '🟢 60 min restantes · próxima mensagem ≈ $0.01 · 50K / 1M · ✅ Pode seguir')
})

test('stats: this chat and this project, from cq components session cache --usd', async ($, on) => {
  engine(on)
  const row = { model: 'claude-opus-5-5', role: 'main', requests: 4, hitRate: 0.9, cacheWrite: 50_000, usd: 0.5 }
  const argv = cqEngine(on, { cache: { chat: { pricing: { sourceDate: '2026-11-17' }, rows: [row] }, project: { pricing: { sourceDate: '2026-11-17' }, rows: [row] } } })
  await start($)
  const t = String((await run($, 'stats')).text)
  expect(t).toContain('| This chat | claude-opus-5-5 | 4 | 90% | 50K | $0.50 |')
  expect(t).toContain('| This project | claude-opus-5-5 | 4 | 90% | 50K | $0.50 |')
  expect(argv).toContainEqual(['/Users/x/proj/.agents/quenching/bin/cq', 'components', 'session', 'cache', '--json', '--usd', '--harness', 'claude', '--session', 'chat-1'])
})

test('stats: no usage yet, and no cq, each say so', async ($, on) => {
  engine(on)
  cqEngine(on, { noCq: true })
  await start($)
  expect(String((await run($, 'stats')).text)).toContain('stats need `cq`')
  expect(String((await run($, 'nope')).text)).toContain('Use: /quenching-cache')
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
  expect(w.commands).toEqual(['quenching-cache'])
  await w.reply($, { read: 0, write: 290_000, ttl: 5 }) // a 5 min cache: its expiry costs 6 simulated minutes, not 62
  await w.clock.advance(MIN)
  await expectBar($, '🟢 4 min left · next message ≈ $0.06 · 290K / 1M · 🔄 Try /quenching-cache handoff or a new chat') // past shared.contextBudgets.main
  await w.clock.advance(5 * MIN)
  expect(w.toasts.filter(t => t.includes('🔴 cache expired')).length).toBe(1)
})

test('weeks away: an 8-day-old record is pruned (7-day rule), and a resume still fills the bar', async ($, on) => {
  const old = { at: T0 - 8 * 24 * 60 * MIN, prefix: 50_000, out: 0, model: 'claude-opus-5-5', read: 50_000, write: 0, ttlMin: 60, warned: false, window: 1_000_000 }
  engine(on, { store: { 'cmx:chat-1': old } })
  await start($)
  await expectBar($, WAITING) // pruned: kept, it would show its expired record
  await $.classic.SessionStart({ source: 'resume', session_id: 'chat-1', seconds_since_last_response: 30 * 24 * 3600, context_tokens: 290_000, prompt_cache_likely_expired: true, model: 'claude-opus-5-5' } as never)
  await expectBar($, '🔴 cache expired · next message ≈ $2.32 (40× more) · 290K / 1M · 🔄 Try /quenching-cache handoff to save 232K tokens | $2.21')
})

test('clock set back: a record from the "future" still gives a valid bar', async ($, on) => {
  const saved = { at: T0 + 10 * MIN, prefix: 50_000, out: 0, model: 'claude-opus-5-5', read: 50_000, write: 0, ttlMin: 60, warned: false, window: 1_000_000 }
  engine(on, { store: { 'cmx:chat-1': saved } })
  await start($)
  const out = await bars($)
  expect(out.some(t => !t || /NaN|-\d/.test(t))).toBe(false)
})

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
  const w = engine(on, { streamMs: MIN })
  await start($)
  await w.reply($, { read: 45_000, write: 5_000 }) // started at T0, ended 1 min later
  await $.classic.SessionStart({ source: 'resume', session_id: 'chat-1', seconds_since_last_response: 0, context_tokens: 50_000, model: 'claude-opus-5-5' } as never)
  await expectBar($, '🟢 59 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going')
})

test('the 🔴 saving uses the size of your own fresh chats, learned from their first replies (issue #3)', async ($, on) => {
  const w = engine(on, { store: { fresh: [40_000, 44_000] } })
  await start($)
  await $.classic.SessionStart({ source: 'startup', session_id: 'chat-1', transcript_path: '/t/chat-1.jsonl', model: 'claude-opus-5-5' } as never)
  await w.reply($, { read: 0, write: 42_000 })
  await w.reply($, { read: 42_000, write: 186_000, ttl: 5 }) // a 5 min write: expired after 6 min, not 70
  await w.clock.advance(6 * MIN)
  // 228K - 45K Haiku estimate - (42K median of 40K, 44K and this chat's 42K + 4K brief) = 137K; two samples would fall back to 13K: 170K
  expect((await bars($))[0]).toContain('🔄 Try /quenching-cache handoff to save 137K tokens')
})

test('compact: a 0 from the engine is not a free rebuild (issue #5)', async ($, on) => {
  const w = engine(on, { contextTokens: 0 })
  await start($)
  await w.reply($, { read: 228_000, write: 0 })
  await $.classic.PostCompact({ trigger: 'manual', compact_summary: 'x'.repeat(40_000) } as never)
  await expectBar($, '🟠 cache reset (chat compacted) · next message ≈ $0.24 (40× more) · 30K / 1M · Small chat, fine to keep going')
})

