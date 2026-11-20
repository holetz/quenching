// One chat's last main-thread request, as the bar needs it. Also saved in $.store under
// `cmx:<sessionId>` so an app restart or resume keeps the countdown.
export type Rec = {
  at: number // ms epoch when the last main-thread request started (the cache refresh)
  prefix: number // tokens the next request re-sends
  out: number // last reply's output tokens: written, not read, by the next request
  model: string
  read: number
  write: number
  ttlMin: number // 60, or 5 when the reply wrote the 5-minute cache or the checkout forces it
  warned: boolean // expiry pop-up already shown for this request
  window?: number // the model's context window in tokens
  resetBy?: 'model' | 'compact' // cache gone before its time ran out; cleared by the next reply
  isEstimate?: boolean // filled in from session-start data, not from a reply this plugin saw
}

declare module 'claude-code' {
  interface PluginState {
    'quenching-cache': { last: Shaped<Rec | null>; tick: number; hidden: boolean }
  }
}
