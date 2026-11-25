// The Claude subscription's OAuth token, read and never written, logged or refreshed. Two sources,
// in order: OpenCode's own `auth.json` (an `anthropic` OAuth login), then Claude Code's
// `.credentials.json` (the `claude-agent` route). Only `readFile`; nothing here opens a process.
import { readFile } from "node:fs/promises"
import { homedir } from "node:os"
import { join } from "node:path"

export type Source = "opencode" | "claude"

/** A usable token, a token past its expiry (never sent), or no subscription at all. */
export type Token =
  | { state: "ok"; source: Source; value: string }
  | { state: "expired"; source: Source }
  | { state: "none" }

/** Where to look; the environment and the home are parameters so the checks can point them at a scratch tree. */
export type Places = { env: NodeJS.ProcessEnv; home: string }

const here = (): Places => ({ env: process.env, home: homedir() })

export function authJsonPaths({ env, home }: Places): string[] {
  return [
    env.XDG_DATA_HOME ? join(env.XDG_DATA_HOME, "opencode", "auth.json") : undefined,
    join(home, ".local", "share", "opencode", "auth.json"),
    env.LOCALAPPDATA ? join(env.LOCALAPPDATA, "opencode", "auth.json") : undefined,
  ].filter((p): p is string => Boolean(p))
}

export function credentialsPath({ env, home }: Places): string {
  return join(env.CLAUDE_CONFIG_DIR || join(home, ".claude"), ".credentials.json")
}

async function readJson(path: string): Promise<Record<string, unknown> | undefined> {
  try {
    const parsed = JSON.parse(await readFile(path, "utf8")) as unknown
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? (parsed as Record<string, unknown>) : undefined
  } catch {
    return undefined
  }
}

function pick(source: Source, value: unknown, expires: unknown, now: number): Token | undefined {
  if (typeof value !== "string" || !value.trim()) return undefined
  if (typeof expires === "number" && Number.isFinite(expires) && expires <= now) return { state: "expired", source }
  return { state: "ok", source, value: value.trim() }
}

/** The first source holding a token wins, expired or not: an expired login is the person's to renew. */
export async function readToken(now = Date.now(), places: Places = here()): Promise<Token> {
  for (const path of authJsonPaths(places)) {
    const login = (await readJson(path))?.anthropic as Record<string, unknown> | undefined
    if (login?.type !== "oauth") continue
    const found = pick("opencode", login.access, login.expires, now)
    if (found) return found
  }
  const oauth = (await readJson(credentialsPath(places)))?.claudeAiOauth as Record<string, unknown> | undefined
  return (oauth && pick("claude", oauth.accessToken, oauth.expiresAt, now)) ?? { state: "none" }
}
