// The plugin's only child process: `cq config show --effective --json`, by fixed argv and without a
// shell. Discovery and launch are cut from integrations/opencode-vitrine/src/cq.ts, without the
// remote release, the deploy, `git` or any other verb: the project's `.agents/quenching/bin/cq`
// (found by walking up from the session's directory), then `QUENCHING_CQ`, then this checkout's
// own `quenching/assets/bin/cq`, then `cq` on PATH.
import { spawn, type ChildProcess, type SpawnOptions } from "node:child_process"
import { existsSync, readFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const ARGV = ["config", "show", "--effective", "--json"] as const
const TIMEOUT_MS = 20_000
const OUTPUT_CAP = 4 * 1024 * 1024
const WINDOWS = process.platform === "win32"

type Launch = { command: string; prefix: string[]; verbatim?: boolean; file?: string }

function run(command: string, args: string[], cwd: string, extra: SpawnOptions = {}): Promise<{ code: number; stdout: string }> {
  return new Promise((done) => {
    let stdout = ""
    let child: ChildProcess
    try {
      child = spawn(command, args, { cwd, stdio: ["ignore", "pipe", "ignore"], env: process.env, windowsHide: true, ...extra })
    } catch {
      done({ code: -1, stdout })
      return
    }
    const kill = () => {
      child.kill()
      setTimeout(() => { if (child.exitCode === null && child.signalCode === null) child.kill("SIGKILL") }, 2_000).unref()
    }
    const timer = setTimeout(kill, TIMEOUT_MS)
    child.stdout?.setEncoding("utf8").on("data", (chunk: string) => {
      stdout += chunk
      if (stdout.length > OUTPUT_CAP) kill()
    })
    child.once("error", () => { clearTimeout(timer); done({ code: -1, stdout }) })
    child.once("close", (code) => { clearTimeout(timer); done({ code: code ?? -1, stdout }) })
  })
}

function isPython(file: string): boolean {
  try {
    return /^#!.*python/.test(readFileSync(file, "utf8").split("\n", 1)[0] ?? "")
  } catch {
    return false
  }
}

function cmdQuote(value: string): string {
  return value === "" || /[\s"&|<>^()%!,;=]/.test(value) ? `"${value.replace(/"/g, '""')}"` : value
}

/** A `.cmd` goes through `cmd.exe`: Node does not start one without it (Windows only). */
const viaCmd = (file: string): Launch => ({ command: process.env.ComSpec || "cmd.exe", prefix: ["/d", "/s", "/c"], verbatim: true, file })

function launchFile(file: string): Launch | undefined {
  if (WINDOWS && /\.(cmd|bat)$/i.test(file)) return viaCmd(file)
  if (isPython(file)) return WINDOWS ? { command: "py", prefix: ["-3", file], file } : { command: "python3", prefix: [file], file }
  if (WINDOWS) return existsSync(`${file}.cmd`) ? viaCmd(`${file}.cmd`) : undefined
  return { command: file, prefix: [], file }
}

function projectCq(directory: string): string | undefined {
  for (let dir = directory; ; dir = dirname(dir)) {
    const file = join(dir, ".agents", "quenching", "bin", "cq")
    if (existsSync(file)) return file
    if (dirname(dir) === dir) return undefined
  }
}

function pluginCq(): string | undefined {
  const file = fileURLToPath(new URL("../../../quenching/assets/bin/cq", import.meta.url))
  return existsSync(file) ? file : undefined
}

function launchFor(directory: string): Launch {
  const env = process.env.QUENCHING_CQ?.trim()
  for (const file of [projectCq(directory), env && existsSync(env) ? env : undefined, pluginCq()]) {
    const launch = file ? launchFile(file) : undefined
    if (launch) return launch
  }
  return WINDOWS ? viaCmd("cq") : { command: "cq", prefix: [] }
}

/** `cq config show --effective --json` in `directory`: its stdout on exit 0, else `undefined`. */
export async function configShow(directory: string): Promise<string | undefined> {
  const launch = launchFor(directory)
  const args = [...ARGV]
  const result = launch.verbatim
    ? await run(launch.command, [...launch.prefix, `"${[launch.file ?? "", ...args].map(cmdQuote).join(" ")}"`], directory, { windowsVerbatimArguments: true })
    : await run(launch.command, [...launch.prefix, ...args], directory)
  return result.code === 0 ? result.stdout : undefined
}
