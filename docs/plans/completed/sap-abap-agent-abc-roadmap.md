# Execution Plan: SAP ABAP Agent — Roadmap A+B+C

Date: 2026-08-01

## Status

Completed

## Outcome

Sau khi hoàn tất, một user mới (consultant hoặc ABAP dev) có thể:

1. **A — Stabilize:** cài/đọc docs khớp đúng bản **1.18.0** (plugin + wheel + badge), không còn conflict git / drift version, pytest CI thu thập và chạy test thật.
2. **B — Ship GUI:** tải **1 installer Windows** (MSI hoặc NSIS từ Tauri) → mở app → add profile → ping/reauth/connect → đăng ký MCP core **không cần gõ terminal** cho happy path.
3. **C — Onboarding personas:** có **1 trang onboarding** phân 3 persona (ABAP Dev / Functional / Key user) là đường happy-path; README monolith không còn là tài liệu cài đặt chính.

Workspace Harness (`harness_sap_abap_agent`) giữ plan/decisions; product truth nằm ở `docs/product/sap-abap-agent/` (nested git repo).

## Context

- Đánh giá: canvas `sap-abap-agent-project-review` (2026-08-01).
- Product: `docs/product/sap-abap-agent/` — plugin `1.18.0`, HEAD quan sát `a36025b`, branch `main` **ahead 1 / behind 1**, `CHANGELOG.md` **UU**.
- Drift đã quan sát:
  - `.claude-plugin/plugin.json` + `reference/mcp-server/pyproject.toml` = `1.18.0`
  - `README.md` badge = `1.12.0`; pip example = wheel `1.14.0`; sample JSON `plugin_version` = `1.12.0`
- GUI:
  - Tkinter: `mcp_sap_connect.gui` via pip extra `[gui]`
  - Native: `gui-native/` Tauri v2, package version `0.1.0`, **chưa có release build** trong tree
- Architecture GUI đúng hướng: Rust UI gọi `mcp-sap-connect … --json` (không rewrite auth).
- Workflow: `docs/WORKFLOW.md` — plan durable cho work đa session.
- Known limits: `docs/product/sap-abap-agent/KNOWN_LIMITATIONS.md` (SAML MFA, vsp single-profile) — **không** nằm trong A+B+C trừ khi chặn ship.

## Scope

In scope:

- **Phase A:** resolve merge conflict; sync mọi user-facing version string về `1.18.0` (hoặc version hiện tại sau bump nếu CI đã vượt); chạy/ghi nhận pytest root + mcp-server; sửa CI nếu vẫn ignore tests; cập nhật CHANGELOG nếu cần mục “docs sync”.
- **Phase B:** hoàn thiện `gui-native` đủ ship Windows (bundle targets, version align với product, doctor/first-run tối thiểu, artifact MSI/NSIS trên GitHub Release hoặc script build có chứng minh); deprecate path Tkinter (docs + timeline, không xóa code ngay trong B nếu còn user).
- **Phase C:** viết `docs/onboarding-guide.md` (hoặc thay thế) theo 3 persona; rút README “Cài đặt” xuống link + 5–10 dòng; preset MCP “Core only” vs “Full research” mô tả trong onboarding + GUI panel nếu đã có.

Out of scope (session này / plan này):

- SaaS multi-tenant secret broker.
- Deep integrate vsp debug adapter / cookie jar sharing (KNOWN_LIMITATIONS).
- Rewrite toàn bộ 41 skills.
- macOS/Linux native installer (Windows first; document follow-up).
- Thay thế Claude Code plugin bằng Cursor-native plugin đầy đủ (Phase B/C chỉ **templates MCP + hướng dẫn Cursor**, không port hooks Claude).

## Approach

Thứ tự cứng (không song song A với B khi conflict chưa xong):

```text
A Stabilize  →  B Ship GUI Windows  →  C Onboarding personas
     │                    │                      │
     └─ proof: pytest     └─ proof: MSI chạy    └─ proof: walkthrough
        + docs sync            + MCP register         3 persona
```

### Phase A — Stabilize (session 1, ~1–2h)

1. Trong product git: `git status`, xem conflict markers `CHANGELOG.md`.
2. Merge/rebase với `origin/main` an toàn (không force); giữ entry `v1.18.0` đầy đủ.
3. Sync strings:
   - `README.md` badge, pip wheel URL/examples, sample `plugin_version`
   - `docs/onboarding-guide.md` nếu còn số version cũ trên happy path
   - Không đụng lịch sử CHANGELOG cũ (`## [v1.12.0]` là lịch sử hợp lệ)
