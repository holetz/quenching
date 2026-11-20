export type View = 'specs' | 'config'

/** What the session did with a spec: the checkout it is in, a commit, a write, a read or a mention. */
export type Kind = 'worktree' | 'command' | 'read' | 'commit' | 'mention'

export type LedgerEntry = { id: number; kind: Kind; at: number }

declare module 'claude-code' {
  interface PluginState {
    'quenching-vitrine': { view: View; ledger: Shaped<LedgerEntry[]> }
  }
}
