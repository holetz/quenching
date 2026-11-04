import { spawn, type ChildProcess, type SpawnOptions } from "node:child_process"
import { existsSync, readFileSync } from "node:fs"
import { dirname, isAbsolute, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"

/** Uma execução de processo, sem lançar: o chamador decide pelo exit code. */
export type Run = { code: number; stdout: string; stderr: string }

/**
 * Como iniciar um `cq`: o executável, os argumentos que vêm antes dos do chamador e se a
 * linha vai crua para o `cmd.exe` (Windows, um `.cmd`). `source` diz de onde ele veio.
 */
export type Launch = {
  command: string
  prefix: string[]
  verbatim?: boolean
  file?: string
  source: "env" | "project" | "plugin" | "path"
}

const WINDOWS = process.platform === "win32"

/** Uma leitura do `cq` responde em 0,5–2 s; 15 s já é um processo preso, não um lento. */
export const READ_TIMEOUT = 15_000

/** Teto da saída guardada por processo: um `cq` que despeja mais que isso é morto, não acumulado. */
const OUTPUT_CAP = 8 * 1024 * 1024

function runProcess(command: string, args: string[], cwd: string, timeout: number, extra: SpawnOptions = {}): Promise<Run> {
  return new Promise((done) => {
    let child: ChildProcess
    try {
      child = spawn(command, args, { cwd, stdio: ["ignore", "pipe", "pipe"], env: process.env, windowsHide: true, ...extra })
    } catch (error) {
      done({ code: -1, stdout: "", stderr: String(error) })
      return
    }
    let stdout = ""
    let stderr = ""
    // SIGKILL depois do SIGTERM: um filho que ignora o primeiro não pode sobreviver ao plugin.
    const kill = () => {
      child.kill()
      setTimeout(() => { if (child.exitCode === null && child.signalCode === null) child.kill("SIGKILL") }, 2_000).unref()
    }
    const timer = setTimeout(kill, timeout)
    child.stdout?.setEncoding("utf8").on("data", (chunk: string) => {
      stdout += chunk
      if (stdout.length > OUTPUT_CAP) kill()
    })
    child.stderr?.setEncoding("utf8").on("data", (chunk: string) => {
      if (stderr.length < 64 * 1024) stderr += chunk
    })
    child.once("error", (error) => { clearTimeout(timer); done({ code: -1, stdout, stderr: String(error) }) })
    child.once("close", (code) => { clearTimeout(timer); done({ code: code ?? -1, stdout, stderr }) })
  })
}

// ── teto de processos ────────────────────────────────────────────────────────

/**
 * Um semáforo simples: no máximo `limit` tarefas ao mesmo tempo, o resto espera em fila.
 * O plugin roda dentro do serviço do OpenCode; uma rajada de hooks não pode virar uma
 * rajada de processos Python.
 */
export function limiter(limit: number): <T>(task: () => Promise<T>) => Promise<T> {
  let active = 0
  const queue: (() => void)[] = []
  const next = () => {
    if (active >= limit) return
    const start = queue.shift()
    if (start) start()
  }
  return <T>(task: () => Promise<T>) => new Promise<T>((resolveTask, rejectTask) => {
    queue.push(() => {
      active += 1
      task().then(resolveTask, rejectTask).finally(() => {
        active -= 1
        next()
      })
    })
    next()
  })
}

/** `cq` de leitura simultâneos. O deploy (`upgrade`) e o portal não passam por aqui. */
export const CQ_CONCURRENCY = 2
const cqSlot = limiter(CQ_CONCURRENCY)
const gitSlot = limiter(4)

/** Quantos processos `cq` de leitura estão rodando agora e o pico desde que o módulo subiu. */
export const cqStats = { running: 0, peak: 0, spawned: 0 }

/**
 * Uma promessa por chave enquanto ela está em voo: quem pede o mesmo durante a execução
 * espera a mesma resposta em vez de subir outro processo.
 */
export function singleFlight<T>(): (key: string, task: () => Promise<T>) => Promise<T> {
  const flying = new Map<string, Promise<T>>()
  return (key, task) => {
    const current = flying.get(key)
    if (current) return current
    const promise = task().finally(() => { flying.delete(key) })
    flying.set(key, promise)
    return promise
  }
}

export function exec(command: string, args: string[], cwd: string, timeout = READ_TIMEOUT): Promise<Run> {
  return runProcess(command, args, cwd, timeout)
}

export async function git(cwd: string, args: string[]): Promise<string | undefined> {
  const run = await gitSlot(() => exec("git", args, cwd, 10_000))
  return run.code === 0 ? run.stdout.trim() : undefined
}

const roots = new Map<string, { at: number; value: Promise<string | undefined> }>()

/**
 * O checkout principal do repositório. `--git-common-dir` é o mesmo para todas as worktrees;
 * o diretório pai dele é o checkout que hospeda `.git`. Muda só quando a worktree some, então
 * fica em cache por 10 min: antes cada leitura do `cq` subia um `git` só para isto.
 */
export function mainRoot(cwd: string): Promise<string | undefined> {
  const hit = roots.get(cwd)
  if (hit && Date.now() - hit.at < 600_000) return hit.value
  const value = git(cwd, ["rev-parse", "--git-common-dir"]).then((common) =>
    common ? dirname(isAbsolute(common) ? common : resolve(cwd, common)) : undefined)
  roots.set(cwd, { at: Date.now(), value })
  // Uma falha não fica em cache: a próxima chamada tenta de novo.
  void value.then((root) => { if (!root && roots.get(cwd)?.value === value) roots.delete(cwd) })
  return value
}

// ── o interpretador Python ───────────────────────────────────────────────────

let python: Promise<{ command: string; prefix: string[] }> | undefined

/**
 * O Python que roda o `cq`: `python3` fora do Windows; no Windows o launcher `py -3` quando
 * existe, senão `python` — a mesma ordem do `cq.cmd` que o deploy gera.
 */
function pythonLauncher(): Promise<{ command: string; prefix: string[] }> {
  if (!WINDOWS) return Promise.resolve({ command: "python3", prefix: [] })
  python ??= runProcess("py", ["-3", "--version"], process.cwd(), 10_000).then((run) =>
    run.code === 0 ? { command: "py", prefix: ["-3"] } : { command: "python", prefix: [] })
  return python
}

// ── a linha do cmd.exe ───────────────────────────────────────────────────────

function cmdQuote(value: string): string {
  return value === "" || /[\s"&|<>^()%!,;=]/.test(value) ? `"${value.replace(/"/g, '""')}"` : value
}

/** Um `.cmd` (ou um nome do PATH) pelo `cmd.exe`: o Node não abre `.cmd` sem shell. */
function viaCmd(target: string, source: Launch["source"]): Launch {
  return { command: process.env.ComSpec || "cmd.exe", prefix: ["/d", "/s", "/c"], verbatim: true, file: target, source }
}

// ── de onde vem o `cq` ───────────────────────────────────────────────────────

function isPython(file: string): boolean {
  try {
    return /^#!.*python/.test(readFileSync(file, "utf8").split("\n", 1)[0] ?? "")
  } catch {
    return false
  }
}

/** Um arquivo `cq`: pelo Python quando é script Python; senão o `.cmd` ao lado (Windows) ou o próprio arquivo. */
async function launchFile(file: string, source: Launch["source"]): Promise<Launch | undefined> {
  if (WINDOWS && /\.(cmd|bat)$/i.test(file)) return viaCmd(file, source)
  if (isPython(file)) {
    const py = await pythonLauncher()
    return { command: py.command, prefix: [...py.prefix, file], file, source }
  }
  if (WINDOWS) {
    const cmd = `${file}.cmd`
    return existsSync(cmd) ? viaCmd(cmd, source) : undefined
  }
  return { command: file, prefix: [], file, source }
}

/**
 * O `cq` que vem com o plugin: o pacote é instalado apontando para este checkout, e o
 * checkout carrega `quenching/assets/bin/cq` dois níveis acima do pacote.
 */
export function pluginCq(): string | undefined {
  try {
    const file = fileURLToPath(new URL("../../../quenching/assets/bin/cq", import.meta.url))
    return existsSync(file) ? file : undefined
  } catch {
    return undefined
  }
}

function fromEnv(): string | undefined {
  const value = process.env.QUENCHING_CQ?.trim()
  return value && existsSync(value) ? value : undefined
}

async function projectCq(root: string | undefined): Promise<Launch | undefined> {
  if (!root) return undefined
  const local = join(root, ".agents/quenching/bin/cq")
  return existsSync(local) ? launchFile(local, "project") : undefined
}

function pathCq(): Launch {
  return WINDOWS ? viaCmd("cq", "path") : { command: "cq", prefix: [], source: "path" }
}

/** O `cq` disponível para instalar: `QUENCHING_CQ`, o do checkout do plugin, o do PATH. */
export async function toolCq(): Promise<Launch> {
  const env = fromEnv()
  const envLaunch = env ? await launchFile(env, "env") : undefined
  if (envLaunch) return envLaunch
  const bundled = pluginCq()
  const bundledLaunch = bundled ? await launchFile(bundled, "plugin") : undefined
  return bundledLaunch ?? pathCq()
}

/** O `cq` do repositório quando existe; senão o disponível (`toolCq`). */
export async function cqBinary(cwd: string): Promise<{ launch: Launch; root?: string }> {
  const hit = binaries.get(cwd)
  if (hit && Date.now() - hit.at < 60_000) return hit.value
  const root = await mainRoot(cwd)
  const value = { launch: (await projectCq(root)) ?? (await toolCq()), root }
  binaries.set(cwd, { at: Date.now(), value })
  return value
}

const binaries = new Map<string, { at: number; value: { launch: Launch; root?: string } }>()

/** Depois de um deploy, o `cq` do projeto pode ter mudado de lugar. */
export function forgetBinaries(): void {
  binaries.clear()
}

/** Os argumentos finais do `spawn` e as opções que o lançamento exige. */
export function spawnArgs(launch: Launch, args: string[]): { command: string; args: string[]; options: SpawnOptions } {
  if (launch.verbatim) {
    const line = [launch.file ?? "", ...args].map(cmdQuote).join(" ")
    return { command: launch.command, args: [...launch.prefix, `"${line}"`], options: { windowsVerbatimArguments: true } }
  }
  return { command: launch.command, args: [...launch.prefix, ...args], options: {} }
}

export function runCq(launch: Launch, args: string[], cwd: string, timeout = READ_TIMEOUT): Promise<Run> {
  const call = spawnArgs(launch, args)
  return runProcess(call.command, call.args, cwd, timeout, call.options)
}

/** O processo de leitura em si; trocável nos testes para medir fila e deduplicação sem Python. */
export let readRunner: (launch: Launch, args: string[], cwd: string, timeout: number) => Promise<Run> = runCq

export function setReadRunner(runner: typeof readRunner): void {
  readRunner = runner
}

const reads = singleFlight<unknown>()

/**
 * Uma leitura `--json` do `cq`; `undefined` quando o comando recusa ou não devolve JSON.
 * A mesma leitura em voo é compartilhada e no máximo `CQ_CONCURRENCY` rodam ao mesmo tempo.
 */
export function cqJson<T>(cwd: string, args: string[], timeout = READ_TIMEOUT): Promise<T | undefined> {
  return reads(`${cwd}\0${args.join("\0")}`, async () => {
    const { launch } = await cqBinary(cwd)
    const run = await cqSlot(async () => {
      cqStats.running += 1
      cqStats.spawned += 1
      cqStats.peak = Math.max(cqStats.peak, cqStats.running)
      try {
        return await readRunner(launch, [...args, "--json"], cwd, timeout)
      } finally {
        cqStats.running -= 1
      }
    })
    if (run.code !== 0) return undefined
    try {
      return JSON.parse(run.stdout) as T
    } catch {
      return undefined
    }
  }) as Promise<T | undefined>
}
