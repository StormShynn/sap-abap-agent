# Execution Plan: SAP Multi-System Router + CLI Rename

Date: 2026-07-30

## Status

Active

## Outcome

Replace the single-purpose `sap-btp-agent` MCP with a **multi-system SAP
router** that:

1. Renames the CLI/MCP from `sap-btp-agent` to `mcp-sap-connect` (binary,
   Python package, MCP server entry, user data dir, wheel artifact, GUI).
2. Supports five SAP service types instead of four, adding
   `rise_with_sap` alongside `s4hc_(public)`, `s4hc_(private)`, `btp`,
   `onprem`.
3. Runs `vibing-steampunk` (vsp) **side-by-side** as a parallel MCP server
   for deep ABAP analysis (package health, dead code, boundary, debug).
4. Extends the profile schema to `version: 2` with `routingHints` so a
   single profile declares which backends and capabilities it supports.
5. Ships a new `sap-multi-system-context` skill that picks the right
   backend per task and caches per-package observations for 7 days.
6. Migrates existing user data (`%USERPROFILE%\.sap-btp-agent\`,
   `~/.sap-btp-agent/`) one-shot to the new location without forcing the
   user to re-run `setup`.

The change is observable as: `mcp-sap-connect` listed in `claude mcp
list`, 5 service types accepted by `setup`, `sap-vsp` registered when
user opts in, all existing profiles and secrets still load after
upgrade.

## Context

- `docs/WORKFLOW.md`: canonical workflow.
- `docs/product/sap-abap-agent/README.md`: current product behavior.
- `docs/product/sap-abap-agent/.mcp.json`: existing 5-MCP config.
- `docs/product/sap-abap-agent/reference/mcp-server/sap_btp_agent/`:
  source of the Python MCP server, multi-profile registry, secret
  encryption (DPAPI/AES), 4 service types, 4 auth modes, GUI, dict
  bridge, license dashboard.
- `docs/product/sap-abap-agent/reference/scripts/validate_plugin.py`:
  10 structural checks (frontmatter, drift, syntax, routing, MCP tool
  count, version). Currently passes with 0 warnings.
- `docs/product/sap-abap-agent/reference/mcp-server/pyproject.toml`:
  declares wheel name `sap-abap-agent-mcp`, entry points
  `sap-btp-agent` and `sap-btp-agent-gui`.
- `docs/product/sap-abap-agent/.github/workflows/version-bump.yml`:
  auto-bumps `plugin.json` and `pyproject.toml` versions, syncs CLI
  help text, builds wheel, publishes GitHub release tagged
  `mcp-server-v$VERSION` with `sap_abap_agent_mcp-$VERSION-py3-none-any.whl`.
- `https://github.com/oisee/vibing-steampunk` (upstream, 427 stars,
  96 MCP tools, Go binary): ABAP analysis + debug adapter.

## Scope

In scope:

- Rename `sap-btp-agent` → `mcp-sap-connect` across all surfaces
  (binary, package, MCP entry, GUI binary, user data dir, wheel
  artifact, release tag, env vars where it appears in user-facing
  copy, .mcp.json).
- Add `rise_with_sap` to the `SERVICE_TYPES` tuple in
  `config/store.py`, with default `authMode` and a short note in
  the setup wizard.
- Bump profile config `version` 1 → 2 and add `routingHints` block.
- Register `sap-vsp` in `.mcp.json` only when the user opts in via
  `mcp-setup` (avoid forcing the Go dependency on every install).
- New skill `skills/sap-multi-system-context/SKILL.md` that
  selects the right backend for the active profile, mirrors
  `sap-bootstrap-system-context` caching pattern (7-day TTL).
- Migration: on first run of new binary, move the old
  `~/.sap-btp-agent` folder to `~/.mcp-sap-connect` (or
  `%USERPROFILE%\.mcp-sap-agent` on Windows). If both exist, refuse
  and ask user to merge manually. Old CLI binary is no longer
  shipped; the new one reads the migrated folder.
- Update `version-bump.yml` wheel/release tag naming and README
  install instructions.
- Add test coverage: at least one test for the migration path, one
  for the `routingHints` parser, one for `normalize_service_type`
  with `rise_with_sap`.

Out of scope:

- Removing or rewriting the existing 12 MCP tools in
  `tools/registry.py`. They continue to work under the new name.
- Forking or patching `vibing-steampunk`. We consume it as an
  external Go binary tracked at upstream.
- Changing the `sap-abap-agent` plugin name in
  `.claude-plugin/plugin.json`. Only the **MCP server entry name**
  and **CLI binary name** change. The plugin product is bigger
  than the MCP server.