4. Chạy:
   - `pytest tests/` (product root)
   - `pytest reference/mcp-server/tests/` (xác nhận không còn collect 0)
5. Ghi validation evidence vào Progress; commit chỉ khi user yêu cầu.

### Phase B — Ship GUI (session 2–3)

1. Align version `gui-native` (`package.json`, `Cargo.toml`, `tauri.conf.json`) với product release scheme (đề xuất: GUI version = product version `1.18.x` hoặc `1.18.0-gui.1` — **Decision** bên dưới).
2. First-run checklist trong app: thiếu `mcp-sap-connect` → hướng dẫn pip / embed sidecar (ưu tiên: require pip preinstall v1; embed sidecar = v2 nếu Decision chọn).
3. `npm run tauri build` trên Windows → artifact `msi`/`nsis`.
4. Workflow GitHub Actions (optional trong B): build Windows artifact khi tag `gui-v*`.
5. Docs: `gui-native/README.md` + product README mục GUI trỏ installer; đánh dấu Tkinter “legacy / vẫn hỗ trợ 1–2 release”.
6. Manual E2E: Add profile from file → Ping → Connect → MCP status/register core.

### Phase C — Onboarding personas (session 3–4)

1. Viết lại `docs/onboarding-guide.md`:
   - Persona **ABAP Dev**: plugin + wheel + profile + scaffold path
   - Persona **Functional**: plugin + CDS/docs MCP + ask-consultant (không scaffold)
   - Persona **Key user**: key-user-toolkit + tra cứu (minimal MCP)
2. Happy path ≤ 15 phút / persona; advanced (cron, error reporting, Notion, vsp) tách “Tùy chọn”.
3. README: mục Cài đặt rút gọn → link onboarding; giữ reference sâu bên dưới hoặc collapse.
4. (Nếu B xong) Onboarding bước 1 = “Cài MSI” thay vì pip cho Windows GUI users.

## Risks And Recovery

| Risk | Mitigation | Recovery |
|------|------------|----------|
| Resolve CHANGELOG mất entry 1.18 | Giữ cả hai phía; ưu tiên nội dung local 1.18 + remote mới hơn | `git checkout --ours/--theirs` có chủ đích + so diff |
| ahead/behind diverged | rebase hoặc merge commit rõ ràng; không `--force` main | Abort rebase; hỏi user trước push |
| pytest fail sau khi bỏ ignore | Fix test hoặc quarantine có lý do trong plan Progress | Không claim A done |
| Tauri build thiếu WebView2/Rust | Document prerequisite; CI Windows runner | Fallback: tiếp tục ship wheel + Tkinter trong khi B blocked |
| Embed Python sidecar phình artifact | Default B: **không embed** — require `mcp-sap-connect` trên PATH | Decision đổi sang embed ở session riêng |
| Onboarding mâu thuẫn README | C cập nhật cả hai; onboarding là authority cài đặt end-user | Revert doc-only |

## Progress

### Phase A — Stabilize

- [x] Resolve `CHANGELOG.md` UU + sync với `origin/main`
- [x] Sync README badge + pip wheel examples → `1.18.0` (hoặc version pin đúng release mới nhất)
- [x] Quét drift còn lại trên happy-path docs (`onboarding-guide`, sample JSON trong README)
- [x] `pytest tests/` pass (ghi số collected / failed)
- [x] `pytest reference/mcp-server/tests/` pass (không collect 0)
- [x] Cập nhật Progress + Validation bằng chứng

### Phase B — Ship GUI

- [x] Decision versioning + sidecar vs PATH-only → `docs/decisions/0001-gui-path-only-no-sidecar.md` (Accepted)
- [x] Align version manifests `gui-native` → **1.19.0** (theo product sau CI bump)
- [x] First-run / doctor UX tối thiểu (`check_runtime` + banner) — shipped `f2e7da7`
- [x] `tauri build` tạo MSI/NSIS thành công (2026-08-01, exit 0):
  - `gui-native/dist-bundle/SAP ABAP Agent_1.19.0_x64-setup.exe`
  - `gui-native/dist-bundle/SAP ABAP Agent_1.19.0_x64_en-US.msi`
