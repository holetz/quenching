/**
 * A superfície de segurança, lida no código: um destino de rede, um processo (o `cq`), nenhuma
 * escrita, nenhum log, nenhum storage. Falha quando um arquivo do plugin sai desse contorno.
 *
 *   node integrations/opencode-quota/tests/surface.check.mjs
 */
import { readdirSync, readFileSync } from "node:fs"
import { join, relative } from "node:path"
import { fileURLToPath } from "node:url"

const root = fileURLToPath(new URL("..", import.meta.url))
const files = []
const walk = (dir) => {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name)
    if (entry.isDirectory()) walk(path)
    else if (/\.(ts|tsx)$/.test(entry.name)) files.push(path)
  }
}
walk(join(root, "src"))
const fail = []
const rule = (file, text, pattern, allowed, what) => {
  if (pattern.test(text) && !allowed.includes(file)) fail.push(`${file}: ${what}`)
}
for (const path of files) {
  const file = relative(root, path).replaceAll("\\", "/")
  const text = readFileSync(path, "utf8")
  rule(file, text, /\bfetch\s*\(|\bfetcher\s*\(|XMLHttpRequest|WebSocket|node:https?\b|node:net\b|node:tls\b/, ["src/fetch.ts"], "rede fora de src/fetch.ts")
  rule(file, text, /node:child_process|\bspawn\s*\(|\bexecFile\s*\(|\bexecSync\s*\(/, ["src/cq.ts"], "processo fora de src/cq.ts")
  rule(file, text, /\bshell\s*:\s*true/, [], "shell: true")
  rule(file, text, /\bconsole\./, [], "log")
  rule(file, text, /\b(writeFile|appendFile|mkdir|rmSync|unlink|rename|copyFile|createWriteStream)\w*\s*\(/, [], "escrita em disco")
  rule(file, text, /\bstorage\.(set|get)\b/, [], "storage do host")
  rule(file, text, /\beval\s*\(|new Function\s*\(/, [], "código dinâmico")
  for (const url of text.match(/https?:\/\/[^\s"'`)]+/g) ?? []) {
    if (url !== "https://api.anthropic.com/api/oauth/usage") fail.push(`${file}: destino ${url}`)
  }
}
const token = readFileSync(join(root, "src/token.ts"), "utf8")
const imports = [...token.matchAll(/from\s+"([^"]+)"/g)].map((m) => m[1]).sort()
if (JSON.stringify(imports) !== JSON.stringify(["node:fs/promises", "node:os", "node:path"])) fail.push(`src/token.ts importa ${imports.join(", ")}`)
for (const path of files) {
  if (/\.refresh\w*|\[\s*["']refresh|grant_type/.test(readFileSync(path, "utf8"))) fail.push(`${relative(root, path)}: lê o refresh token`)
}
if (fail.length) {
  console.error(`FALHOU:\n${fail.join("\n")}`)
  process.exit(1)
}
console.log("ok")