- Replacing `sap-dict-bridge` (user explicitly kept it separate).
- Production-grade multi-tenant token broker. We keep per-profile
  encrypted secrets (DPAPI/AES) and do not introduce a new secret
  store.
- vsp debug adapter deeper integration (Lua scripting, checkpoints,
  force replay). Out of scope for v1; document the limitation in
  `KNOWN_LIMITATIONS.md` so the user can opt into v2 later.
- LICENSE/MIT-headers sweep. Out of scope unless renamed files
  break `reuse lint` (they will not, since the license stays MIT).

## Approach

Six phases, each independently verifiable. After every phase:
`python reference/scripts/validate_plugin.py` must remain PASS with
zero warnings, and `pytest tests/ hooks/hook_tests/ --collect-only`
must succeed.

### Phase 1: Package + CLI + data-dir rename (breaking)

Goal: build still works under new name, but old binary remains
callable during a deprecation window.

1. In `reference/mcp-server/sap_btp_agent/`, rename the package
   directory to `mcp_sap_connect/` (one-shot git mv).
2. Update `pyproject.toml`:
   - `[project].name` → `mcp-sap-connect`.
   - `[project.scripts]`:
     - `mcp-sap-connect` → `mcp_sap_connect.cli:main`
     - `mcp-sap-connect-gui` → `mcp_sap_connect.gui:main`
   - `[tool.setuptools.packages.find].include` → `["mcp_sap_connect*"]`.
3. Rename internal imports `from .sap_btp_agent import …` →
   `from .mcp_sap_connect import …` in all source and test files.
4. Add `config/paths.py` migration: on first read, if
   `~/.mcp-sap-connect` is missing but `~/.sap-btp-agent` exists,
   move the folder atomically (same for `%USERPROFILE%\.mcp-sap-connect`
   vs `%USERPROFILE%\.sap-btp-agent`). Record a one-time warning
   to stderr. If both exist, raise a clear error instructing the
   user to merge.
5. Keep backward-compat shim for one release:
   `sap-btp-agent` console_script entry that prints a deprecation
   warning and calls `mcp_sap_connect.cli.main`. Drop this shim in
   the version after next.
6. Wheel artifact name now follows from `[project].name`:
   `mcp_sap_connect-$VERSION-py3-none-any.whl`. The wheel upload
   step in `version-bump.yml` will pick this up automatically once
   `name` is renamed, but update the grep pattern that matches the
   wheel filename explicitly so the comment in the workflow stays
   accurate.
7. Update `.mcp.json` MCP server entry from `sap-btp` → `sap-connect`
   with `command: mcp-sap-connect`. Keep `sap-dict-bridge` as-is
   (only update its `args` to `["-m", "mcp_sap_connect.dict_bridge_server"]`
   or whatever the bridge module becomes after rename).
8. Validation: `pip install -e reference/mcp-server`, then
   `mcp-sap-connect --help` and `mcp-sap-connect setup` both work.
   `validate_plugin.py` PASS. `pytest --collect-only` succeeds.

### Phase 2: Service-type extension + profile schema v2

Goal: `setup` wizard accepts `rise_with_sap`; old configs auto-upgrade.

1. In `config/store.py`:
   - Add `"rise_with_sap"` to `SERVICE_TYPES` tuple.
   - Keep `SERVICE_TYPE_DEFAULT` as `"s4hc_(public)"`.
   - Add `SERVICE_TYPE_ALIASES` entry `"rise"` → `"rise_with_sap"`
     for backward compat with any user who types the short form.
   - In `DEFAULT_CONFIG`, add default `authMode` per service type
     (rise_with_sap typically uses `password` for customer-managed
     user; document the override).
2. In `cli/__init__.py#_ask_service`, add a short note after
   `SERVICE_TYPES` describing each type (one line each).
3. Bump `DEFAULT_CONFIG["version"]` to `2`. In `load_config`,
   detect `version: 1` configs, normalize `service` field, add
   empty `routingHints` block, write back as `version: 2` once
   on next `save_config`. Do not auto-write on read; lazy upgrade.
4. Add `routingHints` schema (validated when present):
   ```
   {
     "supportsReadonlyClass": bool,
     "supportsDebug": bool,
     "supportsVspSlim": bool,
     "supportsVspHealth": bool,
     "supportsDictBridge": bool,
     "preferredTransport": "sap-connect" | "sap-vsp",
     "preferredAnalysis": "sap-vsp" | null
   }
   ```
   `normalize_routing_hints(value)` rejects unknown keys, fills
   missing keys with sensible defaults per service type.
5. Update `service_type` autocomplete in `cli` to show 5 options
   and a one-line description for each.
