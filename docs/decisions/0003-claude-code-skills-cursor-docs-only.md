# 0003 Claude Code owns skills; Cursor is MCP docs-only

Date: 2026-08-02

## Status

Accepted

## Context

`sap-abap-agent` ships Claude Code plugin surfaces (skills, agents, SessionStart
hooks, slash commands). Cursor and VS Code can use the same MCP servers
(`mcp-sap-connect`, dict-bridge, research servers) but do not run Claude Code
hooks or `/plugin install`. The maturity plan needed an explicit host policy
so work does not silently expand into a second skill pack.

User decision (2026-08-02): build and maintain skills for Claude Code only.

## Decision

1. **Skills, agents, hooks, and plugin marketplace remain Claude Code–primary.**
2. **Cursor / VS Code:** document MCP registration and presets only (docs-only).
   Do not port or maintain a parallel Cursor rules/skills pack unless a future
   decision supersedes this one.
3. Onboarding and README must state the host matrix without claiming hook or
   skill-routing parity on Cursor.

## Alternatives Considered

1. Port rules/skills to Cursor (`.cursor/rules` / Agent Skills) for near-parity
   — rejected for now (duplicate maintenance, sync drift).
2. Drop Cursor mentions entirely — rejected; MCP already works and users ask.

## Consequences

Positive:

- Single skill authority (Claude Code plugin tree under product repo).
- Maturity polish stays focused on GUI signing, verification gates, MCP UX.

Tradeoffs:

- Cursor users get tools without automatic routing/verification discipline.
- Future Cursor-first teams need a new decision before investing in a pack.

## Follow-Up

- P0.2 in `docs/plans/active/sap-abap-agent-maturity-polish.md`: expand
  onboarding host matrix to match this decision.
- Close the open ABC-roadmap note (“Cursor skill pack vs templates only”).
