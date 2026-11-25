import { readFile } from "node:fs/promises"
import { join } from "node:path"
import { git, remoteRepo, runCq, toolCq, type Launch } from "./cq.js"
import { localWarnings } from "./warnings.js"

/**
 * O que o painel precisa saber sobre a instalação do quenching no projeto.
 * `available` é a versão do `cq` que um upgrade usaria (`toolCq`): `QUENCHING_CQ`, a árvore
 * do repositório-fonte, a última release remota, o checkout do plugin ou, por último, o PATH.
 */
export type QuenchingHealth = {
  installed: boolean
  version: string
  available: string
  outdated: boolean
  missing: boolean
  root: string
  error: string
  /** De onde vem o `cq` de `available`, em uma frase curta para o tooltip. */
  origin: string
  /** Avisos locais: profundidade de subagentes e servidor MCP, lidos da configuração. */
  warnings: string[]
}

export type QuenchingUpdate = {
  ok: boolean
  version: string
  available: string
  output: string
}

const MANIFESTS = [
  ".agents/.quenching-deploy.json",
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

const ORIGIN: Record<Launch["source"], string> = {
  env: "QUENCHING_CQ",
  project: "cq do projeto",
  source: "árvore do repositório-fonte",
  remote: "release remota",
  plugin: "checkout do plugin",
  path: "PATH",
}

export function originOf(launch: Launch): string {
  return launch.source === "remote" ? `release ${launch.tag} (${remoteRepo()}, via uvx)` : ORIGIN[launch.source]
}

function absence(launch: Launch): string {
  if (launch.source === "path") return "cq não encontrado: nem QUENCHING_CQ, nem release remota (uvx), nem o checkout do plugin, nem o PATH"
  return `Python 3.11+ não encontrado (${launch.command}) para rodar o cq de ${ORIGIN[launch.source]}`
}

/** O primeiro `uvx` de uma tag clona e monta o pacote; o deploy remoto ganha mais folga. */
const DEPLOY_TIMEOUT = { local: 180_000, remote: 600_000 }

async function toolVersion(cwd: string, launch: Launch): Promise<{ version: string; error: string }> {
  // A tag já é a versão: abrir o painel não paga um clone pelo `uvx`.
  if (launch.source === "remote" && launch.tag) return { version: launch.tag, error: "" }
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
  const launch = await toolCq(root)
  const tool = await toolVersion(root, launch)
  const installed = version !== ""
  return {
    installed,
    version,
    available: tool.version,
    outdated: installed && tool.version !== "" && isOlder(version, tool.version),
    missing: !installed,
    root,
    error: tool.error,
    origin: originOf(launch),
    warnings: installed ? await localWarnings(root) : [],
  }
}

/**
 * Escreve a superfície do quenching no projeto com o mesmo `cq` (`toolCq`) que deu a
 * versão do aviso — por padrão a última release, pelo `uvx`. Um alvo já instalado reusa
 * o manifesto; um alvo novo recebe só o harness OpenCode.
 */
export async function upgrade(cwd: string): Promise<QuenchingUpdate> {
  const root = await rootOf(cwd)
  const before = await installedVersion(root)
  const args = ["deploy", "--target", root, "--write", "--json"]
  if (!before) args.push("--harness", "opencode")
  const launch = await toolCq(root)
  const run = await runCq(launch, args, root, launch.source === "remote" ? DEPLOY_TIMEOUT.remote : DEPLOY_TIMEOUT.local)
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
