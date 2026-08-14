# Execution Plan: Skill Consolidation (Phase 1 — low-risk relocation)

Date: 2026-07-31

## Status

Completed

## Outcome

Reduce the global, auto-discovered `skills/` count in `docs/product/sap-abap-agent`
from 45 to 38 by relocating 7 skills into the `reference/` tiers that already
exist for exactly this purpose (`reference/mcp-guides/`, `reference/process/`,
and folding into an existing `reference/modules/` owner) — mirroring the
pattern the 2026-07-14 audit (`docs/audits/2026-Q3-skill-rationalization.md`)
already validated for `mcp-sap-adt`/`mcp-sap-gui`/`mcp-sap-successfactors` and
`sap-context-module-routing`/`sap-context-tool-result-trim`/
`sap-scaffold-context-summary`. No skill's *capability* is removed — each
becomes reachable the same way those six already are: read on demand by the
skill/agent whose prose names it, instead of auto-discovered globally.

The change is observable as: `skills/` contains 38 directories (down from 45,
excluding the `sap-user-skills` placeholder), `validate_plugin.py` and
`pytest` remain green, `index.html`'s "45 skills" claim is updated to match,
and every prose reference to the 7 moved names still resolves (either as a
path readers can open, or — where an agent/skill still legitimately declares
it by name — via `skill_exists()`'s existing 4-path resolution).

## Context

- User request: review the full skill set (45 in `skills/`, felt like "too
  many"), identify a lean "main" set, and push the rest into the existing
  hide-but-linked mechanism rather than deleting capability.
- `docs/product/sap-abap-agent/docs/audits/2026-Q3-skill-rationalization.md`
  (2026-07-14): prior audit of the same problem. Executed several merges
  (BAdI 3-way, `sapui5-fiori`→`sap-fiori-cloud`, `mcp-sap-adt/gui/
  successfactors`→`reference/mcp-guides/`, 3 process skills→
  `reference/process/`). Left 2 items explicitly un-executed pending
  confirmation: the BTP best-practices/connectivity overlap, and a shared
  CData MCP install template (the template — `reference/mcp-guides/
  mcp-sap-cdata-setup.md` — was in fact written since, but `mcp-sap-concur`/
  `mcp-sap-fieldglass` were never switched to point at it as their primary
  install doc; only `mcp-sap-successfactors.md` uses it today).
- `docs/product/sap-abap-agent/SKILL_TEMPLATE.md:46`: `description`+
  `when_to_use` share a hard 1,536-char budget per skill, plus one combined
  budget across the whole skill list — concrete mechanism behind "too many
  skills degrades all of them", not just a feeling.
- `docs/product/sap-abap-agent/reference/scripts/validate_plugin.py`:
  `skill_exists()` (line 95) already resolves 4 paths (`skills/`,
  `reference/modules/`, `reference/mcp-guides/`, `reference/process/`) — the
  July-14 TODO to teach the validator about the new categories is already
  done. `check_agent_frontmatter()` requires every name an agent declares in
  its `skills:` frontmatter to resolve via `skill_exists()`, and separately
  warns (does not fail) if an agent's body mentions a `skills/`- or
  `reference/modules/`-known name that isn't declared and doesn't read like a
  dispatch mention.
- Verified directly (not assumed) before starting:
  - `reference/modules/sap-btp-connectivity/SKILL.md` already exists as a
    **separate, pre-existing "knowledge note"** (not tied to any agent's
    `skills:` list, referenced by name from 8 other `reference/modules/*`
    integration docs as "BTP architecture: `sap-btp-connectivity`") —
    genuinely different content from `skills/sap-btp-connectivity/SKILL.md`,
    despite the identical `name:` in frontmatter. This is a 3-way naming
    collision the 2026-07-14 audit did not catch.
  - `tests/test_skill_multi_system_context.py` hard-codes
    `ROOT / "skills" / "sap-multi-system-context"` and asserts
    skill-specific frontmatter fields (`tools`, `argument-hint`, `effort`,
    `model: sonnet`) — moving this file requires rewriting this test, not
    just editing a path.
  - `tests/test_agent_backend_capability.py` only asserts the literal
    substring `"sap-multi-system-context"` appears in each of the 25
    `sap-*-consultant-cloud.md` agents — safe across the move as long as the
    updated prose still contains that string (it will, via the new path).
  - `reference/scripts/mcp_inventory.json` has a **pre-existing path bug**
    unrelated to this plan: the `sap-fieldglass` entry's `doc` field says
    `skills/sap-fieldglass/SKILL.md`, but the real directory is
    `skills/mcp-sap-fieldglass/` (confirmed via directory listing). Will fix
    while touching this file for the move.
  - `validate_plugin.py` currently passes with 1 pre-existing, unrelated
    warning (`version-drift`: `plugin.json` 1.13.3 vs CHANGELOG 1.14.0 — the
    router plan's own note says this clears itself on next CI push).
  - `index.html` already correctly says "45 skills" (3 places + 1 tree
    comment) — `CLAUDE.md`'s "43 skills" is the only stale count, unrelated
    to this plan's moves (predates the last 2 skills added).

## Scope

In scope (7 skills relocated, 0 deleted in substance):

- `skills/sap-multi-system-context/SKILL.md` → `reference/process/
  sap-multi-system-context.md`. Still invoked the same way (by name, from
  `sap-ask-consultant` step 5.5, `sap-routing-discipline`, `sap-deployment-
  target`, `sap-bootstrap-system-context`) — those already treat it as a
  named sub-step, not something the user types first.
- `skills/sap-service-type-context/SKILL.md` → `reference/process/
  sap-service-type-context.md`. Same reasoning (`sap-routing-discipline` R9,
  `sap-ask-consultant`, `sap-extensibility`, `sap-clean-code`, `sap-abap-sql`
  already call it by name as a pre-step).
- `skills/mcp-sap-notes/SKILL.md` → `reference/mcp-guides/mcp-sap-notes.md`
  (same shape as the already-moved `mcp-sap-adt`/`mcp-sap-gui`/
  `mcp-sap-successfactors`: read once at setup time, not a business trigger).
- `skills/mcp-sap-concur/SKILL.md` → `reference/mcp-guides/mcp-sap-concur.md`,
  trimmed to product-specific content (entities, sample queries), pointing at
  the existing shared `mcp-sap-cdata-setup.md` for the generic install steps
  — same pattern `mcp-sap-successfactors.md` already uses for its CData
  option.
- `skills/mcp-sap-fieldglass/SKILL.md` → `reference/mcp-guides/
  mcp-sap-fieldglass.md`, same treatment.
- `skills/sap-btp-connectivity/SKILL.md` → merged into the pre-existing
  `reference/modules/sap-btp-connectivity/SKILL.md` knowledge note (adds this
  skill's stronger destination-JSON examples, auth-type table, and
  troubleshooting table; the knowledge note's CF-binding/env-var/best-practice
  content is not duplicated elsewhere and is kept). Source skill file
  deleted; the 8 existing "BTP architecture: `sap-btp-connectivity`"
  pointers elsewhere need no change since that name still resolves at the
  same path.
- `skills/sap-btp-best-practices/SKILL.md` → folded into `reference/modules/
  sap-btp-admin-cloud/deep/SKILL.md` as new sections (account structure,
  naming conventions, performance & cost, app-router config); overlapping
  parts (XSUAA security, CI/CD) merged rather than duplicated. Source skill
  file deleted.
- Frontmatter `skills:` list edits in the 4 agents that declare the 2 BTP
  skills by name (`sap-btp-admin-consultant-cloud`, `sap-cap-consultant-
  cloud`, `sap-cpi-consultant-cloud`, `sap-fiori-consultant-cloud`) — remove
  the now-nonexistent names, matching how the already-moved MCP guides were
  handled in `sap-docs-researcher.md`.
- `tests/test_skill_multi_system_context.py` rewritten to test the new
  `reference/process/sap-multi-system-context.md` location and content
  (drop the skill-frontmatter-specific assertions that no longer apply).
- Global count updates: `CLAUDE.md` skill count, `index.html` (4 lines),
  `README.md` skill-tree comment.
- One new CHANGELOG entry (not editing old entries — same convention the
  router plan itself followed) and one new audit file
  (`docs/audits/2026-Q3-skill-consolidation-part2.md`), matching this
  repo's own "append, don't rewrite" audit convention.

Out of scope (explicitly deferred, not decided yet):

- Consolidating the "technical knowledge" skills (`sap-abap-sql`,
  `sap-authorization`, `sap-rap-events`, `sap-released-classes`,
  `sap-badi-enhancement`, `sap-key-user-toolkit`, `sap-odata-service`) into
  fewer hub files. User asked for this to be *investigated* separately
  before any edit, given the higher risk (these are declared in most of the
  25 module-consultant agents' frontmatter, and cramming multiple topics
  into one `description` risks hitting the same 1,536-char budget faster).
  Tracked as a follow-up research task in this session, not this plan.
- Any change to the MCP server rename/router work from `docs/plans/
  completed/sap-multi-system-router.md` — unrelated, already shipped
  (v1.14.0).
- Writing a truly shared CData MCP template beyond what already exists at
  `mcp-sap-guides/mcp-sap-cdata-setup.md` — reusing it, not redesigning it.

## Approach

Four independently-verifiable groups, in this order (least to most
content-editing effort):

1. **`reference/process/` group** (multi-system-context, service-type-context):
   move file, strip skill-style frontmatter (these become plain `.md` like
   `sap-context-module-routing.md`), rewrite the dedicated test file, fix
   prose in `sap-ask-consultant`, `sap-routing-discipline`, `sap-deployment-
   target`, `sap-bootstrap-system-context`, `sap-extensibility`,
   `sap-clean-code`, `sap-abap-sql`, `README.md`, and bulk-fix the 25
   identical "Backend capability" agent lines with one script pass (all 25
   are byte-identical today, confirmed by grep).
2. **`reference/mcp-guides/` group** (notes, concur, fieldglass): move +
   reformat, update `sap-docs-researcher.md` (frontmatter + body sentence,
   matching how gui/adt/successfactors are already phrased there), update
   `mcp_inventory.json` (3 doc paths, including the pre-existing fieldglass
   typo), update `mcp-sap-cdata-setup.md`'s own "used at" header line,
   update `README.md` skill-tree comment.
3. **BTP merge group** (best-practices, connectivity): content merge (not
   mechanical move) into the two existing reference homes, frontmatter edits
   in 4 agents, update `sap-btp-admin-cloud/deep/SKILL.md` §3 pointer and the
   knowledge note's stale self-referential line.
4. **Global counts + records**: `CLAUDE.md`, `index.html` (4 spots),
   `README.md` tree, new CHANGELOG entry, new audit file + audits/README.md
   index row.

After each group: `python reference/scripts/validate_plugin.py` must stay at
0 failures (warnings tracked, not required to be 0 given the pre-existing
version-drift one). After all groups: full `pytest tests/
hooks/hook_tests/`.

## Risks And Recovery

- **R1: bulk sed across 25 agent files touches the wrong line.** Mitigation:
  the exact line was confirmed byte-identical across all 25 files via grep
  before writing the replacement command; dry-run the match count first
  (expect exactly 25) before writing.
- **R2: BTP content merge silently drops something.** Mitigation: full
  content of all 3 source files (`skills/sap-btp-connectivity`,
  `skills/sap-btp-best-practices`, `reference/modules/sap-btp-connectivity`)
  was read in full before drafting the merge, not summarized/assumed.
- **R3: removing a name from an agent's frontmatter `skills:` list breaks
  something depending on the declaration itself (not just the resolution).**
  Mitigation: `check_agent_frontmatter()` is the only consumer of that field
  found via repo-wide grep; it only validates resolution, doesn't gate
  runtime behavior. No other script parses `skills:` besides this validator
  (confirmed by grep for `skills:` parsing logic outside `validate_plugin.py`).
- **R4: test rewrite for `test_skill_multi_system_context.py` loses
  coverage.** Mitigation: keep equivalent assertions (5 editions, 3 backends,
  7 routingHints keys, 7-day cache mention) against the new path; only drop
  assertions that were about skill-specific frontmatter fields that
  correctly no longer apply to a plain reference doc.
- **Recovery**: every step is a file move/edit inside a git working tree with
  no destructive git operation involved; `git diff`/`git status` at any point
  shows the exact delta, and nothing is pushed. If a group fails validation,
  fix forward within that group before starting the next one.

## Progress

- [x] Group 1: `reference/process/` relocation (multi-system-context,
      service-type-context) + test rewrite + prose fixes. **Hoan thanh
      2026-07-31.**
- [x] Group 2: `reference/mcp-guides/` relocation (notes, concur, fieldglass)
      + sap-docs-researcher.md + mcp_inventory.json + cdata-setup.md.
      **Hoan thanh 2026-07-31** — also fixed a pre-existing path bug in
      `mcp_inventory.json` (`sap-fieldglass` entry pointed at the wrong
      directory name, unrelated to this plan but touched anyway).
- [x] Group 3: BTP merge (best-practices, connectivity) + agents'
      frontmatter. **Hoan thanh 2026-07-31** — turned out to need only 3
      agent frontmatter edits, not 4: `sap-btp-connectivity` kept resolving
      via the pre-existing `reference/modules/sap-btp-connectivity/`
      knowledge note (a 3-way naming collision the 2026-07-14 audit never
      caught), so only `sap-btp-best-practices` needed removing from
      declared `skills:` lists (btp-admin, cap, cpi — fiori never declared
      it). CORE file's route map updated in place to keep the 30-line
      budget `check_core_deep_size()` enforces.
- [x] Group 4: global counts (CLAUDE.md, index.html, README.md) + CHANGELOG
      + new audit file. **Hoan thanh 2026-07-31** — also fixed 6 stale
      per-skill path references inside `index.html`'s documentation
      sections (beyond the count itself) since they'd otherwise point at
      deleted paths.
- [x] Full validation: `validate_plugin.py` + `pytest tests/
      hooks/hook_tests/`. **Hoan thanh 2026-07-31** — 0 failures, 1
      pre-existing unrelated warning (version-drift); 221/221 tests pass
      (224 baseline − 3 net from rewriting `test_skill_multi_system_context.py`
      with fewer, more accurate assertions).

## Decisions

- 2026-07-31: Relocate rather than delete — every moved skill's capability
  is preserved, only its auto-discovery scope changes. Reason: user
  explicitly asked to keep the "link between skills" so a main skill still
  pulls in the related one; deleting would lose that.
- 2026-07-31: Reuse the pre-existing `reference/modules/sap-btp-connectivity`
  knowledge note as the BTP-connectivity merge target instead of folding
  into `sap-btp-admin-cloud/deep/` directly. Reason: 8 other
  `reference/modules/*-integration/SKILL.md` files already point at that
  exact name/path for "BTP architecture" — reusing it means those 8 files
  need zero edits, versus redirecting all 8 if the merge target were
  elsewhere.
- 2026-07-31: Leave the "technical knowledge" skill group (`sap-abap-sql`
  and siblings) untouched pending separate research, per explicit user
  request to see a concrete proposal before any edit there.

## Validation

- Focused proof: `python reference/scripts/validate_plugin.py` after each
  group (0 failures each time).
- Integration proof: `python -m pytest tests/ hooks/hook_tests/` after all
  groups (all green, including the rewritten
  `test_skill_multi_system_context.py`).
- Repository-required checks: same two commands, run once more at the end
  as the final gate before moving this plan to `docs/plans/completed/`.

## Result

Shipped 2026-07-31. `skills/` went from 45 to 38 (real count, excluding the
`sap-user-skills` placeholder) with zero loss of capability — every relocated
skill is still reachable the same way the six already-relocated ones
(`mcp-sap-adt`/`mcp-sap-gui`/`mcp-sap-successfactors`/
`sap-context-module-routing`/`sap-context-tool-result-trim`/
`sap-scaffold-context-summary`) have been since 2026-07-14.

**What changed**: 7 skills relocated (2 to `reference/process/`, 3 to
`reference/mcp-guides/`, 2 merged into existing `reference/modules/` files);
3 agents' frontmatter cleaned up; 1 test file rewritten; ~40 individual prose
cross-references fixed across skills, agents, README.md, index.html (incl.
6 stale per-skill doc-path mentions), and `mcp_inventory.json`; global skill
counts corrected in `CLAUDE.md` and `index.html`; one CHANGELOG entry
(v1.14.1) and one new audit file added, following this repo's own
"append, don't rewrite" convention for both.

**Deviations from the plan, both verified rather than assumed**:

- `reference/modules/sap-btp-connectivity/SKILL.md` already existed as a
  separate "knowledge note" under the identical name before this plan
  started — a 3-way naming collision with `skills/sap-btp-connectivity/`
  that the 2026-07-14 audit never caught. Reusing it as the merge target
  meant the 8 other `reference/modules/*-integration/SKILL.md` files that
  already pointed at that name needed zero edits, and only 3 agents (not 4)
  needed frontmatter changes — `sap-btp-connectivity` kept resolving via
  `skill_exists()`'s `reference/modules/` path with no declaration change
  needed.
- The 2026-07-14 audit's own status header claimed the BTP best-practices/
  connectivity overlap was already merged. Direct verification (reading both
  files in full) showed this was only a partial dedup (one paragraph
  redirected, both files otherwise still full and separate) — the actual
  merge happens in this plan.

**Bugs found and fixed along the way that predated this session's work**
(none introduced by this plan, both now corrected):

1. `reference/scripts/mcp_inventory.json`: the `sap-fieldglass` entry's `doc`
   field pointed at `skills/sap-fieldglass/SKILL.md`, but the real directory
   was always `skills/mcp-sap-fieldglass/` (missing the `mcp-` prefix).
2. `CLAUDE.md` claimed "43 skills" while the real pre-existing count (before
   any change in this plan) was 45 — stale since the 2 most recent skill
   additions (`sap-security-review`, `sap-package-backup`) were never
   reflected there. `index.html`'s count was already correct at 45.

**Explicitly not done** (out of scope for this plan, tracked separately):
consolidating the "technical knowledge" skill group (`sap-abap-sql` and
6 siblings) — flagged by the user as higher-risk and requiring a concrete
proposal before any edit; being researched as a follow-up in the same
conversation, not this plan.

**Validation**: `python reference/scripts/validate_plugin.py` → 0 failures,
1 pre-existing unrelated warning (version-drift, self-documented as
non-blocking). `python -m pytest tests/ hooks/hook_tests/` → 221 passed,
0 failed.

**Not committed**: all changes are staged/modified in the working tree
(confirmed via `git status`) but not committed — committing is a separate
decision for the user.
