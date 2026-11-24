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
// Caso 1: o bloco global está em $OPENCODE_CONFIG; o aviso nomeia esse arquivo, sem mandar rodar o deploy.
const mcpOnly = { mcp: deployed.mcp }
const envFile = { path: "/x/custom.json", json: { experimental: { x: 1 } } }
const case1 = configWarnings(mcpOnly, [envFile])
ok(case1.length === 1 && case1[0].includes("/x/custom.json") && case1[0].includes('"subagent_depth": 4') && !case1[0].includes("cq deploy"), "o bloco em OPENCODE_CONFIG é nomeado e o deploy não é aconselhado")
// Caso 2: dois arquivos; as chaves estão no que o plugin não lia (config.json).
const two = [{ path: "/c/opencode.json", json: {} }, { path: "/c/config.json", json: { experimental: { x: 1 } } }]
ok(configWarnings(mcpOnly, two)[0].includes("/c/config.json"), "o bloco em config.json é nomeado")
ok(configWarnings(mcpOnly, [...two.slice(0, 1), { path: "/c/config.json", json: { experimental: { subagent_depth: 4 } } }]).length === 0, "a profundidade em qualquer global vale")
console.log("ok")
