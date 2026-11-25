// The plugin's only network call: `GET https://api.anthropic.com/api/oauth/usage` with the
// subscription's token. One reply is reused for at least `MIN_INTERVAL_SECONDS`, the same request in
// flight is shared, a 429 pauses, a 401/403 stops until the token changes. The state lives on
// `globalThis` because OpenCode loads one copy of a plugin per directory in the same process, and
// the endpoint rate-limits per token (upstream's lesson). The token never leaves this module: no
// reading, detail or key carries it, only its SHA-256 fingerprint keys the memory.
import { createHash } from "node:crypto"
import { MIN_INTERVAL_SECONDS, parseUsage, type Usage } from "./core/usage.ts"
import { readToken, type Source, type Token } from "./token.ts"

export const USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
const BETA = "oauth-2025-04-20"
const TIMEOUT_MS = 5_000
const MAX_PAUSE_MS = 15 * 60_000

export type Reading =
  | { state: "ok"; usage: Usage; source: Source; readAt: number }
  | { state: "none" }
  | { state: "expired"; source: Source }
  | { state: "rejected"; source: Source }
  | { state: "rateLimited"; retryAt: number }
  | { state: "unavailable"; detail: string }
  | { state: "unexpected" }

type Memory = {
  recent: Map<string, { reading: Reading; at: number }>
  flying: Map<string, Promise<Reading>>
  paused: Map<string, { until: number; failures: number }>
  refused: Set<string>
}

const KEY = Symbol.for("quenching-quota/usage/v1")
const memory = ((globalThis as Record<symbol, unknown>)[KEY] ??= {
  recent: new Map(), flying: new Map(), paused: new Map(), refused: new Set(),
}) as Memory

/** Forget every reading, pause and refusal: the checks start each scenario clean. */
export function forget(): void {
  memory.recent.clear(); memory.flying.clear(); memory.paused.clear(); memory.refused.clear()
}

export type Options = {
  intervalSeconds: number
  now?: number
  /** `Atualizar`: reuse a reply only for the 60 s floor, not the whole interval. */
  force?: boolean
  token?: () => Promise<Token>
  fetcher?: typeof fetch
}

function retryAfterMs(header: string | null, now: number): number {
  if (!header) return 0
  const seconds = Number(header)
  if (Number.isFinite(seconds)) return Math.max(0, seconds * 1_000)
  const at = Date.parse(header)
  return Number.isFinite(at) ? Math.max(0, at - now) : 0
}

async function ask(value: string, source: Source, print: string, intervalMs: number, now: number, fetcher: typeof fetch): Promise<Reading> {
  let reply: Response
  try {
    reply = await fetcher(USAGE_URL, {
      method: "GET",
      headers: { Authorization: `Bearer ${value}`, "anthropic-beta": BETA, Accept: "application/json" },
      redirect: "error",
      signal: AbortSignal.timeout(TIMEOUT_MS),
    })
  } catch (error) {
    // A fixed word, never the error's message: nothing the runtime printed may carry the header.
    return { state: "unavailable", detail: (error as { name?: string })?.name === "TimeoutError" ? "timeout" : "network" }
  }
  if (reply.status === 401 || reply.status === 403) {
    memory.refused.add(print)
    return { state: "rejected", source }
  }
  if (reply.status === 429) {
    const failures = (memory.paused.get(print)?.failures ?? 0) + 1
    const pause = Math.min(MAX_PAUSE_MS, Math.max(retryAfterMs(reply.headers.get("Retry-After"), now), intervalMs * 2 ** (failures - 1)))
    memory.paused.set(print, { until: now + pause, failures })
    return { state: "rateLimited", retryAt: now + pause }
  }
  memory.paused.delete(print)
  if (!reply.ok) return { state: "unavailable", detail: `HTTP ${reply.status}` }
  let body: unknown
  try {
    body = await reply.json()
  } catch {
    return { state: "unexpected" }
  }
  const usage = parseUsage(body)
  return usage ? { state: "ok", usage, source, readAt: now } : { state: "unexpected" }
}

/** The quota now, from memory when a reply is fresh enough; at most one request per token a minute. */
export async function readQuota(options: Options): Promise<Reading> {
  const now = options.now ?? Date.now()
  const token = await (options.token ?? (() => readToken(now)))()
  if (token.state === "none") return token
  if (token.state === "expired") return token
  const print = createHash("sha256").update(token.value).digest("hex")
  if (memory.refused.has(print)) return { state: "rejected", source: token.source }
  const paused = memory.paused.get(print)
  if (paused && paused.until > now) return { state: "rateLimited", retryAt: paused.until }
  const intervalMs = Math.max(MIN_INTERVAL_SECONDS, options.intervalSeconds) * 1_000
  const recent = memory.recent.get(print)
  // A failed reading is retried after the floor; a good one is kept for the interval unless forced.
  const reuseMs = options.force || recent?.reading.state !== "ok" ? MIN_INTERVAL_SECONDS * 1_000 : intervalMs
  if (recent && now >= recent.at && now - recent.at < reuseMs) return recent.reading
  const flying = memory.flying.get(print)
  if (flying) return flying
  const request = ask(token.value, token.source, print, intervalMs, now, options.fetcher ?? fetch).then((reading) => {
    if (reading.state !== "rateLimited" && reading.state !== "rejected") {
      // One token at a time in practice; an old login's reading is dropped, never accumulated.
      for (const key of memory.recent.keys()) if (key !== print) memory.recent.delete(key)
      memory.recent.set(print, { reading, at: now })
    }
    return reading
  }).finally(() => { memory.flying.delete(print) })
  memory.flying.set(print, request)
  return request
}