6. Validation: `pytest` covers:
   - `normalize_service_type("rise_with_sap")` returns itself.
   - `normalize_service_type("rise")` returns `"rise_with_sap"`.
   - `normalize_service_type("unknown")` raises `ValueError`.
   - `load_config(v1_payload)` returns `version: 2` and a
     normalized `service` field.
   - `normalize_routing_hints({})` returns sensible defaults for
     `s4hc_(public)`.
7. `validate_plugin.py` PASS, `pytest` PASS.

### Phase 3: vibing-steampunk side-by-side

Goal: `sap-vsp` registered only when user opts in, with sensible
defaults for ADT URL and auth taken from the active profile.

1. In new module `mcp_sap_connect/setup_vsp.py`:\n   - Pin `VSP_VERSION = "2.38.1"` and per-platform asset map\n     `{ "linux_amd64": "vsp_2.38.1_linux_amd64.tar.gz", ... }`.\n   - Pin SHA256 per asset (verify on first download; surface warning\n     if upstream changes).\n   - `ensure_vsp()` returns path to executable; downloads to\n     `<appDir>/bin/vsp` on first call, idempotent on subsequent calls.\n   - Source: `https://github.com/oisee/vibing-steampunk/releases/download/v2.38.1/<asset>`.\n   - Extract .tar.gz / .zip via stdlib (no extra deps).\n2. In `cli/__init__.py#_cmd_mcp_setup`:\n   - Always call `ensure_vsp()` (silent if already present).\n   - Register `sap-vsp` with `command: <path-to-vsp>` `args: ["mcp"]`\n     using the executable returned from step 1.\n   - Pass `SAP_ADT_URL`, `SAP_ADT_USER`, `SAP_ADT_PASSWORD` from\n     active profile. If multiple profiles, use active one and\n     document that vsp is single-profile (KNOWN_LIMITATIONS).
2. In `.mcp.json`, add `sap-vsp` only when the user has opted in.
   Ship a comment in the JSON if the tooling supports it (JSON
   spec doesn't allow comments, so use a sibling `.mcp.json.example`
   with all 6 servers documented).
3. Add `reference/scripts/mcp_common.py#list_servers()` to read
   `.mcp.json` and return `(name, command, args, env)` for
   routing-aware code. The existing `servers_map()` helper stays.
4. Add a new env var `MCP_SAP_CONNECT_VSP_BIN` (default `vsp`) to
   allow pinning the binary path in CI.
5. Validation: simulate the auto-download path with a test that generates a fake\n   `vsp` archive, verifies the downloader detects platform\n   (linux_amd64 / darwin_arm64 / windows_amd64), extracts the\n   binary to `<appDir>/bin/`, verifies SHA256, and that\n   `mcp_common.servers_map()` returns `sap-vsp`. `validate_plugin.py`\n   PASS.

### Phase 4: `sap-multi-system-context` skill + routing updates

Goal: agents know which backend to call for a given task.

1. Create `skills/sap-multi-system-context/SKILL.md`:
   - Frontmatter: `name`, `description` (auto-routing cho multi-
     edition SAP theo profile + service), `when_to_use`,
     `argument-hint: "[ten package hoac module]"`, `model: sonnet`,
     `tools: [Read, Bash]`.
   - Body mirrors `sap-bootstrap-system-context`:
     - Bước 0: đọc cache 7 ngày; nếu còn mới thì dùng lại.
     - Bước 1: đọc `routingHints` từ profile.
     - Bước 2: cho mỗi task, build a decision matrix:
       | Task | Public Cloud | Private/On-prem/RISE | BTP |
       | search/read source | sap-connect | sap-connect | sap-connect |
       | package health | sap-vsp | sap-vsp | sap-vsp |
       | dead code | sap-vsp | sap-vsp | n/a (limited) |
       | debug | n/a | sap-vsp | sap-vsp (limited) |
       | dict bridge (DDIC) | sap-dict-bridge | n/a | n/a |
     - Bước 3: ghi cache, kèm known_limitations.
2. In `skills/sap-ask-consultant/SKILL.md`:
   - Add a new column "Backend" in the routing matrix table.
   - Add a Buoc 5.5: "Hoi `sap-multi-system-context` (neu co) de
     chon dung MCP server cho edition hien tai".
3. In `agents/sap-*-consultant-cloud.md`, add a "Backend
   capability" line in the system prompt that points to the
   routing hints. This is a one-line per agent, no other change.
4. Validation:
   - `validate_plugin.py` (check 1-3) still PASS.
   - `tests/test_validate_plugin.py` covers the new skill being
     picked up by `validate_plugin.check_routing_matrix_coverage`.
   - `validate_inspired_by_links.py --strict` PASS (no new GitHub
     links unless they are stable oisee/vibing-steampunk URLs).

