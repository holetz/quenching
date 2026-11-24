// The band's state machine, with no OpenCode import so it runs under plain Node in the checks:
// a step's usage becomes a `Rec`, a compaction or a model switch resets it, and `view` turns it
// into the text and tone the pill draws. Every decision is the shared core's (`./core`).
import type { Rec } from './core/types.ts'
import type { Words } from './core/i18n.ts'
import { costs, decide, money, priceOf, tokens, ttlFromUsage } from './core/logic.ts'
import type { PriceSource, Settings, Light } from './core/logic.ts'

export type ModelRef = { id: string; providerID: string }
export type Usage = { input: number; output: number; cache: { read: number; write: number } }
export type Tone = 'success' | 'warning' | 'danger'
export type View = { light: Light | 'none'; text: string; tone?: Tone; shouldPopup: boolean; implicit: boolean }

/** 'anthropic/claude-opus-4.5' → 'anthropic/claude-opus-4-5': the table's spelling. */
export const normModel = (id: string) => id.toLowerCase().replace(/(\d)\.(\d)/g, '$1-$2')

/**
 * Whether the provider marks cache breakpoints (and so has a lifetime to count). Claude routes do;
 * OpenAI, Gemini and gateways that cache on their own do not. A model whose family the table or the
 * id does not name as Claude is treated as implicit: a countdown that is not true is worse than none.
 */
export function explicitCache(model: ModelRef | undefined): boolean {
  return model ? /claude/i.test(model.id) : true
}

// `native` carries the provider's own usage; Anthropic splits the write into 5m and 1h.
export function ephemeralOf(native: unknown): { ephemeral_5m_input_tokens?: number; ephemeral_1h_input_tokens?: number } {
  const out: { ephemeral_5m_input_tokens?: number; ephemeral_1h_input_tokens?: number } = {}
  const walk = (v: unknown, depth: number) => {
    if (!v || typeof v !== 'object' || depth > 4) return
    for (const [k, x] of Object.entries(v as Record<string, unknown>)) {
      if ((k === 'ephemeral_5m_input_tokens' || k === 'ephemeral_1h_input_tokens') && typeof x === 'number') out[k] = (out[k] ?? 0) + x
      else walk(x, depth + 1)
    }
  }
  walk(native, 0)
  return out
}

/** The record a finished step leaves: the next request re-sends everything this one saw. */
export function applyStep(prev: Rec | null, step: { tokens: Usage; native?: unknown; at: number; model: string; window?: number }, s: Settings): Rec {
  const prefix = step.tokens.input + step.tokens.cache.read + step.tokens.cache.write
  return {
    at: step.at,
    prefix,
    out: step.tokens.output,
    model: step.model,
    read: step.tokens.cache.read,
    write: step.tokens.cache.write,
    ttlMin: ttlFromUsage(s.ttlMinutes, ephemeralOf(step.native), prev?.ttlMin),
    warned: false,
    window: step.window ?? prev?.window,
  }
}

/** The cache is gone before its time: a compaction rewrites the prefix, a model switch is a new cache. */
export const reset = (rec: Rec, by: 'model' | 'compact'): Rec => ({ ...rec, resetBy: by, warned: false })

/** A reply opened the new cache: whatever had reset it is over. */
export const clearReset = (rec: Rec): Rec => {
  const { resetBy: _gone, ...rest } = rec
  return rest
}

const toneOf = (l: Light): Tone => (l === 'green' ? 'success' : l === 'red' ? 'danger' : 'warning')

/** Size and next-message cost only: nothing to count down on a provider that caches on its own. */
function reduced(rec: Rec, w: Words, price: PriceSource, s: Settings): string {
  const c = costs(rec, price)
  const ctx = rec.window ? `${tokens(rec.prefix)} / ${tokens(rec.window)}` : tokens(rec.prefix)
  const next = c && s.costStyle === 'dollars' ? ` · ${w.next(money(c.warm))}` : ''
  return `ℹ️ ${ctx}${next}`
}

export function view(rec: Rec | null, now: number, s: Settings, w: Words, price: PriceSource = priceOf, implicit = false): View {
  if (!rec) return { light: 'none', text: w.waiting, shouldPopup: false, implicit }
  if (implicit) return { light: 'green', text: reduced(rec, w, price, s), tone: 'success', shouldPopup: false, implicit }
  const v = decide(rec, now, s, w, price)
  return { light: v.light, text: v.text, tone: toneOf(v.light), shouldPopup: v.shouldPopup, implicit }
}

/** Milliseconds until the cache runs out; null when there is nothing to time. */
export const expiresIn = (rec: Rec | null, now: number): number | null =>
  rec ? Math.max(0, rec.at + rec.ttlMin * 60_000 - now) : null
