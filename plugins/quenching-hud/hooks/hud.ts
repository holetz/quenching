import type { HudLine } from '../types'

const BRANCH = /^plan\/(\d+)-/

/** The spec id a `plan/<id>-<handle>` branch carries; digits only, so it is safe in an argv. */
export const specIdFromBranch = (branch: string): number | null => {
  const match = BRANCH.exec(branch.trim())

  return match ? Number(match[1]) : null
}

export const formatLine = (line: HudLine): string =>
  `spec ${line.id} · ${line.stage} · ${line.checked}/${line.total} · ${line.worktree}`

/** Builds a line from `cq specs status --spec <id> --json` stdout; null when it does not parse. */
export const lineFromStatus = (
  id: number,
  stdout: string,
  worktree: string
): HudLine | null => {
  try {
    const status = JSON.parse(stdout)
    const tasks = status?.tasks

    if (typeof status?.stage !== 'string' || typeof tasks?.checked !== 'number' || typeof tasks?.total !== 'number') {
      return null
    }

    return { id, stage: status.stage, checked: tasks.checked, total: tasks.total, worktree }
  } catch {
    return null
  }
}

export const basename = (path: string): string => path.replace(/\/+$/, '').split('/').pop() ?? path
