import { readFile } from "node:fs/promises"
import { join } from "node:path"
import { git, runCq, toolCq, type Launch } from "./cq.js"

/**
 * O que o painel precisa saber sobre a instalação do quenching no projeto.
 * `available` é a versão do `cq` que um upgrade usaria: `QUENCHING_CQ`, o checkout do
 * plugin ou, por último, o PATH.
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

function absence(launch: Launch): string {
  if (launch.source === "path") return "cq não encontrado: nem o checkout do plugin, nem QUENCHING_CQ, nem o PATH"
  return `Python 3.11+ não encontrado (${launch.command}) para rodar o cq do ${launch.source === "env" ? "QUENCHING_CQ" : "checkout do plugin"}`
}

async function toolVersion(cwd: string, launch: Launch): Promise<{ version: string; error: string }> {
  const run = await runCq(launch, ["--version"], cwd, 10_000)
  if (run.code !== 0) {
    const raw = (run.stderr || "").trim()
    const absent = /ENOENT|not found|não é reconhecido|is not recognized/i.test(raw)
    return { version: "", error: absent ? absence(launch) : (raw || "cq falhou ao responder --version").slice(0, 300) }
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
  const tool = await toolVersion(root, await toolCq())
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
 * Escreve a superfície do quenching no projeto com o mesmo `cq` (`toolCq`) cujo
 * `--version` alimenta o aviso. Um alvo já instalado reusa o manifesto; um alvo
 * novo recebe só o harness OpenCode.
 */
export async function upgrade(cwd: string): Promise<QuenchingUpdate> {
  const root = await rootOf(cwd)
  const before = await installedVersion(root)
  const args = ["deploy", "--target", root, "--write", "--json"]
  if (!before) args.push("--harness", "opencode")
  const launch = await toolCq()
  const run = await runCq(launch, args, root, 180_000)
  const version = await installedVersion(root)
  const tool = await toolVersion(root, launch)
  const output = `${run.stdout}\n${run.stderr}`.trim()
  return {
    ok: run.code === 0,
    version,
    available: tool.version,
    output: output.slice(-4_000),
  }
}
