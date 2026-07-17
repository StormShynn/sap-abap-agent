# SAP ABAP Agent (Tiếng Việt)

[![Version](https://img.shields.io/badge/version-1.3.3-blue.svg)](CHANGELOG.md) [![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org) [![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE) [![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md) [![Security Policy](https://img.shields.io/badge/Security-View_Policy-blue.svg)](SECURITY.md) [![Changelog](https://img.shields.io/badge/Changelog-%23ff69b4.svg)](CHANGELOG.md) [![CI/CD](https://github.com/StormShynn/sap-abap-agent/actions/workflows/deploy.yml/badge.svg)](https://github.com/StormShynn/sap-abap-agent/actions/workflows/deploy.yml) [![GitHub Pages](https://img.shields.io/github/deployments/StormShynn/sap-abap-agent/github-pages?label=GitHub%20Pages&logo=github)](https://stormshynn.github.io/sap-abap-agent/)

Plugin Claude Code + MCP server tự động kết nối **SAP BTP / S/4HANA Cloud** để thao tác
ABAP (đọc / tìm / syntax-check / activate). Hỗ trợ **multi-profile** — mỗi project SAP
có profile riêng (URL, tenant, secret), lưu trong **folder user** trên máy
(`%USERPROFILE%\.sap-btp-agent\` Windows, `~/.sap-btp-agent/` macOS/Linux).

## Nổi bật

- **🧠 SAP Consultant System (28 agents)**: Routing tự động bằng auto-scoring engine. 25 module
  consultants cho SD, FI, MM, CO, PP, QM, PM, WM, PS, HCM, BW, Basis, TM, TR, Ariba, CA, GTS, EHS,
  IBP, EWM, Fiori/UI5, CAP, CPI, SuccessFactors, BTP Admin + Docs Researcher + Daily Learner + Reviewer.
- **🔌 SAP BTP Connection**: `sap-btp-agent` — kết nối S/4HANA Cloud, đọc/activate ABAP, multi-profile.
- **🧱 DDIC Dictionary Bridge**: `sap-dict-bridge` MCP server (`sap_create_domain`/`sap_create_data_element`/
  `sap_create_table`) — tạo Domain/Data Element/Table trực tiếp qua cookie auth của `sap-btp-agent`
  (xem skill `sap-cloud-dictionary`).
- **📚 CDS Knowledge Base**: Tra cứu 7,355 CDS views released qua semantic search.
- **📖 SAP Docs Research**: Tra cứu SAP Help, Community, API Hub, Fiori App Library.
- **🔒 Process Discipline**: SessionStart hook ép routing trước khi trả lời,
  verification-before-completion, systematic-debugging, finish-ticket checklist — chặn lại kiểu
  lỗi "code đọc ổn nhưng chưa chạy thật".
- **🧠 Context Engineering** (v0.6.2): trim MCP output (observation masking),
  scaffold summary giữa các layer, 2-layer module routing (CORE+DEEP), 3-tier memory
  cho daily-learner — lấy pattern từ agent-skills-for-context-engineering.

## Đóng góp

Dự án là **open-source**, mọi đóng góp đều được chào đón!

| File | Mục đích |
|------|----------|
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Hướng dẫn đóng góp skill, agent, docs |
| [`SKILL_TEMPLATE.md`](SKILL_TEMPLATE.md) | Template chuẩn để tạo skill / agent / reference module |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Quy tắc ứng xử của cộng đồng |

## Cấu trúc

```text
sap-abap-agent/
+-- .claude-plugin/            # Manifest plugin Claude Code
+-- commands/                  # /sap-connect
+-- skills/
|   +-- sap-ask-consultant/    # 🧠 Auto-scoring routing engine (28 agents)
|   +-- sap-daily-learner/     # 📚 Daily SAP Learning — Hermes-like (self-improving)
|   +-- sap-btp-setup/         # Setup & troubleshoot SAP BTP connection
|   +-- sap-clean-code/        # ABAP Cloud naming conventions & clean code
|   +-- sap-extensibility/     # Extensibility bậc thang cho Public Cloud
|   +-- sap-key-user-toolkit/  # Key User Extensibility handbook
|   +-- sap-cds-kb/            # Tra cứu CDS view qua cds-kb-mcp
|   +-- sap-docs-research/     # Tra cứu SAP Docs qua mcp-sap-docs
|   +-- sap-doc-to-md/         # Convert Word/Excel sang Markdown (markitdown)
|   +-- sap-analyze-function-spec/  # FS.docx -> INTAKE.md (bước 1 codegen pipeline)
|   +-- sap-write-technical-spec/   # INTAKE.md -> TECHNICAL_SPEC.md (bước 2)
|   +-- sap-cloud-dictionary/       # Tạo Domain/Data Element/Database Table (DDIC)
|   +-- sap-bootstrap-system-context/ # Dò hệ thống thật qua MCP trước khi scaffold
|   +-- sap-scaffold-rap/           # TECHNICAL_SPEC.md -> RAP 3-layer skeleton (bước 3)
|   +-- sap-scaffold-cds/           # -> CDS view skeleton, pattern read-only (bước 3)
|   +-- sap-scaffold-cds-analytics/ # -> Cube/Dimension/Text + Analytical Query
|   +-- sap-virtual-element/        # Calculated field trong CDS view
|   +-- sap-atc-review/             # Lint naming/released-API/clean-ABAP (bước 4)
|   +-- sap-unit-test/              # Sinh ABAP Unit test class (bước 5)
|   +-- sap-cds-unit-test/          # Test CDS view/RAP BO (bước 5)
|   +-- sap-migrate-segw-to-rap/    # Reverse-engineer SEGW -> RAP
|   +-- sap-finish-ticket/          # Checklist đóng ticket (bước 6)
|   +-- sap-verification-before-completion/  # Bằng chứng chạy thật
|   +-- sap-systematic-debugging/   # Debug runtime có hệ thống
|   +-- sap-routing-discipline/     # SessionStart hook - ép check routing
|   +-- sap-mcp-status/             # Audit MCP server registration
|   +-- sap-security-review/        # Quét bảo mật ABAP Cloud (OWASP-style, gọi từ abap-reviewer)
|   +-- ... (12 skills khác: mcp-sap-notes, mcp-sap-concur, mcp-sap-fieldglass,
|   |       sap-released-classes, sap-abap-sql, sap-badi-enhancement,
|   |       sap-authorization, sap-odata-service, sap-rap-events,
|   |       sap-cloud-migration, sap-btp-connectivity, sap-btp-best-practices)
+-- agents/
|   +-- sap-ask-consultant/    # Auto-scoring routing — dispatch tới 28 agents:
|   |   +-- 25 module consultants (SD, FI, MM, CO, PP, QM, PM, WM, PS, HCM,
|   |   |   BW, Basis, TM, TR, Ariba, CA, GTS, EHS, IBP, EWM, Fiori, CAP,
|   |   |   CPI, SuccessFactors, BTP Admin)
|   |   +-- sap-docs-researcher       # CDS view & Docs Research
|   |   +-- sap-daily-learner         # Daily SAP Learning (Hermes-like)
|   |   +-- abap-reviewer             # Review code ABAP Cloud
|   +-- sap-btp-admin-consultant-cloud  # BTP Platform Administration
|   +-- sap-cap-consultant-cloud        # CAP (Cloud Application Programming)
+-- hooks/                   # Cảnh báo SELECT * (PostToolUse) + routing (SessionStart)
+-- reference/
    +-- modules/             # Kiến thức module cho từng consultant
    |   +-- sap-[module]-cloud/SKILL.md
    |   +-- sap-steampunk-cloud/SKILL.md
    +-- process/             # Context engineering (đã chuyển từ skills/)
    |   +-- sap-context-tool-result-trim.md   # Observation masking
    |   +-- sap-scaffold-context-summary.md   # Compact giữa các layer scaffold
    |   +-- sap-context-module-routing.md     # 2-layer core+deep routing
    +-- mcp-guides/          # MCP setup reference (đã chuyển từ skills/)
    |   +-- mcp-sap-adt.md              # ADT MCP (3 options)
    |   +-- mcp-sap-gui.md              # SAP GUI Automation
    |   +-- mcp-sap-successfactors.md   # SuccessFactors MCP
    |   +-- mcp-sap-cdata-setup.md      # CData MCP common setup
    +-- scripts/             # Lint, validate, cleanup, update
    |   +-- agent_home.py, check_service_type.py, cleanup_agent_home.py,
    |   +-- mcp_common.py, mcp_status.py, mcp_inventory.json,
    |   +-- validate_plugin.py, sync_skills.py, office_to_md.py,
    |   +-- security_scan.py, update.ps1, update.sh, ...
    +-- mcp-server/          # MCP server Python (multi-profile)
        +-- sap_btp_agent/
        |   +-- config/        # paths, profile (registry), store, secrets
        |   +-- sap/           # auth (OAuth2), client (REST + auto-reconnect)
        |   +-- tools/         # registry các tool MCP (có tham số `profile`)
        |   +-- cli/           # wizard setup + quản lý profile
        +-- pyproject.toml
```

## Cài đặt (1 lần)

Yêu cầu: **Python >= 3.10**. **Không cần clone repo** — chỉ cần tải 1 file `.whl` và `pip install`:

```bash
pip install https://github.com/StormShynn/sap-abap-agent/releases/download/mcp-server-v1.7.11/sap_abap_agent_mcp-1.7.11-py3-none-any.whl
```

(Hoặc tải file `.whl` về trước rồi `pip install đường-dẫn-file.whl` nếu máy không có internet lúc chạy lệnh.)

Trên Windows, cài thêm extra `win-dpapi` để mã hóa secrets bằng DPAPI (thêm `[win-dpapi]` ngay sau tên file, trước phần mở rộng `.whl`):

```bash
pip install "sap_abap_agent_mcp-1.7.11-py3-none-any.whl[win-dpapi]"
```

Nếu muốn dùng Cookie-based auth kiểu **tự mở browser đăng nhập** (không cần F12 copy tay), cài thêm extra `playwright`
và download browser binary:

```bash
pip install "sap_abap_agent_mcp-1.7.11-py3-none-any.whl[playwright]"
playwright install chromium
```

Sau bước cài, bạn sẽ có lệnh `sap-btp-agent` trong PATH (entry point khai báo trong `pyproject.toml`).

<details>
<summary>Dev / contributor: cài từ source (editable install)</summary>

```bash
git clone https://github.com/StormShynn/sap-abap-agent.git
cd sap-abap-agent/reference/mcp-server
pip install -e .[win-dpapi,playwright]
```

Dùng khi bạn muốn sửa code MCP server (`reference/mcp-server/sap_btp_agent/`) và thay đổi có hiệu lực ngay
không cần build lại wheel. Build wheel mới để release:

```bash
pip install build
python -m build --wheel
# -> dist/sap_abap_agent_mcp-<version>-py3-none-any.whl
```

</details>

**Kiểm tra ngay sau khi cài** (khuyến dùng, dành cho mọi người — không cần dùng AI để debug):

```bash
python -m sap_btp_agent.doctor
```

Lệnh này chạy được **ngay cả khi `sap-btp-agent` chưa nằm trong PATH** (lỗi thường gặp nhất trên Windows: `pip`
cài vào user-scheme site-packages vì không có quyền viết vào Python gốc, VD `%APPDATA%\Python\PythonXY\Scripts`,
folder này thường không tự động có trong PATH). Doctor sẽ tự phát hiện và in sẵn lệnh PowerShell để fix, kèm
kiểm tra các dependency hay bị thiếu ngầm (pywin32/DPAPI, playwright+chromium...). Sau khi đã cài xong và PATH
đúng, có thể gọi lại qua `sap-btp-agent doctor`.

## Thêm project SAP mới

Cách nhanh nhất — truyền URL trực tiếp:

```bash
sap-btp-agent setup https://project1.s4hana.cloud.sap
```

Wizard sẽ tự sinh profile id từ hostname (`project1.s4hana.cloud.sap`) và hỏi phương thức xác thực (chọn 1-4):

1. **OAuth2** (client_credentials) — `client_id` + `client_secret`, mặc định/khuyến dùng
2. **Password** — `username` + `password`
3. **Bearer token** — token có sẵn, nhập tay
4. **Cookie-based** — session cookie SAP (`MYSAPSSO2`, `SAP_SESSIONID`, `sap-usercontext`...). Wizard hỏi tiếp lấy cookie từ đâu:
   - (1) File cookie Netscape format
   - (2) Paste tay (F12 -> Application -> Cookies)
   - (3) **Auto** — tự mở browser cho bạn đăng nhập, tự lấy cookie (cần extra `playwright`, không có sẽ fallback về paste tay)

   Sau khi có cookie, tự động re-auth qua browser popup (hoặc Playwright) mỗi lần session hết hạn (401).

Sau đó hỏi thêm Region, service type (s4hc_(private) / s4hc_(public) / btp / onprem).

Thông tin được lưu riêng trong `profiles/<id>/`:

```
%USERPROFILE%\.sap-btp-agent\profiles\project1.s4hana.cloud.sap\
+-- config.json     <- URL, tenant, client_id, region, service (không nhạy cảm)
+-- secrets.json    <- client_secret / token (ĐÃ MÃ HÓA)
```

**Thêm project thứ 2, 3...** cũng dễ:

```bash
sap-btp-agent setup https://project1.s4hana.cloud.sap
```

Mỗi project sẽ có profile riêng, secret riêng (mã hóa độc lập).

## Quản lý nhiều profile

```bash
sap-btp-agent profiles list             # liệt kê profile (* = active)
sap-btp-agent profiles use project1     # chọn profile active
sap-btp-agent profiles show             # xem chi tiết profile active
sap-btp-agent profiles remove project2  # xóa 1 profile
sap-btp-agent reset                     # xóa TẤT CẢ (cẩn thận!)
```

## Kiểm tra kết nối

```bash
sap-btp-agent connect                            # test profile active
sap-btp-agent connect project1.s4hana.cloud.sap  # test 1 profile cụ thể
```

## Đăng ký MCP với Claude Code

> **Quản lý nhiều MCP server cùng lúc?** Các phần dưới đây hướng dẫn `claude mcp add`
> từng server riêng lẻ. Nếu bạn dùng nhiều coding agent (Claude Code, Claude Desktop,
> Codex CLI, Gemini CLI...) và muốn 1 chỗ bật/tắt MCP server cho tất cả thay vì sửa tay
> từng file config, xem thử [mcp-switch](https://github.com/StormShynn/mcp-switch) —
> desktop app (Tauri + Rust) riêng của tác giả plugin này, dùng 1 store trung tâm
> (`~/.mcp-switch/store.json`) rồi ghi lại config native của từng tool khi bạn bật/tắt.
> Độc lập với plugin này, không bắt buộc.

`sap-btp-agent` gọi không có argument sẽ chạy MCP stdio server (`sap_btp_agent/server.py`), serve các tool
bên dưới qua JSON-RPC. Đã test end-to-end (initialize -> tools/list -> tools/call) trước khi công bố.

Dùng lệnh `claude mcp add` (Claude Code không còn dùng file `mcp_servers.json`):

```bash
claude mcp add --transport stdio sap-btp -- sap-btp-agent
```

Mặc định là scope `local` (chỉ máy này, chỉ project hiện tại). Dùng `--scope user` để dùng được ở mọi project,
hoặc `--scope project` để lưu vào `.mcp.json` và chia sẻ qua git cho cả team.

Mở Claude Code với plugin, các tool sau sẽ xuất hiện:

| Tool                  | Mô tả                                                       |
|-----------------------|-------------------------------------------------------------|
| `sap_list_profiles`   | Liệt kê các profile đã cấu hình                             |
| `sap_ping`            | Test kết nối profile (có tham số `profile`)                 |
| `sap_list_packages`   | Liệt kê package ABAP                                        |
| `sap_search`          | Tìm object ABAP theo tên                                    |
| `sap_read_source`     | Đọc source code (class, program, include...)                |
| `sap_syntax_check`    | Syntax check (không activate)                               |
| `sap_activate`        | Activate object (transport local)                           |

### MCP server phụ trợ: tra cứu CDS view & SAP docs

Theo mặc định, Claude Code chỉ chấp nhận 1 MCP server stdio. Để sử dụng thêm các MCP server
remote (cds-kb-mcp và mcp-sap-docs), dùng `claude mcp add` với transport `sse`:

**CDS Knowledge Base** (7,355 released CDS views):

Cách 1 — `claude mcp add` (nếu Claude Code hỗ trợ `--transport sse`):

```bash
claude mcp add --transport sse cds-kb --url https://cds-kb-mcp-production.up.railway.app/sse
# Nếu primary không truy cập được, dùng fallback:
# claude mcp add --transport sse cds-kb --url https://cds-kb-mcp.cfapps.ap21.hana.ondemand.com/sse
```

Cách 2 — `supergateway` (tương thích với mọi IDE hỗ trợ MCP: Cursor, Claude Desktop, VS Code, Gemini IDE):

```json
{
  "mcpServers": {
    "cds-kb": {
      "command": "npx",
      "args": ["-y", "supergateway@2.0.0", "--sse", "https://cds-kb-mcp-production.up.railway.app/sse"]
    }
  }
}
```

**SAP Docs Research** (SAP Help, Community, API Hub, Fiori App, Clean Core):

Cách 1 — `claude mcp add`:

```bash
claude mcp add --transport sse mcp-sap-docs-btp --url https://sap-docs-extend-mcp.cfapps.ap21.hana.ondemand.com/sse
# Nếu có SAP-API-HUB-KEY:
# claude mcp add --transport sse mcp-sap-docs-btp --url https://sap-docs-extend-mcp.cfapps.ap21.hana.ondemand.com/sse --headers "{\"SAP-API-HUB-KEY\": \"<YOUR_KEY>\"}"
```

Cách 2 — `supergateway`:

```json
{
  "mcpServers": {
    "mcp-sap-docs-btp": {
      "command": "npx",
      "args": ["-y", "supergateway@2.0.0", "--sse", "https://sap-docs-extend-mcp.cfapps.ap21.hana.ondemand.com/sse"],
      "disabled": false
    }
  }
}
```

> **Windows users**: Nếu dùng supergateway, có thể cần dùng `supergateway.cmd` thay vì `supergateway`
> hoặc chỉ định đường dẫn tuyệt đối.

### Notion — skill notes dùng chung cho team

**notion** — Workspace Notion làm nơi ghi/tra skill notes bổ sung (AI ghi tóm tắt, bạn ghi tay), qua
MCP server **chính chủ** của Notion ([makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server)).
Đã **auto-bundle sẵn trong `.mcp.json`** của plugin này (không cần `claude mcp add` thủ công) — mỗi
thành viên team chỉ cần chạy 1 lệnh trong Claude Code để đăng nhập tài khoản Notion của riêng họ:

```
/mcp
```

Chọn `notion` trong danh sách rồi làm theo OAuth flow (mở browser đăng nhập). **Không có token/secret
nào được lưu trong repo** — mỗi người tự xác thực bằng chính tài khoản Notion của mình.

**Chia sẻ cho team**: invite từng thành viên vào page/workspace Notion tương ứng (thao tác ở phía
Notion — Share → nhập email), không liên quan gì đến file `.mcp.json`/repo. Xem chi tiết cách đăng
ký và cấu hình khác ở [developers.notion.com/guides/mcp](https://developers.notion.com/guides/mcp).

<details>
<summary><b>👥 Mời thêm người vào dùng chung database "SAP Skills" — làm sao cho đúng</b></summary>

Setup phía người được mời, theo đúng thứ tự:

1. **Accept invite/mở link share Notion trước** (thao tác tay trong trình duyệt, ngoài Claude Code)
   — xác nhận thấy đúng nội dung database.
2. Tự chạy `/mcp` trong Claude Code, chọn `notion`, đăng nhập **bằng tài khoản Notion của chính
   họ** (không dùng chung tài khoản với người tạo database).

> ⚠️ **Rủi ro cần biết**: cơ chế tìm database hiện tại dựa theo **tên** (`notion-search "SAP
> Skills"` → thấy thì dùng, không thấy thì tự tạo mới). Chưa test được với 1 tài khoản Notion thứ
> 2 liệu search có chắc chắn tìm ra database đã được share (khác với database tự tạo) hay không —
> nếu không tìm ra, Claude sẽ **tự tạo 1 database "SAP Skills" mới, riêng, không báo lỗi gì cả**,
> làm mất ý nghĩa dùng chung (mỗi người 1 bản, không đồng bộ).
>
> **Cách né**: trước khi để `sap-daily-learner` tự chạy lần đầu, người mới nên tự bảo Claude
> "search notion database SAP Skills" và kiểm tra kết quả có đúng database cũ (có dữ liệu sẵn)
> hay không — thấy database rỗng/khác thì báo ngay để xử lý thủ công, tránh bị tạo trùng trong
> im lặng.

Chi tiết đầy đủ: `skills/sap-daily-learner/SKILL.md` mục 3b.

</details>

Ví dụ prompt:
```
"Tóm tắt skill sap-cloud-dictionary vừa học vào page Notion 'SAP Skills'"
"Tra trong Notion xem có note nào về BAdI enhancement không"
```

**Tự động đồng bộ 2 chiều với `sap-daily-learner`**: skill `sap-daily-learner` (Auto-Skill Creation
Engine) tự tra database "SAP Skills" trên Notion trước khi tự giải 1 vấn đề từ đầu — nếu thành viên
khác trong team đã hỏi và tạo skill tương tự rồi thì lấy ra dùng luôn; sau khi tự tạo 1 skill mới,
tự động đẩy lên Notion (không cần thao tác gì thêm ngoài `/mcp` đã làm 1 lần ở trên). Chi tiết quy
trình: `skills/sap-daily-learner/SKILL.md` mục "3b. Đồng bộ Notion".

**Mở rộng cho cả 25 agent tư vấn**: `skills/sap-ask-consultant/SKILL.md` (Bước 5) cũng tra kho
local + Notion này trước khi dispatch bất kỳ agent tư vấn nào (SD/FI/MM/...) — local trước (offline,
nhanh), Notion khi local chưa có (online), tự cache lại local sau khi tìm thấy trên Notion. Mất
local (vd đổi máy) không sao — lần hỏi lại đầu tiên sẽ tự lấy lại từ Notion. Phần **ghi** skill mới
vẫn chỉ riêng `sap-daily-learner` (agent duy nhất có quyền ghi file).

### 🤖 Continuous Improvement Engine — Tự động phát hiện lỗi & tạo issue

Error reporter (`hooks/error_reporter.py`) chạy ngầm qua hook system, tự động phát hiện lỗi
runtime trong quá trình dùng plugin và tạo GitHub issue trên repo chính để theo dõi, fix lỗi
liên tục — **mỗi ngày plugin càng ít lỗi hơn**:

> ⚠️ **Mặc định TẮT (opt-in)**. Cài plugin không bắt buộc bạn phải có GitHub auth, và việc thu
> thập error/code âm thầm mà không hỏi trước là vi phạm quyền riêng tư — nên tính năng này chỉ
> chạy khi bạn bật rõ ràng bằng 1 trong 2 cách:
> **Cách 1 — tạm thời (chỉ trong session terminal hiện tại):**
>
> <details>
> <summary><b>PowerShell</b> (Windows — khuyến nghị)</summary>
>
> ```powershell
> $env:SAP_ABAP_AGENT_ERROR_REPORTING = "1"
> ```
>
> </details>
>
> <details>
> <summary><b>CMD</b> (Windows — Command Prompt)</summary>
>
> ```cmd
> set SAP_ABAP_AGENT_ERROR_REPORTING=1
> ```
>
> </details>
>
> <details>
> <summary><b>bash / zsh / Git Bash / WSL</b> (macOS, Linux)</summary>
>
> ```bash
> export SAP_ABAP_AGENT_ERROR_REPORTING=1
> ```
>
> </details>
>
> **Cách 2 — vĩnh viễn (tạo file marker, không cần set env mỗi lần):**
>
> <details>
> <summary><b>PowerShell</b> (Windows)</summary>
>
> ```powershell
> New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.sap-btp-agent\error-reports"
> New-Item -ItemType File -Force -Path "$env:USERPROFILE\.sap-btp-agent\error-reports\ENABLED"
> ```
>
> </details>
>
> <details>
> <summary><b>CMD</b> (Windows)</summary>
>
> ```cmd
> if not exist "%USERPROFILE%\.sap-btp-agent\error-reports" mkdir "%USERPROFILE%\.sap-btp-agent\error-reports"
> echo. > "%USERPROFILE%\.sap-btp-agent\error-reports\ENABLED"
> ```
>
> </details>
>
> <details>
> <summary><b>bash / zsh / Git Bash / WSL</b> (macOS, Linux)</summary>
>
> ```bash
> mkdir -p ~/.sap-btp-agent/error-reports && touch ~/.sap-btp-agent/error-reports/ENABLED
> ```
>
> </details>
> Ngoài ra, phần "đính code fix vào issue" **chỉ hoạt động khi bạn sửa chính code của plugin
> này** (VD đang dev fix bug plugin) — không bao giờ đính kèm code ABAP/project nội bộ của bạn
> lên issue public, dù đã bật opt-in.

```
User chạy lệnh → PostToolUse detect → ghi error_log.jsonl
                                           ↓
Stop hook → gom nhóm 24h → dedup (SHA256) → tạo GitHub issue (nếu mới)
                                           ↓
Khi Claude viết code sửa lỗi → detect-fix → ghi fix_log.jsonl
                                           ↓
Stop → match fix với issue → add comment "cách sửa" vào issue có sẵn
                                           ↓
Issue = [🐛 error] + [✅ fix solution] → Dev fix → release → user update → ít lỗi hơn
```

#### Các chế độ hook

| Hook event | Mode | Chức năng |
|------------|------|-----------|
| PostToolUse (Bash) | `detect-bash` | Phát hiện lỗi từ Bash command (exit code ≠ 0, stderr) |
| PostToolUse (sap_*) | `detect-tool` | Phát hiện lỗi từ MCP tool (syntax check fail, activate fail, connection error) |
| PostToolUse (Edit/Write) | `detect-fix` | Khi Claude viết code, kiểm tra có phải đang fix lỗi cũ không → ghi fix record |
| Stop | `report` | Gom error → dedup → tạo issue + Gom fix → add comment |

#### Matching fix với error

`detect-fix` chỉ xét tiếp nếu file đang sửa **nằm trong chính thư mục cài đặt plugin này**
(`_is_plugin_file()`) — sửa code của bạn (VD class ABAP nội bộ) sẽ bị bỏ qua ngay từ bước này,
không bao giờ vào `fix_log.jsonl`. Nếu qua được gate đó, mới quét error_log 7 ngày, scoring:
- **file_path** match → +3
- **session_id** match → +1
- **Code keywords** (tên class, table, method) match với error message → +1 đến +3
- Threshold ≥2 → tạo fix record (đã redact chuỗi giống secret/token), sẽ được add comment vào
  GitHub issue ở Stop hook

#### Kiểm tra trạng thái

Không cần stdin, chạy tay được:

<details>
<summary><b>PowerShell</b> (Windows — khuyến nghị)</summary>

```powershell
"{}" | python hooks/error_reporter.py status
```

</details>

<details>
<summary><b>CMD</b> (Windows — Command Prompt)</summary>

```cmd
echo {} | python hooks\error_reporter.py status
```

</details>

<details>
<summary><b>bash / zsh / Git Bash / WSL</b> (macOS, Linux)</summary>

```bash
echo '{}' | python hooks/error_reporter.py status
```

</details>

Output mẫu:
```json
{
  "plugin_version": "1.5.0",
  "total_logged_errors": 12,
  "total_logged_fixes": 3,
  "active_error_groups_24h": 2,
  "known_issues_created": 1,
  "error_breakdown": {
    "a1b2c3d4e5f6": {
      "type": "abap_syntax_error",
      "count": 5,
      "message_preview": "Syntax error in ZCL_MY_CLASS...",
      "has_issue": true,
      "has_fix": true,
      "fix_count": 1
    }
  }
}
```

#### Ai cũng có local report — không cần GitHub

Dù có GitHub auth hay không, error report **luôn được save thành file Markdown**
tại `~/.sap-btp-agent/error-reports/reports/` — ai cũng đọc được, không cần Dù có GitHub auth hay không, error report **luôn được save thành file Markdown**
tại `~/.sap-btp-agent/error-reports/reports/` — ai cũng đọc được, không cần token.

<details>
<summary><b>PowerShell / CMD</b> (Windows)</summary>

```powershell
# PowerShell
Get-ChildItem "$env:USERPROFILE\.sap-btp-agent\error-reports\reports\"
```

```cmd
:: CMD
dir "%USERPROFILE%\.sap-btp-agent\error-reports\reports\"
```

</details>

<details>
<summary><b>bash / zsh / Git Bash / WSL</b> (macOS, Linux)</summary>

```bash
ls ~/.sap-btp-agent/error-reports/reports/
```

</details>

Mỗi report là 1 file `.md` hoàn chỉnh: error message + context + fix solution
(nếu có) + hướng dẫn share lên GitHub Issues.

#### Tạo GitHub issue (optional — có auth thì tự động)

Fallback chain — không có auth cũng không sao, mọi thứ vẫn hoạt động:

```
1. gh CLI (gh issue create)?           → có → tạo issue
2. GITHUB_TOKEN / GH_TOKEN env var?    → có → REST API → tạo issue
3. Không có cả 2?                      → local report + pending queue → retry sau
```

**Luôn có local report** — bước 3 vẫn lưu file `.md` đầy đủ, không mất gì.

Chỉ cần chạy 1 lần, cần `GITHUB_TOKEN` (không cần `gh` CLI):

<details>
<summary><b>PowerShell</b> (Windows — khuyến nghị)</summary>

```powershell
$env:GITHUB_TOKEN = "ghp_xxx"
python reference/scripts/setup_labels.py
```

</details>

<details>
<summary><b>CMD</b> (Windows — Command Prompt)</summary>

```cmd
set GITHUB_TOKEN=ghp_xxx
python reference\scripts\setup_labels.py
```

</details>

<details>
<summary><b>bash / zsh / Git Bash / WSL</b> (macOS, Linux)</summary>

```bash
export GITHUB_TOKEN=ghp_xxx
python reference/scripts/setup_labels.py
```

</details>

Tạo 2 label: `auto-reported` 🟣 + `auto-fix` 🟢

**Đánh dấu riêng tư**: nếu không muốn 1 skill nào đó bị đẩy lên Notion (vd nội dung gắn với khách
hàng/hệ thống cụ thể), đánh dấu bằng thẻ `<private>...</private>` quanh câu hỏi hoặc nói thẳng
"đừng đồng bộ lên Notion" / "giữ local thôi" — `sap-daily-learner` sẽ chỉ lưu local, bỏ qua bước
đẩy Notion.

**Từ Notion vào thẳng project (quarantine -> active -> promote)**: skill nào được cả team dùng lại
nhiều lần (mặc định >=3, đếm trên Notion) trở thành "ứng viên promote" — lệnh "liệt kê ứng viên
promote" / "promote skill [topic]" đưa nó vào `reference/modules/<module>-cloud/SKILL.md` (git-
tracked, đi kèm plugin cho **mọi** người dùng public, không chỉ riêng team bạn qua Notion). Luôn
hỏi xác nhận trước khi ghi file, không tự commit/push — bạn tự xem diff + tự commit theo đúng flow
trong `CONTRIBUTING.md`.

> **Lưu ý bảo mật**: repo này là public — KHÔNG bao giờ dán token Notion (hoặc bất kỳ API key nào)
> trực tiếp vào `.mcp.json`/`mcp_inventory.json` rồi commit. Với server nào thực sự cần 1 secret tĩnh
> (vd `SAP-API-HUB-KEY` ở trên, hoặc `ADT_USER`/`ADT_PASS`...), dùng `reference/scripts/mcp_register.py`
> (hỏi riêng từng người, đăng ký qua `claude mcp add --scope user`) — giá trị chỉ nằm trong
> `~/.claude.json` của từng máy, không bao giờ vào file commit. Xem `python reference/scripts/mcp_status.py`
> để đối chiếu nhanh server nào đang thiếu env var mong đợi.

### MCP server mới: tra cứu SAP Notes

**mcp-sap-notes** — Tra cứu SAP Notes và KB articles trực tiếp từ SAP Support Portal:

```bash
# Cài đặt từ source
git clone https://github.com/marianfoo/sap-mcp-servers.git
cd sap-mcp-servers/packages/notes
npm install
npm run build

# Đăng ký MCP
claude mcp add --transport stdio sap-notes -- node /abs/path/to/dist/mcp-server.js \
  --env SAP_USERNAME=your@s-user.com --env SAP_PASSWORD=your_pass
```

| Tool | Mô tả |
|------|-------|
| `search` | Tìm SAP Note theo keyword / error code / component |
| `fetch` | Lấy nội dung đầy đủ SAP Note + ABAP correction instructions |

### MCP server mới: SAP GUI Automation (Windows)

**mcp-sap-gui (kts982)** — Điều khiển SAP GUI for Windows qua MCP (57 tools):

```bash
# Cài đặt bằng uvx (khuyến dùng)
pip install uvx

# Đăng ký MCP
claude mcp add --transport stdio sap-gui -- uvx mcp-sap-gui[screenshots] \
  --read-only --allowed-transactions MM03 VA03 IW33
```

**Yêu cầu**: Windows + SAP GUI + SAP GUI Scripting enabled (xem `reference/mcp-guides/mcp-sap-gui.md`).

| Tool | Mô tả |
|------|-------|
| `sap_connect` | Kết nối SAP GUI |
| `sap_run_transaction` | Mở transaction (/nMM03) |
| `sap_read_field` | Đọc giá trị field |
| `sap_read_table` | Đọc toàn bộ ALV/Grid table |

### MCP server mới: ADT ABAP Development (3 lựa chọn)

| Lựa chọn | Lệnh cài đặt | Phù hợp |
|----------|-------------|---------|
| **SAP Official ADT** (VS Code) | Cài extension ADT → Settings → Enable ADT MCP Server | VS Code users, enterprise |
| **ARC-1** (enterprise) | `npx arc-1@latest` | Team/doanh nghiệp cần security |
| **mcp-abap-adt** (community) | `npx -y mcp-abap-adt` | Cá nhân, POC nhanh |

```bash
# ARC-1
claude mcp add --transport stdio arc-1 -- npx -y arc-1@latest

# mcp-abap-adt
claude mcp add --transport stdio mcp-abap-adt -- npx -y mcp-abap-adt \
  --env ADT_URL=https://my-system.s4hana.cloud.sap --env ADT_USER=user --env ADT_PASS=pass
```

### MCP server mới: SAP SuccessFactors (2 options)

**sf-mcp (aiadiguru2025)** — Open-source MCP server cho SAP SuccessFactors OData API (62+ tools):

```bash
# Yêu cầu: Python 3.10+, uv package manager
git clone https://github.com/aiadiguru2025/sf-mcp.git
cd sf-mcp
uv sync

# Đăng ký MCP
claude mcp add --transport stdio sf-mcp -- uv --directory /path/to/sf-mcp run main.py
```

| Tool | Mô tả |
|------|-------|
| `get_employee_info` | Tra cứu thông tin nhân viên theo ID |
| `search_employees` | Tìm nhân viên theo criteria (name, department...) |
| `get_org_structure` | Lấy sơ đồ tổ chức công ty |
| `get_time_off_balance` | Kiểm tra ngày nghỉ còn lại của nhân viên |
| `get_role_permissions` | Kiểm tra RBP permissions của nhân viên |

**Option 2: CData SF MCP** — Java-based, SQL read-only (cần CData JDBC driver license):

```bash
claude mcp add --transport stdio sf-cdata -- java -jar /path/to/CDataMCP-jar-with-dependencies.jar /path/to/sap-successfactors.prp
```

### MCP server mới: SAP Concur Travel & Expense

**CData SAP Concur MCP** — Query expense reports, travel requests, bookings, vendor data qua SQL:

```bash
# Yêu cầu: Java 11+, Maven
git clone https://github.com/CDataSoftware/sap-concur-mcp-server-by-cdata.git
cd sap-concur-mcp-server-by-cdata
mvn clean install

# Đăng ký MCP
claude mcp add --transport stdio sap-concur -- java -jar /path/to/CDataMCP-jar-with-dependencies.jar /path/to/sap-concur.prp
```

| Tool | Mô tả |
|------|-------|
| `concur_get_tables` | Liệt kê các bảng SAP Concur instance |
| `concur_get_columns` | Liệt kê columns của 1 table |
| `concur_run_query` | Thực thi SQL SELECT query |

### MCP server mới: SAP Fieldglass Services Procurement

**CData SAP Fieldglass MCP** — Query contingent workforce, SoW, timesheets, invoices qua SQL:

```bash
# Yêu cầu: Java 11+, Maven
git clone https://github.com/CDataSoftware/sap-fieldglass-mcp-server-by-cdata.git
cd sap-fieldglass-mcp-server-by-cdata
mvn clean install

# License JDBC Driver
java -jar cdata.jdbc.sapfieldglass.jar --license

# Đăng ký MCP
claude mcp add --transport stdio sap-fieldglass -- java -jar /path/to/CDataMCP-jar-with-dependencies.jar /path/to/sap-fieldglass.prp
```

| Tool | Mô tả |
|------|-------|
| `fieldglass_get_tables` | Liệt kê các bảng SAP Fieldglass instance |
| `fieldglass_get_columns` | Liệt kê columns của 1 table |
| `fieldglass_run_query` | Thực thi SQL SELECT query |

### MCP server mới: Chrome DevTools (debug web / Fiori-UI5)

**chrome-devtools-mcp** — MCP server **chính chủ** của Google/ChromeDevTools team, điều khiển 1
Chrome thật (qua Puppeteer) để debug trang web: console log, network request, performance trace,
screenshot, thao tác DOM. Không phải tool SAP-specific, nhưng hữu ích khi cần debug **Fiori/UI5
app chạy trên browser** — việc mà `WebFetch`/`WebSearch` không làm được vì chỉ đọc HTML tĩnh,
không chạy được JS/SPA:

```bash
# Yêu cầu: Node.js LTS + Google Chrome (bản stable) đã cài sẵn máy
claude mcp add --transport stdio chrome-devtools -- npx -y chrome-devtools-mcp@latest

# Khuyến dùng: thêm --isolated để dùng profile Chrome tạm (tự xóa sau khi đóng),
# không đụng tới cookie/session Chrome thật bạn đang dùng hàng ngày
claude mcp add --transport stdio chrome-devtools -- npx -y chrome-devtools-mcp@latest --isolated
```

Hoặc dùng script chung của plugin (hỏi Y/n rồi tự chạy lệnh trên giúp bạn, không cần gõ tay):

```bash
python reference/scripts/mcp_register.py
```

Server này **không** nằm trong `.mcp.json` bundled sẵn của plugin (khác `sap-btp`/`cds-kb`/`notion`)
— dù không cần credential, nó vẫn cần 1 bước xác nhận (Y/n) vì là năng lực điều khiển 1 Chrome
thật, không nên tự động bật cho mọi người cài plugin.

| Tool | Mô tả |
|------|-------|
| `navigate_page` | Mở 1 URL (VD: Fiori Launchpad app) |
| `take_snapshot` | Chụp DOM snapshot (đọc cấu trúc trang, phục vụ click/fill tiếp theo) |
| `list_console_messages` | Liệt kê console log/error của trang (debug UI5 runtime error) |
| `list_network_requests` | Liệt kê network request (kiểm tra OData call bị lỗi 400/500) |
| `performance_start_trace` / `performance_stop_trace` | Ghi performance trace (debug app load chậm) |
| `take_screenshot` | Chụp màn hình trang hiện tại |

Chi tiết đầy đủ (toàn bộ nhóm tool, CLI flags, security notes): xem
[`reference/mcp-guides/mcp-chrome-devtools.md`](reference/mcp-guides/mcp-chrome-devtools.md).

_Sau khi cấu hình, AI sẽ có thêm các tool:_

| Tool | Server | Mô tả |
|------|--------|-------|
| `search_cds` | cds-kb | Tìm CDS view theo business meaning |
| `get_cds_view` | cds-kb | Lấy definition đầy đủ của 1 CDS view |
| `get_views_by_tag` | cds-kb | Liệt kê CDS view theo tag (BO, LOB, module) |
| `get_taxonomy` | cds-kb | Khám phá Lines of Business → Business Objects |
| `kb_info` | cds-kb | Kiểm tra version KB |
| `search` | mcp-sap-docs-btp | Tra cứu SAP Help Portal + offline docs |
| `sap_community_search` | mcp-sap-docs-btp | Tìm kiếm SAP Community Q&A |
| `sap_search_objects` | mcp-sap-docs-btp | Tra cứu Clean Core Released Objects |
| `abap_feature_matrix` | mcp-sap-docs-btp | Kiểm tra ABAP syntax support |
| `sap_accelerator_hub_*` | mcp-sap-docs-btp | Khám phá API trên SAP Accelerator Hub |
| `sap_fiori_library_*` | mcp-sap-docs-btp | Tra cứu Fiori App Reference Library |
| `sap_discovery_center_*` | mcp-sap-docs-btp | Khám phá BTP services & pricing |
| `abap_lint` | mcp-sap-docs-btp | Kiểm tra chất lượng code ABAP |

> **Lưu ý**: Server `mcp-sap-docs-btp` cần `SAP-API-HUB-KEY` để các tool `sap_accelerator_hub_*`
> hoạt động đầy đủ. Các tool còn lại vẫn chạy không cần key.

Mọi tool đều có tham số `profile` (để trống = profile active). Ví dụ:

```
"Liệt kê các package trong project project1"
-> Claude gọi sap_list_packages({ profile: "project1.s4hana.cloud.sap" })

"Tìm class ZCL_* trong project đang dùng"
-> Claude gọi sap_search({ query: "ZCL_" })
```

## 📚 SAP Daily Learner — Skill Curator & Cron thật (Hermes-like)

`skills/sap-daily-learner/SKILL.md` là agent tự cải thiện (self-improving) lấy cảm hứng từ
**Hermes Agent** ([NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)) —
gia sư SAP hàng ngày + tự tạo skill document từ tương tác phức tạp (xem mục "Notion" ở trên cho
phần đồng bộ team). 2 khả năng dưới đây (thêm 2026-07-16) đọc trực tiếp kiến trúc thật của Hermes
trước khi build — không đoán mò tên gọi rồi tự chế cơ chế bên trong.

### 🧹 Skill Curator — vòng đời skill tự động

Skill tự tạo trong `memory/procedural/skills/` càng tích luỹ càng dễ "chết" — không còn ai dùng
nhưng vẫn nằm mãi, làm chậm việc tra cứu. `reference/scripts/skill_curator.py` xử lý việc này,
đúng cơ chế **Curator** của Hermes: skill không dùng tới sau **30 ngày** chuyển `stale`, sau
**90 ngày** chuyển `archived` (di chuyển vào `memory/procedural/skills/.archive/`, **không bao
giờ xoá thật** — khôi phục được bất kỳ lúc nào bằng cách chuyển file trở lại). Dùng lại 1 skill sẽ
tự đưa nó về `active`.

Chạy tự động mỗi khi `sap-daily-learner` được gọi (tự gate theo interval 7 ngày — gọi sớm hơn sẽ
tự bỏ qua, không cần tự canh giờ) — **không cần setup gì thêm**. Muốn tự kiểm tra trạng thái:

```bash
python reference/scripts/skill_curator.py run "$(python reference/scripts/agent_home.py memory/procedural)" --dry-run
```

### ⏰ Cron thật — daily tip chạy nền qua Windows Task Scheduler

> ⚠️ **Mặc định TẮT (opt-in tuyệt đối)**, cùng triết lý với Continuous Improvement Engine ở dưới.
> Mỗi lần cron thật sự chạy sẽ gọi 1 phiên Claude Code (`claude -p`) thật — **tốn chi phí API
> thật** trên tài khoản của bạn. Cài xong vẫn chưa chạy gì cả cho tới khi bạn bật rõ ràng.

Khác Hermes bản gốc (có `gateway daemon` chạy liên tục, tự poll mỗi 60 giây): plugin này không có
tiến trình nền thật — dùng **Windows Task Scheduler** làm "cái luôn túc trực" thay cho daemon đó.

**Bước 1 — Cài lịch Task Scheduler** (chỉ đặt lịch, CHƯA chạy gì — cần quyền Administrator):

```
Click phải reference\scripts\install-daily-learner-cron.bat → Run as administrator
```

Sau khi cài, task sẽ tự "tick" mỗi 5 phút nhưng vẫn no-op (không làm gì) cho tới Bước 2.

**Bước 2 — Bật opt-in thật sự** (chọn 1 trong 2 cách):

<details>
<summary><b>PowerShell</b> (Windows — khuyến nghị)</summary>

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.sap-abap-agent\cron"
New-Item -ItemType File -Force -Path "$env:USERPROFILE\.sap-abap-agent\cron\ENABLED"
```

</details>

<details>
<summary><b>CMD</b> (Windows — Command Prompt)</summary>

```cmd
if not exist "%USERPROFILE%\.sap-abap-agent\cron" mkdir "%USERPROFILE%\.sap-abap-agent\cron"
echo. > "%USERPROFILE%\.sap-abap-agent\cron\ENABLED"
```

</details>

Hoặc set biến môi trường hệ thống `SAP_ABAP_AGENT_CRON_ENABLED=1` (System Properties → Environment
Variables) thay vì tạo file marker — 2 cách tương đương.

**Bước 3 — Thêm ít nhất 1 job** (cron chỉ có việc để làm sau bước này):

> ⚠️ Prompt bắt đầu bằng `/` (gọi thẳng 1 skill) **phải thêm qua PowerShell**, không dùng Git
> Bash — đã xác nhận qua test thật: Git Bash tự "dịch" chuỗi bắt đầu bằng `/` thành đường dẫn
> Windows (MSYS path-mangling), làm hỏng nội dung prompt.

```powershell
python reference\scripts\cron_manage.py add "$env:USERPROFILE\.sap-abap-agent" daily-tip "/sap-daily-learner cho toi 1 tip hoc SAP hom nay dua tren tien do hien tai" daily@08:00
```

**Kiểm tra trạng thái / chi phí đã dùng** (bất kỳ lúc nào):

```bash
python reference/scripts/cron_manage.py status "$(python reference/scripts/agent_home.py)"
```

**Kết quả tick** được ghi vào `<agent-home>/cron/pending/`, rồi tự bơm vào phiên chat Claude Code
kế tiếp khi bạn mở lên (SessionStart hook `hooks/cron_deliver.py`) — không có tích hợp Telegram/
Slack như Hermes thật, nhưng không cần thêm thao tác nào.

**Gỡ bỏ**: `schtasks /delete /tn "SAP ABAP Agent - Daily Learner Cron Tick" /f`, xoá file
`ENABLED`/`cron_manage.py disable <job-id>` là đủ.

Chi tiết đầy đủ (bao gồm bảng so sánh Memory/Skill Creation/Curator/Cron với Hermes thật):
`skills/sap-daily-learner/SKILL.md` mục "Scheduling cơ chế" + "3d. Skill Curator".

## Chạy nhiều instance cùng lúc (1 profile / instance)

Đặt env `SAP_BTP_PROFILE=<id>` trước mỗi lần chạy:

<details>
<summary><b>PowerShell</b> (Windows — khuyến nghị)</summary>

```powershell
# Terminal 1: Claude 1 với profile A
$env:SAP_BTP_PROFILE = "project1.s4hana.cloud.sap"
sap-btp-agent

# Terminal 2: Claude 2 với profile B
$env:SAP_BTP_PROFILE = "project2.s4hana.cloud.sap"
sap-btp-agent
```

</details>

<details>
<summary><b>CMD</b> (Windows — Command Prompt)</summary>

```cmd
:: Terminal 1: Claude 1 với profile A
set SAP_BTP_PROFILE=project1.s4hana.cloud.sap
sap-btp-agent

:: Terminal 2: Claude 2 với profile B
set SAP_BTP_PROFILE=project2.s4hana.cloud.sap
sap-btp-agent
```

</details>

<details>
<summary><b>bash / zsh / Git Bash / WSL</b> (macOS, Linux)</summary>

```bash
# Terminal 1: Claude 1 với profile A
SAP_BTP_PROFILE=project1.s4hana.cloud.sap sap-btp-agent

# Terminal 2: Claude 2 với profile B
SAP_BTP_PROFILE=project2.s4hana.cloud.sap sap-btp-agent
```

</details>

## Cấu hình folder

```
%USERPROFILE%\.sap-btp-agent\   (Windows)
~/.sap-btp-agent/               (macOS/Linux)
+-- profiles.json                <- registry (danh sách + active)
+-- profiles/
|   +-- <profile-id>/            <- 1 folder / project SAP
|       +-- config.json
|       +-- secrets.json         <- MÃ HÓA
+-- log/
+-- cache/
```

- **Windows**: secrets mã hóa bằng **DPAPI** qua PowerShell (gắn với tài khoản Windows).
- **macOS/Linux**: **AES-256-GCM**, key derive từ `hostname + username`.
- File mode `0o600`, chỉ owner đọc/ghi.

**Lưu ý**: `%USERPROFILE%\.sap-abap-agent\` (tên gần giống nhưng KHÁC folder trên) là nơi lưu
state riêng của **plugin Claude Code** (memory của `sap-daily-learner`, cache của
`sap-context-tool-result-trim`, session/handoff đang làm dở) — không liên quan kết nối SAP BTP.
Cache/log trong đó tự dọn theo tuổi (mặc định 7 ngày, xem
`reference/scripts/cleanup_agent_home.py`). Chi tiết: `CONTRIBUTING.md` mục "SAP_ABAP_AGENT_HOME".

## Env

Các biến môi trường quan trọng (đặt **trước khi** chạy `sap-btp-agent` / `claude`):

| Tên biến | Ý nghĩa |
|----------|---------|
| `SAP_BTP_PROFILE=<id>` | Khóa profile cho 1 lần chạy (ưu tiên registry) |
| `SAP_BTP_AGENT_HOME=/path` | Đổi folder cấu hình (test, multi-tenant) |
| `GITHUB_TOKEN=ghp_xxx` | Token GitHub (tự tạo issue khi error reporter bật) |
| `SAP_ABAP_AGENT_ERROR_REPORTING=1` | Bật error reporter (xem mục Error Reporting ở trên) |

### Cách đặt env tùy theo shell

**PowerShell (Windows — khuyến nghị):**

```powershell
# Tạm thời (chỉ session hiện tại)
$env:SAP_BTP_PROFILE = "project1.s4hana.cloud.sap"

# Vĩnh viễn (cho user hiện tại, mở lại shell mới vẫn còn)
[System.Environment]::SetEnvironmentVariable("SAP_BTP_PROFILE", "project1.s4hana.cloud.sap", "User")
```

**CMD (Windows):**

```cmd
:: Tạm thời (chỉ session hiện tại)
set SAP_BTP_PROFILE=project1.s4hana.cloud.sap

:: Vĩnh viễn (cho user hiện tại)
setx SAP_BTP_PROFILE "project1.s4hana.cloud.sap"
```

**bash / zsh / Git Bash / WSL (macOS, Linux):**

```bash
# Tạm thời (chỉ session hiện tại)
export SAP_BTP_PROFILE=project1.s4hana.cloud.sap

# Vĩnh viễn: thêm vào ~/.bashrc (bash) hoặc ~/.zshrc (zsh)
echo 'export SAP_BTP_PROFILE=project1.s4hana.cloud.sap' >> ~/.bashrc
```

> **Sau khi đổi vĩnh viễn**, đóng và mở lại terminal / shell mới để biến có hiệu lực.

## 🧠 SAP Consultant System (Auto-scoring Routing Engine)

`skills/sap-ask-consultant/SKILL.md` là skill trung tâm, dispatch câu hỏi user tới **25 module
consultants + 1 researcher + 1 daily learner + 1 reviewer** bằng cơ chế **keyword scoring + parallel dispatch**.

### Cách hoạt động

1. **Keyword Matrix**: Mỗi module có keywords với weight 3/2/1.
2. **Tính score**: Module nào >= threshold (2) thì được dispatch.
3. **Explicit mention**: "hỏi SD", "hỏi FI" → dispatch mặc định.
4. **Module coupling**: Module thường đi cùng (FI↔CO, PP→QM→MM...) tự động dispatch.
5. **Parallel dispatch**: Tất cả module >= threshold dispatch song song trong 1 message.

### Ví dụ

| Câu hỏi | Module dispatch |
|---------|----------------|
| "tìm CDS view cho sales order bị chậm giao hàng" | `sap-docs-researcher` + `sap-sd-consultant-cloud` song song |
| "cấu hình cost center và GL" | `sap-co-consultant-cloud` + `sap-fi-consultant-cloud` (coupling) |
| "làm sao tạo purchase order" | `sap-mm-consultant-cloud` |
| "hỏi PP, QM, MM" | `sap-pp` + `sap-qm` + `sap-mm` song song |
| "hỏi IBP: dự báo doanh thu quý sau" | `sap-ibp-consultant-cloud` (Demand Planning) |
| "EWM cấu hình wave management cho kho" | `sap-ewm-consultant-cloud` |
| "IBP inventory optimization cho supply chain" | `sap-ibp-consultant-cloud` + `sap-mm-consultant-cloud` (coupling) |
| "Fiori app cho sales order" | `sap-fiori-consultant-cloud` + `sap-sd-consultant-cloud` (coupling) |
| "CAP side-by-side extension cho S/4HANA" | `sap-cap-consultant-cloud` + `sap-btp-admin-consultant-cloud` |
| "iFlow tích hợp S/4HANA với SAP SuccessFactors" | `sap-cpi-consultant-cloud` + `sap-successfactors-consultant-cloud` |
| "BTP destination + Cloud Connector" | `sap-btp-admin-consultant-cloud` |

### Các module đã có

| # | Agent | Module |
|---|-------|--------|
| 1 | `sap-sd-consultant-cloud` | Sales & Distribution |
| 2 | `sap-fi-consultant-cloud` | Financial Accounting |
| 3 | `sap-mm-consultant-cloud` | Materials Management |
| 4 | `sap-co-consultant-cloud` | Controlling |
| 5 | `sap-pp-consultant-cloud` | Production Planning |
| 6 | `sap-qm-consultant-cloud` | Quality Management |
| 7 | `sap-pm-consultant-cloud` | Plant Maintenance |
| 8 | `sap-wm-consultant-cloud` | Warehouse Management |
| 9 | `sap-ps-consultant-cloud` | Project Systems |
| 10 | `sap-hcm-consultant-cloud` | Human Capital Management |
| 11 | `sap-bw-consultant-cloud` | Analytics / BW |
| 12 | `sap-basis-consultant-cloud` | Basis / Technical Admin |
| 13 | `sap-tm-consultant-cloud` | Transportation Management |
| 14 | `sap-tr-consultant-cloud` | Treasury & Cash Management |
| 15 | `sap-ariba-consultant-cloud` | Procurement Collaboration |
| 16 | `sap-ca-consultant-cloud` | Cross-Application Functions |
| 17 | `sap-gts-consultant-cloud` | Global Trade Services |
| 18 | `sap-ehs-consultant-cloud` | Environment, Health & Safety |
| 19 🆕 | `sap-ibp-consultant-cloud` | **Supply Chain Planning (IBP)** |
| 20 🆕 | `sap-ewm-consultant-cloud` | **Extended Warehouse Mgmt (EWM)** |
| 21 🆕 | `sap-fiori-consultant-cloud` | **Fiori/UI5 (Fiori Elements, Adaptation, SAP Build)** |
| 22 🆕 | `sap-cap-consultant-cloud` | **CAP (Cloud Application Programming Model)** |
| 23 🆕 | `sap-cpi-consultant-cloud` | **CPI (Cloud Platform Integration / Integration Suite)** |
| 24 🆕 | `sap-successfactors-consultant-cloud` | **SuccessFactors (HXM Cloud — EC, Recruiting, LMS)** |
| 25 🆕 | `sap-btp-admin-consultant-cloud` | **BTP Admin (Platform; CF, Kyma, Destinations, Security)** |
| — | `sap-docs-researcher` | CDS view & Docs Research |
| — | `sap-daily-learner` | Daily SAP Learning, Hermes-like skill creation |

## 🏗️ Codegen Pipeline (Function Spec -> ABAP code)

8 skill nối tiếp nhau, biến Function Spec (`.docx` khách hàng gửi) thành code ABAP đã activate,
review, test và sẵn sàng release, theo chuẩn RAP/CDS. File trung gian đặt trong `in/`/`out/` — **thư mục local per-user, KHÔNG nằm trong
git repo**: `%USERPROFILE%\.sap-btp-agent\in\` + `...\out\` (Windows) hoặc `~/.sap-btp-agent/in/` +
`.../out/` (macOS/Linux), cùng nơi lưu profile/secrets kết nối SAP BTP (xem mục "Cấu hình folder").
Lý do: tài liệu FS và output sinh ra là dữ liệu nghiệp vụ/khách hàng, không nên nằm chung với
source code plugin (rủi ro commit nhầm lên repo public). Có thể đổi qua env `SAP_BTP_AGENT_HOME`.
Lấy đúng đường dẫn: `python -c "from sap_btp_agent.config.paths import get_in_dir; print(get_in_dir())"`.

```bash
# 0. Đặt FS vào in/ (thư mục local per-user ở trên), convert sang markdown
cp /path/to/FS_xxx.docx "$(python -c 'from sap_btp_agent.config.paths import get_in_dir; print(get_in_dir())')/"
# -> skill sap-doc-to-md (reference/scripts/office_to_md.py, không tham số) -> out/FS_xxx.md

# 1. Phân tích FS -> chuẩn hóa yêu cầu
# -> skill sap-analyze-function-spec -> out/<ticket>/INTAKE.md

# 2. Quyết định kiến trúc (managed/unmanaged/CDS/class)
# -> skill sap-write-technical-spec -> out/<ticket>/TECHNICAL_SPEC.md

# 3. Sinh skeleton code
# -> skill sap-scaffold-rap (CRUD/RAP) hoặc sap-scaffold-cds (chỉ-read) -> out/<ticket>/src/

# 4. Review naming/released-API/clean-ABAP
# -> skill sap-atc-review -> out/<ticket>/ATC_REVIEW.md

# 5. Sinh ABAP Unit test
# -> skill sap-unit-test

# 6. Checklist đóng ticket (activation/ATC/test/transport/abapGit)
# -> skill sap-finish-ticket -> out/<ticket>/FINISH_CHECKLIST.md
```

Skill phụ trợ: `sap-virtual-element` (calculated field trong CDS). Quy ước đặt tên & bậc thang
extensibility dùng chung với `sap-clean-code` / `sap-extensibility`. Khi cần tìm CDS view/API
chuẩn cho 1 phân hệ cụ thể (bước 2), hỏi agent consultant tương ứng (`sap-fi-consultant-cloud`,
`sap-mm-consultant-cloud`...) hoặc `sap-docs-researcher`.

Kỷ luật xuyên suốt (không phải bước riêng, áp dụng mọi lúc trong pipeline): `sap-routing-discipline`
(luôn check routing trước khi trả lời — bơm tự động qua SessionStart hook),
`sap-verification-before-completion` (bằng chứng chạy thật trước khi báo "xong"),
`sap-systematic-debugging` (khi có bug runtime, thay vì đoán-sửa-lặp-lại).

## Test local

```bash
cd ..
claude --plugin-dir ./sap-abap-agent
```

Trong Claude:
- "Setup SAP BTP cho project https://project1.s4hana.cloud.sap" -> gọi wizard
- "Liệt kê các profile SAP của tôi" -> gọi `sap_list_profiles`
- "Tìm class bắt đầu bằng ZCL_ trong project project1" -> gọi `sap_search` với `profile="project1..."`
- "Hỏi SD: cấu hình pricing cho sales order" -> gọi `sap-sd-consultant-cloud`
- "Tìm CDS view cho purchase order quá hạn và hỏi MM" -> `sap-docs-researcher` + `sap-mm-consultant-cloud`
- "Học SAP hôm nay" -> `sap-daily-learner` (daily tip + learning path)
- "Quiz MM cho tôi" -> `sap-daily-learner` (trắc nghiệm MM)
- "Cấu hình cost center và cash management" -> `sap-co-consultant-cloud` + `sap-tr-consultant-cloud`
- "Fiori app cho sales order" -> `sap-fiori-consultant-cloud` + `sap-sd-consultant-cloud`
- "CAP side-by-side extension cho S/4HANA" -> `sap-cap-consultant-cloud` + `sap-btp-admin-consultant-cloud`
- "iFlow tích hợp S/4HANA với SuccessFactors" -> `sap-cpi-consultant-cloud` + `sap-successfactors-consultant-cloud`
- "BTP destination + Cloud Connector" -> `sap-btp-admin-consultant-cloud`

## Cập nhật

Tự động (CI/CD): mỗi lần push code vào `main`, GitHub Actions bump version trong `plugin.json`, tạo git tag `vX.Y.Z` — Claude Code marketplace tự động phát hiện và nhắc bạn cập nhật plugin.

Local (1 lệnh):
```bash
# Windows (PowerShell)
.\reference\scripts\update.ps1

# Linux / macOS
bash reference/scripts/update.sh
```
Script tự động: git pull plugin → tải wheel `.whl` mới nhất từ GitHub Release → `pip install --upgrade`.

## Lỗi thường gặp

| Lỗi                                 | Cách sửa                                                  |
|-------------------------------------|-------------------------------------------------------------|
| `401 Unauthorized`                  | Client_secret sai / hết hạn. Chạy `setup <profile-id>`    |
| `404 /oauth/token`                  | Sửa `tokenUrl` trong `profiles/<id>/secrets.json`         |
| `Khong giai ma duoc secret`         | Đổi máy. Chạy `setup <profile-id>` để tạo lại             |
| `Chua co profile nao`               | Chạy `sap-btp-agent setup <URL>`                          |
| `'sap-btp-agent' is not recognized` | PATH thiếu folder chứa entry point. Chạy `python -m sap_btp_agent.doctor` để tự phát hiện + lấy lệnh fix |

## Trạng thái

v1.3.3 — **28 agents (25 modules + 1 researcher + 1 daily learner + 1 reviewer)** với auto-scoring routing engine,
CDS KB, SAP Docs Research, ABAP Cloud clean code, extensibility, key user toolkit, Hermes-like self-improving learning.
**Mới:** Fiori/UI5, CAP, CPI, SuccessFactors, BTP Admin consultants; state của plugin
(`sap-daily-learner`, cache, session/handoff) chuyển từ project-relative sang
`%USERPROFILE%\.sap-abap-agent\` dùng, kèm script tự dọn cache/log quá 7 ngày
(xem CHANGELOG v1.3.3).

## Cảm hứng (Inspired by)

Plugin tham khảo và lấy cảm hứng từ các dự án open-source dưới đây (tất cả đều đã được tích hợp
hoặc tham khảo pattern, **không fork**):

### Cùng lĩnh vực SAP / ABAP
- [`secondsky/sap-skills`](https://github.com/secondsky/sap-skills) — plugin AI coding assistant
  production-ready (BTP, CAP, Fiori, ABAP, HANA, Analytics Cloud, Datasphere). Tham khảo cấu
  trúc skill/manifest.
- [`marcellourbani/vscode_abap_remote_fs`](https://github.com/marcellourbani/vscode_abap_remote_fs)
  — VS Code agentic AI platform cho ABAP development.
- [`google/ai-abap-assistant-sample`](https://github.com/google/ai-abap-assistant-sample) — Genie
  for SAP (code explain / review / suggest). Tham khảo cho skill `sap-atc-review` mục "RAG Review
  Pattern".
- [`microsoft/aisdkforsapabap`](https://github.com/microsoft/aisdkforsapabap) — AI SDK cho ABAP.
- [`oisee/zllm`](https://github.com/oisee/zllm) — LangChain-lite cho ABAP.
- [`ClementRingot/ROSA`](https://github.com/ClementRingot/ROSA) — MCP server cho Released Objects.
  Tham khảo cho skill `sap-released-classes` mục "Released-Object search pattern".
- [`google-cloud-abap/demo-hpro`](https://github.com/google-cloud-abap/demo-hpro) — RAG với
  Vertex AI SDK for ABAP.
- [`Chirag-Dwivedi/SAP_ABAP_RAG_Chatbot`](https://github.com/Chirag-Dwivedi/SAP_ABAP_RAG_Chatbot)
  — RAG chatbot SAP/ABAP. Tham khảo pattern retrieval.
- [`IaManBel/sap-abap-rag-refactorer`](https://github.com/IaManBel/sap-abap-rag-refactorer) —
  RAG cho ABAP refactor.
- [`Gixsy95/abap_wiki`](https://github.com/Gixsy95/abap_wiki) — Agent-driven knowledge base cho
  S/4HANA custom objects.

### MCP servers tham khảo (xem chi tiết trong `docs/sap-mcp-recommendations.md`)
- [`marianfoo/sap-ai-mcp-servers`](https://github.com/marianfoo/sap-ai-mcp-servers) — repo
  catalog.
- [`fr0ster/mcp-abap-adt`](https://github.com/fr0ster/mcp-abap-adt),
  [`mario-andreschak/mcp-abap-abap-adt-api`](https://github.com/mario-andreschak/mcp-abap-abap-adt-api),
  [`HatriGt/hana-mcp-server`](https://github.com/HatriGt/hana-mcp-server),
  [`marianfoo/mcp-sap-notes`](https://github.com/marianfoo/mcp-sap-notes),
  [`mario-andreschak/mcp-sap-gui`](https://github.com/mario-andreschak/mcp-sap-gui),
  [`gavdilabs/cap-mcp-plugin`](https://github.com/gavdilabs/cap-mcp-plugin),
  [`lemaiwo/btp-sap-odata-to-mcp-server`](https://github.com/lemaiwo/btp-sap-odata-to-mcp-server).

### Curriculum / learning tham khảo (cho `sap-daily-learner`)
- [`anfisc/abap-rap-introduction`](https://github.com/anfisc/abap-rap-introduction),
  [`msg-CareerPaths/sap-abap-internship`](https://github.com/msg-CareerPaths/sap-abap-internship),
  [`KlamGit/sap-basic-abap`](https://github.com/KlamGit/sap-basic-abap),
  [`skalmodiya/sap-ai-core-launchpad`](https://github.com/skalmodiya/sap-ai-core-launchpad).

### Công nghệ nền
- [`NousResearch/hermes-agent`](https://github.com/NousResearch/hermes-agent) — nguồn cảm hứng
  cho `sap-daily-learner` (persistent memory + auto-skill + curator).
- [`agent-skills-for-context-engineering`](https://github.com/muratcankoylan/agent-skills-for-context-engineering)
  — pattern memory-systems + context engineering (đã nhắc trong README ở mục "Context
  Engineering").

### Cách đóng góp thêm

Nếu bạn biết repo open-source khác cùng chủ đề, mở issue / PR thêm vào mục này. Tiêu chí:
- Repo có tài liệu rõ ràng.
- Mã nguồn công khai, license cho phép tham khảo (MIT / Apache-2.0 / BSD…).
- Đã được maintain trong 6 tháng gần nhất.

## Tài liệu

| File                                         | Mục đích                                              |
|----------------------------------------------|--------------------------------------------------------|
| [`docs/onboarding-guide.md`](docs/onboarding-guide.md)         | Hướng dẫn end-user cài đặt + dùng thử                  |
| [`docs/sap-mcp-recommendations.md`](docs/sap-mcp-recommendations.md) | Khuyến nghị MCP server bổ sung (Tier 1/2/3, opt-in)     |
| [`CONTRIBUTING.md`](CONTRIBUTING.md)         | Hướng dẫn đóng góp skill/agent/docs                    |
| [`SKILL_TEMPLATE.md`](SKILL_TEMPLATE.md)     | Template chuẩn để tạo skill/agent/reference module    |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)   | Quy tắc ứng xử cộng đồng                              |
| [`CHANGELOG.md`](CHANGELOG.md)               | Lịch sử thay đổi                                       |
| [`SECURITY.md`](SECURITY.md)                 | Chính sách bảo mật                                     |
| [`LICENSE`](LICENSE)                         | MIT License                                             |
