/**
 * Os avisos de configuração do OpenCode: só disparam no que o deploy não resolveu.
 *
 *   node --experimental-strip-types integrations/opencode-vitrine/bench/warnings.check.mjs
 */
import { configWarnings, parseJsonc } from "../src/warnings.ts"

const ok = (condition, message) => {
  if (!condition) {
    console.error(`FALHOU: ${message}`)
    process.exit(1)
  }
}
const deployed = parseJsonc('{ // c\n "mcp": { "quenching": { "command": ["python3", "cq", "mcp"], }, }, "experimental": { "subagent_depth": 4 } }')
ok(configWarnings(deployed, undefined).length === 0, "o projeto que o deploy configurou não pode avisar")
ok(configWarnings({}, undefined).length === 2, "sem profundidade e sem MCP são dois avisos")
ok(configWarnings({ mcp: { quenching: { command: ["uvx", "x"] } }, experimental: { subagent_depth: 3 } }, undefined).length === 2, "uvx e profundidade 3 avisam")
ok(configWarnings(deployed, { experimental: { subagent_depth: 1 } }).length === 0, "o bloco experimental do projeto vale sozinho")
ok(/global/.test(configWarnings({ mcp: deployed.mcp }, { experimental: { x: 1 } })[0]), "conflito com o bloco global aponta o global")
console.log("ok")
