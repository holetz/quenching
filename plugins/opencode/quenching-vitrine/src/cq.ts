import { spawn } from "node:child_process"
import { existsSync } from "node:fs"
import { dirname, isAbsolute, join, resolve } from "node:path"

/** Uma execução de processo, sem lançar: o chamador decide pelo exit code. */
export type Run = { code: number; stdout: string; stderr: string }

export function exec(command: string, args: string[], cwd: string, timeout = 30_000): Promise<Run> {
  return new Promise((done) => {
    let child
    try {
      child = spawn(command, args, { cwd, stdio: ["ignore", "pipe", "pipe"], env: process.env })
    } catch (error) {
      done({ code: -1, stdout: "", stderr: String(error) })
      return
    }
    let stdout = ""
    let stderr = ""
    const timer = setTimeout(() => child.kill(), timeout)
    child.stdout?.setEncoding("utf8").on("data", (chunk: string) => { stdout += chunk })
    child.stderr?.setEncoding("utf8").on("data", (chunk: string) => { stderr += chunk })
    child.once("error", (error) => { clearTimeout(timer); done({ code: -1, stdout, stderr: String(error) }) })
    child.once("close", (code) => { clearTimeout(timer); done({ code: code ?? -1, stdout, stderr }) })
  })
}

export async function git(cwd: string, args: string[]): Promise<string | undefined> {
  const run = await exec("git", args, cwd, 10_000)
  return run.code === 0 ? run.stdout.trim() : undefined
}

/**
 * O checkout principal do repositório. `--git-common-dir` é o mesmo para todas as worktrees;
 * o diretório pai dele é o checkout que hospeda `.git`.
 */
export async function mainRoot(cwd: string): Promise<string | undefined> {
  const common = await git(cwd, ["rev-parse", "--git-common-dir"])
  if (!common) return undefined
  return dirname(isAbsolute(common) ? common : resolve(cwd, common))
}

/** O `cq` do repositório quando existe; senão, o do PATH. */
export async function cqBinary(cwd: string): Promise<{ bin: string; root?: string }> {
  const root = await mainRoot(cwd)
  if (root) {
    const local = join(root, ".agents/quenching/bin/cq")
    if (existsSync(local)) return { bin: local, root }
  }
  return { bin: "cq", root }
}

/** Uma leitura `--json` do `cq`; `undefined` quando o comando recusa ou não devolve JSON. */
export async function cqJson<T>(cwd: string, args: string[], timeout = 30_000): Promise<T | undefined> {
  const { bin } = await cqBinary(cwd)
  const run = await exec(bin, [...args, "--json"], cwd, timeout)
  if (run.code !== 0) return undefined
  try {
    return JSON.parse(run.stdout) as T
  } catch {
    return undefined
  }
}
