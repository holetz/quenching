// The pure half of quenching-quota: the usage reply's parser, the settings read and the band's words.
// The parser is cut from slkiser/opencode-quota (src/lib/anthropic.ts: `parseQuotaWindow`,
// `readWindow`, `findUsageWindows`), MIT — see NOTICE.md. Nothing here reads a file, opens a
// process or talks to the network.

/** One usage window: `used` in percent (0–100), `resetsAt` in epoch ms when the reply carried it. */
export type Window = { used: number; resetsAt?: number }

/**
 * The windows the band shows. `null` is a limit the plan does not have (Ultra has no 5-hour,
 * Enterprise no weekly); `sonnet` and `opus` are the per-model weeks, absent when not sent.
 */
export type Usage = { fiveHour: Window | null; sevenDay: Window | null; sonnet: Window | null; opus: Window | null }

export type Settings = { warnPercent: number; dangerPercent: number; intervalSeconds: number; showSonnet: boolean }

/** The same numbers as `quenching/assets/bin/quenching/session/quotabar.py`, for a session without `cq`. */
export const DEFAULTS: Settings = { warnPercent: 70, dangerPercent: 90, intervalSeconds: 300, showSonnet: true }

/** The usage endpoint is asked at most once a minute, whatever the configuration says. */
export const MIN_INTERVAL_SECONDS = 60

export type Tone = "success" | "warning" | "danger" | ""

export type Lang = "en" | "pt"

const USED_KEYS = ["utilization", "used_percentage", "usedPercentage", "used_percent", "usedPercent", "percent_used", "percentUsed"]
const NESTED_KEYS = ["quota", "usage", "rate_limits", "rateLimits", "oauth_usage", "oauthUsage"]

function record(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : null
}

/** A finite number, or a numeric string such as "35". */
function percent(value: unknown): number | undefined {
  const n = typeof value === "string" && value.trim() ? Number(value) : value
  return typeof n === "number" && Number.isFinite(n) ? n : undefined
}

function parseWindow(value: unknown): Window | null {
  const w = record(value)
  if (!w) return null
  const used = USED_KEYS.map((key) => percent(w[key])).find((p) => p !== undefined)
  if (used === undefined) return null
  const reset = w.resets_at ?? w.resetsAt ?? w.reset_at ?? w.resetAt
  const at = typeof reset === "string" ? Date.parse(reset) : NaN
  return Number.isFinite(at) ? { used: Math.max(0, Math.min(100, used)), resetsAt: at } : { used: Math.max(0, Math.min(100, used)) }
}

/** The window under its snake or camel key: `null` for an explicit null, `undefined` when missing or malformed. */
function readWindow(candidate: Record<string, unknown>, snake: string, camel: string): Window | null | undefined {
  if (candidate[snake] === null || candidate[camel] === null) return null
  return parseWindow(candidate[snake] ?? candidate[camel]) ?? undefined
}

/**
 * The reply of `GET /api/oauth/usage`, or `null` for a shape this parser does not know: the root
 * or a nested usage object must carry both windows, as objects or explicit nulls, and not both null.
 */
export function parseUsage(data: unknown): Usage | null {
  const root = record(data)
  if (!root) return null
  for (const candidate of [root, ...NESTED_KEYS.map((key) => record(root[key]))]) {
    if (!candidate) continue
    const fiveHour = readWindow(candidate, "five_hour", "fiveHour")
    const sevenDay = readWindow(candidate, "seven_day", "sevenDay")
    if (fiveHour === undefined || sevenDay === undefined) continue
    if (fiveHour === null && sevenDay === null) continue
    return {
      fiveHour,
      sevenDay,
      sonnet: readWindow(candidate, "seven_day_sonnet", "sevenDaySonnet") ?? null,
      opus: readWindow(candidate, "seven_day_opus", "sevenDayOpus") ?? null,
    }
  }
  return null
}

/** `shared.quota` from `cq config show --effective --json`; a leaf out of range keeps its default. */
export function settingsFromConfig(json: string): Settings {
  let values: { key?: unknown; value?: unknown }[] = []
  try {
    const parsed = JSON.parse(json) as { values?: unknown }
    if (Array.isArray(parsed.values)) values = parsed.values as typeof values
  } catch {
    return DEFAULTS
  }
  const at = (key: string) => values.find((v) => v.key === `shared.quota.${key}`)?.value
  const int = (v: unknown, d: number, min: number, max: number) =>
    typeof v === "number" && Number.isInteger(v) && v >= min && v <= max ? v : d
  const showSonnet = at("showSonnet")
  return {
    warnPercent: int(at("warnPercent"), DEFAULTS.warnPercent, 1, 100),
    dangerPercent: int(at("dangerPercent"), DEFAULTS.dangerPercent, 1, 100),
    intervalSeconds: int(at("intervalSeconds"), DEFAULTS.intervalSeconds, MIN_INTERVAL_SECONDS, Number.MAX_SAFE_INTEGER),
    showSonnet: typeof showSonnet === "boolean" ? showSonnet : DEFAULTS.showSonnet,
  }
}

const LANGUAGE = /^Language:\s*([A-Za-z0-9-]+)/m

/** The conversation language the root harness declares; any tag starting with `pt` is Portuguese. */
export function langOf(harness: string | undefined): Lang {
  const m = harness ? LANGUAGE.exec(harness) : null
  return m && m[1]!.toLowerCase().startsWith("pt") ? "pt" : "en"
}

