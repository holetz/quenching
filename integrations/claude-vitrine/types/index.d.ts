export type View = 'specs' | 'config'

declare module 'claude-code' {
  interface PluginState {
    'quenching-vitrine': { view: View }
  }
}