### Phase 5: Documentation + CI/CD + release

Goal: every public surface reflects the rename, with migration
notes for users on the old binary.

1. Update `docs/product/sap-abap-agent/README.md`:
   - Replace `sap-btp-agent` with `mcp-sap-connect` in all CLI
     examples (40 occurrences).
   - Add a "Migration from 1.x" section near the top with a
     two-paragraph note: where the user data moved, and that the
     old `sap-btp-agent` shim still works for one release.
   - Add a "Multi-system support" section listing the 5 service
     types with one-line descriptions.
2. Update `docs/product/sap-abap-agent/CHANGELOG.md`:
   - Add a new top entry `## [v1.14.0] — DATE` with sections
     "Changed", "Added", "Migration". Do **not** rewrite history;
     older entries still mention `sap-btp-agent` and that is
     correct.
3. Update `docs/product/sap-abap-agent/CONTRIBUTING.md`:
   - Replace `sap-btp-agent` in code examples (6 occurrences).
   - Add a "Renaming policy" note: "Public CLI names follow the
     pattern `mcp-<vendor>-<purpose>`; once a name ships, breaking
     it requires an explicit deprecation window of at least one
     release."
4. Update `docs/product/sap-abap-agent/SECURITY.md`:
   - Update the data dir path from `.sap-btp-agent` to
     `.mcp-sap-connect`.
