/** One process run, never thrown: the caller decides by the exit code. */
export type Run = { code: number; stdout: string; stderr: string }

/** Runs an argv, with no shell, in a working directory. The mod binds it to `$.process.run`. */
export type Runner = (argv: string[], cwd: string, timeoutMs: number) => Promise<Run>

/** A `cq` read answers in 0.5 to 2 s; 15 s is a stuck process, not a slow one. */
export const READ_TIMEOUT = 15_000

/** Reads that run at once; the rest wait their turn, so a burst of events is never a burst of processes. */
export const CQ_CONCURRENCY = 2

/** At most `limit` tasks at the same time; the others queue. */
export function limiter(limit: number): <T>(task: () => Promise<T>) => Promise<T> {
  let active = 0
  const queue: (() => void)[] = []
  const next = () => {
    if (active >= limit) {
      return
    }
    queue.shift()?.()
  }

  return <T>(task: () => Promise<T>) =>
    new Promise<T>((resolve, reject) => {
      queue.push(() => {
        active += 1
        task()
          .then(resolve, reject)
          .finally(() => {
            active -= 1
            next()
          })
      })
      next()
    })
}

/** One promise per key while it is in flight: the same ask during the run waits for the same answer. */
export function singleFlight<T>(): (key: string, task: () => Promise<T>) => Promise<T> {
  const flying = new Map<string, Promise<T>>()

  return (key, task) => {
    const current = flying.get(key)

    if (current) {
      return current
    }
    const promise = task().finally(() => {
      flying.delete(key)
    })
    flying.set(key, promise)

    return promise
  }
}

export type ConfigWrite = { ok: boolean; message: string }

/** What the pane learns about `cq` before it draws anything: present, with its version, or not. */
export type Probe = { found: boolean; version: string; detail: string }

export type Cq = {
  /** A `--json` read; `undefined` when `cq` refuses, is absent or prints no JSON. */
  json: <T>(cwd: string, args: string[], timeoutMs?: number) => Promise<T | undefined>
  /** The same read, but exit 1 still hands over the payload: `schedule` exits 1 on a cycle, and the cycle is the datum. */
  jsonPartial: <T>(cwd: string, args: string[], timeoutMs?: number) => Promise<T | undefined>
  /** `cq --version`: found or not, never a crash. */
  probe: (cwd: string) => Promise<Probe>
  /** The raw `cq config schema --values --json` text, or the reason it failed. */
  configSchema: (cwd: string) => Promise<{ ok: boolean; json: string; error: string }>
  /** `cq config set|unset`, the only writer; `value` is JSON, or null to unset. */
  configWrite: (cwd: string, key: string, layer: 'project' | 'local', value: string | null) => Promise<ConfigWrite>
  /** Reads started and the most that ran together, for the tests. */
  stats: { running: number; peak: number; spawned: number }
}

/** `cq` over a runner: JSON reads with a concurrency cap and de-duplication, and the config writer. */
export function createCq(runner: Runner, concurrency = CQ_CONCURRENCY): Cq {
  const slot = limiter(concurrency)
  const reads = singleFlight<unknown>()
  const stats = { running: 0, peak: 0, spawned: 0 }

  const read = <T>(cwd: string, args: string[], timeoutMs: number, accept: (code: number) => boolean) =>
    reads(`${cwd}\0${args.join('\0')}`, async () => {
      const run = await slot(async () => {
        stats.running += 1
        stats.spawned += 1
        stats.peak = Math.max(stats.peak, stats.running)

        try {
          return await runner(['cq', ...args, '--json'], cwd, timeoutMs)
        } finally {
          stats.running -= 1
        }
      })

      if (!accept(run.code)) {
        return undefined
      }

      try {
        return JSON.parse(run.stdout) as T
      } catch {
        return undefined
      }
    }) as Promise<T | undefined>

  return {
    json: (cwd, args, timeoutMs = READ_TIMEOUT) => read(cwd, args, timeoutMs, code => code === 0),
    jsonPartial: (cwd, args, timeoutMs = READ_TIMEOUT) => read(cwd, args, timeoutMs, code => code === 0 || code === 1),
    probe: async cwd => {
      const run = await runner(['cq', '--version'], cwd, 10_000)

      if (run.code !== 0) {
        return { found: false, version: '', detail: run.stderr.trim() || `cq --version exited ${run.code}` }
      }

      return { found: true, version: run.stdout.trim(), detail: '' }
    },
    configSchema: async cwd => {
      const run = await runner(['cq', 'config', 'schema', '--values', '--json'], cwd, READ_TIMEOUT)

      if (run.code !== 0) {
        return { ok: false, json: '', error: run.stderr.trim() || run.stdout.trim() || `cq exited ${run.code}` }
      }

      return { ok: true, json: run.stdout, error: '' }
    },
    configWrite: async (cwd, key, layer, value) => {
      const args =
        value === null
          ? ['cq', 'config', 'unset', key, '--layer', layer, '--json']
          : ['cq', 'config', 'set', key, value, '--layer', layer, '--json']
      const run = await runner(args, cwd, READ_TIMEOUT)

      try {
        const payload = JSON.parse(run.stdout) as { message?: string; remedy?: string }

        if (run.code === 0) {
          return { ok: true, message: '' }
        }

        return { ok: false, message: [payload.message, payload.remedy].filter(Boolean).join(' — ') }
      } catch {
        return { ok: run.code === 0, message: run.stderr.trim() || run.stdout.trim() }
      }
    },
    stats,
  }
}
