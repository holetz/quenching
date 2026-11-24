import { readFile } from "node:fs/promises"
import { homedir } from "node:os"
import { join } from "node:path"

/** A profundidade que o fluxo orquestrado pede: condutor → orchestrator → runner → filho. */
export const MIN_DEPTH = 4

type Json = Record<string, unknown>

/** JSONC → JSON: tira comentários e vírgulas finais sem tocar em texto de string. */
export function parseJsonc(text: string): Json | undefined {
  let out = ""
  let index = 0
  while (index < text.length) {
    const char = text[index]
    if (char === '"') {
      let end = index + 1
      while (end < text.length && text[end] !== '"') end += text[end] === "\\" ? 2 : 1
      out += text.slice(index, end + 1)
      index = end + 1
    } else if (char === "/" && text[index + 1] === "/") {
      while (index < text.length && text[index] !== "\n") index += 1
    } else if (char === "/" && text[index + 1] === "*") {
      const end = text.indexOf("*/", index + 2)
      index = end < 0 ? text.length : end + 2
    } else {
      out += char
      index += 1
    }
  }
  try {
    const value = JSON.parse(out.replace(/,(\s*[}\]])/g, "$1")) as unknown
    return value && typeof value === "object" && !Array.isArray(value) ? (value as Json) : undefined
  } catch {
    return undefined
  }
}

const object = (value: unknown): Json | undefined =>
  value && typeof value === "object" && !Array.isArray(value) ? (value as Json) : undefined

/**
 * Os avisos locais do quenching no OpenCode, a partir das duas configurações já lidas.
 * Só leem; nenhum corpo de comando nem chamada de tool paga por eles.
 *
 * O deploy grava `experimental.subagent_depth` e o servidor MCP no `opencode.json` do projeto
 * (e pula a profundidade só quando um bloco `experimental` global seria escondido pelo do
 * projeto, anomalyco/opencode#60410). O aviso então dispara só no que o deploy não resolveu.
 */
export function configWarnings(project: Json | undefined, global: Json | undefined): string[] {
  const warnings: string[] = []

  const projectBlock = object(project?.experimental)
  const globalBlock = object(global?.experimental)
  // Um bloco `experimental` do projeto substitui o global inteiro.
  const depth = projectBlock ? projectBlock.subagent_depth : globalBlock?.subagent_depth
  if (typeof depth !== "number" || depth < MIN_DEPTH) {
    const have = typeof depth === "number" ? `está em ${depth}` : "não está definida (o padrão do OpenCode é 1)"
    const fix = !projectBlock && globalBlock && Object.keys(globalBlock).length > 0
      ? `adicione "subagent_depth": ${MIN_DEPTH} ao bloco experimental do opencode.jsonc global (o deploy não o escreve no projeto para não escondê-lo)`
      : `rode \`cq deploy --target . --write\` ou defina experimental.subagent_depth: ${MIN_DEPTH} no opencode.json do projeto`
    warnings.push(`A profundidade de subagentes ${have}; o fluxo do quenching precisa de ${MIN_DEPTH} — ${fix}, e reinicie o OpenCode.`)
  }

  const entry = object(object(project?.mcp)?.quenching) ?? object(object(global?.mcp)?.quenching)
  const command = Array.isArray(entry?.command) ? entry.command.map(String) : []
  if (!entry) {
    warnings.push("O servidor MCP quenching não está em opencode.json; rode `cq deploy --target . --write` (no Windows, declare shared.mcp.command, pois python3 não existe).")
  } else if (command.some((part) => /(^|[\\/])uvx(\.exe)?$/.test(part))) {
    warnings.push("O servidor MCP quenching usa uvx (um processo por chamada); rode `cq deploy --target . --runtime vendor --write` para o runtime vendorizado.")
  }
  return warnings
}

async function read(path: string): Promise<Json | undefined> {
  try {
    return parseJsonc(await readFile(path, "utf8"))
  } catch {
    return undefined
  }
}

async function first(paths: string[]): Promise<Json | undefined> {
  for (const path of paths) {
    const value = await read(path)
    if (value) return value
  }
  return undefined
}

/** Lê o opencode.json(c) do projeto e o global, uma vez, e devolve os avisos. */
export async function localWarnings(root: string): Promise<string[]> {
  const base = process.env.XDG_CONFIG_HOME || join(homedir(), ".config")
  const project = await first([join(root, "opencode.json"), join(root, "opencode.jsonc")])
  const global = await first([join(base, "opencode", "opencode.jsonc"), join(base, "opencode", "opencode.json")])
  return configWarnings(project, global)
}
