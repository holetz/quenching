import { Plugin } from "@opencode/plugin"
import { readFile } from "node:fs/promises"
import { join } from "node:path"
import { configShow } from "./cq.ts"
import { bandText, DEFAULTS, detailText, langOf, settingsFromConfig, toneOf, WORDS } from "./core/usage.ts"
import type { Lang, Settings } from "./core/usage.ts"
import { readQuota, type Reading } from "./fetch.ts"
import { Quota, type QuotaView } from "./rpc.ts"

type Checkout = { settings: Settings; lang: Lang; at: number }

const CHECKOUT_TTL_MS = 5 * 60_000

function viewOf(reading: Reading, settings: Settings, lang: Lang, hidden: boolean, now: number): QuotaView {
  const words = WORDS[lang]
  const plain = (text: string, tone = ""): QuotaView => ({ text, tone, hidden, title: words.detailTitle, detail: text, lang })
  switch (reading.state) {
    case "ok":
      return {
        text: bandText(reading.usage, now, lang),
        tone: toneOf(reading.usage, settings),
        hidden,
        title: words.detailTitle,
        detail: detailText(reading.usage, now, settings, lang, reading.source, reading.readAt),
        lang,
      }
    case "none": return plain(words.noToken)
    case "expired": return plain(words.expired, "danger")
    case "rejected": return plain(words.rejected, "danger")
    case "rateLimited": return plain(words.rateLimited(Math.max(1, Math.ceil((reading.retryAt - now) / 1_000))), "warning")
    case "unavailable": return plain(words.unavailable(reading.detail))
    case "unexpected": return plain(words.unexpected)
  }
}

export default Plugin.define({
  id: "quenching-quota",
  async setup(ctx) {
    // The quota is the account's, not a session's: one band for every window, hidden or shown together.
    let hidden = false
    const checkouts = new Map<string, Checkout>()
    const loading = new Map<string, Promise<Checkout>>()

    /** The checkout's language and `shared.quota`, read once in a while; the first answer never waits on `cq`. */
    async function checkoutOf(directory: string): Promise<Checkout> {
      const hit = checkouts.get(directory)
      if (hit && Date.now() - hit.at < CHECKOUT_TTL_MS) return hit
      const fallback: Checkout = hit ?? { settings: DEFAULTS, lang: "en", at: Date.now() }
      let work = loading.get(directory)
      if (!work) {
        work = (async () => {
          const harness = await readFile(join(directory, "AGENTS.md"), "utf8").catch(() => readFile(join(directory, "CLAUDE.md"), "utf8")).catch(() => undefined)
          const shown = await configShow(directory).catch(() => undefined)
          const fresh: Checkout = { settings: shown ? settingsFromConfig(shown) : fallback.settings, lang: langOf(harness), at: Date.now() }
          checkouts.set(directory, fresh)
          return fresh
        })().finally(() => { loading.delete(directory) })
        loading.set(directory, work)
      }
      return hit ?? Promise.race([work, new Promise<Checkout>((done) => setTimeout(() => done(fallback), 1_500).unref?.())])
    }

    async function show(directory: string, force: boolean): Promise<QuotaView> {
      const { settings, lang } = await checkoutOf(directory)
      const reading = await readQuota({ intervalSeconds: settings.intervalSeconds, force })
      return viewOf(reading, settings, lang, hidden, Date.now())
    }

    const rpc = await ctx.rpc.register(Quota, {
      state: async (input) => show((input as { directory: string }).directory, false),
      refresh: async (input) => show((input as { directory: string }).directory, true),
      toggle: async (input) => {
        hidden = !hidden
        void Promise.resolve(rpc.events.emit("changed", {})).catch(() => undefined)
        return show((input as { directory: string }).directory, false)
      },
    })
  },
})