- [x] CI release workflow Windows: `.github/workflows/gui-release.yml` (tag `gui-v*`)
- [x] Docs deprecate Tkinter + link installer (README + gui-native/README)
- [x] Manual E2E smoke (2026-08-01):
  - MSI silent `/qn` → **fail 1603** (Error 1925 privileges / per-machine)
  - NSIS → cài OK → `...\AppData\Local\SAP ABAP Agent\gui-native.exe` chạy
  - `mcp-sap-connect ping` OK (`nfg_dev`)
  - `mcp-sap-connect connect` OK (read + CSRF/write)
  - `mcp-setup --register-json sap-btp` + `sap-dict-bridge` → `registered: true`

### Phase C — Onboarding personas

- [x] Rewrite `docs/onboarding-guide.md` (3 persona + optional advanced) v1.19.0
- [x] Rút README cài đặt → link onboarding
- [x] Align GUI first-run / MSI caveat với onboarding (NSIS ưu tiên)
- [x] Checklist persona trong onboarding (self-serve walkthrough)

## Decisions

- **2026-08-01 (Accepted):** PATH-only — `docs/decisions/0001-gui-path-only-no-sidecar.md`. User xác nhận “tiếp tục B với default PATH-only”.
- **2026-08-01 (Accepted):** Version GUI = semver product; hiện **1.19.0**; release tag `gui-v1.19.0`.
- **2026-08-01 (Accepted):** Tkinter legacy ≥2 minor sau GUI GA.
- **2026-08-01 (A done):** Merge conflict CHANGELOG — commit `a1f127e`.
- **Decision required trước Phase C sâu Cursor:** templates MCP only (default) vs Cursor skill pack.

## Validation

- Focused proof (A):
  - [x] `git status` sạch conflict — merge concluded `a1f127e`, branch ahead 2
  - [x] README badge/wheel/sample → `1.18.0`; onboarding-guide không còn happy-path pin `1.12`/`1.14`
  - [x] pytest root: **210 passed** (collected 210)
  - [x] pytest mcp-server: **20 passed** (collected 20, không còn 0)
- Integration (B):
  - [x] Artifact installer tồn tại (NSIS+MSI local build exit 0)
  - [x] App mở (NSIS install path + portable exe); profiles qua CLI/GUI PATH
  - [x] Đăng ký `sap-btp` + `sap-dict-bridge` (`registered: true`)
  - [!] MSI silent không elevate → 1603/1925 — document ưu tiên NSIS
- End-user (C):
  - [x] Onboarding 3 persona trong `docs/onboarding-guide.md`
  - [x] README Cài đặt → link onboarding + tóm tắt 3 bước

Repository-required checks: pre-commit / `validate_plugin.py` nếu đụng plugin surfaces; không skip hooks.

## Result

Verified 2026-08-01 (forked subagent re-check):

- **A:** Version stabilize + pytest 230 green (prior session); product at plugin
  **1.19.1** / mcp wheel pin **1.19.0**.
- **B:** NSIS install path
  `%LOCALAPPDATA%\SAP ABAP Agent\gui-native.exe` launches (PID observed).
  `mcp-sap-connect ping` OK (`pmc_dev`); `connect` OK (read + CSRF/write).
  MCP core: `sap-btp` + `sap-dict-bridge` `registered: true` (`claudeAvailable: true`).
  MSI silent without elevation → 1603/1925 — docs prefer NSIS.
- **C:** `docs/onboarding-guide.md` 3 personas; README Cài đặt → onboarding link.
  Local polish (NSIS note, badge 1.19.1) may be unstaged — commit when authorized.

Follow-up (optional): push polish commit; `git tag gui-v1.19.0 && git push origin gui-v1.19.0`
for GitHub Release artifacts.

## Session log

| Session | Date | Focus | Done |
|---------|------|-------|------|
| 0 | 2026-08-01 | Tạo plan A+B+C | Plan Active |
| 1 | 2026-08-01 | Phase A Stabilize | Conflict resolved + README sync + pytest |
| 2 | 2026-08-01 | Phase B PATH-only | Runtime banner; build NSIS/MSI; gui-release.yml |
| 3 | 2026-08-01 | Smoke + Phase C | NSIS OK; ping/connect/MCP core; 3 personas |
| 3b | 2026-08-01 | Re-verify + close plan | Ping/connect/MCP + GUI process; plan Completed |
