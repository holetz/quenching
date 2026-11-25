/**
 * O parser da resposta de uso e as palavras da faixa.
 *
 *   node --experimental-strip-types integrations/opencode-quota/tests/usage.check.mjs
 */
import { readFileSync } from "node:fs"
import { bandText, bar, detailText, DEFAULTS, langOf, parseUsage, settingsFromConfig, toneOf, untilReset, weekday } from "../src/core/usage.ts"

const ok = (condition, message) => {
  if (!condition) {
    console.error(`FALHOU: ${message}`)
    process.exit(1)
  }
}
const fixture = (name) => JSON.parse(readFileSync(new URL(`./fixtures/${name}.json`, import.meta.url), "utf8"))

// O parser: janelas ausentes por plano, porcentagem em string, semanas por modelo.
const noFive = parseUsage(fixture("no-five-hour-limit"))
ok(noFive && noFive.fiveHour === null && noFive.sevenDay?.used === 33, "sem 5 h: a semana vem e a 5 h é null")
const noWeek = parseUsage(fixture("no-weekly-limit"))
ok(noWeek && noWeek.sevenDay === null && noWeek.fiveHour?.used === 12, "sem semana: a 5 h vem e a semana é null")
const sonnet = parseUsage(fixture("sonnet"))
ok(sonnet && sonnet.fiveHour?.used === 35 && sonnet.sonnet?.used === 8 && sonnet.opus === null, "utilização em string e seven_day_sonnet")
ok(sonnet.fiveHour.resetsAt === Date.parse("2026-11-24T20:30:00Z"), "resets_at vira epoch ms")
ok(parseUsage({ usage: { fiveHour: { utilization: 5 }, sevenDay: { utilization: 6 } } })?.sevenDay?.used === 6, "objeto aninhado e chaves camel")
ok(parseUsage({ five_hour: null, seven_day: null }) === null, "as duas janelas null é forma desconhecida")
ok(parseUsage({ five_hour: { utilization: 1 } }) === null, "janela faltando é forma desconhecida")
ok(parseUsage("x") === null && parseUsage(null) === null && parseUsage([]) === null, "não-objeto é forma desconhecida")
ok(parseUsage({ five_hour: { utilization: 140 }, seven_day: { utilization: -3 } })?.fiveHour?.used === 100, "uso fora de 0–100 é limitado")

// A formatação: barras, reset curto, dia da semana, as duas línguas.
ok(bar(35) === "▓▓░░" && bar(17) === "▓░░░" && bar(0) === "░░░░" && bar(100) === "▓▓▓▓", "quatro células")
ok(untilReset(Date.UTC(2026, 0, 1, 2, 30), Date.UTC(2026, 0, 1)) === "2h30" && untilReset(45 * 60_000, 0) === "45m" && untilReset(0, 10) === "0m", "reset curto")
const thu13 = new Date(2026, 10, 26, 13, 0).getTime()
ok(weekday(thu13, "pt") === "qui 13h" && weekday(thu13, "en") === "Thu 13h", "dia da semana local")
ok(weekday(new Date(2026, 10, 26, 13, 5).getTime(), "pt") === "qui 13h05", "minutos quando não é hora cheia")
const now = Date.UTC(2026, 10, 24, 18, 0)
const usage = { fiveHour: { used: 35, resetsAt: now + 150 * 60_000 }, sevenDay: { used: 17, resetsAt: thu13 }, sonnet: { used: 8 }, opus: null }
ok(bandText(usage, now, "pt") === "5h ▓▓░░ 35% ↻ 2h30 · semana ▓░░░ 17% ↻ qui 13h", `faixa pt: ${bandText(usage, now, "pt")}`)
ok(bandText(usage, now, "en") === "5h ▓▓░░ 35% ↻ 2h30 · week ▓░░░ 17% ↻ Thu 13h", "faixa en")
ok(bandText({ ...usage, fiveHour: null }, now, "pt").startsWith("5h sem limite · "), "janela sem limite")
const detail = detailText(usage, now, DEFAULTS, "pt", "claude", now)
ok(detail.includes("semana · Sonnet: 8%") && detail.includes(".credentials.json"), "detalhe com Sonnet e a fonte")
ok(!detailText(usage, now, { ...DEFAULTS, showSonnet: false }, "pt", "claude", now).includes("Sonnet"), "showSonnet false esconde o Sonnet")

// Tons pelos limiares, e as configurações lidas do `cq`.
ok(toneOf(usage, DEFAULTS) === "success", "35% é verde")
ok(toneOf({ ...usage, sevenDay: { used: 70 } }, DEFAULTS) === "warning", "70% é amarelo")
ok(toneOf({ ...usage, fiveHour: { used: 95 } }, DEFAULTS) === "danger", "95% é vermelho")
const shown = JSON.stringify({ values: [
  { key: "shared.quota.warnPercent", value: 50 }, { key: "shared.quota.dangerPercent", value: 101 },
  { key: "shared.quota.intervalSeconds", value: 30 }, { key: "shared.quota.showSonnet", value: false },
] })
const settings = settingsFromConfig(shown)
ok(settings.warnPercent === 50 && settings.dangerPercent === 90 && settings.intervalSeconds === 300 && settings.showSonnet === false, "folha fora da faixa cai no padrão")
ok(settingsFromConfig("not json") === DEFAULTS, "saída ilegível dá os padrões")
ok(langOf("# x\n\nLanguage: pt-BR — y") === "pt" && langOf("Language: en") === "en" && langOf(undefined) === "en", "idioma do AGENTS.md")
console.log("ok")
