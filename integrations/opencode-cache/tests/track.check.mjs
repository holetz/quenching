/**
 * The band's state machine, with no OpenCode: usage → record → verdict.
 *
 *   node --experimental-strip-types integrations/opencode-cache/tests/track.check.mjs
 */
import { DEFAULTS, hostPrice, priceOf } from "../src/core/logic.ts"
import { WORDS } from "../src/core/i18n.ts"
import { applyStep, clearReset, ephemeralOf, expiresIn, explicitCache, normModel, reset, view } from "../src/track.ts"

let failed = 0
const ok = (condition, message) => {
  if (!condition) {
    console.error(`FALHOU: ${message}`)
    failed += 1
  }
}
const W = WORDS.en
const MIN = 60_000
const usage = (input, read, write, output = 500) => ({ input, output, cache: { read, write } })
const model = "claude-opus-5-5"

// the prefix the next request re-sends is everything this one saw
const first = applyStep(null, { tokens: usage(100, 200_000, 8_000), at: 0, model, window: 1_000_000 }, DEFAULTS)
ok(first.prefix === 208_100, "prefix = input + cache read + cache write")
ok(first.out === 500 && first.read === 200_000 && first.write === 8_000, "out, read and write are carried")
ok(first.ttlMin === 60, "no native split and ttl auto: the 1h default")

// the TTL is learned per write from `native`
ok(ephemeralOf({ usage: { cache_creation: { ephemeral_5m_input_tokens: 7, ephemeral_1h_input_tokens: 0 } } }).ephemeral_5m_input_tokens === 7, "native is read at any depth")
const five = applyStep(first, { tokens: usage(100, 1, 8_000), native: { usage: { cache_creation: { ephemeral_5m_input_tokens: 8_000, ephemeral_1h_input_tokens: 0 } } }, at: 0, model }, DEFAULTS)
ok(five.ttlMin === 5, "a 5m write sets the 5-minute lifetime")
const keep = applyStep(five, { tokens: usage(100, 9_000, 0), at: 0, model }, DEFAULTS)
ok(keep.ttlMin === 5, "a reply that wrote nothing keeps the previous lifetime")
ok(applyStep(null, { tokens: usage(1, 1, 1), at: 0, model }, { ...DEFAULTS, ttlMinutes: "5" }).ttlMin === 5, "shared.cache.ttlMinutes forces it")

// the verdict, by time
ok(view(null, 0, DEFAULTS, W).light === "none", "no record yet: the waiting line")
ok(view(first, 10 * MIN, DEFAULTS, W).light === "green", "warm: green")
ok(view(first, 50 * MIN, DEFAULTS, W).light === "yellow", "under warnMinutes on the 1h cache: yellow")
const gone = view(first, 61 * MIN, DEFAULTS, W)
ok(gone.light === "red" && gone.tone === "danger" && gone.shouldPopup, "expired and big: red, danger, one pop-up")
ok(expiresIn(first, 59 * MIN) === 1 * MIN && expiresIn(null, 0) === null, "expiresIn counts down to the lifetime")

// a compaction or a model switch ends the cache early, until the next reply
const compacted = reset(first, "compact")
ok(view(compacted, 1 * MIN, DEFAULTS, W).light !== "green", "a compaction is not warm")
ok(clearReset(compacted).resetBy === undefined, "the next reply clears the reset")

// implicit cache: reduced band, no countdown, no light that can expire
ok(explicitCache({ id: "claude-opus-5-5", providerID: "anthropic" }) && !explicitCache({ id: "gpt-5", providerID: "openai" }), "only Claude routes have breakpoints")
const reduced = view(first, 500 * MIN, DEFAULTS, W, priceOf, true)
ok(reduced.implicit && reduced.light === "green" && !reduced.shouldPopup && !/min|left|expired/i.test(reduced.text), "implicit: size and cost, never expired")
ok(reduced.text.startsWith("ℹ️"), "implicit: the reduced mark")

// a model the table does not know is priced by the host
const odd = { ...first, model: "gpt-x" }
ok(view(odd, 1 * MIN, DEFAULTS, W).text.includes("$") === false, "no price: no dollars")
ok(view(odd, 1 * MIN, DEFAULTS, W, hostPrice([{ input: 3, cacheRead: 0.3, cacheWrite: 3.75 }])).text.includes("$"), "host price: dollars")
ok(normModel("anthropic/claude-opus-4.5") === "anthropic/claude-opus-4-5", "dots between digits become hyphens")

if (failed > 0) process.exit(1)
console.log("track: ok")
