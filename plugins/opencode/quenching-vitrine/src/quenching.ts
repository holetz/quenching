import { readFile } from "node:fs/promises"
import { join } from "node:path"
import { exec, git } from "./cq.js"

/**
 * O que o painel precisa saber sobre a instalação do quenching no projeto.
 * `available` é a versão do `cq` que o PATH entrega — a mesma que um upgrade usaria.
 */
export type QuenchingHealth = {
  installed: boolean
  version: string
  available: string
  outdated: boolean
  missing: boolean
  root: string
  error: string
}

export type QuenchingUpdate = {
  ok: boolean
  version: string
  available: string
  output: string
}

const MANIFESTS = [
  ".agents/.quenching-deploy.json",
  ".agents/quenching/.claude-plugin/plugin.json",
]

async function jsonVersion(path: string): Promise<string> {
  try {
    const value = JSON.parse(await readFile(path, "utf8")) as { version?: unknown }
    return typeof value.version === "string" ? value.version.trim() : ""
  } catch {
    return ""
  }
}

/** A versão materializada no projeto: o manifesto do deploy, o payload ou o VERSION. */
export async function installedVersion(root: string): Promise<string> {
  for (const rel of MANIFESTS) {
    const version = await jsonVersion(join(root, rel))
    if (version) return version
  }
  try {
    return (await readFile(join(root, ".agents/quenching/VERSION"), "utf8")).trim()
  } catch {
    return ""
  }
}

/** `[major, minor, patch]`, ou vazio quando a string não é uma versão numérica. */
export function parseVersion(value: string): number[] {
  const match = /(\d+)\.(\d+)\.(\d+)/.exec(value)
  return match ? [Number(match[1]), Number(match[2]), Number(match[3])] : []
}

export function isOlder(installed: string, available: string): boolean {
  const have = parseVersion(installed)
  const want = parseVersion(available)
  if (have.length !== 3 || want.length !== 3) return false
  for (let index = 0; index < 3; index += 1) {
    if (have[index] !== want[index]) return have[index] < want[index]
  }
  return false
}

async function toolVersion(cwd: string): Promise<{ version: string; error: string }> {
  const run = await exec("cq", ["--version"], cwd, 10_000)
  if (run.code !== 0) {
    const raw = (run.stderr || "").trim()
    const absent = /ENOENT|not found/i.test(raw)
    return { version: "", error: absent ? "cq não encontrado no PATH" : (raw || "cq falhou ao responder --version").slice(0, 300) }
  }
  const version = (run.stdout.match(/\d+\.\d+\.\d+[^\s]*/) ?? [""])[0]
  return { version, error: version ? "" : "o cq não devolveu uma versão" }
}

async function rootOf(cwd: string): Promise<string> {
  // A raiz da worktree atual, não o checkout principal: o alvo do aviso e do
  // deploy é o projeto que a sessão está editando.
  return (await git(cwd, ["rev-parse", "--show-toplevel"])) ?? cwd
}

export async function health(cwd: string): Promise<QuenchingHealth> {
  const root = await rootOf(cwd)
  const version = await installedVersion(root)
  const tool = await toolVersion(root)
  const installed = version !== ""
  return {
    installed,
    version,
    available: tool.version,
    outdated: installed && tool.version !== "" && isOlder(version, tool.version),
    missing: !installed,
    root,
    error: tool.error,
  }
}

/**
 * Escreve a superfície do quenching no projeto com o `cq` do PATH, o mesmo cujo
 * `--version` alimenta o aviso. Um alvo já instalado reusa o manifesto; um alvo
 * novo recebe só o harness OpenCode.
 */
export async function upgrade(cwd: string): Promise<QuenchingUpdate> {
  const root = await rootOf(cwd)
  const before = await installedVersion(root)
  const args = ["deploy", "--target", root, "--write", "--json"]
  if (!before) args.push("--harness", "opencode")
  const run = await exec("cq", args, root, 180_000)
  const version = await installedVersion(root)
  const tool = await toolVersion(root)
  const output = `${run.stdout}\n${run.stderr}`.trim()
  return {
    ok: run.code === 0,
    version,
    available: tool.version,
    output: output.slice(-4_000),
  }
}
