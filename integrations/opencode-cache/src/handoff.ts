// /quenching-cache handoff for OpenCode. Filled in by the handoff task; the server already calls it.
import type { Words } from './core/i18n.ts'

export type HandoffInput = { sessionID: string; directory: string; focus: string; words: Words }
export type HandoffResult = { ok: boolean; text: string; line: string }

export async function runHandoff(input: HandoffInput): Promise<HandoffResult> {
  return { ok: false, text: input.words.handoffFailed('not wired yet'), line: '' }
}
