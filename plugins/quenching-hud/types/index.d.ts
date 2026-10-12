export type HudLine = {
  id: number
  stage: string
  checked: number
  total: number
  worktree: string
}

declare module 'claude-code' {
  interface PluginState {
    'quenching-hud': { line: HudLine | null }
  }
}