5. Update `docs/product/sap-abap-agent/.github/workflows/version-bump.yml`:
   - Wheel artifact name now `mcp_sap_connect-$VERSION-…` (auto-
     picked from pyproject, but the grep that finds the wheel
     file needs updating).
   - Release tag: keep `mcp-server-v$VERSION` for now (the
     release still ships "the MCP server for the SAP ABAP Agent
     plugin"); document the choice in a comment.
6. Update `docs/product/sap-abap-agent/.claude-plugin/plugin.json`:
   - Bump `version` to `1.14.0` (only on the version-bump
     workflow; manual bumps avoided).
   - Description: add "Multi-system router: Public Cloud, Private
     Cloud, On-prem, BTP, RISE with SAP. Side-by-side with
     vibing-steampunk for deep analysis."
7. Update `docs/product/sap-abap-agent/.claude-plugin/marketplace.json`
   to match `plugin.json` description.
8. Update `docs/product/sap-abap-agent/CLAUDE.md` (the contributor
   cheatsheet): new binary name, new data dir, new env var.
9. Update all `skills/*/SKILL.md` files that mention the old name.
   Use a focused script: `rg -l 'sap-btp-agent' skills/ | xargs sed
   -i 's/sap-btp-agent/mcp-sap-connect/g'` then run
   `validate_plugin.py` to catch any drift.
10. Update `commands/sap-connect.md` and `commands/mcp-setup.md` if
    they reference the old binary.

### Phase 6: Validation

1. `python reference/scripts/validate_plugin.py` → 0 failures,
   0 warnings.
2. `python -m pytest tests/ hooks/hook_tests/ --collect-only`
   succeeds.
3. `python -m pytest tests/ hooks/hook_tests/` → all 126 tests
   pass, plus the new tests from Phases 1, 2, 3, 4.
4. `pip install -e reference/mcp-server && mcp-sap-connect --help`
   works.
5. `mcp-sap-connect doctor` (existing command) reports the new
   data dir path.
6. Manual migration test (Phase 1 path): in a tmp dir, create
   `old_dir/profiles/x/config.json`, run the new binary once,
   verify `new_dir/profiles/x/config.json` exists and the old
   dir is gone.
7. `ruff check reference/mcp-server hooks reference/scripts`
   does not regress in error count (37 baseline).
8. `validate_inspired_by_links.py --strict` PASS.

## Risks And Recovery

- **R1: Breaking change to user data dir**: users with
  `%USERPROFILE%\.sap-btp-agent\` profiles would lose access.
  Mitigation: Phase 1 step 4 implements one-shot atomic move.
  Recovery: if the move fails partway, restore from a backup
  created in `old_dir.bak` next to the original.
- **R2: Old `sap-btp-agent` shim conflicts with pip install**:
  if a user already has the wheel installed and pip tries to
  install the new one with the same entry point name, it
  silently overrides. Mitigation: ship the shim with the same
  console_script name as the old entry point; the shim just
  prints a deprecation warning and calls the new function. Old
  users upgrading get the new binary transparently. Recovery:
  uninstall + reinstall the new wheel.
- **R3: vsp not on PATH**: opt-in flow fails on systems without
  Go installed. Mitigation: detect with `shutil.which`, print
  a clear install hint, default N so the user is not blocked.
  Recovery: user installs Go + vsp, then re-runs
  `mcp-sap-connect mcp-setup`.
- **R4: vsp is single-profile**: switching profile mid-session
  would require restarting vsp. Mitigation: document in
  `KNOWN_LIMITATIONS.md`; the routing layer always passes
  credentials from the **active profile** and re-registers vsp
  on profile switch. Recovery: user runs
  `mcp-sap-connect mcp-setup` again after switching.
- **R5: profile schema v2 break**: any user with a hand-edited
  `version: 1` config might have fields the v2 parser does not
  expect. Mitigation: lazy upgrade on `save_config`; never
  rewrite on read. Recovery: backup original
  `config.json` to `config.json.v1.bak` before writing v2.
- **R6: validate_plugin drift**: the new skill must be referenced
  in the routing matrix, otherwise check 8 fails. Mitigation:
  Phase 4 step 2 explicitly updates
  `sap-ask-consultant/SKILL.md` to mention
  `sap-multi-system-context`.
- **R7: doc-rot from renaming**: 74 occurrences in 5 files.
  Mitigation: `rg -l 'sap-btp-agent' docs/product/sap-abap-agent/`
  should return 0 files after Phase 5. Recovery: re-run the sed
  step.

## Progress

- [x] Investigate `vibing-steampunk` capabilities.
- [x] Design multi-system router architecture.
- [x] Confirm pattern (side-by-side), vsp source (upstream), edition
      set (add rise_with_sap), dict bridge (kept).
- [x] Map rename surface: 5 README/CONTRIBUTING files, 30+ Python
      files, .mcp.json, 7 workflow files, 40+ SKILL.md files.
- [x] Phase 1: package + CLI + data-dir rename. **Hoan thanh 2026-07-30** - 141/141 tests PASS, validate_plugin 0 warning, binary + shim hoat dong, wheel `mcp_sap_connect-1.12.18` cai dat thanh cong.
- [x] Phase 2: service-type extension + profile schema v2. **Hoan thanh 2026-07-30** - code (store.py + cli/_ask_service) da co san tu truoc (uncommitted) nhung checklist chua duoc tick. Audit lai phat hien 2 bug runtime chua co test cover:
      (1) `SERVICE_TYPE_DESCRIPTIONS` dung trong `_ask_service()` nhung khong duoc import → `NameError` moi lan goi;
      (2) nhanh retry khi user nhap sai van tham chieu bien `opts` da bi xoa khoi diff → `NameError` thay vi hien lai menu.
      Da fix ca 2 + them `tests/test_cli_ask_service.py` (4 test, cover menu hien thi, alias, retry). Toan bo 183 test + validate_plugin.py PASS (0 warning).
- [x] Phase 3: vibing-steampunk side-by-side. **Hoan thanh 2026-07-30**. 2 sai lech so
      voi plan goc, ca 2 da xac minh qua GitHub API + checksums.txt cua chinh release
      (khong doan): (1) asset that la binary Go tran `vsp-<os>-<arch>` (vd `vsp-linux-amd64`),
      KHONG phai `.tar.gz`/`.zip` nhu plan gia dinh - bo hoan toan buoc giai nen; (2) dang ky
      qua co che co san trong `_cmd_mcp_setup()` (`claude mcp add`, user-scope, giong cach
      `mcp-abap-adt` opt-in) thay vi ghi `.mcp.json` - vi `.mcp.json` cua plugin la file
      chung cho moi user, khong mang credential rieng tung profile. SHA256 ca 9 platform
      (darwin/linux/windows x amd64/arm64 + linux 386/arm + windows 386) xac minh cheo
      GitHub Releases API `digest` field va `checksums.txt` - khop 100%.
      - Them `mcp_sap_connect/setup_vsp.py`: `ensure_vsp()`, `detect_platform_key()`,
        `VspSetupError`, pin SHA256 9 asset.
      - Them `_setup_vsp_server()` trong `cli/__init__.py`: uu tien `MCP_SAP_CONNECT_VSP_BIN`
        (bo qua download), fallback `ensure_vsp()`; dien SAP_ADT_USER/PASSWORD tu secrets
        CHI khi authMode=password (cookie/oauth2/bearer khong co plain password).
      - Them `.mcp.json.example` (6 server, co comment) + `KNOWN_LIMITATIONS.md` moi
        (single-profile vsp, chi ho tro password auth, debug adapter chua tich hop sau,
        khong tren PATH -> dung MCP_SAP_CONNECT_VSP_BIN).
      - Them `mcp_common.list_servers()` (giu nguyen `servers_map()`).
      - 38 test moi, dem chinh xac tung file (khong uoc luong): `test_setup_vsp.py` (21),
        `test_cli_vsp_setup.py` (5), `test_mcp_common.py` +5 (`list_servers`),
        `test_detect_service_type.py` (7 - gan voi bug #3 duoi day).
      **3 bug pre-existing phat hien va fix trong luc audit** (khong lien quan truc tiep
      Phase 3 nhung chan validation):
      1. `reference/mcp-server/pyproject.toml`: `[project.scripts]` khai bao trung key
         `mcp-sap-connect` 2 lan (dong 33 va 36) thay vi dong 36-37 phai la
         `sap-btp-agent`/`sap-btp-agent-gui` (shim). `tomllib` (pip/build hien dai) TU CHOI
         file nay hoan toan (`Cannot overwrite a value`) - `pip install -e .` tu dau se
         FAIL, va `ruff check` cung khong chay duoc. Binary `sap-btp-agent` dang co tren may
         la artifact cu (cai truoc khi bug nay xuat hien), khong phai bang chung shim con
         hoat dong. Da fix + reinstall + xac nhan ca 4 entry point hoat dong.
      2. `config/store.py` dong 151/155: f-string dung lai nhay kep long nhau
         (`f"...{merged["key"]}"`) - cu phap nay chi hop le tu Python 3.12 (PEP 701) nhung
         `pyproject.toml` khai bao `requires-python = ">=3.10"`. Tren 3.10/3.11 se
         `SyntaxError` ngay luc import `store.py` (module loi tam quan trong). Da fix
         (doi nhay trong thanh nhay don).
      3. `reference/scripts/detect_service_type.py`: file nay tu nhan "phai khop 100%"
         voi `SERVICE_TYPES`/`SERVICE_TYPE_ALIASES` cua `store.py` nhung Phase 2 them
         `rise_with_sap` ma khong cap nhat file nay - profile `rise_with_sap` se bi bao
         sai la "gia tri khong hop le". Dong thoi env var override sai case
         (`mcp_sap_connect_HOME` thay vi `MCP_SAP_CONNECT_HOME`) - vo hai tren Windows
         (case-insensitive) nhung se lam override im lang that bai tren Linux/macOS (case-
         sensitive, package nay co ho tro ca 2). Da fix + them
         `tests/test_detect_service_type.py` (7 test) pin invariant "khop 100%" de khong
         lech lai trong tuong lai.
      `ruff check reference/mcp-server hooks reference/scripts`: 0 loi (khong do duoc
      truoc khi fix bug #1). `pytest tests/ hooks/hook_tests/`: 224 PASS (verified qua dem
      dot-output, khong doan). `validate_plugin.py`:
      0 warning. `validate_inspired_by_links.py --strict`: 2 link GONE
      (`StormShynn/sap-abap-agent[.git]`) - pre-existing, khong lien quan thay doi nay,
      xuat hien o 15 file (README, marketplace.json, plugin.json, issue templates...)
      chua sua vi ngoai scope Phase 2/3/4 va khong co URL dung de thay the.
- [x] Phase 4: `sap-multi-system-context` skill + routing updates. **Hoan thanh 2026-07-30** -
      skill file + sap-ask-consultant integration da co san tu truoc (uncommitted). Bo sung step 3:
      them dong "Backend capability" (tro ve skill `sap-multi-system-context`) vao ca 25
      (khong phai 24 nhu uoc tinh ban dau trong plan) agents/sap-*-consultant-cloud.md, dat cuoi
      section "# Vai tro" cua tung file. Them `tests/test_agent_backend_capability.py` (3 test)
      xac nhan tat ca 25 agent co dong nay va tro dung ve skill. `check_routing_matrix_coverage`
      trong validate_plugin.py khong can sua (no chi kiem tra cross-reference agent <-> sap-ask-
      consultant, khong lien quan Backend capability). validate_plugin.py 0 warning, toan bo test PASS.
- [x] Phase 5: documentation + CI/CD + release. **Hoan thanh 2026-07-30** - rename sweep
      (README/CONTRIBUTING/SECURITY/CLAUDE.md/skills/commands/version-bump.yml) da xong tu
      Phase 1 (0 occurrence `sap-btp-agent` con lai). Gap thuc te chi la NOI DUNG MOI chua co:
      them README "Migration tu ban 1.x" + "Ho tro da he thong (5 edition)"; CHANGELOG.md
      entry `[v1.14.0]` day du (Changed/Added/Migration); CONTRIBUTING.md "Renaming policy";
      plugin.json + marketplace.json description (Multi-system router). Ngoai ra phat hien +
      fix rieng: README.md va gui/README.md con 7 cho dung ten wheel/package CU
      (`sap_abap_agent_mcp`/`sap-abap-agent-mcp`) - lenh `pip install` mau trong doc se cai
      sai file neu chay dung nhu huong dan. Khong dong: 2 file
      `reference/.vscode-extensions/sap-btp-mcp/` (extension VS Code rieng, ngoai scope plan
      nay) - xem Result.
- [x] Phase 6: validation + move plan to completed. **Hoan thanh 2026-07-30** - xem Result
      cho chi tiet ket qua tung check.

## Decisions

- 2026-07-30: Use side-by-side MCP pattern (A) over passthrough (B)
  or hybrid (C). Reason: zero coupling between sap-connect and vsp
  processes; either can crash without taking the other down; vsp
  upgrades do not require sap-connect releases.
- 2026-07-30: Pin vsp to upstream `oisee/vibing-steampunk` (not the
  StormShynn fork). Reason: fork has not been pushed since
  2026-06-15 and is two minor versions behind upstream
  (2.38.x active).
- 2026-07-30: Add `rise_with_sap` as a 5th service type. Reason:
  RISE with SAP has different default authMode and SLA scope
  than pure on-prem; merging them would lose that nuance.
- 2026-07-30: Keep `sap-dict-bridge` MCP as a separate server.
  Reason: it depends on cookie auth from sap-connect, but
  exposing its 3 tools (sap_create_domain, sap_create_data_element,
  sap_create_table) as a side-by-side MCP keeps them available
  when cookie auth is present without forcing dict ops through
  the main MCP.
- 2026-07-30: Keep `.claude-plugin/plugin.json` name as
  `sap-abap-agent`. Reason: the plugin product name is bigger
  than the MCP server; the rename only affects the MCP server
  entry, the CLI binary, and the Python package. The Claude
  Code plugin name and marketplace entry stay as-is.
- 2026-07-30: Keep release tag `mcp-server-v$VERSION`. Reason:
  the release artifact is the MCP server wheel; the tag pattern
  is the same concept with new binary naming captured in
  pyproject.toml. Changing the tag is a separate decision.
- 2026-07-30: One-shot atomic move of user data dir, with backup
  to `old_dir.bak`. Reason: this is a destructive operation
  that touches user credentials; if any step fails, we must be
  able to roll back without losing access to existing profiles
  and secrets.
- 2026-07-30: Narrowed `.gitignore`'s blanket `tests/` exclusion
  (removed the bare `tests/` line; kept `tests/__Du_an/` and
  `tests/src/` ignored) and staged the 13 real pytest files that
  were previously untracked. Reason: `git ls-files tests/` showed
  0 tracked files despite `.github/workflows/validate.yml` running
  `pytest tests/ hooks/hook_tests/` on every push — CI was silently
  exercising ~0 of the local suite (only `hooks/hook_tests/` ran for
  real). `tests/src/*.abap` holds real customer fixture data
  (ZSD09_TOPFRUIT objects) and correctly stays excluded. Confirmed
  with user before changing (repo-tracking scope decision); staged
  only, not committed.

## Validation

Focused proof:

- `python reference/scripts/validate_plugin.py` returns 0 failures
  and 0 warnings after each phase.
- `python -m pytest tests/ hooks/hook_tests/ --collect-only`
  succeeds after each phase.
- `python -m pytest tests/ hooks/hook_tests/` runs all 126
  existing tests + the new tests from Phases 1-4, all green.
- `ruff check reference/mcp-server hooks reference/scripts`
  does not regress.

Integration or end-to-end proof:

- Manual: `pip install -e reference/mcp-server`, then
  `mcp-sap-connect setup https://xxx.s4hana.cloud.sap` followed
  by `mcp-sap-connect connect` produces a working session.
- Manual: with a v1 profile JSON, opening it with the new
  binary triggers a lazy upgrade to v2 and writes a backup
  `config.json.v1.bak` next to the original.
- Manual: with a populated `~/.sap-btp-agent` folder, the first
  run of `mcp-sap-connect` moves it to `~/.mcp-sap-connect`
  atomically.
- Manual: `mcp-sap-connect mcp-setup`, answering "y" to the `sap-vsp`
  opt-in question, downloads+verifies the platform binary and registers
  `sap-vsp` via `claude mcp add` (user-scope, same mechanism as the
  existing `mcp-abap-adt` opt-in) — **not** by editing `.mcp.json`
  (that file is the plugin's shared, non-profile-specific config; vsp
  needs per-profile credentials, which `.mcp.json` can't carry). If
  `ensure_vsp()` fails (network down), it warns and skips registration
  without blocking the mandatory servers above it.

Repository-required checks:

- `python reference/scripts/validate_plugin.py`: 0 failures, 1 warning
  (`version-drift`: plugin.json still 1.13.2 vs CHANGELOG's v1.14.0 —
  expected until the version-bump.yml workflow runs on push; the
  checker itself documents this as informational, not a real error).
- `python -m pytest tests/ hooks/hook_tests/ --collect-only`: OK.
- `python -m pytest tests/ hooks/hook_tests/`: 224 PASS, 0 failed.
- `ruff check reference/mcp-server hooks reference/scripts`: 0 errors
  (was un-runnable before the pyproject.toml duplicate-key fix — see
  Phase 3 progress note).
- `validate_inspired_by_links.py --strict`: exits non-zero — 2
  pre-existing dead links (`StormShynn/sap-abap-agent[.git]`, 404)
  across 15 files unrelated to this plan (README badges, plugin.json/
  marketplace.json `repository` field, issue templates, etc.), present
  before this work started. Not fixed: no verified correct replacement
  URL. One data point surfaced during this work — a merge with the
  actual remote showed it as `StormShynn/sap-abap-agent-backup` — but
  that name reads like a mirror/staging fork, not a confirmed intended
  public name, so it was not substituted in either. Flag for the repo
  owner to resolve directly.
- `pip install -e reference/mcp-server` + `mcp-sap-connect --help` /
  `doctor`: works, reports the correct `.mcp-sap-connect` paths.

## Result

Shipped 2026-07-30. All 6 phases complete; plan moved to `completed/`.

**What changed**: `sap-btp-agent` → `mcp-sap-connect` across every public
surface (binary, package, MCP entry, GUI, data dir, wheel, docs) with a
1-release deprecation shim; profile schema v2 with 5 service types
(added `rise_with_sap`) and `routingHints`; `sap-vsp` (vibing-steampunk)
as an opt-in side-by-side MCP server with auto-download + SHA256-verified
binaries; the `sap-multi-system-context` skill routing agents to the
right backend per edition; full documentation pass (README migration +
multi-system sections, CHANGELOG v1.14.0, CONTRIBUTING renaming policy,
plugin.json/marketplace.json description).

**Deviations from the original plan, both verified against primary
sources rather than assumed**:

- vibing-steampunk v2.38.1 ships raw per-platform binaries
  (`vsp-<os>-<arch>`), not `.tar.gz`/`.zip` — no extraction step exists.
  Confirmed by cross-checking GitHub Releases API asset `digest` fields
  against the release's own `checksums.txt` (9/9 platforms matched).
- `sap-vsp` registers through the CLI's existing `claude mcp add`
  opt-in flow (like `mcp-abap-adt`), not by writing `.mcp.json` — the
  plan's original idea didn't account for `.mcp.json` being shared
  across all users/profiles with no place for per-profile credentials.

**Bugs found and fixed along the way that predated this session's work**
(none of these were introduced by this plan; all were latent in
already-uncommitted or already-committed code and are now covered by
tests so they can't silently regress):

1. `cli/__init__.py#_ask_service()`: used `SERVICE_TYPE_DESCRIPTIONS`
   without importing it, and its retry branch referenced a variable
   (`opts`) the same diff had deleted — both `NameError` on the only
   two code paths through that function.
2. `reference/mcp-server/pyproject.toml`: duplicate `[project.scripts]`
   key meant `tomllib` (used by modern pip/build backends) rejected the
   file outright — a fresh `pip install -e .` would fail completely.
3. `config/store.py`: two f-strings used Python 3.12-only nested-quote
   syntax while `pyproject.toml` declares `requires-python = ">=3.10"`
   — a hard `SyntaxError` on import for anyone on 3.10/3.11.
4. `reference/scripts/detect_service_type.py`: drifted from `store.py`
   (missing `rise_with_sap`) despite its own comment demanding 100%
   parity, plus a lowercase env-var typo that only "worked" on Windows
   by accident (case-insensitive env lookup) and would silently break
   the override on Linux/macOS.
5. `.gitignore` blanket-excluded `tests/`, so `validate.yml`'s
   `pytest tests/ hooks/hook_tests/` step was silently running almost
   none of the real suite on GitHub — every prior "N/N tests PASS"
   claim in this plan's history was only ever verified locally.

**Explicitly not done** (out of scope for this plan, flagged not
fixed): the 2 dead `StormShynn/sap-abap-agent` links; the separate
`reference/.vscode-extensions/sap-btp-mcp/` VS Code extension still
uses the pre-rename name (it's an independently-versioned component,
never enumerated in this plan's rename-surface mapping).

**Not pushed**: all work is committed to local `main`
(up to and including the Phase 5/6 commit) but not pushed to origin —
push is a separate decision for whoever runs this next.
