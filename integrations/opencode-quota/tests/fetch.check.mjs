/**
 * O token só para leitura e o destino único: fontes na ordem, nenhum envio de token vencido,
 * uma requisição por minuto por token, 429 pausa, 401 não renova, nada do token sai do módulo.
 *
 *   node --experimental-strip-types integrations/opencode-quota/tests/fetch.check.mjs
 */
import { mkdirSync, mkdtempSync, readFileSync, statSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { forget, readQuota, USAGE_URL } from "../src/fetch.ts"
import { readToken } from "../src/token.ts"

const ok = (condition, message) => {
  if (!condition) {
    console.error(`FALHOU: ${message}`)
    process.exit(1)
  }
}
const NOW = Date.UTC(2026, 10, 24, 18)
const scratch = mkdtempSync(join(tmpdir(), "quota-fetch-"))
const tree = (name) => {
  const home = join(scratch, name)
  mkdirSync(join(home, ".claude"), { recursive: true })
  mkdirSync(join(home, ".local", "share", "opencode"), { recursive: true })
  return { home, env: {} }
}
const claude = (places, token, expiresAt = NOW + 3_600_000) =>
  writeFileSync(join(places.home, ".claude", ".credentials.json"), JSON.stringify({ claudeAiOauth: { accessToken: token, refreshToken: "r-secret", expiresAt } }))
const opencode = (places, login) =>
  writeFileSync(join(places.home, ".local", "share", "opencode", "auth.json"), JSON.stringify({ anthropic: login }))
const reply = { five_hour: { utilization: 35, resets_at: "2026-11-24T20:30:00Z" }, seven_day: { utilization: 17, resets_at: "2026-11-26T16:00:00Z" } }
const fake = (status = 200, body = reply, headers = {}) => {
  const calls = []
  const fetcher = async (url, init) => {
    calls.push({ url, init })
    return new Response(JSON.stringify(body), { status, headers })
  }
  return { calls, fetcher }
}

// As fontes, na ordem: auth.json do OpenCode (só OAuth), depois o .credentials.json do Claude Code.
const empty = tree("empty")
ok((await readToken(NOW, empty)).state === "none", "sem arquivo não há assinatura")
const both = tree("both")
claude(both, "tok-claude")
ok((await readToken(NOW, both)).source === "claude", "só o Claude Code: fonte claude")
opencode(both, { type: "api", key: "sk-x" })
ok((await readToken(NOW, both)).source === "claude", "login do OpenCode que não é OAuth é ignorado")
opencode(both, { type: "oauth", access: "tok-opencode", refresh: "r", expires: NOW + 1 })
const first = await readToken(NOW, both)
ok(first.source === "opencode" && first.value === "tok-opencode", "OAuth do OpenCode vence")
const custom = tree("custom")
mkdirSync(join(custom.home, "cfg"))
writeFileSync(join(custom.home, "cfg", ".credentials.json"), JSON.stringify({ claudeAiOauth: { accessToken: "tok-dir" } }))
ok((await readToken(NOW, { home: custom.home, env: { CLAUDE_CONFIG_DIR: join(custom.home, "cfg") } })).value === "tok-dir", "CLAUDE_CONFIG_DIR é respeitado")
const old = tree("old")
claude(old, "tok-old", NOW - 1)
ok((await readToken(NOW, old)).state === "expired", "token vencido é reconhecido")

// Ler não grava: os arquivos ficam como estavam.
const credPath = join(both.home, ".claude", ".credentials.json")
const before = [readFileSync(credPath, "utf8"), statSync(credPath).mtimeMs]

const tokenOf = (places) => () => readToken(NOW, places)
// Sem assinatura e com token vencido, nenhuma requisição.
forget()
let net = fake()
ok((await readQuota({ intervalSeconds: 300, now: NOW, token: tokenOf(empty), fetcher: net.fetcher })).state === "none", "sem token: none")
ok((await readQuota({ intervalSeconds: 300, now: NOW, token: tokenOf(old), fetcher: net.fetcher })).state === "expired", "vencido: expired")
ok(net.calls.length === 0, "nem sem token nem com token vencido há requisição")

// O destino único, os headers e o redirect recusado.
const fresh = await readQuota({ intervalSeconds: 300, now: NOW, token: tokenOf(both), fetcher: net.fetcher })
ok(fresh.state === "ok" && fresh.usage.fiveHour.used === 35 && fresh.source === "opencode", "leitura ok")
ok(net.calls.length === 1 && net.calls[0].url === USAGE_URL && USAGE_URL === "https://api.anthropic.com/api/oauth/usage", "um destino só")
const sent = net.calls[0].init
ok(sent.headers.Authorization === "Bearer tok-opencode" && sent.headers["anthropic-beta"] === "oauth-2025-04-20" && sent.redirect === "error" && sent.method === "GET", "headers e redirect")
ok(!JSON.stringify(fresh).includes("tok-opencode"), "a leitura não carrega o token")

// Intervalo mínimo de 60 s, mesmo com intervalSeconds menor; o intervalo configurado acima dele.
await readQuota({ intervalSeconds: 10, now: NOW + 59_000, token: tokenOf(both), fetcher: net.fetcher })
ok(net.calls.length === 1, "dentro de 60 s não pergunta de novo, mesmo com intervalo 10")
await readQuota({ intervalSeconds: 300, now: NOW + 120_000, token: tokenOf(both), fetcher: net.fetcher })
ok(net.calls.length === 1, "dentro do intervalo configurado reaproveita")
await readQuota({ intervalSeconds: 300, now: NOW + 120_000, force: true, token: tokenOf(both), fetcher: net.fetcher })
ok(net.calls.length === 2, "Atualizar pergunta passado o piso de 60 s")
await readQuota({ intervalSeconds: 300, now: NOW + 130_000, force: true, token: tokenOf(both), fetcher: net.fetcher })
ok(net.calls.length === 2, "Atualizar não fura o piso de 60 s")

// Requisições simultâneas compartilham uma.
forget()
net = fake()
await Promise.all([1, 2, 3].map(() => readQuota({ intervalSeconds: 300, now: NOW, token: tokenOf(both), fetcher: net.fetcher })))
ok(net.calls.length === 1, "leituras simultâneas viram uma requisição")

// 401: para de perguntar até o token mudar, e nunca renova.
forget()
net = fake(401, { error: "tok-opencode is invalid" })
ok((await readQuota({ intervalSeconds: 300, now: NOW, token: tokenOf(both), fetcher: net.fetcher })).state === "rejected", "401 é rejected")
ok((await readQuota({ intervalSeconds: 300, now: NOW + 3_600_000, token: tokenOf(both), fetcher: net.fetcher })).state === "rejected" && net.calls.length === 1, "token recusado não é reenviado")
opencode(both, { type: "oauth", access: "tok-opencode-2", expires: NOW + 7_200_000 })
await readQuota({ intervalSeconds: 300, now: NOW + 3_600_000, token: tokenOf(both), fetcher: net.fetcher })
ok(net.calls.length === 2, "token novo pergunta de novo")
ok(net.calls.every((c) => c.url === USAGE_URL), "401 não leva a nenhum outro destino (nada de refresh)")

// 429: pausa pelo Retry-After, no mínimo o intervalo.
forget()
net = fake(429, {}, { "Retry-After": "600" })
const limited = await readQuota({ intervalSeconds: 300, now: NOW, token: tokenOf(both), fetcher: net.fetcher })
ok(limited.state === "rateLimited" && limited.retryAt === NOW + 600_000, "429 respeita o Retry-After")
await readQuota({ intervalSeconds: 300, now: NOW + 599_000, token: tokenOf(both), fetcher: net.fetcher })
ok(net.calls.length === 1, "pausado não pergunta")

// Falha de rede: texto fixo, sem a mensagem do runtime; nova tentativa só depois de 60 s.
forget()
let thrown = 0
const boom = async () => { thrown += 1; throw new Error("connect failed, header Bearer tok-opencode-2") }
const failed = await readQuota({ intervalSeconds: 300, now: NOW, token: tokenOf(both), fetcher: boom })
ok(failed.state === "unavailable" && failed.detail === "network" && !JSON.stringify(failed).includes("tok-"), "erro de rede não ecoa a mensagem")
await readQuota({ intervalSeconds: 300, now: NOW + 30_000, token: tokenOf(both), fetcher: boom })
await readQuota({ intervalSeconds: 300, now: NOW + 61_000, token: tokenOf(both), fetcher: boom })
ok(thrown === 2, "falha é repetida depois do piso, não do intervalo inteiro")
forget()
net = fake(200, { nothing: true })
ok((await readQuota({ intervalSeconds: 300, now: NOW, token: tokenOf(both), fetcher: net.fetcher })).state === "unexpected", "forma desconhecida é unexpected")
net = fake(500, { echo: "tok-opencode-2" })
forget()
const server = await readQuota({ intervalSeconds: 300, now: NOW, token: tokenOf(both), fetcher: net.fetcher })
ok(server.state === "unavailable" && server.detail === "HTTP 500", "erro do servidor diz só o status")

ok(readFileSync(credPath, "utf8") === before[0] && statSync(credPath).mtimeMs === before[1], "o .credentials.json não foi tocado")
console.log("ok")
