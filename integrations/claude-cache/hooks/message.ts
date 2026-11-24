// The conversation row the shared core reads: the least both hosts can give. The Claude Code
// plugin passes its `SessionMessage` (structurally this shape); the OpenCode plugin maps its own
// session context into it. Nothing here imports a host.
export type ToolUse = { tool: string; input: unknown; isError?: boolean }
export type SessionMessage = { role: string; text: string; toolUses: ToolUse[] }
