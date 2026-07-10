# 📋 Changelog — SAP ABAP Agent

All notable changes to this project will be documented in this file.

Format dựa trên [Keep a Changelog](https://keepachangelog.com/) và [Semantic Versioning](https://semver.org/).

---

## [v0.5.0] — 2026-07-11

### Added
- 🧠 **sap-daily-learner** — Hermes-like self-improving learning agent:
  - Agent definition (`agents/sap-daily-learner.md`)
  - Skill implementation (`skills/sap-daily-learner/SKILL.md`)
  - Reference module (`reference/modules/sap-daily-learner/SKILL.md`)
  - Auto-skill creation từ tương tác người dùng
  - Persistent memory qua `LEARNING_PROGRESS.md`
  - Progressive learning paths (Beginner → Intermediate → Expert)
- 🔀 **Routing Engine update**: Thêm Daily Learner vào keyword matrix (threshold ≥ 1)
- 🌐 **English translations**: ~80+ translation entries cho architecture, how-to-ask, daily learner sections
- 🏗️ **Architecture documentation**: Sơ đồ hệ thống + flow xử lý + file map
- 📚 **Hướng dẫn đặt câu hỏi**: Mẫu câu cho từng module, multi-module examples, skill usage guide
- 📝 **SKILL_TEMPLATE.md**: Template chuẩn cho skill, agent, reference module
- 🤝 **CONTRIBUTING.md**: Hướng dẫn đóng góp chi tiết (PR checklist, naming conventions, templates)

### Changed
- `skills/sap-ask-consultant/SKILL.md`: Cập nhật routing engine từ 19 → 20 agents
- `.claude-plugin/plugin.json`: Bump version v0.4.0 → v0.5.0
- `README.md`: Cập nhật danh sách agents + contributing links
- `index.html`: Thêm architecture docs + translations + daily learner section

---

## [v0.4.0] — 2026-07-11

### Added
- 🧠 **SAP Consultant System**: 18 module consultants + 1 researcher
  - `sap-sd-consultant-cloud`, `sap-fi-consultant-cloud`, `sap-mm-consultant-cloud`
  - `sap-co-consultant-cloud`, `sap-pp-consultant-cloud`, `sap-qm-consultant-cloud`
  - `sap-pm-consultant-cloud`, `sap-wm-consultant-cloud`, `sap-ps-consultant-cloud`
  - `sap-hcm-consultant-cloud`, `sap-bw-consultant-cloud`, `sap-basis-consultant-cloud`
  - `sap-tm-consultant-cloud`, `sap-tr-consultant-cloud`, `sap-ariba-consultant-cloud`
  - `sap-ca-consultant-cloud`, `sap-gts-consultant-cloud`, `sap-ehs-consultant-cloud`
  - `sap-docs-researcher` (CDS view & Docs Research)
- 🔀 **Auto-scoring Routing Engine**:
  - Keyword matrix (weight 3/2/1)
  - Module coupling (FI↔CO, PP→QM→MM...)
  - Explicit mention dispatch ("hoi SD")
  - Parallel dispatch
- 📚 **CDS Knowledge Base**: 7,355 released CDS views qua `cds-kb-mcp`
- 📖 **SAP Docs Research**: SAP Help, Community, API Hub, Fiori App Library qua `mcp-sap-docs`
- 🌐 **Bilingual support**: VI ↔ EN toggle trong index.html
- 🍪 **Cookie Auth + Web Popup Re-Auth**: SAP session cookies (`MYSAPSSO2`, `SAP_SESSIONID`)
- 🛡️ **Stampede Protection**: Chỉ 1 lần re-auth cho multiple 401 requests
- 🧹 **sap-clean-code** skill: ABAP Cloud naming conventions
- 🧩 **sap-extensibility** skill: Extensibility checklist
- 🛠️ **sap-key-user-toolkit** skill: Key User handbook
- ⚙️ **sap-btp-setup** skill: BTP connection manager
- 📄 `commands/sap-connect.md`: CLI command guide

### Changed
- `reference/mcp-server/`: MCP server Python với multi-profile support
- `index.html`: Thiết kế lại với sidebar, dark/light theme, copy buttons
- `.claude-plugin/plugin.json`: v0.3.0 → v0.4.0

---

## [v0.3.0] — 2026-07-10

> Version này là initial commit, toàn bộ dự án được tạo trong 1 commit.

### Added
- MCP server Python (`sap-btp-agent` CLI)
  - OAuth2 authentication (client_credentials, password, bearer)
  - Multi-profile support
  - Secret encryption (DPAPI Windows, AES-256-GCM macOS/Linux)
  - ABAP tools: `sap_search`, `sap_read_source`, `sap_syntax_check`, `sap_activate`
- Claude Code plugin structure
  - `.claude-plugin/plugin.json`
  - `hooks/hooks.json` (SELECT * warning)
  - `agents/`, `skills/`, `commands/`, `reference/` directories
- `abap-reviewer` agent
- `sap-clean-code` skill cơ bản
- `README.md` + `index.html` cơ bản
- Git ignore patterns

---

## [Unreleased]

### Planned
- 🚀 **Thêm SECURITY.md**: Hướng dẫn báo cáo lỗi bảo mật
- 🚀 **Thêm badges**: Python version, PRs welcome, GitHub stars
- 🚀 **Thêm CHANGELOG.md badge vào README.md header**
- 🚀 **Thêm agents còn thiếu**: TM, TR, Ariba, CA, GTS, EHS agent files
- 🚀 **Hoàn thiện reference modules**: Knowledge base cho 18 modules

### ✅ Đã hoàn thành gần đây
- ✅ **GitHub Issue templates**: Bug report + Feature request (`.github/ISSUE_TEMPLATE/`)
- ✅ **Background sync daemon**: `reference/scripts/sync_skills.py` + `install-task-scheduler.bat`
- ✅ **Open-source files**: `LICENSE` (MIT), `CODE_OF_CONDUCT.md`, `.github/PULL_REQUEST_TEMPLATE.md`
- ✅ **Skill sync command**: `commands/sync-skills.md` với hướng dẫn daemon background

---

## 📊 Version history

| Version | Date | Agents | Skills | Highlights |
|---------|------|--------|--------|------------|
| v0.5.0 | 2026-07-11 | 20 | 8 | Daily Learner, translations, open-source files |
| v0.4.0 | 2026-07-11 | 19 | 7 | Consultant System, routing engine, CDS KB, Docs |
| v0.3.0 | 2026-07-10 | 1 | 1 | Initial release, MCP server, basic structure |

---

*Changelog này được duy trì thủ công. Cập nhật khi có release mới.*