/** The band's colour from the fuller of the two windows. */
export function toneOf(usage: Usage, settings: Settings): Tone {
  const used = Math.max(usage.fiveHour?.used ?? 0, usage.sevenDay?.used ?? 0)
  if (used >= settings.dangerPercent) return "danger"
  if (used >= settings.warnPercent) return "warning"
  return "success"
}

/** Four cells, a cell lit per started quarter: 35% → ▓▓░░. */
export function bar(used: number, cells = 4): string {
  const lit = used <= 0 ? 0 : Math.min(cells, Math.ceil((used / 100) * cells))
  return "▓".repeat(lit) + "░".repeat(cells - lit)
}

/** Time until a 5-hour reset: `2h30`, `45m`, `0m`. */
export function untilReset(at: number, now: number): string {
  const minutes = Math.max(0, Math.round((at - now) / 60_000))
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `${h}h${String(m).padStart(2, "0")}` : `${m}m`
}

const DAYS = { en: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], pt: ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"] }

/** A weekly reset in local time: `qui 13h`, `Thu 13h`; minutes only when not on the hour. */
export function weekday(at: number, lang: Lang): string {
  const d = new Date(at)
  const m = d.getMinutes()
  return `${DAYS[lang][d.getDay()]} ${d.getHours()}h${m ? String(m).padStart(2, "0") : ""}`
}

export type Words = {
  week: string
  noLimit: string
  noToken: string
  expired: string
  rejected: string
  rateLimited: (seconds: number) => string
  unavailable: (detail: string) => string
  unexpected: string
  loading: string
  detailTitle: string
  sourceOpencode: string
  sourceClaude: string
  readAt: (time: string) => string
  sonnet: string
  opus: string
  resets: (when: string) => string
}

export const WORDS: Record<Lang, Words> = {
  en: {
    week: "week",
    noLimit: "no limit",
    noToken: "Claude: no subscription detected",
    expired: "Claude: token expired — sign in again (claude auth login)",
    rejected: "Claude: the token was refused — sign in again (claude auth login)",
    rateLimited: (s) => `Claude quota: paused by the API, retry in ${s}s`,
    unavailable: (d) => `Claude quota unavailable (${d})`,
    unexpected: "Claude quota: unexpected reply",
    loading: "Claude quota…",
    detailTitle: "Claude subscription quota",
    sourceOpencode: "token: OpenCode auth.json",
    sourceClaude: "token: Claude Code .credentials.json",
    readAt: (t) => `read at ${t}`,
    sonnet: "week · Sonnet",
    opus: "week · Opus",
    resets: (w) => `resets ${w}`,
  },
  pt: {
    week: "semana",
    noLimit: "sem limite",
    noToken: "Claude: nenhuma assinatura detectada",
    expired: "Claude: token vencido — reautentique (claude auth login)",
    rejected: "Claude: o token foi recusado — reautentique (claude auth login)",
    rateLimited: (s) => `Cota do Claude: pausada pela API, nova leitura em ${s}s`,
    unavailable: (d) => `Cota do Claude indisponível (${d})`,
    unexpected: "Cota do Claude: resposta inesperada",
    loading: "Cota do Claude…",
    detailTitle: "Cota da assinatura Claude",
    sourceOpencode: "token: auth.json do OpenCode",
    sourceClaude: "token: .credentials.json do Claude Code",
    readAt: (t) => `lida às ${t}`,
    sonnet: "semana · Sonnet",
    opus: "semana · Opus",
    resets: (w) => `renova ${w}`,
  },
}

function segment(label: string, w: Window | null, reset: (at: number) => string, words: Words): string {
  if (!w) return `${label} ${words.noLimit}`
  const used = Math.round(w.used)
  return `${label} ${bar(w.used)} ${used}%${w.resetsAt !== undefined ? ` ↻ ${reset(w.resetsAt)}` : ""}`
}

/** `5h ▓▓░░ 35% ↻ 2h30 · semana ▓░░░ 17% ↻ qui 13h`. */
export function bandText(usage: Usage, now: number, lang: Lang): string {
  const words = WORDS[lang]
  return [
    segment("5h", usage.fiveHour, (at) => untilReset(at, now), words),
    segment(words.week, usage.sevenDay, (at) => weekday(at, lang), words),
  ].join(" · ")
}

/** The `/quenching-quota` detail: one line per window, the token's source and the reading's time. */
export function detailText(usage: Usage, now: number, settings: Settings, lang: Lang, source: "opencode" | "claude", readAt: number): string {
  const words = WORDS[lang]
  const line = (label: string, w: Window | null, reset: (at: number) => string) =>
    w ? `${label}: ${Math.round(w.used)}%${w.resetsAt !== undefined ? ` — ${words.resets(reset(w.resetsAt))}` : ""}` : `${label}: ${words.noLimit}`
  const lines = [
    line("5h", usage.fiveHour, (at) => `${untilReset(at, now)} (${weekday(at, lang)})`),
    line(words.week, usage.sevenDay, (at) => weekday(at, lang)),
  ]
  if (settings.showSonnet && usage.sonnet) lines.push(line(words.sonnet, usage.sonnet, (at) => weekday(at, lang)))
  if (settings.showSonnet && usage.opus) lines.push(line(words.opus, usage.opus, (at) => weekday(at, lang)))
  const t = new Date(readAt)
  lines.push(`${source === "opencode" ? words.sourceOpencode : words.sourceClaude} · ${words.readAt(`${t.getHours()}:${String(t.getMinutes()).padStart(2, "0")}`)}`)
  return lines.join("\n")
}
